import dataclasses

@dataclasses.dataclass
class D:
    hoge: str = "hoge"

d = D()
print(d.hoge)
setattr(d, 'hoge', 'fuga')
print(d.hoge)

ababa = D()
print(ababa.hoge)