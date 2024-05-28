#!/usr/bin/env python3
"""
A simple example of a few buttons and click handlers.
"""

from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.widgets import Frame, TextArea
from prompt_toolkit.shortcuts import message_dialog

import os
from data_cls import data_cls
from tabulate import tabulate
from prompt_toolkit.completion import Completer, Completion




data = data_cls()
raw_data = data.load_data()
data.to_table(raw_data)

f=open("/dev/tty")
os.dup2(f.fileno(), 0)

# select_area = TextArea(focusable=True,text="coucou")
# path_explorer_arera = TextArea(focusable=True,text="coucou",read_only=True)

path_buffer = Buffer()
path_explorer_buffer = Buffer()
path_area = Window(BufferControl(buffer=path_buffer))
path_explorer_arera = Window(BufferControl(buffer=path_explorer_buffer))
path_explorer_buffer.text = '\n'.join(str(paths) for paths in data.paths)



select_buffer = Buffer()
select_area = TextArea(text=data.select_view(), read_only=True)

table_area = TextArea(text=tabulate(data.rows), read_only=True)
select_area.text = data.select_view()


select_kb = KeyBindings()
select_kb.add("z")(focus_next)

def refresh(_):
    data.to_table(raw_data,path=path_buffer.text)
    table_area.text = tabulate(data.rows)
    select_area.text = data.select_view()

path_kb = KeyBindings()
path_kb.add("c-m")(refresh)


root_container = HSplit([
    Frame(table_area, title="table_area"),
    VSplit([
        Frame(path_explorer_arera, title="Path"),
        Frame(select_area, title="Select",key_bindings=select_kb)
        ]),
    Frame(path_area,key_bindings=path_kb,height=3)
    ]
)



kb = KeyBindings()
kb.add("tab")(focus_next)
kb.add("s-tab")(focus_previous)

@kb.add("c-c", eager=True)
def _(event):
    event.app.exit()

layout = Layout(container=root_container, focused_element=select_area)
application = Application(layout=layout, key_bindings=kb, full_screen=True)

path_buffer.text = "{}"

next_item = ['host','cloud']

def change_path(_):
    for item in next_item:
        if item.startswith(path_buffer.text):
            path_buffer._set_cursor_position(len(item))
            select_area.text = str(path_buffer.cursor_position)
            path_buffer.text = item
            

    
path_buffer.on_cursor_position_changed  += change_path


application.run()


