#!/usr/bin/env python3


from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager


loader = DataLoader()
inventory = InventoryManager(loader=loader, sources='./dev/pay/hosts_dc_1.ini')
variable_manager = VariableManager(loader=loader, inventory=inventory)

print(dir(inventory))
print(inventory.groups)
print(inventory.hosts.values().get_vars)

print(inventory.groups['rmp'].get_vars())
