"""
Utils Module

Deze module bevat helper functies en utilities die door andere modules gebruikt worden.
"""

import logging
import re
import os
from typing import Any, Dict, List, Optional, Union


def safe_get_nested_value(data: Dict, keys: str, default: Any = None) -> Any:
    """
    Veilig ophalen van geneste waarden uit dict met dot notation.
    
    Args:
        data: Dict om waarde uit op te halen
        keys: Dot-separated keys (bijv. 'stamp_data.institutions')
        default: Default waarde als key niet bestaat
        
    Returns:
        Waarde of default
    """
    try:
        value = data
        for key in keys.split('.'):
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    except (KeyError, TypeError, AttributeError):
        return default


def safe_list_get(lst: List, index: int, default: Any = None) -> Any:
    """
    Veilig ophalen van list element op index.
    
    Args:
        lst: List om element uit op te halen
        index: Index van element
        default: Default waarde als index niet bestaat
        
    Returns:
        Element of default waarde
    """
    try:
        if isinstance(lst, list) and 0 <= index < len(lst):
            return lst[index]
        return default
    except (IndexError, TypeError):
        return default


def normalize_string_for_comparison(text: str) -> str:
    """
    Normaliseert string voor vergelijking (lowercase, stripped, geen speciale tekens).
    
    Args:
        text: String om te normaliseren
        
    Returns:
        Genormaliseerde string
    """
    try:
        if not text:
            return ""
        
        # Converteer naar string en lowercase
        normalized = str(text).lower().strip()
        
        # Vervang speciale tekens en spaties door underscores
        normalized = re.sub(r'[^\w\s]', '', normalized)
        normalized = re.sub(r'\s+', '_', normalized)
        
        return normalized
    except Exception as e:
        logging.error(f"Fout bij string normalisatie: {e}")
        return str(text).lower() if text else ""


def is_empty_value(value: Any) -> bool:
    """
    Controleert of waarde leeg/None/NaN is.
    
    Args:
        value: Waarde om te controleren
        
    Returns:
        True als waarde leeg is
    """
    try:
        import pandas as pd
        
        # Pandas NaN check
        if pd.isna(value):
            return True
        
        # None check
        if value is None:
            return True
        
        # String check
        if isinstance(value, str):
            return value.strip() == ""
        
        # List/dict empty check
        if isinstance(value, (list, dict)):
            return len(value) == 0
        
        return False
        
    except Exception:
        return value is None or (isinstance(value, str) and value.strip() == "")


def convert_to_number(value: Any, default: Union[int, float, None] = None) -> Union[int, float, None]:
    """
    Probeert waarde te converteren naar nummer.
    
    Args:
        value: Waarde om te converteren
        default: Default waarde als conversie faalt
        
    Returns:
        Nummer of default waarde
    """
    try:
        if is_empty_value(value):
            return default
        
        # String preprocessing
        if isinstance(value, str):
            # Vervang comma door punt voor decimalen
            value = value.strip().replace(',', '.')
            
            # Verwijder whitespace en currency symbolen
            value = re.sub(r'[€$£¥\s]', '', value)
        
        # Probeer int conversie eerst
        try:
            num = float(value)
            if num.is_integer():
                return int(num)
            return num
        except (ValueError, TypeError):
            return default
            
    except Exception as e:
        logging.error(f"Fout bij nummer conversie voor '{value}': {e}")
        return default


def format_error_message(error_type: str, field_name: str, value: Any, 
                        additional_info: str = None) -> str:
    """
    Formatteert error message voor consistente foutmeldingen.
    
    Args:
        error_type: Type van fout
        field_name: Naam van veld
        value: Waarde die fout veroorzaakt
        additional_info: Extra informatie
        
    Returns:
        Geformatteerde foutmelding
    """
    try:
        base_messages = {
            'required_field_missing': f"Verplicht veld '{field_name}' is leeg",
            'invalid_data_type': f"Waarde '{value}' heeft niet het juiste data type voor '{field_name}'",
            'value_too_long': f"Waarde '{value}' in '{field_name}' is te lang",
            'value_too_short': f"Waarde '{value}' in '{field_name}' is te kort", 
            'invalid_format': f"Waarde '{value}' in '{field_name}' heeft geen geldige format",
            'value_not_allowed': f"Waarde '{value}' is niet toegestaan voor '{field_name}'",
            'value_out_of_range': f"Waarde '{value}' in '{field_name}' valt buiten toegestane bereik"
        }
        
        message = base_messages.get(error_type, f"Validatie fout in '{field_name}': {value}")
        
        if additional_info:
            message += f" ({additional_info})"
            
        return message
        
    except Exception as e:
        logging.error(f"Fout bij error message formatting: {e}")
        return f"Validatie fout in '{field_name}'"


def ensure_directory_exists(directory_path: str) -> bool:
    """
    Zorgt ervoor dat directory bestaat.
    
    Args:
        directory_path: Pad naar directory
        
    Returns:
        True als directory bestaat of succesvol aangemaakt
    """
    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path, exist_ok=True)
            logging.info(f"Directory aangemaakt: {directory_path}")
        return True
    except Exception as e:
        logging.error(f"Kon directory niet aanmaken {directory_path}: {e}")
        return False


