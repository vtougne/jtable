


# Jtable  
jtable helps you to render table from key / values sources like json, yaml, and Python key / values.  
It works as a cli ina shell and Jinja filter that may be integrated in a Python framework like Ansible, Django, Flask and others  


```yaml
- hostname: host_1
  os: linux
  cost: 5000
  state: alive
  env: qua
- hostname: host_2
  os: linux
  cost: 5000
  state: alive
  env: qua
- hostname: host_3
  os: linux
  state: unreachable
  env: qua
```
```bash

cat host_dataset.yml  | jtable
```
output:

```text
hostname    os       cost  state        env
----------  -----  ------  -----------  -----
host_1      linux    5000  alive        qua
host_2      linux    5000  alive        qua
host_3      linux          unreachable  qua

```
## Examples

- [Setup](./doc/setup/README.md)
- [Examples](./doc/examples/README.md)


---

### Todo

- [ ] manage multijson string [stakoverflow](https://stackoverflow.com/questions/27907633/how-to-extract-multiple-json-objects-from-one-file)
- [ ] select as argument in cli