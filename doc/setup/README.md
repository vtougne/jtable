[[_TOC_]]
# Setup
  
Clone repo

```bash
git clone git@github.com:vtougne/jtable.git
```

Install

```bash
cd jtable
pip install .
```

## known issues
- on Cygwin / Git bash env  
  jtable freeze (python also)
fix: 
```bash
winpty ./jtable.exe
```
notes: https://stackoverflow.com/questions/48199794/winpty-and-git-bash

