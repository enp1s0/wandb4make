# wandb4make

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
```

## License
MIT
