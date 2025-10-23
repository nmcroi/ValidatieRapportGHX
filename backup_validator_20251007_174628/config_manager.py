"""
Configuratie Manager Module

Deze module beheert het laden en normaliseren van alle configuratie bestanden.
"""

import json
import logging
import os
from typing import Dict, Any, Optional


def load_field_mapping() -> Optional[Dict[str, Any]]:
    """
    Laadt field mapping configuratie uit JSON bestand.
    
    Returns:
        Field mapping configuratie dict of None bij fout
    """
    try:
        # Zoek field_validation_v20.json in project directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        mapping_path = os.path.join(base_dir, "field_validation_v20.json")
        
        if not os.path.exists(mapping_path):
            logging.error(f"Field mapping bestand niet gevonden: {mapping_path}")
            return None
        
        with open(mapping_path, 'r', encoding='utf-8') as file:
            config = json.load(file)
            logging.info(f"Field mapping geladen uit: {mapping_path}")
            return config
            
    except Exception as e:
        logging.error(f"Fout bij laden field mapping: {e}")
        return None


def load_institution_codes() -> Dict[str, str]:
    """
    Laadt institution codes uit configuratie bestand.
    
    Returns:
        Dict met institution code mapping: {code: full_name}
    """
    try:
        # Zoek institution_codes.json in Template Generator Files directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        codes_path = os.path.join(base_dir, "Template Generator Files", "institution_codes.json")
        
        if os.path.exists(codes_path):
            with open(codes_path, 'r', encoding='utf-8') as file:
                config = json.load(file)
                institution_mapping = config.get('institution_mapping', {})
                
                # Converteer naar simple code -> name mapping
                simple_mapping = {}
                for code, info in institution_mapping.items():
                    simple_mapping[code] = info.get('name', code)
                
                logging.info(f"Institution codes geladen uit config: {len(simple_mapping)} instellingen")
                return simple_mapping
        else:
            logging.warning(f"Institution codes config niet gevonden: {codes_path}")
            return get_fallback_institution_codes()
            
    except Exception as e:
        logging.error(f"Fout bij laden institution codes: {e}")
        return get_fallback_institution_codes()


def get_fallback_institution_codes() -> Dict[str, str]:
    """
    Fallback institution codes als config bestand niet beschikbaar is.
    
    Returns:
        Dict met hardcoded institution mapping
    """
    return {
        "umcu": "UMC Utrecht",
        "lumc": "LUMC Leiden", 
        "amcu": "Amsterdam UMC",
        "mumc": "Maastricht UMC+",
        "umcg": "UMCG Groningen",
        "sq": "Sanquin",
        "pmc": "Prinses Máxima Centrum",
        "pb": "Prothya Biosolutions",
        "ul": "Universiteit Leiden",
        "uu": "Universiteit Utrecht", 
        "uva": "Universiteit van Amsterdam",
        "zxl": "ZorgService XL",
        "algemeen": "Algemeen gebruik"
    }


def detect_json_version(validation_config: Dict) -> str:
    """
    Detecteert de versie van validation config JSON.
    
    Args:
        validation_config: Geladen JSON configuratie
        
    Returns:
        Versie string ("v18", "v20", etc.)
    """
    try:
        # Check voor expliciete versie field
        if 'version' in validation_config:
            version = validation_config['version']
            logging.info(f"JSON versie gedetecteerd via version field: {version}")
            return version
        
        # Check voor v20 kenmerken
        if 'fields' in validation_config and isinstance(validation_config['fields'], dict):
            # V20 heeft field objects met visibility/mandatory properties
            sample_field = next(iter(validation_config['fields'].values()), {})
            if 'visibility' in sample_field or 'mandatory' in sample_field:
                logging.info("JSON versie gedetecteerd als v20 (field objects)")
                return "v20"
        
        # Default naar v18
        logging.info("JSON versie gedetecteerd als v18 (legacy format)")
        return "v18"
        
    except Exception as e:
        logging.error(f"Fout bij JSON versie detectie: {e}")
        return "v18"  # Safe fallback


def normalize_v20_to_v18_structure(validation_config: Dict, reference_lists: Dict = None) -> Dict:
    """
    Normaliseert v20 configuratie naar v18 compatibele structuur.
    
    Args:
        validation_config: V20 configuratie dict
        reference_lists: Optional reference lists dict
        
    Returns:
        V18 compatibele configuratie dict
    """
    try:
        if detect_json_version(validation_config) == "v18":
            # Al in v18 format
            return validation_config
        
        logging.info("Normaliseren v20 naar v18 structuur...")
        
        normalized_config = {
            "template_config": {},
            "field_validation": {},
            "version": "v18_normalized"
        }
        
        # Template config sectie
        if "template_config" in validation_config:
            normalized_config["template_config"] = validation_config["template_config"]
        
        # Field validation normalisatie
        if "fields" in validation_config:
            field_validation = {}
            
            for field_name, field_config in validation_config["fields"].items():
                if isinstance(field_config, dict):
                    # V20 field config naar V18 format
                    v18_field = {}
                    
                    # Validatie regels
                    if "validation" in field_config:
                        validation = field_config["validation"]
                        
                        # Required regel
                        if validation.get("required", False):
                            v18_field["required"] = True
                        
                        # Data type
                        if "data_type" in validation:
                            v18_field["data_type"] = validation["data_type"]
                        
                        # Min/max values
                        if "min_value" in validation:
                            v18_field["min_value"] = validation["min_value"]
                        if "max_value" in validation:
                            v18_field["max_value"] = validation["max_value"]
                        
                        # Reference list
                        if "reference_list" in validation:
                            ref_list_name = validation["reference_list"]
                            if reference_lists and ref_list_name in reference_lists:
                                v18_field["allowed_values"] = reference_lists[ref_list_name]
                        
                        # Pattern validation
                        if "pattern" in validation:
                            v18_field["pattern"] = validation["pattern"]
                    
                    if v18_field:  # Alleen toevoegen als er validatie regels zijn
                        field_validation[field_name] = v18_field
            
            normalized_config["field_validation"] = field_validation
        
        logging.info(f"V20 naar V18 normalisatie voltooid: {len(normalized_config.get('field_validation', {}))} velden")
        return normalized_config
        
    except Exception as e:
        logging.error(f"Fout bij v20 naar v18 normalisatie: {e}")
        return validation_config  # Return original bij fout


def _map_v20_condition_to_v18(v20_condition: str) -> str:
    """
    Mapt V20 conditie syntax naar V18 format.
    
    Args:
        v20_condition: V20 conditie string
        
    Returns:
        V18 compatibele conditie string
    """
    try:
        # V20 -> V18 condition mapping
        condition_map = {
            "medical": "medisch",
            "facility": "facilitair", 
            "lab": "laboratorium",
            "other": "overige",
            "nfu": "nfu_hospitals",
            "research": "research_institutes"
        }
        
        v18_condition = v20_condition
        for v20_term, v18_term in condition_map.items():
            v18_condition = v18_condition.replace(v20_term, v18_term)
            
        return v18_condition
        
    except Exception as e:
        logging.error(f"Fout bij conditie mapping: {e}")
        return v20_condition