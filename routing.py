def decide_route(extracted_fields, missing_fields):
    """
    Applies routing rules exactly in order.
    Returns (route_string, reasoning_string)
    """
    # 1. Mandatory field missing
    if missing_fields:
        return "Manual Review", f"Missing mandatory fields: {', '.join(missing_fields)}"

    # 2. Fraud keywords
    description = (extracted_fields.get('description') or "").lower()
    fraud_keywords = ["fraud", "staged", "inconsistent"]
    for word in fraud_keywords:
        if word in description:
            return "Investigation", f"Description contains suspicious keyword: '{word}'"

    # 3. Injury
    if extracted_fields.get('claimType') == "injury":
        return "Specialist Queue", "Claim involves injury"

    # 4. Low value
    damage = extracted_fields.get('estimatedDamage')
    if damage is not None and damage < 25000:
        val_str = f"${damage:,}"
        return "Fast-track", f"Estimated damage ({val_str}) is below $25,000 threshold"

    # 5. Default
    return "Manual Review", "Does not meet Fast-track criteria and no other flags detected"
