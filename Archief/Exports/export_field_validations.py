#!/usr/bin/env python3
"""
Export field validations van JSON v2.0 naar Excel/CSV
Elk veld wordt een aparte kolom met de complete JSON snippet.
"""

import json
import pandas as pd
from pathlib import Path

def export_field_validations_to_excel(json_file_path, output_file_path):
    """
    Exporteert field_validations naar Excel met elk veld in een aparte kolom.
    
    Args:
        json_file_path: Path naar field_validation_v20.json
        output_file_path: Path voor output Excel bestand
    """
    
    # Laad JSON data
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    field_validations = data.get('field_validations', {})
    
    if not field_validations:
        print("❌ Geen field_validations gevonden in JSON")
        return
    
    print(f"📊 Verwerken van {len(field_validations)} velden...")
    
    # Prepare data voor Excel
    export_data = {}
    
    for field_name, field_config in field_validations.items():
        # Converteer field config naar mooie JSON string
        json_snippet = json.dumps(field_config, indent=4, ensure_ascii=False)
        
        # Gebruik veldnaam als kolom header
        export_data[field_name] = [json_snippet]  # List omdat pandas dat verwacht
    
    # Maak DataFrame - alle velden in één rij
    df = pd.DataFrame(export_data)
    
    # Export naar Excel
    if output_file_path.endswith('.xlsx'):
        with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Field_Validations', index=False)
            
            # Maak kolommen breder voor leesbaarheid
            worksheet = writer.sheets['Field_Validations']
            for idx, col in enumerate(df.columns, 1):
                # Zet kolombreedte op basis van content lengte
                max_length = max(
                    len(str(col)),  # Header length
                    len(df[col].iloc[0].split('\n')[0]) if len(df) > 0 else 0  # First line length
                )
                adjusted_width = min(max_length + 5, 50)  # Max 50 characters wide
                worksheet.column_dimensions[worksheet.cell(row=1, column=idx).column_letter].width = adjusted_width
            
            # Zet rij hoogte voor betere leesbaarheid
            worksheet.row_dimensions[2].height = 300  # Hoogte voor JSON content
            
    elif output_file_path.endswith('.csv'):
        df.to_csv(output_file_path, index=False, encoding='utf-8')
    
    print(f"✅ Export voltooid naar: {output_file_path}")
    print(f"📋 {len(field_validations)} velden geëxporteerd in {len(df.columns)} kolommen")
    
    return df

def export_field_validations_summary(json_file_path, output_file_path):
    """
    Exporteert een summary versie met alleen key info per veld.
    """
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    field_validations = data.get('field_validations', {})
    
    summary_data = []
    
    for field_name, field_config in field_validations.items():
        data_format = field_config.get('data_format', 'unknown')
        rules_count = len(field_config.get('rules', []))
        
        # Extract rule types and codes
        rules = field_config.get('rules', [])
        rule_types = [rule.get('type', 'unknown') for rule in rules]
        rule_codes = [rule.get('code', 'unknown') for rule in rules]
        
        summary_data.append({
            'Field_Name': field_name,
            'Data_Format': data_format,
            'Rules_Count': rules_count,
            'Rule_Types': ', '.join(rule_types),
            'Rule_Codes': ', '.join(map(str, rule_codes)),
            'Has_Mandatory': any(rule.get('condition') == 'is_empty' and rule.get('type') == 'rejection' for rule in rules),
            'JSON_Snippet': json.dumps(field_config, ensure_ascii=False)
        })
    
    # Maak DataFrame
    df = pd.DataFrame(summary_data)
    
    # Export
    if output_file_path.endswith('.xlsx'):
        df.to_excel(output_file_path, index=False)
    else:
        df.to_csv(output_file_path, index=False, encoding='utf-8')
    
    print(f"✅ Summary export voltooid naar: {output_file_path}")
    
    return df

if __name__ == "__main__":
    # Configuratie
    json_file = "field_validation_v20.json"
    excel_output = "field_validations_export.xlsx"
    csv_output = "field_validations_export.csv"
    summary_output = "field_validations_summary.xlsx"
    
    try:
        print("🚀 Starting field validations export...")
        
        # Check of JSON bestand bestaat
        if not Path(json_file).exists():
            print(f"❌ JSON bestand niet gevonden: {json_file}")
            exit(1)
        
        # Export volledig (zoals gevraagd - alle velden horizontaal)
        print("\n📊 Exporteren naar Excel (horizontaal)...")
        export_field_validations_to_excel(json_file, excel_output)
        
        # Export naar CSV als backup
        print("\n📊 Exporteren naar CSV...")
        export_field_validations_to_excel(json_file, csv_output)
        
        # Export summary versie (verticaal voor analyse)
        print("\n📊 Exporteren summary versie...")
        export_field_validations_summary(json_file, summary_output)
        
        print(f"\n🎉 Alle exports voltooid!")
        print(f"📁 Bestanden aangemaakt:")
        print(f"   - {excel_output} (hoofdexport - horizontaal)")
        print(f"   - {csv_output} (CSV backup)")
        print(f"   - {summary_output} (summary - verticaal)")
        
    except Exception as e:
        print(f"❌ Fout tijdens export: {e}")
        import traceback
        traceback.print_exc()
