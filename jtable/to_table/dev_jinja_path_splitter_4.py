#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
dev_jinja_path_splitter_3.py

Ce script découpe un chemin / une chaîne donnée en morceaux
- les blocs entre crochets [ … ] ou accolades { … }
- les séquences de caractères qui ne sont pas entre ces blocs

Chaque morceau est affiché sur sa propre ligne.
"""

import re
import sys
from pathlib import Path

# ------------------------------------------------------------------
# 1️⃣  Fonction principale
# ------------------------------------------------------------------
def split_path_into_tokens(text: str) -> list[str]:
    """
    Retourne une liste de morceaux (tokens) séparés par :
      • les blocs `[ … ]`
      • les blocs `{ … }`
      • les séquences de caractères qui ne contiennent pas
        de crochets ni d’accolades

    Exemple:
        >>> split_path_into_tokens('f1[f2]f3{f4}[f5]')
        ['f1', '[f2]', 'f3', '{f4}', '[f5]']
    """
    # Expression régulière:
    #   1.  \[.*?\]   : un bloc entre crochets (non gourmand)
    #   2.  \{.*?\}   : un bloc entre accolades
    #   3.  [^{}\[\]]+  : toute séquence sans crochets ni accolades
    pattern = r'\[.*?\]|\{.*?\}|[^{}\[\]]+'
    tokens = re.findall(pattern, text)
    return tokens

# ------------------------------------------------------------------
# 2️⃣  Interface en ligne de commande
# ------------------------------------------------------------------
def main(argv: list[str] | None = None) -> None:
    argv = argv or sys.argv[1:]

    if not argv:
        print("Usage : dev_jinja_path_splitter_3.py <chaine>", file=sys.stderr)
        sys.exit(1)

    # On ne traite qu’un seul argument (le « chemin »)
    # Si vous voulez traiter plusieurs, décommentez la boucle suivante
    # for arg in argv:
    #     tokens = split_path_into_tokens(arg)
    #     for t in tokens:
    #         print(t)

    tokens = split_path_into_tokens(argv[0])
    for t in tokens:
        print(t)

# ------------------------------------------------------------------
# 3️⃣  Entry‑point
# ------------------------------------------------------------------
if __name__ == "__main__":
    main()
    