"""
Ananke Research Analytics Tool

Generates publication-quality visualizations and statistical analysis
from simulation research data.

Usage:
    python -m tools.analytics [research_data_dir]
"""

import json
import csv
import os
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any, Optional
import statistics

# Optional: matplotlib for visualizations
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib not installed. Install with: pip install matplotlib")

# Optional: numpy for statistics  
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


def load_research_data(data_dir: str = "research_data") -> Dict[str, Any]:
    """Load all research data files from the output directory."""
    data = {
        "population": [],
        "agents": [],
        "generations": [],
        "correlations": {},
        "summary": {},
        "demon_events": []
    }
    
    if not os.path.exists(data_dir):
        print(f"Research data directory not found: {data_dir}")
        return data
    
    # Find the most recent simulation files
    files = list(Path(data_dir).glob("*_summary.json"))
    if not files:
        print("No simulation data found. Run a simulation first.")
        return data
    
    # Get the most recent by timestamp in filename
    latest = sorted(files, key=lambda x: x.stem)[-1]
    prefix = str(latest).replace("_summary.json", "")
    
    print(f"Loading data from: {prefix}")
    
    # Load each data file
    try:
        with open(f"{prefix}_summary.json") as f:
            data["summary"] = json.load(f)
    except FileNotFoundError:
        pass
        
    try:
        with open(f"{prefix}_agents.json") as f:
            data["agents"] = json.load(f)
    except FileNotFoundError:
        pass
        
    try:
        with open(f"{prefix}_correlations.json") as f:
            data["correlations"] = json.load(f)
    except FileNotFoundError:
        pass
    
    try:
        with open(f"{prefix}_population.csv") as f:
            reader = csv.DictReader(f)
            data["population"] = list(reader)
    except FileNotFoundError:
        pass
        
    try:
        with open(f"{prefix}_generations.csv") as f:
            reader = csv.DictReader(f)
            data["generations"] = list(reader)
    except FileNotFoundError:
        pass
    
    try:
        with open(f"{prefix}_demon_influence.csv") as f:
            reader = csv.DictReader(f)
            data["demon_events"] = list(reader)
    except FileNotFoundError:
        pass
    
    return data


def print_summary(data: Dict[str, Any]):
    """Print a text summary of the simulation."""
    summary = data.get("summary", {})
    
    print("\n" + "=" * 60)
    print("ANANKE SIMULATION SUMMARY")
    print("=" * 60)
    
    print(f"\nReproducibility Seed: {summary.get('simulation_seed', 'Unknown')}")
    print(f"Duration: {summary.get('duration_seconds', 0):.1f} seconds")
    print(f"Total Ticks: {summary.get('total_ticks', 0)}")
    
    print(f"\n📊 Population Statistics:")
    print(f"  • Total Births: {summary.get('total_births', 0)}")
    print(f"  • Total Deaths: {summary.get('total_deaths', 0)}")
    print(f"  • Final Population: {summary.get('final_population', 0)}")
    print(f"  • Peak Population: {summary.get('peak_population', 0)}")
    print(f"  • Max Generation: {summary.get('max_generation_reached', 0)}")
    
    print(f"\n🧬 Genetic Analysis:")
    print(f"  • Avg Genetic Diversity: {summary.get('avg_genetic_diversity', 0):.3f}")
    
    correlations = summary.get("trait_fitness_correlations", {})
    if correlations:
        print(f"\n📈 Evolutionary Pressure (Trait-Fitness Correlations):")
        sorted_corr = sorted(correlations.items(), key=lambda x: -abs(x[1]))
        for trait, corr in sorted_corr[:5]:
            direction = "🔺 POSITIVE" if corr > 0.1 else "🔻 NEGATIVE" if corr < -0.1 else "⚪ NEUTRAL"
            print(f"  • {trait}: {corr:+.3f} {direction}")
            
        print(f"\n  Strongest positive selection: {summary.get('strongest_positive_trait', 'None')}")
        print(f"  Strongest negative selection: {summary.get('strongest_negative_trait', 'None')}")


