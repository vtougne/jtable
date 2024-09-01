[[_TOC_]]
# coucou

```bash
hostname    os       cost  state
----------  -----  ------  -----------
host_1      linux    5000  alive
host_3      linux     200  unreachable
host_4      linux     [0;31m200  [0malive
host_5      linux     200  unreachable

```
format: github
| hostname   | os      | state       |   cost |
|------------|---------|-------------|--------|
| host_1     | linux   | [0;32malive[0m       |   5000 |
| host_2     | windows |             |    200 |
| host_3     | linux   | [4;31munreachable[0m |    200 |
| host_4     | aix     | [0;32malive[0m       |    200 |
| host_5     | linux   | [4;31munreachable[0m |    200 |
