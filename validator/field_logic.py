"""
Field Logic Module

Deze module implementeert de kern logica voor veld zichtbaarheid en mandatory status.
"""

import logging
import pandas as pd
from typing import Dict, Any, List, Tuple


def apply_field_visibility(field_mapping: Dict[str, Any], context: Dict[str, Any], excel_data: pd.DataFrame = None) -> Dict[str, Any]:
    """
    Hoofdfunctie voor het toepassen van veld zichtbaarheid en mandatory logica.
    
    Args:
        field_mapping: Field mapping configuratie uit JSON
        context: Template context (TG metadata, product types, etc.)
        excel_data: Optional Excel data voor depends_on checks
        
    Returns:
        Dict met visible_fields, mandatory_fields, hidden_fields en decisions
    """
    try:
        # Extract field mapping - check multiple possible keys
        fields = field_mapping.get('fields', {})  # Nieuwe structuur
        if not fields:
            fields = field_mapping.get('field_validations', {})  # V20 structuur
        
        if not fields:
            logging.error("Geen fields/field_validations gevonden in field mapping")
            logging.info(f"Available keys in field_mapping: {list(field_mapping.keys())}")
            return _empty_field_result()
        
        # Context labels bepalen
        context_labels = _build_context_labels(context)
        product_types = context.get('stamp_data', {}).get('product_types', [])
        
        logging.info(f"Field visibility analyse: {len(fields)} velden, "
                    f"context: {context_labels}, "
                    f"product types: {product_types}")
        
        # Analyseer elk veld
        visible_fields = []
        mandatory_fields = []
        hidden_fields = []
        field_decisions = {}
        
        for field_name, field_config in fields.items():
            if not isinstance(field_config, dict):
                continue
                
            # Bepaal zichtbaarheid
            is_visible, visibility_reason = evaluate_field_visibility(
                field_config, context_labels, product_types
            )
            
            # Bepaal mandatory status (alleen voor zichtbare velden)
            is_mandatory, mandatory_reason = False, "Veld niet zichtbaar"
            if is_visible:
                is_mandatory, mandatory_reason = evaluate_field_mandatory(
                    field_config, context_labels, product_types, excel_data
                )
            
            # Bewaar beslissing
            if is_visible:
                visible_fields.append(field_name)
                if is_mandatory:
                    mandatory_fields.append(field_name)
            else:
                hidden_fields.append(field_name)
            
            field_decisions[field_name] = {
                'col': field_config.get('col', '??'),
                'visible': is_visible,
                'visibility_reason': visibility_reason,
                'mandatory': is_mandatory,
                'mandatory_reason': mandatory_reason,
                'field_config': field_config
            }
        
        logging.info(f"Field analyse voltooid: {len(visible_fields)} zichtbaar, "
                    f"{len(mandatory_fields)} mandatory, {len(hidden_fields)} verborgen")
        
        return {
            'visible_fields': visible_fields,
            'mandatory_fields': mandatory_fields,
            'hidden_fields': hidden_fields,
            'field_decisions': field_decisions,
            'context_labels': context_labels,
            'summary': {
                'total': len(fields),
                'visible': len(visible_fields),
                'mandatory': len(mandatory_fields),
                'hidden': len(hidden_fields)
            }
        }
        
    except Exception as e:
        logging.error(f"Fout bij field visibility toepassing: {e}")
        return _empty_field_result()


def evaluate_field_visibility(field_config: Dict[str, Any], context_labels: List[str], product_types: List[str]) -> Tuple[bool, str]:
    """
    Evalueert of een veld zichtbaar moet zijn op basis van visibility regels.
    
    Args:
        field_config: Field configuratie uit JSON
        context_labels: Context labels (institutions, etc.)
        product_types: Product types (medisch, facilitair, etc.)
        
    Returns:
        Tuple van (is_visible: bool, reason: str)
    """
    try:
        visibility_config = field_config.get('visibility', {})
        
        # Als geen visibility config: standaard zichtbaar
        if not visibility_config:
            return True, "Geen visibility regels - standaard zichtbaar"
        
        # Check show_if condities
        show_if = visibility_config.get('show_if', [])
        if show_if:
            for condition in show_if:
                if _evaluate_condition(condition, context_labels, product_types):
                    return True, f"Show_if match: {condition}"
            
            # Geen show_if match gevonden
            return False, f"Geen show_if match voor: {show_if}"
        
        # Check hide_if condities  
        hide_if = visibility_config.get('hide_if', [])
        if hide_if:
            for condition in hide_if:
                if _evaluate_condition(condition, context_labels, product_types):
                    return False, f"Hide_if match: {condition}"
            
            # Geen hide_if match - zichtbaar
            return True, f"Geen hide_if match - zichtbaar"
        
        # Default: zichtbaar
        return True, "Default zichtbaar (geen specifieke regels)"
        
    except Exception as e:
        logging.error(f"Fout bij visibility evaluatie voor {field_config.get('name', 'unknown')}: {e}")
        return True, f"Fout bij evaluatie - default zichtbaar: {e}"


