"""
Research Metrics Collection System

Collects and exports comprehensive data for evolutionary and behavioral analysis.
Designed for academic research workflows.
"""

import json
import csv
import os
import logging
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


@dataclass
class GenerationStats:
    """Statistics for a single generation."""
    generation: int
    population_count: int = 0
    avg_lifespan: float = 0.0
    avg_fitness: float = 0.0
    avg_children: float = 0.0
    
    # Trait averages
    trait_means: Dict[str, float] = field(default_factory=dict)
    trait_stddevs: Dict[str, float] = field(default_factory=dict)
    
    # Survival analysis
    survival_rate: float = 0.0  # % that survived to reproduce
    causes_of_death: Dict[str, int] = field(default_factory=dict)
    
    # Demon influence
    demon_whisper_follow_rate: float = 0.0


@dataclass 
class PopulationSnapshot:
    """Snapshot of population state at a specific tick."""
    tick: int
    timestamp: float
    population_size: int
    total_births: int
    total_deaths: int
    avg_energy: float
    avg_age: float
    max_generation: int
    genetic_diversity: float  # Avg genetic distance between agents


class ResearchMetrics:
    """
    Comprehensive research metrics collector.
    
    Tracks:
    - Population dynamics over time
    - Generational statistics
    - Trait-fitness correlations
    - Demon influence outcomes
    - Evolutionary pressure indicators
    """
    
    def __init__(self, output_dir: str = "research_data"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Time series data
        self.population_snapshots: List[PopulationSnapshot] = []
        
        # Generational tracking
        self.generation_stats: Dict[int, GenerationStats] = {}
        
        # Individual agent records (for detailed analysis)
        self.agent_records: Dict[str, Dict[str, Any]] = {}
        
        # Demon influence tracking
        self.demon_events: List[Dict[str, Any]] = []
        
        # Counters
        self.total_births = 0
        self.total_deaths = 0
        self.simulation_seed: Optional[int] = None
        self.start_time = time.time()
        
    def set_seed(self, seed: int):
        """Record the random seed for reproducibility."""
        self.simulation_seed = seed
        
    def record_birth(self, agent: Any, parent_ids: List[str] = None):
        """Record an agent birth for research tracking."""
        self.total_births += 1
        
        self.agent_records[agent.id] = {
            "id": agent.id,
            "birth_tick": agent.age_ticks,
            "generation": agent.lineage.generation,
            "parent_ids": parent_ids or [],
            "genome": agent.genome.to_dict(),
            "agent_type": agent.agent_type,
            "birth_time": time.time(),
        }
        
    def record_death(self, agent: Any, cause: str):
        """Record an agent death with full statistics."""
        self.total_deaths += 1
        
        if agent.id in self.agent_records:
            record = self.agent_records[agent.id]
            record.update({
                "death_tick": agent.age_ticks,
                "lifespan": agent.age_ticks,
                "cause_of_death": cause,
                "fitness_score": agent.get_fitness_score(),
                "lifetime_stats": agent.lifetime_stats.copy(),
                "death_time": time.time(),
            })
            
    def record_demon_whisper(self, agent_id: str, whisper_type: str, 
                             suggestion: str, action_taken: str, 
                             was_followed: bool):
        """Track demon influence events for analysis."""
        self.demon_events.append({
            "timestamp": time.time(),
            "agent_id": agent_id,
            "whisper_type": whisper_type,
            "suggestion": suggestion,
            "action_taken": action_taken,
            "was_followed": was_followed,
        })
        
    def record_population_snapshot(self, tick: int, agents: List[Any]):
        """Take a snapshot of the current population state."""
        if not agents:
            snapshot = PopulationSnapshot(
                tick=tick,
                timestamp=time.time(),
                population_size=0,
                total_births=self.total_births,
                total_deaths=self.total_deaths,
                avg_energy=0,
                avg_age=0,
                max_generation=0,
                genetic_diversity=0,
            )
        else:
            living_agents = [a for a in agents if a.is_alive]
            
            # Calculate genetic diversity (avg pairwise distance)
            diversity = 0.0
            if len(living_agents) > 1:
                distances = []
                for i, a1 in enumerate(living_agents[:10]):  # Sample for efficiency
                    for a2 in living_agents[i+1:10]:
                        distances.append(a1.genome.genetic_distance(a2.genome))
                if distances:
                    diversity = statistics.mean(distances)
            
            snapshot = PopulationSnapshot(
                tick=tick,
                timestamp=time.time(),
                population_size=len(living_agents),
                total_births=self.total_births,
                total_deaths=self.total_deaths,
                avg_energy=statistics.mean([a.drives.energy for a in living_agents]) if living_agents else 0,
                avg_age=statistics.mean([a.age_ticks for a in living_agents]) if living_agents else 0,
                max_generation=max([a.lineage.generation for a in living_agents]) if living_agents else 0,
                genetic_diversity=diversity,
            )
        
        self.population_snapshots.append(snapshot)
        
    def compute_generation_stats(self) -> Dict[int, GenerationStats]:
        """Compute statistics for each generation from agent records."""
        gen_agents: Dict[int, List[Dict]] = defaultdict(list)
        
        for record in self.agent_records.values():
            gen = record.get("generation", 0)
            gen_agents[gen].append(record)
        
        for gen, agents in gen_agents.items():
            # Filter to agents with complete records (died or still alive long enough)
            complete_agents = [a for a in agents if "lifespan" in a or a.get("lifetime_stats")]
            
            if not complete_agents:
                continue
                
            # Compute trait statistics
            trait_values: Dict[str, List[float]] = defaultdict(list)
            for agent in complete_agents:
                genome = agent.get("genome", {})
                for trait, value in genome.items():
                    trait_values[trait].append(value)
            
            trait_means = {t: statistics.mean(v) for t, v in trait_values.items() if v}
            trait_stddevs = {t: statistics.stdev(v) if len(v) > 1 else 0 for t, v in trait_values.items() if v}
            
            # Compute survival stats
            lifespans = [a.get("lifespan", 0) for a in complete_agents if "lifespan" in a]
            fitness_scores = [a.get("fitness_score", 0) for a in complete_agents if "fitness_score" in a]
            children_counts = [a.get("lifetime_stats", {}).get("children_produced", 0) for a in complete_agents]
            
            # Causes of death
            causes = defaultdict(int)
            for agent in complete_agents:
                cause = agent.get("cause_of_death")
                if cause:
                    causes[cause] += 1
            
            # Survival rate (reproduced before death)
            reproduced = sum(1 for a in complete_agents if a.get("lifetime_stats", {}).get("children_produced", 0) > 0)
            survival_rate = reproduced / len(complete_agents) if complete_agents else 0
            
            # Demon influence
            demon_followed = sum(a.get("lifetime_stats", {}).get("demon_whispers_followed", 0) for a in complete_agents)
            demon_received = sum(a.get("lifetime_stats", {}).get("demon_whispers_received", 0) for a in complete_agents)
            demon_rate = demon_followed / demon_received if demon_received > 0 else 0
            
            self.generation_stats[gen] = GenerationStats(
                generation=gen,
                population_count=len(agents),
                avg_lifespan=statistics.mean(lifespans) if lifespans else 0,
                avg_fitness=statistics.mean(fitness_scores) if fitness_scores else 0,
                avg_children=statistics.mean(children_counts) if children_counts else 0,
                trait_means=trait_means,
                trait_stddevs=trait_stddevs,
                survival_rate=survival_rate,
                causes_of_death=dict(causes),
                demon_whisper_follow_rate=demon_rate,
            )
        
        return self.generation_stats
    
    def get_trait_fitness_correlation(self) -> Dict[str, float]:
        """
        Compute correlation between each trait and fitness score.
        Returns dict of trait -> correlation coefficient.
        """
        correlations = {}
        
        # Gather data
        trait_data: Dict[str, List[float]] = defaultdict(list)
        fitness_data: List[float] = []
        
        for record in self.agent_records.values():
            if "fitness_score" not in record:
                continue
            genome = record.get("genome", {})
            fitness = record["fitness_score"]
            
            fitness_data.append(fitness)
            for trait, value in genome.items():
                trait_data[trait].append(value)
        
        # Compute correlations
        if len(fitness_data) > 2:
            for trait, values in trait_data.items():
                if len(values) == len(fitness_data):
                    try:
                        corr = self._pearson_correlation(values, fitness_data)
                        correlations[trait] = corr
                    except:
                        correlations[trait] = 0.0
        
        return correlations
    
    def _pearson_correlation(self, x: List[float], y: List[float]) -> float:
        """Compute Pearson correlation coefficient."""
        n = len(x)
        if n < 2:
            return 0.0
        
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        
        numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
        
        var_x = sum((xi - mean_x) ** 2 for xi in x)
        var_y = sum((yi - mean_y) ** 2 for yi in y)
        
        denominator = (var_x * var_y) ** 0.5
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def export_all(self, filename_prefix: str = "simulation"):
        """Export all research data to files."""
        timestamp = int(time.time())
        prefix = f"{self.output_dir}/{filename_prefix}_{timestamp}"
        
        # Compute final statistics
        self.compute_generation_stats()
        correlations = self.get_trait_fitness_correlation()
        
        # 1. Export population time series (CSV)
        self._export_population_csv(f"{prefix}_population.csv")
        
        # 2. Export agent records (JSON)
        self._export_agents_json(f"{prefix}_agents.json")
        
        # 3. Export generation statistics (CSV)
        self._export_generations_csv(f"{prefix}_generations.csv")
        
        # 4. Export trait-fitness correlations (JSON)
        self._export_correlations_json(f"{prefix}_correlations.json", correlations)
        
        # 5. Export demon influence data (CSV)
        self._export_demon_csv(f"{prefix}_demon_influence.csv")
        
        # 6. Export summary report (JSON)
        self._export_summary_json(f"{prefix}_summary.json", correlations)
        
        logger.info(f"Research data exported to {self.output_dir}/")
        
    def _export_population_csv(self, filepath: str):
        """Export population snapshots to CSV."""
        if not self.population_snapshots:
            return
            
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "tick", "timestamp", "population_size", "total_births", 
                "total_deaths", "avg_energy", "avg_age", "max_generation", 
                "genetic_diversity"
            ])
            for snap in self.population_snapshots:
                writer.writerow([
                    snap.tick, snap.timestamp, snap.population_size,
                    snap.total_births, snap.total_deaths, snap.avg_energy,
                    snap.avg_age, snap.max_generation, snap.genetic_diversity
                ])
        logger.info(f"Exported population data to {filepath}")
        
    def _export_agents_json(self, filepath: str):
        """Export all agent records to JSON."""
        with open(filepath, 'w') as f:
            json.dump(list(self.agent_records.values()), f, indent=2)
        logger.info(f"Exported {len(self.agent_records)} agent records to {filepath}")
        
    def _export_generations_csv(self, filepath: str):
        """Export generation statistics to CSV."""
        if not self.generation_stats:
            return
            
        # Get all trait names
        trait_names = set()
        for stats in self.generation_stats.values():
            trait_names.update(stats.trait_means.keys())
        trait_names = sorted(trait_names)
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            header = [
                "generation", "population_count", "avg_lifespan", "avg_fitness",
                "avg_children", "survival_rate", "demon_follow_rate"
            ]
            header.extend([f"trait_mean_{t}" for t in trait_names])
            header.extend([f"trait_std_{t}" for t in trait_names])
            writer.writerow(header)
            
            # Data rows
            for gen in sorted(self.generation_stats.keys()):
                stats = self.generation_stats[gen]
                row = [
                    stats.generation, stats.population_count, stats.avg_lifespan,
                    stats.avg_fitness, stats.avg_children, stats.survival_rate,
                    stats.demon_whisper_follow_rate
                ]
                row.extend([stats.trait_means.get(t, 0) for t in trait_names])
                row.extend([stats.trait_stddevs.get(t, 0) for t in trait_names])
                writer.writerow(row)
                
        logger.info(f"Exported generation statistics to {filepath}")
        
    def _export_correlations_json(self, filepath: str, correlations: Dict[str, float]):
        """Export trait-fitness correlations."""
        # Sort by absolute correlation strength
        sorted_corr = dict(sorted(
            correlations.items(), 
            key=lambda x: abs(x[1]), 
            reverse=True
        ))
        
        with open(filepath, 'w') as f:
            json.dump({
                "trait_fitness_correlations": sorted_corr,
                "interpretation": {
                    trait: "positive selection pressure" if corr > 0.1 
                           else "negative selection pressure" if corr < -0.1 
                           else "neutral"
                    for trait, corr in sorted_corr.items()
                }
            }, f, indent=2)
        logger.info(f"Exported correlations to {filepath}")
        
    def _export_demon_csv(self, filepath: str):
        """Export demon influence events."""
        if not self.demon_events:
            return
            
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "agent_id", "whisper_type", 
                "suggestion", "action_taken", "was_followed"
            ])
            for event in self.demon_events:
                writer.writerow([
                    event["timestamp"], event["agent_id"], event["whisper_type"],
                    event["suggestion"], event["action_taken"], event["was_followed"]
                ])
        logger.info(f"Exported {len(self.demon_events)} demon events to {filepath}")
        
    def _export_summary_json(self, filepath: str, correlations: Dict[str, float]):
        """Export high-level simulation summary."""
        summary = {
            "simulation_seed": self.simulation_seed,
            "duration_seconds": time.time() - self.start_time,
            "total_ticks": len(self.population_snapshots),
            "total_births": self.total_births,
            "total_deaths": self.total_deaths,
            "max_generation_reached": max(self.generation_stats.keys()) if self.generation_stats else 0,
            "final_population": self.population_snapshots[-1].population_size if self.population_snapshots else 0,
            "peak_population": max(s.population_size for s in self.population_snapshots) if self.population_snapshots else 0,
            "avg_genetic_diversity": statistics.mean([s.genetic_diversity for s in self.population_snapshots]) if self.population_snapshots else 0,
            "strongest_positive_trait": max(correlations.items(), key=lambda x: x[1])[0] if correlations else None,
            "strongest_negative_trait": min(correlations.items(), key=lambda x: x[1])[0] if correlations else None,
            "trait_fitness_correlations": correlations,
        }
        
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Exported simulation summary to {filepath}")
