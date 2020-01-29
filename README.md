# 概要

configを自動生成する

## 使用方法

- インストール
```shell script
echo ".config.lock" >> ./.gitignore
pip install git+https://github.com/Nkriskeeic/configer#egg=configer
mkdir setting
vi setting/default.yml (もちろんemacsでもよい)
vi setting/optimizer.yml (もちろんemacsでもよい)
vi setting/training.yml (もちろんemacsでもよい)
```

- default.ymlには以下の内容を記述（例）
```yaml
models:
  BaseMLP:
    in_channels: 32
    middle_channels: 64
    middle_depth: 3
    out_channels: 1
    activation: ReLU
    last_activation:
    drop_out: 0.5
    batch_norm: false
use_model: BaseMLP
loss: mean_absolute_error
optimizer:
  adam:
    alpha: 0.1
    beta: 0.09
scheduler: cosine

training:
  batchsize: 64
```

- optimizer.ymlには以下の内容を記述（例）

```yaml
optimizer:
  adam:
    alpha: 0.2
```
- training.ymlには以下の内容を記述（例）
```yaml
training:
  batchsize: 128
```

- settingを読み込む
```shell script
configer create --setting setting/default.yml --output default.py
```

default.pyが生成される

実装する時
```python
from default import ConfigGenerator, Config
config = ConfigGenerator(default_from='setting/default.yml')\
            .generate()  # default値が使用される

config = ConfigGenerator(default_from='setting/default.yml')\
            .update(['optimizer.yml', 'training.yml'])
            .generate()  # default値が上書きされて使用される

config.training.batchsize  # intでサジェストされる
```

- \[default.ymlを更新した場合\]
```shell script
configer update
````