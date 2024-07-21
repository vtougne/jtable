### test coloring

```bash
for code in {0..255}
    do echo -e "\e[38;5;${code}m"'\\e[38;5;'"$code"m"\e[0m"
  done
```

- https://stackoverflow.com/questions/60598837/html-to-image-using-python

- https://pypi.org/project/ansi2html/

- https://askubuntu.com/questions/79280/how-to-install-chrome-browser-properly-via-command-line

### Color Latex

$`\textcolor{red}{\text{your text}}`$   
$`\textcolor{cyan}{\text{your text}}`$   
$`\textcolor{blue}{\text{your text}}`$   
$`\textcolor{teal}{\text{your text}}`$   

### Color using diff

```diff
- RED text
+ GREEN text
! ORANGE text
# GRAY text
```

### text yaml

\- hosts: localhost  
  &nbsp;&nbsp;&nbsp;tasks:  
&nbsp;&nbsp;&nbsp;- name: Install packages  
    apt:  
      name:  
        - package1  
        - package2  
        - package3  
      state: present  
