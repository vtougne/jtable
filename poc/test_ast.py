#!/usr/bin/env python3
import ast

expression = "['planet'].regions[0].hosts"
parsed_expression = ast.parse(expression, mode='eval')

# Vous pouvez parcourir l'arbre syntaxique ici pour analyser les différentes parties de l'expression
print(parsed_expression.value)


print(dir(parsed_expression))