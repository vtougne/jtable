#!/usr/bin/python3
import yaml, sys, os, curses, time
from prettytable import PrettyTable

class data_cls:
    def __init__(self):
        self.paths = []
        self.fields = []
        self.rows = []
        self.raw_rows = []
        self.source_object_type = "list"

    def get_paths(self,dataset):
        self.cover_paths(dataset)
        return('\n'.join(self.paths))
    
    def cover_paths(self,dataset,path=[]):
        if type(dataset) is dict:
            for key,value in dataset.items():
                the_path = path + [ key ]
                self.cover_paths(value,the_path )
        elif type(dataset) is list:
            pass
            # index=0
            # for item in dataset:
            #     index += 1
            #     the_path = path + [ str(index) ]
            #     self.cover_paths(item,the_path)
        else:
            self.paths = self.paths + [ path + [dataset] ]
            if path[1:] not in self.fields:
                self.fields = self.fields + [path[1:]]

    def cover_data(self,dataset): 
        if type(dataset) is dict:
            the_list = []
            for key,value in dataset.items():
                the_list = the_list + [ {'key': key, 'value': value} ]
                self.source_object_type="dict"
            self.cover_data(the_list)
        elif type(dataset) is list:
            index=0
            for item in dataset:
                for key,value in item.items():
                    self.cover_paths(value,[str(index),key])
                    index+=1
                self.raw_rows = self.raw_rows + [ item ]

    def to_table(self,dataset):
      self.cover_data(dataset)
      for item in self.raw_rows:
          row=[]
          for field in self.fields:
            try:
                cell=eval('item[\'' + '\'][\''.join(field) + '\']')
            except:
                cell=""
            row = row + [ cell ]
        #   print(row)
          self.rows = self.rows + [ row ]





class PrettyTableCls:
    def __init__(self,dataset):
        self.pt = PrettyTable()
        self.dataset = dataset
        self.shift = 0
        self.load()
    def load(self,shift=0):
        console_width_exceed = False
        index=0
        last_field_displayed=""
        for field in my_data_cls.fields[shift:]:
            column=[]
            if self.dataset == "dict":
                print('debug field: ' + str(field))
                field_name = '.'.join(field[1:][-1:])
                print('debug field name: ' + field_name)
            else:
                field_name = '.'.join(field[-1:])

            for row in my_data_cls.rows:
                column = column + [str(row[index])]
            if len(self.pt.get_string().split('\n')[0]) < os.get_terminal_size().columns:
                self.pt.add_column(field_name,column)
                last_field_displayed = field_name
            else:
                console_width_exceed = True
                break
            index+=1

        if last_field_displayed is not None and console_width_exceed == True:
            self.pt.del_column(last_field_displayed)
    def scroll(self,way):
        if way == "right":
            self.shift = self.shift + 1
            self.pt.clear()
            self.load(self.shift)
        if way == "left":
            self.shift = self.shift - 1
            self.pt.clear()
            self.load(self.shift)





stdin=""
for line in sys.stdin:
    stdin = stdin + line

my_data_cls = data_cls()
input = yaml.safe_load(stdin)


my_data_cls.to_table(input)

pt = PrettyTableCls(my_data_cls)





def main(win):
    pt = PrettyTableCls(my_data_cls)
    win.nodelay(True)
    key=""
    win.clear()
    curses.curs_set(0)
    f=open("/dev/tty")
    os.dup2(f.fileno(), 0)
    try:
        win.addstr(str(pt.pt))
        win.addstr('\n' + 'Press Enter to quit')
    except:
        pass
    # win.addstr(the_text)
    # win.curs_set(0)
    while 1:
        try:
            os.dup2(f.fileno(), 0)
            key = win.getkey()
            if str(key)  == "KEY_RIGHT":
                pt.scroll("right")
            elif str(key)  == "KEY_LEFT":
                pt.scroll("left")
            elif key == os.linesep:
                curses.curs_set(2)
                break
            win.clear()
            win.addstr(str(pt.pt))
            win.addstr( "\n" + "Detected key: " + str(key) )

        except Exception as e:
            # No input
            pass
        time.sleep(0.1)
    # curses.curs_set(1)

curses.wrapper(main)
# curses.curs_set(0)