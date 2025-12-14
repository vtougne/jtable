#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
paser.py

Ajout de la prise en charge des accolades en plus des crochets.

Usage :
    ./paser.py [chaine_a_parcourir]

Si aucun argument n’est fourni, la chaîne suivante est utilisée par défaut :

    [vince][dupont][status: \[not contacted\]]
"""

import re
import sys

# --------------------------------------------------------------------
# 1. Récupération de la chaîne fournie en argument (ou valeur par défaut)
# --------------------------------------------------------------------
if len(sys.argv) > 1:
    user_input = sys.argv[1]
else:
    user_input = r"[vince][dupont][status: \[not contacted\]]"

# --------------------------------------------------------------------
# 2. Détection de tous les blocs « [ … ] » ou « { … } » (avec échappements)
# --------------------------------------------------------------------
#   - r'\[(?:\\.|[^\]])*\]'   : bloc entre crochets (avec échappements)
#   - r'\{(?:\\.|[^\}])*\}'   : bloc entre accolades (avec échappements)
#   On les combine avec le « | » (ou) pour que l’expression capture les deux types.
block_pattern = r'\[(?:\\.|[^\]])*\]|\{(?:\\.|[^\}])*\}'

blocks_raw = re.findall(block_pattern, user_input)

# --------------------------------------------------------------------
# 3. Nettoyage des blocs
# --------------------------------------------------------------------
cleaned_blocks = []
for b in blocks_raw:
    # 3.1. Retirer le caractère d’ouverture et de fermeture
    inner = b[1:-1]

    # 3.2. Dé‑échappement : \[ → [, \] → ], \{ → {, \} → }
    # (et on conserve le caractère d’échappement de l’autre type, s’il existe)
    inner_unescaped = re.sub(r'\\([\\\[\]\{\}])', r'\1', inner)

    cleaned_blocks.append(inner_unescaped)

# --------------------------------------------------------------------
# 4. Affichage
# --------------------------------------------------------------------
print('\n'.join(cleaned_blocks))
