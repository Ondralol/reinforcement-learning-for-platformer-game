# Reinforcement Learning for a Platformer Game
I built a simple 2D platformer game and then implemented a Q-learning reinforcement learning algorithm that taught an agent how to win that game. More details can be found in [report](/report.pdf)

## User guide

### Prerequisites
- `Python >= 3.11`
- `Pip`

### Install dependencies
```
pip install -r requirements
```

### Run the application
```
python3 src/main.py
```
Note: Use appropriate Python alias for your environment (python3, python, py)

### How to use the Application
Upon opening the application, user can choose to either play the game (testing purposes) or let the agent play the game.
#### Player mode
- User can use `WASD` and `JUMP` to control the game and `R` to restart the game
#### Agent mode
- User can watch the agent learn and change the agent training speed. Statistics about the agent are also shown.

### Map format
User can create their own maps and add them in `maps/` folder. The maps must be **rectangular** and maps that are either too small or too large maps might cause issues. \
Format of the tiles is as follows:
`S` = Start \
`E` = End \
`#` Grass \
`X` = Dirt \
`.` = Air \
`*` = Coin \ 
`-` = Void

### CLI Arguments
To show all CLI arguments use 
```
python3 src/main.py -h
```

### Documentation
To generate documentation use `PYTHONPATH=src pdoc ./src -o ./docs` and then find docs in `docs/index.html`.


## Dev Guide

### Note regarding pylint in CI/CD 
For some reason, when running Pylint inside CI/CD there are PySide import errors, however,  these errors are false positives and should be completely ignored



### Run linter to check PEP8
```
pylint src/
```
Note: Because I'm building a game with a lot of physics and also an agent that accepts a lot of arguments, I had to disable a few unnecessary Pylint codes. A high number of parameters is common for both Machine Learning models and complex Game class constructors. A higher branching factor is also necessary due to collision detection and splitting logic into multiple functions would only cause code duplications, more parameters and possible errors.

### Run tests
```
pytest
```

### Use black to format the code
``` 
black src/
```

