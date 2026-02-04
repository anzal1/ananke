import asyncio
import logging
import sys
from config import (
    SIMULATION_TIMEOUT_TICKS, INITIAL_RESOURCE_COUNT, TICK_DURATION_SEC,
    RANDOM_SEED, initialize_seed
)
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Initialize random seed FIRST for reproducibility
actual_seed = initialize_seed(RANDOM_SEED)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("ananke.log")
    ]
)

logger = logging.getLogger("MAIN")

from system.runtime import Runtime
from system.governor import Governor


async def main():
    logger.info("=" * 60)
    logger.info("ANANKE - Theological Ontology Simulation")
    logger.info("=" * 60)
    logger.info(f"Random Seed: {actual_seed} (save this for reproducibility)")
    logger.info("")
    logger.info("Initializing cosmology...")
    
    # 1. Initialize Runtime (includes Angel subsystems and Demon)
    runtime = Runtime(seed=actual_seed)
    governor = Governor(runtime)
    
    # 2. Initial Provision (via Provisioner angel)
    runtime.provisioner.provision_initial(INITIAL_RESOURCE_COUNT)
    logger.info(f"Provisioner: {INITIAL_RESOURCE_COUNT} resources created")
    
    # 3. Genesis - Create Adam and Eve (the origin ancestors)
    runtime.spawn_origin_agents()
    logger.info(f"Genesis complete: {len(runtime.agents)} origin agents created")
    
    logger.info("")
    logger.info("Simulation begins...")
    logger.info("=" * 60)
    
    # 4. Main Loop
    try:
        while True:
            # Check Governor bounds
            if not governor.check_bounds():
                logger.info("Governor stopped simulation - bounds met.")
                break
                
            # Step
            await runtime.step()
            
            # Real-time pacing
            await asyncio.sleep(TICK_DURATION_SEC)
            
    except Exception as e:
        logger.error(f"Simulation crashed: {e}", exc_info=True)
    finally:
        # Export research data
        logger.info("=" * 60)
        logger.info("Exporting research data...")
        runtime.export_research_data(f"seed_{actual_seed}")
        
        logger.info("=" * 60)
        logger.info("Simulation ended.")
        logger.info(f"Random Seed Used: {actual_seed}")
        logger.info(f"Total ticks: {runtime.tick_count}")
        logger.info(f"Surviving agents: {len([a for a in runtime.agents if a.is_alive])}")
        logger.info(f"Total births: {runtime.metrics.total_births}")
        logger.info(f"Total deaths: {runtime.metrics.total_deaths}")
        logger.info(f"Demon whispers: {runtime.demon.total_whispers}")
        
        # Print trait-fitness correlations
        correlations = runtime.metrics.get_trait_fitness_correlation()
        if correlations:
            logger.info("")
            logger.info("Trait-Fitness Correlations (evolutionary pressure indicators):")
            for trait, corr in sorted(correlations.items(), key=lambda x: -abs(x[1]))[:5]:
                direction = "↑" if corr > 0 else "↓"
                logger.info(f"  {trait}: {corr:+.3f} {direction}")
        
        logger.info("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Simulation interrupted by user.")

