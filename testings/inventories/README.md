

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

### view groups and vars ansible play 

```bash
ansible-playbook -i dev/pay/hosts_dc_1.ini play_view_inventoy.yml | jtable -q view_hosts.yml
```
### read multi jsons

```bash
jtable -jfs {config}:export*.json -p [0].content.global_custom_stats
```