import sys
import os

# Ajoute le répertoire courant au début de `sys.path` pour privilégier les modules locaux
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    # Tente d'importer Jinja2 depuis le répertoire local
    from jinja2 import Environment, BaseLoader
    print("Using local Jinja2 module.")
except ImportError:
    # Si non disponible, utilise la version globale installée
    from jinja2 import Environment, BaseLoader
    print("Using globally installed Jinja2 module.")

# Exemple d'utilisation de Jinja2
env = Environment(loader=BaseLoader())
template = env.from_string("Hello, {{ name }}!")
print(template.render(name="World"))
