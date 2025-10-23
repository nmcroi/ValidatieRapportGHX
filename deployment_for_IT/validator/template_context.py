"""
Template Context Module

Deze module extraheert en parseert metadata uit Template Generator templates.
"""

import logging
import pandas as pd
import re
from typing import Dict, Any, Optional, List


def extract_template_generator_context(excel_path: str) -> Optional[Dict[str, Any]]:
    """
    Extraheert volledige Template Generator context uit Excel metadata.
    
    Args:
        excel_path: Pad naar Template Generator Excel bestand
        
    Returns:
        Dict met volledige TG context of None als geen TG template
    """
    try:
        # Check eerst of het een TG template is
        from .template_detector import has_template_generator_stamp
        if not has_template_generator_stamp(excel_path):
            return None
        
        # Laad eerste paar rijen voor stamp parsing
        df = pd.read_excel(excel_path, nrows=5)
        
        context = {
            'template_type': 'TG',
            'excel_path': excel_path,
            'stamp_data': {},
            'version_info': {},
            'parsed_config': {},
            'institution_info': {}
        }
        
        # Parse stamp uit A1 of header
        stamp_code = None
        
        # Probeer A1 eerst
        if not df.empty and len(df.columns) > 0:
            a1_value = str(df.iloc[0, 0]).strip() if pd.notna(df.iloc[0, 0]) else ""
            if a1_value and (a1_value.startswith("S-") or a1_value.startswith("F-")):
                stamp_code = a1_value
        
        # Als geen A1 stamp, check headers
        if not stamp_code:
            df_headers = pd.read_excel(excel_path, nrows=0)
            for col in df_headers.columns:
                col_str = str(col).lower().strip()
                if "deze code niet verwijderen" in col_str:
                    lines = col_str.split('\n')
                    for line in lines:
                        line = line.strip()
                        if (line.startswith("s-") or line.startswith("f-")) and "v" in line and "m" in line:
                            stamp_code = line.upper()  # Normalize to uppercase
                            break
                    if stamp_code:
                        break
        
        if stamp_code:
            stamp_data = parse_template_code(stamp_code)
            context['stamp_data'] = stamp_data
            context['parsed_config'] = stamp_data  # Backward compatibility
            
            logging.info(f"TG context geëxtraheerd: {stamp_data.get('template_type', 'Unknown')} template")
        
        # Parse versie info uit A2 indien beschikbaar
        if len(df) > 1 and len(df.columns) > 0:
            a2_value = str(df.iloc[1, 0]).strip() if pd.notna(df.iloc[1, 0]) else ""
            if a2_value:
                version_info = parse_version_line(a2_value)
                context['version_info'] = version_info
        
        # Voeg institution mapping toe
        if 'institutions' in context['stamp_data']:
            from .config_manager import load_institution_codes
            institution_codes = load_institution_codes()
            institution_info = {}
            
            for inst_code in context['stamp_data']['institutions']:
                if inst_code in institution_codes:
                    institution_info[inst_code] = institution_codes[inst_code]
            
            context['institution_info'] = institution_info
        
        return context
        
    except Exception as e:
        logging.error(f"Fout bij TG context extractie: {e}")
        return None


