# Generated-by: Cursor (claude-4-sonnet)
# MCP Server Development Targets
# ==============================

VENV_CURSOR_DIR ?= .venv-cursor

.PHONY: venv-cursor install-cursor

venv-cursor: ## Create dedicated virtual environment for Cursor MCP integration
	@if [ ! -d "$(VENV_CURSOR_DIR)" ]; then \
		$(PYTHON) -m venv $(VENV_CURSOR_DIR); \
		$(VENV_CURSOR_DIR)/bin/pip install -r requirements.txt; \
		printf "$(GREEN)✅ Cursor MCP virtual environment created$(RESET)\n"; \
	fi

install-cursor: venv-cursor ## Install MCP server for Cursor integration
	@$(VENV_CURSOR_DIR)/bin/pip install -e .
	@if [ -f "scripts/update_cursor_config.py" ]; then \
		$(VENV_CURSOR_DIR)/bin/python scripts/update_cursor_config.py "$$(pwd)/$(VENV_CURSOR_DIR)/bin/python" "$$(realpath .)"; \
		printf "$(GREEN)✅ Cursor MCP integration configured$(RESET)\n"; \
		printf "\n$(YELLOW)Next steps:$(RESET)\n"; \
		printf "  1. Restart Cursor to load the new MCP server\n"; \
		printf "  2. Open a new chat session (⌘+L on Mac, Ctrl+L on Linux)\n"; \
		printf "  3. Test your MCP server\n"; \
	else \
		printf "$(YELLOW)⚠️  MCP configuration script not found.$(RESET)\n"; \
		printf "   Create scripts/update_cursor_config.py to enable automatic Cursor configuration\n"; \
	fi

clean-cursor: ## Clean MCP-specific artifacts including Cursor venv
	@rm -rf $(VENV_CURSOR_DIR) 2>/dev/null || true
	@printf "$(GREEN)✅ MCP cleanup completed$(RESET)\n"