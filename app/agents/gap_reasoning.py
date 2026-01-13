"""Gap Reasoning Agent - Synthesizes findings and generates explainable recommendations."""
from typing import Dict, Any, List
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import get_settings
from app.core.models import AgentState, CoverageGap, CoverageType, RiskSeverity
from app.utils.logger import get_logger

logger = get_logger(__name__)


class GapReasoningAgent:
    """Agent that synthesizes findings and creates explainable coverage gap recommendations."""
    
    def __init__(self):
        settings = get_settings()
        self.llm = ChatGroq(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            api_key=settings.groq_api_key
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an insurance advisor expert at explaining coverage gaps to customers.
            Your job is to take technical underwriting recommendations and create clear, 
            business-friendly explanations that customers can understand.
            
            For each coverage gap:
            1. Write a clear, compelling title (5-8 words)
            2. Explain WHY this gap matters in plain English (2-3 sentences)
            3. Provide a specific recommendation (1-2 sentences)
            4. Emphasize the customer benefit and risk mitigation
            
            Be empathetic, professional, and avoid insurance jargon. Focus on protecting 
            the customer's financial wellbeing."""),
            ("user", """Customer Profile:
{customer_profile}

Risk Factors Identified:
{risk_factors}

Underwriting Recommendations:
{recommendations}

For each recommendation, create a clear, customer-friendly explanation of:
- Why this coverage gap matters
- What specific coverage is recommended
- How it protects the customer

Format each gap clearly and separately.""")
        ])
    
    def analyze(self, state: AgentState) -> Dict[str, Any]:
        """Generate coverage gaps with explanations."""
        logger.info("GapReasoningAgent starting analysis...")
        
        customer = state.policy_input.customer_profile
        risk_factors = state.risk_factors or []
        recommendations = state.underwriting_recommendations or []
        
        if not recommendations:
            logger.info("No recommendations found, no gaps to report")
            return {"coverage_gaps": []}
        
        # Prepare data for LLM
        customer_data = {
            "name": customer.name,
            "zip_code": customer.zip_code,
            "net_worth": f"${customer.net_worth:,}" if customer.net_worth else "Not specified",
            "home_value": f"${customer.home_value:,}" if customer.home_value else "Not specified",
        }
        
        # Get LLM explanations
        chain = self.prompt | self.llm
        response = chain.invoke({
            "customer_profile": str(customer_data),
            "risk_factors": "\n".join(f"- {rf}" for rf in risk_factors),
            "recommendations": str(recommendations)
        })
        
        # Create structured coverage gaps
        coverage_gaps = self._create_coverage_gaps(recommendations, response.content)
        
        logger.info(f"GapReasoningAgent created {len(coverage_gaps)} coverage gaps")
        
        # Update state
        return {
            "coverage_gaps": coverage_gaps
        }
    
    def _create_coverage_gaps(self, recommendations: List[Dict], 
                             llm_explanations: str) -> List[CoverageGap]:
        """Create structured coverage gap objects."""
        gaps = []
        
        # Map each recommendation to a coverage gap
        for rec in recommendations:
            coverage_type_str = rec.get("coverage_type", "").lower()
            
            # Map to CoverageType enum
            try:
                coverage_type = CoverageType(coverage_type_str)
            except ValueError:
                logger.warning(f"Unknown coverage type: {coverage_type_str}")
                continue
            
            # Determine severity
            severity = rec.get("severity", RiskSeverity.MEDIUM)
            if isinstance(severity, str):
                try:
                    severity = RiskSeverity(severity)
                except ValueError:
                    severity = RiskSeverity.MEDIUM
            
            # Create gap
            gap = CoverageGap(
                gap_type=coverage_type,
                severity=severity,
                title=self._generate_title(coverage_type, rec),
                explanation=self._extract_explanation(coverage_type_str, llm_explanations, rec),
                recommendation=self._generate_recommendation(coverage_type, rec),
                estimated_annual_premium=rec.get("estimated_premium"),
                risk_factors=rec.get("risk_factors", [])
            )
            gaps.append(gap)
        
        return gaps
    
    def _generate_title(self, coverage_type: CoverageType, rec: Dict) -> str:
        """Generate a clear title for the gap."""
        titles = {
            CoverageType.UMBRELLA: "Missing Umbrella Liability Protection",
            CoverageType.FLOOD: "Flood Insurance Coverage Gap",
            CoverageType.EARTHQUAKE: "Earthquake Coverage Not Included",
            CoverageType.WATERCRAFT: "Watercraft Liability Exposure",
            CoverageType.JEWELRY: "High-Value Items Underinsured",
        }
        return titles.get(coverage_type, f"Missing {coverage_type.value.title()} Coverage")
    
    def _extract_explanation(self, coverage_type: str, llm_text: str, rec: Dict) -> str:
        """Extract or generate explanation for the gap."""
        # Try to extract from LLM response
        # For now, use a template-based approach with the recommendation reason
        reason = rec.get("reason", "Coverage gap identified")
        
        templates = {
            "umbrella": "Your current liability coverage may not adequately protect your assets. {reason}. Without umbrella coverage, you could be personally liable for damages exceeding your policy limits.",
            "flood": "Standard homeowner policies don't cover flood damage. {reason}. Flood insurance is essential to protect your property investment.",
            "earthquake": "Your home insurance policy excludes earthquake damage. {reason}. Earthquake insurance protects your home's structure and contents from seismic events.",
        }
        
        template = templates.get(coverage_type, "{reason}. This coverage gap could leave you financially exposed.")
        return template.format(reason=reason)
    
    def _generate_recommendation(self, coverage_type: CoverageType, rec: Dict) -> str:
        """Generate specific recommendation."""
        limit = rec.get("recommended_limit")
        premium = rec.get("estimated_premium")
        
        if limit and premium:
            return f"We recommend adding {coverage_type.value} coverage with a ${limit:,} limit. Estimated annual premium: ${premium:,.2f}."
        elif limit:
            return f"We recommend adding {coverage_type.value} coverage with a ${limit:,} limit."
        else:
            return f"We recommend adding {coverage_type.value} coverage to your policy."
