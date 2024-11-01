#!/usr/bin/env python3
import yaml, sys, json, re, os, ast, inspect, datetime, time, logging, logging.config, html, shutil, platform, subprocess
from os import isatty
from sys import exit
# from tabulate import tabulate
import tabulate
from typing import Any, Dict, Optional
try:
    from . import version
except:
    import version

running_platform = platform.system()

if running_platform == "Windows":
    ms_system = os.environ.get('MSYSTEM', '')
    if ms_system == "MINGW64" or ms_system == "CLANGARM64":
        running_os = "Linux"
    elif os.environ.get('TERM', '')  == "xterm":
            running_os = "Linux"
    else:
        running_os = "Windows"
else:
    running_os = running_platform


class CustomFormatter(logging.Formatter):
    def format(self, record):
        frame = inspect.currentframe()
        
        parent_function = inspect.getouterframes(frame)[9].function
        
        record.parent_function = parent_function
              
        try:
            class_name = inspect.currentframe().f_back.f_back.f_back.f_back.f_back.f_back.f_back.f_back.f_back.f_locals["self"].__class__.__name__
        except:
            class_name = "unknown"
        class_name = class_name.lower().replace("jtable","")
        record.class_name = class_name
        return super().format(record)

class CustomFilter(logging.Filter):
    def filter(self, record):
        record.class_name = getattr(record, 'class_name', 'UnknownClass')
        record.parent_function = getattr(record, 'parent_function', 'UnknownFunction')
        
        context = f"{record.class_name}.{record.parent_function}"
        record.fixed_context = f"{context:<50}"
        
        total_message_size = len(record.fixed_context) + len(record.msg)
        # logging.info(f"total_message_size: {str(total_message_size)}")
        # print(f"total_message_size: {str(total_message_size)}")
        if total_message_size > terminal_size.columns:
            record.msg = str(record.msg)[:terminal_size.columns - len(record.fixed_context) ] + '...'

        return True

class _ExcludeErrorsFilter(logging.Filter):
    def filter(self, record):
        """Only lets through log messages with log level below ERROR ."""
        return record.levelno < logging.ERROR

"""
https://stackoverflow.com/questions/14058453/making-python-loggers-output-all-messages-to-stdout-in-addition-to-log-file
"""
logging_config = {
    'version': 1,
    'formatters': {
        'my_formatter': {
            '()': CustomFormatter,
            # 'format': '%(asctime)s (%(lineno)s) %(class_name)s.%(parent_function)s | %(levelname)s %(message)s',
            'datefmt': '%H:%M:%S'

        }
    },
    'filters': {
        'custom': {
            '()': CustomFilter,
        },
    },
    'handlers': {
        'console_stderr': {
            'class': 'logging.StreamHandler',
            'level': 'ERROR',
            'formatter': 'my_formatter',
            'stream': sys.stderr,
            'filters': ['custom'],
        },
    },
    'root': {
        'level': 'NOTSET',
        'handlers': ['console_stderr']
    },
}

