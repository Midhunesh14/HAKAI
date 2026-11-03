# Functions in HAKAI

Functions in HAKAI are first-class citizens. They can be assigned to variables, passed into other functions, and returned from functions.

## Syntax
```hakai
function function_name(param1, param2 = default_value) {
    // Body
    return value
}
```

## Closures
Functions retain the environment in which they were created:
```hakai
function make_counter() {
    let count = 0
    function tick() {
        count = count + 1
        return count
    }
    return tick
}

let counter = make_counter()
print(counter()) // 1
print(counter()) // 2
```

## Recursion
```hakai
function factorial(n) {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}

print(factorial(5)) // 120
```

