# Onboarding Makefile
# -------------------
# '||:' is a shortcut to '|| true' to avoid the
# 'make: [target] Error 1 (ignored)' warning message.

# Switch to bash instead of sh
SHELL := /bin/bash

# Colors.
WHITE  = \033[38;05;15m
RED    = \033[38;05;9m
GREEN  = \033[38;05;41m
YELLOW = \033[38;05;11m
BLUE   = \033[38;05;33m
CYAN   = \033[38;05;14m
ORANGE = \033[38;05;14m

PYENV_ROOT	    = $$HOME/.pyenv
PYENV_INSTALLER	= ./bin/pyenv-installer.sh
PYTHON_VERSION	= $$(cat .python-version)

.PHONY: help
help: ## Show this message.

	@echo "usage: make [task]" \
	&& echo "available tasks:" \
	&& awk \
		'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / \
		{printf "$(CYAN)%-8s$(WHITE) : %s\n", $$1, $$2}' $(MAKEFILE_LIST)

