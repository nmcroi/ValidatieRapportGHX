"""
Mandatory Fields Module

Deze module bepaalt welke velden mandatory zijn voor verschillende template types.
"""

import logging
from typing import Dict, Any, List


def determine_mandatory_fields_for_template(excel_path: str) -> List[str]:
    """
    Hoofd entry point voor het bepalen van mandatory fields.
    
    Gebruikt de TG → N → O beslissingsboom om de juiste mandatory fields te bepalen.
    
    Args:
        excel_path: Pad naar Excel template
        
    Returns:
        Lijst van mandatory field names
    """
    try:
        from .template_detector import determine_template_type
        from .template_context import extract_template_generator_context
        from .config_manager import load_field_mapping
        
        # Laad configuratie
        template_config = load_field_mapping()
        if not template_config:
            logging.error("Kon field mapping niet laden - gebruik fallback")
            fallback_fields = get_fallback_mandatory_fields()
            logging.warning(f"🔍 DEBUG: Config fallback - returning {len(fallback_fields)} velden")
            return fallback_fields
        
        # Bepaal template type via beslissingsboom
        template_type = determine_template_type(excel_path)
        
        if template_type == "TG":
            # Template Generator: gebruik context voor specifieke mandatory fields
            context = extract_template_generator_context(excel_path)
            if context:
                result = get_tg_mandatory_fields(template_config, context)
                return result
            else:
                logging.warning("TG template type maar context extractie gefaald, gebruik N fallback")
                result = get_nieuwe_generatie_mandatory_fields(template_config)
                return result
                
        elif template_type == "N":
            # Nieuwe Generatie Template: gebruik standaard GHX mandatory fields
            result = get_nieuwe_generatie_mandatory_fields(template_config)
            return result
            
        else:  # template_type == "O" of "AT"
            # Oude/Alternatieve Template: gebruik alle 17 standaard GHX mandatory fields
            result = get_oude_template_mandatory_fields(template_config)
            return result
        
    except Exception as e:
        logging.error(f"Fout bij bepalen mandatory fields: {e}")
        fallback_fields = get_fallback_mandatory_fields()
        logging.warning(f"🔍 DEBUG EXCEPTION: Returning fallback {len(fallback_fields)} velden")
        return fallback_fields


def get_tg_mandatory_fields(template_config: Dict, context: Dict[str, Any]) -> List[str]:
    """
    Bepaalt mandatory fields voor Template Generator templates op basis van context.
    
    Args:
        template_config: Field mapping configuratie
        context: TG context met parsed stamp data
        
    Returns:
        Lijst van context-specifieke mandatory fields
    """
    try:
        # Basis mandatory fields uit config
        mandatory_fields = get_context_mandatory_fields(template_config, context)
        
        # Voeg institution-specifieke fields toe
        stamp_data = context.get('stamp_data', {})
        institutions = stamp_data.get('institutions', [])
        if institutions:
            institution_fields = get_institution_mandatory_fields(institutions)
            mandatory_fields.extend(institution_fields)
        
        # Remove duplicates
        mandatory_fields = list(set(mandatory_fields))
        
        logging.info(f"TG mandatory fields: {len(mandatory_fields)} velden voor {institutions}")
        return mandatory_fields
        
    except Exception as e:
        logging.error(f"Fout bij bepalen TG mandatory fields: {e}")
        return get_fallback_mandatory_fields()


def get_context_mandatory_fields(template_config: Dict, context: Dict[str, Any]) -> List[str]:
    """
    Bepaalt context-afhankelijke mandatory fields uit field mapping.
    
    Args:
        template_config: Field mapping configuratie
        context: Template context met product types etc.
        
    Returns:
        Lijst van context-specifieke mandatory fields
    """
    try:
        from .field_logic import apply_field_visibility
        import pandas as pd
        
        # Laad Excel data voor depends_on checks als path beschikbaar is
        excel_data = None
        excel_path = context.get('excel_path')
        if excel_path:
            try:
                # Limiteer Excel data lezen voor performance (max 5000 rijen voor Quick Mode)
                excel_data = pd.read_excel(excel_path, nrows=5000)
                logging.info(f"Excel data geladen voor mandatory fields bepaling: {excel_data.shape}")
            except Exception as e:
                logging.warning(f"Kon Excel data niet laden voor mandatory fields: {e}")
        
        # Gebruik field visibility logic om mandatory fields te bepalen
        field_decisions = apply_field_visibility(template_config, context, excel_data)
        
        mandatory_fields = field_decisions.get('mandatory_fields', [])
        logging.info(f"Context mandatory fields: {len(mandatory_fields)} velden")
        
        return mandatory_fields
        
    except Exception as e:
        logging.error(f"Fout bij context mandatory fields: {e}")
        return get_fallback_mandatory_fields()


