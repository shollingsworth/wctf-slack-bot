# comlex Makefile example here: https://github.com/ansible/ansible/blob/devel/Makefile

.DEFAULT_GOAL := default
PYTHON=python2
NAME=wctf-bot
VERSION=$(shell cat VERSION)
GIT_BRANCH=$(shell git rev-parse --abbrev-ref HEAD | sed 's/\//_/g')
MYID=$(shell id -u)
ifeq ($(MYID),0)
	SUDO=
else
	SUDO=sudo
endif

.PHONY: default
default: python

.PHONY:
python:
	@echo $(VERSION)

.PHONY: lint
lint:
	# Use https://github.com/nvie/vim-flake8 if you want to incorporate into vim
	find . -path ./venv -prune -o -name '*.py' -type f -not -name '__init__.py' -print | xargs flake8 --isolated --ignore E501,E251,E203,E221
	# ignore non-used includes in __init__.py files
	find . -path ./venv -prune -o -name '*.py' -type f -name '__init__.py' -print | xargs flake8 --isolated --ignore E501,E251,E203,E221,F401
