#! /usr/bin/env python3

import logging
import logging.config
import sys
import inspect

# Créer un formatter personnalisé
class CustomFormatter(logging.Formatter):
    def format(self, record):
        # Obtenir la pile d'exécution
        frame = inspect.currentframe()
        
        # Obtenir la fonction parente (deuxième élément dans la pile)
        parent_function = inspect.getouterframes(frame)[9].function
        class_name = inspect.currentframe().f_back.f_back.f_back.f_back.f_back.f_back.f_back.f_back.f_back.f_locals["self"].__class__.__name__
        # print(f"class_name: {class_name}")
        
        # Ajouter la fonction parente au record de log
        record.parent_function = parent_function
        record.class_name = class_name
        # Ajouter le nom de la classe au record s'il existe
        if not hasattr(record, 'class_name'):
            record.class_name = None
        
        # Utiliser le formatter de base
        return super().format(record)

# Classe pour exclure les erreurs
class _ExcludeErrorsFilter(logging.Filter):
    def filter(self, record):
        """Ne laisse passer que les messages de log en dessous de ERROR."""
        return record.levelno < logging.ERROR

# Configuration du logging
logging_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'exclude_errors': {
            '()': _ExcludeErrorsFilter
        }
    },
    'formatters': {
        'my_formatter': {
            '()': CustomFormatter,  # Utilisation du CustomFormatter
            'format': '%(asctime)s (line %(lineno)s) | %(levelname)s %(class_name)s %(parent_function)s %(message)s',
            'datefmt': '%H:%M:%S'
        }
    },
    'handlers': {
        'console_stderr': {
            'class': 'logging.StreamHandler',
            'level': 'ERROR',
            'formatter': 'my_formatter',
            'stream': sys.stderr
        },
        'console_stdout': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'my_formatter',
            'filters': ['exclude_errors'],
            'stream': sys.stdout
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console_stdout', 'console_stderr']
    },
}

# Appliquer la configuration
logging.config.dictConfig(logging_config)


# Exemple de classe qui utilise le logger
class MaClasse:


    def ma_methode_1(self):
        logging.debug("Message de log")

    def ma_methode_2(self):
        logging.info(f"Un autre message")

# Appeler les méthodes de classe
obj = MaClasse()
obj.ma_methode_1()
obj.ma_methode_2()
