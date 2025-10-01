"""
Test script voor AT (Alternatieve Template) detectie en mapping.
"""

import sys
import os
sys.path.append('/Users/ncroiset/Vibe Coding Projecten/Cursor Projecten/Project PrijsValGem_WS app')

from validator.debug_tools import debug_template_detection_flow

# Test verschillende template types
test_files = [
    "/Users/ncroiset/Vibe Coding Projecten/Cursor Projecten/Project PrijsValGem_WS app/test/testinput/generator_small.xlsx",  # Verwacht: TG
    "/Users/ncroiset/Vibe Coding Projecten/Cursor Projecten/Project PrijsValGem_WS app/test/testinput/ghx_default_small.xlsx",  # Verwacht: N
    "/Users/ncroiset/Vibe Coding Projecten/Cursor Projecten/Project PrijsValGem_WS app/test/testinput/legacy_small.xlsx",  # Verwacht: O
    "/Users/ncroiset/Vibe Coding Projecten/Cursor Projecten/Project PrijsValGem_WS app/test/testinput/Test1.xlsx",  # Onbekend
    "/Users/ncroiset/Vibe Coding Projecten/Cursor Projecten/Project PrijsValGem_WS app/test/testinput/Test2.xlsx",  # Onbekend
]

print("🔍 AT (ALTERNATIEVE TEMPLATE) DETECTIE TEST")
print("="*80)

for i, test_file in enumerate(test_files, 1):
    filename = os.path.basename(test_file)
    
    if os.path.exists(test_file):
        print(f"\n{i}. 📁 {filename}")
        print("-" * 60)
        
        try:
            result = debug_template_detection_flow(test_file)
            template_type = result.get('template_type', 'Error')
            mandatory_count = result.get('mandatory_count', 0)
            
            if template_type == 'TG':
                context = result.get('context', {})
                stamp_data = context.get('stamp_data', {}) if context else {}
                print(f"✅ Template Generator - {stamp_data.get('raw_code', 'N/A')}")
                print(f"   Expected M{stamp_data.get('mandatory_fields', 0)}, Got {mandatory_count}")
                
            elif template_type == 'N':
                print(f"✅ Nieuwe Generatie - {mandatory_count} mandatory fields")
                
            elif template_type == 'O':
                print(f"⚠️  Oude/Alternatieve - {mandatory_count} mandatory fields (minimale set)")
                
            else:
                print(f"❌ Error: {template_type}")
                
        except Exception as e:
            print(f"❌ Error bij detectie: {e}")
    else:
        print(f"\n{i}. ❌ {filename} - Bestand niet gevonden")

print(f"\n" + "="*80)
print("AT Template Analysis voltooid")