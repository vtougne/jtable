# How to Test Tab Completion

## What I Fixed

1. **Updated cli_parser.py** (/home/vince/repos/jtable/jtable/cli_parser.py:47):
   - Changed from custom completer to `argcomplete.completers.ChoicesCompleter`
   - This provides more reliable completion using `Apps.AppsModule().list_all()`

2. **Verified the list works**:
   - 55 apps/filters available (2 custom + 53 Jinja built-ins)
   - Includes: to_table, to_yaml, tojson, upper, etc.

## Step-by-Step Test Instructions

### Step 1: Open a NEW terminal/shell session

### Step 2: Register completion for THIS session only
```bash
cd /home/vince/repos/jtable/jtable
eval "$(register-python-argcomplete ./cli_parser.py)"
```

### Step 3: Test tab completion
Now try these (press TAB where indicated):

```bash
# Test 1: Complete 'to' prefix
./cli_parser.py to<TAB>
# Expected: to_table, to_yaml, tojson

# Test 2: Complete 'upp' prefix
./cli_parser.py upp<TAB>
# Expected: upper

# Test 3: Show all options
./cli_parser.py <TAB><TAB>
# Expected: All 55 options listed

# Test 4: Verify a selection works
./cli_parser.py to_table
# Expected: "Selected app/filter: to_table"
```

## To Make It Permanent

If the above tests work, add this to your ~/.bashrc:

```bash
echo 'eval "$(register-python-argcomplete /home/vince/repos/jtable/jtable/cli_parser.py)"' >> ~/.bashrc
```

Then reload:
```bash
source ~/.bashrc
```

## Troubleshooting

### If completion doesn't work:

1. **Check argcomplete is installed:**
   ```bash
   python3 -c "import argcomplete; print('OK')"
   ```

2. **Verify completion is registered:**
   ```bash
   complete -p cli_parser.py
   ```
   Should show: `complete -o bashdefault... _python_argcomplete cli_parser.py`

3. **Check the list manually:**
   ```bash
   ./cli_parser.py --list-apps
   ```
   Should show all 55 options

4. **Try re-registering:**
   ```bash
   eval "$(register-python-argcomplete ./cli_parser.py)"
   ```

### Still not working?

Try this diagnostic:
```bash
# Set debug mode
export _ARC_DEBUG=1
./cli_parser.py to<TAB>
```

This will show what argcomplete is doing.

## What Gets Completed

The completion suggests entries from `Apps.AppsModule().list_all()`:

**Custom apps (2):**
- to_table
- to_yaml

**Jinja built-ins (53):**
- abs, attr, batch, capitalize, center, default, dictsort, escape, filesizeformat, first, float, forceescape, format, groupby, indent, int, items, join, keys, last, length, list, lower, map, max, min, pprint, random, reject, rejectattr, replace, reverse, round, safe, select, selectattr, slice, sort, string, striptags, sum, title, tojson, trim, truncate, unique, upper, urlencode, urlize, values, wordcount, wordwrap, xmlattr
