"""Mock risk data for demonstration purposes."""
from typing import Dict, Any


# Flood risk zones (FEMA-style zones)
FLOOD_ZONES = {
    # High-risk areas (coastal and river zones)
    "33139": {"zone": "AE", "risk": "High", "region": "Miami, FL"},
    "70112": {"zone": "AE", "risk": "High", "region": "New Orleans, LA"},
    "10002": {"zone": "A", "risk": "High", "region": "New York, NY"},
    "94102": {"zone": "X (protected)", "risk": "Medium", "region": "San Francisco, CA"},
    
    # Moderate risk
    "77002": {"zone": "X (500-year)", "risk": "Medium", "region": "Houston, TX"},
    "02108": {"zone": "X (protected)", "risk": "Medium", "region": "Boston, MA"},
    
    # Low risk
    "85001": {"zone": "X", "risk": "Low", "region": "Phoenix, AZ"},
    "80202": {"zone": "X", "risk": "Low", "region": "Denver, CO"},
    "60601": {"zone": "X", "risk": "Low", "region": "Chicago, IL"},
    "30303": {"zone": "X", "risk": "Low", "region": "Atlanta, GA"},
}


# Earthquake risk zones
EARTHQUAKE_ZONES = {
    "94102": {"risk": "Very High", "region": "San Francisco, CA", "zone": "Alquist-Priolo"},
    "90001": {"risk": "Very High", "region": "Los Angeles, CA", "zone": "Alquist-Priolo"},
    "98101": {"risk": "High", "region": "Seattle, WA", "zone": "Cascadia"},
    "97201": {"risk": "High", "region": "Portland, OR", "zone": "Cascadia"},
    
    # Moderate
    "84101": {"risk": "Medium", "region": "Salt Lake City, UT", "zone": "Wasatch"},
    "89101": {"risk": "Medium", "region": "Las Vegas, NV", "zone": "Basin and Range"},
    
    # Low risk areas
    "33139": {"risk": "Low", "region": "Miami, FL", "zone": "Stable"},
    "60601": {"risk": "Low", "region": "Chicago, IL", "zone": "Stable"},
    "10002": {"risk": "Low", "region": "New York, NY", "zone": "Stable"},
}


# Crime rate scores (1-10, 10 = highest crime)
CRIME_SCORES = {
    "10002": 7,  # Manhattan
    "90001": 8,  # South LA
    "60601": 6,  # Downtown Chicago
    "33139": 5,  # Miami Beach
    "94102": 7,  # SF Tenderloin
    "85001": 6,  # Phoenix downtown
    "30303": 7,  # Downtown Atlanta
    "02108": 4,  # Boston Beacon Hill
    "98101": 5,  # Seattle downtown
    "80202": 5,  # Denver downtown
}


def get_flood_risk(zip_code: str) -> Dict[str, Any]:
    """Get flood risk data for a ZIP code."""
    return FLOOD_ZONES.get(zip_code, {"zone": "X", "risk": "Low", "region": "Unknown"})


def get_earthquake_risk(zip_code: str) -> Dict[str, Any]:
    """Get earthquake risk data for a ZIP code."""
    return EARTHQUAKE_ZONES.get(zip_code, {"risk": "Low", "region": "Unknown", "zone": "Stable"})


def get_crime_score(zip_code: str) -> int:
    """Get crime score for a ZIP code (1-10)."""
    return CRIME_SCORES.get(zip_code, 5)  # Default to medium


def get_all_risk_data(zip_code: str) -> Dict[str, Any]:
    """Get comprehensive risk data for a ZIP code."""
    return {
        "zip_code": zip_code,
        "flood": get_flood_risk(zip_code),
        "earthquake": get_earthquake_risk(zip_code),
        "crime_score": get_crime_score(zip_code),
    }
