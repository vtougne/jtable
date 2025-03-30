#!/usr/bin/env python3

import re

def parse_line(line):
    # Supprimer les crochets extérieurs
    line = line.strip()[1:-1]

    # Utiliser une expression régulière pour trouver les éléments entre guillemets
    pattern = re.compile(r'"(?:[^"\\]|\\.)*"')
    # pattern = re.compile(r'"(?:[^"\\])*"')
    matches = pattern.findall(line)

    # Supprimer les guillemets extérieurs et remplacer les séquences d'échappement
    # parsed_list = [match[1:-1].replace('\\"', '"') for match in matches]

    return matches

# Exemple d'utilisation
line = '["identifiant de l\'utilisateur"]["prenom"]'
line = '["identifiant de l\'utilisateur"]prenom'
result_list = parse_line(line)

i = 0
for res in result_list:
    print(f"{i}: {res}")
    i = i + 1