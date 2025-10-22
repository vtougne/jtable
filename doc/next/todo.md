

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

```





### Todo
| #         | category    |   task |
|------------------|-------|--------|
 1 | bug/fix    | unaccepeted chars in json format input
 1 | bug/fix    | Plugin issue on git bash: printf "2025-04-12 11:19:32" | jtable.exe -o "{{ (stdin | to_epoch) }}"
 1 | feature    | option as in to_table to name fileds --as hostname,os,cost
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


## Explore

https://github.com/aisbergg/python-templer

## New names

| ShortCut	|	Project name                |
|-----------|-------------------------------|
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