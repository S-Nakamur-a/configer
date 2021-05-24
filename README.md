# Configer

This tool generates a corresponding Python script from a YAML file.
The Python script defines the Config class, which declares all values written in YAML with type annotations.
This allows the editor to perform autocomplete when accessing configuration values during coding. Also, the IDE detects type mismatches, which reduces bugs.
As an additional feature, it is possible to detect which YAML file initializes or updates each setting values.

## How to installs

```shell script
pip install git+https://github.com/Nkriskeeic/configer#egg=configer
```

## How to use

### 1. Write default setting values in one YAML file.

example: *\<ProjectDir\>*/config/default.yml

```yaml
models:
  base_mlp:
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

### 2. Convert the default YAML file into Python script by `configer`

```shell script
$ configer create -s <ProjectDir>/config/default.yml -o <ProjectDir>/src/config/default.py
```

### 3. Use the Python script in other scripts.

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
  base_mlp:
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
  base_mlp:
    middle_channels: 32
loss: mean_absolute_error
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
