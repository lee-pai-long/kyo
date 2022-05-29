# Kyo

A Flask and SQLAlchemy project bootstrap.

## Why Kyo

Because handling project plumbing is cumbersome and always the same.

With this project you can start with sane defaults.

I was planning on to make a [cookiecutter][1], but there is nothing to template
here.

## How to use it

- Clone the master branch
- Branch out to your own branch
- Start coding

## Contributing

You need at least git and build-essential

### Git clone this repository

```
$ git clone https://github.com/lee-pai-long/kyo
```

### Install the dev environment

```
$ make init
```

### Do your magic

- Run flask dev server

```
$ make run
```

*The server is then reachable at http://APPNAME.loc:5000*

- Use the flask shell

```
$ make shell
```

*The shell is a ipython REPL*

### Check the todo list

```
$ make todo
```

Shows code tags(TODO, FIXME, CHANGED, XXX, REVIEW, BUG, REFACTOR, IDEA, WARNING)
in all project.

### Lint the code

```
$ make lint
```

### Run the test suite

```
$ make test
```

### Check dependencies vulnerabilities

```
$ make safe
```

### Connect to database

```
$ make db
```

*The shell is provided by litecli*

### Check for code smells

```
$ make smell
```

### List all make helper tasks

```
$ make help
```

### Activate the virtualenv

```
$ pyenv activate $VIRTUALENV
```

*$VIRTUALENV is added to the user environment by*
*direnv as '{project_name}-{branch}'*

### Create a migration

*With the virtualenv activated*

```
$ alembic revision -m "<name of the revision>"
```

### Upgrade migration

```
$ alembic upgrade head
```

or

```
$ alembic upgrade +1
```

### Downgrade migration

#### Downgrade to 0

```
$ alembic upgrade base
```

or

#### Downgrade to the previous revision

```
$ alembic downgrade -1
```

For more usage of Alembic run:

```
$ alembic --help
```

Also if you are not familiar with Alembic check the [tutorial][2]

[1]: https://github.com/cookiecutter/cookiecutter
[2]: https://alembic.sqlalchemy.org/en/latest/tutorial.html