def analyze_generations(data: Dict[str, Any]):
    """Analyze generational trends."""
    generations = data.get("generations", [])
    
    if not generations:
        print("\nNo generation data available.")
        return
    
    print(f"\n🧬 Generational Analysis ({len(generations)} generations):")
    print("-" * 50)
    
    for gen in generations[:10]:  # Show first 10 generations
        print(f"  Gen {gen.get('generation', '?')}: "
              f"n={gen.get('population_count', 0)}, "
              f"lifespan={float(gen.get('avg_lifespan', 0)):.1f}, "
              f"fitness={float(gen.get('avg_fitness', 0)):.2f}, "
              f"survival={float(gen.get('survival_rate', 0))*100:.0f}%")


def analyze_demon_influence(data: Dict[str, Any]):
    """Analyze demon influence patterns."""
    events = data.get("demon_events", [])
    agents = data.get("agents", [])
    
    if not events and not agents:
        print("\nNo demon influence data available.")
        return
    
    # Calculate from agent records
    total_whispers = sum(a.get("lifetime_stats", {}).get("demon_whispers_received", 0) for a in agents)
    total_followed = sum(a.get("lifetime_stats", {}).get("demon_whispers_followed", 0) for a in agents)
    
    print(f"\n😈 Demon Influence Analysis:")
    print("-" * 50)
    print(f"  Total whispers: {total_whispers}")
    print(f"  Total followed: {total_followed}")
    if total_whispers > 0:
        print(f"  Follow rate: {total_followed/total_whispers*100:.1f}%")
    
    # Analyze if following demon leads to worse outcomes
    if agents:
        followed_deaths = []
        resisted_deaths = []
        
        for agent in agents:
            stats = agent.get("lifetime_stats", {})
            if stats.get("demon_whispers_received", 0) > 0:
                follow_rate = stats.get("demon_whispers_followed", 0) / stats.get("demon_whispers_received", 1)
                fitness = agent.get("fitness_score", 0)
                
                if follow_rate > 0.5:
                    followed_deaths.append(fitness)
                else:
                    resisted_deaths.append(fitness)
        
        if followed_deaths and resisted_deaths:
            avg_followed = statistics.mean(followed_deaths)
            avg_resisted = statistics.mean(resisted_deaths)
            print(f"\n  Avg fitness (high demon follow): {avg_followed:.2f}")
            print(f"  Avg fitness (low demon follow): {avg_resisted:.2f}")
            
            if avg_resisted > avg_followed:
                print("  → Resisting demon whispers correlates with higher fitness!")
            else:
                print("  → Following demon whispers may not harm fitness")


