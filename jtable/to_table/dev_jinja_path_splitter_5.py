#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
dev_jinja_path_splitter.py

Découpe une chaîne en tokens :
- blocs entre crochets [ … ]
- blocs entre accolades { … }
- séquences de caractères qui ne contiennent pas
  { } [ ] ou le point .
"""

import re
import sys

def split_path_into_tokens(text: str) -> list[str]:
    """
    Retourne une liste de morceaux (tokens) séparés par :
        * les blocs `[ … ]`
        * les blocs `{ … }`
        * le séparateur `.` (il n’est pas retourné)
        * les séquences de caractères sans { } [ ] ou .
    """
    pattern = r'\[.*?\]|\{.*?\}|[^{}\[\]\.]+'
    return re.findall(pattern, text)

def main(argv: list[str] | None = None) -> None:
    argv = argv or sys.argv[1:]

    if not argv:
        print("Usage : dev_jinja_path_splitter.py <chaine>", file=sys.stderr)
        sys.exit(1)

    tokens = split_path_into_tokens(argv[0])
    for t in tokens:
        print(t)

if __name__ == "__main__":
    main()
