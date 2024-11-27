import logging

class MyLogFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        """
        Personnalisation du format de la date pour qu'il corresponde à "HH:mm:ss.sss".
        """
        # Utilisation de la méthode formatTime de la classe parente pour obtenir l'heure au format voulu
        return logging.Formatter.formatTime(self, record, '%H:%M:%S') + f'.{record.msecs:03.0f}'  # Ajout des millisecondes

    def format(self, record):
        # Création du format "Classe.Fonction:NuméroDeLigne"
        location = '%s.%s:%s' % (record.name, record.funcName, record.lineno)
        
        # Formatage du message complet avec date personnalisée
        msg = '%s %-60s %-8s %s' % (self.formatTime(record), location, record.levelname, record.getMessage())
        
        # Retourner le message formaté
        return msg


class LoggingCls:
    def __init__(self):
        # Initialisation du logger à l'échelle du module
        self.logger = logging.getLogger("custom_logger")
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            handler = logging.StreamHandler()

            # Application du format personnalisé
            formatter = MyLogFormatter('%(asctime)s.%(msecs)03d', '%H:%M:%S')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    # Exposer le logger avec un alias pour l'utilisation facile
    @property
    def logging(self):
        return self.logger

