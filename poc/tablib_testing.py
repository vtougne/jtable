#!/usr/bin/env python3
import tablib


daniel_tests = [
    ('11/24/09', 'Math 101 Mid-term Exam', 56.),
    ('05/24/10', 'Math 101 Final Exam', 62.)
]

suzie_tests = [
    ('11/24/09', 'Math 101 Mid-term Exam', 56.),
    ('05/24/10', 'Math 101 Final Exam', 62.)
]

# Create new dataset
tests = tablib.Dataset()
tests.headers = ['Date', 'Test Name', 'Grade']

# Daniel's Tests
tests.append_separator('Daniel\'s Scores')

for test_row in daniel_tests:
   tests.append(test_row)

# Susie's Tests
tests.append_separator('Susie\'s Scores')

for test_row in suzie_tests:
   tests.append(test_row)

# Write spreadsheet to disk
with open('grades.xls', 'wb') as f:
    f.write(tests.export('xls'))
