"""
Experimental Goals Manager Component

This component provides a Streamlit interface for managing experimental goals
and tracking validation progress according to the CodeTuneStudio research framework.
"""

import streamlit as st
from typing import Dict, Any, Optional
import logging
import json
import plotly.graph_objects as go
import plotly.express as px
from experimental import (
    ExperimentalGoalsManager, 
    ExperimentalGoal,
    initialize_experimental_goals_manager
)

logger = logging.getLogger(__name__)


def experimental_goals_manager():
    """Main component for experimental goals management"""
    st.header("🎯 Experimental Goals")
    
    # Initialize experimental goals manager in session state
    if "experimental_manager" not in st.session_state:
        st.session_state.experimental_manager = initialize_experimental_goals_manager()
    
    experimental_manager = st.session_state.experimental_manager
    
    # Overview and hypothesis section
    st.markdown("""
    Our research and experimentation focus on validating key hypotheses about 
    Spec-Driven Development and modern software engineering practices:
    """)
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔬 Objectives Overview", 
        "📊 Experiment Tracking", 
        "📈 Validation Dashboard",
        "🎯 Goals Configuration"
    ])
    
    with tab1:
        _display_objectives_overview(experimental_manager)
    
    with tab2:
        _display_experiment_tracking(experimental_manager)
    
    with tab3:
        _display_validation_dashboard(experimental_manager)
    
    with tab4:
        _display_goals_configuration(experimental_manager)


def _display_objectives_overview(manager: ExperimentalGoalsManager):
    """Display overview of all experimental objectives"""
    st.subheader("🎯 Research Objectives")
    
    objectives = manager.list_objectives()
    
    for objective in objectives:
        with st.expander(f"🔬 {objective.name}", expanded=False):
            # Hypothesis
            st.markdown("**Hypothesis:**")
            st.info(objective.get_hypothesis())
            
            # Validation criteria
            st.markdown("**Validation Criteria:**")
            criteria = objective.get_validation_criteria()
            for i, criterion in enumerate(criteria, 1):
                st.markdown(f"{i}. {criterion}")
            
            # Implementation approaches
            st.markdown("**Implementation Approaches:**")
            approaches = objective.get_implementation_approaches()
            
            for approach in approaches:
                st.markdown(f"**{approach['name']}**")
                st.markdown(f"*{approach['description']}*")
                
                if 'technology_stacks' in approach:
                    st.markdown("Technology Stacks:")
                    for stack in approach['technology_stacks']:
                        st.markdown(f"• **{stack['name']}** - {stack['focus']}")
                
                if 'components' in approach:
                    st.markdown("Components:")
                    for component in approach['components']:
                        st.markdown(f"• {component}")
                
                if 'validation_metrics' in approach:
                    st.markdown("Validation Metrics:")
                    for metric in approach['validation_metrics']:
                        st.markdown(f"• {metric}")
                
                st.markdown("---")


