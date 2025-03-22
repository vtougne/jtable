#!/usr/bin/env python3

from dateutil import parser
print(parser.parse("12 october 2021 at 9 am and 18 minutes"))
# print(parser.parse("one hour before 12 october 2021 at 9 am and 18 minutes"))
print(parser.parse("One year ago at midnight"))