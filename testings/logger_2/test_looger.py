#!/usr/bin/env python3
from logging_cls import LoggingCls

# Création d'une instance de LoggingCls
logger = LoggingCls()

# Utilisation du logger avec l'alias "logging"
logger.logging.info("Ceci est un message de log avec le format personnalisé.")
logger.logging.error("Ceci est un message d'erreur.")


# @LoggingCls
# class MyClass:
#     def do_something(self):
#         # logger = setup_logger_alias()
#         self.logger.info("Ceci est un message loggué avec un alias automatique.")