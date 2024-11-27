#!/usr/bin/env python3
import pickle

# Un exemple d'objet Python à sérialiser
data = {
    "name": "Alice",
    "age": 30,
    "is_admin": True,
    "favorites": ["chocolat", "café", "lecture"]
}

# Sérialiser (sauvegarder) les données dans un fichier
with open("data.pkl", "wb") as file:
    pickle.dump(data, file)
print("Données sauvegardées dans data.pkl")

# Désérialiser (charger) les données depuis le fichier
with open("data.pkl", "rb") as file:
    loaded_data = pickle.load(file)
print("Données chargées :", loaded_data)
