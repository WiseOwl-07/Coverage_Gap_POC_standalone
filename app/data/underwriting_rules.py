"""Underwriting rules and premium calculations."""
from typing import Dict, Any, List
from app.core.models import CoverageType, RiskSeverity


# Umbrella policy thresholds
UMBRELLA_NET_WORTH_THRESHOLD = 1_000_000
UMBRELLA_MIN_PREMIUM = 150
UMBRELLA_PREMIUM_RATE = 0.0002  # 0.02% of net worth


# Flood insurance
FLOOD_HIGH_RISK_PREMIUM = 2500
FLOOD_MEDIUM_RISK_PREMIUM = 800
FLOOD_LOW_RISK_PREMIUM = 400


# Earthquake insurance
EARTHQUAKE_VERY_HIGH_PREMIUM = 3000
EARTHQUAKE_HIGH_PREMIUM = 1800
EARTHQUAKE_MEDIUM_PREMIUM = 600


# Jewelry and valuable items insurance
JEWELRY_BASE_PREMIUM = 200
JEWELRY_COVERAGE_LIMIT = 50_000  # Default coverage limit


# Home insurance coverage-to-value ratio
HOME_COVERAGE_TO_VALUE_MIN = 0.8  # 80% minimum


# Liability limits
LIABILITY_MINIMUM = 300_000
LIABILITY_RECOMMENDED_HIGH_NETWORTH = 500_000


