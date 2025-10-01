#!/usr/bin/env python3
"""
Debug specifieke headers uit screenshot die zouden moeten mappen maar dat niet doen
"""

import pandas as pd
import json
import logging
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from validator.price_tool import map_headers, clean_column_name

def debug_specific_headers():
    """Test specifieke headers uit screenshot"""
    
    print("=== DEBUG SPECIFIEKE HEADERS UIT SCREENSHOT ===\n")
    
    # Headers uit screenshot die geel zijn (zouden moeten mappen)
    problematic_headers = [
        "Eenheidscode Gewicht",
        "Eenheidscode Bruto Gewicht"
    ]
    
    # Load mapping config
    with open('header_mapping.json', 'r', encoding='utf-8') as f:
        mapping_config = json.load(f)
    
    # Test elke header individueel
    for header in problematic_headers:
        print(f"\n=== TESTING: {header} ===")
        
        # 1. Test clean_column_name
        cleaned = clean_column_name(header)
        print(f"Original: '{header}'")
        print(f"Cleaned: '{cleaned}'")
        
        # 2. Check if in mapping
        header_mapping = {k: v["alternatives"] for k, v in mapping_config.get("standard_headers", {}).items()}
        
        found_in_mapping = False
        matched_standard = None
        
        for std_header, alternatives in header_mapping.items():
            # Check direct match
            if clean_column_name(std_header) == cleaned:
                found_in_mapping = True
                matched_standard = std_header
                print(f"✅ Direct match with standard header: '{std_header}'")
                break
            
            # Check alternatives
            for alt in alternatives:
                if clean_column_name(alt) == cleaned:
                    found_in_mapping = True
                    matched_standard = std_header
                    print(f"✅ Alternative match: '{alt}' -> '{std_header}'")
                    break
            
            if found_in_mapping:
                break
        
        if not found_in_mapping:
            print(f"❌ NOT found in mapping")
            # Let's specifically search for these headers
            print("Searching specifically for this header in alternatives...")
            for std_header, alternatives in header_mapping.items():
                for alt in alternatives:
                    if header.lower() in alt.lower() or alt.lower() in header.lower():
                        print(f"   Similar found: '{alt}' in standard header '{std_header}'")
            print("   Exact match search:")
            for std_header, alternatives in header_mapping.items():
                if header in alternatives:
                    print(f"   ✅ EXACT MATCH FOUND: '{header}' is alternative of '{std_header}'")
                    break
        
        # 3. Test map_headers function
        print(f"\n--- Testing map_headers function ---")
        test_df = pd.DataFrame({header: ["test_value"]})
        
        try:
            mapped_df, unrecognized, duplicates, original_mapping = map_headers(test_df, mapping_config, return_mapping=True)
            
            print(f"Original columns: {list(test_df.columns)}")
            print(f"Mapped columns: {list(mapped_df.columns)}")
            print(f"Unrecognized: {unrecognized}")
            
            if header in unrecognized:
                print(f"❌ Header is in UNRECOGNIZED list!")
            else:
                print(f"✅ Header is NOT in unrecognized list")
                
            if len(mapped_df.columns) > 0:
                final_col = list(mapped_df.columns)[0]
                print(f"Final column name: '{final_col}'")
                
                if final_col in original_mapping:
                    print(f"✅ Found in original_mapping: '{original_mapping[final_col]}'")
                else:
                    print(f"❌ NOT found in original_mapping")
        
        except Exception as e:
            print(f"❌ Error in map_headers: {e}")
            import traceback
            traceback.print_exc()
        
        print("-" * 60)

if __name__ == "__main__":
    debug_specific_headers()