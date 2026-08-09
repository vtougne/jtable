#!/usr/bin/env python3
import sys, json, re, os, ast, inspect, datetime, time, logging, logging.config, html, shutil, platform
from os import isatty
from sys import exit
from typing import Any, Dict, Optional

jtable_path = os.path.dirname(os.path.abspath(__file__))

if jtable_path not in sys.path:
    sys.path.insert(0, jtable_path)

parent_path = os.path.dirname(jtable_path)

if parent_path not in sys.path:
    sys.path.insert(0, parent_path)

from logger import CustomFormatter, CustomFilter, _ExcludeErrorsFilter, logging_config

import version
import tabulate
import yaml

import functions
Filters = functions
Plugin = functions.Plugin
# InspectDataset = functions.InspectDataset
running_context = functions.running_context()

# Import Templater from the new module
import templater
Templater = templater.Templater

# Import Styling from the new module
from Styling import Styling



def create_templater(*args, **kwargs):
    """Helper function to create Templater instances with to_table and to_table_x filters"""
    to_table_filter = ToTable().render_object
    to_table_x_filter = ToTable().render_object
    return Templater(*args, to_table_filter=to_table_filter, to_table_x_filter=to_table_x_filter, **kwargs)

class ToTable:
    def __init__(self, render="jinja_native"):
        logging.info(f"Initilizing render: {render}")
        self.td = []
        self.th = []
        # rows kept as [(label, value), ...] so tables rendered with different
        # field sets can be aligned on a common header at the end
        self.labeled_rows = []
        self.table_headers = []
        self.json = []
        self.render = render
        self.splitted_path = []
        self.when = []
        self.select = []
        self.unselect = []
        self.views = {}
        self.path = "{}"
        self.format = ""
        self.alias = []
        self.reverse = None

    def next_path_key(self, next_path):
        # returns the dict key consumed by the next path segment, if any
        if len(next_path) > 0:
            next_segment = str(next_path[0])
            if next_segment[0:2] == "['":
                return next_segment[2:-2]
            elif next_segment[0] == ".":
                return next_segment[1:]
        return None

    def strip_crossed_key(self, value, crossed_key):
        # keeps every key of the item but the one already crossed by the path
        if crossed_key is not None and type(value) is dict and crossed_key in value:
            return { k: v for k,v in value.items() if k != crossed_key }
        return value

    def cross_path(self, dataset, path, cross_path_context = {} ):
        level = len(path)
        if level > 1:
            # logging.info(f"path: {path}")
            next_path = path[1:]
            current_path = str(path[0])
            current_path_value = "unknown"
            if current_path[0:2] == "['":
                current_path_value = current_path[2:-2]
                if current_path_value in list(dataset):
                    self.cross_path(dataset[current_path_value], next_path, cross_path_context = cross_path_context)
                else:
                    logging.error('keys dataset were:')
                    logging.error(list(dataset))
                    logging.error(current_path + " was not found in dataset level: " + str(len(self.splitted_path) - level))
                    # exit(1)
            elif current_path[0] == ".":
                current_path_value = current_path[1:]
                if current_path_value in list(dataset):
                    self.cross_path(dataset[current_path_value],next_path, cross_path_context = cross_path_context)
                else:
                    logging.info(list(dataset))
                    logging.error(current_path + " was not found in dataset level: " + str(len(self.splitted_path) - level))
                    # exit(1)
                    
            elif current_path[0] == "[":
                current_path_value = current_path[1:-1]
                if int(current_path_value) <= len(dataset):
                    self.cross_path(dataset[int(current_path_value)],next_path, cross_path_context = cross_path_context)
                    
                else:
                    logging.error( current_path + " was not found in dataset level: " + str(len(self.splitted_path) - level))
                    exit(1)
            
            elif current_path[0] == "{":
                item_name = current_path[1:-1]
                if level > 0:
                    # the key crossed by the next path segment is already part of the
                    # path, it is removed from the value stored in the context
                    crossed_key = self.next_path_key(next_path)
                    if type(dataset) is dict:
                        for key,value in dataset.items():
                            next_path = path[1:]
                            item_value = self.strip_crossed_key(value, crossed_key)
                            # new_cross_path_context = {item_name: {"key": key, "value": value}}
                            cross_path_context = { **cross_path_context, **{item_name: {"key": key, "value": item_value}}}
                            self.cross_path(dataset[key],next_path,cross_path_context=cross_path_context)

                    elif type(dataset) is list:
                        index = 0
                        for item in dataset:
                            next_path = path[1:]
                            item_value = self.strip_crossed_key(item, crossed_key)
                            # new_cross_path_context = { item_name: item }
                            cross_path_context = { **cross_path_context, **{ item_name: item_value }}
                            self.cross_path(dataset[index],next_path,cross_path_context=cross_path_context)
                            index += 1
                else:
                    logging.info(f"item_name: {item_name}")
                    self.render_table(dataset=dataset,select=self.select, item_name = item_name, context = cross_path_context)
            else:
                logging.info("[ERROR] was looking for path...")
                exit(1)
        else:
            item_name = path[0][1:-1]
            # logging.info(f"item_name: {item_name}")
            self.render_table(dataset=dataset,select=self.select, item_name = item_name, context=cross_path_context)
    
    def render_object(self, dataset, path="{}", select=[], unselect=[], views={}, when=[], format="", context={}, queryset={}, reverse=""):
        # exit(0)
        for query_item,query_data in queryset.items():
            logging.info(f"query_item: {query_item}")
            # exit(0)
            if query_item == "select":
                self.select = query_data
            elif query_item == "unselect":
                self.unselect = query_data
            elif query_item == "path":
                # logging.info(f"self.path query_data: {query_data}")
                self.path = query_data
            elif query_item == "views":
                self.views = query_data
            elif query_item == "when":
                self.when = query_data
            elif query_item == "format":
                self.format = query_data
            elif query_item == "alias":
                self.alias = query_data
            elif query_item == "reverse":
                self.reverse = query_data
            else:
                raise Exception(f"the queryset argument contains a non accepted key: {query_item}")
            
        self.path = path if path != "{}" else self.path
        self.select = select if select != [] and select != "" else self.select
        self.unselect = unselect if unselect != [] and unselect != "" else self.unselect
        self.views = views if views != {} else self.views
        # self.when = when if when != [] else self.when
        self.when = when if when != [] and when != "" else self.when
        # logging.info(f"when: {self.when.__class__.__name__}")
        # if self.when.__class__.__name__ == "str":
        #     self.when = self.when.split(',')
            
        logging.info(f"when: {self.when}")
        # exit(0)
        self.format = format if format != "" else self.format
        self.reverse = reverse if reverse != "" else self.reverse
        self.context = context
        logging.info(f"unselect: {self.unselect}")

        self.dataset = dataset
        
        for k,v in self.views.items():
            self.views = {**self.views, **{ k: '{{' + str(v) + '}}' } }
        from .jinja_path_splitter import JinjaPathSplitter

        self.splitted_path = JinjaPathSplitter().split_path(self.path)
        
        logging.info(f"Crossing paths")
        self.cross_path(self.dataset, self.splitted_path )
        self.align_rows()
        self.reverse_table()

        if self.format == "json":
            return json.dumps(self.json)
        elif self.format == "th":
            return self.th
        elif self.format == "td":
            return self.td
        elif self.format == "github":
            return tabulate.tabulate(self.td,self.th,tablefmt="github")
        elif self.format == "gitlab_json_table":
            out_dataset = {
                "fields": [ { "key": key, "sortable": "true" } for key in self.th ],
                "items": self.json,
                "filter": True,
                "caption": ""
            }
            return f"```json:table\n{json.dumps(out_dataset,indent=2, separators=(',', ': '))}\n```"
        elif self.format == "html":
            return tabulate.tabulate(self.td,self.th,tablefmt="unsafehtml")
        else:
            return tabulate.tabulate(self.td,self.th,tablefmt=self.format)
        
        # return out_return[self.format]
    
    def align_rows(self):
        # each row is placed under the columns it was rendered with, missing
        # fields are left empty
        aligned_td = []
        for labeled_row in self.labeled_rows:
            available = list(labeled_row)
            row = []
            for field in self.th:
                value = ""
                for index,(label,label_value) in enumerate(available):
                    if label == field:
                        value = label_value
                        del available[index]
                        break
                row = row + [ value ]
            aligned_td = aligned_td + [ row ]
        self.td = aligned_td

    def reverse_table(self):
        # pivots the table: the given key column becomes the header row,
        # every other field becomes a row labeled with its own field name
        if not self.reverse or self.reverse not in self.th:
            return
        key_index = self.th.index(self.reverse)
        key_values = [row[key_index] for row in self.td]
        other_fields = [field for field in self.th if field != self.reverse]
        reversed_th = [self.reverse] + [str(value) for value in key_values]
        reversed_td = []
        for field in other_fields:
            field_index = self.th.index(field)
            reversed_td = reversed_td + [ [field] + [row[field_index] for row in self.td] ]
        self.th = reversed_th
        self.td = reversed_td

    def render_table(self, dataset, select=[], item_name='', context={}):
        stylings = []
        logging.info(f"unselect: {self.unselect}")
        def escape_field_name(field_name):
            """Escape single quotes in field names for safe Jinja templating"""
            return field_name.replace("'", "\\'")
            
        if len(select) > 0:
            logging.info(f"select: {select.__class__.__name__}")
            if select.__class__.__name__ == "str":
                fields_label = select.split(",")
                item_name = 'item' if item_name == '' else item_name
                # Transform field names into proper Jinja expressions that handle quotes safely
                # Special handling for context variables (e.g., file.path, region.key)
                def generate_expression(field):
                    if '.' in field:
                        # Check if this field references a context variable
                        field_prefix = field.split('.')[0]
                        # If the prefix is in the context, it's a context variable access
                        if field_prefix in context:
                            return field  # Direct context access (e.g., file.path, region.key)
                    # Otherwise it's an item field access
                    return item_name + '["' + escape_field_name(field) + '"]'
                expressions = list(map(generate_expression, fields_label))
            else:
                expressions = [expressions['expr'] for expressions in select]
                stylings = [(stylings['styling'] if 'styling' in stylings else []) for stylings in select]
                fields_label = [fields_label['as'] for fields_label in select]
        else:
            fields = path_auto_discover().discover_paths(dataset)
            fields_label = list(map(lambda item: '.'.join(item), fields))
            item_name = 'item' if item_name == '' else item_name
            # Use double quotes for dictionary access to handle single quotes in field names
            expressions = list(map(lambda item:  item_name + '["' + '"]["'.join([escape_field_name(part) for part in item]) + '"]' , fields))
            # Apply positional aliases when no select was specified
            for i, alias in enumerate(self.alias):
                if i < len(fields_label):
                    fields_label[i] = alias
        
        if self.unselect != [] and self.unselect != "":
            for field in self.unselect.split(','):
                if field in fields_label:
                    index = fields_label.index(field)
                    del expressions[index]
                    del fields_label[index]
                    if stylings != []:
                        del stylings[index]

        logging.info(f"expressions: {expressions}")
        logging.info(f"fields_label: {fields_label}")
        # exit()

        if type(dataset) is dict:
            dataset_to_cover = []
            for key,value in dataset.items():
                dataset_to_cover = dataset_to_cover + [ {'key': key, 'value': value} ]
        elif type(dataset) is list:
            dataset_to_cover = dataset
        else:
            raise Exception('[ERROR] dataset must be a dict or list, was: ' + str(type(dataset)))

        # static_context = {"dataset": dataset, **context}
        column_templates = []
        for expr in expressions:
            jinja_expr = '{{ ' + expr  + ' }}'
            column_templates = column_templates + [create_templater(template_string=jinja_expr, static_context={**context,**self.context},strict_undefined=False)]

        view_templates = []
        for var_name,var_data in self.views.items():
            view_templates = view_templates + [create_templater(template_string=str(var_data), static_context={**context,**self.context},strict_undefined=False)]

        when_templates = []
        for condition in self.when:
            when_templates = when_templates + [create_templater(template_string=condition, static_context={**context,**self.context},strict_undefined=False)]



        for item in dataset_to_cover:
            row = []
            json_dict = {}

            def when(when=[],when_context={}):
                condition_test_result = True
                for condition in when:
                    jinja_expr = '{{ ' + condition  + ' }}'
                    # logging.info(f"item_name: {item_name}")
                    logging.info(f"when: {when}")
                    # loop_condition_context = item
                    # loop_condition_context = { item_name: item } if item_name != '' else item
                    loop_condition_context = { item_name: item } if (item_name != '' and item_name != 'item' ) else item
                    logging.info(f"loop_condition_context: {loop_condition_context}")
                    logging.info(f"when_context: {when_context}")
                    # loop_condition_context = { item_name: item }
                    condition_template = create_templater(template_string=jinja_expr, static_context= {**when_context,**loop_condition_context},strict_undefined=False)
                    condition_test_result = condition_template.render({},eval_str=True)
                    logging.info(f"condition_test_result: {condition_test_result}, type: {type(condition_test_result)}")
                    
                    # Handle different result types
                    if isinstance(condition_test_result, list) and len(condition_test_result) > 0:
                        # If result is a list, check the first element
                        condition_test_result = condition_test_result[0]
                    
                    if condition_test_result == "False" or condition_test_result == False:
                        break
                return condition_test_result

            for expr in expressions:
                loop_context = { item_name: item } if item_name != '' else item
                view_context = {}
                view_index = 0
                for exp_key,exp_val in self.views.items():
                    try:
                        templated_var = view_templates[view_index].render({**loop_context,**view_context,**context},eval_str=True)
                    except Exception as error:
                        logging.error(f"Error while rendering var_name: {exp_key}, exp_val: {exp_val}, error was:\n{error}")
                        exit(1)
                    view_context.update({ exp_key: templated_var })
                    view_index += 1

            if self.when != []:
                condition_test_result = when(when = self.when, when_context = {**self.context,**context,**view_context})
                # logging.warning(f"condition_test_result: {condition_test_result}, type: {type(condition_test_result)}")
            else:
                condition_test_result = True
            
                
            if condition_test_result  == True or condition_test_result == "True":

                column_index = 0
                for expr in expressions:
                    loop_context = { item_name: item } if item_name != '' else item
                    try:
                        render_context = {**loop_context,**view_context,**context}
                        value_for_json = value = column_templates[column_index].render(render_context,eval_str=True)
                        # the table is rendered as text while the json output keeps
                        # the type of the source data (int, float, bool, ...)
                        native_value = column_templates[column_index].render_native(render_context)
                        if native_value is not None:
                            value_for_json = native_value
                        del render_context
                    except:
                        break
                    del loop_context
                    if self.format == "html":
                        value = html.escape(str(value))
                    key = fields_label[column_index]
                    if value_for_json != None:
                        json_value = { key: value_for_json }
                        json_dict = {**json_dict, **json_value }
                        del json_value
                        del value_for_json
                    if stylings != []:
                        styling = stylings[column_index]
                        condition_color = True
                        # if styling != []:
                        for styling_attributes in styling:
                            color_conditions = [color_conditions for color_conditions in  styling_attributes['when'] ]
                            # logging.info(color_conditions)
                            condition_color = when(when = color_conditions, when_context = {**context,**view_context})
                            logging.info(f"condition_color: {condition_color}")
                            if condition_color == True or condition_color == "True":
                                value = Styling().apply(value = value,format=self.format, styling_attributes = styling_attributes)
                                # logging.info(f"condition_color value: {value}")

                    row = row + [ value ]
                    del value
                    column_index += 1
                self.json = self.json + [ json_dict ]
                self.labeled_rows = self.labeled_rows + [ list(zip(fields_label, row)) ]
                self.td = self.td + [ row ]
        
        
        if fields_label is None:
            headers = list(map(lambda item: '.'.join(item), expressions))
            fields_label = headers
        
        # several tables can be rendered when the path crosses many items, the
        # header is the union of all fields, in order of first appearance
        for field in fields_label:
            if field not in self.th:
                self.th = self.th + [ field ]

        try:
            self.json_content = json.dumps(self.json)
        except Exception as error:

            logging.info(tabulate(self.td,self.th))
            logging.error(f"\nSomething wrong with json rendering, Errors was:\n  {error}")
            exit(2)