class Filters:
    def b64decode(value):
        import base64
        return base64.b64decode(value).decode('utf-8')
    def b64encode(value):
        import base64
        return base64.b64encode(value.encode('utf-8')).decode('utf-8')
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
    def js_wrap(data):
        resources_path = '/'.join(__file__.split('/')[:-1]) + "/resources"
        # js_wrapper_css =  "##replace_tag##js_wrapper.css"
        # js_wrapper_script = "##replace_tag##js_wrapper.js"
        js_wrapper_script =  "Ly8gdmFyIHRhYmxlcyA9IGRvY3VtZW50LmdldEVsZW1lbnRzQnlUYWdOYW1lKCd0YWJsZScpOwpjb25zdCB0YWJsZXMgPSBkb2N1bWVudC5xdWVyeVNlbGVjdG9yQWxsKCJ0YWJsZSIpOwp0b3Bfc2VhcmNoX2JveCA9ICI8aW5wdXQgdHlwZT0ndGV4dCcgaWQ9J3RvcC1zZWFyY2gtY29udGFpbmVyJyBvbmtleXVwPSdmaWx0ZXJBbGxUYWJsZXMoKScgcGxhY2Vob2xkZXI9J2ZpbHRlciBvbiBhbGwgdGFibGVzJz5cbiIKCmxldCBzZWxlY3RlZFRhYmxlID0gbnVsbDsgLy8gVmFyaWFibGUgcG91ciBzdG9ja2VyIGxhIHRhYmxlIHPDqWxlY3Rpb25uw6llCgovLyDDiWNvdXRldXIgcG91ciBkw6l0ZWN0ZXIgbGUgY2xpYyBzdXIgdW5lIHRhYmxlCnRhYmxlcy5mb3JFYWNoKHRhYmxlID0+IHsKICB0YWJsZS5hZGRFdmVudExpc3RlbmVyKCJjbGljayIsIGZ1bmN0aW9uICgpIHsKICAgIHNlbGVjdGVkVGFibGUgPSB0YWJsZTsgLy8gTWV0IMOgIGpvdXIgbGEgdGFibGUgYWN0dWVsbGVtZW50IHPDqWxlY3Rpb25uw6llCiAgfSk7Cn0pOwoKLy8gw4ljb3V0ZXVyIGQnw6l2w6luZW1lbnQgcG91ciBpbnRlcmNlcHRlciBDdHJsICsgQQpkb2N1bWVudC5hZGRFdmVudExpc3RlbmVyKCJrZXlkb3duIiwgZnVuY3Rpb24gKGV2ZW50KSB7CiAgaWYgKGV2ZW50LmN0cmxLZXkgJiYgZXZlbnQua2V5ID09PSAiYSIgJiYgc2VsZWN0ZWRUYWJsZSkgewogICAgZXZlbnQucHJldmVudERlZmF1bHQoKTsgLy8gRW1ww6pjaGUgbGEgc8OpbGVjdGlvbiBkZSB0b3V0ZSBsYSBwYWdlCgogICAgLy8gQ3LDqWF0aW9uIGQndW5lIHPDqWxlY3Rpb24gcG91ciBsYSB0YWJsZSBzw6lsZWN0aW9ubsOpZSBlbiBleGNsdWFudCBsZSBoZWFkZXIKICAgIGNvbnN0IHNlbGVjdGlvbiA9IHdpbmRvdy5nZXRTZWxlY3Rpb24oKTsKICAgIHNlbGVjdGlvbi5yZW1vdmVBbGxSYW5nZXMoKTsgLy8gVmlkYWdlIGRlIGxhIHPDqWxlY3Rpb24gYWN0dWVsbGUKCiAgICBjb25zdCByYW5nZSA9IGRvY3VtZW50LmNyZWF0ZVJhbmdlKCk7CgogICAgLy8gVsOpcmlmaWUgcydpbCB5IGEgYXUgbW9pbnMgdW5lIGxpZ25lIGRhbnMgbGUgdGJvZHkKICAgIGlmIChzZWxlY3RlZFRhYmxlLnRCb2RpZXNbMF0/LnJvd3MubGVuZ3RoID4gMSkgewogICAgICAvLyBTw6lsZWN0aW9uIGRlIHRvdXRlcyBsZXMgbGlnbmVzIHNhdWYgbGEgcHJlbWnDqHJlCiAgICAgIHJhbmdlLnNldFN0YXJ0QmVmb3JlKHNlbGVjdGVkVGFibGUudEhlYWQucm93c1sxXSk7CiAgICAgIHJhbmdlLnNldEVuZEFmdGVyKHNlbGVjdGVkVGFibGUudEJvZGllc1swXS5yb3dzW3NlbGVjdGVkVGFibGUudEJvZGllc1swXS5yb3dzLmxlbmd0aCAtIDFdKTsKCiAgICAgIHNlbGVjdGlvbi5hZGRSYW5nZShyYW5nZSk7IC8vIEFqb3V0IGRlIGxhIHPDqWxlY3Rpb24gZHUgY29udGVudSBkZSBsYSB0YWJsZSBzw6lsZWN0aW9ubsOpZQogICAgfQogIH0KfSk7CgoKJCh0b3Bfc2VhcmNoX2JveCkucHJlcGVuZFRvKCJib2R5Iik7Ci8vIGNvbnNvbGUubG9nKHRvcF9zZWFyY2hfYm94KTsKbGV0IHRhYmxlX2lkID0gMDsKZm9yIChjb25zdCB0YWJsZSBvZiB0YWJsZXMpIHsKICBsZXQgcHJlcGFfc2VhcmNoX2JveGVzID0gIjx0cj5cbiI7CiAgbGV0IGNvbHVtbl9pZCA9IDA7CiAgdGFibGUuaWQgPSB0YWJsZV9pZDsKCiAgZm9yIChjb25zdCBjZWxsIG9mIHRhYmxlLnRIZWFkLnJvd3MuaXRlbSgwKS5jZWxscykgewogICAgY2VsbC5vbmNsaWNrID0gKGZ1bmN0aW9uICh0YWJsZV9pZCwgY29sdW1uX2lkKSB7CiAgICAgIHJldHVybiBmdW5jdGlvbiAoKSB7CiAgICAgICAgc29ydFRhYmxlKHRhYmxlX2lkLCBjb2x1bW5faWQpOwogICAgICB9OwogICAgfSkodGFibGVfaWQsIGNvbHVtbl9pZCk7CiAgICBwcmVwYV9zZWFyY2hfYm94ZXMgPSBwcmVwYV9zZWFyY2hfYm94ZXMgKyAiPHRoPjxpbnB1dCB0eXBlPSd0ZXh0JyBjbGFzcz0nc2VhcmNoLWNvbnRhaW5lcicgb25rZXl1cD0nZmlsdGVyVGFibGUoIiArCiAgICAgIHRhYmxlX2lkICsgIiwiICsgY29sdW1uX2lkICsgIiknIHBsYWNlaG9sZGVyPSdmaWx0ZXIgYnkgIiArIGNlbGwuaW5uZXJUZXh0ICsgIic+PC90aD5cbiI7CiAgICBjb2x1bW5faWQrKzsKICB9CiAgcHJlcGFfc2VhcmNoX2JveGVzID0gcHJlcGFfc2VhcmNoX2JveGVzICsgIjwvdHI+IjsKICAkKHRhYmxlLnRIZWFkKS5wcmVwZW5kKHByZXBhX3NlYXJjaF9ib3hlcyk7CiAgdGFibGVfaWQrKzsKCn0KZnVuY3Rpb24gZmlsdGVyQWxsVGFibGVzKCkgewogIHZhciBzZWFyY2hfaW5wdXQgPSAkKCIjdG9wLXNlYXJjaC1jb250YWluZXIiKS52YWwoKS50b1VwcGVyQ2FzZSgpOwogIHRhYmxlSWQgPSAwOwogIGZvciAoY29uc3QgdGFibGUgb2YgdGFibGVzKSB7CiAgICBmaWx0ZXJUYWJsZSh0YWJsZUlkKTsKICAgIHRhYmxlSWQrKzsKICB9Cn0KCmZ1bmN0aW9uIGZpbHRlclRhYmxlKHRhYmxlX2lkLCBjb2x1bW4gPSAwKSB7CiAgLy8gZmlsdGVyQWxsVGFibGVzKCkKICB2YXIgdG9wX3NlYXJjaF9pbnB1dCA9ICQoIiN0b3Atc2VhcmNoLWNvbnRhaW5lciIpLnZhbCgpLnRvVXBwZXJDYXNlKCk7CgogIHZhciB0YWJsZSA9IGRvY3VtZW50LmdldEVsZW1lbnRCeUlkKHRhYmxlX2lkKTsKICB2YXIgcm93cyA9IEFycmF5LnByb3RvdHlwZS5zbGljZS5jYWxsKHRhYmxlLnRCb2RpZXNbMF0ucm93cyk7CgogIHJvd3MuZm9yRWFjaChmdW5jdGlvbiAocm93KSB7CiAgICB2YXIgY2VsbFRleHQgPSByb3cudGV4dENvbnRlbnQudG9VcHBlckNhc2UoKTsKICAgIGlmIChjZWxsVGV4dC5pbmRleE9mKHRvcF9zZWFyY2hfaW5wdXQpID4gLTEpIHsKICAgICAgcm93LnN0eWxlLmRpc3BsYXkgPSAiIjsKICAgIH0gZWxzZSB7CiAgICAgIHJvdy5zdHlsZS5kaXNwbGF5ID0gIm5vbmUiOwogICAgfQogIH0pOwoKICBsZXQgY29sdW1uSWQgPSAwOwogIGZvciAoY29uc3QgY29sdW1uIG9mIHRhYmxlLnJvd3NbMF0uY2VsbHMpIHsKICAgIGlucHV0ID0gY29sdW1uLnF1ZXJ5U2VsZWN0b3IoImlucHV0IikudmFsdWU7CiAgICBmaWx0ZXJDb2x1bW4odGFibGVfaWQsIGNvbHVtbklkKTsKICAgIGNvbHVtbklkKys7CiAgfQp9CgoKZnVuY3Rpb24gZmlsdGVyQ29sdW1uKHRhYmxlX2lkLCBjb2x1bW4pIHsKICB2YXIgdGFibGUgPSBkb2N1bWVudC5nZXRFbGVtZW50QnlJZCh0YWJsZV9pZCk7CiAgLy8gdmFyIGlucHV0ID0gdGFibGUucm93c1swXS5jZWxsc1tjb2x1bW5dLnF1ZXJ5U2VsZWN0b3IoImlucHV0Iik7CiAgdmFyIGlucHV0ID0gdGFibGUucm93c1swXS5jZWxsc1tjb2x1bW5dLnF1ZXJ5U2VsZWN0b3IoImlucHV0Iik7CiAgdmFyIGZpbHRlclRleHQgPSBpbnB1dC52YWx1ZS50b1VwcGVyQ2FzZSgpOwogIHZhciByb3dzID0gQXJyYXkucHJvdG90eXBlLnNsaWNlLmNhbGwodGFibGUudEJvZGllc1swXS5yb3dzKS5maWx0ZXIocm93ID0+IHJvdy5zdHlsZS5kaXNwbGF5ICE9PSAibm9uZSIpOwogIHJvd3MuZm9yRWFjaChmdW5jdGlvbiAocm93KSB7CiAgICB2YXIgY2VsbFRleHQgPSByb3cuY2VsbHNbY29sdW1uXS50ZXh0Q29udGVudC50b1VwcGVyQ2FzZSgpOwogICAgaWYgKGNlbGxUZXh0LmluZGV4T2YoZmlsdGVyVGV4dCkgPiAtMSkgewogICAgICByb3cuc3R5bGUuZGlzcGxheSA9ICIiOwogICAgfSBlbHNlIHsKICAgICAgcm93LnN0eWxlLmRpc3BsYXkgPSAibm9uZSI7CiAgICB9CiAgfSk7Cn0KCgoKZnVuY3Rpb24gc29ydFRhYmxlKHRhYmxlX2lkLCBjb2x1bW4pIHsKICB2YXIgdGFibGUgPSBkb2N1bWVudC5nZXRFbGVtZW50QnlJZCh0YWJsZV9pZCk7CiAgdmFyIHJvd3MgPSBBcnJheS5wcm90b3R5cGUuc2xpY2UuY2FsbCh0YWJsZS50Qm9kaWVzWzBdLnJvd3MpOwogIHZhciBpc0FzY2VuZGluZyA9IHRhYmxlLnRIZWFkLnJvd3NbMF0uY2VsbHNbY29sdW1uXS5jbGFzc0xpc3QudG9nZ2xlKCJhc2NlbmRpbmciKTsKICB2YXIgbXVsdGlwbGllciA9IGlzQXNjZW5kaW5nID8gMSA6IC0xOwogIHJvd3Muc29ydChmdW5jdGlvbiAoYSwgYikgewogICAgdmFyIGFWYWwgPSBhLmNlbGxzW2NvbHVtbl0udGV4dENvbnRlbnQ7CiAgICB2YXIgYlZhbCA9IGIuY2VsbHNbY29sdW1uXS50ZXh0Q29udGVudDsKICAgIGlmICghaXNOYU4oYVZhbCkgJiYgIWlzTmFOKGJWYWwpKSB7CiAgICAgIGFWYWwgPSBOdW1iZXIoYVZhbCk7CiAgICAgIGJWYWwgPSBOdW1iZXIoYlZhbCk7CiAgICAgIHJldHVybiBtdWx0aXBsaWVyICogKGFWYWwgLSBiVmFsKTsKICAgIH0gZWxzZSB7CiAgICAgIHJldHVybiBtdWx0aXBsaWVyICogYVZhbC5sb2NhbGVDb21wYXJlKGJWYWwpOwogICAgfQogIH0pOwogIHRhYmxlLnRCb2RpZXNbMF0uaW5uZXJIVE1MID0gIiI7CiAgcm93cy5mb3JFYWNoKGZ1bmN0aW9uIChyb3cpIHsKICAgIHRhYmxlLnRCb2RpZXNbMF0uYXBwZW5kQ2hpbGQocm93KTsKICB9KTsKfQo="
        js_wrapper_css = "CnRhYmxlIHsKICAgIGZvbnQtZmFtaWx5OiBhcmlhbCwgc2Fucy1zZXJpZjsKICAgIGJvcmRlci1jb2xsYXBzZTogY29sbGFwc2U7CiAgICAvKiB3aWR0aDogODAlOyAqLwogICAgdGV4dC1hbGlnbjogbGVmdDsKICAgIG1hcmdpbi1sZWZ0OiAyLjUlCiAgfQogIHRoLCB0ZCB7CiAgICBib3JkZXI6IDFweCBzb2xpZCAjZGRkZGRkOwogICAgdGV4dC1hbGlnbjogbGVmdDsKICAgIHBhZGRpbmc6IDhweDsKICB9CiAgdGJvZHkgdHI6bnRoLWNoaWxkKGV2ZW4pIHsKICAgIGJhY2tncm91bmQtY29sb3I6ICNmMmYyZjI7CiAgfQogICN0b3Atc2VhcmNoLWNvbnRhaW5lciB7CiAgICBkaXNwbGF5OiBibG9jazsKICAgIGFsaWduLWl0ZW1zOiBjZW50ZXI7CiAgICAvKiBib3JkZXI6IDFweCBzb2xpZCAjNGYxNjE2OyAqLwogICAgLyogcGFkZGluZzogNXB4OyAqLwogICAgbWFyZ2luOiA1cHggYXV0bzsKICAgIGJvcmRlci1yYWRpdXM6IDVweDsKICAgIC8qIHdpZHRoOiAzMDBweDsgKi8KICB9CiAgLnNlYXJjaC1jb250YWluZXIgewogICAgLyogZGlzcGxheTogZmxleDsgKi8KICAgIGFsaWduLWl0ZW1zOiBjZW50ZXI7CiAgICBib3JkZXI6IDFweCBzb2xpZCAjNGYxNjE2OwogICAgLyogcGFkZGluZzogNXB4OyAqLwogICAgYm9yZGVyLXJhZGl1czogNXB4OwogICAgLyogd2lkdGg6IDMwMHB4OyAqLwogIH0K"
        def load_file_or_decrypt(file_string, expected_file_name):
            # print('coucou')
            # exit
            if file_string.replace("##replace_tag##","") == expected_file_name:
                with open(resources_path + "/" + expected_file_name, 'r') as file:
                    content = file.read()
            else:
                content = Filters.b64decode(file_string)
            return content
        
        js_wrapper_css = load_file_or_decrypt(js_wrapper_css,"js_wrapper.css")
        js_wrapper_script = load_file_or_decrypt(js_wrapper_script,"js_wrapper.js")

        return f"""
          <!DOCTYPE html>
            <html>
              <head>
                <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.4/jquery.min.js"></script>
                
                <style>
                  {js_wrapper_css}
                </style>
                <body>
                  {data}
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
            return Lookup.shell(f"powershell -c \"[math]::Round((Get-Date '{date_str}' -UFormat '%s'))\"")
        else:
            return datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
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

class Inspect:
    def __init__(self):
        self.out = []
    def add_row(self,row):
        # self.out = self.out + [ [row[0][1:]] + [row[1]] ]
        self.out = self.out + [ [row[0]] + [row[1]] ]
        # print([ [row[0]] + [row[1]] ])
    def view_paths(self,dataset,path="", max_depth=0):
        self.cover_data(dataset,path="", max_depth=0)
        return self.out
    def cover_data(self,dataset,path="", max_depth=0):
        if type(dataset) is dict:
            for key,value in dataset.items():
                if " " in str(key):
                    the_path = path + "['" + str(key) + "']"
                else:
                    if path == "":
                        the_path = path + str(key)
                    else:
                        the_path = path + "." + str(key)
                self.cover_data(value,the_path )
        elif type(dataset) is list:
            index=0
            for item in dataset:
                the_path = path + "[" + str(index) + "]"
                # logging.warning(f"the_path: {the_path}")
                index += 1
                self.cover_data(item,the_path)
        else:
            self.add_row([path] + [str(dataset)])

class JtableCli:
    def __init__(self):
        self.path = ""
        self.dataset = {}
        
        global BaseLoader,Environment
        from jinja2 import Environment, BaseLoader
        
    def parse_args(self):

        select = []
        queryset = {}
        self.tabulate_var_name="stdin"
        if 'JTABLE_RENDER' in os.environ:
            render=os.environ['JTABLE_RENDER']
        else:
            render="jinja_native"

        import argparse

        parser = argparse.ArgumentParser(description='Tabulate your JSON/Yaml data and transform it using Jinja',add_help=False)

        parser.add_argument("-h", "--help",action="store_true", help = "Show this help")
        parser.add_argument("-p", "--json_path", help = "json path")
        parser.add_argument("-s", "--select", help = "select key_1,key_2,...")
        parser.add_argument("-w", "--when", help = "key_1 == 'value'")
        parser.add_argument("-f", "--format", help = "Table format applyed in simple,json,th,td... list below")
        parser.add_argument("-us", "--unselect", help = "Unselect unwanted key_1,key_2,...")
        parser.add_argument("-q", "--query_file", help = "Load jtbale query file")
        parser.add_argument("--inspect", action="store_true", help="Inspect stdin")
        parser.add_argument("-jf", "--json_file", help = "Load json")
        parser.add_argument("-jfs", "--json_files", action='append', help = "Load multiple Json's")
        parser.add_argument("-yfs", "--yaml_files", action='append', help = "Load multiple Yaml's")
        parser.add_argument("-vq", "--view_query", action="store_true", help = "View query")
        parser.add_argument('--version', action='version', version=version.__version__)
        parser.add_argument('-v', '--verbose', action='count', default=0, help='Verbosity level')
        parser.add_argument('-d', '--debug', action="store_true", help='Add code row number in log')
        parser.add_argument( '--stdout', help='Ovewrite applyed ouput filter, default: {{ stdin | jtable(queryset=queryset) }}')

        args = parser.parse_args()
        global terminal_size
        terminal_size = shutil.get_terminal_size((80, 20))  # Largeur par défaut 80, hauteur 20
        # logging.warning(f"terminal_size: {terminal_size}")  

        if os.environ.get('JTABLE_LOGGING') == "DEBUG" or args.debug:
            logging_config['formatters']['my_formatter']['format'] = '%(asctime)s (%(lineno)s) %(class_name)s.%(parent_function)-16s | %(levelname)s %(message)s'
        else:
            logging_config['formatters']['my_formatter']['format'] = '%(asctime)s %(class_name)s.%(parent_function)-15s | %(levelname)s %(message)s'

        
        if args.verbose == 0:
            logging_config['handlers']['console_stderr']['level'] = 'WARNING'
        if args.verbose == 1:
            logging_config['handlers']['console_stderr']['level'] = 'INFO'
        elif args.verbose == 2:
            logging_config['handlers']['console_stderr']['level'] = 'DEBUG'
        logging.config.dictConfig(logging_config)
        logging.info(f"running_os: {running_os}")
        
        # global logging_format
        # logging_format = '%(asctime)s (%(lineno)s) %(class_name)s.%(parent_function)s | %(levelname)s %(message)s'
        
        if args.query_file:
            logging.info(f"loading query file: {args.query_file}")
            with open(args.query_file, 'r') as file:
                try:
                    query_file = yaml.safe_load(file)
                except Exception as error:
                    logging.error(f"Fail to load query file {args.query_file}, check Yaml format")
                    logging.error(f"error was:\n{error}")
                    exit(2)
                
            if 'vars' in query_file:
                if 'queryset' in query_file['vars']:
                    queryset = query_file['vars']['queryset']
            if 'secrets' in query_file:
                global secrets
                secrets = query_file['secrets']

                
        is_pipe = not isatty(sys.stdin.fileno())

        stdin=""
        if is_pipe:
            logging.info("stdin is a pipe")
            for line in sys.stdin:
                stdin = stdin + line
            # self.dataset = { self.tabulate_var_name: yaml.safe_load(stdin) }
            self.dataset = { self.tabulate_var_name: stdin }

        if not is_pipe and not args.json_file and not args.json_files and not args.query_file and not args.yaml_files and not args.stdout:

            parser.print_help(sys.stdout)
            jtable_core_filters = [name for name, func in inspect.getmembers(Filters, predicate=inspect.isfunction)]
            jtable_lookups = [name for name, func in inspect.getmembers(Lookup, predicate=inspect.isfunction)]
            print(f"\njtable core filters:\n   {', '.join(jtable_core_filters)}\n")
            tablulate_formats = next((value for name, value in inspect.getmembers(tabulate) if name == 'tabulate_formats'), None)
            print(f"table formats:\n   {', '.join(tablulate_formats)}\n")
            print(f"jtable lookups:\n   {', '.join(jtable_lookups)}\n")
            exit(1)

        if args.json_file:
            logging.info(f"loading json file: {args.json_file}")
            got_variable_name_pattern = r'^\{[a-zA-Z_1-9]+\}:.*'
            if re.match(got_variable_name_pattern, args.json_file):
                self.tabulate_var_name = args.json_file[1:].split('}:')[0]
                file_name = ':'.join(args.json_file.split(':')[1:])
            else:
                self.tabulate_var_name = "input_1"
                file_name = args.json_file
            logging.info(f"file_name: {file_name}, self.tabulate_var_name: {self.tabulate_var_name}")
            # exit(0)
            with open(file_name, 'r') as input_yaml:
                self.dataset = {**self.dataset, **{ self.tabulate_var_name: yaml.safe_load(input_yaml) } }
                
        # logging.info(f"queryset['path']: {queryset['path']}") ; exit(0)
                
        def load_multiple_inputs(file_search_string,format):
            logging.info(f"loading {format} files: {file_search_string}")
            err_help = f"\n[ERROR] {format}_files must looks like this:\n\n\
                jtable --{format}_files \"{{target_var_name}}:folder_1/*/*/config.yml\"\n"
            got_variable_name_pattern = r'^\{[a-zA-Z_1-9]+\}:.*'
            if re.match(got_variable_name_pattern, file_search_string):
                logging.info(f"Contains variable name file_names: {file_search_string}")
                splitted_path = file_search_string[1:].split('}:')
                path=splitted_path[1]
                self.tabulate_var_name = splitted_path[0]
            else:
                self.tabulate_var_name = "input_1"
                logging.info(f"Adding var_name: {self.tabulate_var_name}")
                path = file_search_string
            logging.info(f"var_name: {self.tabulate_var_name}, path: {path}")
            # if file_search_string[0] != "{":
            #     pass
            #     # logging.error(err_help)
            #     # exit(1)
            # else:

            # print(tabulate_var_name) ; exit(0)
            # path = file_search_string[len(self.tabulate_var_name) + 3 :]
            logging.info(f"path: {path}")
            
            if running_os == "Windows":
                cmd = f"dir /s /b {path}"
                logging.info(f"cmd: {cmd}")
                files_str = os.popen("dir /s /b " + path).read()
            else:
                files_str = os.popen("ls -1 " + path).read()
            # for windows syntax will be --> # dir /s /b data\*config.yml
            file_list_dataset = []
            for file_name_full_path in files_str.split('\n'):
                if file_name_full_path != '':
                    with open(file_name_full_path, 'r') as input_yaml:
                        try:
                            file_content =  yaml.safe_load(input_yaml)
                            if running_os == "Windows":
                                sep = "\\"
                                file_path = sep.join(file_name_full_path.split('\\')[:-1])
                                file_name = file_name_full_path.split('\\')[-1]
                            else:
                                file_path = "/".join(file_name_full_path.split('/')[:-1])
                                file_name = file_name_full_path.split('/')[-1]
                            file = { 
                                    "name": file_name,
                                    "path": file_path,
                                    "content": file_content
                                    }
                            file_list_dataset = file_list_dataset + [{ **file }]
                        except Exception as error:
                            logging.warning(f"fail loading file {file_name_full_path}, skipping")
            self.dataset = {**self.dataset, **{ self.tabulate_var_name: file_list_dataset } }
        
        if args.json_files:
            for file in args.json_files:
                load_multiple_inputs(file,"json")

        if args.yaml_files:
            for file in args.yaml_files:
                load_multiple_inputs(file,"yaml")
        
        if args.json_path:
            new_path = args.json_path
            expr_end_by_braces=(re.sub('.*({).*(})$',r'\1\2',args.json_path))
            if expr_end_by_braces != "{}":
                new_path = new_path + "{}"
            queryset['path'] = new_path

        if args.query_file:
            if 'sources' in query_file:
                for source_name in query_file['sources']: 
                    if 'json_files' in query_file['sources'][source_name]:
                        expr = query_file['sources'][source_name]['json_files']
                        expr_with_name = f"{{{source_name}}}:{expr}"
                        load_multiple_inputs(expr_with_name,"json")
                    if 'yaml_files' in query_file['sources'][source_name]:
                        expr = query_file['sources'][source_name]['yaml_files']
                        expr_with_name = f"{{{source_name}}}:{expr}"
                        load_multiple_inputs(expr_with_name,"yaml")
                    if 'shell' in query_file['sources'][source_name]:
                        shell_command = query_file['sources'][source_name]['shell']
                        jinja_eval = Templater(template_string=str(shell_command), static_context=self.dataset).render({},eval_str=True)
                        logging.info(f"Launch shell, cmd: {jinja_eval}")
                        # shell_output = subprocess.check_output(shell_command, shell=True,universal_newlines=True)
                        shell_output = Lookup.shell(jinja_eval)
                        self.dataset = {**self.dataset, **{ source_name: shell_output } }

                    if 'env' in query_file['sources'][source_name]:
                        env_var = query_file['sources'][source_name]['env']
                        env_value = Lookup.env(env_var)
                        # print(f"env_value: {env_value}")
                        # exit(0)
                        self.dataset = {**self.dataset, **{ source_name: env_value } }
            if 'vars' in query_file:
                vars = {}
                for key,value in query_file['vars'].items():
                    logging.info(f"Covering vars, key: {key}")
                    jinja_eval = Templater(template_string=str(value), static_context=self.dataset).render({},eval_str=True)
                    vars.update({key: jinja_eval})
                    self.dataset = {**self.dataset,**vars, **{"vars": vars}}

            
        if 'select' in queryset:
            select = queryset['select']

        if args.unselect:
           queryset['unselect'] = args.unselect

        if args.select:
            queryset['select'] = args.select

        if args.when:
            queryset['when'] = args.when

        if not 'path' in queryset:
            queryset['path'] = "{}"
                    
        if not "format" in queryset:
            queryset['format'] = 'simple'

        if args.format:
            queryset['format'] = args.format

        if args.view_query:
            queryset['format'] = "th"
            
        # def out_expr_fct(select,path,format):
            # return "{{ " + self.tabulate_var_name + " | jtable(queryset=queryset) }}"
            
        # out_expr = out_expr_fct(str(select), queryset['path'] , queryset['format'])
        if args.stdout:
            out_expr = args.stdout
        else:
            if self.tabulate_var_name == "stdin":
                out_expr = "{{ " + self.tabulate_var_name + " | from_json_or_yaml | jtable(queryset=queryset) }}"
            else:
                out_expr = "{{ " + self.tabulate_var_name + " | jtable(queryset=queryset) }}"
        # print(out_expr) ; exit(0)
        if args.query_file:
            if 'stdout' in query_file:
                out_expr = query_file['stdout']


                    
            
        if args.inspect:
            if self.tabulate_var_name == "stdin":
                inspected_paths = Inspect().view_paths(yaml.safe_load(stdin))
            else:
                inspected_paths = Inspect().view_paths(self.dataset[self.tabulate_var_name])
            tbl = tabulate.tabulate(inspected_paths,['path','value'])
            print(tbl)
            return



        if args.view_query:
            out = Templater(template_string=out_expr, static_context={**self.dataset,**{"queryset": queryset}}).render({},eval_str=True)
            query_file_out = {}
            query_set_out = {}
            fields = out
            if select == []:
                for field in fields:
                    select = select + [ {'as': field, 'expr':field }  ]
            query_set_out['path'] = queryset['path']
            query_set_out['select'] = select
            if args.when:
                query_set_out['when'] = args.when
            # query_file_out['queryset'] = query_set_out
            query_file_out['vars'] = {'queryset': query_set_out }
            # query_file_out['out'] = out_expr_fct('select', queryset['path'] , 'simple')
            query_file_out['stdout'] = out_expr
            yaml_query_out = yaml.dump(query_file_out, allow_unicode=True,sort_keys=False)
            print(yaml_query_out)
        else:
            logging.info(f"queryset: {queryset}")
            out = Templater(template_string=out_expr, static_context={**self.dataset,**{"queryset": queryset}}).render({},eval_str=False)
            print(out)

class JtableCls:
    def __init__(self, render="jinja_native"):
        logging.info(f"Initilizing render: {render}")
        self.td = []
        self.th = []
        self.table_headers = []
        self.json = []
        self.render = render
        self.splitted_path = []
        self.when = []
        self.select = []
        self.unselect = []
        self.views = {}
        self.path = "{}"
        self.format = ""

        if self.render == "jinja_ansible":
            global Templar,AnsibleContext,AnsibleEnvironment
            from ansible.template import Templar,AnsibleContext,AnsibleEnvironment
            from ansible.parsing.dataloader import DataLoader
            self.loader = DataLoader()
        elif self.render == "jinja_native":
            self.loader=BaseLoader()
            self.tenv = Environment(loader=self.loader)
            jtable_core_filters = [name for name, func in inspect.getmembers(Filters, predicate=inspect.isfunction)]
            for filter_name in jtable_core_filters:
                self.tenv.filters[filter_name] = getattr(Filters, filter_name)
        elif self.render == "jinja_ansible_extensions":
            self.tenv = Environment(extensions=['jinja2_ansible_filters.AnsibleCoreFiltersExtension'])
        else:
            logging.error("Unknown render option")
            exit(1)
    
    def cross_path(self, dataset, path, cross_path_context = {} ):
        level = len(path)
        if level > 1:
            # logging.info(f"path: {path}")
            next_path = path[1:]
            current_path = str(path[0])
            current_path_value = "unknown"
            if current_path[0:2] == "['":
                current_path_value = current_path[2:-2]
                if current_path_value in list(dataset):
                    self.cross_path(dataset[current_path_value], next_path, cross_path_context = cross_path_context)
                else:
                    logging.error('keys dataset were:')
                    logging.error(list(dataset))
                    logging.error(current_path + " was not found in dataset level: " + str(len(self.splitted_path) - level))
                    # exit(1)
            elif current_path[0] == ".":
                current_path_value = current_path[1:]
                if current_path_value in list(dataset):
                    self.cross_path(dataset[current_path_value],next_path, cross_path_context = cross_path_context)
                else:
                    logging.info(list(dataset))
                    logging.error(current_path + " was not found in dataset level: " + str(len(self.splitted_path) - level))
                    # exit(1)
                    
            elif current_path[0] == "[":
                current_path_value = current_path[1:-1]
                if int(current_path_value) <= len(dataset):
                    self.cross_path(dataset[int(current_path_value)],next_path, cross_path_context = cross_path_context)
                    
                else:
                    logging.error( current_path + " was not found in dataset level: " + str(len(self.splitted_path) - level))
                    exit(1)
            
            elif current_path[0] == "{":
                item_name = current_path[1:-1]
                if level > 0:
                    if type(dataset) is dict:
                        for key,value in dataset.items():
                            next_path = path[1:]
                            # new_cross_path_context = {item_name: {"key": key, "value": value}}
                            cross_path_context = { **cross_path_context, **{item_name: {"key": key, "value": value}}}
                            self.cross_path(dataset[key],next_path,cross_path_context=cross_path_context)
                            
                    elif type(dataset) is list:
                        index = 0
                        for item in dataset:
                            next_path = path[1:]
                            # new_cross_path_context = { item_name: item }
                            cross_path_context = { **cross_path_context, **{ item_name: item }}
                            self.cross_path(dataset[index],next_path,cross_path_context=cross_path_context)
                            index += 1
                else:
                    logging.info(f"item_name: {item_name}")
                    self.render_table(dataset=dataset,select=self.select, item_name = item_name, context = cross_path_context)
            else:
                logging.info("[ERROR] was looking for path...")
                exit(1)
        else:
            item_name = path[0][1:-1]
            # logging.info(f"item_name: {item_name}")
            self.render_table(dataset=dataset,select=self.select, item_name = item_name, context=cross_path_context)
    
    def render_object(self, dataset, path="{}", select=[], unselect=[], views={}, when=[], format="", context={}, queryset={}):
        # exit(0)
        for query_item,query_data in queryset.items():
            logging.info(f"query_item: {query_item}")
            # exit(0)
            if query_item == "select":
                self.select = query_data
            elif query_item == "unselect":
                self.unselect = query_data
            elif query_item == "path":
                # logging.info(f"self.path query_data: {query_data}")
                self.path = query_data
            elif query_item == "views":
                self.views = query_data
            elif query_item == "when":
                self.when = query_data
            elif query_item == "format":
                self.format = query_data
            else:
                raise Exception(f"the queryset argument contains a non accepted key: {query_item}")
            
        self.path = path if path != "{}" else self.path
        self.select = select if select != [] and select != "" else self.select
        self.unselect = unselect if unselect != [] and unselect != "" else self.unselect
        self.views = views if views != {} else self.views
        # self.when = when if when != [] else self.when
        self.when = when if when != [] and when != "" else self.when
        logging.info(f"when: {self.when.__class__.__name__}")
        if self.when.__class__.__name__ == "str":
            self.when = self.when.split(',')
        logging.info(f"when: {self.when}")
        # exit(0)
        self.format = format if format != "" else self.format
        self.context = context
        logging.info(f"unselect: {self.unselect}")

        self.dataset = dataset
        
        for k,v in self.views.items():
            self.views = {**self.views, **{ k: '{{' + str(v) + '}}' } }

        self.splitted_path = JinjaPathSplitter().split_path(self.path)
        if self.splitted_path[0] == "['']":
            self.splitted_path[0] = "['input']"
            self.dataset = {"input": self.dataset}
        
        logging.info(f"Crossing paths")
        # for item in inspect.stack():
        #     logging.info(f"  {item[3]}")
        # self.cross_path(self.dataset, self.splitted_path, cross_path_context=self.views )
        self.cross_path(self.dataset, self.splitted_path )

        if self.format == "json":
            return json.dumps(self.json)
        elif self.format == "th":
            return self.th
        elif self.format == "td":
            return self.td
        elif self.format == "github":
            return tabulate.tabulate(self.td,self.th,tablefmt="github")
        elif self.format == "html":
            return tabulate.tabulate(self.td,self.th,tablefmt="unsafehtml")
        else:
            return tabulate.tabulate(self.td,self.th,tablefmt=self.format)
        
        # return out_return[self.format]
    
    def render_table(self, dataset, select=[], item_name='', context={}):
        stylings = []
        logging.info(f"unselect: {self.unselect}")
        if len(select) > 0:
            logging.info(f"select: {select.__class__.__name__}")
            if select.__class__.__name__ == "str":
                expressions = fields_label = select.split(",")
            else:
                expressions = [expressions['expr'] for expressions in select]
                stylings = [(stylings['styling'] if 'styling' in stylings else []) for stylings in select]
                fields_label = [fields_label['as'] for fields_label in select]
        else:
            fields = path_auto_discover().discover_paths(dataset)
            fields_label = list(map(lambda item: '.'.join(item), fields))
            item_name = 'item' if item_name == '' else item_name
            expressions = list(map(lambda item:  item_name + '[\'' + '\'][\''.join(item) + '\']' , fields))
        
        if self.unselect != [] and self.unselect != "":
            for field in self.unselect.split(','):
                if field in fields_label:
                    index = fields_label.index(field)
                    del expressions[index]
                    del fields_label[index]
                    if stylings != []:
                        del stylings[index]

        logging.info(f"expressions: {expressions}")
        logging.info(f"fields_label: {fields_label}")
        # exit()

        if type(dataset) is dict:
            dataset_to_cover = []
            for key,value in dataset.items():
                dataset_to_cover = dataset_to_cover + [ {'key': key, 'value': value} ]
        elif type(dataset) is list:
            dataset_to_cover = dataset
        else:
            raise Exception('[ERROR] dataset must be a dict or list, was: ' + str(type(dataset)))

        # static_context = {"dataset": dataset, **context}
        column_templates = []
        for expr in expressions:
            jinja_expr = '{{ ' + expr  + ' }}'
            column_templates = column_templates + [Templater(template_string=jinja_expr, static_context={**context,**self.context})]

        view_templates = []
        for var_name,var_data in self.views.items():
            view_templates = view_templates + [Templater(template_string=str(var_data), static_context={**context,**self.context})]

        when_templates = []
        for condition in self.when:
            when_templates = when_templates + [Templater(template_string=condition, static_context={**context,**self.context})]



        for item in dataset_to_cover:
            row = []
            json_dict = {}

            def when(when=[],when_context={}):
                condition_test_result = "True"
                for condition in when:
                    jinja_expr = '{{ ' + condition  + ' }}'
                    logging.info(f"item_name: {item_name}")
                    logging.info(f"when: {when}")
                    # loop_condition_context = item
                    # loop_condition_context = { item_name: item } if item_name != '' else item
                    loop_condition_context = { item_name: item } if (item_name != '' and item_name != 'item' ) else item
                    logging.info(f"loop_condition_context: {loop_condition_context}")
                    # loop_condition_context = { item_name: item }
                    condition_template = Templater(template_string=jinja_expr, static_context= {**when_context,**loop_condition_context})
                    condition_test_result = condition_template.render({},eval_str=True)
                    if condition_test_result == "False":
                        break
                return condition_test_result

            for expr in expressions:
                loop_context = { item_name: item } if item_name != '' else item
                view_context = {}
                view_index = 0
                for var_name,var_data in self.views.items():
                    templated_var = view_templates[view_index].render({**loop_context,**view_context},eval_str=True)
                    view_context.update({ var_name: templated_var })
                    view_index += 1

            if self.when != []:
                condition_test_result = when(when = self.when, when_context = {**self.context,**context,**view_context})
            else:
                condition_test_result = "True"
            
                
            if condition_test_result == "True":
                column_index = 0
                for expr in expressions:
                    loop_context = { item_name: item } if item_name != '' else item
                    try:
                        value_for_json = value = column_templates[column_index].render({**loop_context,**view_context},eval_str=True,strict_undefined=False)
                    except:
                        break
                    del loop_context
                    if self.format == "html":
                        value = html.escape(str(value))
                    key = fields_label[column_index]
                    if value_for_json != None:
                        json_value = { key: value_for_json }
                        json_dict = {**json_dict, **json_value }
                        del json_value
                        del value_for_json
                    if stylings != []:
                        styling = stylings[column_index]
                        condition_color = "True"
                        # if styling != []:
                        for styling_attributes in styling:
                            color_conditions = [color_conditions for color_conditions in  styling_attributes['when'] ]
                            # logging.info(color_conditions)
                            condition_color = when(when = color_conditions, when_context = {**context,**view_context})
                            if condition_color == "True":
                                value = Styling().apply(value = value,format=self.format, styling_attributes = styling_attributes)

                    row = row + [ value ]
                    del value
                    column_index += 1
                self.json = self.json + [ json_dict ]
                self.td = self.td + [ row ]
        
        
        if fields_label is None:
            headers = list(map(lambda item: '.'.join(item), expressions))
            fields_label = headers
        
        self.th = fields_label
            
        try:
            self.json_content = json.dumps(self.json)
        except Exception as error:

            logging.info(tabulate(self.td,self.th))
            logging.error(f"\nSomething wrong with json rendering, Errors was:\n  {error}")
            exit(2)

class Lookup:
    def env(var_name,**kwargs):
        if var_name not in os.environ:
            if 'default' in kwargs:
                return kwargs['default']
            else:
                raise Exception(f"Environment variable {var_name} not found")
        else:
            return os.environ[var_name]

    def shell(cmd,default=None):
        shell_output = subprocess.check_output(cmd, shell=True,universal_newlines=True)
        return shell_output
    
class path_auto_discover:
    def __init__(self):
        self.paths = []
        self.fields = []
        self.raw_rows = []
        
    def cover_paths(self,dataset,path=[]):
        if type(dataset) is dict:
            for key,value in dataset.items():
                the_path = path + [ key ]
                self.cover_paths(value,the_path )
        elif type(dataset) is list:
            # pass
            if len(dataset) > 0:
                index=0
                for item in dataset:
                    self.cover_paths(item,path)
            else:
                if path[1:] not in self.fields:
                    self.fields = self.fields + [path[1:]]
        else:
            self.paths = self.paths + [ path + [dataset] ]
            if path[1:] not in self.fields:
                self.fields = self.fields + [path[1:]]

    def discover_paths(self,dataset):
        
        # when input is dict transform as list like dict2items
        if type(dataset) is dict:
            dataset_as_list = []
            for key,value in dataset.items():
                dataset_as_list = dataset_as_list + [ {'key': key, 'value': value} ]
            dataset = dataset_as_list
        index=0

        try:
            for item in dataset:
                for key,value in item.items():
                    self.cover_paths(value,[str(index),key])
                    index+=1
                self.raw_rows = self.raw_rows + [ item ]
        except(Exception) as error:
            logging.error(f"Something wrong with your dataset, error was:")
            logging.error(f"    {error}")
            exit(1)

        return self.fields

class JinjaPathSplitter:

    def cover_path(self,path=""):
        if len(path) > 0:
            reference_found = "no"
            if path[0:2] == "['":
                if "']" in path:
                    left_part = path[2:].split("']")[0]
                    if left_part == "":
                        logging.info("Error dict expression empty, starting at " + str("".join(self.path_list)) )
                        exit(1)
                    else:
                        left_part = "['" + left_part + "']"
                        remaining_path = path[len(left_part):]
                        self.path_list = self.path_list + [ left_part ]
                        if remaining_path != "":
                            self.cover_path(remaining_path)
                        reference_found = "yes"
                        
                else:
                    logging.info('error expect "\']" was not found')
                    exit(1)
                
            if path[0] == ".":
                left_part = re.sub(r'^([^[^{^\.]*).*',r'.\1',path[1:])
                remaining_path = path[len(left_part):]
                self.path_list = self.path_list + [ left_part ]
                if remaining_path != "":
                    self.cover_path(remaining_path)
                
            elif path[0] == "{":
                if "}" in path:
                    left_part = re.sub(r'^([^}]*).*',r'\1}',path)
                    remaining_path = path[len(left_part):]
                    self.path_list = self.path_list + [ left_part ]
                    if remaining_path != "":
                        self.cover_path(remaining_path)
                else:
                    logging.info('error expect "}" was not found')
                    exit(1)
                    
            elif path[0] == "[":
                if reference_found == "no":
                    if "]" in path:
                        left_part = re.sub(r'^([^]]*).*',r'\1]',path)
                        remaining_path = path[len(left_part):]
                        self.path_list = self.path_list + [ left_part ]
                        if remaining_path != "":
                            self.cover_path(remaining_path)
                    else:
                        logging.info('error expect "}" was not found')
                        exit(1)
                    
            else:
                if path == "" or path[0:2] == "['" or path[0] == "{" or path[0] == ".":
                    pass
                else:
                    logging.info(path[0:2])
                    logging.info('Error what know to do with ' + path)
                    logging.info('Error hapenned there ' + ''.join(self.path_list))
                    exit(1)
                
    def extract_var_from_path(self,path):
        if len(path) > 0:
            left_part = re.sub(r'^([^[^\.^{]*).*',r'\1',path)
            self.path_list = [ "['" + left_part + "']" ]
            remaining_path = path[len(left_part):]
            return remaining_path
    
    def split_path(self,path=""):
        remaining_path = self.extract_var_from_path(path)
        # logging.info('debug remaining_path: ' + remaining_path)
        self.cover_path(remaining_path)
        return self.path_list

class Styling:
    def __init__(self):
        self.color_table = [{"name":"Black","ansi_code":30,"hex":"#000000"},{"name":"Red","ansi_code":31,"hex":"#FF0000"},{"name":"Green","ansi_code":32,"hex":"#008000"},{"name":"Yellow","ansi_code":33,"hex":"#FFFF00"},{"name":"Blue","ansi_code":34,"hex":"#0000FF"},{"name":"Magenta","ansi_code":35,"hex":"#FF00FF"},{"name":"Cyan","ansi_code":36,"hex":"#00FFFF"},{"name":"White","ansi_code":37,"hex":"#FFFFFF"},{"name":"Gray","ansi_code":90,"hex":"#808080"},{"name":"LightRed","ansi_code":91,"hex":"#FF8080"},{"name":"LightGreen","ansi_code":92,"hex":"#80FF80"},{"name":"LightYellow","ansi_code":93,"hex":"#FFFF80"},{"name":"LightBlue","ansi_code":94,"hex":"#8080FF"},{"name":"LightMagenta","ansi_code":95,"hex":"#FF80FF"},{"name":"LightCyan","ansi_code":96,"hex":"#80FFFF"},{"name":"LightWhite","ansi_code":97,"hex":"#F0F0F0"}]
    
    def get_color(self,color_name="",format=""):
        return [color for color in self.color_table if color['name'].lower() == color_name.lower() ][0][format]

    def apply(self,value="",format="",styling_attributes={}):
        # if format == "simple":
            logging.info(f"style: {styling_attributes['style']}")
            if "style" in styling_attributes:
                style_value = styling_attributes['style'].split(": ")[1]
            else:
                style_value = "white"
            text_formating = 0
            formating = ""
            if "formating" in styling_attributes:
                formating = styling_attributes['formating']
            if formating == "normal" or formating == "":
                text_formating = 0
            elif formating == "bold":
                text_formating = 1
            elif formating == "dim":
                text_formating = 2
            elif formating == "italic":
                text_formating = 3
            elif formating == "underlined":
                text_formating = 4
            else:
                logging.error(f"Unknown formating: {formating}")
                exit(1)
            logging.info(f"style_value: {style_value}")
            color_value = self.get_color(style_value,"ansi_code")
            if format == "simple":
                value_colorized = f"\x1b[{text_formating};{color_value}m{value}\x1b[0m"
            elif format == "github":
                # value_colorized = f"\x1b[{text_formating};{color_value}m{value}\x1b[0m"
                # value_colorized = f"$`\textcolor{{red}}{{\text{{Smith}}`$"
                value_colorized = r"$`\textcolor{"+ style_value + r"}{\text{" + value + "}}`$"
            elif format == "html":
                value_colorized = r'<span style="' + styling_attributes['style'] + r';">' + value + r"</span>"
            else:
                value_colorized = f"\x1b[{text_formating};{color_value}m{value}\x1b[0m"

            logging.info(f"format: {format}")   
            return value_colorized

class Templater:
    def __init__(self, template_string = "", static_context = {}):
        if 'Environment' not in sys.modules:
            from jinja2 import Environment, StrictUndefined
        env = Environment(undefined=StrictUndefined)
        
        jtable_core_filters = [name[0] for name in inspect.getmembers(Filters, predicate=inspect.isfunction)]
        for filter_name in jtable_core_filters:
            env.filters[filter_name] = getattr(Filters, filter_name)

        ####################  Add lookup function ####################
        jtable_core_lookups = [name[0] for name in inspect.getmembers(Lookup, predicate=inspect.isfunction)]
        logging.info(f"jtable_core_lookups: {jtable_core_lookups}")
        class lookup_fct(object):
            def process_lookup(self,*args, **kwargs):
                if len(args) == 0 and len(kwargs) == 0:
                    logging.error("lookup function must have at least one argument in:")
                    exit(3)
                if args[0] not in jtable_core_lookups:
                    logging.error(f"lookup function {args[0]} not found in {', '.join(jtable_core_lookups)}")
                    exit(3)
                method_to_call = getattr(Lookup, args[0], None)
                try:
                    res = method_to_call(*args[1:],**kwargs)
                except Exception as error:
                    logging.error(f"Failed to call lookup function {args[0]}, error was:\n  {str(error)}")
                    exit(3)
                return res

            
        lookup = lambda: lookup_fct().process_lookup
        static_context = {**static_context, **{"lookup": lookup()}}

        ##############################################################
        try:
            self.template = env.from_string(template_string, globals=static_context)
        except Exception as error:
            logging.error(f"Failed to compile template, error was:\n  {str(error)}")
            exit(3)
    
    def render(self, vars, eval_str = False, strict_undefined = True):

        try:
            out_str = self.template.render(vars)
        except Exception as error:
            if str(error)[0:30] == "'dict object' has no attribute" or str(error)[0:30] == "'list object' has no attribute":
                if strict_undefined == True:
                    logging.error(f"Failed while rendering context, error was:\n  {str(error)}")
                    exit(3)
                else:
                    out = out_str =""
            else:
                out = out_str = error
                logging.error(f"Failed while rendering context, error was:\n  {str(error)}")
                raise out
            
        if eval_str == True:
            try:
                expr = ast.parse(out_str, mode='eval').body
                expr_type = expr.__class__.__name__
                if expr_type == 'List' or expr_type == 'Dict':
                    out =  ast.literal_eval(out_str)
                elif expr_type == 'Name':
                    out = out_str
                else:
                    out = str(out_str)
            except:
                out = out_str
        else:
            out = out_str
                    
        return out

def main():
    JtableCli().parse_args()
    return

if __name__ == '__main__':
    main()