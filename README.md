# Autonomous Insurance Claims Processing Agent

## Overview
This agent processes images of First Notice of Loss (FNOL) documents (specifically ACORD forms) to automate data extraction and routing. It uses Optical Character Recognition (OCR) to convert images to text and applies regex-based parsing to structure the data.

## Features
- **OCR extraction**: Uses `pytesseract` to read text from multiple image pages.
- **Rule-based Extraction**: Identifies key insurance fields like Policy Number, Incident Date, Drivers, and Vehicles.
- **Validation**: Automatically detects missing mandatory fields.
- **Smart Routing**: Routes claims to Fast-track, Investigation, Specialist, or Manual Review based on strict business logic.

## Project Structure
```
synapx-fnol-agent/
├── main.py              # CLI Entry point
├── extractor.py         # Regex extraction patterns and logic
├── routing.py           # Business rules for claim routing
├── utils.py             # Image loading and OCR helper functions
├── sample_input/        # Sample FNOL images
├── output/              # Generated JSON output
├── tests/               # Unit test suite
└── requirements.txt     # Dependencies
```

## How to Run
1. **Prerequisites**: 
   - Python 3.x
   - Tesseract-OCR installed on your system.
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Execute**:
   ```bash
   python main.py --images sample_input/page1.jpg sample_input/page2.jpg --out output.json
   ```

## Extraction Strategy
The agent uses Python's `re` module to find patterns.
- **Policy Number**: Looks for "POLICY NUMBER" followed by alphanumerics.
- **Dates**: Matches `MM/DD/YYYY` formats near "DATE OF LOSS".
- **Money**: Matches `$` symbols or "ESTIMATED AMOUNT".

## Routing Logic
1. **Manual Review**: If any mandatory field (`policyNumber`, `incidentLocation`, etc.) is missing.
2. **Investigation**: If description contains "fraud", "staged", or "inconsistent".
3. **Specialist Queue**: If `claimType` is "injury".
4. **Fast-track**: If `estimatedDamage` < $25,000.
5. **Manual Review**: Default fallback.

## Developer Notes
- **Accuracy**: Dependent on image quality and OCR fidelity.
- **Scalability**: Can be extended with named-entity recognition (NER) models for better accuracy on unstructured text.
