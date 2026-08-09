

#### Next
```
CLI Endpoints:
- jtable            # Filter cascading
- jtable-play       # Play a sequence written in yaml
- jtable-template   # Template string or file



jtable usage:
    # first action may be a module, for example load_json, and the suite is anytime a filter
      jtable [module <module options>] [ filter <filer options> ] [ filter <filter options> ]

    # Or a filter, assuming data are piped from stdin
      echo <some_data> | jtable [ filter <filer options> ] [ filter <filter options> ]
    

    # Examples
        jtable load_json <json_file> to_table -p hosts -s hostname,os,state
        # will be equivalent to 
        jtable load_json <json_file> to_nice_yaml
        cat hosts_dataset.json | jtable from_json to_table -p hosts -s hostname,os,state


jtable-play:
    jtable [-f|--file] <jtable_playbook.yml> 
    jtable <jtable_playbook.yml> -v "first_name=john" -d '{"last_name": "Doe"}'


jtable-template:
    echo John | jtable-template "Hello {{ stdin }}"


```





### Todo
| #         | category    |   task |
|------------------|-------|--------|
|   | feature    | --sort column by rows
|   | feature    | limit rendering / preview / pagination
|   | feature    | limit inspect to 1000 values found, 0 for unlimited, q0 for no pagination
|   | feature    | option custom filter / plugin /functions
|   | feature    | option data caching, optioon: cached_vars = var_1, var_2
|   | feature    | optional output formats: pdf, xls
|   | bug/fix    | jtable-play variable precedence
|   | feature    | manage multijson inputs [stackoverflow](https://stackoverflow.com/questions/27907633/w-to-extract-multiple-json-objects-from-one-file)
|   | feature    | encryption
|   | bug/fix    | Plugin issue on git bash: printf "2025-04-12 11:19:32" | jtable.exe -o "{{ (stdin | to_epoch) }}"
 ✅ | feature    | -as rename field in selection
✅  | feature    | --inspect as a filter
✅  | feature    | --reverse column by rows
 ✅ | feature    | optional input formats: xml, html
 ✅ | feature    | select as argument in cli ++ unselect
 ✅ | feature    | from_xml
 ✅ | feature    | from_flatten: convert text as list of dict [ "value": "row1","value": "row2",... ]
 ✅ | bug/fix    | cross path can't target key containing double quotes, escaping must be implemented
 ✅ | refacto    | class decoupling in seperated modules


## Explore

https://github.com/aisbergg/python-templer

## New names

| ShortCut	|	Project name                |
|-----------|-------------------------------|
|	jd      |	jdcode
|	ol      |	opslab
|	ml      |	mylab
|	frog    |	frog
|	clup    |	close-up
|	dm 		|	data-mute
|	dc 		|	data-chemist
|	sk      |	skiner
|	tb 		|	tabulable
|	dp 		|	data-picker
|	snatch  |	snatcher
|	burst   |	burster
|	dp 		|	dtpick
|	tm 		|	transmutable
|	tb 		|	tabulon
|	rd 		|	remodeler
|	rd 		|	redoer
|	ft 		|	From2 / FromTo
|	fl 		|	flavored
|	mt 		|	metamorphose
|	rec 	|	recaster
|	ag 		|	angulate
|	xm 		|	xmute
|	dp 		|	data-pumper
|	cr		|	crabber
|	crab	|	crab
|	gr		|	graby
|	xc		|	xConv
|	io		|	InputOuput
|	tg		|	tego
|	rex		|	rex