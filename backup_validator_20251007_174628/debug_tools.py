"""
Debug Tools Module

Deze module bevat debug utilities voor troubleshooting en analyse.
"""

import logging
from typing import Dict, Any, List, Tuple


def debug_field_mapping_decisions(field_mapping: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Gedetailleerde debug analyse van field mapping beslissingen.
    
    Args:
        field_mapping: Field mapping configuratie
        context: Template context
        
    Returns:
        Dict met debug informatie
    """
    try:
        from .field_logic import apply_field_visibility
        
        print("\n" + "="*80)
        print("🔍 FIELD MAPPING DECISIONS DEBUG")
        print("="*80)
        
        # Context info
        template_type = context.get('template_type', 'Unknown')
        stamp_data = context.get('stamp_data', {})
        
        print(f"\n📋 CONTEXT INFO:")
        print(f"Template Type: {template_type}")
        if template_type == 'TG':
            print(f"TG Code: {stamp_data.get('raw_code', 'N/A')}")
            print(f"Product Types: {stamp_data.get('product_types', [])}")
            print(f"Institutions: {stamp_data.get('institutions', [])}")
            print(f"Expected Fields: V{stamp_data.get('visible_fields', 0)}-M{stamp_data.get('mandatory_fields', 0)}")
        
        # Voer field visibility analyse uit
        result = apply_field_visibility(field_mapping, context)
        
        visible_fields = result['visible_fields']
        mandatory_fields = result['mandatory_fields']
        hidden_fields = result['hidden_fields']
        field_decisions = result['field_decisions']
        context_labels = result['context_labels']
        
        print(f"\n📊 SUMMARY:")
        print(f"Context Labels: {context_labels}")
        print(f"Total Fields: {len(field_mapping.get('fields', {}))}")
        print(f"Visible Fields: {len(visible_fields)}")
        print(f"Mandatory Fields: {len(mandatory_fields)}")  
        print(f"Hidden Fields: {len(hidden_fields)}")
        
        # Gedetailleerde field analyse (eerste 20)
        print(f"\n🔎 DETAILED FIELD ANALYSIS (first 20):")
        print(f"{'Field Name':<40} {'Col':<4} {'Status':<15} {'Reason'}")
        print("-" * 100)
        
        count = 0
        for field_name, decision in field_decisions.items():
            if count >= 20:
                break
                
            col = decision.get('col', '??')
            visible = decision.get('visible', False)
            mandatory = decision.get('mandatory', False)
            
            if visible and mandatory:
                status = "VIS + MAND"
            elif visible:
                status = "VISIBLE"
            else:
                status = "HIDDEN"
            
            reason = decision.get('visibility_reason', 'Unknown')
            if mandatory:
                reason += f" | Mandatory: {decision.get('mandatory_reason', 'Unknown')}"
                
            print(f"{field_name:<40} [{col:>3}] {status:<15} {reason}")
            count += 1
        
        if len(field_decisions) > 20:
            print(f"... and {len(field_decisions) - 20} more fields")
        
        # Mandatory fields lijst
        print(f"\n✅ MANDATORY FIELDS ({len(mandatory_fields)}):")
        for i, field in enumerate(mandatory_fields, 1):
            col = field_decisions.get(field, {}).get('col', '??')
            print(f"{i:2d}. [{col:>3}] {field}")
        
        # Hidden fields (eerste 10)
        if hidden_fields:
            print(f"\n❌ HIDDEN FIELDS (first 10 of {len(hidden_fields)}):")
            for i, field in enumerate(hidden_fields[:10], 1):
                col = field_decisions.get(field, {}).get('col', '??')
                reason = field_decisions.get(field, {}).get('visibility_reason', 'Unknown')
                print(f"{i:2d}. [{col:>3}] {field} - {reason}")
        
        return {
            'context': context,
            'summary': result['summary'],
            'field_decisions': field_decisions,
            'context_labels': context_labels,
            'debug_info': {
                'template_type': template_type,
                'stamp_data': stamp_data
            }
        }
        
    except Exception as e:
        logging.error(f"Fout bij field mapping debug: {e}")
        print(f"\n❌ DEBUG ERROR: {e}")
        return {'error': str(e)}


def debug_evaluate_field_visibility(field_config: Dict[str, Any], context_labels: List[str], 
                                   product_types: List[str]) -> Dict[str, Any]:
    """
    Debug analyse voor field visibility evaluatie.
    
    Args:
        field_config: Field configuratie
        context_labels: Context labels
        product_types: Product types
        
    Returns:
        Dict met debug informatie
    """
    try:
        from .field_logic import evaluate_field_visibility
        
        field_name = field_config.get('name', field_config.get('field_name', 'Unknown Field'))
        
        print(f"\n🔍 VISIBILITY DEBUG voor: {field_name}")
        print("-" * 60)
        
        # Evalueer visibility
        is_visible, reason = evaluate_field_visibility(field_config, context_labels, product_types)
        
        print(f"Field: {field_name}")
        print(f"Column: {field_config.get('col', '??')}")
        print(f"Result: {'VISIBLE' if is_visible else 'HIDDEN'}")
        print(f"Reason: {reason}")
        
        # Visibility config details
        visibility_config = field_config.get('visibility', {})
        if visibility_config:
            print(f"\nVisibility Config:")
            
            show_if = visibility_config.get('show_if', [])
            if show_if:
                print(f"  show_if: {show_if}")
                for condition in show_if:
                    matches = (condition.lower() in [cl.lower() for cl in context_labels] or
                              condition.lower() in [pt.lower() for pt in product_types])
                    print(f"    '{condition}' -> {'MATCH' if matches else 'NO MATCH'}")
            
            hide_if = visibility_config.get('hide_if', [])
            if hide_if:
                print(f"  hide_if: {hide_if}")
                for condition in hide_if:
                    matches = (condition.lower() in [cl.lower() for cl in context_labels] or
                              condition.lower() in [pt.lower() for pt in product_types])
                    print(f"    '{condition}' -> {'MATCH (HIDE)' if matches else 'NO MATCH'}")
        else:
            print(f"No visibility config - default visible")
        
        print(f"\nContext Labels: {context_labels}")
        print(f"Product Types: {product_types}")
        
        return {
            'field_name': field_name,
            'is_visible': is_visible,
            'reason': reason,
            'visibility_config': visibility_config,
            'context_labels': context_labels,
            'product_types': product_types
        }
        
    except Exception as e:
        logging.error(f"Fout bij visibility debug: {e}")
        print(f"❌ VISIBILITY DEBUG ERROR: {e}")
        return {'error': str(e)}


def debug_evaluate_field_mandatory(field_config: Dict[str, Any], context_labels: List[str], 
                                  product_types: List[str]) -> Dict[str, Any]:
    """
    Debug analyse voor field mandatory evaluatie.
    
    Args:
        field_config: Field configuratie
        context_labels: Context labels
        product_types: Product types
        
    Returns:
        Dict met debug informatie
    """
    try:
        from .field_logic import evaluate_field_mandatory
        
        field_name = field_config.get('name', field_config.get('field_name', 'Unknown Field'))
        
        print(f"\n🔍 MANDATORY DEBUG voor: {field_name}")
        print("-" * 60)
        
        # Evalueer mandatory status
        is_mandatory, reason = evaluate_field_mandatory(field_config, context_labels, product_types)
        
        print(f"Field: {field_name}")
        print(f"Column: {field_config.get('col', '??')}")
        print(f"Result: {'MANDATORY' if is_mandatory else 'OPTIONAL'}")
        print(f"Reason: {reason}")
        
        # Mandatory config details
        mandatory_config = field_config.get('mandatory', {})
        if mandatory_config:
            print(f"\nMandatory Config:")
            
            always = mandatory_config.get('always', False)
            if always:
                print(f"  always: {always}")
            
            mandatory_if = mandatory_config.get('if', [])
            if mandatory_if:
                print(f"  if: {mandatory_if}")
                for condition in mandatory_if:
                    matches = (condition.lower() in [cl.lower() for cl in context_labels] or
                              condition.lower() in [pt.lower() for pt in product_types])
                    print(f"    '{condition}' -> {'MATCH' if matches else 'NO MATCH'}")
            
            depends_on = mandatory_config.get('depends_on')
            if depends_on:
                print(f"  depends_on: {depends_on} (requires Excel data for evaluation)")
        else:
            print(f"No mandatory config - default optional")
        
        print(f"\nContext Labels: {context_labels}")
        print(f"Product Types: {product_types}")
        
        return {
            'field_name': field_name,
            'is_mandatory': is_mandatory,
            'reason': reason,
            'mandatory_config': mandatory_config,
            'context_labels': context_labels,
            'product_types': product_types
        }
        
    except Exception as e:
        logging.error(f"Fout bij mandatory debug: {e}")
        print(f"❌ MANDATORY DEBUG ERROR: {e}")
        return {'error': str(e)}


def debug_template_detection_flow(excel_path: str) -> Dict[str, Any]:
    """
    Debug de complete template detectie flow.
    
    Args:
        excel_path: Pad naar Excel bestand
        
    Returns:
        Dict met debug informatie
    """
    try:
        from .template_detector import test_template_detection, determine_template_type
        from .template_context import extract_template_generator_context
        
        print("\n" + "="*80)
        print("🔍 TEMPLATE DETECTION FLOW DEBUG")
        print("="*80)
        
        print(f"📁 Excel Path: {excel_path}")
        
        # Stap 1: Gedetailleerde template detection test
        print(f"\n1️⃣ TEMPLATE DETECTION TEST")
        print("-" * 40)
        
        detection_result = test_template_detection(excel_path)
        template_type = detection_result.get('template_type', 'Unknown')
        
        print(f"Template Type: {template_type}")
        print(f"Has TG Stamp: {detection_result.get('has_tg_stamp', False)}")
        
        if detection_result.get('tg_stamp_value'):
            print(f"TG Stamp: {detection_result.get('tg_stamp_value')}")
        
        print(f"Nieuwe Generatie Markers: {detection_result.get('heeft_nieuwe_generatie_markers', False)}")
        if detection_result.get('gevonden_markers'):
            print(f"Gevonden Markers: {detection_result.get('gevonden_markers')}")
        
        # Stap 2: Context extractie (voor TG templates)
        if template_type == 'TG':
            print(f"\n2️⃣ TEMPLATE GENERATOR CONTEXT")
            print("-" * 40)
            
            context = extract_template_generator_context(excel_path)
            if context:
                stamp_data = context.get('stamp_data', {})
                print(f"Raw Code: {stamp_data.get('raw_code', 'N/A')}")
                print(f"Template Choice: {stamp_data.get('template_choice', 'N/A')}")
                print(f"Product Types: {stamp_data.get('product_types', [])}")
                print(f"Institutions: {stamp_data.get('institutions', [])}")
                print(f"Has Chemicals: {stamp_data.get('has_chemicals', False)}")
                print(f"GS1 Mode: {stamp_data.get('gs1_mode', 'N/A')}")
                print(f"Expected Fields: V{stamp_data.get('visible_fields', 0)}-M{stamp_data.get('mandatory_fields', 0)}")
                
                # Institution info
                institution_info = context.get('institution_info', {})
                if institution_info:
                    print(f"\nInstitution Mapping:")
                    for code, name in institution_info.items():
                        print(f"  {code} -> {name}")
            else:
                print("❌ Context extractie gefaald")
        
        # Stap 3: Mandatory fields bepaling
        print(f"\n3️⃣ MANDATORY FIELDS DETERMINATION")
        print("-" * 40)
        
        from .mandatory_fields import determine_mandatory_fields_for_template
        mandatory_fields = determine_mandatory_fields_for_template(excel_path)
        
        print(f"Mandatory Fields Count: {len(mandatory_fields)}")
        print(f"Mandatory Fields: {mandatory_fields[:5]}{'...' if len(mandatory_fields) > 5 else ''}")
        
        return {
            'excel_path': excel_path,
            'detection_result': detection_result,
            'template_type': template_type,
            'context': context if template_type == 'TG' else None,
            'mandatory_fields': mandatory_fields,
            'mandatory_count': len(mandatory_fields)
        }
        
    except Exception as e:
        logging.error(f"Fout bij template detection debug: {e}")
        print(f"❌ TEMPLATE DETECTION DEBUG ERROR: {e}")
        return {'error': str(e)}


def debug_institution_mapping() -> Dict[str, Any]:
    """
    Debug institution mapping configuratie.
    
    Returns:
        Dict met institution mapping debug info
    """
    try:
        from .config_manager import load_institution_codes, get_fallback_institution_codes
        
        print("\n" + "="*60)
        print("🔍 INSTITUTION MAPPING DEBUG")
        print("="*60)
        
        # Probeer configuratie te laden
        config_codes = load_institution_codes()
        fallback_codes = get_fallback_institution_codes()
        
        print(f"\n📋 CONFIG INSTITUTION CODES ({len(config_codes)}):")
        for code, name in config_codes.items():
            print(f"  {code:<10} -> {name}")
        
        print(f"\n📋 FALLBACK INSTITUTION CODES ({len(fallback_codes)}):")
        for code, name in fallback_codes.items():
            in_config = "✓" if code in config_codes else "❌"
            print(f"  {code:<10} -> {name:<30} [{in_config}]")
        
        # Check verschillen
        config_only = set(config_codes.keys()) - set(fallback_codes.keys())
        fallback_only = set(fallback_codes.keys()) - set(config_codes.keys())
        
        if config_only:
            print(f"\n⚠️  ALLEEN IN CONFIG: {list(config_only)}")
        if fallback_only:
            print(f"\n⚠️  ALLEEN IN FALLBACK: {list(fallback_only)}")
        
        return {
            'config_codes': config_codes,
            'fallback_codes': fallback_codes,
            'config_only': list(config_only),
            'fallback_only': list(fallback_only)
        }
        
    except Exception as e:
        logging.error(f"Fout bij institution mapping debug: {e}")
        print(f"❌ INSTITUTION MAPPING DEBUG ERROR: {e}")
        return {'error': str(e)}


def debug_configuration_loading() -> Dict[str, Any]:
    """
    Debug configuratie laden process.
    
    Returns:
        Dict met configuratie debug info
    """
    try:
        from .config_manager import load_field_mapping, detect_json_version
        
        print("\n" + "="*60)
        print("🔍 CONFIGURATION LOADING DEBUG")
        print("="*60)
        
        # Probeer field mapping te laden
        field_mapping = load_field_mapping()
        
        if field_mapping:
            version = detect_json_version(field_mapping)
            fields = field_mapping.get('fields', {})
            
            print(f"✅ Field mapping geladen")
            print(f"📊 Versie: {version}")
            print(f"📊 Aantal velden: {len(fields)}")
            
            # Sample fields
            sample_fields = list(fields.keys())[:5]
            print(f"📊 Voorbeeld velden: {sample_fields}")
            
            # Check for specific configurations
            default_template = field_mapping.get('default_template', {})
            if default_template:
                print(f"📊 Default template config aanwezig")
            
        else:
            print("❌ Field mapping kon niet geladen worden")
        
        return {
            'field_mapping_loaded': field_mapping is not None,
            'version': detect_json_version(field_mapping) if field_mapping else None,
            'field_count': len(field_mapping.get('fields', {})) if field_mapping else 0
        }
        
    except Exception as e:
        logging.error(f"Fout bij configuration loading debug: {e}")
        print(f"❌ CONFIGURATION DEBUG ERROR: {e}")
        return {'error': str(e)}