#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys

# --------------------------------------------
# 1. Récupération de la chaîne d’entrée
# --------------------------------------------
user_input = sys.argv[1] if len(sys.argv) > 1 else r"[vince][dupont][status: \[not contacted\]]"

# --------------------------------------------
# 2. Détection des blocs [ … ] ou { … } (échappés)
# --------------------------------------------
block_pattern = r'\[(?:\\.|[^\]])*\]|\{(?:\\.|[^\}])*\}'
blocks_raw = re.findall(block_pattern, user_input)

# print('\n'.join(blocks_raw))

# --------------------------------------------
# 3. Nettoyage : retirer les délimiteurs externes
#     et dé‑échappement des séquences \[ \] \{ \}
# --------------------------------------------
cleaned_blocks = []
for b in blocks_raw:
    # inner = b[1:-1]  # enlève le délimiteur extérieur
    # dé‑échappement (récupère \[ → [, \] → ], \{ → {, \} → })
    inner_unescaped = re.sub(r'\\([\\\[\]\{\}])', r'\1', b)
    cleaned_blocks.append(inner_unescaped)

# --------------------------------------------
# 4. Affichage
# --------------------------------------------
print('\n'.join(cleaned_blocks))
