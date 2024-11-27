import logging,inspect

class MyLogFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        return logging.Formatter.formatTime(self, record, '%H:%M:%S') + f'.{record.msecs:03.0f}'

    def format(self, record):
        location = '%s.%s:%s' % (record.name, record.funcName, record.lineno)
        msg = '%s %-30s %-8s %s' % (self.formatTime(record), location, record.levelname, record.getMessage())
        return msg


def with_logger(cls):
    class WrappedClass(cls):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.logger = logging.getLogger(cls.__name__)
            self.logger.setLevel(logging.DEBUG)
            self.logger.propagate = False
            if not self.logger.handlers:
                handler = logging.StreamHandler()
                formatter = MyLogFormatter('%(asctime)s.%(msecs)03d', '%H:%M:%S')
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)

    WrappedClass.__name__ = cls.__name__
    WrappedClass.__qualname__ = cls.__qualname__
    return WrappedClass


class LoggingCls:
    def __init__(self):
        # self.logger = logging.getLogger("custom_logger")
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            handler = logging.StreamHandler()

            formatter = MyLogFormatter('%(asctime)s.%(msecs)03d', '%H:%M:%S')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    @property
    def logging(self):
        return self.logger

def setup_logger_alias():
    frame = inspect.currentframe()
    try:
        while frame:
            local_vars = frame.f_locals
            if "self" in local_vars:
                instance = local_vars["self"]
                if hasattr(instance, "logger"):
                    return instance.logger
            frame = frame.f_back
    finally:
        del frame  # Nettoyage explicite pour éviter des cycles de référence
    raise RuntimeError("Impossible de trouver `self.logger` dans la pile.")



logger = LoggingCls().logging
