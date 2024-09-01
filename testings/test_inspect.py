#!/usr/bin/env python3

import tabulate
import inspect

# Obtenir tous les membres du module tabulate
members = inspect.getmembers(tabulate)

tablulate_formats = next((value for name, value in members if name == 'tabulate_formats'), None)

print(f"tabulate_formats : {', '.join(tablulate_formats)}")
