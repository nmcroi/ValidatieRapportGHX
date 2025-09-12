#!/usr/bin/env python3
"""
Flask API voor GHX Clean Generator HTML interface.
Verbindt de HTML frontend met onze Python backend.
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import tempfile
import os
from pathlib import Path
import uuid
from datetime import datetime

# Import onze backend modules
import sys
sys.path.append('src')

from src.context import Context
from src.mapping import FieldMapping
from src.engine import TemplateEngine
from src.excel import ExcelProcessor

app = Flask(__name__)
CORS(app)  # Enable CORS voor frontend

# Globale storage voor gegenereerde bestanden
generated_files = {}

# Load configuration from JSON
def load_template_generator_config():
    """Load template generator configuration from field_validation JSON."""
    try:
        config_path = '../field_validation_v20.json'
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config.get('template_generator', {})
    except Exception as e:
        print(f"⚠️ Could not load template generator config: {e}")
        return {}

# Load configuration at startup
TEMPLATE_CONFIG = load_template_generator_config()
INSTITUTION_MAPPING = TEMPLATE_CONFIG.get('institution_mapping', {})
INSTITUTION_MANDATORY_FIELDS = TEMPLATE_CONFIG.get('institution_mandatory_fields', {})

def convert_institution_names_to_codes(institution_names):
    """Convert frontend institution names to short codes."""
    # Mapping van frontend namen naar short codes
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
    
    codes = []
    for name in institution_names:
        code = name_to_code.get(name, name)  # Fallback to original name
        codes.append(code)
        print(f"🔄 Institution mapping: '{name}' → '{code}'")
    
    return codes

def get_institution_mandatory_fields(institutions):
    """
    Bepaal welke velden mandatory zijn voor de geselecteerde institutions.
    
    Args:
        institutions: List van institution codes (zoals van UI)
        
    Returns:
        List van extra mandatory field names
    """
    extra_mandatory = []
    
    for institution in institutions:
        if institution in INSTITUTION_MANDATORY_FIELDS:
            for field in INSTITUTION_MANDATORY_FIELDS[institution]:
                if field not in extra_mandatory:
                    extra_mandatory.append(field)
    
    return extra_mandatory

def generate_readable_config_code(wizard_data, visible_count, mandatory_count):
    """
    Genereer een leesbare configuratie code die alle antwoorden weergeeft.
    
    Format: S-PT-CHEM-STAF-GS1-INST-V91-M20
    
    Onderdelen:
    - S = Standard template (F = Staffel template) 
    - PT = Product types (F=Facilitair, M=Medisch, L=Lab, O=Overige, FM/ML/etc=Combinaties)
    - CHEM = Chemicals (1=ja, 0=nee)
    - STAF = Staffel (1=ja, 0=nee)  
    - GS1 = GS1 mode (0=none, 1=gs1, 2=gs1_only)
    - INST = Institution codes (bijv: umcu+sq of amcu+lumc+mumc)
    - V91 = Visible fields
    - M20 = Mandatory fields
    
    Note: ORD (Orderable) positie weggehaald omdat vraag uit generator is verwijderd
    """
    parts = []
    
    # Template type (S=Standard, F=Staffel)
    is_staffel = wizard_data.get('is_staffel_file', False)
    parts.append("F" if is_staffel else "S")
    
    # Product types - specifiek welke combinaties
    product_types = wizard_data.get('product_types', [])
    if len(product_types) == 1:
        type_map = {'facilitair': 'F', 'medisch': 'M', 'lab': 'L', 'overige': 'O'}
        parts.append(type_map.get(product_types[0], 'O'))
    elif len(product_types) == 0:
        parts.append('N')  # None
    else:
        # Meerdere types: combinatie van letters
        type_letters = []
        for ptype in sorted(product_types):  # Sort voor consistente volgorde
            if ptype == 'facilitair':
                type_letters.append('F')
            elif ptype == 'medisch':
                type_letters.append('M')  
            elif ptype == 'lab':
                type_letters.append('L')
            elif ptype == 'overige':
                type_letters.append('O')
        parts.append(''.join(type_letters) if type_letters else 'N')
    
    # Chemicals (orderable positie weggehaald)
    chemicals = wizard_data.get('has_chemicals', False)
    parts.append('1' if chemicals else '0')
    
    # Staffel
    staffel = wizard_data.get('is_staffel_file', False)
    parts.append('1' if staffel else '0')
    
    # GS1 mode (alleen 2 opties: none=0, gs1=1)
    gs1_map = {'none': '0', 'gs1': '1'}
    gs1_mode = wizard_data.get('gs1_mode', 'none')
    parts.append(gs1_map.get(gs1_mode, '0'))
    
    # Institution codes (niet aantal maar welke)
    institutions_raw = wizard_data.get('institutions', [])
    institutions = convert_institution_names_to_codes(institutions_raw)
    if institutions:
        # Sorteer voor consistente volgorde, verbind met +
        institutions_code = '+'.join(sorted(institutions))
        parts.append(institutions_code)
    else:
        parts.append('none')
    
    # Visible en mandatory counts
    parts.append(f"V{visible_count}")
    parts.append(f"M{mandatory_count}")
    
    return "-".join(parts)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'message': 'GHX Template Generator API is running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/generate-template', methods=['POST'])
def generate_template():
    """
    Genereer template op basis van wizard data.
    
    Expected JSON:
    {
        "gs1_mode": "none", 
        "all_orderable": false,
        "product_types": ["facilitair"],
        "has_chemicals": false,
        "is_staffel_file": false,
        "institutions": ["AMC"],
        "version": "v1.0.0"
    }
    """
    try:
        # Parse wizard data
        wizard_data = request.get_json()
        if not wizard_data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        print(f"📥 Received wizard data: {wizard_data}")
        
        # Filter wizard data voor Context (verwijder HTML-specifieke velden)
        context_data = {k: v for k, v in wizard_data.items() 
                       if k not in ['timestamp', 'file_id']}  # Filter HTML metadata
        
        # Creëer Context object
        context = Context(**context_data)
        
        # Laad field mapping
        mapping = FieldMapping.from_file('config/field_mapping.json')
        
        # Maak template engine
        engine = TemplateEngine(context, mapping)
        decisions = engine.process_all_fields()
        
        # 🔥 NIEUWE FUNCTIONALITEIT: Institution-specific mandatory fields
        institutions_raw = wizard_data.get('institutions', [])
        print(f"🔍 DEBUG: institutions received: {institutions_raw}")
        print(f"🔄 JSON reloaded - current config: {INSTITUTION_MANDATORY_FIELDS}")
        # Force reload to test updated JSON
        
        # Convert frontend institution names to short codes
        institutions = convert_institution_names_to_codes(institutions_raw)
        print(f"🔄 DEBUG: converted to codes: {institutions}")
        
        if institutions:
            print(f"📋 Applying institution mandatory fields for: {institutions}")
            
            # Haal extra mandatory fields op voor geselecteerde institutions
            extra_mandatory_fields = get_institution_mandatory_fields(institutions)
            print(f"📋 Extra mandatory fields: {extra_mandatory_fields}")
        else:
            print(f"⚠️  No institutions provided, skipping mandatory fields logic")
        
        # Update decisions om extra mandatory fields toe te voegen (alleen als er institutions zijn)
        if institutions:
            field_names = list(mapping.get_all_fields().keys())
            for i, field_name in enumerate(field_names):
                if field_name in extra_mandatory_fields and i < len(decisions):
                    # Maak field mandatory als het zichtbaar is
                    if decisions[i].visible:
                        decisions[i].mandatory = True
                        print(f"✅ Made '{field_name}' mandatory for institutions: {institutions}")
        
        # Bepaal template op basis van staffel keuze
        is_staffel = wizard_data.get('is_staffel_file', False)
        if is_staffel:
            template_path = Path('templates/template_staffel.xlsx')
        else:
            template_path = Path('templates/GHXstandaardTemplate v25.1.xlsx')  # Default
        
        if not template_path.exists():
            return jsonify({'error': f'Template niet gevonden: {template_path}'}), 400
        
        # Genereer output bestand
        file_id = str(uuid.uuid4())
        output_path = Path(f'out/generated_{file_id}.xlsx')
        
        # Maak Excel processor met onze nieuwe kleuren
        excel_processor = ExcelProcessor(
            mandatory_color="#f89a8c",  # Onze perfecte oranje kleur
            hidden_color="#EEEEEE"
        )
        
        # Verwerk template
        context_dict = context.to_dict()
        context_dict["_labels"] = list(context.labels())
        
        # 🔥 STAP 4: Bewaar originele wizard_data voor volledige context
        context_dict["_wizard_data"] = wizard_data  # Inclusief institutions met volledige namen
        context_dict["_institution_codes"] = convert_institution_names_to_codes(
            wizard_data.get('institutions', [])
        )  # Short codes voor validatie
        
        # Voeg decisions toe voor volledige traceability
        context_dict["_decisions"] = {
            field_name: {
                "visible": decision.visible,
                "mandatory": decision.mandatory,
                "column": decision.column,
                "notes": decision.notes
            }
            for field_name, decision in zip(mapping.get_all_fields().keys(), decisions)
        }
        
        # Bereken statistieken voor config code
        visible_count = sum(1 for d in decisions if d.visible)
        mandatory_count = sum(1 for d in decisions if d.visible and d.mandatory)
        hidden_count = len(decisions) - visible_count
        
        # Genereer leesbare configuratie code
        config_code = generate_readable_config_code(wizard_data, visible_count, mandatory_count)
        
        # Voeg metadata en config code toe
        context_dict["_generator"] = {
            "version": "2.0.0",
            "mapping_fields": len(decisions),
            "timestamp": datetime.now().isoformat()
        }
        context_dict["_config_code"] = config_code
        
        excel_processor.process_template(
            template_path,
            output_path,
            decisions,
            context_dict,
            "Template NL"
        )
        
        # Bewaar file info
        generated_files[file_id] = {
            'path': output_path,
            'filename': f'ghx_template_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
            'created': datetime.now(),
            'context': wizard_data
        }
        
        # Bereken bestandsgrootte
        file_size_kb = round(output_path.stat().st_size / 1024, 1)
        
        return jsonify({
            'success': True,
            'file_id': file_id,
            'filename': generated_files[file_id]['filename'],
            'file_size_kb': file_size_kb,
            'preset_code': config_code,
            'stats': {
                'total_fields': len(decisions),
                'visible_fields': visible_count,
                'mandatory_fields': mandatory_count,
                'hidden_fields': hidden_count,
                'template_used': template_path.name
            },
            'message': 'Template succesvol gegenereerd!'
        })
        
    except Exception as e:
        print(f"❌ Error generating template: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Fout bij genereren van template'
        }), 500

@app.route('/api/download/<file_id>', methods=['GET'])
def download_template(file_id):
    """Download gegenereerd template bestand."""
    try:
        if file_id not in generated_files:
            return jsonify({'error': 'File niet gevonden'}), 404
        
        file_info = generated_files[file_id]
        file_path = file_info['path']
        
        if not file_path.exists():
            return jsonify({'error': 'Bestand niet meer beschikbaar'}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=file_info['filename'],
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        print(f"❌ Error downloading file: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/templates', methods=['GET'])
def list_templates():
    """Lijst beschikbare templates."""
    templates_dir = Path('templates')
    templates = []
    
    for template_file in templates_dir.glob('template_*.xlsx'):
        templates.append({
            'id': template_file.stem.replace('template_', ''),
            'name': template_file.name,
            'display_name': template_file.stem.replace('template_', '').replace('_', ' ').title()
        })
    
    return jsonify({'templates': templates})

@app.route('/api/test-samples', methods=['GET'])
def list_test_samples():
    """Lijst beschikbare test samples."""
    samples_dir = Path('tests/samples')
    samples = []
    
    for sample_file in samples_dir.glob('sample_context_*.json'):
        try:
            with open(sample_file, 'r') as f:
                sample_data = json.load(f)
            
            samples.append({
                'id': sample_file.stem,
                'name': sample_file.name,
                'display_name': sample_file.stem.replace('sample_context_', '').replace('_', ' ').title(),
                'data': sample_data
            })
        except Exception as e:
            print(f"⚠️ Kon sample niet laden: {sample_file} - {e}")
    
    return jsonify({'samples': samples})

@app.route('/api/institutions', methods=['GET'])
def list_institutions():
    """Geef de institution mapping terug voor de frontend."""
    return jsonify({
        'mapping': INSTITUTION_MAPPING,
        'mandatory_fields': INSTITUTION_MANDATORY_FIELDS
    })

if __name__ == '__main__':
    print("🚀 Starting GHX Template Generator API...")
    print("📍 API endpoints:")
    print("   • Health: http://127.0.0.1:8080/api/health")
    print("   • Generate: http://127.0.0.1:8080/api/generate-template")
    print("   • Download: http://127.0.0.1:8080/api/download/<file_id>")
    print("   • Templates: http://127.0.0.1:8080/api/templates")
    print("   • Samples: http://127.0.0.1:8080/api/test-samples")
    print("")
    print("🌐 Frontend: ghx_clean_generator.html")
    print("")
    
    app.run(host='127.0.0.1', port=8080, debug=True)
