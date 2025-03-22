#!/usr/bin/env python3

import xmltodict

xml_data = """
<root>
    <child>
        <subchild>data</subchild>
    </child>
</root>
"""

dict_data = xmltodict.parse(xml_data)
print(dict_data)
