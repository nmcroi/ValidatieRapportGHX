#!/usr/bin/env python3
"""
Debugging script om volledige validatie proces te testen met legacy_small.xlsx
"""

import pandas as pd
import json
import logging
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from validator.price_tool import map_headers, clean_column_name

def debug_full_validation():
    """Test volledig validatie proces met legacy_small.xlsx"""
    
    print("=== VOLLEDIGE VALIDATIE DEBUG MET LEGACY_SMALL.XLSX ===\n")
    
    # Load the actual file
    file_path = "test/testinput/legacy_small.xlsx"
    
    try:
        df = pd.read_excel(file_path)
        print(f"Loaded Excel file with {len(df)} rows and {len(df.columns)} columns")
        print(f"Columns: {list(df.columns)}")
        
        # Find ADR column specifically
        adr_col = None
        for col in df.columns:
            if "ADR" in str(col) and "Gevarenklasse" in str(col):
                adr_col = col
                break
        
        if adr_col:
            print(f"\n✅ Found ADR column: {repr(adr_col)}")
            print(f"Cleaned: {repr(clean_column_name(adr_col))}")
        else:
            print("\n❌ No ADR Gevarenklasse column found!")
            return
        
        # Load mapping config
        with open('header_mapping.json', 'r', encoding='utf-8') as f:
            mapping_config = json.load(f)
        
        # Test map_headers directly
        print(f"\n=== TESTING MAP_HEADERS DIRECTLY ===")
        df_mapped, unrecognized, duplicates, original_mapping = map_headers(df, mapping_config, return_mapping=True)
        
        print(f"Mapped {len(df_mapped.columns)} columns")
        print(f"Unrecognized: {len(unrecognized)} headers")
        
        if adr_col in unrecognized:
            print(f"❌ ADR column '{adr_col}' is in UNRECOGNIZED list!")
        else:
            print(f"✅ ADR column is NOT in unrecognized list")
        
        # Check if ADR Gevarenklasse is in final columns
        if "ADR Gevarenklasse" in df_mapped.columns:
            print(f"✅ 'ADR Gevarenklasse' found in final mapped columns")
        else:
            print(f"❌ 'ADR Gevarenklasse' NOT found in final mapped columns")
            print(f"Available columns: {list(df_mapped.columns)}")
        
        # Check original_mapping
        if "ADR Gevarenklasse" in original_mapping:
            print(f"✅ 'ADR Gevarenklasse' found in original_mapping")
            print(f"Maps to: {repr(original_mapping['ADR Gevarenklasse'])}")
        else:
            print(f"❌ 'ADR Gevarenklasse' NOT found in original_mapping")
            print(f"Available keys: {list(original_mapping.keys())}")
        
        print(f"\n=== DEBUGGING COMPLETE ===")
        print("map_headers function appears to work correctly for ADR Gevarenklasse")
        print("The issue must be elsewhere in the validation chain")
            
    except Exception as e:
        print(f"❌ Failed to load or process file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_full_validation()