def get_institution_mandatory_fields(institutions: List[str]) -> List[str]:
    """
    Bepaalt institution-specifieke mandatory fields.
    
    Args:
        institutions: Lijst van institution codes
        
    Returns:
        Lijst van institution-specifieke mandatory fields
    """
    try:
        institution_fields = []
        
        for institution in institutions:
            if institution in ['umcu', 'lumc', 'amcu', 'mumc', 'umcg']:
                # NFU ziekenhuizen: Levertijd is mandatory
                if "Levertijd" not in institution_fields:
                    institution_fields.append("Levertijd")
                    
            elif institution == 'sq':
                # Sanquin: Menselijk weefsel veld is mandatory
                field_name = "Bevat het Artikel Menselijk Weefsel"
                if field_name not in institution_fields:
                    institution_fields.append(field_name)
        
        if institution_fields:
            logging.info(f"Institution mandatory fields: {institution_fields} voor {institutions}")
        
        return institution_fields
        
    except Exception as e:
        logging.error(f"Fout bij institution mandatory fields: {e}")
        return []


def get_nieuwe_generatie_mandatory_fields(template_config: Dict) -> List[str]:
    """
    Bepaalt mandatory fields voor Nieuwe Generatie Template (standaard GHX template).
    
    Returns:
        Lijst van 17 standaard GHX mandatory fields
    """
    try:
        default_config = template_config.get("default_template", {})
        mandatory_fields = default_config.get("mandatory_fields", [])
        
        if mandatory_fields:
            logging.info(f"N mandatory fields uit config: {len(mandatory_fields)} velden")
            return mandatory_fields
        else:
            # Fallback naar hardcoded lijst
            return get_fallback_mandatory_fields()
            
    except Exception as e:
        logging.error(f"Fout bij bepalen N mandatory fields: {e}")
        return get_fallback_mandatory_fields()


def get_oude_template_mandatory_fields(template_config: Dict) -> List[str]:
    """
    Bepaalt mandatory fields voor Oude/Alternatieve Template.
    
    AT templates moeten ook alle 17 standaard GHX mandatory velden hebben.
    Na mapping worden ze gevalideerd tegen dezelfde standaard als TG/N templates.
    
    Returns:
        Lijst van alle 17 standaard GHX mandatory fields voor AT templates
    """
    try:
        # AT templates moeten alle 17 standaard GHX mandatory velden hebben
        # Na header mapping valideren we tegen dezelfde standaard als andere templates
        at_mandatory_fields = get_fallback_mandatory_fields()
        
        # DEBUG: Extra logging om te traceren waarom dashboard 4 velden toont
        
        return at_mandatory_fields
        
    except Exception as e:
        logging.error(f"Fout bij bepalen AT mandatory fields: {e}")
        fallback_fields = get_fallback_mandatory_fields()
        logging.warning(f"🔍 DEBUG AT mandatory fields EXCEPTION: Returning fallback {len(fallback_fields)} velden")
        return fallback_fields


def get_fallback_mandatory_fields() -> List[str]:
    """
    Fallback mandatory fields als configuratie niet beschikbaar is.
    
    Returns:
        Hardcoded lijst van standaard GHX mandatory fields (17 velden)
    """
    return [
        "Artikelnummer",
        "Artikelnaam", 
        "Omschrijving",
        "Brutoprijs",
        "Nettoprijs",
        "Eenheid",
        "Verpakkingseenheid",
        "Producent",
        "Leverancier",
        "Leveranciernummer",
        "Catalogusnummer Producent", 
        "GTIN",
        "Product groep",
        "Sub categorie",
        "Geregistreerd geneesmiddel",
        "MDR/MDD Klasse",
        "Conditie"
    ]


def validate_mandatory_field_count(expected_count: int, actual_fields: List[str]) -> Dict[str, Any]:
    """
    Valideert of het aantal mandatory fields klopt met verwachting.
    
    Args:
        expected_count: Verwacht aantal (bijv. uit TG stamp M18)
        actual_fields: Lijst van daadwerkelijke mandatory fields
        
    Returns:
        Dict met validatie resultaat
    """
    try:
        actual_count = len(actual_fields)
        is_match = actual_count == expected_count
        
        result = {
            'expected_count': expected_count,
            'actual_count': actual_count,
            'is_match': is_match,
            'difference': actual_count - expected_count,
            'mandatory_fields': actual_fields
        }
        
        if is_match:
            logging.info(f"✓ Mandatory field count match: {actual_count} velden")
        else:
            logging.warning(f"✗ Mandatory field count mismatch: verwacht {expected_count}, kreeg {actual_count}")
        
        return result
        
    except Exception as e:
        logging.error(f"Fout bij mandatory field count validatie: {e}")
        return {
            'expected_count': expected_count,
            'actual_count': len(actual_fields),
            'is_match': False,
            'error': str(e)
        }