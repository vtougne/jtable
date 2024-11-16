
# local install without connection to any external service PyPI or others

```bash
pip install --no-index --find-links=dependencies
```


# create wheel

```bash
python3 setup.py bdist_wheel
```

```bash
cd dist
pip install jtable-0.9.8-py3-none-any.whl
```

```bash
cd jtable
pyinstaller --name jtable.exe --distpath ../dist --onefile jtable.py
```

### from windows MINGW64
```bash
cd jtable
python -m PyInstaller  --name jtable.exe --distpath ../dist --onefile jtable.py
python -m PyInstaller  --workpath ../build --specpath ../build --name jtable.exe --distpath ../dist --onefile jtable.py
```

### from windows
```bash
cd jtable
python -m PyInstaller --name jtable.exe --distpath ..\dist --onefile jtable.py
python -m PyInstaller --workpath ../build --specpath ../build --name jtable.exe --distpath ../dist --onefile jtable.py
```

### build setup file
```bash
"C:\Program Files (x86)\NSIS\makensis.exe" jtable.nsi
```
