#!/usr/bin/env python3
import logging
import inspect


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

def with_logger(cls):
    """
    Décorateur pour ajouter un logger à une classe tout en conservant le nom d'origine.
    """
    class WrappedClass(cls):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.logger = logging.getLogger(cls.__name__)
            self.logger.setLevel(logging.DEBUG)

            if not self.logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter(
                    '%(asctime)s.%(msecs)03d  - %(name)-20s - %(levelname)s - %(message)s',
                    '%H:%M:%S'
                )

                handler.setFormatter(formatter)
                self.logger.addHandler(handler)


    WrappedClass.__name__ = cls.__name__
    WrappedClass.__qualname__ = cls.__qualname__
    return WrappedClass