def _display_experiment_tracking(manager: ExperimentalGoalsManager):
    """Display experiment tracking interface"""
    st.subheader("📊 Experiment Tracking")
    
    # Experiment creation
    with st.expander("🆕 Create New Experiment", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            experiment_name = st.text_input(
                "Experiment Name",
                placeholder="e.g., technology_independence_Q1_2024"
            )
            
            goal_type = st.selectbox(
                "Experimental Goal",
                options=[goal.value for goal in ExperimentalGoal]
            )
        
        with col2:
            experiment_description = st.text_area(
                "Experiment Description",
                placeholder="Describe the experiment objectives and methodology...",
                height=100
            )
        
        if st.button("Start Experiment", type="primary"):
            if experiment_name and goal_type:
                # Find the corresponding ExperimentalGoal enum
                selected_goal = None
                for goal in ExperimentalGoal:
                    if goal.value == goal_type:
                        selected_goal = goal
                        break
                
                if selected_goal and manager.start_experiment(experiment_name, selected_goal):
                    st.success(f"Started experiment: {experiment_name}")
                    st.rerun()
                else:
                    st.error("Failed to start experiment")
            else:
                st.error("Please provide experiment name and select a goal")
    
    # Active experiments
    st.subheader("⚡ Active Experiments")
    
    if manager.active_experiments:
        for experiment in manager.active_experiments:
            with st.expander(f"📈 {experiment}"):
                _display_experiment_details(manager, experiment)
    else:
        st.info("No active experiments. Create a new experiment to get started.")
    
    # Results input interface
    st.subheader("📝 Record Experiment Results")
    
    if manager.active_experiments:
        selected_experiment = st.selectbox(
            "Select Experiment",
            options=manager.active_experiments
        )
        
        # Dynamic results input based on experiment type
        _display_results_input_interface(manager, selected_experiment)
    else:
        st.info("Start an experiment first to record results.")


def _display_experiment_details(manager: ExperimentalGoalsManager, experiment_name: str):
    """Display details for a specific experiment"""
    st.markdown(f"**Experiment:** {experiment_name}")
    
    # Show if results have been recorded
    if experiment_name in manager.experiment_results:
        results = manager.experiment_results[experiment_name]
        st.success("✅ Results recorded")
        
        # Show summary of results
        with st.expander("View Results Summary"):
            st.json(results)
    else:
        st.warning("⏳ Awaiting results")
    
    # Experiment management actions
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(f"Complete {experiment_name}", key=f"complete_{experiment_name}"):
            if experiment_name in manager.active_experiments:
                manager.active_experiments.remove(experiment_name)
                st.success(f"Completed experiment: {experiment_name}")
                st.rerun()
    
    with col2:
        if st.button(f"Delete {experiment_name}", key=f"delete_{experiment_name}"):
            if experiment_name in manager.active_experiments:
                manager.active_experiments.remove(experiment_name)
            if experiment_name in manager.experiment_results:
                del manager.experiment_results[experiment_name]
            st.success(f"Deleted experiment: {experiment_name}")
            st.rerun()


def _display_results_input_interface(manager: ExperimentalGoalsManager, experiment_name: str):
    """Display interface for inputting experiment results"""
    
    # Determine experiment type from name
    experiment_type = None
    for goal in ExperimentalGoal:
        if goal.value.lower().replace(" ", "_") in experiment_name.lower():
            experiment_type = goal
            break
    
    if not experiment_type:
        st.error("Could not determine experiment type from name")
        return
    
    with st.form(f"results_form_{experiment_name}"):
        st.markdown(f"**Recording results for: {experiment_name}**")
        
        results = {}
        
        if experiment_type == ExperimentalGoal.TECHNOLOGY_INDEPENDENCE:
            results = _input_technology_independence_results()
        elif experiment_type == ExperimentalGoal.ENTERPRISE_CONSTRAINTS:
            results = _input_enterprise_constraints_results()
        elif experiment_type == ExperimentalGoal.USER_CENTRIC_DEVELOPMENT:
            results = _input_user_centric_results()
        elif experiment_type == ExperimentalGoal.CREATIVE_ITERATIVE_PROCESSES:
            results = _input_creative_processes_results()
        
        submitted = st.form_submit_button("Record Results", type="primary")
        
        if submitted and results:
            manager.record_experiment_results(experiment_name, results)
            st.success("Results recorded successfully!")
            st.rerun()


def _input_technology_independence_results() -> Dict[str, Any]:
    """Input interface for technology independence results"""
    st.subheader("Technology Independence Results")
    
    results = {}
    
    # Multi-stack implementation results
    st.markdown("**Multi-Stack Implementation Results:**")
    num_stacks = st.number_input("Number of technology stacks implemented", min_value=0, max_value=10, value=0)
    
    if num_stacks > 0:
        stack_results = []
        for i in range(num_stacks):
            col1, col2, col3 = st.columns(3)
            with col1:
                stack_name = st.text_input(f"Stack {i+1} Name", key=f"stack_name_{i}")
            with col2:
                success = st.checkbox(f"Implementation Successful", key=f"stack_success_{i}")
            with col3:
                completion_time = st.number_input(f"Development Time (weeks)", min_value=0, key=f"stack_time_{i}")
            
            if stack_name:
                stack_results.append({
                    "name": stack_name,
                    "success": success,
                    "development_time_weeks": completion_time
                })
        
        results["multi_stack_results"] = stack_results
    
    # Framework agnostic results
    st.markdown("**Framework Agnostic Design Results:**")
    code_reuse = st.slider("Code Reuse Percentage", 0, 100, 0)
    migration_effort = st.selectbox("Migration Effort", ["Low", "Medium", "High"])
    
    results["framework_agnostic_results"] = {
        "code_reuse_percentage": code_reuse,
        "migration_effort": migration_effort
    }
    
    # Cloud independence results
    st.markdown("**Cloud Provider Independence Results:**")
    num_deployments = st.number_input("Number of cloud providers deployed to", min_value=0, max_value=5, value=0)
    
    if num_deployments > 0:
        cloud_results = []
        providers = ["AWS", "Azure", "Google Cloud", "On-premises", "Other"]
        
        for i in range(num_deployments):
            col1, col2 = st.columns(2)
            with col1:
                provider = st.selectbox(f"Provider {i+1}", providers, key=f"provider_{i}")
            with col2:
                deployment_success = st.checkbox(f"Deployment Successful", key=f"deployment_success_{i}")
            
            cloud_results.append({
                "provider": provider,
                "success": deployment_success
            })
        
        results["cloud_independence_results"] = cloud_results
    
    return results


def _input_enterprise_constraints_results() -> Dict[str, Any]:
    """Input interface for enterprise constraints results"""
    st.subheader("Enterprise Constraints Results")
    
    results = {}
    
    # Design system integration
    st.markdown("**Design System Integration:**")
    compliance_percentage = st.slider("Design Compliance Percentage", 0, 100, 0)
    accessibility_score = st.slider("Accessibility Score", 0, 100, 0)
    
    results["design_system_results"] = {
        "compliance_percentage": compliance_percentage,
        "accessibility_score": accessibility_score
    }
    
    # Compliance framework
    st.markdown("**Compliance Framework:**")
    col1, col2 = st.columns(2)
    with col1:
        passed_audits = st.number_input("Passed Audits", min_value=0, value=0)
    with col2:
        total_audits = st.number_input("Total Audits", min_value=1, value=1)
    
    security_score = st.slider("Security Audit Score", 0, 100, 0)
    
    results["compliance_results"] = {
        "passed_audits": passed_audits,
        "total_audits": total_audits,
        "security_score": security_score
    }
    
    # Enterprise integration
    st.markdown("**Enterprise Integration:**")
    col1, col2 = st.columns(2)
    with col1:
        successful_integrations = st.number_input("Successful Integrations", min_value=0, value=0)
    with col2:
        total_integrations = st.number_input("Total Integrations", min_value=1, value=1)
    
    results["integration_results"] = {
        "successful_integrations": successful_integrations,
        "total_integrations": total_integrations
    }
    
    return results


def _input_user_centric_results() -> Dict[str, Any]:
    """Input interface for user-centric development results"""
    st.subheader("User-Centric Development Results")
    
    results = {}
    
    # Multi-cohort interface results
    st.markdown("**Multi-Cohort Interface Results:**")
    average_satisfaction = st.slider("Average User Satisfaction", 0, 100, 0)
    task_completion_rate = st.slider("Task Completion Rate", 0, 100, 0)
    
    results["multi_cohort_results"] = {
        "average_satisfaction": average_satisfaction,
        "task_completion_rate": task_completion_rate
    }
    
    # AI-native support results
    st.markdown("**AI-Native Support Results:**")
    adoption_rate = st.slider("AI Feature Adoption Rate", 0, 100, 0)
    productivity_improvement = st.slider("Productivity Improvement", 0, 100, 0)
    
    results["ai_native_results"] = {
        "adoption_rate": adoption_rate,
        "productivity_improvement": productivity_improvement
    }
    
    # Personalization results
    st.markdown("**Personalization Engine Results:**")
    effectiveness_score = st.slider("Personalization Effectiveness", 0, 100, 0)
    engagement_improvement = st.slider("Engagement Improvement", 0, 100, 0)
    
    results["personalization_results"] = {
        "effectiveness_score": effectiveness_score,
        "engagement_improvement": engagement_improvement
    }
    
    return results


def _input_creative_processes_results() -> Dict[str, Any]:
    """Input interface for creative and iterative processes results"""
    st.subheader("Creative & Iterative Processes Results")
    
    results = {}
    
    # Parallel exploration results
    st.markdown("**Parallel Implementation Exploration:**")
    prototypes_generated = st.number_input("Number of Prototypes Generated", min_value=0, value=0)
    solution_quality_score = st.slider("Final Solution Quality Score", 0, 100, 0)
    
    results["parallel_exploration_results"] = {
        "prototypes_generated": prototypes_generated,
        "solution_quality_score": solution_quality_score
    }
    
    # Iterative enhancement results
    st.markdown("**Iterative Enhancement Framework:**")
    velocity_improvement = st.slider("Development Velocity Improvement (%)", 0, 100, 0)
    feature_adoption_rate = st.slider("Feature Adoption Rate", 0, 100, 0)
    
    results["iterative_enhancement_results"] = {
        "velocity_improvement": velocity_improvement,
        "feature_adoption_rate": feature_adoption_rate
    }
    
    # Modernization workflow results
    st.markdown("**Modernization Workflow Engine:**")
    modernization_success_rate = st.slider("Modernization Success Rate", 0, 100, 0)
    risk_mitigation_effectiveness = st.slider("Risk Mitigation Effectiveness", 0, 100, 0)
    
    results["modernization_workflow_results"] = {
        "modernization_success_rate": modernization_success_rate,
        "risk_mitigation_effectiveness": risk_mitigation_effectiveness
    }
    
    return results


def _display_validation_dashboard(manager: ExperimentalGoalsManager):
    """Display validation dashboard with metrics and visualizations"""
    st.subheader("📈 Validation Dashboard")
    
    # Get overall validation status
    validation_status = manager.get_overall_validation_status()
    
    # Overall status
    col1, col2, col3 = st.columns(3)
    
    with col1:
        overall_score = validation_status["overall_score"]
        st.metric(
            "Overall Validation Score",
            f"{overall_score:.1f}%",
            delta=None,
            help="Average score across all experimental objectives"
        )
    
    with col2:
        validated_count = validation_status["validated_objectives"]
        total_count = validation_status["total_objectives"]
        st.metric(
            "Validated Objectives",
            f"{validated_count}/{total_count}",
            delta=None,
            help="Number of objectives that have reached validation threshold"
        )
    
    with col3:
        status_color = {
            "VALIDATED": "🟢",
            "PARTIAL": "🟡", 
            "NOT_VALIDATED": "🔴"
        }
        status_icon = status_color.get(validation_status["validation_status"], "⚪")
        st.metric(
            "Validation Status",
            f"{status_icon} {validation_status['validation_status']}",
            delta=None,
            help="Overall validation status based on objective scores"
        )
    
    # Objective-level validation details
    if validation_status["objective_validations"]:
        st.subheader("🎯 Objective Validation Details")
        
        # Create visualization
        objective_names = []
        objective_scores = []
        objective_statuses = []
        
        for obj_name, obj_validation in validation_status["objective_validations"].items():
            objective_names.append(obj_name)
            objective_scores.append(obj_validation["overall_score"])
            objective_statuses.append(obj_validation["validation_status"])
        
        # Bar chart of objective scores
        fig = go.Figure(data=[
            go.Bar(
                x=objective_names,
                y=objective_scores,
                text=[f"{score:.1f}%" for score in objective_scores],
                textposition='auto',
                marker_color=['green' if status == 'VALIDATED' else 'orange' if status == 'PARTIAL' else 'red' 
                             for status in objective_statuses]
            )
        ])
        
        fig.update_layout(
            title="Experimental Objective Validation Scores",
            xaxis_title="Objectives",
            yaxis_title="Validation Score (%)",
            yaxis=dict(range=[0, 100]),
            height=400
        )
        
        # Add threshold lines
        fig.add_hline(y=80, line_dash="dash", line_color="green", 
                     annotation_text="Validation Threshold (80%)")
        fig.add_hline(y=65, line_dash="dash", line_color="orange", 
                     annotation_text="Partial Threshold (65%)")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed validation breakdown
        for obj_name, obj_validation in validation_status["objective_validations"].items():
            with st.expander(f"📊 {obj_name} - {obj_validation['validation_status']}", expanded=False):
                
                # Score breakdown
                st.metric("Overall Score", f"{obj_validation['overall_score']:.1f}%")
                
                # Details breakdown
                if "details" in obj_validation and obj_validation["details"]:
                    st.markdown("**Component Scores:**")
                    for component, details in obj_validation["details"].items():
                        if isinstance(details, dict) and "score" in details:
                            st.markdown(f"• **{component.replace('_', ' ').title()}**: {details['score']:.1f}")
                
                # Recommendations
                if "recommendations" in obj_validation and obj_validation["recommendations"]:
                    st.markdown("**Recommendations:**")
                    for rec in obj_validation["recommendations"]:
                        st.markdown(f"• {rec}")
    else:
        st.info("No validation data available. Record experiment results to see validation dashboard.")


def _display_goals_configuration(manager: ExperimentalGoalsManager):
    """Display configuration interface for experimental goals"""
    st.subheader("🎯 Goals Configuration")
    
    # Experiment management
    st.markdown("### Experiment Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Clear All Experiments"):
            manager.active_experiments.clear()
            manager.experiment_results.clear()
            st.success("All experiments cleared!")
            st.rerun()
    
    with col2:
        if st.button("Export Experiment Data"):
            export_data = {
                "active_experiments": manager.active_experiments,
                "experiment_results": manager.experiment_results,
                "validation_status": manager.get_overall_validation_status()
            }
            st.download_button(
                label="Download JSON",
                data=json.dumps(export_data, indent=2),
                file_name="experimental_goals_data.json",
                mime="application/json"
            )
    
    # Configuration settings
    st.markdown("### Configuration Settings")
    
    # Validation thresholds
    with st.expander("Validation Thresholds"):
        st.markdown("Current validation thresholds:")
        st.markdown("• **Validated**: ≥ 80%")
        st.markdown("• **Partial**: ≥ 65%")
        st.markdown("• **Not Validated**: < 65%")
        
        st.info("Thresholds are currently fixed but could be made configurable in future versions.")
    
    # Debug information
    with st.expander("Debug Information"):
        st.markdown("**Active Experiments:**")
        st.write(manager.active_experiments)
        
        st.markdown("**Experiment Results:**")
        st.write(manager.experiment_results)
        
        st.markdown("**Registered Objectives:**")
        for obj in manager.list_objectives():
            st.write(f"• {obj.name} ({obj.goal_type.value})")


# Export the main function
__all__ = ["experimental_goals_manager"]