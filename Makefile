.PHONY: setup run verify observatory clean analytics research

PYTHON = .venv/bin/python3

# Setup Python environment
setup:
	uv venv .venv
	uv pip install google-generativeai python-dotenv numpy matplotlib
	cd tools/observatory && npm install

# Run simulation only
run:
	$(PYTHON) main.py

# Run quick verification
verify:
	$(PYTHON) verify_simulation.py

# 🌌 Run backend + frontend with live updates
observatory:
	@echo "🌌 Ananke Observatory - Live Mode"
	@echo "================================="
	@echo ""
	@echo "Starting simulation in background..."
	@$(PYTHON) main.py &
	@sleep 1
	@echo "Starting Observatory at http://localhost:5173"
	@echo ""
	@echo "Press Ctrl+C to stop"
	@cd tools/observatory && npm run dev

# 📊 Generate analytics from research data
analytics:
	@echo "📊 Generating research analytics..."
	$(PYTHON) -m tools.analytics

# 🔬 Run simulation with specific seed for reproducibility
research:
	@echo "🔬 Running reproducible research simulation..."
	@echo "Set RANDOM_SEED in config.py for reproducible runs"
	$(PYTHON) main.py

# Clean generated files
clean:
	rm -f *.log divine_ledger.jsonl simulation_telemetry.jsonl
	rm -f tools/observatory/public/divine_ledger.jsonl
	rm -rf research_data/
	rm -f analytics_report.png
