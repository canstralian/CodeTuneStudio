"""
Experimental Goals Module

This module implements the experimental goals framework for CodeTuneStudio:
- Technology independence
- Enterprise constraints  
- User-centric development
- Creative & iterative processes
"""

from .goals import (
    ExperimentalGoal,
    ExperimentalObjective,
    ExperimentalGoalsManager,
    TechnologyIndependenceObjective,
    EnterpriseConstraintsObjective,
    UserCentricDevelopmentObjective,
    CreativeIterativeProcessesObjective,
    initialize_experimental_goals_manager
)

__all__ = [
    'ExperimentalGoal',
    'ExperimentalObjective', 
    'ExperimentalGoalsManager',
    'TechnologyIndependenceObjective',
    'EnterpriseConstraintsObjective',
    'UserCentricDevelopmentObjective',
    'CreativeIterativeProcessesObjective',
    'initialize_experimental_goals_manager'
]