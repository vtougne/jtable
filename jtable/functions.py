#!/usr/bin/env python3

# @property
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
