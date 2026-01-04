# Topic of your semestral work

# Note for pylint in CI/CD 
For some reason, Pylint cannot see PySide import, this happened to me in CLI as well but I managed to fix it there. These errors are false positives and should be completely ignored

## Documentation
Use `PYTHONPATH=src pdoc ./src -o ./docs` and then find docs in `docs/index.html`.


## Dev

### Run linter to check PEP8
`pylint src/`


### Use black to format code (for devs)
`black src/`


### Map format
`S` = Start \
`E` = End \
`#` Grass \
`X` = Dirt \
`.` = Air \
`*` = Coin \ 
`-` = Void
