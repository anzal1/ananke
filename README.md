# 🌌 Ananke

**A Research-Grade Artificial Life Simulation**

Ananke is an autonomous artificial life system where AI-driven agents navigate a resource-scarce world, make decisions via LLM cognition, evolve through reproduction, and compete for survival. Watch life emerge from simple rules.

---

## ✨ Features

- **🧠 LLM-Powered Cognition**: Each agent thinks using Google Gemini, deciding actions based on perception, memory, and internal drives.
- **🧬 Genetic Evolution**: Agents reproduce with mutation. Over generations, successful traits propagate.
- **⚡ Energy Economics**: Survival requires finding and consuming resources. Every action has a cost.
- **📊 Rich Telemetry**: Every event is logged for offline analysis and replay.
- **🌐 Web Visualizer**: A real-time dashboard to observe the simulation.

---

## 🚀 Quick Start

```bash
# 1. Clone and enter the project
cd ananke

# 2. Setup the environment
make setup

# 3. Set your API key
export GEMINI_API_KEY="your_key_here"

# 4. Run the simulation with live visualization
make start
```

Then open **http://localhost:8000** to observe!

---

## 📂 Project Structure

```
ananke/
├── agent/           # Agent internals (Brain, Genome, Drives, Memory)
├── world/           # Environment (Grid, Resources, Physics)
├── system/          # Runtime loop, Telemetry, Safety Governor
├── tools/           # Visualization & Analytics
│   ├── web_visualizer.py   # FastAPI + Canvas Dashboard
│   └── analytics.py        # Matplotlib trend analysis
├── main.py          # Entry point
├── config.py        # Tunable parameters
└── Makefile         # Commands
```

---

## 🎮 Make Commands

| Command          | Description                                    |
|------------------|------------------------------------------------|
| `make setup`     | Create venv and install all dependencies       |
| `make start`     | Run simulation + web visualizer together       |
| `make run`       | Run simulation only (terminal output)          |
| `make web`       | Run web visualizer only                        |
| `make analytics` | Generate analytics plots from telemetry logs   |
| `make clean`     | Remove logs and generated files                |

---

## 🔬 The Simulation

### Agent Loop
```
Perception → Internal State → Goal Generation → Action → Outcome → Memory Update
                                    ↓
                              Reflection & Learning
```

### World Rules
- **Grid**: 100x100 discrete cells
- **Resources**: Spawn randomly, provide energy when consumed
- **Partial Observability**: Agents only see within a perception radius

### Evolution
- Agents can **reproduce** when they have sufficient energy
- Child genomes are **mutated** copies of the parent
- **Selection pressure** emerges naturally from survival

---

## 📈 Analytics

After running a simulation, analyze the data:

```bash
make analytics
```

This generates `analytics_report.png` with:
- **Population Dynamics** over time
- **Trait vs Outcome** scatter plots (e.g., Risk Tolerance vs Lifespan)
- **Evolutionary pressure** correlations showing which traits are being selected

---

## 🔬 Research Features

Ananke is built for rigorous scientific research:

### Reproducibility
```python
# config.py
RANDOM_SEED = 42  # Set for reproducible experiments (None for random)
```

Every simulation logs its seed, so you can reproduce exact results.

### Sexual Reproduction & Crossover
Agents can mate when close enough, combining genes from two parents:
- **Uniform crossover**: Each gene randomly selected or blended from parents
- **Mutation**: Small random changes after crossover
- Controlled via `SEXUAL_REPRODUCTION`, `CROSSOVER_RATE`, `MATING_RADIUS`

### Expanded Genome
10 heritable traits that influence behavior:
| Trait | Range | Effect |
|-------|-------|--------|
| `risk_tolerance` | 0-1 | Exploration vs caution |
| `curiosity` | 0-1 | Movement patterns |
| `social_bias` | 0-1 | Interaction tendency |
| `aggression` | 0-1 | Competition behavior |
| `cooperation` | 0-1 | Resource sharing |
| `memory_retention` | 0-1 | Learning from past |
| `metabolism_efficiency` | 0.5-2.0 | Energy cost multiplier |
| `reproduction_threshold` | 0.2-0.8 | Energy % to trigger reproduction |
| `perception_acuity` | 0.5-1.5 | Vision range multiplier |
| `lifespan_factor` | 0.8-1.5 | Natural lifespan |

### Lineage Tracking
Every agent tracks:
- Generation number
- Parent IDs (1 or 2 for sexual reproduction)
- Full ancestor chain
- Lifetime statistics (energy, children, demon influence, etc.)

### Research Data Export
After each simulation, data is exported to `research_data/`:
```
research_data/
├── simulation_*_summary.json      # High-level metrics
├── simulation_*_population.csv    # Time series data
├── simulation_*_agents.json       # All agent records
├── simulation_*_generations.csv   # Per-generation statistics
├── simulation_*_correlations.json # Trait-fitness correlations
└── simulation_*_demon_influence.csv
```

### Trait-Fitness Correlations
Automatically computes Pearson correlation between each genome trait and fitness score, revealing evolutionary selection pressure.

---

## 🌐 Web Visualizer

The dashboard at `localhost:8000` provides:

| Feature           | Description                                      |
|-------------------|--------------------------------------------------|
| **Ghost Trails**  | Fading paths showing agent movement history      |
| **Energy View**   | Heatmap mode showing agent health via color      |
| **Time Controls** | Speed up (100x) or pause the replay              |
| **Agent Inspector** | Hover to see genome, energy, and lineage       |

---

## ⚙️ Configuration

Edit `config.py` to tune:

```python
# Reproducibility
RANDOM_SEED = 42  # Set to None for random

# World
WORLD_WIDTH = 100
WORLD_HEIGHT = 100

# Genetics
MUTATION_RATE = 0.1
CROSSOVER_RATE = 0.7
SEXUAL_REPRODUCTION = True

# Cognition
LLM_MODEL_NAME = "gemini-2.5-pro"
```

---

## 🔑 Environment Variables

| Variable         | Required | Description                     |
|------------------|----------|---------------------------------|
| `GEMINI_API_KEY` | Yes      | Your Google AI API key          |

Create a `.env` file in the project root:
```
GEMINI_API_KEY=your_api_key_here
```

**Note**: Without an API key, agents use a smart fallback behavior that still demonstrates evolution.
---

## 🛡️ Safety

- **Governor**: Enforces population caps and simulation timeouts
- **Read-Only Telemetry**: Observer cannot influence the simulation
- **Kill Switch**: Governor can terminate runaway simulations

---

## 📜 License

MIT

---

<p align="center">
  <i>"Life finds a way."</i>
</p>
