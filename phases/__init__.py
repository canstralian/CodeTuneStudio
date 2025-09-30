"""
Development Phases Module

This module implements the development phases framework for CodeTuneStudio:
- 0-to-1 Development ("Greenfield")
- Creative Exploration
- Iterative Enhancement ("Brownfield")
"""

from .base import DevelopmentPhase, PhaseManager, PhaseType
from .greenfield import GreenfieldPhase
from .creative import CreativeExplorationPhase
from .brownfield import BrownfieldPhase

__all__ = [
    'DevelopmentPhase',
    'PhaseManager', 
    'PhaseType',
    'GreenfieldPhase',
    'CreativeExplorationPhase',
    'BrownfieldPhase'
]