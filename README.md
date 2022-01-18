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

## [Optional] Add this projetc to your project
### Add
```bash
cd your_git_project
git remote add wandb4make https://github.com/enp1s0/wandb4make
git subtree add --prefix wandb4make --squash wandb4make main
```

### Update
```bash
git subtree pull --prefix wandb4make --squash wandb4make main
```

## License
MIT
