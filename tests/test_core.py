import pytest
from extractor import Extractor
from routing import decide_route

# --- CORE MOCK DATA TESTS ---

def test_extract_core_fields():
    mock_text = """
    AGENCY: My Insurance Co
    POLICY NUMBER: 123-ABC-456
    NAME OF INSURED: John Doe
    DATE OF LOSS: 01/15/2025
    LOCATION OF LOSS: 123 Main St, Springfield
    ESTIMATED AMOUNT: $5,000
    DESCRIPTION OF ACCIDENT:
    Rear ended by another vehicle at stop light.
    VEHICLE
    MAKE: Toyota
    MODEL: Camry
    """
    extractor = Extractor(mock_text)
    fields, _ = extractor.extract_all()
    
    assert fields['policyNumber'] == "123-ABC-456"
    assert fields['policyholderName'] == "John Doe"
    assert fields['estimatedDamage'] == 5000
    assert fields['make'] == "Toyota"
    assert fields['model'] == "Camry"

def test_missing_fields():
    # Missing Date and Location
    mock_text = """
    POLICY NUMBER: 123
    NAME OF INSURED: Jane Doe
    ESTIMATED AMOUNT: 100
    """
    extractor = Extractor(mock_text)
    fields, missing = extractor.extract_all()
    
    assert "incidentDate" in missing
    assert "incidentLocation" in missing
    assert "policyNumber" not in missing

def test_routing_investigation():
    fields = {"description": "The confusing events seemed inconsistent with the damage."}
    missing = []
    route, reasoning = decide_route(fields, missing)
    assert route == "Investigation"
    assert "inconsistent" in reasoning

def test_routing_fasttrack():
    fields = {
        "description": "Minor scratch",
        "estimatedDamage": 2000,
        "claimType": "property_damage"
    }
    missing = []
    route, reasoning = decide_route(fields, missing)
    assert route == "Fast-track"
    assert "below $25,000" in reasoning

def test_routing_specialist():
    fields = {
        "description": "Ouch",
        "estimatedDamage": 50000,
        "claimType": "injury"
    }
    missing = []
    route, reasoning = decide_route(fields, missing)
    assert route == "Specialist Queue"

def test_routing_manual_review_missing():
    fields = {}
    missing = ["policyNumber"]
    route, reasoning = decide_route(fields, missing)
    assert route == "Manual Review"
    assert "Missing mandatory" in reasoning
