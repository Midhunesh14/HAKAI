# HAKAI Syntax Reference

This document provides a concise syntax reference for the HAKAI language.

## 1. Programs
Optional program block wrappers:
```hakai
HAKAI START
// statements
HAKAI END
```

## 2. Variables & Constants
```hakai
let age = 21
let name = "Santhiya"
let height = 5.8
let is_student = true

const MAX_CONNECTIONS = 100
```

## 3. Data Structures
```hakai
// Array
let numbers = [10, 20, 30, 40]
let first = numbers[0]
numbers[1] = 25

// Map
let user = {"id": 1, "username": "alex"}
let uname = user["username"]

// Tuple
let coords = (10, 20)
```

## 4. Control Structures

### If - Else If - Else
```hakai
if age >= 18 {
    print("Eligible")
} else if age >= 16 {
    print("Conditional")
} else {
    print("Not Eligible")
}
```

### Repeat
```hakai
repeat 5 {
    print("Iteration")
}
```

### While
```hakai
let count = 0
while count < 10 {
    count = count + 1
    if count == 5 {
        continue
    }
    if count == 8 {
        break
    }
}
```

## 5. Functions
```hakai
function add(a, b) {
    return a + b
}

let result = add(10, 20)
```

## 6. Classes
```hakai
class Student {
    function init(name, age) {
        self.name = name
        self.age = age
    }

    function display() {
        print(self.name)
        print(self.age)
    }
}

let s = Student("Santhiya", 21)
s.display()
```

