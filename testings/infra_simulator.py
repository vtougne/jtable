#!/usr/bin/env python3

import random
import string
import json
import sys

def generate_random_hostname():
    """Génère un hostname aléatoire."""
    prefix = ''.join(random.choices(string.ascii_lowercase, k=3))
    suffix = ''.join(random.choices(string.digits, k=3))
    return f"host-{prefix}{suffix}"

def generate_ip_address():
    """Génère une adresse IP aléatoire."""
    return '.'.join(str(random.randint(0, 255)) for _ in range(4))

def generate_hosts(scope):
    """
    Génère un dictionnaire de hosts en fonction de l'entrée scope.

    :param scope: Un dictionnaire indiquant les environnements et leur nombre maximum de hosts.
    :return: Un dictionnaire JSON contenant les hosts générés.
    """
    states = ["alive","alive","alive","alive","alive","alive", "unreachable", ""]
    os_types = ["Linux","Linux","Linux","Linux", "Windows"]
    ap_codes =  ['AP' + ''.join(random.choices(string.digits, k=3)) for i in range(4)]


    hosts = {}

    for env, max_hosts in scope.items():
        # for _ in range(random.randint(0, max_hosts)):
        for _ in range(max_hosts):
            hostname = generate_random_hostname()
            hosts[hostname] = {
                "environment": env,
                "dc_name": f"dc-{random.randint(1, 10)}",
                "ip_address": generate_ip_address(),
                "state": random.choice(states),
                "os": random.choice(os_types),
                "os_level": f"{random.randint(1, 10)}.{random.randint(0, 9)}",
                "uptime": f"{random.randint(1, 90) * 24 * 60 * 60}",
                "ap_code": random.choice(ap_codes)
            }

    return hosts

# Exemple d'entrée
# scope = {'dev': 500, 'qua': 500, 'prod': 1000}
# scope = {'dev': 1000, 'qua': 1000, 'prod': 2000}
# scope = {'dev': 2000, 'qua': 2000, 'prod': 4000}
# scope = {'dev': 4000, 'qua': 4000, 'prod': 8000}
scope = {'dev': 10, 'qua': 15, 'prod': 20}

# Génération des hosts
hosts_dict = generate_hosts(scope)

# Sortie JSON
print(json.dumps(hosts_dict, indent=4))

# print('debug something in stderr',file=sys.stderr)