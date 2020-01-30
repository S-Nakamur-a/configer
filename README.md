# 概要

configファイルをPythonに直書きするのはちょっと気が引けるし、
yamlとかで管理したいけどそうすると補完が効かなくなるし型アノテーションも出来なくなるし、
う〜〜〜〜ん！という方のためのconfigモジュール

なるべくyacsから乗り換えやすく設計したつもり

- 全てのconfigのデフォルト値を１つのyamlに記述しておく（yacsのpythonファイルと同じノリ）
- configer cliを提供しているので、上のyamlからdefault.pyを生成する
- default.pyに、ConfigGeneratorとConfigがクラスとして用意されている
- main.pyとかで `config = ConfigGenerator(default_from='default.yml').generate()` のように書けば, yamlファイルの内容をPythonオブジェクトとして生成してくれる
- `config = ConfigGenerator(default_from='default.yml').update('hoge.yml').generate()`とかで一部を上書きして使用することも出来る（型が一致していないと落ちる）
- `config.pprint(wait=True)`とかでconfigを見やすく表示してくれる
- `config.save(out_path, 'yaml')`とかで最終的なconfigを保存してくれる
- 次回は`config = ConfigGenerator(default_from='default.yml').update(out_path).generate()`で同じ内容を復元できる

## 使用方法

### インストール
```shell script
pip install git+https://github.com/Nkriskeeic/configer#egg=configer
```

### default.ymlからdefault.pyを生成する

```shell script
echo ".config.lock" >> ./.gitignore  # どのdefault.ymlからどのdefault.pyを生成したかを記録するためのファイル
mkdir setting
vi setting/default.yml (もちろんemacsでもよい)
```

default.ymlには以下の内容を記述（例）
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

生成する
```shell script
configer create --setting setting/default.yml --output default.py
```

### コード上から利用する
```python
from default import ConfigGenerator, Config
config: Config = ConfigGenerator(assert_identical_to_default=True).generate()  # 生成に使用したymlから変更がないかを確認してconfigをloadする
config.pprint(wait=False)  # configを表示してくれる
in_channels = config.models.BaseMLP.in_channels  # サジェストが出るし、int型であることを追ってくれる
```

### 一部の設定を上書きして利用する

設定値は全てdefault.ymlに存在し、型が同じ時だけ上書きを許している

- （例）optimizer.ymlに以下の内容を記述
```shell script
vi setting/optimizer.yml
```
```yaml
optimizer:
  adam:
    alpha: 0.2
```
- training.ymlには以下の内容を記述（例）
```shell script
vi setting/training.yml (もちろんemacsでもよい)
```
```yaml
training:
  batchsize: 128
```

### コード内で呼び出す

```python
config = ConfigGenerator()\
            .update(['setting/optimizer.yml', 'setting/training.yml'])  # optimizerとtrainingで同じ項目を上書きしようとするとエラーになる
            .generate()  # default値が上書きされて使用される
config = ConfigGenerator()\
            .update('setting/optimizer.yml')  # updateを分ければ衝突項目があっても問題ない
            .update('setting/training.yml')  # 仮に衝突する項目がある場合は、後からupdateしたほうが優先される
            .generate()  # default値が上書きされて使用される

# 保存
config.save_as('some_path', 'yaml')  # yaml形式で保存する
```

### default.ymlを更新した場合
```shell script
configer update
````
lockファイルを見て更新があればcreateしたときと同じパスで更新をかけてくれる
