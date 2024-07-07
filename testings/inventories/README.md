

### list hosts nad vars

```bash
ansible-inventory -i ./dev/pay --list
```
### list groups

```bash
ansible -i . localhost -m debug -a "var=groups"
```


### json callback

```bash
export ANSIBLE_STDOUT_CALLBACK=json
export ANSIBLE_SHOW_CUSTOM_STATS=true
```

### view whole inventory

```bash
ansible-playbook $(find . -name hosts_dc*.ini |  sed "s/.*/-i &/g") \
  play_view_inventoy_use_debug.yml | jtable -q view_hosts_use_debug.yml
```