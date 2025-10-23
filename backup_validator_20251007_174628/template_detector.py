"""
Template Detectie Module

Deze module implementeert de TG → N → O beslissingsboom voor template type detectie.
"""

import logging
import pandas as pd
from typing import Dict, Any, Optional


def determine_template_type(excel_path: str) -> str:
    """
    Bepaalt het type template volgens beslissingsboom:
    
    1. TG (Template Generator): Stamp in A1 + A2
    2. N (Nieuwe Generatie): "Is BestelbareEenheid" + "Omschrijving Verpakkingseenheid" aanwezig  
    3. O (Oude/Alternatieve): Alle andere templates
    
    Args:
        excel_path: Pad naar Excel bestand
        
    Returns:
        'TG' - Template Generator (met stamp metadata)
        'N' - Nieuwe Generatie Template (versie 24.1+)
        'O' - Oude/Alternatieve Template (voor nov 2024 of supplier templates)
    """
    try:
        # STAP 1: Check voor Template Generator stamp in A1 + A2
        if has_template_generator_stamp(excel_path):
            logging.info("Template type: TG (Template Generator) - stamp gedetecteerd")
            return "TG"
        
        # STAP 2: Check voor Nieuwe Generatie Template markers
        try:
            df = pd.read_excel(excel_path, nrows=0)  # Alleen headers laden
            columns = [str(col).strip().lower() for col in df.columns]
            
            # Nieuwe Generatie markers (altijd aanwezig in templates na nov 2024)
            nieuwe_generatie_markers = [
                'is bestelbarereenheid',
                'omschrijving verpakkingseenheid'
            ]
            
            # Check of minimaal één van de markers aanwezig is
            has_markers = any(
                any(marker in col for col in columns) 
                for marker in nieuwe_generatie_markers
            )
            
            if has_markers:
                logging.info("Template type: N (Nieuwe Generatie) - nieuwe template structuur gedetecteerd")
                return "N"
            else:
                logging.info("Template type: O (Oude/Alternatieve) - geen nieuwe generatie markers gevonden")
                return "O"
                
        except Exception as e:
            logging.warning(f"Fout bij kolom analyse voor template type: {e}")
            return "O"  # Default naar oude template bij fout
            
    except Exception as e:
        logging.error(f"Fout bij template type detectie: {e}")
        return "O"  # Default fallback


def has_template_generator_stamp(excel_path: str) -> bool:
    """
    Controleert of er een Template Generator stamp aanwezig is.
    
    Template Generator plaatst stamp code op verschillende locaties:
    1. In A1 cel (oude format)
    2. In eerste kolom header (nieuwe format)
    Format: "S-LM-0-0-0-ul-V78-M18" of in header: "deze code niet verwijderen:\ns-lm-0-0-0-ul-v78-m18"
    
    Args:
        excel_path: Pad naar Excel bestand
        
    Returns:
        True als Template Generator stamp wordt gedetecteerd
    """
    try:
        # Controleer A1 cel (oude format)
        df_cells = pd.read_excel(excel_path, nrows=2, usecols=[0, 1])
        if not df_cells.empty and len(df_cells.columns) > 0:
            a1_value = str(df_cells.iloc[0, 0]).strip() if pd.notna(df_cells.iloc[0, 0]) else ""
            
            # Template Generator stamp pattern: "S-" of "F-" gevolgd door meer codes
            if a1_value and (a1_value.startswith("S-") or a1_value.startswith("F-")):
                # Verificeer dat het een echte TG code is (bevat V## en M##)
                if "V" in a1_value and "M" in a1_value and "-" in a1_value:
                    logging.info(f"Template Generator stamp gedetecteerd in A1: {a1_value}")
                    return True
        
        # Controleer kolom headers (nieuwe format)  
        df_headers = pd.read_excel(excel_path, nrows=0)
        for col in df_headers.columns:
            col_str = str(col).lower().strip()
            
            # Check voor TG stamp in header
            if "deze code niet verwijderen" in col_str or "s-" in col_str or "f-" in col_str:
                # Zoek naar TG code pattern in header
                lines = col_str.split('\n')
                for line in lines:
                    line = line.strip()
                    # Check voor TG code pattern
                    if (line.startswith("s-") or line.startswith("f-")) and "v" in line and "m" in line:
                        logging.info(f"Template Generator stamp gedetecteerd in header: {line}")
                        return True
        
        return False
        
    except Exception as e:
        logging.error(f"Fout bij Template Generator stamp detectie: {e}")
        return False


def test_template_detection(excel_path: str) -> Dict[str, Any]:
    """
    Test utility voor template detectie - geeft gedetailleerde informatie.
    
    Args:
        excel_path: Pad naar Excel bestand
        
    Returns:
        Dict met detectie resultaten en debug info
    """
    try:
        result = {
            'excel_path': excel_path,
            'template_type': None,
            'has_tg_stamp': False,
            'tg_stamp_value': None,
            'heeft_nieuwe_generatie_markers': False,
            'gevonden_markers': [],
            'alle_kolommen': [],
            'debug_info': []
        }
        
        # Test TG stamp
        result['has_tg_stamp'] = has_template_generator_stamp(excel_path)
        if result['has_tg_stamp']:
            # Haal stamp waarde op
            try:
                df = pd.read_excel(excel_path, nrows=1, usecols=[0])
                if not df.empty:
                    result['tg_stamp_value'] = str(df.iloc[0, 0]).strip()
            except:
                pass
        
        # Test Nieuwe Generatie markers
        try:
            df = pd.read_excel(excel_path, nrows=0)
            columns = [str(col).strip().lower() for col in df.columns]
            result['alle_kolommen'] = columns
            
            nieuwe_generatie_markers = [
                'is bestelbarereenheid',
                'omschrijving verpakkingseenheid'
            ]
            
            gevonden_markers = []
            for marker in nieuwe_generatie_markers:
                if any(marker in col for col in columns):
                    gevonden_markers.append(marker)
            
            result['gevonden_markers'] = gevonden_markers
            result['heeft_nieuwe_generatie_markers'] = len(gevonden_markers) > 0
            
        except Exception as e:
            result['debug_info'].append(f"Fout bij kolom analyse: {e}")
        
        # Bepaal template type
        result['template_type'] = determine_template_type(excel_path)
        
        return result
        
    except Exception as e:
        logging.error(f"Fout bij template detectie test: {e}")
        return {'error': str(e)}