
```bash
for code in {0..255}
    do echo -e "\e[38;5;${code}m"'\\e[38;5;'"$code"m"\e[0m"
  done
```

- https://stackoverflow.com/questions/60598837/html-to-image-using-python

- https://pypi.org/project/ansi2html/


- https://askubuntu.com/questions/79280/how-to-install-chrome-browser-properly-via-command-line