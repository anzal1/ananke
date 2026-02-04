"""
Angel Subsystems

Non-volitional executors - pure functions with no will.
They do not decide. They do not tempt. They do not rebel.

- Recorder: Append-only action ledger
- Provisioner: Resource spawn engine
- Terminator: Death finalization
"""

from cosmology.angels.recorder import Recorder
from cosmology.angels.provisioner import Provisioner
from cosmology.angels.terminator import Terminator

__all__ = ["Recorder", "Provisioner", "Terminator"]
