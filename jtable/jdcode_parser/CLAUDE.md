
# Contexte

Je suis en train de revoir ma solution jtable https://github.com/vtougne/jtable, developpement python de représentation sous forme de tables des entrées type de json, yaml, xml exploitant le jinja.

Voici le nouveau prototype, dont le cli permet d'invoquer des filtres jinja, dont to_table le filtre principal de jtable.
Les filtres et méthodes sont fictives

# les fichiers
Apps                    # Objet de type filtre jinja ou méthode (décrit plus bas)
jdcode_parser.py        # Le Cli charge les Apps, et parse la ligne de commande pour la transormer en expression jinja
                        # il permet de proposer la iste des filtres et options au moyen de la completion
jdcode-completion.bash  # la partie completion naive qui demande à jdcode_parser de fournir la completion

# Les syntaxes possibles

## exemple utilisation méthode puis filtre
```bash
jdcode_parser load_json the_file.json, to_yaml  
# load_json est un méthode (c'est en fait un namespace jinja)
# la virgule est l'équivalent du pipe en jinja  
# to_yaml est un filtre jinja

# génère l'expression jinja suivante:
# load_json("the_file") | to_yaml
```

## exemple utilisation filtre uniquement avec des entrée en stdin
```bash
cat the_json.json  | jdcode_parser from_json , to_yaml
# le texte en stdin sera stocké dans ne variable "stdin"
# from_json est un filtre
# to_yaml est un filtre

# génère l'expression jinja suivante:
# stdin | from_json | to_yaml
```



# les composants

## App
> une app est une fonction qui prend en option:
- soit aucune               # exemple to_yaml
- soit un argument          # exemple load_json ./the_json.json
- soit des arguments nommés # exemple to_table --format html

## filter
> est une application de type filter
il sera invoqué après un pipe en jinja, le contenu du pipe sera le premier argument passé à l'appplication  
tel qu c'est fait en jinja

## méthode
> est une application de type method
fonction qui seront injectés en tant qu'objets dans le namespace jinja