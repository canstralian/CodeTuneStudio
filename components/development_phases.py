"""
Development Phases Manager Component

This component provides a Streamlit interface for managing development phases
according to the CodeTuneStudio development methodology.
"""

import streamlit as st
from typing import Dict, Any, Optional
import logging
import json
from phases import PhaseManager, PhaseType, GreenfieldPhase, CreativeExplorationPhase, BrownfieldPhase

logger = logging.getLogger(__name__)


def development_phases_manager():
    """Main component for development phases management"""
    st.header("🌟 Development Phases")
    
    # Initialize phase manager in session state
    if "phase_manager" not in st.session_state:
        st.session_state.phase_manager = _initialize_phase_manager()
    
    phase_manager = st.session_state.phase_manager
    
    # Phase selection and overview
    st.markdown("""
    Choose your development approach based on your project's current state and goals:
    
    - **🌱 Greenfield Development**: Start from scratch with high-level requirements
    - **🎨 Creative Exploration**: Explore multiple solutions and technology stacks in parallel
    - **🔧 Brownfield Enhancement**: Iteratively modernize and enhance existing systems
    """)
    
    # Phase selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_phase_name = st.selectbox(
            "Select Development Phase",
            options=[phase.value for phase in PhaseType],
            help="Choose the development phase that best matches your current situation"
        )
        
        # Find the corresponding PhaseType
        selected_phase_type = None
        for phase_type in PhaseType:
            if phase_type.value == selected_phase_name:
                selected_phase_type = phase_type
                break
    
    with col2:
        if st.button("Set Active Phase", type="primary"):
            if selected_phase_type and phase_manager.set_current_phase(selected_phase_type):
                st.success(f"Set active phase to: {selected_phase_name}")
                st.rerun()
    
    # Display current phase information
    current_phase = phase_manager.get_current_phase()
    if current_phase:
        _display_phase_information(current_phase)
        
        # Phase execution interface
        _display_phase_execution_interface(current_phase, phase_manager)
    else:
        st.info("Please select and set an active development phase to continue.")
    
    # Phase history and management
    _display_phase_history(phase_manager)


def _initialize_phase_manager() -> PhaseManager:
    """Initialize the phase manager with all phases"""
    manager = PhaseManager()
    
    # Register all phases
    manager.register_phase(GreenfieldPhase())
    manager.register_phase(CreativeExplorationPhase())
    manager.register_phase(BrownfieldPhase())
    
    return manager


def _display_phase_information(phase):
    """Display information about the selected phase"""
    st.subheader(f"📋 {phase.name}")
    
    # Phase details in expandable sections
    with st.expander("🎯 Focus Areas", expanded=True):
        focus_areas = phase.get_focus_areas()
        for area in focus_areas:
            st.markdown(f"• {area}")
    
    with st.expander("⚡ Key Activities"):
        activities = phase.get_key_activities()
        for activity in activities:
            st.markdown(f"• {activity}")
    
    with st.expander("📥 Required Inputs"):
        inputs = phase.get_required_inputs()
        for inp in inputs:
            st.markdown(f"• **{inp.replace('_', ' ').title()}**")
    
    with st.expander("📤 Expected Outputs"):
        outputs = phase.get_expected_outputs()
        for output in outputs:
            st.markdown(f"• **{output.replace('_', ' ').title()}**")


def _display_phase_execution_interface(phase, phase_manager: PhaseManager):
    """Display the phase execution interface"""
    st.subheader("🚀 Execute Phase")
    
    # Input collection based on phase requirements
    inputs = _collect_phase_inputs(phase)
    
    # Validation and execution
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("Validate Inputs"):
            errors = phase.validate_inputs(inputs)
            if errors:
                for error in errors:
                    st.error(error)
            else:
                st.success("All inputs are valid!")
    
    with col2:
        if st.button("Execute Phase", type="primary"):
            try:
                with st.spinner(f"Executing {phase.name}..."):
                    results = phase_manager.execute_current_phase(inputs)
                    st.session_state.phase_results = results
                    st.success("Phase executed successfully!")
                    st.rerun()
            except Exception as e:
                st.error(f"Phase execution failed: {str(e)}")
                logger.error(f"Phase execution error: {e}", exc_info=True)
    
    with col3:
        if st.button("Clear Inputs"):
            _clear_phase_inputs(phase)
            st.rerun()
    
    # Display results if available
    if hasattr(st.session_state, 'phase_results') and st.session_state.phase_results:
        _display_phase_results(st.session_state.phase_results)


