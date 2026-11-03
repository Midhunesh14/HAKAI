# HAKAI Standard Library Reference

## 1. `math`
- `math.sqrt(x)`: Square root of $x$
- `math.pow(x, y)`: $x^y$
- `math.abs(x)`: Absolute value
- `math.floor(x)`, `math.ceil(x)`, `math.round(x)`
- `math.sin(x)`, `math.cos(x)`, `math.tan(x)`
- `math.pi`, `math.e`

## 2. `strings`
- `strings.len(s)`: String character count
- `strings.upper(s)`, `strings.lower(s)`
- `strings.trim(s)`: Strip whitespace
- `strings.split(s, delimiter)`: Split into array
- `strings.join(arr, delimiter)`: Combine array into string
- `strings.contains(s, sub)`: Boolean check
- `strings.replace(s, old, new)`: Replace occurrences

## 3. `collections`
- `collections.push(arr, item)`: Append element
- `collections.pop(arr)`: Remove and return last element
- `collections.length(coll)`: Number of items
- `collections.keys(map)`: List of map keys
- `collections.values(map)`: List of map values
- `collections.has_key(map, key)`: Check map key presence

## 4. `files`
- `files.read_text(path)`: Read file to string
- `files.write_text(path, content)`: Overwrite file with content
- `files.append_text(path, content)`: Append content to file
- `files.exists(path)`: Check existence
- `files.delete(path)`: Delete file
- `open(path, mode)`: File object context

## 5. `io`
- `print(...)`: Print values to standard output
- `println(...)`: Print with newline
- `input(prompt)`: Read line from standard input

## 6. `system`
- `system.time()`: Current epoch timestamp
- `system.sleep(seconds)`: Pause execution
- `system.platform()`: Host operating system name
- `system.version()`: HAKAI version string
- `system.args()`: Array of command-line arguments
- `system.exit(code)`: Terminate process with exit code

