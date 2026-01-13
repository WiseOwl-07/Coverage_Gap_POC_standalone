"""Pydantic models for the application."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class CoverageType(str, Enum):
    """Types of insurance coverage."""
    AUTO = "auto"
    HOME = "home"
    UMBRELLA = "umbrella"
    FLOOD = "flood"
    EARTHQUAKE = "earthquake"
    JEWELRY = "jewelry"
    WATERCRAFT = "watercraft"
    RENTERS = "renters"


class RiskSeverity(str, Enum):
    """Risk severity levels."""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class Coverage(BaseModel):
    """Existing coverage details."""
    coverage_type: CoverageType
    limit: Optional[int] = None
    deductible: Optional[int] = None
    premium: Optional[float] = None
    details: Optional[Dict[str, Any]] = None


class CustomerProfile(BaseModel):
    """Customer profile and risk factors."""
    name: str
    zip_code: str
    net_worth: Optional[int] = None
    home_value: Optional[int] = None
    vehicles: Optional[List[Dict[str, Any]]] = None
    additional_properties: Optional[int] = 0
    has_watercraft: bool = False
    has_high_value_items: bool = False


class PolicyInput(BaseModel):
    """Input policy data for analysis."""
    policy_number: str
    customer_profile: CustomerProfile
    existing_coverages: List[Coverage]


class CoverageGap(BaseModel):
    """Identified coverage gap."""
    gap_type: CoverageType
    severity: RiskSeverity
    title: str
    explanation: str = Field(..., description="Plain-English explanation of why this gap matters")
    recommendation: str = Field(..., description="Specific coverage recommendation")
    estimated_annual_premium: Optional[float] = Field(None, description="Estimated annual premium for recommended coverage")
    risk_factors: List[str] = Field(default_factory=list, description="Specific risk factors identified")


class AnalysisResult(BaseModel):
    """Analysis result with coverage gaps."""
    policy_number: str
    customer_name: str
    total_gaps_found: int
    coverage_gaps: List[CoverageGap]
    total_estimated_premium_impact: float
    analysis_summary: str = Field(..., description="Overall summary of the analysis")
    

class AgentState(BaseModel):
    """State passed between agents in the LangGraph workflow."""
    policy_input: PolicyInput
    
    # Agent outputs
    policy_summary: Optional[str] = None
    existing_coverages_summary: Optional[Dict[str, Any]] = None
    risk_profile: Optional[Dict[str, Any]] = None
    risk_factors: Optional[List[str]] = None
    underwriting_recommendations: Optional[List[Dict[str, Any]]] = None
    coverage_gaps: Optional[List[CoverageGap]] = None
    
    # Final result
    analysis_result: Optional[AnalysisResult] = None
    
    class Config:
        arbitrary_types_allowed = True
