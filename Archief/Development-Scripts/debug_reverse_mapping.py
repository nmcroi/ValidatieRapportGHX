#!/usr/bin/env python3
"""
Debug de reverse_mapping logica om te zien wat er mis gaat
"""

import json
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from validator.price_tool import clean_column_name

def debug_reverse_mapping():
    """Debug de reverse mapping logica"""
    
    print("=== DEBUG REVERSE MAPPING ===\n")
    
    # Load mapping config
    with open('header_mapping.json', 'r', encoding='utf-8') as f:
        mapping_config = json.load(f)
    
    # Recreate the reverse mapping logic from map_headers()
    header_mapping = {k: v["alternatives"] for k, v in mapping_config.get("standard_headers", {}).items()}
    
    # Maak een reverse mapping: opgeschoonde alternatieve naam -> standaard header
    reverse_mapping = {}
    
    print("Building reverse mapping...")
    
    for std_header, alternatives in header_mapping.items():
        # Voeg de standaard header zelf ook toe als alternatief (lowercase, schoon)
        cleaned_std_header = clean_column_name(std_header)
        print(f"\nProcessing standard header: '{std_header}' -> cleaned: '{cleaned_std_header}'")
        
        if cleaned_std_header not in reverse_mapping: # Voorkom overschrijven door alternatief
             reverse_mapping[cleaned_std_header] = std_header
             print(f"  ✅ Added to reverse_mapping: '{cleaned_std_header}' -> '{std_header}'")
        else:
             print(f"  ⚠️  Already exists: '{cleaned_std_header}' maps to '{reverse_mapping[cleaned_std_header]}'")
        
        # Voeg alternatieven toe
        for alt in alternatives:
            cleaned_alt = clean_column_name(alt)
            if cleaned_alt:  # Only process non-empty cleaned alternatives
                print(f"    Alt: '{alt}' -> cleaned: '{cleaned_alt}'")
                
                # Apply the FIX: Check if cleaned_alt already exists to prevent overwriting!
                if cleaned_alt in reverse_mapping:
                    print(f"    ⚠️  SKIPPING: '{cleaned_alt}' already maps to '{reverse_mapping[cleaned_alt]}', not overwriting with '{std_header}'")
                else:
                    print(f"    ✅ Adding: '{cleaned_alt}' -> '{std_header}'")
                    reverse_mapping[cleaned_alt] = std_header # Alternatief wijst naar standaard
    
    print(f"\n=== FINAL REVERSE MAPPING ===")
    print(f"Total entries: {len(reverse_mapping)}")
    
    # Test our problematic headers
    test_headers = ["Eenheidscode Gewicht", "Eenheidscode Bruto Gewicht"]
    
    for header in test_headers:
        cleaned = clean_column_name(header)
        result = reverse_mapping.get(cleaned)
        print(f"\nTest: '{header}' -> cleaned: '{cleaned}' -> maps to: '{result}'")
        
        if result:
            print(f"  ✅ Found mapping!")
        else:
            print(f"  ❌ NOT found in reverse_mapping")
            
            # Search for partial matches
            print(f"  Searching for similar keys:")
            for key in reverse_mapping.keys():
                if 'eenheidscode' in key and 'gewicht' in key:
                    print(f"    Similar: '{key}' -> '{reverse_mapping[key]}'")

if __name__ == "__main__":
    debug_reverse_mapping()