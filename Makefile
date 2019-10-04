# Kyo Makefile
# ------------
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
ORANGE = \033[38;05;202m

# Project.
PROJECT_NAME    ?= $$(git rev-parse --show-toplevel | xargs basename)
BRANCH_NAME     ?= $$(git rev-parse --abbrev-ref HEAD)
PYTHON_VERSION  ?= $$(cat .python-version)

# Helpers.
PYENV_ROOT      ?= $$HOME/.pyenv
PYENV_INSTALLER ?= ./bin/pyenv-installer.sh

VIRTUALENV_NAME ?= $(PROJECT_NAME)-$(BRANCH_NAME)
VIRTUALENV_DIR  ?= $(PYENV_ROOT)/versions/$(PYTHON_VERSION)/envs/$(VIRTUALENV_NAME)
VIRTUALENV_BIN  ?= $(VIRTUALENV_DIR)/bin
PIP             ?= $(VIRTUALENV_BIN)/pip
REQUIREMENTS    ?= ./requirements.txt

TO_CLEAN        ?= *.pyc *.orig


.PHONY: help
help: max-length ## Show this message.

	@echo -e "Usage: make [task]\n" \
	&& echo "Available tasks:" \
	&& awk ' \
			BEGIN {FS = ":.*?## "} \
			/^[a-zA-Z_-]+:.*?## / \
			{printf "$(CYAN)%-$(MAX_LENGTH)s$(WHITE) : %s\n", $$1, $$2} \
	   ' $(MAKEFILE_LIST)

.PHONY: init
init: python requirements direnv ## Init workspace.

	@echo \
	&& echo -ne "$(ORANGE)Please reload your bash environement $(WHITE)" \
	&& echo -e "$(ORANGE)for the modifications to take effects.$(WHITE)" \
	&& echo "e.g: source ~/.bashrc"

.PHONY: clean
clean: ## Remove all .pyc,.orig,etc..

	@echo -n $(TO_CLEAN) | xargs -d ' ' -I_ find . -type f -name _ -delete

.PHONY: install-pyenv
install-pyenv: # Install pyenv.

	@which pyenv &> /dev/null \
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
		&& echo "export PATH='\$$HOME/.pyenv/bin:\$$PATH'" >> $$HOME/.bashrc \
		&& echo 'eval "$$(pyenv init -)"' >> $$HOME/.bashrc \
		&& echo 'eval "$$(pyenv virtualenv-init -)"' >> $$HOME/.bashrc \
	) && echo -e "$(GREEN)--- pyenv installed ---$(WHITE)"

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

.PHONY: venv
venv: python # Create a virtualenv in the current python version.

	@[ ! -d "$(VIRTUALENV_DIR)" ] \
	&& ( \
		echo -e "$(YELLOW)--- Creating virtualenv $(VIRTUALENV_NAME) ---$(WHITE)" \
		&& pyenv virtualenv "$(PYTHON_VERSION)" "$(VIRTUALENV_NAME)" \
		&& echo -e "$(GREEN)--- python $(PYTHON_VERSION) installed ---$(WHITE)" \
	) ||:

.PHONY: requirements
requirements: venv ## Install (or update) requirements.

	@echo -e "$(YELLOW)--- Installing requirements ---$(WHITE)" \
	&& $(PIP) install --upgrade pip \
	&& $(PIP) install --upgrade --requirement $(REQUIREMENTS) \
	&& echo -e "$(GREEN)--- requirements installed ---$(WHITE)"

.PHONY: max-length
max-length: # Return the length of the longest explosed(commented with ##) rule name.

	@$(eval MAX_LENGTH := $(shell \
		awk ' \
			BEGIN {FS = ":.*?## "} \
			/^[a-zA-Z_-]+:.*?## / \
			{print length($$1)} \
		' $(MAKEFILE_LIST) \
		| awk -v max=0 '{if($$1>max){max=$$1}}END{print max}' \
	))

.PHONY: direnv
direnv: # Install direnv

	@which direnv &> /dev/null \
	|| ( \
		echo -e "$(YELLOW)--- Installing direnv ---$(WHITE)" \
		&& sudo apt install -y direnv \
		&& echo 'eval "$$(direnv hook bash)"' >> $$HOME/.bashrc \
		&& direnv allow $$PWD \
	) && echo -e "$(GREEN)--- direnv installed ---$(WHITE)"
