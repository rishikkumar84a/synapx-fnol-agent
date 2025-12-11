import re

class Extractor:
    def __init__(self, text):
        self.text = text
        self.extracted_fields = {}
        self.missing_fields = []
        
    def extract_all(self):
        """Runs all extraction methods and returns the fields."""
        self.extract_carrier()
        self.extract_policy_number()
        self.extract_dates()
        self.extract_people()
        self.extract_location()
        self.extract_description()
        self.extract_vehicle_info()
        self.extract_monetary()
        self.extract_claim_type()
        
        # Others defaulting to logic or null if not found
        self.extracted_fields['attachments'] = self._detect_attachments()
        
        # Verify mandatory fields
        self._check_missing()
        
        return self.extracted_fields, self.missing_fields

    def _search(self, pattern, flags=re.IGNORECASE):
        """Helper to find regex matches."""
        match = re.search(pattern, self.text, flags)
        return match.group(1).strip() if match else None

    def extract_carrier(self):
        # Look for headers or specific carrier keywords
        # Common ones in ACORD forms
        self.extracted_fields['carrier'] = self._search(r"CARRIER\s*[:\-]?\s*([A-Za-z0-9\s\.,&]+?)(?:NAIC|POLICY|AGENCY|CODE|SUBCODE)") or \
                                           self._search(r"AGENCY\s*[:\-]?\s*([A-Za-z0-9\s\.,&]+)")

    def extract_policy_number(self):
        self.extracted_fields['policyNumber'] = self._search(r"POLICY NUMBER\s*[:\-]?\s*([A-Z0-9\-]+)")

    def extract_dates(self):
        # Effective dates often appear as EFF DATE: ... EXP DATE: ...
        eff = self._search(r"EFFECTIVE DATE\s*[:\-]?\s*(\d{2}/\d{2}/\d{4})")
        exp = self._search(r"EXPIRATION DATE\s*[:\-]?\s*(\d{2}/\d{2}/\d{4})")
        if eff and exp:
            self.extracted_fields['policyEffectiveDates'] = f"{eff} - {exp}"
        else:
            self.extracted_fields['policyEffectiveDates'] = None

        # Incident Date and Time (Date of Loss)
        self.extracted_fields['incidentDate'] = self._search(r"DATE OF LOSS\s*(?:AND TIME)?\s*[:\-]?\s*(\d{2}/\d{2}/\d{4})")
        self.extracted_fields['incidentTime'] = self._search(r"TIME OF LOSS\s*[:\-]?\s*(\d{1,2}:\d{2}\s*(?:AM|PM)?)") or \
                                                self._search(r"(\d{1,2}:\d{2}\s*(?:AM|PM))\s*(?:AM|PM)?", re.IGNORECASE) 
                                                # Fallback if time is near date

    def extract_people(self):
        # Insured / Policyholder
        self.extracted_fields['policyholderName'] = self._search(r"NAME OF INSURED\s*[:\-]?\s*([^\n]+)")
        
        # Claimant implies usually a third party if distinct, but valid to check "CLAIMANT" or "DRIVER"
        self.extracted_fields['claimantName'] = self._search(r"CLAIMANT\s*[:\-]?\s*([^\n]+)") or \
                                                self._search(r"DRIVER'S NAME\s*[:\-]?\s*([^\n]+)")
        
        # Contact info usually nearby
        self.extracted_fields['claimantContact'] = self._search(r"PRIMARY PHONE\s*[:#]?\s*([\d\-\(\)\s]+)")

        # Third parties - rudimentary list extraction
        self.extracted_fields['thirdParties'] = [] # Default empty, regex for lists is hard on unstructured OCR

    def extract_location(self):
        # Location of loss line
        self.extracted_fields['incidentLocation'] = self._search(r"LOCATION OF LOSS\s*[:\-]?\s*([^\n]+)")

    def extract_description(self):
        # Often a large box "DESCRIPTION OF ACCIDENT"
        desc = self._search(r"DESCRIPTION OF ACCIDENT\s*[:\-]?\s*(.*?)(?:AUTHORITY|REPORTED TO|VEHICLE|WITNESSES|$)", re.DOTALL)
        if desc:
            self.extracted_fields['description'] = desc.replace('\n', ' ').strip()
        else:
            self.extracted_fields['description'] = None

    def extract_vehicle_info(self):
        # Scan for Make, Model, VIN
        self.extracted_fields['make'] = self._search(r"MAKE\s*[:\-]?\s*([A-Za-z]+)")
        self.extracted_fields['model'] = self._search(r"MODEL\s*[:\-]?\s*([A-Za-z0-9]+)")
        self.extracted_fields['year'] = self._search(r"YEAR\s*[:\-]?\s*(\d{4})")
        self.extracted_fields['vin'] = self._search(r"V\.?I\.?N\.?\s*[:\-#]?\s*([A-Z0-9]{17})")
        self.extracted_fields['plateNumber'] = self._search(r"PLATE NUMBER\s*[:\-]?\s*([A-Z0-9]+)")
        
        # Asset type is usually inferred from form title or "VEHICLE" section, defaulting "Automobile" if checks pass
        if "AUTOMOBILE" or "VEHICLE" in self.text.upper():
            self.extracted_fields['assetType'] = "Automobile"
        else:
            self.extracted_fields['assetType'] = None

    def extract_monetary(self):
        # Look for currency symbols
        est = self._search(r"ESTIMATED AMOUNT\s*[:\-]?\s*\$?([\d,]+)")
        self.extracted_fields['estimatedDamage'] = int(est.replace(',', '')) if est else None
        
        # Initial estimate often same as estimated damage in simple forms
        self.extracted_fields['initialEstimate'] = self.extracted_fields['estimatedDamage']
        
        self.extracted_fields['damageDescription'] = self._search(r"DESCRIBE DAMAGE\s*[:\-]?\s*([^\n]+)")

    def extract_claim_type(self):
        # Logic to infer claim type
        if "INJURY" in self.text.upper() or "MEDIC" in self.text.upper():
            self.extracted_fields['claimType'] = "injury"
        elif "THEFT" in self.text.upper():
            self.extracted_fields['claimType'] = "theft"
        else:
            self.extracted_fields['claimType'] = "property_damage" # Default

    def _detect_attachments(self):
        # logic: pages > 1 means attachments?
        # For now return empty list usually, this is hard without image analysis
        return []

    def _check_missing(self):
        MANDATORY = [
            "policyNumber", "policyholderName", "incidentDate", 
            "incidentLocation", "claimantName", "assetType", "initialEstimate"
        ]
        for field in MANDATORY:
            if not self.extracted_fields.get(field):
                self.missing_fields.append(field)
