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

.PHONY: init
init: python ## Init workspace.

.PHONY: install-pyenv
install-pyenv: # Install pyenv.

	@which pyenv \
	|| ( \
		echo -e "$(YELLOW)--- Installing pyenv ---$(WHITE)" \
		&& sudo apt-get install -y \
			libssl-dev \
			zlib1g-dev \
			libbz2-dev \
			libreadline-dev \
			libsqlite3-dev \
			wget \
			curl \
			llvm \
			libncurses5-dev \
			libncursesw5-dev \
			xz-utils \
			tk-dev \
		&& PYENV_ROOT=$(PYENV_ROOT) bash $(PYENV_INSTALLER) \
		&& echo "export PATH='$$HOME/.pyenv/bin:$$PATH'" >> $$HOME/.bashrc \
		&& echo 'eval "$(pyenv init -)"' >> $$HOME/.bashrc \
		&& echo 'eval "$(pyenv virtualenv-init -)"' >> $$HOME/.bashrc \
		&& source $$HOME/.bashrc \
		&& echo -e "$(GREEN)--- pyenv installed ---$(WHITE)" \
	)

.PHONY: update-pyenv
update-pyenv: install-pyenv # Update pyenv to get latest versions.

	@echo -e "$(YELLOW)--- Updating Pyenv ---$(WHITE)" \
	&& cd $(PYENV_ROOT) && git pull && cd - \
	&& echo -e "$(GREEN)--- pyenv updated ---$(WHITE)"

.PHONY: python
python: update-pyenv # Install python(from .python-version).

	@echo -e "$(YELLOW)--- Installing python $(PYTHON_VERSION) ---$(WHITE)" \
	&& pyenv install -s "$(PYTHON_VERSION)" \
	&& echo -e "$(GREEN)--- python $(PYTHON_VERSION) installed ---$(WHITE)"

