#!/usr/bin/env python3
"""
Complete export van alle error codes uit JSON v2.0
Ondersteunt alle code ranges: 73-97, 101-122, 201-205
"""

import json
import csv
from pathlib import Path

def export_all_error_codes(json_file_path, output_file_path):
    """
    Exporteert ALLE error codes naar CSV met complete categorisering.
    """
    
    # Laad JSON data
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    error_codes = data.get('global_settings', {}).get('error_code_descriptions', {})
    
    if not error_codes:
        print("❌ Geen error_code_descriptions gevonden in JSON")
        return
    
    print(f"📊 Verwerken van {len(error_codes)} error codes...")
    
    # Prepare data met uitgebreide categorisering
    csv_data = []
    
    for code, description in error_codes.items():
        code_num = int(code)
        
        # Uitgebreide categorisering
        category_info = categorize_error_code(code_num, description)
        
        csv_data.append({
            'Code': code,
            'Code_Number': code_num,
            'Category': category_info['category'],
            'Subcategory': category_info['subcategory'],
            'Type_Prefix': category_info['type_prefix'],
            'Severity': category_info['severity'],
            'Description_Clean': category_info['clean_description'],
            'Description_Full': description,
            'Category_Description': category_info['category_desc'],
            'Usage_Context': category_info['usage_context'],
            'Recommended_Action': category_info['recommended_action']
        })
    
    # Sorteer op code nummer
    csv_data.sort(key=lambda x: x['Code_Number'])
    
    # Schrijf naar CSV
    with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'Code', 'Code_Number', 'Category', 'Subcategory', 'Type_Prefix', 'Severity',
            'Description_Clean', 'Description_Full', 'Category_Description', 
            'Usage_Context', 'Recommended_Action'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        
        writer.writeheader()
        writer.writerows(csv_data)
    
    print(f"✅ Complete export voltooid naar: {output_file_path}")
    print(f"📋 {len(error_codes)} error codes geëxporteerd")
    
    # Gedetailleerde statistieken
    print_detailed_statistics(csv_data)
    
    return csv_data

def categorize_error_code(code_num, description):
    """Uitgebreide categorisering van error codes."""
    
    info = {
        'category': 'UNKNOWN',
        'subcategory': '',
        'type_prefix': '',
        'severity': 'UNKNOWN',
        'clean_description': description,
        'category_desc': '',
        'usage_context': '',
        'recommended_action': ''
    }
    
    # Parse type prefix
    if description.startswith("FLAG:"):
        info['type_prefix'] = "FLAG"
        info['clean_description'] = description[5:].strip()
    elif description.startswith("CORRECTION:"):
        info['type_prefix'] = "CORRECTION"
        info['clean_description'] = description[11:].strip()
    elif description.startswith("GLOBAL FLAG:"):
        info['type_prefix'] = "GLOBAL FLAG"
        info['clean_description'] = description[12:].strip()
    
    # Categoriseer op basis van code range
    if 73 <= code_num <= 97:
        info.update({
            'category': 'REJECTION',
            'subcategory': 'Field Validation',
            'severity': 'CRITICAL',
            'category_desc': 'Critical validation errors that will reject data',
            'usage_context': 'Individual field validation rules',
            'recommended_action': 'Fix data to pass validation'
        })
        
    elif 101 <= code_num <= 122:
        if info['type_prefix'] == 'FLAG':
            info.update({
                'category': 'FLAG',
                'subcategory': 'Warning',
                'severity': 'WARNING',
                'category_desc': 'Warnings and recommendations',
                'usage_context': 'Quality checks and recommendations',
                'recommended_action': 'Review and consider fixing'
            })
        elif info['type_prefix'] == 'CORRECTION':
            info.update({
                'category': 'CORRECTION',
                'subcategory': 'Auto-fix',
                'severity': 'INFO',
                'category_desc': 'Automatic corrections applied by system',
                'usage_context': 'Data transformation and enhancement',
                'recommended_action': 'Verify auto-correction is correct'
            })
        else:
            info.update({
                'category': 'VALIDATION',
                'subcategory': 'Advanced',
                'severity': 'WARNING',
                'category_desc': 'Advanced validation rules',
                'usage_context': 'Complex field validation',
                'recommended_action': 'Review validation logic'
            })
            
    elif 201 <= code_num <= 205:
        info.update({
            'category': 'GLOBAL_FLAG',
            'subcategory': 'Cross-field',
            'severity': 'WARNING',
            'category_desc': 'Global validations and cross-field checks',
            'usage_context': 'File-level and cross-field validation',
            'recommended_action': 'Review global data consistency'
        })
        
    return info

def print_detailed_statistics(csv_data):
    """Print gedetailleerde statistieken."""
    
    print("\n📊 Gedetailleerde verdeling:")
    
    # Groepeer per categorie
    categories = {}
    severities = {}
    
    for item in csv_data:
        cat = item['Category']
        sev = item['Severity']
        
        categories[cat] = categories.get(cat, 0) + 1
        severities[sev] = severities.get(sev, 0) + 1
    
    print("   Per categorie:")
    for cat, count in sorted(categories.items()):
        print(f"     {cat}: {count} codes")
    
    print("   Per severity:")
    for sev, count in sorted(severities.items()):
        print(f"     {sev}: {count} codes")
    
    # Code ranges
    ranges = {
        '73-97 (Rejection)': len([x for x in csv_data if 73 <= x['Code_Number'] <= 97]),
        '101-122 (Flag/Correction)': len([x for x in csv_data if 101 <= x['Code_Number'] <= 122]),
        '201-205 (Global)': len([x for x in csv_data if 201 <= x['Code_Number'] <= 205])
    }
    
    print("   Per code range:")
    for range_desc, count in ranges.items():
        print(f"     {range_desc}: {count} codes")

def create_codes_by_category_export(csv_data, output_dir):
    """Maak separate exports per categorie."""
    
    categories = {}
    for item in csv_data:
        cat = item['Category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)
    
    for category, items in categories.items():
        filename = f"{output_dir}/error_codes_{category.lower()}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Code', 'Description_Clean', 'Severity', 'Recommended_Action']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            
            writer.writeheader()
            for item in items:
                writer.writerow({
                    'Code': item['Code'],
                    'Description_Clean': item['Description_Clean'],
                    'Severity': item['Severity'],
                    'Recommended_Action': item['Recommended_Action']
                })
        
        print(f"✅ {category} codes exported to: {filename}")

if __name__ == "__main__":
    # Configuratie
    json_file = "field_validation_v20.json"
    complete_output = "error_codes_complete.csv"
    
    try:
        print("🚀 Starting COMPLETE error codes export...")
        
        # Check of JSON bestand bestaat
        if not Path(json_file).exists():
            print(f"❌ JSON bestand niet gevonden: {json_file}")
            exit(1)
        
        # Export alle error codes
        print("\n📊 Exporteren ALLE error codes naar CSV...")
        csv_data = export_all_error_codes(json_file, complete_output)
        
        # Maak category-specific exports
        print(f"\n📊 Maken van category-specific exports...")
        create_codes_by_category_export(csv_data, ".")
        
        print(f"\n🎉 Complete error codes export voltooid!")
        print(f"📁 Hoofdbestand: {complete_output}")
        print(f"💡 Open {complete_output} in Excel voor complete overzicht!")
        print(f"📋 Dit script werkt met ALLE code ranges (73-97, 101-122, 201-205)")
        
    except Exception as e:
        print(f"❌ Fout tijdens export: {e}")
        import traceback
        traceback.print_exc()
