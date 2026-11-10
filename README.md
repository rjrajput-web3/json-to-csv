# json-to-csv

Convert a JSON array of objects to CSV. Stdlib only, no dependencies.

## Usage

```
json_to_csv.py [input.json] [--columns a,b,c] [--flatten]
```

- Reads JSON from a file, or from stdin when no file is given.
- Writes CSV to stdout, so you can redirect it to a file.
- Column order is the order keys first appear in the input.
- `--columns` picks a subset of columns, in the order you list them.
- `--flatten` expands one level of nested objects into dotted keys
  (`address.city`). Without it, nested values are JSON-encoded.
- Missing keys become empty cells; `null` becomes an empty cell.

## Examples

Input file `sample.json`:

```json
[{"name": "Asha", "city": "Pune", "orders": 3}, {"name": "Ben", "city": "Leeds", "orders": 1, "vip": true}]
```

```
$ python3 json_to_csv.py sample.json
name,city,orders,vip
Asha,Pune,3,
Ben,Leeds,1,true
```

Pick columns, in your order:

```
$ python3 json_to_csv.py --columns name,vip sample.json
name,vip
Asha,
Ben,true
```

Nested values, flattened:

```json
[{"name": "Asha", "address": {"city": "Pune", "pin": 411001}, "tags": ["new", "web"]}]
```

```
$ python3 json_to_csv.py --flatten nested.json
name,address.city,address.pin,tags
Asha,Pune,411001,"[""new"",""web""]"
```

Without `--flatten`, nested values are JSON-encoded instead:

```
$ python3 json_to_csv.py nested.json
name,address,tags
Asha,"{""city"":""Pune"",""pin"":411001}","[""new"",""web""]"
```

From stdin:

```
$ cat sample.json | python3 json_to_csv.py
name,city,orders,vip
Asha,Pune,3,
Ben,Leeds,1,true
```

## Exit codes

| Code | Meaning |
| ---- | ------- |
| 0 | Converted successfully |
| 1 | Bad input — missing file, invalid JSON, top level not an array, empty array, or an item that is not an object |
| 2 | Bad usage — `--columns` names a key that does not exist |

## Requirements

Python 3.8+ — standard library only.
