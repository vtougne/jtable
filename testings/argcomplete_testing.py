#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
import argcomplete, argparse

def main():
    parser = argparse.ArgumentParser(description="Exemple avec argcomplete")
    
    # Ajout des arguments
    parser.add_argument("--action", choices=["start", "stop", "restart"], help="Action à effectuer")
    parser.add_argument("--name", help="Nom de l'objet")
    
    # Activation de l'autocomplétion
    argcomplete.autocomplete(parser)
    
    # Analyse des arguments
    args = parser.parse_args()
    print(f"Action : {args.action}")
    print(f"Nom : {args.name}")

if __name__ == "__main__":
    main()
