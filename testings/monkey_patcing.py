#!/usr/bin/env python3
# base.py
class BaseClass:
    def greet(self):
        print("Hello from BaseClass")
    
    def existing_method(self):
        print("This method exists in BaseClass")


# main.py
import importlib

# from base import BaseClass

def apply_user_methods(base_class, user_module_name):
    # Charger dynamiquement le module utilisateur
    user_module = importlib.import_module(user_module_name)
    
    # Vérifier que le module a bien la classe UserClass
    if hasattr(user_module, 'UserClass'):
        user_class = user_module.UserClass()
        
        # Parcourir les méthodes et attributs de la classe utilisateur
        for attr_name in dir(user_class):
            # Ignorer les attributs spéciaux (méthodes dunder)
            if not attr_name.startswith("__"):
                # Récupérer l'attribut/méthode de la classe utilisateur
                attr = getattr(user_class, attr_name)
                # Remplacer ou ajouter dans la classe de base
                setattr(base_class, attr_name, attr)

# Appliquer les méthodes de UserClass à BaseClass
apply_user_methods(BaseClass, 'user_cls')

# Tester les modifications
obj = BaseClass()
obj.greet()          # Affiche: Hello from UserClass - overridden
obj.existing_method()  # Affiche: This method exists in BaseClass
obj.new_method()     # Affiche: This is a new method added by UserClass