def evaluate_field_mandatory(field_config: Dict[str, Any], context_labels: List[str], product_types: List[str], excel_data: pd.DataFrame = None) -> Tuple[bool, str]:
    """
    Evalueert of een veld mandatory is op basis van mandatory regels.
    
    Args:
        field_config: Field configuratie uit JSON
        context_labels: Context labels  
        product_types: Product types
        excel_data: Excel data voor depends_on checks
        
    Returns:
        Tuple van (is_mandatory: bool, reason: str)
    """
    try:
        mandatory_config = field_config.get('mandatory', {})
        
        # Als geen mandatory config: niet mandatory
        if not mandatory_config:
            return False, "Geen mandatory regels"
        
        # Check always mandatory
        if mandatory_config.get('always', False):
            return True, "Always mandatory"
        
        # Check context-based mandatory
        mandatory_if = mandatory_config.get('if', [])
        if mandatory_if:
            for condition in mandatory_if:
                if _evaluate_condition(condition, context_labels, product_types):
                    # Check voor depends_on regel
                    depends_on = mandatory_config.get('depends_on')
                    if depends_on:
                        if _check_depends_on(depends_on, excel_data):
                            return True, f"Mandatory_if match + depends_on satisfied: {condition}"
                        else:
                            return False, f"Mandatory_if match maar depends_on niet satisfied: {depends_on}"
                    else:
                        return True, f"Mandatory_if match: {condition}"
            
            # Geen mandatory_if match
            return False, f"Geen mandatory_if match voor: {mandatory_if}"
        
        # Check depends_on zonder context
        depends_on = mandatory_config.get('depends_on')
        if depends_on:
            if _check_depends_on(depends_on, excel_data):
                return True, f"Depends_on satisfied: {depends_on}"
            else:
                return False, f"Depends_on niet satisfied: {depends_on}"
        
        # Default: niet mandatory
        return False, "Default niet mandatory"
        
    except Exception as e:
        logging.error(f"Fout bij mandatory evaluatie voor {field_config.get('name', 'unknown')}: {e}")
        return False, f"Fout bij evaluatie - default niet mandatory: {e}"


def _evaluate_condition(condition: str, context_labels: List[str], product_types: List[str]) -> bool:
    """
    Evalueert een enkele conditie tegen context.
    
    Args:
        condition: Conditie string (bijv. "medisch", "nfu_hospitals")
        context_labels: Context labels
        product_types: Product types
        
    Returns:
        True als conditie matches
    """
    try:
        condition_lower = condition.lower().strip()
        
        # Check product types
        if condition_lower in [pt.lower() for pt in product_types]:
            return True
        
        # Check context labels
        if condition_lower in [cl.lower() for cl in context_labels]:
            return True
        
        # Special mappings
        condition_mappings = {
            'medical': 'medisch',
            'facility': 'facilitair',
            'lab': 'laboratorium', 
            'other': 'overige',
            'nfu': 'nfu_hospitals'
        }
        
        mapped_condition = condition_mappings.get(condition_lower, condition_lower)
        if mapped_condition in [cl.lower() for cl in context_labels]:
            return True
        if mapped_condition in [pt.lower() for pt in product_types]:
            return True
        
        return False
        
    except Exception as e:
        logging.error(f"Fout bij conditie evaluatie '{condition}': {e}")
        return False


def _check_depends_on(depends_on: str, excel_data: pd.DataFrame) -> bool:
    """
    Controleert depends_on regel tegen Excel data.
    
    Args:
        depends_on: Depends_on regel (bijv. "Geregistreerd geneesmiddel == Ja")
        excel_data: DataFrame met Excel data
        
    Returns:
        True als depends_on conditie satisfied is
    """
    try:
        if excel_data is None or excel_data.empty:
            logging.warning(f"Geen Excel data voor depends_on check: {depends_on}")
            return False
        
        # Parse depends_on regel (format: "FieldName == Value")
        if " == " in depends_on:
            field_name, expected_value = depends_on.split(" == ", 1)
            field_name = field_name.strip()
            expected_value = expected_value.strip()
            
            if field_name not in excel_data.columns:
                logging.warning(f"Depends_on veld niet gevonden in data: {field_name}")
                return False
            
            # Check of er waarden in de kolom zijn die matchen
            column_values = excel_data[field_name].dropna().astype(str).str.strip()
            matches = column_values.str.lower() == expected_value.lower()
            
            has_match = matches.any()
            logging.info(f"Depends_on check '{depends_on}': {has_match}")
            return has_match
        
        logging.warning(f"Unsupported depends_on format: {depends_on}")
        return False
        
    except Exception as e:
        logging.error(f"Fout bij depends_on check '{depends_on}': {e}")
        return False


