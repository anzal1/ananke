"""
Verification script for the Ananke simulation.
Tests the theological ontology architecture.
"""

import asyncio
import logging
import sys
from system.runtime import Runtime
from config import INITIAL_RESOURCE_COUNT

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger("VERIFY")


async def test_simulation():
    logger.info("=" * 50)
    logger.info("Starting Theological Ontology Verification...")
    logger.info("=" * 50)
    
    runtime = Runtime()
    
    # Test 1: Provision initial resources via Provisioner angel
    runtime.provisioner.provision_initial(INITIAL_RESOURCE_COUNT)
    logger.info(f"✓ Provisioner: {len(runtime.world.resources)} resources created")
    
    # Test 2: Genesis - spawn Adam and Eve
    runtime.spawn_origin_agents()
    logger.info(f"✓ Genesis: {len(runtime.agents)} origin agents created")
    
    # Verify agent types
    for agent in runtime.agents:
        logger.info(f"  - {agent.id}: type={agent.agent_type}, energy={agent.drives.energy}")
    
    # Test 3: Run 5 ticks
    logger.info("")
    logger.info("Running simulation ticks...")
    for i in range(5):
        await runtime.step()
        await asyncio.sleep(0.1)
        
    logger.info("")
    logger.info("=" * 50)
    logger.info("Verification Complete!")
    logger.info("=" * 50)
    logger.info(f"Final Agent Count: {len(runtime.agents)}")
    logger.info(f"Total Deaths: {runtime.terminator.total_deaths}")
    logger.info(f"Demon Whispers: {runtime.demon.total_whispers}")
    
    # Check ledger
    try:
        with open("divine_ledger.jsonl", "r") as f:
            lines = f.readlines()
            logger.info(f"Recorder: {len(lines)} events logged to divine_ledger.jsonl")
    except FileNotFoundError:
        logger.warning("Recorder: Ledger file not found")


if __name__ == "__main__":
    asyncio.run(test_simulation())
