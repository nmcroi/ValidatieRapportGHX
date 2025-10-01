"""
Vergelijk TG vs AT template validatie rapporten.
"""

import sys
import os
sys.path.append('/Users/ncroiset/Vibe Coding Projecten/Cursor Projecten/Project PrijsValGem_WS app')

from validator.price_tool import validate_pricelist

# Test beide template types
templates = [
    {
        'name': 'Template Generator (TG)',
        'file': '/Users/ncroiset/Vibe Coding Projecten/Cursor Projecten/Project PrijsValGem_WS app/test/testinput/generator_small.xlsx',
        'expected_type': 'TG'
    },
    {
        'name': 'Alternatieve Template (O)', 
        'file': '/Users/ncroiset/Vibe Coding Projecten/Cursor Projecten/Project PrijsValGem_WS app/test/testinput/legacy_small.xlsx',
        'expected_type': 'O'
    }
]

print("📊 TG vs AT TEMPLATE VALIDATIE VERGELIJKING")
print("="*80)

for template in templates:
    print(f"\n🧪 {template['name']}")
    print("-" * 60)
    
    file_path = template['file']
    filename = os.path.basename(file_path)
    
    if os.path.exists(file_path):
        try:
            # Voer validatie uit
            report_path = validate_pricelist(
                input_excel_path=file_path,
                mapping_json_path="/Users/ncroiset/Vibe Coding Projecten/Cursor Projecten/Project PrijsValGem_WS app/header_mapping.json",
                validation_json_path="/Users/ncroiset/Vibe Coding Projecten/Cursor Projecten/Project PrijsValGem_WS app/field_validation_v20.json",
                original_input_filename=filename,
                reference_json_path="/Users/ncroiset/Vibe Coding Projecten/Cursor Projecten/Project PrijsValGem_WS app/reference_lists.json"
            )
            
            if report_path and os.path.exists(report_path):
                import pandas as pd
                
                # Lees Excel rapport
                with pd.ExcelFile(report_path) as xl:
                    sheets = xl.sheet_names
                    
                    print(f"✅ Rapport: {os.path.basename(report_path)}")
                    print(f"📋 Sheets ({len(sheets)}): {sheets}")
                    
                    # Lees samenvatting data
                    if 'Samenvatting' in sheets:
                        summary_df = pd.read_excel(report_path, sheet_name='Samenvatting', header=None)
                        
                        # Extract key metrics
                        metrics = {}
                        for i, row in summary_df.iterrows():
                            if not row.isna().all() and len(row.dropna()) >= 2:
                                key = str(row.dropna().iloc[0])
                                val = row.dropna().iloc[1] if len(row.dropna()) > 1 else ""
                                metrics[key] = val
                        
                        # Display key metrics
                        print(f"📊 Template Type: {metrics.get('Template Type', 'Unknown')}")
                        print(f"📊 Mandatory Columns: {metrics.get('Aantal aanwezige verplichte kolommen', '?')}")
                        print(f"📊 Rows: {metrics.get('Aantal rijen', '?')}")
                        print(f"📊 Columns: {metrics.get('Aantal kolommen', '?')}")
                        
                        if template['expected_type'] == metrics.get('Template Type'):
                            print(f"✅ Template type correct gedetecteerd!")
                        else:
                            print(f"❌ Template type mismatch: verwacht {template['expected_type']}, kreeg {metrics.get('Template Type')}")
                            
            else:
                print(f"❌ Geen rapport gegenereerd")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"❌ Bestand niet gevonden: {filename}")

print(f"\n" + "="*80)