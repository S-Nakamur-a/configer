# Configer

This is a configuration management tool for Python projects.

It is an inevitable problem that your editor does not complement variable names and predict their types
when you load setting values ​​from YAML files.

This tool provides a converter from your YAML files to python files with type annotations.

## How to installs

```shell script
pip install git+https://github.com/Nkriskeeic/configer#egg=configer
```

## How to use

### 1. Write default setting values in one YAML file.

example: *\<ProjectDir\>*/config/default.yml

```yaml
models:
  BaseMLP:
    in_channels: 3
    middle_channels: 64
    out_channels: 3
    activation: ReLU
loss: mean_absolute_error
optimizer:
  adam:
    alpha: 0.1
    beta: 0.09
scheduler: cosine
```

### 2. Convert the default YAML file into Python script with `configer`

```shell script
$ configer create -s <ProjectDir>/config/default.yml -o <ProjectDir>/src/config/default.py
```

### 3. Import the converted Python script in other scripts.

example: main.py
```python
from config.default import ConfigGenerator, Config


config: Config = ConfigGenerator().generate()  # generates a config object.
config.pprint(wait=False)  # display your setting values
in_channels = config.models.BaseMLP.in_channels  # your editor may complement these names and predict its type (int)

config.models.BaseMLP.in_channels = 1  # raises Error. These setting values are read-only.
```

### CASE1: Update default values.

1: update your default YAML file.

```yaml
models:
  BaseMLP:
    in_channels: 3
    middle_channels: 32  # <- previous is 64
    out_channels: 3
    activation: ReLU
loss: mean_absolute_error
optimizer:
  adam:
    alpha: 0.1
    beta: 0.09
scheduler: cosine
```

2: then update your Python script with `configer`.

```shell script
$ configer update
```

If you do not update your Python script,
`default.ConfigGenerator().generate()` will raise `ChangeDefaultError`.

### CASE 2: Overwrite default setting values.

1. Write new values in your YAML file(s).

model.yml
```yaml
models:
  BaseMLP:
    middle_channels: 32  # <- default is 64
```

loss.yml
```yaml
loss: mean_squared_error  # <- default is mean_absolute_error
```

main.py
```python
from config.default import ConfigGenerator, Config


config: Config = ConfigGenerator() \
                    .update_by(['model.yml', 'loss.yml']) \
                    .generate()  # Overwrite default values
config.pprint(wait=True)  # display your setting values and Which values ​​were overwritten by which files
```

### CASE 3: Save your current setting values.

```python
from config.default import ConfigGenerator, Config


config: Config = ConfigGenerator().generate()
config.save_as(output_path, 'yaml')  # dumps current values as one YAML file.
```
