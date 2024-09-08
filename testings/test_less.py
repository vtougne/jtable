#!/usr/bin/env python3

import os
import shutil

def paginate_text(text):
    # Obtenir la taille du terminal (nombre de lignes visibles)
    terminal_size = shutil.get_terminal_size((80, 20))  # Largeur par défaut 80, hauteur 20
    lines_per_page = terminal_size.lines - 1  # Moins une ligne pour la lisibilité

    # Découper le texte en lignes
    lines = text.splitlines()

    # Afficher le texte page par page
    for i in range(0, len(lines), lines_per_page):
        # Afficher une "page" de texte
        print("\n".join(lines[i:i + lines_per_page]))

        # Si on n'est pas à la fin du texte, demander à l'utilisateur d'appuyer sur une touche
        if i + lines_per_page < len(lines):
            input("Appuyez sur 'Entrée' pour continuer, ou 'q' pour quitter... ")
            # Permet à l'utilisateur de quitter avec 'q'
            if input().lower() == 'q':
                break

# Exemple d'utilisation
long_text = """Voici un texte très long que nous allons paginer. Il peut s'agir de n'importe quel texte.
...
Ajoute des lignes ici pour qu'il soit assez long et puisse remplir plusieurs pages de terminal.
Chaque page affichera un nombre limité de lignes. L'utilisateur devra appuyer sur 'Entrée' ou 'Espace' pour
passer à la page suivante. 
Ajoute des lignes ici pour qu'il soit assez long et puisse remplir plusieurs pages de terminal.
Chaque page affichera un nombre limité de lignes. L'utilisateur devra appuyer sur 'Entrée' ou 'Espace' pour
passer à la page suivante. 
Ajoute des lignes ici pour qu'il soit assez long et puisse remplir plusieurs pages de terminal.
Chaque page affichera un nombre limité de lignes. L'utilisateur devra appuyer sur 'Entrée' ou 'Espace' pour
passer à la page suivante. 
Ajoute des lignes ici pour qu'il soit assez long et puisse remplir plusieurs pages de terminal.
Chaque page affichera un nombre limité de lignes. L'utilisateur devra appuyer sur 'Entrée' ou 'Espace' pour
passer à la page suivante. 
Ajoute des lignes ici pour qu'il soit assez long et puisse remplir plusieurs pages de terminal.
Chaque page affichera un nombre limité de lignes. L'utilisateur devra appuyer sur 'Entrée' ou 'Espace' pour
passer à la page suivante. 
Ajoute des lignes ici pour qu'il soit assez long et puisse remplir plusieurs pages de terminal.
Chaque page affichera un nombre limité de lignes. L'utilisateur devra appuyer sur 'Entrée' ou 'Espace' pour
passer à la page suivante. 
Ajoute des lignes ici pour qu'il soit assez long et puisse remplir plusieurs pages de terminal.
Chaque page affichera un nombre limité de lignes. L'utilisateur devra appuyer sur 'Entrée' ou 'Espace' pour
passer à la page suivante. 
Ajoute des lignes ici pour qu'il soit assez long et puisse remplir plusieurs pages de terminal.
Chaque page affichera un nombre limité de lignes. L'utilisateur devra appuyer sur 'Entrée' ou 'Espace' pour
passer à la page suivante. 
Ajoute des lignes ici pour qu'il soit assez long et puisse remplir plusieurs pages de terminal.
Chaque page affichera un nombre limité de lignes. L'utilisateur devra appuyer sur 'Entrée' ou 'Espace' pour
passer à la page suivante. 
Ajoute des lignes ici pour qu'il soit assez long et puisse remplir plusieurs pages de terminal.
Chaque page affichera un nombre limité de lignes. L'utilisateur devra appuyer sur 'Entrée' ou 'Espace' pour
passer à la page suivante. 
Ajoute des lignes ici pour qu'il soit assez long et puisse remplir plusieurs pages de terminal.
Chaque page affichera un nombre limité de lignes. L'utilisateur devra appuyer sur 'Entrée' ou 'Espace' pour
passer à la page suivante. 
Ajoute des lignes ici pour qu'il soit assez long et puisse remplir plusieurs pages de terminal.
Chaque page affichera un nombre limité de lignes. L'utilisateur devra appuyer sur 'Entrée' ou 'Espace' pour
passer à la page suivante. 

Ajoute des lignes ici pour qu'il soit assez long et puisse remplir plusieurs pages de terminal.
Chaque page affichera un nombre limité de lignes. L'utilisateur devra appuyer sur 'Entrée' ou 'Espace' pour
passer à la page suivante. 
...
Continuez à ajouter du texte pour simuler le comportement.
"""
paginate_text(long_text)
