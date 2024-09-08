from typing import Any


class Test:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def get_value(self, value: str) -> Any:
        return getattr(self, value)


class Test1:

    @staticmethod
    def get_value(obj: Any, value: str) -> Any:
        return getattr(obj, value)


test = Test(name="Tom", age=15)
test1 = Test1()

print(test)
print(test1.get_value(test, "age"))  # 15
