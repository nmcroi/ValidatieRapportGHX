#!/usr/bin/env python3
"""
Genereer Excel testplan met alle testcodes en verwachte mandatory/ingeklapte kolommen.
"""
import sys
sys.path.append('src')

import pandas as pd
import json
from pathlib import Path
from src.context import Context
from src.mapping import FieldMapping  
from src.engine import TemplateEngine

def load_field_mapping():
    """Laad field mapping."""
    return FieldMapping.from_file('config/field_mapping.json')

def load_template_config():
    """Laad template generator configuratie."""
    config_path = '../field_validation_v20.json'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config.get('template_generator', {})

def convert_institution_names_to_codes(institution_names):
    """Convert frontend institution names to short codes."""
    name_to_code = {
        'universitair_medisch_centrum_utrecht_(umc_utrecht)': 'umcu',
        'leids_universitair_medisch_centrum_(lumc,_leiden)': 'lumc', 
        'amsterdam_umc_(locaties_amc_en_vumc)': 'amcu',
        'maastricht_umc+': 'mumc',
        'universitair_medisch_centrum_groningen_(umcg)': 'umcg',
        'sanquin_(nationale_bloedbank)': 'sq',
        'prinses_máxima_centrum_voor_kinderoncologie': 'pmc',
        'prothya_biosolutions': 'pb',
        'universiteit_leiden': 'ul',
        'universiteit_utrecht_(uu)': 'uu',
        'universiteit_van_amsterdam_(uva)': 'uva',
        'zorgservice_xl': 'zxl',
        'algemeen_gebruik_(geen_specifieke_instelling)': 'algemeen'
    }
    
    return [name_to_code.get(name, name) for name in institution_names]

def get_institution_mandatory_fields(institutions, config):
    """Bepaal welke velden mandatory zijn voor institutions."""
    mandatory_fields_config = config.get('institution_mandatory_fields', {})
    extra_mandatory = []
    
    for institution in institutions:
        if institution in mandatory_fields_config:
            for field in mandatory_fields_config[institution]:
                if field not in extra_mandatory:
                    extra_mandatory.append(field)
    
    return extra_mandatory

def generate_test_case(test_name, wizard_data, mapping, template_config):
    """Genereer een test case met alle verwachte kolommen."""
    try:
        # Creëer context
        context = Context(**wizard_data)
        
        # Maak template engine
        engine = TemplateEngine(context, mapping)
        decisions = engine.process_all_fields()
        
        # Haal extra mandatory fields op voor institutions
        institutions_raw = wizard_data.get('institutions', [])
        institutions = convert_institution_names_to_codes(institutions_raw)
        extra_mandatory_fields = get_institution_mandatory_fields(institutions, template_config)
        
        # Update decisions voor institution mandatory fields
        if institutions:
            field_names = list(mapping.get_all_fields().keys())
            for i, field_name in enumerate(field_names):
                if field_name in extra_mandatory_fields and i < len(decisions):
                    if decisions[i].visible:
                        decisions[i].mandatory = True
        
        # Bereken statistieken
        visible_count = sum(1 for d in decisions if d.visible)
        mandatory_count = sum(1 for d in decisions if d.visible and d.mandatory)
        hidden_count = len(decisions) - visible_count
        
        # Maak kolom details
        mandatory_columns = []
        hidden_columns = []
        visible_columns = []
        
        field_names = list(mapping.get_all_fields().keys())
        for i, decision in enumerate(decisions):
            if i < len(field_names):
                field_name = field_names[i]
                col = decision.column
                
                if decision.visible:
                    visible_columns.append(col)
                    if decision.mandatory:
                        mandatory_columns.append(col)
                else:
                    hidden_columns.append(col)
        
        return {
            'test_name': test_name,
            'wizard_data': wizard_data,
            'visible_count': visible_count,
            'mandatory_count': mandatory_count,
            'hidden_count': hidden_count,
            'mandatory_columns': ', '.join(sorted(mandatory_columns)),
            'hidden_columns': ', '.join(sorted(hidden_columns)),
            'visible_columns': ', '.join(sorted(visible_columns)),
            'institutions': ', '.join(institutions),
            'extra_mandatory_fields': ', '.join(extra_mandatory_fields),
            'actual_code': f"V{visible_count}-M{mandatory_count}"
        }
        
    except Exception as e:
        print(f"❌ Error processing {test_name}: {e}")
        return None