def _collect_phase_inputs(phase) -> Dict[str, Any]:
    """Collect inputs for the current phase"""
    st.subheader("📝 Phase Inputs")
    
    inputs = {}
    required_inputs = phase.get_required_inputs()
    
    # Create input fields based on phase type
    if phase.phase_type == PhaseType.GREENFIELD:
        inputs = _collect_greenfield_inputs(required_inputs)
    elif phase.phase_type == PhaseType.CREATIVE:
        inputs = _collect_creative_inputs(required_inputs)
    elif phase.phase_type == PhaseType.BROWNFIELD:
        inputs = _collect_brownfield_inputs(required_inputs)
    
    return inputs


def _collect_greenfield_inputs(required_inputs: list) -> Dict[str, Any]:
    """Collect inputs for greenfield development"""
    inputs = {}
    
    with st.form("greenfield_inputs"):
        st.markdown("### Greenfield Development Inputs")
        
        # Requirements
        if "requirements" in required_inputs:
            inputs["requirements"] = st.text_area(
                "High-Level Requirements",
                placeholder="Describe the system requirements, goals, and objectives...",
                height=150,
                help="Provide detailed requirements for the system you want to build"
            )
        
        # Technology stack
        if "target_technology_stack" in required_inputs:
            col1, col2 = st.columns(2)
            with col1:
                tech_preference = st.selectbox(
                    "Technology Stack Preference",
                    ["Python/Streamlit", "JavaScript/React", "Python/FastAPI", "Microservices", "Cloud-Native", "Custom"]
                )
            with col2:
                custom_tech = st.text_input(
                    "Custom Technology Stack",
                    placeholder="Specify if 'Custom' selected above"
                )
            
            inputs["target_technology_stack"] = custom_tech if tech_preference == "Custom" else tech_preference
        
        # Performance criteria
        if "performance_criteria" in required_inputs:
            st.markdown("**Performance Criteria**")
            col1, col2, col3 = st.columns(3)
            with col1:
                response_time = st.number_input("Max Response Time (ms)", min_value=100, value=1000)
            with col2:
                concurrent_users = st.number_input("Concurrent Users", min_value=1, value=100)
            with col3:
                uptime_requirement = st.number_input("Uptime Requirement (%)", min_value=90.0, max_value=100.0, value=99.9)
            
            inputs["performance_criteria"] = {
                "response_time_ms": response_time,
                "concurrent_users": concurrent_users,
                "uptime_percent": uptime_requirement
            }
        
        # Deployment environment
        if "deployment_environment" in required_inputs:
            deployment_env = st.selectbox(
                "Deployment Environment",
                ["Cloud (AWS/Azure/GCP)", "On-Premises", "Hybrid", "Edge Computing", "Local Development"]
            )
            inputs["deployment_environment"] = deployment_env
        
        submitted = st.form_submit_button("Save Inputs")
        if submitted:
            st.success("Greenfield inputs saved!")
    
    return inputs


