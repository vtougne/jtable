#!/usr/bin/env python3


# Séquences d'échappement ANSI pour la couleur
GREEN = "\033[1;32m"
RESET = "\033[0m"

# Votre tableau de données
data = [
    {"hostname": "host_1", "os": "linux", "cost": 5000, "state": "alive"},
    {"hostname": "host_2", "os": "windows", "cost": 200, "state": "alive"},
    {"hostname": "host_3", "os": "linux", "cost": 200, "state": "unreachable"},
    {"hostname": "host_4", "os": "linux", "cost": 200, "state": "alive"},
    {"hostname": "host_5", "os": "linux", "cost": 200, "state": "unreachable"},
]

# Affichage du tableau avec la coloration
print(f"{'hostname':<10} {'os':<10} {'cost':<6} {'state':<15}")
print('-' * 40)
for entry in data:
    state = entry["state"]
    if state == "alive":
        state_colored = f"{GREEN}{state}{RESET}"
    else:
        state_colored = state
    print(f"{entry['hostname']:<10} {entry['os']:<10} {entry['cost']:<6} {state_colored:<15}")