class UnderwritingRule:
    """Base underwriting rule."""
    
    def __init__(self, rule_id: str, coverage_type: CoverageType, 
                 severity: RiskSeverity, description: str):
        self.rule_id = rule_id
        self.coverage_type = coverage_type
        self.severity = severity
        self.description = description
    
    def applies(self, customer_profile: Dict[str, Any], 
                existing_coverages: List[Dict[str, Any]],
                risk_data: Dict[str, Any]) -> bool:
        """Check if this rule applies to the customer."""
        raise NotImplementedError
    
    def get_recommendation(self, customer_profile: Dict[str, Any], 
                          risk_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get coverage recommendation and premium estimate."""
        raise NotImplementedError


class UmbrellaRule(UnderwritingRule):
    """Umbrella policy rule for high net worth individuals."""
    
    def __init__(self):
        super().__init__(
            rule_id="UMBRELLA_001",
            coverage_type=CoverageType.UMBRELLA,
            severity=RiskSeverity.HIGH,
            description="Umbrella policy recommended for individuals with net worth over $1M"
        )
    
    def applies(self, customer_profile: Dict[str, Any], 
                existing_coverages: List[Dict[str, Any]],
                risk_data: Dict[str, Any]) -> bool:
        """Check if umbrella policy is needed."""
        net_worth = customer_profile.get("net_worth", 0)
        has_umbrella = any(c.get("coverage_type") == "umbrella" for c in existing_coverages)
        return net_worth >= UMBRELLA_NET_WORTH_THRESHOLD and not has_umbrella
    
    def get_recommendation(self, customer_profile: Dict[str, Any], 
                          risk_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get umbrella policy recommendation."""
        net_worth = customer_profile.get("net_worth", 0)
        premium = max(UMBRELLA_MIN_PREMIUM, net_worth * UMBRELLA_PREMIUM_RATE)
        
        return {
            "coverage_type": "umbrella",
            "recommended_limit": min(net_worth, 5_000_000),  # Cap at $5M
            "estimated_premium": round(premium, 2),
            "reason": f"Net worth of ${net_worth:,} requires additional liability protection",
            "risk_factors": ["High net worth", "Asset protection needed"]
        }


class FloodRule(UnderwritingRule):
    """Flood insurance rule based on location."""
    
    def __init__(self):
        super().__init__(
            rule_id="FLOOD_001",
            coverage_type=CoverageType.FLOOD,
            severity=RiskSeverity.HIGH,
            description="Flood insurance required for properties in high-risk flood zones"
        )
    
    def applies(self, customer_profile: Dict[str, Any], 
                existing_coverages: List[Dict[str, Any]],
                risk_data: Dict[str, Any]) -> bool:
        """Check if flood insurance is needed."""
        has_flood = any(c.get("coverage_type") == "flood" for c in existing_coverages)
        flood_risk = risk_data.get("flood", {}).get("risk", "Low")
        return not has_flood and flood_risk in ["High", "Medium"]
    
    def get_recommendation(self, customer_profile: Dict[str, Any], 
                          risk_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get flood insurance recommendation."""
        flood_data = risk_data.get("flood", {})
        risk = flood_data.get("risk", "Low")
        zone = flood_data.get("zone", "X")
        region = flood_data.get("region", "Unknown")
        
        if risk == "High":
            premium = FLOOD_HIGH_RISK_PREMIUM
            severity = RiskSeverity.HIGH
        elif risk == "Medium":
            premium = FLOOD_MEDIUM_RISK_PREMIUM
            severity = RiskSeverity.MEDIUM
        else:
            premium = FLOOD_LOW_RISK_PREMIUM
            severity = RiskSeverity.LOW
        
        return {
            "coverage_type": "flood",
            "recommended_limit": 250_000,
            "estimated_premium": premium,
            "reason": f"Property located in FEMA flood zone {zone} ({region})",
            "risk_factors": [f"Flood zone {zone}", f"{risk} flood risk"],
            "severity": severity
        }


class EarthquakeRule(UnderwritingRule):
    """Earthquake insurance rule based on location."""
    
    def __init__(self):
        super().__init__(
            rule_id="EARTHQUAKE_001",
            coverage_type=CoverageType.EARTHQUAKE,
            severity=RiskSeverity.MEDIUM,
            description="Earthquake insurance recommended for properties in seismic zones"
        )
    
    def applies(self, customer_profile: Dict[str, Any], 
                existing_coverages: List[Dict[str, Any]],
                risk_data: Dict[str, Any]) -> bool:
        """Check if earthquake insurance is needed."""
        has_earthquake = any(c.get("coverage_type") == "earthquake" for c in existing_coverages)
        eq_risk = risk_data.get("earthquake", {}).get("risk", "Low")
        return not has_earthquake and eq_risk in ["Very High", "High", "Medium"]
    
    def get_recommendation(self, customer_profile: Dict[str, Any], 
                          risk_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get earthquake insurance recommendation."""
        eq_data = risk_data.get("earthquake", {})
        risk = eq_data.get("risk", "Low")
        zone = eq_data.get("zone", "Stable")
        region = eq_data.get("region", "Unknown")
        
        if risk == "Very High":
            premium = EARTHQUAKE_VERY_HIGH_PREMIUM
            severity = RiskSeverity.HIGH
        elif risk == "High":
            premium = EARTHQUAKE_HIGH_PREMIUM
            severity = RiskSeverity.HIGH
        else:
            premium = EARTHQUAKE_MEDIUM_PREMIUM
            severity = RiskSeverity.MEDIUM
        
        return {
            "coverage_type": "earthquake",
            "recommended_limit": customer_profile.get("home_value", 300_000),
            "estimated_premium": premium,
            "reason": f"Property located in {zone} seismic zone ({region})",
            "risk_factors": [f"{risk} earthquake risk", f"{zone} zone"],
            "severity": severity
        }


class JewelryRule(UnderwritingRule):
    """Jewelry and valuable items insurance rule."""
    
    def __init__(self):
        super().__init__(
            rule_id="JEWELRY_001",
            coverage_type=CoverageType.JEWELRY,
            severity=RiskSeverity.MEDIUM,
            description="Jewelry and valuable items coverage recommended for customers with high-value possessions"
        )
    
    def applies(self, customer_profile: Dict[str, Any], 
                existing_coverages: List[Dict[str, Any]],
                risk_data: Dict[str, Any]) -> bool:
        """Check if jewelry/valuable items insurance is needed."""
        has_jewelry = any(c.get("coverage_type") == "jewelry" for c in existing_coverages)
        has_high_value_items = customer_profile.get("has_high_value_items", False)
        return not has_jewelry and has_high_value_items
    
    def get_recommendation(self, customer_profile: Dict[str, Any], 
                          risk_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get jewelry/valuable items insurance recommendation."""
        return {
            "coverage_type": "jewelry",
            "recommended_limit": JEWELRY_COVERAGE_LIMIT,
            "estimated_premium": JEWELRY_BASE_PREMIUM,
            "reason": "Customer owns high-value items (jewelry, art, collectibles, etc.)",
            "risk_factors": ["High-value items owned", "Standard home policy limits insufficient"],
            "severity": RiskSeverity.MEDIUM
        }


# All underwriting rules
ALL_RULES = [
    UmbrellaRule(),
    FloodRule(),
    EarthquakeRule(),
    JewelryRule(),
]


def get_applicable_rules(customer_profile: Dict[str, Any],
                        existing_coverages: List[Dict[str, Any]],
                        risk_data: Dict[str, Any]) -> List[UnderwritingRule]:
    """Get all applicable underwriting rules for a customer."""
    applicable = []
    for rule in ALL_RULES:
        if rule.applies(customer_profile, existing_coverages, risk_data):
            applicable.append(rule)
    return applicable