def parse_template_code(template_code: str) -> Dict[str, Any]:
    """
    Parseert Template Generator code naar configuratie dict.
    
    Template code format: S-LM-0-0-0-ul-V78-M18
    - S/F: Standard/Staffel template type
    - LM: Product types (L=Lab, M=Medisch)
    - 0/1: Chemicals (0=Nee, 1=Ja)
    - 0/1: Staffel (0=Nee, 1=Ja) 
    - 0/1: GS1 mode (0=Alleen GHX, 1=Ook GS1)
    - ul: Institution codes
    - V78: Visible field count
    - M18: Mandatory field count
    
    Args:
        template_code: Template Generator stamp code
        
    Returns:
        Dict met geparsede configuratie
    """
    try:
        parts = template_code.strip().split('-')
        
        if len(parts) < 8:
            logging.warning(f"Template code heeft niet genoeg onderdelen: {template_code}")
            return {'raw_code': template_code, 'parse_error': 'Insufficient parts'}
        
        # Parse alle onderdelen
        config = {
            'raw_code': template_code,
            'template_choice': 'staffel' if parts[0] == 'F' else 'standard',
            'product_types': _parse_product_types(parts[1]),
            'has_chemicals': parts[2] == '1',
            'is_staffel_file': parts[3] == '1',
            'gs1_mode': 'also_gs1' if parts[4] == '1' else 'ghx_only',
            'institutions': _parse_institutions(parts[5]),
            'visible_fields': int(parts[6].replace('V', '')),
            'mandatory_fields': int(parts[7].replace('M', ''))
        }
        
        # Voeg template_type toe voor backward compatibility
        config['template_type'] = config['template_choice']
        
        logging.info(f"Template code geparsed: {config['template_choice']} template, "
                    f"{len(config['product_types'])} product types, "
                    f"{len(config['institutions'])} instellingen")
        
        return config
        
    except Exception as e:
        logging.error(f"Fout bij template code parsing: {e}")
        return {
            'raw_code': template_code,
            'parse_error': str(e),
            'template_choice': 'standard',
            'product_types': [],
            'institutions': []
        }


def _parse_product_types(type_code: str) -> List[str]:
    """
    Parseert product type codes naar lijst van types.
    
    Args:
        type_code: Product type code (F, M, L, O, FM, FML, etc.)
        
    Returns:
        Lijst van product type strings
    """
    type_mapping = {
        'F': 'facilitair',
        'M': 'medisch', 
        'L': 'laboratorium',
        'O': 'overige'
    }
    
    types = []
    for char in type_code.upper():
        if char in type_mapping:
            types.append(type_mapping[char])
    
    return types if types else ['medisch']  # Default fallback


def _parse_institutions(inst_code: str) -> List[str]:
    """
    Parseert institution code naar lijst van institution codes.
    
    Template Generator gebruikt enkele codes zoals:
    - ul = Universiteit Leiden
    - umcu = UMC Utrecht  
    - alle_nfu = Alle NFU ziekenhuizen
    
    Args:
        inst_code: Institution code uit template
        
    Returns:
        Lijst van institution codes
    """
    # Special multi-institution codes
    if inst_code == 'alle_nfu':
        return ['umcu', 'lumc', 'amcu', 'mumc', 'umcg']
    elif inst_code == 'alle_uni':
        return ['ul', 'uu', 'uva']
    
    # Single institution - return as list voor consistentie
    return [inst_code]


def parse_version_line(version_line: str) -> Dict[str, str]:
    """
    Parseert versie informatie uit A2 cel.
    
    Args:
        version_line: Versie string uit A2
        
    Returns:
        Dict met versie informatie
    """
    try:
        version_info = {
            'raw_version': version_line,
            'version': None,
            'release_date': None
        }
        
        # Zoek versie nummer patroon (V25.1, versie 25.1, etc.)
        version_patterns = [
            r'[Vv](\d+\.?\d*)',  # V25.1 of v25.1
            r'versie[:\s]+(\d+\.?\d*)',  # versie: 25.1
            r'Template versie[:\s]+V?(\d+\.?\d*)'  # Template versie: V25.1
        ]
        
        for pattern in version_patterns:
            match = re.search(pattern, version_line, re.IGNORECASE)
            if match:
                version_info['version'] = match.group(1)
                break
        
        # Zoek datum en tijd patroon - verschillende formaten
        date_patterns = [
            r'(\d{2}-\d{2}-\d{4} \d{2}:\d{2})',  # dd-mm-yyyy hh:mm
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2})',  # yyyy-mm-dd hh:mm
            r'(\d{2}-\d{2}-\d{4})',              # dd-mm-yyyy
            r'(\d{4}-\d{2}-\d{2})',              # yyyy-mm-dd
        ]
        
        for pattern in date_patterns:
            date_match = re.search(pattern, version_line)
            if date_match:
                version_info['release_date'] = date_match.group(1)
                break
        
        return version_info
        
    except Exception as e:
        logging.error(f"Fout bij versie parsing: {e}")
        return {'raw_version': version_line}