def _collect_creative_inputs(required_inputs: list) -> Dict[str, Any]:
    """Collect inputs for creative exploration"""
    inputs = {}
    
    with st.form("creative_inputs"):
        st.markdown("### Creative Exploration Inputs")
        
        # Base requirements
        if "base_requirements" in required_inputs:
            inputs["base_requirements"] = st.text_area(
                "Base Requirements",
                placeholder="Core functionality and constraints...",
                height=100
            )
        
        # Exploration scope
        if "exploration_scope" in required_inputs:
            scope_areas = st.multiselect(
                "Exploration Scope",
                ["Technology Stacks", "Architecture Patterns", "UI/UX Designs", "Performance Approaches", "Deployment Models"],
                default=["Technology Stacks", "UI/UX Designs"]
            )
            
            exploration_depth = st.select_slider(
                "Exploration Depth",
                options=["Surface", "Moderate", "Deep", "Comprehensive"],
                value="Moderate"
            )
            
            inputs["exploration_scope"] = {
                "areas": scope_areas,
                "depth": exploration_depth
            }
        
        # Target user cohorts
        if "target_user_cohorts" in required_inputs:
            user_cohorts = st.multiselect(
                "Target User Cohorts",
                ["Beginners", "Experienced Users", "Data Scientists", "ML Engineers", "Business Users", "Developers"],
                default=["Data Scientists", "ML Engineers"]
            )
            inputs["target_user_cohorts"] = user_cohorts
        
        # Technology constraints
        if "technology_constraints" in required_inputs:
            st.markdown("**Technology Constraints**")
            col1, col2 = st.columns(2)
            with col1:
                team_skills = st.multiselect(
                    "Team Skills",
                    ["Python", "JavaScript", "React", "Vue.js", "Node.js", "SQL", "NoSQL", "Docker", "Kubernetes"],
                    default=["Python", "SQL"]
                )
            with col2:
                budget_constraint = st.selectbox(
                    "Budget Constraint",
                    ["Low", "Medium", "High", "No Constraint"]
                )
            
            time_constraint = st.slider("Time Constraint (weeks)", 1, 24, 12)
            
            inputs["technology_constraints"] = {
                "team_skills": team_skills,
                "budget": budget_constraint,
                "time_weeks": time_constraint
            }
        
        # Evaluation criteria
        if "evaluation_criteria" in required_inputs:
            st.markdown("**Evaluation Criteria Weights**")
            col1, col2, col3 = st.columns(3)
            with col1:
                dev_speed_weight = st.slider("Development Speed", 0.0, 1.0, 0.2, 0.05)
                scalability_weight = st.slider("Scalability", 0.0, 1.0, 0.15, 0.05)
                maintainability_weight = st.slider("Maintainability", 0.0, 1.0, 0.15, 0.05)
            with col2:
                performance_weight = st.slider("Performance", 0.0, 1.0, 0.1, 0.05)
                cost_weight = st.slider("Cost", 0.0, 1.0, 0.1, 0.05)
                team_expertise_weight = st.slider("Team Expertise", 0.0, 1.0, 0.15, 0.05)
            with col3:
                ecosystem_weight = st.slider("Ecosystem Maturity", 0.0, 1.0, 0.1, 0.05)
                security_weight = st.slider("Security", 0.0, 1.0, 0.05, 0.05)
            
            inputs["evaluation_criteria"] = {
                "weights": {
                    "development_speed": dev_speed_weight,
                    "scalability": scalability_weight,
                    "maintainability": maintainability_weight,
                    "performance": performance_weight,
                    "cost": cost_weight,
                    "team_expertise": team_expertise_weight,
                    "ecosystem_maturity": ecosystem_weight,
                    "security": security_weight
                }
            }
        
        submitted = st.form_submit_button("Save Inputs")
        if submitted:
            st.success("Creative exploration inputs saved!")
    
    return inputs


