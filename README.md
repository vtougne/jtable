[[_TOC_]]

### cli usage
#### simple
```
cat dataset.yml | jtable -jp host
```
equivalent to
```
cat dataset.yml | jc --yaml | jq '.[0].host' | jtable
```
#### with query file
```
cat dataset.yml | jtable -jp host -q ansible/jtable_query_sample.yml 
```
equivalent to
```
cat dataset.yml | jc --yaml | jq '.[0].host' | jtable -q ansible/jtable_query_sample.yml 
```
#### scraping
```
curl -s https://samples-files.com/samples/Code/json/sample3.json | jtable
```
#### Inside ansible
```bash
ansible-playbook ansible/test_jtable_filter.yml
```

#### ansible inventory
```bash
ansible all -i ../ansible/inventory.yml -m ansible.builtin.setup | jtable -jp 'plays[0].tasks[0].hosts' -q ../jtable/inventory_view.query_file.yml
export ANSIBLE_STDOUT_CALLBACK=json
ansible all -i inventory.yml -m ansible.builtin.setup > ansible_facts.json
cat ansible_facts.json | jq  '.["plays"][0]|.["tasks"][0]["hosts"]' | jtable -q ../jtable/inventory_view.query_file.yml
cat ansible_facts.json | jq  '.["plays"][0]|.["tasks"][0]["hosts"]["alice"]["ansible_facts"]|keys'
```

### Functioning
#### query_set

```yaml
jtable:
    dataset:                # key / value data, list or dict
    queryset:               # optiional
      select:               # contains field labels and jinja filter 
        - as:               # label of field
          expr:             # jinja expression
        - as:               # ...
          expr:
        ...
    agregat:                # contains
      group_by:             # f1,f2,f3
      functions:            # count(f4), avg(f5)
    styling:
      - style:              # font-color=pink, bg-color=yellow, font=bold ...
        when:               # jinja expresseion returning true / false
    out:                    # text, color_text, gitlab_md, github_md, pdf, html, html_js

```

#### return
```yaml
dict_object:                # default contains json,text, color_text
  json:                     # list of key / value filtered without styling
  th:                       # list of headers
  td:                       # list of values
  text:                     
  color_text:
  gitlab_md:
  github_md:
  pdf:
  html:
```
        

#### Todo
- [ ] add styling
- [ ] facilitate ordering

#### Deatures
- diffrent outputs formats
  - text
  - json
  - th (list of headers)
  - td (list of rows)
  