def extract_template_code_from_a1(cell_value: str) -> Optional[str]:
    """
    Extraheert template code uit A1 cel waarde.
    
    Args:
        cell_value: Waarde uit A1 cel
        
    Returns:
        Template code string of None
    """
    try:
        if not cell_value or not isinstance(cell_value, str):
            return None
        
        cell_value = str(cell_value).strip()
        
        # Check of het een geldige template code format is
        if re.match(r'^[SF]-[FMLO]+-[01]-[01]-[01]-\w+-V\d+-M\d+$', cell_value):
            return cell_value
        
        return None
        
    except Exception as e:
        logging.error(f"Fout bij A1 template code extractie: {e}")
        return None


def extract_version_info_from_sheet(worksheet) -> Dict[str, str]:
    """
    Extraheert versie informatie uit Excel worksheet.
    
    Args:
        worksheet: Openpyxl worksheet object
        
    Returns:
        Dict met versie informatie
    """
    try:
        version_info = {}
        
        # Check A2 voor versie info
        a2_cell = worksheet['A2']
        if a2_cell.value:
            version_data = parse_version_line(str(a2_cell.value))
            version_info.update(version_data)
        
        # Check andere bekende locaties voor metadata
        metadata_cells = ['B1', 'C1', 'A3', 'B2']
        for cell_ref in metadata_cells:
            cell = worksheet[cell_ref]
            if cell.value and 'versie' in str(cell.value).lower():
                extra_version = parse_version_line(str(cell.value))
                if extra_version.get('version') and not version_info.get('version'):
                    version_info.update(extra_version)
        
        return version_info
        
    except Exception as e:
        logging.error(f"Fout bij worksheet versie extractie: {e}")
        return {}


def detect_chemical_fields_in_template(excel_path: str) -> bool:
    """
    Detecteert of een template chemical fields bevat door header analysis.
    
    Deze functie is specifiek voor AT (Alternative Template) bestanden die
    geen Template Generator stamp hebben maar wel chemical fields kunnen bevatten.
    
    Args:
        excel_path: Pad naar Excel bestand
        
    Returns:
        True als chemical fields gedetecteerd, anders False
    """
    try:
        # Laad alleen headers (eerste rij)
        df = pd.read_excel(excel_path, nrows=0)
        headers = [str(col).lower().strip() for col in df.columns]
        
        # Chemical field patterns om te detecteren
        chemical_patterns = [
            'adr',
            'gevarenklasse',
            'danger',
            'stofnaam',
            'substance',
            'chemical',
            'brutoformule',
            'formula',
            'cas',
            'un-nummer',
            'un nummer',
            'veiligheidsblad',
            'sds',
            'vib'
        ]
        
        # Check of headers chemical patterns bevatten
        chemical_count = 0
        found_patterns = []
        
        for header in headers:
            for pattern in chemical_patterns:
                if pattern in header:
                    chemical_count += 1
                    found_patterns.append(pattern)
                    break  # Avoid counting same header multiple times
        
        # Als 2 of meer chemical patterns gevonden, waarschijnlijk chemical template
        has_chemicals = chemical_count >= 2
        
        if has_chemicals:
            logging.info(f"Chemical fields gedetecteerd in template: {found_patterns}")
        else:
            logging.debug(f"Geen significante chemical fields gedetecteerd ({chemical_count} patterns)")
        
        return has_chemicals
        
    except Exception as e:
        logging.error(f"Fout bij chemical field detectie: {e}")
        return False