def _collect_brownfield_inputs(required_inputs: list) -> Dict[str, Any]:
    """Collect inputs for brownfield enhancement"""
    inputs = {}
    
    with st.form("brownfield_inputs"):
        st.markdown("### Brownfield Enhancement Inputs")
        
        # Existing system analysis
        if "existing_system_analysis" in required_inputs:
            st.markdown("**Current System Analysis**")
            
            current_architecture = st.text_area(
                "Current Architecture Description",
                placeholder="Describe the current system architecture...",
                height=100
            )
            
            col1, col2 = st.columns(2)
            with col1:
                current_tech_stack = st.text_area(
                    "Current Technology Stack",
                    placeholder="List current technologies and versions...",
                    height=80
                )
            with col2:
                known_issues = st.text_area(
                    "Known Issues and Pain Points",
                    placeholder="List current problems and limitations...",
                    height=80
                )
            
            inputs["existing_system_analysis"] = {
                "architecture": current_architecture,
                "technology_stack": {"description": current_tech_stack},
                "known_issues": known_issues,
                "performance_metrics": "Current metrics to be gathered"
            }
        
        # Modernization goals
        if "modernization_goals" in required_inputs:
            modernization_goals = st.multiselect(
                "Modernization Goals",
                ["Improve Performance", "Enhance User Experience", "Increase Scalability", 
                 "Reduce Technical Debt", "Improve Security", "Better Maintainability", 
                 "Cloud Migration", "Modern UI/UX"],
                default=["Improve Performance", "Enhance User Experience"]
            )
            
            success_criteria = st.text_area(
                "Success Criteria",
                placeholder="Define how you'll measure success...",
                height=80
            )
            
            inputs["modernization_goals"] = {
                "goals": modernization_goals,
                "success_criteria": success_criteria
            }
        
        # Enhancement requirements
        if "enhancement_requirements" in required_inputs:
            enhancement_requirements = st.text_area(
                "Enhancement Requirements",
                placeholder="Specific features and improvements needed...",
                height=120
            ).split('\n') if st.text_area(
                "Enhancement Requirements",
                placeholder="Specific features and improvements needed...",
                height=120
            ) else []
            
            inputs["enhancement_requirements"] = [req.strip() for req in enhancement_requirements if req.strip()]
        
        # Constraints and dependencies
        if "constraints_and_dependencies" in required_inputs:
            st.markdown("**Constraints and Dependencies**")
            
            col1, col2 = st.columns(2)
            with col1:
                budget_constraint = st.selectbox("Budget Constraint", ["Low", "Medium", "High", "No Constraint"])
                time_constraint = st.number_input("Time Constraint (weeks)", min_value=1, value=16)
            with col2:
                team_size = st.number_input("Team Size", min_value=1, value=3)
                risk_tolerance = st.selectbox("Risk Tolerance", ["Low", "Medium", "High"])
            
            external_dependencies = st.text_area(
                "External Dependencies",
                placeholder="List external systems, APIs, or services that must be maintained...",
                height=60
            )
            
            inputs["constraints_and_dependencies"] = {
                "budget": budget_constraint,
                "time_weeks": time_constraint,
                "team_size": team_size,
                "risk_tolerance": risk_tolerance,
                "external_dependencies": external_dependencies.split('\n') if external_dependencies else []
            }
        
        # Migration strategy
        if "migration_strategy" in required_inputs:
            migration_approach = st.selectbox(
                "Migration Strategy",
                ["Big Bang", "Phased Rollout", "Blue-Green Deployment", "Canary Releases", "Feature Flags"]
            )
            
            rollback_strategy = st.text_area(
                "Rollback Strategy",
                placeholder="Describe the rollback approach if issues occur...",
                height=60
            )
            
            inputs["migration_strategy"] = {
                "approach": migration_approach,
                "rollback_strategy": rollback_strategy
            }
        
        submitted = st.form_submit_button("Save Inputs")
        if submitted:
            st.success("Brownfield enhancement inputs saved!")
    
    return inputs


def _clear_phase_inputs(phase):
    """Clear stored inputs for the current phase"""
    # Clear form data from session state
    phase_key = f"{phase.phase_type.value.lower()}_inputs"
    if phase_key in st.session_state:
        del st.session_state[phase_key]


