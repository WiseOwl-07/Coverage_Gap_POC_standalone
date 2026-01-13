"""Risk Context Agent - Evaluates customer risk exposure."""
from typing import Dict, Any, List
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import get_settings
from app.core.models import AgentState
from app.data.mock_risk_data import get_all_risk_data
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RiskContextAgent:
    """Agent that evaluates customer risk exposure based on profile and location."""
    
    def __init__(self):
        settings = get_settings()
        self.llm = ChatGroq(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            api_key=settings.groq_api_key
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an insurance risk assessment expert. Your job is to evaluate 
            a customer's risk exposure based on their profile and location data.
            
            Analyze the provided data and identify:
            1. Geographic risks (flood, earthquake, crime)
            2. Asset-based risks (property value, vehicles, net worth)
            3. Lifestyle risks (watercraft, rental properties, high-value items)
            4. Priority risk factors that need coverage attention
            
            Provide a clear, prioritized list of risk factors."""),
            ("user", """Customer Profile:
{customer_profile}

Location Risk Data:
{risk_data}

Identify and prioritize ALL significant risk factors.""")
        ])
    
    def analyze(self, state: AgentState) -> Dict[str, Any]:
        """Analyze risk context and return risk profile."""
        logger.info("RiskContextAgent starting analysis...")
        
        customer = state.policy_input.customer_profile
        
        # Get location-based risk data
        risk_data = get_all_risk_data(customer.zip_code)
        
        # Prepare data for LLM
        customer_data = {
            "name": customer.name,
            "zip_code": customer.zip_code,
            "net_worth": f"${customer.net_worth:,}" if customer.net_worth else "Not specified",
            "home_value": f"${customer.home_value:,}" if customer.home_value else "Not specified",
            "additional_properties": customer.additional_properties,
            "has_watercraft": customer.has_watercraft,
            "has_high_value_items": customer.has_high_value_items,
        }
        
        # Get LLM analysis
        chain = self.prompt | self.llm
        response = chain.invoke({
            "customer_profile": str(customer_data),
            "risk_data": str(risk_data)
        })
        
        # Extract risk factors from response
        risk_factors = self._extract_risk_factors(response.content, customer, risk_data)
        
        logger.info(f"RiskContextAgent identified {len(risk_factors)} risk factors")
        
        # Update state
        return {
            "risk_profile": {
                "location_data": risk_data,
                "analysis": response.content,
                "customer_profile": customer_data
            },
            "risk_factors": risk_factors
        }
    
    def _extract_risk_factors(self, llm_analysis: str, customer, risk_data: Dict) -> List[str]:
        """Extract structured risk factors from analysis."""
        factors = []
        
        # Add location-based risks
        flood_risk = risk_data.get("flood", {}).get("risk", "Low")
        if flood_risk in ["High", "Medium"]:
            factors.append(f"{flood_risk} flood risk - Zone {risk_data['flood'].get('zone')}")
        
        earthquake_risk = risk_data.get("earthquake", {}).get("risk", "Low")
        if earthquake_risk in ["Very High", "High", "Medium"]:
            factors.append(f"{earthquake_risk} earthquake risk - {risk_data['earthquake'].get('zone')} zone")
        
        crime_score = risk_data.get("crime_score", 5)
        if crime_score >= 7:
            factors.append(f"High crime area (score: {crime_score}/10)")
        
        # Add asset-based risks
        if customer.net_worth and customer.net_worth > 1_000_000:
            factors.append(f"High net worth (${customer.net_worth:,}) - liability exposure")
        
        if customer.home_value and customer.home_value > 500_000:
            factors.append(f"High-value property (${customer.home_value:,})")
        
        if customer.additional_properties and customer.additional_properties > 0:
            factors.append(f"Owns {customer.additional_properties} additional properties")
        
        if customer.has_watercraft:
            factors.append("Owns watercraft - specialized coverage needed")
        
        if customer.has_high_value_items:
            factors.append("Owns high-value items - enhanced coverage recommended")
        
        return factors
