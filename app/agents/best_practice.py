"""Best Practice Agent - Applies underwriting rules and industry best practices."""
from typing import Dict, Any, List
from app.core.models import AgentState
from app.data.underwriting_rules import get_applicable_rules
from app.utils.logger import get_logger

logger = get_logger(__name__)


class BestPracticeAgent:
    """Agent that applies underwriting rules and best practices."""
    
    def analyze(self, state: AgentState) -> Dict[str, Any]:
        """Apply underwriting rules and return recommendations."""
        logger.info("BestPracticeAgent starting analysis...")
        
        customer = state.policy_input.customer_profile
        existing_coverages = state.policy_input.existing_coverages
        risk_profile = state.risk_profile
        
        # Convert to dict format for rules engine
        customer_dict = {
            "name": customer.name,
            "zip_code": customer.zip_code,
            "net_worth": customer.net_worth,
            "home_value": customer.home_value,
            "additional_properties": customer.additional_properties,
            "has_watercraft": customer.has_watercraft,
            "has_high_value_items": customer.has_high_value_items,
        }
        
        coverages_dict = [
            {
                "coverage_type": cov.coverage_type.value,
                "limit": cov.limit,
                "deductible": cov.deductible,
                "premium": cov.premium
            }
            for cov in existing_coverages
        ]
        
        # Get location risk data from risk_profile
        risk_data = risk_profile.get("location_data", {})
        
        # Apply underwriting rules
        applicable_rules = get_applicable_rules(customer_dict, coverages_dict, risk_data)
        
        # Get recommendations from each rule
        recommendations = []
        for rule in applicable_rules:
            rec = rule.get_recommendation(customer_dict, risk_data)
            rec["rule_id"] = rule.rule_id
            rec["description"] = rule.description
            recommendations.append(rec)
        
        logger.info(f"BestPracticeAgent generated {len(recommendations)} recommendations")
        
        # Update state
        return {
            "underwriting_recommendations": recommendations
        }
