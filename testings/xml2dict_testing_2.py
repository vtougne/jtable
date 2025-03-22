#!/usr/bin/env python3

import xmltodict

xml_file = open("informatica_wkf_sample.xml", "r")
xml_data = xml_file.read()
xml_file.close()

dict_data = xmltodict.parse(xml_data)
print(dict_data)