def main():
    """Genereer Excel testplan."""
    print("📋 Genereren Excel testplan...")
    
    # Laad configuraties
    mapping = load_field_mapping()
    template_config = load_template_config()
    
    # Definieer testcases
    test_cases = [
        {
            'name': 'TC01_BASIS_FACILITAIR',
            'description': 'S-F-0-0-0-algemeen-V91-M17 (Basis facilitair, Algemeen gebruik)',
            'wizard_data': {
                'template_choice': 'standard',
                'gs1_mode': 'none', 
                'all_orderable': False,
                'product_types': ['facilitair'],
                'has_chemicals': False,
                'is_staffel_file': False,
                'institutions': ['algemeen_gebruik_(geen_specifieke_instelling)'],
                'version': 'test'
            }
        },
        {
            'name': 'TC02_MEDISCH_UMCU',
            'description': 'S-M-1-0-0-umcu-V91-M21 (Medisch + chemicals, UMC Utrecht mandatory)',
            'wizard_data': {
                'template_choice': 'standard',
                'gs1_mode': 'none',
                'all_orderable': False,
                'product_types': ['medisch'],
                'has_chemicals': True,
                'is_staffel_file': False,
                'institutions': ['universitair_medisch_centrum_utrecht_(umc_utrecht)'],
                'version': 'test'
            }
        },
        {
            'name': 'TC03_MULTI_NFU_GS1',
            'description': 'S-FM-0-0-1-amcu+lumc-V93-M22 (Facilitair+Medisch, NFU, GS1)',
            'wizard_data': {
                'template_choice': 'standard',
                'gs1_mode': 'gs1',
                'all_orderable': False,
                'product_types': ['facilitair', 'medisch'],
                'has_chemicals': False,
                'is_staffel_file': False,
                'institutions': ['amsterdam_umc_(locaties_amc_en_vumc)', 'leids_universitair_medisch_centrum_(lumc,_leiden)'],
                'version': 'test'
            }
        },
        {
            'name': 'TC04_LAB_SANQUIN',
            'description': 'S-L-1-0-0-sq-V91-M18 (Lab + chemicals, Sanquin special)',
            'wizard_data': {
                'template_choice': 'standard',
                'gs1_mode': 'none',
                'all_orderable': False,
                'product_types': ['lab'],
                'has_chemicals': True,
                'is_staffel_file': False,
                'institutions': ['sanquin_(nationale_bloedbank)'],
                'version': 'test'
            }
        },
        {
            'name': 'TC05_MEDISCH_OVERIGE_RESEARCH',
            'description': 'S-MO-0-0-0-pmc+pb-V91-M17 (Medisch+Overige, research institutes)',
            'wizard_data': {
                'template_choice': 'standard',
                'gs1_mode': 'none',
                'all_orderable': False,
                'product_types': ['medisch', 'overige'],
                'has_chemicals': False,
                'is_staffel_file': False,
                'institutions': ['prinses_máxima_centrum_voor_kinderoncologie', 'prothya_biosolutions'],
                'version': 'test'
            }
        },
        {
            'name': 'TC06_FACILITAIR_LAB_UNI',
            'description': 'S-FL-1-0-1-uu+ul-V93-M17 (Facilitair+Lab, universiteiten, GS1)',
            'wizard_data': {
                'template_choice': 'standard',
                'gs1_mode': 'gs1',
                'all_orderable': False,
                'product_types': ['facilitair', 'lab'],
                'has_chemicals': True,
                'is_staffel_file': False,
                'institutions': ['universiteit_utrecht_(uu)', 'universiteit_leiden'],
                'version': 'test'
            }
        },
        {
            'name': 'TC07_ALLE_NFU_GS1',
            'description': 'S-FMLO-1-0-1-amcu+lumc+mumc+umcg+umcu-V95-M25 (Alle NFU, GS1)',
            'wizard_data': {
                'template_choice': 'standard',
                'gs1_mode': 'gs1',
                'all_orderable': False,
                'product_types': ['facilitair', 'medisch', 'lab', 'overige'],
                'has_chemicals': True,
                'is_staffel_file': False,
                'institutions': ['amsterdam_umc_(locaties_amc_en_vumc)', 'leids_universitair_medisch_centrum_(lumc,_leiden)', 'maastricht_umc+', 'universitair_medisch_centrum_groningen_(umcg)', 'universitair_medisch_centrum_utrecht_(umc_utrecht)'],
                'version': 'test'
            }
        },
        {
            'name': 'TC08_OVERIGE_PROTHYA',
            'description': 'S-O-0-0-0-pb-V91-M17 (Alleen overige, Prothya Biosolutions)',
            'wizard_data': {
                'template_choice': 'standard',
                'gs1_mode': 'none',
                'all_orderable': False,
                'product_types': ['overige'],
                'has_chemicals': False,
                'is_staffel_file': False,
                'institutions': ['prothya_biosolutions'],
                'version': 'test'
            }
        },
    ]
    
    # Genereer testplan data
    results = []
    for test_case in test_cases:
        print(f"🔄 Processing {test_case['name']}...")
        result = generate_test_case(
            test_case['name'], 
            test_case['wizard_data'], 
            mapping, 
            template_config
        )
        if result:
            # Update description with actual stats
            original_desc = test_case['description']
            # Replace the old V##-M## with actual stats
            import re
            updated_desc = re.sub(r'V\d+-M\d+', result['actual_code'], original_desc)
            result['description'] = updated_desc
            results.append(result)
    
    # Maak DataFrame
    df = pd.DataFrame(results)
    
    # Herorden kolommen voor leesbaarheid
    column_order = [
        'test_name', 'description', 'institutions', 'visible_count', 
        'mandatory_count', 'hidden_count', 'mandatory_columns', 
        'hidden_columns', 'extra_mandatory_fields'
    ]
    df = df[column_order]
    
    # Exporteer naar Excel
    output_path = Path('testplan_template_generator.xlsx')
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Testplan', index=False)
        
        # Pas kolom breedtes aan
        worksheet = writer.sheets['Testplan']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    print(f"✅ Excel testplan gegenereerd: {output_path}")
    print(f"📊 {len(results)} testcases verwerkt")

if __name__ == '__main__':
    main()