def plot_visualizations(data: Dict[str, Any], output_file: str = "analytics_report.png"):
    """Generate matplotlib visualizations."""
    if not HAS_MATPLOTLIB:
        print("\nSkipping visualizations (matplotlib not installed)")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Ananke Simulation Analysis", fontsize=14, fontweight='bold')
    
    # 1. Population over time
    ax1 = axes[0, 0]
    population = data.get("population", [])
    if population:
        ticks = [int(p.get("tick", 0)) for p in population]
        pop_sizes = [int(p.get("population_size", 0)) for p in population]
        ax1.plot(ticks, pop_sizes, 'b-', linewidth=2)
        ax1.fill_between(ticks, pop_sizes, alpha=0.3)
        ax1.set_xlabel("Tick")
        ax1.set_ylabel("Population Size")
        ax1.set_title("Population Dynamics")
        ax1.grid(True, alpha=0.3)
    else:
        ax1.text(0.5, 0.5, "No population data", ha='center', va='center')
    
    # 2. Trait-Fitness Correlations
    ax2 = axes[0, 1]
    correlations = data.get("correlations", {}).get("trait_fitness_correlations", {})
    if correlations:
        traits = list(correlations.keys())
        values = list(correlations.values())
        colors = ['green' if v > 0 else 'red' for v in values]
        
        y_pos = range(len(traits))
        ax2.barh(y_pos, values, color=colors, alpha=0.7)
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(traits, fontsize=8)
        ax2.axvline(x=0, color='black', linewidth=0.5)
        ax2.set_xlabel("Correlation with Fitness")
        ax2.set_title("Evolutionary Selection Pressure")
        ax2.grid(True, alpha=0.3, axis='x')
    else:
        ax2.text(0.5, 0.5, "No correlation data", ha='center', va='center')
    
    # 3. Fitness by Generation
    ax3 = axes[1, 0]
    generations = data.get("generations", [])
    if generations:
        gens = [int(g.get("generation", 0)) for g in generations]
        fitness = [float(g.get("avg_fitness", 0)) for g in generations]
        survival = [float(g.get("survival_rate", 0)) * 100 for g in generations]
        
        ax3.plot(gens, fitness, 'g-o', label="Avg Fitness", markersize=4)
        ax3_twin = ax3.twinx()
        ax3_twin.plot(gens, survival, 'b--s', label="Survival Rate %", markersize=4, alpha=0.7)
        
        ax3.set_xlabel("Generation")
        ax3.set_ylabel("Fitness Score", color='green')
        ax3_twin.set_ylabel("Survival Rate %", color='blue')
        ax3.set_title("Fitness & Survival by Generation")
        ax3.legend(loc='upper left')
        ax3_twin.legend(loc='upper right')
        ax3.grid(True, alpha=0.3)
    else:
        ax3.text(0.5, 0.5, "No generation data", ha='center', va='center')
    
    # 4. Genetic Diversity over time
    ax4 = axes[1, 1]
    if population:
        diversity = [float(p.get("genetic_diversity", 0)) for p in population]
        ax4.plot(ticks, diversity, 'purple', linewidth=2)
        ax4.fill_between(ticks, diversity, alpha=0.3, color='purple')
        ax4.set_xlabel("Tick")
        ax4.set_ylabel("Genetic Diversity")
        ax4.set_title("Genetic Diversity Over Time")
        ax4.grid(True, alpha=0.3)
    else:
        ax4.text(0.5, 0.5, "No diversity data", ha='center', va='center')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n📊 Visualization saved to: {output_file}")
    plt.close()


def main():
    """Main entry point for analytics."""
    # Get data directory from args or use default
    data_dir = sys.argv[1] if len(sys.argv) > 1 else "research_data"
    
    print("🔬 Ananke Research Analytics")
    print("=" * 60)
    
    # Load data
    data = load_research_data(data_dir)
    
    if not data.get("summary") and not data.get("agents"):
        print("\nNo research data found. Run a simulation first:")
        print("  make run")
        return
    
    # Print summary
    print_summary(data)
    
    # Analyze generations
    analyze_generations(data)
    
    # Analyze demon influence
    analyze_demon_influence(data)
    
    # Generate visualizations
    plot_visualizations(data)
    
    print("\n" + "=" * 60)
    print("Analysis complete!")
    

if __name__ == "__main__":
    main()

    scatter = ax2.scatter(risk_tolerances, lifespans, c=colors, cmap='viridis', alpha=0.7)
    ax2.set_title("Genome Trait: Risk Tolerance vs Lifespan")
    ax2.set_xlabel("Risk Tolerance (0.0 - 1.0)")
    ax2.set_ylabel("Lifespan (Events)")
    plt.colorbar(scatter, ax=ax2, label='Food Consumed')
    ax2.grid(True)
    
    plt.tight_layout()
    output_image = "analytics_report.png"
    plt.savefig(output_image)
    print(f"Saved analysis to {output_image}")

if __name__ == "__main__":
    main()
