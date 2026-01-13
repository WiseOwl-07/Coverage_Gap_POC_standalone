"""Policy parser for JSON and PDF files."""
import json
from typing import Dict, Any
from pathlib import Path
from app.core.models import PolicyInput, CustomerProfile, Coverage, CoverageType
from app.utils.logger import get_logger

logger = get_logger(__name__)


def parse_json_policy(file_content: str) -> PolicyInput:
    """Parse JSON policy data into PolicyInput model."""
    try:
        data = json.loads(file_content)
        
        # Parse customer profile
        customer_data = data.get("customer_profile", {})
        customer_profile = CustomerProfile(**customer_data)
        
        # Parse existing coverages
        coverages_data = data.get("existing_coverages", [])
        existing_coverages = []
        for cov_data in coverages_data:
            # Ensure coverage_type is a valid enum
            cov_type_str = cov_data.get("coverage_type", "").lower()
            if cov_type_str in [e.value for e in CoverageType]:
                cov_data["coverage_type"] = cov_type_str
                existing_coverages.append(Coverage(**cov_data))
        
        policy_input = PolicyInput(
            policy_number=data.get("policy_number", "UNKNOWN"),
            customer_profile=customer_profile,
            existing_coverages=existing_coverages
        )
        
        logger.info(f"Successfully parsed policy {policy_input.policy_number}")
        return policy_input
        
    except Exception as e:
        logger.error(f"Error parsing JSON policy: {e}")
        raise ValueError(f"Invalid policy JSON format: {e}")


def parse_policy_file(file_path: str = None, file_content: str = None) -> PolicyInput:
    """Parse policy file (JSON or PDF) and return PolicyInput."""
    if file_content:
        # Assume JSON if content is provided directly
        return parse_json_policy(file_content)
    
    if file_path:
        path = Path(file_path)
        if path.suffix.lower() == '.json':
            with open(path, 'r') as f:
                return parse_json_policy(f.read())
        elif path.suffix.lower() == '.pdf':
            # TODO: Implement PDF parsing with PyPDF2
            raise NotImplementedError("PDF parsing not yet implemented")
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")
    
    raise ValueError("Either file_path or file_content must be provided")
