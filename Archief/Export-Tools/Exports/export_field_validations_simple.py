#!/usr/bin/env python3
"""
Export field validations van JSON v2.0 naar CSV
Elk veld wordt een aparte kolom met de complete JSON snippet.
Gebruikt alleen standaard Python libraries.
"""

import json
import csv
from pathlib import Path

def export_field_validations_to_csv(json_file_path, output_file_path):
    """
    Exporteert field_validations naar CSV met elk veld in een aparte kolom.
    
    Args:
        json_file_path: Path naar field_validation_v20.json
        output_file_path: Path voor output CSV bestand
    """
    
    # Laad JSON data
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    field_validations = data.get('field_validations', {})
    
    if not field_validations:
        print("❌ Geen field_validations gevonden in JSON")
        return
    
    print(f"📊 Verwerken van {len(field_validations)} velden...")
    
    # Prepare data voor CSV - alle velden als kolommen, JSON snippets als waarden
    field_names = list(field_validations.keys())
    
    # Maak CSV bestand
    with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        
        # Schrijf header rij (veldnamen)
        writer.writerow(field_names)
        
        # Schrijf data rij (JSON snippets)
        json_snippets = []
        for field_name in field_names:
            field_config = field_validations[field_name]
            json_snippet = json.dumps(field_config, indent=2, ensure_ascii=False)
            json_snippets.append(json_snippet)
        
        writer.writerow(json_snippets)
    
    print(f"✅ Export voltooid naar: {output_file_path}")
    print(f"📋 {len(field_validations)} velden geëxporteerd in {len(field_names)} kolommen")
    
    return field_names

def export_field_validations_vertical(json_file_path, output_file_path):
    """
    Exporteert field validations in verticaal formaat (elk veld een rij).
    """
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    field_validations = data.get('field_validations', {})
    
    with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        
        # Header
        writer.writerow(['Field_Name', 'Data_Format', 'Rules_Count', 'Rule_Codes', 'JSON_Snippet'])
        
        # Data
        for field_name, field_config in field_validations.items():
            data_format = field_config.get('data_format', 'unknown')
            rules = field_config.get('rules', [])
            rules_count = len(rules)
            rule_codes = [rule.get('code', 'unknown') for rule in rules]
            json_snippet = json.dumps(field_config, indent=2, ensure_ascii=False)
            
            writer.writerow([
                field_name,
                data_format,
                rules_count,
                ', '.join(map(str, rule_codes)),
                json_snippet
            ])
    
    print(f"✅ Vertical export voltooid naar: {output_file_path}")

def create_field_overview_txt(json_file_path, output_file_path):
    """
    Maakt een leesbare text overview van alle velden.
    """
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    field_validations = data.get('field_validations', {})
    
    with open(output_file_path, 'w', encoding='utf-8') as txtfile:
        txtfile.write("# Field Validations Overview\\n")
        txtfile.write("# Generated from field_validation_v20.json\\n")
        txtfile.write(f"# Total fields: {len(field_validations)}\\n")
        txtfile.write("=" * 80 + "\\n\\n")
        
        for i, (field_name, field_config) in enumerate(field_validations.items(), 1):
            txtfile.write(f"## {i:3d}. {field_name}\\n")
            txtfile.write("-" * 50 + "\\n")
            
            # Basis info
            data_format = field_config.get('data_format', 'unknown')
            txtfile.write(f"Data Format: {data_format}\\n")
            
            rules = field_config.get('rules', [])
            txtfile.write(f"Rules Count: {len(rules)}\\n")
            
            # Rules details
            if rules:
                txtfile.write("\\nRules:\\n")
                for j, rule in enumerate(rules, 1):
                    rule_type = rule.get('type', 'unknown')
                    condition = rule.get('condition', 'unknown')
                    code = rule.get('code', 'unknown')
                    message = rule.get('message', 'No message')
                    
                    txtfile.write(f"  {j}. [{code}] {rule_type.upper()}: {condition}\\n")
                    txtfile.write(f"     Message: {message}\\n")
            
            # JSON snippet
            txtfile.write("\\nJSON Snippet:\\n")
            json_snippet = json.dumps(field_config, indent=2, ensure_ascii=False)
            for line in json_snippet.split('\\n'):
                txtfile.write(f"  {line}\\n")
            
            txtfile.write("\\n" + "=" * 80 + "\\n\\n")
    
    print(f"✅ Text overview voltooid naar: {output_file_path}")

if __name__ == "__main__":
    # Configuratie
    json_file = "field_validation_v20.json"
    csv_horizontal = "field_validations_horizontal.csv"
    csv_vertical = "field_validations_vertical.csv"
    txt_overview = "field_validations_overview.txt"
    
    try:
        print("🚀 Starting field validations export...")
        
        # Check of JSON bestand bestaat
        if not Path(json_file).exists():
            print(f"❌ JSON bestand niet gevonden: {json_file}")
            exit(1)
        
        # Export horizontaal (zoals gevraagd - alle velden in kolommen)
        print("\\n📊 Exporteren naar CSV (horizontaal - zoals gevraagd)...")
        export_field_validations_to_csv(json_file, csv_horizontal)
        
        # Export verticaal (voor analyse)
        print("\\n📊 Exporteren naar CSV (verticaal)...")
        export_field_validations_vertical(json_file, csv_vertical)
        
        # Export text overview (leesbaar)
        print("\\n📊 Exporteren text overview...")
        create_field_overview_txt(json_file, txt_overview)
        
        print(f"\\n🎉 Alle exports voltooid!")
        print(f"📁 Bestanden aangemaakt:")
        print(f"   - {csv_horizontal} (HOOFDEXPORT - horizontaal zoals gevraagd)")
        print(f"   - {csv_vertical} (verticaal voor analyse)")
        print(f"   - {txt_overview} (leesbaar overzicht)")
        
        print(f"\\n💡 Open {csv_horizontal} in Excel voor het gewenste horizontale format!")
        
    except Exception as e:
        print(f"❌ Fout tijdens export: {e}")
        import traceback
        traceback.print_exc()
