#!/usr/bin/env python3
"""
Export error codes van JSON v2.0 naar Excel/CSV
Exporteert alle error code descriptions met categorisering.
"""

import json
import csv
from pathlib import Path

def export_error_codes_to_csv(json_file_path, output_file_path):
    """
    Exporteert error codes naar CSV met categorisering.
    
    Args:
        json_file_path: Path naar field_validation_v20.json
        output_file_path: Path voor output CSV bestand
    """
    
    # Laad JSON data
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    error_codes = data.get('global_settings', {}).get('error_code_descriptions', {})
    
    if not error_codes:
        print("❌ Geen error_code_descriptions gevonden in JSON")
        return
    
    print(f"📊 Verwerken van {len(error_codes)} error codes...")
    
    # Prepare data met categorisering
    csv_data = []
    
    for code, description in error_codes.items():
        code_num = int(code)
        
        # Bepaal categorie op basis van code range
        if 73 <= code_num <= 97:
            category = "REJECTION"
            category_desc = "Critical validation errors - will reject data"
        elif 101 <= code_num <= 122:
            if "FLAG:" in description:
                category = "FLAG"
                category_desc = "Warnings and recommendations"
            elif "CORRECTION:" in description:
                category = "CORRECTION"
                category_desc = "Auto-corrections applied"
            else:
                category = "VALIDATION"
                category_desc = "Advanced validation rules"
        elif 201 <= code_num <= 205:
            category = "GLOBAL_FLAG"
            category_desc = "Cross-field validations and global checks"
        else:
            category = "OTHER"
            category_desc = "Other validation rules"
        
        # Extract type prefix van description
        type_prefix = ""
        clean_description = description
        if description.startswith("FLAG:"):
            type_prefix = "FLAG"
            clean_description = description[5:].strip()
        elif description.startswith("CORRECTION:"):
            type_prefix = "CORRECTION"
            clean_description = description[11:].strip()
        elif description.startswith("GLOBAL FLAG:"):
            type_prefix = "GLOBAL FLAG"
            clean_description = description[12:].strip()
        
        csv_data.append({
            'Code': code,
            'Category': category,
            'Type_Prefix': type_prefix,
            'Description': clean_description,
            'Full_Description': description,
            'Category_Description': category_desc,
            'Usage_Context': _get_usage_context(code_num)
        })
    
    # Sorteer op code nummer
    csv_data.sort(key=lambda x: int(x['Code']))
    
    # Schrijf naar CSV
    with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Code', 'Category', 'Type_Prefix', 'Description', 'Full_Description', 'Category_Description', 'Usage_Context']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        
        writer.writeheader()
        writer.writerows(csv_data)
    
    print(f"✅ Export voltooid naar: {output_file_path}")
    print(f"📋 {len(error_codes)} error codes geëxporteerd")
    
    # Print statistieken
    categories = {}
    for item in csv_data:
        cat = item['Category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\n📊 Verdeling per categorie:")
    for category, count in sorted(categories.items()):
        print(f"   {category}: {count} codes")
    
    return csv_data

def _get_usage_context(code_num):
    """Bepaalt in welke context de error code wordt gebruikt."""
    if 73 <= code_num <= 97:
        return "Field validation rules - used in individual field validation"
    elif 101 <= code_num <= 122:
        return "Advanced field rules - flags, corrections, and conditional validation"
    elif 201 <= code_num <= 205:
        return "Global validation rules - cross-field and file-level checks"
    else:
        return "Unknown context"

def create_error_codes_summary(json_file_path, output_file_path):
    """
    Maakt een samenvatting van error codes per categorie.
    """
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    error_codes = data.get('global_settings', {}).get('error_code_descriptions', {})
    
    # Categoriseer alle codes
    categories = {
        'REJECTION (73-97)': [],
        'FLAG (101-122)': [],
        'CORRECTION (101-122)': [],
        'GLOBAL_FLAG (201-205)': []
    }
    
    for code, description in error_codes.items():
        code_num = int(code)
        
        if 73 <= code_num <= 97:
            categories['REJECTION (73-97)'].append((code, description))
        elif 101 <= code_num <= 122:
            if "FLAG:" in description:
                categories['FLAG (101-122)'].append((code, description))
            elif "CORRECTION:" in description:
                categories['CORRECTION (101-122)'].append((code, description))
        elif 201 <= code_num <= 205:
            categories['GLOBAL_FLAG (201-205)'].append((code, description))
    
    # Schrijf samenvatting
    with open(output_file_path, 'w', encoding='utf-8') as txtfile:
        txtfile.write("# Error Codes Summary\n")
        txtfile.write("# Generated from field_validation_v20.json\n")
        txtfile.write(f"# Total error codes: {len(error_codes)}\n")
        txtfile.write("=" * 80 + "\n\n")
        
        for category, codes in categories.items():
            if codes:
                txtfile.write(f"## {category} ({len(codes)} codes)\n")
                txtfile.write("-" * 50 + "\n")
                
                for code, description in sorted(codes, key=lambda x: int(x[0])):
                    txtfile.write(f"{code}: {description}\n")
                
                txtfile.write("\n")
    
    print(f"✅ Error codes summary voltooid naar: {output_file_path}")

if __name__ == "__main__":
    # Configuratie
    json_file = "field_validation_v20.json"
    csv_output = "error_codes_export.csv"
    summary_output = "error_codes_summary.txt"
    
    try:
        print("🚀 Starting error codes export...")
        
        # Check of JSON bestand bestaat
        if not Path(json_file).exists():
            print(f"❌ JSON bestand niet gevonden: {json_file}")
            exit(1)
        
        # Export error codes naar CSV
        print("\n📊 Exporteren error codes naar CSV...")
        export_error_codes_to_csv(json_file, csv_output)
        
        # Export summary
        print("\n📊 Exporteren error codes summary...")
        create_error_codes_summary(json_file, summary_output)
        
        print(f"\n🎉 Error codes export voltooid!")
        print(f"📁 Bestanden aangemaakt:")
        print(f"   - {csv_output} (HOOFDEXPORT - alle error codes)")
        print(f"   - {summary_output} (samenvatting per categorie)")
        
        print(f"\n💡 Open {csv_output} in Excel voor complete error codes lijst!")
        
    except Exception as e:
        print(f"❌ Fout tijdens export: {e}")
        import traceback
        traceback.print_exc()
