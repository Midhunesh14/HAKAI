# Object-Oriented Programming in HAKAI

HAKAI supports clean object-oriented programming with classes, single inheritance, instance methods, constructors, static methods, and member encapsulation.

## Class Definition
```hakai
class Animal {
    function init(name) {
        self.name = name
    }

    function speak() {
        print(self.name + " makes a sound.")
    }
}
```

## Inheritance
Use the `extends` keyword:
```hakai
class Dog extends Animal {
    function speak() {
        print(self.name + " barks: Woof!")
    }
}

let d = Dog("Rex")
d.speak()
```

## Static Methods
Methods declared with `static` belong to the class:
```hakai
class MathUtil {
    static function square(x) {
        return x * x
    }
}

print(MathUtil.square(9))
```
