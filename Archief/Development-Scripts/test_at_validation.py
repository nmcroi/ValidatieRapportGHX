"""
Test script voor volledige AT validatie workflow.
"""

import sys
import os
sys.path.append('/Users/ncroiset/Vibe Coding Projecten/Cursor Projecten/Project PrijsValGem_WS app')

from validator.validation_engine import validate_pricelist

# Test AT template door volledige validatie pipeline
at_template = "/Users/ncroiset/Vibe Coding Projecten/Cursor Projecten/Project PrijsValGem_WS app/test/testinput/legacy_small.xlsx"

print("🧪 AT TEMPLATE VOLLEDIGE VALIDATIE TEST")
print("="*80)
print(f"📁 Bestand: {os.path.basename(at_template)}")
print()

if os.path.exists(at_template):
    try:
        # Voer volledige validatie uit
        report_path = validate_pricelist(
            input_excel_path=at_template,
            mapping_json_path="/Users/ncroiset/Vibe Coding Projecten/Cursor Projecten/Project PrijsValGem_WS app/header_mapping.json",
            validation_json_path="/Users/ncroiset/Vibe Coding Projecten/Cursor Projecten/Project PrijsValGem_WS app/field_validation_v20.json",
            original_input_filename="legacy_small.xlsx",
            reference_json_path="/Users/ncroiset/Vibe Coding Projecten/Cursor Projecten/Project PrijsValGem_WS app/reference_lists.json"
        )
        
        if report_path:
            print(f"✅ Validatie succesvol voltooid!")
            print(f"📊 Rapport gegenereerd: {os.path.basename(report_path)}")
            
            # Check of rapport bestaat
            if os.path.exists(report_path):
                file_size = os.path.getsize(report_path)
                print(f"📏 Rapport grootte: {file_size} bytes")
                
                # Probeer Excel te lezen om sheets te controleren
                try:
                    import pandas as pd
                    with pd.ExcelFile(report_path) as xl:
                        sheets = xl.sheet_names
                        print(f"📋 Aantal sheets: {len(sheets)}")
                        print(f"📋 Sheet namen: {sheets}")
                        
                        # Lees samenvatting sheet
                        if 'Samenvatting' in sheets:
                            summary_df = pd.read_excel(report_path, sheet_name='Samenvatting', header=None)
                            print(f"\n📊 Samenvatting inhoud (eerste 10 rijen):")
                            for i, row in summary_df.head(10).iterrows():
                                if not row.isna().all():
                                    print(f"  {i+1}: {list(row.dropna())}")
                                    
                except Exception as e:
                    print(f"⚠️  Kon rapport niet lezen: {e}")
            else:
                print(f"❌ Rapport bestand niet gevonden: {report_path}")
        else:
            print(f"❌ Validatie gefaald - geen rapport gegenereerd")
            
    except Exception as e:
        print(f"❌ Error tijdens validatie: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"❌ Test bestand niet gevonden: {at_template}")

print(f"\n" + "="*80)