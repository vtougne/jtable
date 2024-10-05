#!/usr/bin/env python3
import re

def escape_custom(texte):
    return re.sub(r"(['\[\]])", r'\\\1', texte)


texte = "Ceci est un exemple avec une guillemet simple ' à protéger."
texte_escaped = escape_custom(texte)


print(texte_escaped)


bob = texte_escaped
print(bob)