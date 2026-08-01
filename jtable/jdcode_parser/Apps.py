#!/usr/bin/env python3
"""
App registry for jdcode.

An "app" is a function exposed to the jdcode CLI, of one of two types:
  - filter : a jinja filter, invoked after a pipe; the piped content is
             its first argument (e.g. `stdin | from_json | to_yaml`)
  - method : an object injected into the jinja namespace and called
             directly (e.g. `load_json("the_file.json")`)

An app takes either no argument, one positional argument, or named
options (e.g. `to_table --format html`).

Apps are declared with the @filter_app / @method_app decorators and
collected in the module-level `registry`. The implementations below are
fictive placeholders while the parser is being prototyped.
"""

from dataclasses import dataclass, field

FILTER = "filter"
METHOD = "method"

jinja_builtins = [
    'abs', 'attr', 'batch', 'capitalize', 'center', 'default',
    'dictsort', 'escape', 'filesizeformat', 'first', 'float',
    'forceescape', 'format', 'groupby', 'indent', 'int', 'join',
    'last', 'length', 'list', 'lower', 'map', 'max', 'min',
    'pprint', 'random', 'reject', 'rejectattr', 'replace',
    'reverse', 'round', 'safe', 'select', 'selectattr', 'slice',
    'sort', 'string', 'striptags', 'sum', 'title', 'trim',
    'truncate', 'unique', 'upper', 'urlencode', 'urlize',
    'wordcount', 'wordwrap', 'xmlattr', 'items', 'keys',
    'values'
]


@dataclass
class App:
    """Declaration of a CLI-exposed app."""
    name: str
    func: callable
    type: str                       # FILTER or METHOD
    args: list = field(default_factory=list)    # positional arg names (excluding piped value for filters)
    options: dict = field(default_factory=dict) # '--format' -> {'default': ..., 'choices': [...], 'help': ...}
    doc: str = ""

    @property
    def is_filter(self):
        return self.type == FILTER

    @property
    def is_method(self):
        return self.type == METHOD


class Registry:
    def __init__(self):
        self._apps = {}

    def register(self, app: App):
        self._apps[app.name] = app
        return app

    def get(self, name):
        return self._apps.get(name)

    def apps(self):
        return dict(self._apps)

    def list_apps(self):
        return list(self._apps.keys())

    def list_filters(self):
        return [name for name, app in self._apps.items() if app.is_filter]

    def list_methods(self):
        return [name for name, app in self._apps.items() if app.is_method]

    def list_builtins(self):
        return list(jinja_builtins)

    def list_all(self):
        return sorted(set(jinja_builtins + self.list_apps()))

    def is_known_filter(self, name):
        """A name usable after a pipe: a declared filter or a jinja builtin."""
        app = self.get(name)
        if app is not None:
            return app.is_filter
        return name in jinja_builtins


registry = Registry()


def _make_decorator(app_type):
    def decorator(func=None, *, name=None, args=None, options=None):
        def wrap(f):
            registry.register(App(
                name=name or f.__name__,
                func=f,
                type=app_type,
                args=list(args or []),
                options=dict(options or {}),
                doc=(f.__doc__ or "").strip(),
            ))
            return f
        if func is not None:            # used as @filter_app without parentheses
            return wrap(func)
        return wrap                     # used as @filter_app(options=...)
    return decorator


filter_app = _make_decorator(FILTER)
method_app = _make_decorator(METHOD)


# ---------------------------------------------------------------------------
# Fictive apps (placeholders for the real jtable filters/methods)
# ---------------------------------------------------------------------------

@filter_app
def to_yaml(value):
    """Render the value as YAML."""
    pass


@filter_app
def from_json(value):
    """Parse a JSON string into a dataset."""
    pass


@filter_app(options={
    "--format": {"default": "simple",
                 "choices": ["simple", "html", "github", "json", "th", "td", "latex"],
                 "help": "output table format"},
    "--select": {"help": "columns to display"},
    "--when":   {"help": "row filter condition"},
})
def to_table(value, format="simple", select=None, when=None):
    """Render the value as a table."""
    pass


@method_app(args=["path"])
def load_json(path):
    """Load a JSON file."""
    pass


@method_app(args=["path"])
def load_yaml(path):
    """Load a YAML file."""
    pass


# ---------------------------------------------------------------------------
# Backwards-compatible facade (used by jdcode_parser.py and the bash completion)
# ---------------------------------------------------------------------------

class AppsModule:
    """Kept for compatibility with existing callers; delegates to `registry`."""

    def apps(self):
        # legacy shape: {'name': {'app': func, 'types': [...]}}
        return {
            name: {"app": app.func, "types": [app.type],
                   "args": app.args, "options": app.options}
            for name, app in registry.apps().items()
        }

    def list_apps(self):
        return registry.list_apps()

    def list_builtins(self):
        return registry.list_builtins()

    def list_all(self):
        return registry.list_all()

    def list_filters(self):
        return registry.list_filters() + jinja_builtins

    def list_methods(self):
        return registry.list_methods()


if __name__ == "__main__":
    for name, app in registry.apps().items():
        opts = " ".join(app.options.keys())
        args = " ".join(f"<{a}>" for a in app.args)
        print(f"{app.type:<8} {name:<12} {args} {opts}  # {app.doc}")
