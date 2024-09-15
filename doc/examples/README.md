[[_TOC_]]
## Overview  
- jtable helps you to render table from key / lists / values sources like json, yaml, and Python objects.  
- It works as a cli in a shell and as a Jinja filter that may be integrated in a Python framework like Ansible, Django, Flask and others  
## Simple usage

  
#### json coming from curl

command: 
```bash
curl -s https://samples-files.com/samples/Code/json/sample3.json | jtable -p books
```
output:

```
text💥 Something was wrong with this report
 cmd was  ->  curl -s https://samples-files.com/samples/Code/json/sample3.json | jtable -p books
```
