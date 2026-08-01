#!/usr/bin/env python3
"""
jdcode CLI parser.

Loads the apps declared in Apps.py, parses the command line and turns it
into a jinja expression. The comma is the CLI equivalent of the jinja pipe:

  jdcode_parser load_json the_file.json, to_yaml
    -> load_json("the_file.json") | to_yaml

  cat the_json.json | jdcode_parser from_json , to_yaml
    -> stdin | from_json | to_yaml     (stdin holds the piped text)

Also provides the app list used by jdcode-completion.bash.
"""

import argparse
import sys

from Apps import registry, AppsModule


def tokenize(words):
    """Split argv words on commas, keeping ',' as a standalone token."""
    tokens = []
    for word in words:
        parts = word.split(',')
        for i, part in enumerate(parts):
            if part:
                tokens.append(part)
            if i < len(parts) - 1:
                tokens.append(',')
    return tokens


def split_segments(tokens):
    """Split the token stream into pipe segments: [app_name, arg, ...]."""
    segments, current = [], []
    for token in tokens:
        if token == ',':
            if current:
                segments.append(current)
            current = []
        else:
            current.append(token)
    if current:
        segments.append(current)
    return segments


def render_value(value):
    """Render a CLI argument as a jinja literal (numbers kept bare)."""
    try:
        float(value)
        return value
    except ValueError:
        pass
    if value in ("true", "false", "none", "True", "False", "None"):
        return value
    return '"{}"'.format(value.replace('"', '\\"'))


def parse_segment(segment):
    """Parse one segment into (app_name, positional_args, named_options)."""
    name, rest = segment[0], segment[1:]
    app = registry.get(name)
    positional, options = [], {}
    i = 0
    while i < len(rest):
        token = rest[i]
        if token.startswith('--'):
            if app is not None and app.options and token not in app.options:
                raise ValueError(
                    f"'{name}' has no option '{token}' "
                    f"(available: {', '.join(app.options)})")
            if i + 1 >= len(rest):
                raise ValueError(f"option '{token}' of '{name}' expects a value")
            options[token.lstrip('-')] = rest[i + 1]
            i += 2
        else:
            positional.append(token)
            i += 1
    return name, positional, options


def render_call(name, positional, options, piped=False):
    """Render an app invocation as jinja code.

    piped=True renders a filter usage (no parentheses when no argument).
    """
    rendered = [render_value(v) for v in positional]
    rendered += [f'{key}={render_value(value)}' for key, value in options.items()]
    if piped and not rendered:
        return name
    return f'{name}({", ".join(rendered)})'


def build_expression(segments):
    """Turn pipe segments into a jinja expression."""
    parts = []
    for index, segment in enumerate(segments):
        name, positional, options = parse_segment(segment)
        app = registry.get(name)

        if index == 0:
            if app is not None and app.is_method:
                parts.append(render_call(name, positional, options))
                continue
            if not registry.is_known_filter(name):
                raise ValueError(f"'{name}' is not a valid app or filter")
            # a filter in first position applies to stdin
            parts.append('stdin')
            parts.append(render_call(name, positional, options, piped=True))
        else:
            if not registry.is_known_filter(name):
                raise ValueError(f"'{name}' cannot be used after a pipe: "
                                 "not a filter")
            parts.append(render_call(name, positional, options, piped=True))
    return ' | '.join(parts)


def create_parser():
    parser = argparse.ArgumentParser(
        description='jdcode - CLI tool turning a command line into a jinja expression',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'expression',
        nargs=argparse.REMAINDER,
        help='apps/filters separated by commas (pipe equivalent), '
             'use tab completion to see available options'
    )
    parser.add_argument(
        '--list_filters',
        action='store_true',
        help='List all available filters'
    )
    parser.add_argument(
        '--list_all',
        action='store_true',
        help='List all apps, filters and jinja builtins (used by completion)'
    )
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    if args.list_filters:
        print("\t".join(sorted(AppsModule().list_filters())))
        return 0

    if args.list_all:
        print("\t".join(registry.list_all()))
        return 0

    if not args.expression:
        parser.print_help()
        filters = AppsModule().list_filters()
        methods = AppsModule().list_methods()
        print(f"\nAvailable filters ({len(filters)}):")
        print(", ".join(filters))
        print(f"\nAvailable methods ({len(methods)}):")
        print(", ".join(methods))
        return 0

    segments = split_segments(tokenize(args.expression))
    try:
        expression = build_expression(segments)
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(expression)
    return 0


if __name__ == "__main__":
    sys.exit(main())
