"""Orchestrator Agent - Coordinates the multi-agent workflow using LangGraph."""
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from app.core.models import AgentState, AnalysisResult, PolicyInput
from app.agents.policy_analyzer import PolicyAnalyzerAgent
from app.agents.risk_context import RiskContextAgent
from app.agents.best_practice import BestPracticeAgent
from app.agents.gap_reasoning import GapReasoningAgent
from app.utils.logger import get_logger

logger = get_logger(__name__)


class Orchestrator:
    """Orchestrates the multi-agent coverage gap analysis workflow."""
    
    def __init__(self):
        self.policy_analyzer = PolicyAnalyzerAgent()
        self.risk_context = RiskContextAgent()
        self.best_practice = BestPracticeAgent()
        self.gap_reasoning = GapReasoningAgent()
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow."""
        # Create the state graph
        workflow = StateGraph(AgentState)
        
        # Add nodes for each agent
        workflow.add_node("policy_analysis", self._policy_analysis_node)
        workflow.add_node("risk_assessment", self._risk_assessment_node)
        workflow.add_node("best_practices", self._best_practices_node)
        workflow.add_node("gap_reasoning", self._gap_reasoning_node)
        workflow.add_node("finalize", self._finalize_node)
        
        # Define the workflow edges
        workflow.set_entry_point("policy_analysis")
        workflow.add_edge("policy_analysis", "risk_assessment")
        workflow.add_edge("risk_assessment", "best_practices")
        workflow.add_edge("best_practices", "gap_reasoning")
        workflow.add_edge("gap_reasoning", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    def _policy_analysis_node(self, state: AgentState) -> Dict[str, Any]:
        """Execute policy analysis agent."""
        logger.info("Executing Policy Analysis Agent...")
        return self.policy_analyzer.analyze(state)
    
    def _risk_assessment_node(self, state: AgentState) -> Dict[str, Any]:
        """Execute risk assessment agent."""
        logger.info("Executing Risk Context Agent...")
        return self.risk_context.analyze(state)
    
    def _best_practices_node(self, state: AgentState) -> Dict[str, Any]:
        """Execute best practices agent."""
        logger.info("Executing Best Practice Agent...")
        return self.best_practice.analyze(state)
    
    def _gap_reasoning_node(self, state: AgentState) -> Dict[str, Any]:
        """Execute gap reasoning agent."""
        logger.info("Executing Gap Reasoning Agent...")
        return self.gap_reasoning.analyze(state)
    
    def _finalize_node(self, state: AgentState) -> Dict[str, Any]:
        """Finalize analysis and create result."""
        logger.info("Finalizing analysis results...")
        
        coverage_gaps = state.coverage_gaps or []
        policy_input = state.policy_input
        
        # Calculate total premium impact
        total_premium_impact = sum(
            gap.estimated_annual_premium or 0 for gap in coverage_gaps
        )
        
        # Create analysis summary
        if coverage_gaps:
            high_severity = sum(1 for gap in coverage_gaps if gap.severity.value == "High")
            summary = f"Analysis identified {len(coverage_gaps)} coverage gap(s), "
            summary += f"including {high_severity} high-priority item(s). "
            summary += f"Total estimated premium impact: ${total_premium_impact:,.2f}/year. "
            summary += "Addressing these gaps will significantly improve financial protection."
        else:
            summary = "No significant coverage gaps identified. Current policy provides adequate protection."
        
        # Create final result
        analysis_result = AnalysisResult(
            policy_number=policy_input.policy_number,
            customer_name=policy_input.customer_profile.name,
            total_gaps_found=len(coverage_gaps),
            coverage_gaps=coverage_gaps,
            total_estimated_premium_impact=total_premium_impact,
            analysis_summary=summary
        )
        
        logger.info(f"Analysis complete: {len(coverage_gaps)} gaps found")
        
        return {"analysis_result": analysis_result}
    
    def analyze_policy(self, policy_input: PolicyInput) -> AnalysisResult:
        """Run the complete coverage gap analysis workflow."""
        logger.info(f"Starting coverage gap analysis for policy {policy_input.policy_number}")
        
        # Initialize state
        initial_state = AgentState(policy_input=policy_input)
        
        # Execute workflow
        final_state = self.workflow.invoke(initial_state)
        
        logger.info("Coverage gap analysis completed successfully")
        
        return final_state["analysis_result"]
