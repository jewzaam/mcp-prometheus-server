# Generated-by: Cursor (claude-4-sonnet)
# Common Variables and Constants
# ==============================

# Python virtual environment
VENV_DIR ?= .venv
PYTHON := python3
VENV_PYTHON := $(VENV_DIR)/bin/python
VENV_PIP := $(VENV_DIR)/bin/pip
VENV_UV := $(VENV_DIR)/bin/uv

# Coverage settings
COVERAGE_THRESHOLD ?= 90

# Colors for output
BLUE := \033[34m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m