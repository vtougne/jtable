#!/usr/bin/env python3
from jinja2 import Environment, StrictUndefined

# Configuration de l'environnement avec StrictUndefined
env = Environment(undefined=StrictUndefined)

# Exemple de template Jinja
template_string = '{{ {"name": "vince"}.names }}'

# Crée le template avec le contexte statique si nécessaire
template = env.from_string(template_string)

try:
    # Rend le template (cela lèvera une erreur si l'attribut est manquant)
    output = template.render()
    print(output)
except Exception as e:
    print(f"Erreur : {e}")
