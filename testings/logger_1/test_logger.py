#!/usr/bin/env python3
from logging_cls import with_logger
from logging_cls import logger
from logging_cls import setup_logger_alias


logger.info("C'est parti")

@with_logger
class MyClass:
    def do_something(self):
        logger = setup_logger_alias()
        self.logger.info("Ceci est un message loggué avec un alias automatique.")
        logger.info("C'est parti depuis MyClass")
        
@with_logger
class MyClass2:
    def do_something(self):
        self.logger.info("Ceci est un message loggué avec un alias automatique.")
        # logger.info("Et un autre.")
        # print(my_logger(self))
        

from sub_cls import SubCls
my_sub_cls =  with_logger(SubCls)()
my_sub_cls.coucou()



# Exemple
cls_1 = MyClass()
cls_2 = MyClass2()

cls_2.do_something()
cls_1.do_something()


# Création d'une instance de LoggingCls

# Utilisation du logger avec l'alias "logging"
# logger.info("Ceci est un message de log avec le format personnalisé.")