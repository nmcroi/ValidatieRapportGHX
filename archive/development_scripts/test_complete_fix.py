#!/usr/bin/env python3
"""
Test de complete fix voor ADR Gevarenklasse visibility
"""

import sys
import os
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Enable logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_complete_validation():
    """Test de volledige validation pipeline met legacy_small.xlsx"""
    
    print("=== TESTING COMPLETE VALIDATION PIPELINE ===\n")
    
    try:
        from validator.price_tool import validate_pricelist
        
        # Test paths
        input_file = "test/testinput/legacy_small.xlsx"
        mapping_json = "header_mapping.json"
        validation_json = "field_validation_v20.json"
        
        print(f"Testing validation with:")
        print(f"  Input: {input_file}")
        print(f"  Mapping: {mapping_json}")
        print(f"  Validation: {validation_json}")
        print()
        
        # Run validation
        print("Starting validation...")
        result_file = validate_pricelist(
            input_excel_path=input_file,
            mapping_json_path=mapping_json,
            validation_json_path=validation_json,
            original_input_filename="legacy_small.xlsx"
        )
        
        if result_file:
            print(f"✅ Validation completed successfully!")
            print(f"Result file: {result_file}")
            
            # Check if ADR Gevarenklasse was processed correctly
            # We can check logs for chemical detection
            print("\nChecking if chemical detection worked...")
            print("Look for log messages about 'Chemical fields gedetecteerd' above")
            
        else:
            print("❌ Validation failed or returned no result")
            
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_validation()