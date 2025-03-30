
### Next Power Template
pt player <template-play.yml> --vars name = vince  --vars ... --data {"location": "Paris"}
pt free "{{ stdin | from_xml | to_table }}"
cat dataset.json | pt to_table -p hosts -s hostname,location
cat dataset.xml | pt filter from_xml to_table

### Todo
| #         | category    |   task |
|------------------|-------|--------|
 1 | bug/fix    | unaccepeted chars in json format input
 1 | feature    | option infile_filters / functions / types
 1 | feature    | option custom filter / plugin /functions
 1 | feature    | option data caching, optioon: cached_vars = var_1, var_2
 1 | feature    | encryption
 1 | feature    | limit rendering / preview / pagination
 2 | feature    | optional output formats: pdf, xls
 2 | feature    | optional input formats: xml, html
 2 | feature    | limit inspect to 1000 values found, 0 for unlimited, q0 for no pagination
 2 | feature    | manage multijson inputs [stakoverflow](https://stackoverflow.com/questions/27907633/w-to-extract-multiple-json-objects-from-one-file)
 2 | feature    | args copletion ++path
 2 | bug/fix    | cross path can't target key containing double quotes, escaping must be implemented
 2 | refacto    | class decoupling in seperated modules


## Done
| #         | category    |   task |
|------------------|-------|--------|
 2 | feature    | select as argument in cli ++ unselect
 2 | feature    | from_xml
 2 | feature    | from_flatten: convert text as list of dict [ "value": "row1","value": "row2",... ]