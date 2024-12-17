#!/usr/bin/env python3
import shutil
import functions


class Context:
    def __init__(self):
        self._terminal = functions.shell_context()

    @property
    def terminal(self):
        return self._terminal
    
    @property
    def all(self):
        return {
            key: getattr(self, key)
            for key in dir(self)
            if key != "all" and isinstance(getattr(type(self), key, None), property)
        }

if __name__ == "__main__":
    context = Context()
    print(context.all)
