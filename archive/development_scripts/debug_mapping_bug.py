#!/usr/bin/env python3
"""
Debugging script om ADR Gevarenklasse mapping bug te diagnosticeren
"""

import pandas as pd
import json
import logging
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from validator.price_tool import map_headers, clean_column_name

def debug_adr_mapping():
    """Test ADR Gevarenklasse mapping specifiek"""
    
    print("=== ADR GEVARENKLASSE MAPPING DEBUG ===\n")
    
    # Load mapping config
    with open('header_mapping.json', 'r', encoding='utf-8') as f:
        mapping_config = json.load(f)
    
    # Create test DataFrame with ADR header
    original_header = "ADR Gevarenklasse\n(Voor Uni's)\n\nADR Dangercategory\n(For Universities)"
    df = pd.DataFrame({original_header: ["test_value"]})
    
    print(f"Original header: {repr(original_header)}")
    print(f"Cleaned header: {repr(clean_column_name(original_header))}")
    
    # Check if it's in mapping
    header_mapping = {k: v["alternatives"] for k, v in mapping_config.get("standard_headers", {}).items()}
    
    print(f"\nChecking if ADR Gevarenklasse is in mapping...")
    if "ADR Gevarenklasse" in header_mapping:
        print("✅ ADR Gevarenklasse found in header_mapping")
        alternatives = header_mapping["ADR Gevarenklasse"]
        print(f"Alternatives: {alternatives}")
        
        # Check if our specific header matches any alternative
        cleaned_original = clean_column_name(original_header)
        matched = False
        for alt in alternatives:
            cleaned_alt = clean_column_name(alt)
            if cleaned_alt == cleaned_original:
                print(f"✅ MATCH FOUND: '{cleaned_alt}' matches original")
                matched = True
                break
        
        if not matched:
            print("❌ NO MATCH FOUND in alternatives")
    else:
        print("❌ ADR Gevarenklasse NOT found in header_mapping")
    
    # Test the actual mapping
    print(f"\n=== TESTING MAP_HEADERS FUNCTION ===")
    df_mapped, unrecognized, duplicates, original_mapping = map_headers(df, mapping_config, return_mapping=True)
    
    print(f"Original columns: {list(df.columns)}")
    print(f"Mapped columns: {list(df_mapped.columns)}")
    print(f"Unrecognized: {unrecognized}")
    print(f"Original mapping keys: {list(original_mapping.keys())}")
    print(f"Original mapping: {original_mapping}")
    
    # The issue might be here - what happens when we look up the renamed column?
    for col in df_mapped.columns:
        print(f"\nFinal column '{col}':")
        if col in original_mapping:
            print(f"  ✅ Found in original_mapping: '{original_mapping[col]}'")
        else:
            print(f"  ❌ NOT found in original_mapping")
            print(f"  Available keys: {list(original_mapping.keys())}")

if __name__ == "__main__":
    debug_adr_mapping()