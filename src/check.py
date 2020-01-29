import dataclasses

@dataclasses.dataclass
class A:
    piyo = 1

@dataclasses.dataclass
class D:
    hoge: A = dataclasses.field(init=False)

    def __post_init__(self):
        self.hoge = A()


class E:
    def __init__(self):
        self.d = None

    def get_d(self, update):
        self.d = D()
        print(self.d)
        if update:
            self.update()
        return self.d

    def update(self):
        setattr(self.d, 'hoge', 'fuga')


e = E()
d = e.get_d(update=True)
print(d.hoge)

e2 = E()
d2 = e2.get_d(update=False)
print(d2.hoge)
