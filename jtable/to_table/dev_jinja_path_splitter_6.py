#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

def split_path(text: str) -> list[str]:
    """
    Découpe une chaîne selon les règles suivantes :

    * '[' et '{' ouvrent un bloc qui se termine au premier
      ']' ou '}' non échappé. Le bloc complet, avec ses délimiteurs,
      est renvoyé comme un seul token.
    * '.' est un séparateur. Les points non échappés délimitent les tokens.
    * Tout caractère spécial de '[]{}.' précédé d'un antislash est
      traité comme un caractère littéral (l'antislash est supprimé).
    * Les autres caractères sont ajoutés au token courant.
    """
    specials = set('[]{}.')
    opening = {'[': ']', '{': '}'}
    tokens = []
    current = []

    i = 0
    n = len(text)
    while i < n:
        ch = text[i]

        # Gestion des échappements
        if ch == '\\':
            if i + 1 < n and text[i + 1] in specials:
                current.append(text[i + 1])
                i += 2
            else:
                current.append('\\')
                i += 1
            continue

        # Début d'un bloc
        if ch in opening:
            if current:
                tokens.append(''.join(current))
                current = []
            block_start = ch
            block_end = opening[ch]
            block = [block_start]
            i += 1  # passe le délimiteur d’ouverture

            while i < n:
                c = text[i]
                # Échappements à l’intérieur du bloc
                if c == '\\' and i + 1 < n and text[i + 1] in specials:
                    nxt = text[i + 1]
                    if nxt == block_end:
                        block.append(block_end)
                        i += 2
                        continue
                    else:
                        block.append(nxt)
                        i += 2
                        continue

                if c == block_end:
                    block.append(c)
                    i += 1
                    break

                block.append(c)
                i += 1

            tokens.append(''.join(block))
            continue

        # Séparateur '.'
        if ch == '.':
            if current:
                tokens.append(''.join(current))
                current = []
            i += 1
            continue

        # Tous les autres caractères (y compris les crochets fermants hors bloc)
        current.append(ch)
        i += 1

    if current:
        tokens.append(''.join(current))

    return tokens

def main(argv: list[str] | None = None) -> None:
    argv = argv or sys.argv[1:]
    if not argv:
        print("Usage: dev_jinja_path_splitter_6.py <chaine>", file=sys.stderr)
        sys.exit(1)

    # Traite le premier argument
    for token in split_path(argv[0]):
        print(token)

if __name__ == "__main__":
    main()

