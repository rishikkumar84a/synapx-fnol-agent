import argparse
import json
import os
import sys
from utils import load_image, run_ocr
from extractor import Extractor
from routing import decide_route

def main():
    parser = argparse.ArgumentParser(description="Autonomous Insurance Claims Processing Agent")
    parser.add_argument('--images', nargs='+', required=True, help="Path to input image(s)")
    parser.add_argument('--out', required=True, help="Path to output JSON file")
    
    args = parser.parse_args()
    
    # 1. Load Images
    images = []
    print(f"Loading {len(args.images)} images...")
    for img_path in args.images:
        img = load_image(img_path)
        if img:
            images.append(img)
        else:
            print(f"Failed to load {img_path}")
            sys.exit(1)

    # 2. OCR
    print("Running OCR...")
    raw_text = run_ocr(images)
    print("OCR Complete.")
    # Debug: print(raw_text)

    # 3. Extract
    print("Extracting fields...")
    extractor = Extractor(raw_text)
    extracted_fields, missing_fields = extractor.extract_all()
    
    # 4. Route
    print("Applying routing rules...")
    route, reasoning = decide_route(extracted_fields, missing_fields)
    
    # 5. Output
    output_data = {
        "extractedFields": extracted_fields,
        "missingFields": missing_fields,
        "recommendedRoute": route,
        "reasoning": reasoning
    }
    
    try:
        with open(args.out, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"Success! Output written to {args.out}")
        print(json.dumps(output_data, indent=2))
    except Exception as e:
        print(f"Error writing output: {e}")

if __name__ == "__main__":
    main()
