# wandb4make

A wandb sweep script for make/cmake projects

## Sample sweep config
```yaml
program: hp_search.py
method: grid
metric:
  goal: maximize
  name: performance
name: hoge
parameters:
  hoge:
    values:
    - 16
    - 32
  foo:
    values:
    - a
    - b
```

## License
MIT