class path_auto_discover:
    def __init__(self):
        self.paths = []
        self.fields = []
        self.raw_rows = []
        
    def cover_paths(self,dataset,path=[]):
        if type(dataset) is dict:
            for key,value in dataset.items():
                the_path = path + [ key ]
                self.cover_paths(value,the_path )
        elif type(dataset) is list:
            if path[1:] not in self.fields:
                self.fields = self.fields + [path[1:]]
        else:
            self.paths = self.paths + [ path + [dataset] ]
            if path[1:] not in self.fields:
                self.fields = self.fields + [path[1:]]

    def discover_paths(self,dataset):
        
        # Check if dataset is None or empty
        if dataset is None:
            logging.error("Dataset is None. Please check your input data.")
            exit(1)
        
        # when input is dict transform as list like dict2items
        if type(dataset) is dict:
            dataset_as_list = []
            for key,value in dataset.items():
                dataset_as_list = dataset_as_list + [ {'key': key, 'value': value} ]
            dataset = dataset_as_list
        index=0

        try:
            for item in dataset:
                for key,value in item.items():
                    self.cover_paths(value,[str(index),key])
                    index+=1
                self.raw_rows = self.raw_rows + [ item ]
        except(Exception) as error:
            logging.error(f"Something wrong with your dataset, error was:")
            logging.error(f"    {error}")
            logging.error(f"Dataset type: {type(dataset)}")
            logging.error(f"Dataset content: {dataset}")
            exit(1)
        logging.info(f"fields: {self.fields}")
        return self.fields

if __name__ == "__main__":
    # Configure basic logging for testing
    logging.basicConfig(
        # level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )

    sample_dataset = {
        "users": [
            {"name": "Alice", "age": 30, "role": "admin"},
            {"name": "Bob", "age": 25, "role": "user"},
            {"name": "Charlie", "age": 35, "role": "user"}
        ]
    }

    print("Sample dataset:", sample_dataset)

    to_table = ToTable(render="jinja_native")
    result = to_table.render_object(
        dataset=sample_dataset,
        path="users{}",
        # select="name,age",
        format="simple"
    )
    print("\nResult:")
    print(result)