def _display_phase_results(results: Dict[str, Any]):
    """Display the results of phase execution"""
    st.subheader("📊 Phase Results")
    
    # Display results in an organized manner
    with st.expander("Full Results (JSON)", expanded=False):
        st.json(results)
    
    # Extract and display key results
    if "phase_status" in results:
        status = results["phase_status"]
        if status == "completed":
            st.success("✅ Phase completed successfully!")
        else:
            st.warning(f"⚠️ Phase status: {status}")
    
    # Display specific outputs based on phase type
    _display_type_specific_results(results)
    
    # Next steps
    if "next_recommended_phase" in results:
        st.info(f"💡 Recommended next phase: {results['next_recommended_phase']}")


def _display_type_specific_results(results: Dict[str, Any]):
    """Display results specific to the phase type"""
    
    # Greenfield results
    if "system_specification" in results:
        with st.expander("🏗️ System Specification"):
            st.write(results["system_specification"])
    
    if "architecture_design" in results:
        with st.expander("🏛️ Architecture Design"):
            st.write(results["architecture_design"])
    
    if "implementation_plan" in results:
        with st.expander("📋 Implementation Plan"):
            st.write(results["implementation_plan"])
    
    # Creative exploration results
    if "multiple_solution_prototypes" in results:
        with st.expander("🎨 Solution Prototypes"):
            prototypes = results["multiple_solution_prototypes"]
            for prototype in prototypes:
                st.subheader(prototype.get("name", "Prototype"))
                st.write(f"**Technology Stack:** {prototype.get('technology_stack', {})}")
                st.write(f"**Estimated Effort:** {prototype.get('estimated_effort', 'Unknown')}")
                if "advantages" in prototype:
                    st.write("**Advantages:**")
                    for advantage in prototype["advantages"]:
                        st.write(f"• {advantage}")
    
    if "recommended_approach" in results:
        with st.expander("🎯 Recommended Approach"):
            recommendation = results["recommended_approach"]
            if "primary_recommendation" in recommendation:
                primary = recommendation["primary_recommendation"]
                st.subheader(primary.get("approach", "Primary Recommendation"))
                st.write("**Rationale:**")
                for rationale in primary.get("rationale", []):
                    st.write(f"• {rationale}")
                st.write("**Implementation Strategy:**")
                for strategy in primary.get("implementation_strategy", []):
                    st.write(f"• {strategy}")
    
    # Brownfield results
    if "modernization_roadmap" in results:
        with st.expander("🗺️ Modernization Roadmap"):
            roadmap = results["modernization_roadmap"]
            if "phased_approach" in roadmap:
                for phase in roadmap["phased_approach"]:
                    st.subheader(f"Phase: {phase.get('phase', 'Unknown')}")
                    st.write(f"**Duration:** {phase.get('duration', 'Unknown')}")
                    st.write(f"**Focus:** {phase.get('focus', 'Unknown')}")
                    st.write(f"**Risk Level:** {phase.get('risk_level', 'Unknown')}")
    
    if "risk_mitigation_strategy" in results:
        with st.expander("⚠️ Risk Mitigation Strategy"):
            st.write(results["risk_mitigation_strategy"])


def _display_phase_history(phase_manager: PhaseManager):
    """Display phase execution history"""
    if phase_manager.phase_history:
        with st.expander("📚 Phase History"):
            st.markdown("**Previously executed phases:**")
            for i, phase_type in enumerate(phase_manager.phase_history):
                st.write(f"{i+1}. {phase_type.value}")
    
    # Phase management actions
    st.subheader("🔧 Phase Management")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Clear Phase History"):
            phase_manager.phase_history.clear()
            st.success("Phase history cleared!")
            st.rerun()
    
    with col2:
        if st.button("Reset Phase Manager"):
            if "phase_manager" in st.session_state:
                del st.session_state.phase_manager
            if "phase_results" in st.session_state:
                del st.session_state.phase_results
            st.success("Phase manager reset!")
            st.rerun()


# Export the main function
__all__ = ["development_phases_manager"]