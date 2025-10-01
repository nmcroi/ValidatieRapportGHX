#!/usr/bin/env python3
"""
Test chemical field detection function
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from validator.template_context import detect_chemical_fields_in_template

def test_chemical_detection():
    """Test chemical detection with legacy_small.xlsx"""
    
    print("=== TESTING CHEMICAL FIELD DETECTION ===\n")
    
    file_path = "test/testinput/legacy_small.xlsx"
    
    try:
        has_chemicals = detect_chemical_fields_in_template(file_path)
        print(f"File: {file_path}")
        print(f"Chemical fields detected: {'YES' if has_chemicals else 'NO'}")
        
        if has_chemicals:
            print("✅ Chemical detection working correctly!")
            print("This means ADR Gevarenklasse should be visible with has_chemicals=True")
        else:
            print("❌ Chemical detection failed to detect chemical fields")
            print("This means the detection logic needs improvement")
        
    except Exception as e:
        print(f"❌ Error during chemical detection: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chemical_detection()