#!/usr/bin/env python3
import re, json

# escape_testing.py

json_sample = [{ "name": "John", "age": 30, "city": "New York" },{ "name": "Jane", "age": 25, "city": "Los Angeles" }]


# print(re.escape(json_sample))

the_json = json.dumps(json_sample, indent=4, sort_keys=True)

escaped_json = re.escape(the_json)

print(escaped_json)