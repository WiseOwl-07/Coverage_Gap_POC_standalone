"""Policy Analysis Agent - Extracts and summarizes existing coverages."""
from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import get_settings
from app.core.models import AgentState, PolicyInput
from app.utils.logger import get_logger

logger = get_logger(__name__)


class PolicyAnalyzerAgent:
    """Agent that analyzes and summarizes existing policy coverages."""
    
    def __init__(self):
        settings = get_settings()
        self.llm = ChatGroq(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            api_key=settings.groq_api_key
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an insurance policy analysis expert. Your job is to review 
            existing insurance coverages and create a clear, structured summary.
            
            Analyze the policy data and provide:
            1. A brief overview of the customer profile
            2. Summary of ALL existing coverages with limits and deductibles
            3. Key observations about the current coverage portfolio
            
            Be factual and concise. Output in a structured format."""),
            ("user", "Policy Data:\n{policy_data}")
        ])
    
    def analyze(self, state: AgentState) -> Dict[str, Any]:
        """Analyze policy and return summary."""
        logger.info("PolicyAnalyzerAgent starting analysis...")
        
        policy_input = state.policy_input
        
        # Prepare policy data for LLM
        policy_data = {
            "policy_number": policy_input.policy_number,
            "customer": {
                "name": policy_input.customer_profile.name,
                "zip_code": policy_input.customer_profile.zip_code,
                "net_worth": policy_input.customer_profile.net_worth,
                "home_value": policy_input.customer_profile.home_value,
                "additional_properties": policy_input.customer_profile.additional_properties,
                "has_watercraft": policy_input.customer_profile.has_watercraft,
                "has_high_value_items": policy_input.customer_profile.has_high_value_items,
            },
            "existing_coverages": [
                {
                    "type": cov.coverage_type.value,
                    "limit": cov.limit,
                    "deductible": cov.deductible,
                    "premium": cov.premium
                }
                for cov in policy_input.existing_coverages
            ]
        }
        
        # Get LLM analysis
        chain = self.prompt | self.llm
        response = chain.invoke({"policy_data": str(policy_data)})
        
        summary = response.content
        logger.info("PolicyAnalyzerAgent completed analysis")
        
        # Update state
        return {
            "policy_summary": summary,
            "existing_coverages_summary": {
                "count": len(policy_input.existing_coverages),
                "types": [cov.coverage_type.value for cov in policy_input.existing_coverages],
                "total_premium": sum(cov.premium or 0 for cov in policy_input.existing_coverages)
            }
        }
