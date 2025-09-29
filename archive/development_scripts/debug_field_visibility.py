#!/usr/bin/env python3
"""
Debugging script om field visibility logic te testen voor ADR Gevarenklasse
"""

import pandas as pd
import json
import logging
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from validator.price_tool import map_headers, apply_field_visibility, evaluate_field_visibility

def debug_field_visibility():
    """Test field visibility filtering voor ADR Gevarenklasse"""
    
    print("=== FIELD VISIBILITY DEBUG VOOR ADR GEVARENKLASSE ===\n")
    
    # Load configs
    with open('header_mapping.json', 'r', encoding='utf-8') as f:
        mapping_config = json.load(f)
        
    with open('Template Generator Files/field_mapping.json', 'r', encoding='utf-8') as f:
        field_mapping = json.load(f)
    
    # Create test DataFrame with ADR header
    original_header = "ADR Gevarenklasse\n(Voor Uni's)\n\nADR Dangercategory\n(For Universities)"
    df = pd.DataFrame({original_header: ["test_value"]})
    
    # Test mapping first (we know this works)
    df_mapped, unrecognized, duplicates, original_mapping = map_headers(df, mapping_config, return_mapping=True)
    print(f"✅ ADR mapped correctly: {'ADR Gevarenklasse' in df_mapped.columns}")
    
    # Check field visibility for different contexts
    adr_config = field_mapping.get("ADR Gevarenklasse", {})
    print(f"\nADR Gevarenklasse field config: {adr_config}")
    
    # Test visibility with different context labels
    test_contexts = [
        [],  # No context - mimics AT template
        ["chemicals"],  # Chemical context
        ["medical"],  # Medical context
        ["general"]  # General context
    ]
    
    for context_labels in test_contexts:
        is_visible = evaluate_field_visibility(adr_config, context_labels, [])
        print(f"Context {context_labels}: {'VISIBLE' if is_visible else 'HIDDEN'}")
    
    # Test apply_field_visibility with proper context structure
    print(f"\n=== TESTING APPLY_FIELD_VISIBILITY ===")
    
    test_context_configs = [
        {"name": "No context (AT template)", "context": {}},
        {"name": "With chemicals flag", "context": {"has_chemicals": True}},
        {"name": "Medical template", "context": {"product_types": ["medical"]}},
        {"name": "General template", "context": {"product_types": ["general"]}}
    ]
    
    for config in test_context_configs:
        print(f"\nTesting {config['name']}: {config['context']}")
        result = apply_field_visibility(field_mapping, config['context'])
        
        visible_fields = result.get('visible_list', [])
        hidden_fields = result.get('hidden_list', [])
        
        if "ADR Gevarenklasse" in visible_fields:
            print(f"  ✅ ADR Gevarenklasse is VISIBLE")
        elif "ADR Gevarenklasse" in hidden_fields:
            print(f"  ❌ ADR Gevarenklasse is HIDDEN")
        else:
            print(f"  ⚠️  ADR Gevarenklasse not found in visible or hidden lists")
            print(f"     Total visible: {len(visible_fields)}, total hidden: {len(hidden_fields)}")

if __name__ == "__main__":
    debug_field_visibility()