"""
Base classes for development phases
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PhaseType(Enum):
    """Development phase types"""
    GREENFIELD = "0-to-1 Development"
    CREATIVE = "Creative Exploration"
    BROWNFIELD = "Iterative Enhancement"


class DevelopmentPhase(ABC):
    """Base class for development phases"""
    
    def __init__(self, name: str, phase_type: PhaseType):
        self.name = name
        self.phase_type = phase_type
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    def get_key_activities(self) -> List[str]:
        """Get list of key activities for this phase"""
        pass
    
    @abstractmethod
    def get_focus_areas(self) -> List[str]:
        """Get focus areas for this phase"""
        pass
    
    @abstractmethod
    def get_required_inputs(self) -> List[str]:
        """Get required inputs for this phase"""
        pass
    
    @abstractmethod
    def get_expected_outputs(self) -> List[str]:
        """Get expected outputs for this phase"""
        pass
    
    @abstractmethod
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the phase with given inputs"""
        pass
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> List[str]:
        """Validate inputs for this phase"""
        errors = []
        required = self.get_required_inputs()
        
        for field in required:
            if field not in inputs:
                errors.append(f"Missing required input: {field}")
            elif not inputs[field]:
                errors.append(f"Empty required input: {field}")
        
        return errors


class PhaseManager:
    """Manager for coordinating development phases"""
    
    def __init__(self):
        self.phases: Dict[PhaseType, DevelopmentPhase] = {}
        self.current_phase: Optional[PhaseType] = None
        self.phase_history: List[PhaseType] = []
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def register_phase(self, phase: DevelopmentPhase) -> None:
        """Register a development phase"""
        self.phases[phase.phase_type] = phase
        self.logger.info(f"Registered phase: {phase.name}")
    
    def get_phase(self, phase_type: PhaseType) -> Optional[DevelopmentPhase]:
        """Get a phase by type"""
        return self.phases.get(phase_type)
    
    def set_current_phase(self, phase_type: PhaseType) -> bool:
        """Set the current active phase"""
        if phase_type not in self.phases:
            self.logger.error(f"Phase not registered: {phase_type}")
            return False
        
        self.current_phase = phase_type
        self.phase_history.append(phase_type)
        self.logger.info(f"Set current phase to: {phase_type.value}")
        return True
    
    def get_current_phase(self) -> Optional[DevelopmentPhase]:
        """Get the current active phase"""
        if self.current_phase:
            return self.phases.get(self.current_phase)
        return None
    
    def list_phases(self) -> List[DevelopmentPhase]:
        """List all registered phases"""
        return list(self.phases.values())
    
    def execute_current_phase(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the current phase"""
        current = self.get_current_phase()
        if not current:
            raise ValueError("No current phase set")
        
        # Validate inputs
        errors = current.validate_inputs(inputs)
        if errors:
            raise ValueError(f"Input validation failed: {'; '.join(errors)}")
        
        # Execute phase
        self.logger.info(f"Executing phase: {current.name}")
        return current.execute(inputs)