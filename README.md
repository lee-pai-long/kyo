# APP

## Contributing

You need at least git and build-essential

### Git clone this repository

```
$ git clone
```

### Check the Vagrant environment documentation

```
$ make help
```

Execute necessary steps in any:

### Install dev the environment

```
$ make init
```

### Do your magic

- Run flask dev server

```
$ make run
```

*The server is then reachable at http://<appname>.loc:5000*

- Use the flask shell

```
$ make shell
```

*The shell is a ipython REPL*


### Check the todo list

```
$ make todo
```

Show code tags(TODO, FIXME, CHANGED, XXX, REVIEW, BUG, REFACTOR, IDEA, WARNING)
in all project

### Lint the code

```
$ make lint
```

### Check for code smell

```
$ make smell
```

### Run the test suite

```
$ make test
```

### Check dependencies vulnerabilities

```
$ make safe
```

### List all make helper tasks

```
$ make help
```
