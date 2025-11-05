# Exploring args parse and shell completion as part of jtable project

> Focus only on the following files:  
- cli_parser.py
- Apps.py


# Goal

Help the user using cli_parser to complete by watching into Apps Class:  
Apps.AppsModule().apps()

# notes

Bash completion is used for comptabibility with git bash

# how to test:

```bash
source jtable-completion.bash
./cli_parser.py <TAB>
# display:
# abs             attr            batch           capitalize      [...]
./cli_parser.py <F4>
# display
# Hello vince
# hostname    os     cost    state        env
# ----------  -----  ------  -----------  -----
# host_1      linux  5000    alive        qua
# host_2      linux  5000    alive        qua
# host_3      linux          unreachable  qua


```

# Steps
- [x] suggest entry Apps.AppsModule().list_all() while user using tabulattion
- [ ] show preview when F4 pressed
    - [x] main feature
    - [ ] Bug/fix: the CtrlC in not taken in main completion menu (in preview it works)