def generate_filename_timestamp() -> str:
    """
    Genereert timestamp string voor bestandsnamen.
    
    Returns:
        Timestamp string in format YYYYMMDD_HHMMSS
    """
    try:
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    except Exception as e:
        logging.error(f"Fout bij timestamp generatie: {e}")
        return "unknown_time"


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Kort string af tot maximale lengte.
    
    Args:
        text: String om af te korten
        max_length: Maximale lengte
        suffix: Suffix om toe te voegen (wordt meegeteld in max_length)
        
    Returns:
        Afgekorte string
    """
    try:
        if not text or len(text) <= max_length:
            return str(text) if text else ""
        
        truncated_length = max_length - len(suffix)
        if truncated_length < 0:
            return suffix[:max_length]
            
        return text[:truncated_length] + suffix
        
    except Exception as e:
        logging.error(f"Fout bij string truncate: {e}")
        return str(text)[:max_length] if text else ""


def deep_merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """
    Voegt twee dicts recursief samen.
    
    Args:
        dict1: Eerste dict (basis)
        dict2: Tweede dict (overschrijft dict1 waarden)
        
    Returns:
        Samengevoegde dict
    """
    try:
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = deep_merge_dicts(result[key], value)
            else:
                result[key] = value
        
        return result
        
    except Exception as e:
        logging.error(f"Fout bij dict merge: {e}")
        return dict1.copy()


def extract_numeric_from_string(text: str) -> Optional[float]:
    """
    Extraheert eerste numerieke waarde uit string.
    
    Args:
        text: String om nummer uit te extraheren
        
    Returns:
        Numerieke waarde of None
    """
    try:
        if not text:
            return None
        
        # Zoek naar eerste numerieke patroon
        pattern = r'[-+]?\d*\.?\d+'
        match = re.search(pattern, str(text))
        
        if match:
            return float(match.group().replace(',', '.'))
        
        return None
        
    except Exception as e:
        logging.error(f"Fout bij numeric extractie uit '{text}': {e}")
        return None


def batch_process_list(items: List, batch_size: int = 100):
    """
    Generator voor batch processing van lijst.
    
    Args:
        items: Lijst om in batches te verwerken
        batch_size: Grootte van elke batch
        
    Yields:
        Batch van items
    """
    try:
        for i in range(0, len(items), batch_size):
            yield items[i:i + batch_size]
    except Exception as e:
        logging.error(f"Fout bij batch processing: {e}")
        yield items  # Fallback: hele lijst als één batch


def validate_file_path(file_path: str, must_exist: bool = True) -> bool:
    """
    Valideert bestandspad.
    
    Args:
        file_path: Pad naar bestand
        must_exist: Of bestand moet bestaan
        
    Returns:
        True als bestandspad geldig is
    """
    try:
        if not file_path or not isinstance(file_path, str):
            return False
        
        # Check of pad geldig format heeft
        if not os.path.isabs(file_path) and not os.path.exists(file_path):
            return False
        
        # Check of bestand moet bestaan
        if must_exist and not os.path.exists(file_path):
            return False
        
        # Check of parent directory bestaat (voor nieuwe bestanden)
        if not must_exist:
            parent_dir = os.path.dirname(file_path)
            if parent_dir and not os.path.exists(parent_dir):
                return False
        
        return True
        
    except Exception as e:
        logging.error(f"Fout bij file path validatie: {e}")
        return False


def get_file_extension(file_path: str) -> str:
    """
    Haalt bestandsextensie op.
    
    Args:
        file_path: Pad naar bestand
        
    Returns:
        Bestandsextensie (zonder punt) of lege string
    """
    try:
        if not file_path:
            return ""
        
        _, ext = os.path.splitext(file_path)
        return ext.lstrip('.').lower()
        
    except Exception as e:
        logging.error(f"Fout bij extensie extractie: {e}")
        return ""


def count_non_empty_values(data: Union[List, Dict]) -> int:
    """
    Telt niet-lege waarden in lijst of dict.
    
    Args:
        data: Lijst of dict om te tellen
        
    Returns:
        Aantal niet-lege waarden
    """
    try:
        if isinstance(data, list):
            return sum(1 for item in data if not is_empty_value(item))
        elif isinstance(data, dict):
            return sum(1 for value in data.values() if not is_empty_value(value))
        else:
            return 1 if not is_empty_value(data) else 0
            
    except Exception as e:
        logging.error(f"Fout bij counting non-empty values: {e}")
        return 0


def create_lookup_dict(items: List[Dict], key_field: str, value_field: str = None) -> Dict:
    """
    Creëert lookup dictionary uit lijst van dicts.
    
    Args:
        items: Lijst van dicts
        key_field: Veld om als key te gebruiken
        value_field: Veld om als waarde te gebruiken (of hele dict als None)
        
    Returns:
        Lookup dictionary
    """
    try:
        lookup = {}
        
        for item in items:
            if isinstance(item, dict) and key_field in item:
                key = item[key_field]
                value = item[value_field] if value_field and value_field in item else item
                lookup[key] = value
        
        return lookup
        
    except Exception as e:
        logging.error(f"Fout bij lookup dict creatie: {e}")
        return {}