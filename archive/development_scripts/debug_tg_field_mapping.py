"""
Debug TG template field mapping probleem.
"""

import sys
import os
sys.path.append('/Users/ncroiset/Vibe Coding Projecten/Cursor Projecten/Project PrijsValGem_WS app')

from validator.config_manager import load_field_mapping
from validator.template_detector import determine_template_type
from validator.template_context import extract_template_generator_context
from validator.field_logic import apply_field_visibility

tg_file = "/Users/ncroiset/Vibe Coding Projecten/Cursor Projecten/Project PrijsValGem_WS app/test/testinput/generator_small.xlsx"

print("🔍 TG TEMPLATE FIELD MAPPING DEBUG")
print("="*60)

# Stap 1: Template type bepalen
template_type = determine_template_type(tg_file)
print(f"1. Template Type: {template_type}")

# Stap 2: TG context extractie
if template_type == "TG":
    context = extract_template_generator_context(tg_file)
    print(f"2. TG Context extracted: {context is not None}")
    
    if context:
        stamp_data = context.get('stamp_data', {})
        print(f"   Stamp Code: {stamp_data.get('raw_code', 'N/A')}")
        print(f"   Product Types: {stamp_data.get('product_types', [])}")
        print(f"   Institutions: {stamp_data.get('institutions', [])}")
    else:
        print("   ❌ Context extractie gefaald")

# Stap 3: Field mapping laden
print(f"\n3. Field Mapping laden:")
field_mapping = load_field_mapping()

if field_mapping:
    fields = field_mapping.get('fields', {})
    print(f"   ✅ Field mapping geladen: {len(fields)} fields")
    print(f"   Sample field names: {list(fields.keys())[:5]}")
    
    # Check of fields key bestaat
    if not fields:
        print("   ❌ Geen fields key gevonden in field mapping!")
        print(f"   Keys in field_mapping: {list(field_mapping.keys())}")
else:
    print(f"   ❌ Field mapping kon niet geladen worden")

# Stap 4: Field visibility test
if field_mapping and template_type == "TG" and context:
    print(f"\n4. Field Visibility Test:")
    try:
        # Template context met excel_path
        template_context = context.copy()
        template_context['excel_path'] = tg_file
        
        result = apply_field_visibility(field_mapping, template_context)
        
        print(f"   ✅ Field visibility succesvol toegepast")
        print(f"   Visible fields: {len(result.get('visible_fields', []))}")
        print(f"   Mandatory fields: {len(result.get('mandatory_fields', []))}")
        print(f"   Hidden fields: {len(result.get('hidden_fields', []))}")
        
    except Exception as e:
        print(f"   ❌ Field visibility error: {e}")
        import traceback
        traceback.print_exc()

print("="*60)