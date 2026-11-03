# HAKAI Module System

HAKAI features a structured module system that enables clean code organization and reuse.

## Importing Modules
```hakai
// Import whole module
import math

print(math.sqrt(16))

// Import with alias
import strings as s
print(s.upper("hakai"))

// Import specific symbols
from math import sqrt, pow
print(sqrt(64))
```

## Module Search Order
1. Built-in standard modules (`math`, `strings`, `collections`, `files`, `io`, `system`).
2. Current working directory / script directory.
3. HPM installed package directory (`.hakai_packages/`).
4. HAKAI standard library path (`HAKAI_STDLIB_PATH`).

Circular imports are detected at runtime and report descriptive `HakaiImportError` diagnostics.

