#!/usr/bin/env python3


def b64decode(value):
    import base64
    return base64.b64decode(value).decode('utf-8')

def b64encode(value):
    import base64
    return base64.b64encode(value.encode('utf-8')).decode('utf-8')

def escape(value,format="html"):
    if format == "html":
        return html.escape(value)
    elif format == "quote":
        return value.replace('\\', '\\\\').replace('"', '\\"')
    
def unescape(value,format="html"):
    if format == "html":
        return html.unescape(value)
    elif format == "quote":
        return value.replace('\\"', '"').replace('\\\\', '\\')

def flatten(matrix):
    return [item for row in matrix for item in row]

def from_json(str):
    return json.loads(str)


def from_yaml(data):
    return yaml.safe_load(data)

def from_json_or_yaml(data):
    return yaml.safe_load(data)

def from_yaml_all(data):
    return yaml.safe_load_all(data)

def intersect(a, b):
    return list(set(a).intersection(b))

def running_context(format="native"):
    import platform
    import os
    import shutil
    import json

    platform_system = platform.system()
    terminal_name = os.environ.get('TERM', '') 


    ms_system = os.environ.get('MSYSTEM', '')
    if platform_system == "Windows":
        if ms_system == "MINGW64" or ms_system == "CLANGARM64":
            shell_type = "git_bash"
        elif terminal_name  == "xterm":
            shell_type = "cygwin"
        else:
            shell_type = "windows"
    else:
        shell_type = "Linux"
    terminal_size = shutil.get_terminal_size()
    terminal = {
        "columns": terminal_size.columns,
        "lines": terminal_size.lines,
        "name": terminal_name,
    }

    running_platform = {
        "system": platform_system,
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "ms_system": ms_system
    }

    out_dcit = {"platform": running_platform, "shell_type": shell_type, "terminal": terminal}
    if format == "native":
        return out_dcit
    else:
        return json.dumps(out_dcit)

def wrap_html(data,title=""):
    if running_platform == "Windows":
        path_sep = "\\"
    else:
        path_sep = "/"
    base_path = getattr(sys, '_MEIPASS', os.path.abspath(path_sep.join(__file__.split(path_sep)[:-1])))
    logging.info(f"base_path: {base_path}")
    resources_path = f"{base_path}{path_sep}resources"
    def load_file(expected_file_name):
        with open(resources_path + path_sep + expected_file_name, 'r') as file:
            content = file.read()
        return content
    
    js_wrapper_css = load_file("js_wrapper.css")
    js_wrapper_script = load_file("js_wrapper.js")

    return f"""<!DOCTYPE html>
<html lang="fr">
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.4/jquery.min.js"></script>
    <style>
        {js_wrapper_css}
    </style>
<body>
<div id="toc"></div>
{data}
<button id="scrollTopButton" onclick="scrollToTop()">Top</button>
<script>
    {js_wrapper_script}
</script>
</body>
</html>
        """
def jtable(dataset,select=[], unselect=[],path="{}",format="",views={}, when=[],context = {}, queryset={}):
    return JtableCls().render_object( dataset,path=path, select=select, unselect=unselect,views=views, when=when, format=format, context = context, queryset=queryset)

def m5(data):
    import hashlib
    return hashlib.md5(data.encode()).hexdigest()

def regex_replace(value="", pattern="", replacement="", ignorecase=False):
    """ Perform a `re.sub` returning a string """
    if ignorecase:
        flags = re.I
    else:
        flags = 0
    _re = re.compile(pattern, flags=flags)
    return _re.sub(replacement, value)
def strftime(string_format, second=None):
    """ return a date string using string.
    See https://docs.python.org/2/library/time.html#time.strftime for format
    timestamp option strftime(s) Doesn't works on Cygwin => old known cygwin issue """

    if second is not None:
        try:
            second = int(second)
        except Exception:
            raise "Invalid value for epoch value (%s)" % second
    return time.strftime(string_format, time.localtime(second))
def to_datetime(_string, format=r"%Y-%m-%d %H:%M:%S"):
        return datetime.datetime.strptime(_string, format)
def to_epoch(date_str):
    f"""Convert a date string to epoch
    Args:
        date_str (str): Date string format: %Y-%m-%d %H:%M:%S !!! only !!!
    """
    if running_platform == "Windows":
        return int(Plugin.shell(f"powershell -c \"[math]::Round((Get-Date '{date_str}' -UFormat '%s'))\""))
    else:
        return int(time.mktime(datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").timetuple()))
    
def to_json(a, *args, **kw):
    return json.dumps(a, *args, **kw)

def to_pie(dataset):
    title = [list(key.keys()) for key in dataset][0][0]
    out = f"```mermaid\n  pie\n      title {title}\n"
    for item in dataset:
        item_prop = list(item.keys())
        # logging.warning(f"item_prop: {item[item_prop[0]]}")
        out = out + f"      \"{item[item_prop[0]]} ({str(item[item_prop[1]])})\" : {str(item[item_prop[1]])}\n"
    out = out + "```"
    return out

def to_nice_json(v, *args, **kw):
    out = json.dumps(v, indent=2, separators=(',', ': '))
    return out    

def to_nice_yaml(v,indent=2):
    return yaml.dump(v, allow_unicode=True,indent=indent)

def to_yaml(v):
    out = "".join([v.strip() for v in yaml.dump(v,default_flow_style=True).split('\n')])
    return out

def type_debug(o):
    return  o.__class__.__name__







if __name__ == "__main__":
    import sys,inspect
    current_module = sys.modules[__name__]
    safe_globals = {
        name: obj
        for name, obj in inspect.getmembers(current_module, inspect.isfunction)
    }

    if len(sys.argv) != 2:
        print(f"Usage: ./functions.py \"expression\" in {', '.join(safe_globals.keys())}")
        sys.exit(1)



    # Dynamically build safe_globals from functions defined in this module
    py_expr = sys.argv[1]

    try:
        # Evaluate the expression safely
        result = eval(py_expr, {"__builtins__": None}, safe_globals)
        print(result)
    except Exception as e:
        print(f"Error: {e}")