def _build_context_labels(context: Dict[str, Any]) -> List[str]:
    """
    Bouwt context labels op basis van template context.
    
    Args:
        context: Template context
        
    Returns:
        Lijst van context labels
    """
    try:
        labels = []
        
        # Template type
        template_type = context.get('template_type', '')
        if template_type:
            labels.append(template_type.lower())
        
        # Institution labels
        stamp_data = context.get('stamp_data', {})
        institutions = stamp_data.get('institutions', [])
        
        # NFU hospitals check
        nfu_institutions = ['umcu', 'lumc', 'amcu', 'mumc', 'umcg']
        if any(inst in nfu_institutions for inst in institutions):
            labels.append('nfu_hospitals')
        
        # Research institutes check  
        research_institutions = ['pmc', 'pb', 'ul', 'uu', 'uva']
        if any(inst in research_institutions for inst in institutions):
            labels.append('research_institutes')
        
        # Specific institutions
        labels.extend(institutions)
        
        # Andere context eigenschappen
        if stamp_data.get('has_chemicals'):
            labels.append('chemicals')
        if stamp_data.get('gs1_mode') == 'also_gs1':
            labels.append('gs1_mode')
        
        logging.info(f"Context labels: {labels}")
        return labels
        
    except Exception as e:
        logging.error(f"Fout bij context labels opbouw: {e}")
        return []


def _empty_field_result() -> Dict[str, Any]:
    """
    Retourneert lege field result structure.
    """
    return {
        'visible_fields': [],
        'mandatory_fields': [],
        'hidden_fields': [],
        'field_decisions': {},
        'context_labels': [],
        'summary': {'total': 0, 'visible': 0, 'mandatory': 0, 'hidden': 0}
    }


def get_visible_fields(template_context: Dict[str, Any]) -> List[str]:
    """
    Bepaalt welke velden zichtbaar zijn in template.
    
    Args:
        template_context: Template context dict
        
    Returns:
        Lijst van zichtbare field names, of None voor alle velden
    """
    try:
        # Voor TG templates: gebruik decisions metadata als beschikbaar
        decisions = template_context.get('decisions', {})
        if decisions and 'visible_list' in decisions:
            visible_list = decisions.get('visible_list', [])
            logging.info(f"TG visible fields uit metadata: {len(visible_list)} velden")
            return visible_list
        
        # Voor andere templates: retourneer None (alle velden zichtbaar)
        template_type = template_context.get('template_type', 'Unknown')
        logging.info(f"Template type {template_type}: alle velden zichtbaar")
        return None
        
    except Exception as e:
        logging.error(f"Fout bij bepalen zichtbare velden: {e}")
        return None


def get_collapsed_fields(template_context: Dict[str, Any]) -> List[str]:
    """
    Bepaalt welke velden zijn ingeklapte (collapsed) in template.
    
    Args:
        template_context: Template context dict
        
    Returns:
        Lijst van ingeklapte field names
    """
    try:
        # Voor TG templates: gebruik decisions metadata
        decisions = template_context.get('decisions', {})
        if decisions and 'collapsed_list' in decisions:
            collapsed_list = decisions.get('collapsed_list', [])
            logging.info(f"TG collapsed fields uit metadata: {len(collapsed_list)} velden")
            return collapsed_list
        
        # Voor andere templates: geen collapsed fields
        return []
        
    except Exception as e:
        logging.error(f"Fout bij bepalen ingeklapte velden: {e}")
        return []


def should_validate_field(field_name: str, template_context: Dict[str, Any]) -> bool:
    """
    Bepaalt of een veld gevalideerd moet worden.
    
    Args:
        field_name: Naam van het veld
        template_context: Template context
        
    Returns:
        True als veld gevalideerd moet worden
    """
    try:
        # Check of veld zichtbaar is
        visible_fields = get_visible_fields(template_context)
        
        if visible_fields is not None:  # TG template met specific visible fields
            return field_name in visible_fields
        else:  # Alle velden valideren
            return True
        
    except Exception as e:
        logging.error(f"Fout bij should_validate_field check: {e}")
        return True  # Default: valideer wel