# 概要

configを自動生成する

## 使用方法

- インストール
```shell script
echo ".config.lock" >> ./.gitignore
pip install git+https://github.com/Nkriskeeic/configer#egg=configer
mkdir setting
vi setting/setting.yml (もちろんemacsでもよい)
```

- setting.ymlには以下の内容を記述（例）
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

- settingを読み込む
```shell script
configer create --setting setting/setting.yml --output config.py
```

config.pyが生成される

- \[setting.ymlを更新した場合\]
```shell script
configer update
````

## config.pyがあると嬉しいこと

```python
from config import Config
# 設定値を読み込む
# configerで指定したファイルが読み込まれる
my_config = Config.load(setting_file_path)

# wait_yesをTrueにすると設定値を表示したまま一時停止する
# ここで設定値に問題がないかをチェックする
my_config.pprint(wait_yes=True)

# 設定値を保存する
my_config.save(some_out_dir)

# 実際に設定値にアクセスする
in_channels = my_config.models.BaseMLP.in_channels  # 予測変換はもちろん，int型をエディタが認識する
```

