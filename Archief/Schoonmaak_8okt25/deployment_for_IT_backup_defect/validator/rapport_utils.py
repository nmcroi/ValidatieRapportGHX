# rapport_utils.py

import pandas as pd
import logging
import os
import json
import xlsxwriter  # Nodig voor pd.ExcelWriter engine en grafieken
from datetime import datetime
from typing import Dict, List, Tuple, Any  # Type hints zijn goed om te behouden

# -----------------------------
# SERVER PATH CONFIGURATION
# -----------------------------

def load_server_paths():
    """
    Laadt server paths uit configuratie bestand.
    Fallback naar development paths als config niet beschikbaar is.
    """
    try:
        # Zoek server_paths.json in config directory
        config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")
        server_paths_file = os.path.join(config_dir, "server_paths.json")
        
        if os.path.exists(server_paths_file):
            with open(server_paths_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get("server_paths", {})
        else:
            logging.warning(f"Server paths config niet gevonden: {server_paths_file}, gebruik fallback paths")
            return get_fallback_server_paths()
            
    except Exception as e:
        logging.error(f"Fout bij laden server paths: {e}, gebruik fallback paths")
        return get_fallback_server_paths()

def get_fallback_server_paths():
    """
    Fallback server paths voor development omgeving.
    """
    return {
        "logo_path": "/Users/ncroiset/Vibe Coding Projecten/Cursor Projecten/Project GHX Prijstemplate Validatie Tool/static/ghx_logo_2.png",
        "validation_log_file": "/Users/ghxnielscroiset/Library/CloudStorage/OneDrive-GlobalHealthcareExchange/GHX ValidatieRapporten/validaties_overzicht.xlsx",
        "template_generator_files": "Template Generator Files",
        "temp_reports_dir": "/tmp/validation_reports"
    }

# Laad server paths bij import
SERVER_PATHS = load_server_paths()

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------

def detect_data_start_row(excel_path: str) -> int:
    """
    Detecteert op welke rij de data daadwerkelijk begint in het Excel bestand.
    Voor TG templates kan dit rij 4 zijn, voor DT templates rij 3.
    
    Args:
        excel_path: Pad naar het Excel bestand
        
    Returns:
        int: Rijnummer waar data begint (1-indexed, zoals Excel)
    """
    try:
        logging.info(f"DEBUG Sheet 7: Detecteer data start row voor {excel_path}")
        
        # Lees de eerste paar rijen om de structuur te analyseren
        df_peek = pd.read_excel(excel_path, nrows=10, header=None)
        
        # Zoek naar de eerste rij die echte data bevat
        # Data begint meestal na de header rij
        for i in range(len(df_peek)):
            row = df_peek.iloc[i]
            # Check of deze rij data bevat (niet alleen headers of lege cellen)
            non_empty_cells = row.dropna().astype(str).str.strip()
            non_empty_cells = non_empty_cells[non_empty_cells != '']
            
            # Als meer dan 3 gevulde cellen en geen typische header woorden
            if len(non_empty_cells) > 3:
                # Check of dit geen header rij is
                row_text = ' '.join(non_empty_cells.str.lower())
                header_keywords = ['artikel', 'prijs', 'naam', 'nummer', 'omschrijving', 'eenheid', 'code']
                
                # Als het weinig header keywords bevat, is het waarschijnlijk data
                keyword_count = sum(1 for keyword in header_keywords if keyword in row_text)
                if keyword_count < 2:  # Minder dan 2 header woorden = waarschijnlijk data
                    logging.info(f"DEBUG Sheet 7: Data gevonden op rij {i}, Excel rij {i + 1}")
                    return i + 1  # Excel rijnummering is 1-indexed
        
        # Fallback: gebruik rij 3 als default (meeste templates)
        logging.info("DEBUG Sheet 7: Geen data rij gedetecteerd, gebruik default rij 3")
        return 3
        
    except Exception as e:
        logging.warning(f"DEBUG Sheet 7: Kon data start rij niet detecteren voor {excel_path}: {e}")
        return 3  # Safe fallback

# -----------------------------
# NEW INTUITIVE SCORE CALCULATION
# -----------------------------

def load_uom_penalty_config():
    """Laad UOM penalty configuratie."""
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'uom_penalty_config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Kon UOM penalty config niet laden: {e}")
        # Fallback config
        return {
            "uom_penalty_codes": ["720", "724", "752", "753", "754", "755", "722"],
            "penalty_structure": {"penalty_single": -1, "penalty_10_percent": -3, "penalty_25_percent": -5},
            "template_penalties": {"TG": 0, "DT": 0, "AT": -25}
        }

def calculate_uom_penalties(df_errors_mand, df_errors_non_mand, total_rows):
    """
    Berekent UOM penalty's op basis van foutcodes en hun frequentie.
    
    Args:
        df_errors_mand: DataFrame met mandatory field errors
        df_errors_non_mand: DataFrame met non-mandatory field errors  
        total_rows: Totaal aantal rijen in dataset
        
    Returns:
        int: Totale penalty punten (negatief getal)
    """
    try:
        config = load_uom_penalty_config()
        uom_codes = set(config["uom_penalty_codes"])
        penalty_struct = config["penalty_structure"]
        
        total_penalty = 0
        
        # Combineer alle errors
        all_errors = pd.concat([df_errors_mand, df_errors_non_mand], ignore_index=True) if len(df_errors_mand) > 0 or len(df_errors_non_mand) > 0 else pd.DataFrame()
        
        if len(all_errors) == 0 or total_rows == 0:
            return 0
            
        # Group by error code en tel frequentie  
        # Controleer welke kolom naam wordt gebruikt voor error codes
        code_column = None
        if 'code' in all_errors.columns:
            code_column = 'code'
        elif 'Error Code' in all_errors.columns:
            code_column = 'Error Code'
        elif 'Foutcode' in all_errors.columns:
            code_column = 'Foutcode'
        
        if code_column is None:
            logging.warning("Geen foutcode kolom gevonden in error DataFrames")
            return 0
            
        code_counts = all_errors[code_column].value_counts()
        
        for error_code, count in code_counts.items():
            if str(error_code) in uom_codes:
                error_percentage = (count / total_rows) * 100
                
                if error_percentage >= 25:
                    penalty = penalty_struct["penalty_25_percent"]
                elif error_percentage >= 10:
                    penalty = penalty_struct["penalty_10_percent"]
                else:
                    penalty = penalty_struct["penalty_single"]
                    
                total_penalty += penalty
                logging.info(f"UOM penalty - Code {error_code}: {count} fouten ({error_percentage:.1f}%) → {penalty} punten")
        
        return total_penalty
        
    except Exception as e:
        logging.error(f"Fout bij UOM penalty berekening: {e}")
        return 0

def calculate_new_intuitive_score(M_found, total_mandatory, df_errors_mand, df_errors_non_mand, total_rows, template_type, volledigheids_percentage=None, juistheid_percentage=None):
    """
    Berekent de nieuwe intuïtieve score volgens de formule:
    Core = ROUND((M% × J%) ÷ 100) - UOM_Penalty's - Template_Penalty
    
    Args:
        M_found: Aantal gevonden mandatory fields
        total_mandatory: Totaal aantal mandatory fields
        df_errors_mand: DataFrame met mandatory field errors
        df_errors_non_mand: DataFrame met non-mandatory field errors
        total_rows: Totaal aantal rijen 
        template_type: Template type (TG, DT, AT)
        volledigheids_percentage: Voorberekend volledigheids percentage (optioneel)
        juistheid_percentage: Voorberekend juistheid percentage (optioneel)
        
    Returns:
        dict: Score components (M_percentage, J_percentage, core_score, penalties, final_score, grade)
    """
    try:
        config = load_uom_penalty_config()
        
        # M% = Volledigheid
        if volledigheids_percentage is not None:
            # Voor AT templates: herbereken M% op basis van 17 standaard mandatory fields
            if template_type == 'AT':
                # AT templates moeten altijd uit 17 mandatory fields berekend worden
                # Ook als er maar 10 gemapped zijn
                # volledigheids_percentage is gebaseerd op beschikbare fields, maar wij willen altijd /17
                # Schat ingevulde fields: volledigheids_percentage * total_mandatory / 100
                estimated_filled = (volledigheids_percentage * total_mandatory) / 100 if total_mandatory > 0 else 0
                M_percentage = round((estimated_filled / 17) * 100)
            else:
                # Voor TG/DT/GT: gebruik voorberekende waarde (respecteert werkelijke mandatory count)
                # GT templates kunnen 19+ mandatory fields hebben (17 default + extra van zorginstelling)
                M_percentage = round(volledigheids_percentage)
        else:
            # Fallback naar oude berekening
            M_percentage = round((M_found / total_mandatory) * 100) if total_mandatory > 0 else 0
        
        # J% = Juistheid (gebruik voorberekende waarde indien beschikbaar)
        if juistheid_percentage is not None:
            J_percentage = round(juistheid_percentage)
        else:
            # Fallback: hergebruik de bestaande totaal_juist berekening
            try:
                # Deze variabelen zijn al berekend eerder in de functie
                juistheid_percentage = (totaal_juist / total_filled_in_present) * 100 if total_filled_in_present > 0 else 0
                J_percentage = round(juistheid_percentage)
            except NameError:
                # Fallback als variabelen niet beschikbaar zijn
                J_percentage = 100 if M_found > 0 else 0
        
        # Core Score = M% × J% ÷ 100
        core_score = round((M_percentage * J_percentage) / 100)
        
        # UOM Penalty's
        uom_penalties = calculate_uom_penalties(df_errors_mand, df_errors_non_mand, total_rows)
        
        # Template Penalty
        template_penalty = config["template_penalties"].get(template_type, 0)
        
        # Final Score
        final_score = max(0, min(100, core_score + uom_penalties + template_penalty))
        
        # Grade bepaling
        if final_score >= 95:
            grade = "A+"
        elif final_score >= 90:
            grade = "A"
        elif final_score >= 80:
            grade = "B"
        elif final_score >= 70:
            grade = "C"
        elif final_score >= 60:
            grade = "D"
        elif final_score >= 50:
            grade = "E"
        else:
            grade = "F"
            
        result = {
            'M_percentage': M_percentage,
            'J_percentage': J_percentage,
            'core_score': core_score,
            'uom_penalties': uom_penalties,
            'template_penalty': template_penalty,
            'final_score': final_score,
            'grade': grade
        }
        
        logging.info(f"Nieuwe score: M={M_percentage}%, J={J_percentage}%, Core={core_score}, UOM={uom_penalties}, Template={template_penalty}, Final={final_score}({grade})")
        
        return result
        
    except Exception as e:
        logging.error(f"Fout bij nieuwe score berekening: {e}")
        # Fallback naar simpele berekening
        M_percentage = round((M_found / total_mandatory) * 100) if total_mandatory > 0 else 0
        return {
            'M_percentage': M_percentage,
            'J_percentage': 0,
            'core_score': 0,
            'uom_penalties': 0,
            'template_penalty': 0,
            'final_score': M_percentage,
            'grade': 'F'
        }

# -----------------------------
# EXCEL ERROR SUPPRESSION HELPER
# -----------------------------

def suppress_excel_errors(worksheet, max_row=1000, max_col=50):
    """
    Onderdrukt Excel groene driehoekjes (error indicators) voor veelvoorkomende waarschuwingen.
    
    Args:
        worksheet: XlsxWriter worksheet object
        max_row: Maximum rij om error suppression toe te passen
        max_col: Maximum kolom (als letter, bijv. 'AZ' voor kolom 52)
    """
    try:
        # Convert max_col number to Excel column letter if needed
        if isinstance(max_col, int):
            max_col_letter = ""
            while max_col > 0:
                max_col -= 1
                max_col_letter = chr(max_col % 26 + ord('A')) + max_col_letter
                max_col //= 26
        else:
            max_col_letter = max_col
            
        range_str = f"A1:{max_col_letter}{max_row}"
        
        # Suppress common Excel errors that cause green triangles
        error_types = {
            'number_stored_as_text': range_str,    # Numbers stored as text (most common)
            'formula_differs': range_str,          # Formula differs from adjacent cells  
            'eval_error': range_str,               # Formula evaluation errors
            'empty_cell_reference': range_str,     # Empty cell references
            'list_data_validation': range_str,     # Data validation issues
        }
        
        worksheet.ignore_errors(error_types)
        
    except Exception as e:
        # Fail silently - error suppression is niet-kritisch
        logging.debug(f"Error suppression gefaald: {e}")

# -----------------------------
# TEMPLATE DETECTIE FUNCTIES  
# -----------------------------

def has_template_generator_stamp(df: pd.DataFrame, excel_path: str = None) -> bool:
    """
    Detecteert of een DataFrame een Template Generator stamp heeft.
    
    Gebruikt echte stamp detection via Excel metadata wanneer mogelijk.
    """
    if excel_path:
        try:
            import openpyxl
            wb = openpyxl.load_workbook(excel_path, data_only=True, read_only=True)
            
            # Check voor _GHX_META sheet en GHX_STAMP named range
            has_meta_sheet = "_GHX_META" in wb.sheetnames
            has_stamp_range = "GHX_STAMP" in wb.defined_names
            
            wb.close()
            
            # Template Generator stamp vereist beide
            if has_meta_sheet and has_stamp_range:
                logging.info("Template Generator stamp gedetecteerd via Excel metadata")
                return True
                
        except Exception as e:
            logging.warning(f"Fout bij stamp detection: {e}")
    
    # Fallback: simpele heuristiek gebaseerd op kolom patterns
    tg_indicators = [
        "Context Labels",  # Mogelijk TG kolom
        "Template Preset", # Mogelijk TG kolom  
        "GHX_STAMP",      # Mogelijk TG metadata kolom
    ]
    
    has_tg_indicators = any(col in df.columns for col in tg_indicators)
    
    if has_tg_indicators:
        logging.info("Template Generator indicatoren gedetecteerd via heuristiek")
        return True
        
    return False

def extract_template_generator_info(excel_path: str) -> Dict[str, Any]:
    """
    Extraheert uitgebreide Template Generator informatie inclusief parsed codes.
    
    Args:
        excel_path: Pad naar Excel bestand
        
    Returns:
        Dictionary met template informatie of empty dict bij fout
    """
    try:
        from pathlib import Path
        import sys
        import os
        
        # Setup path voor stamp module import
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_tree_path = os.path.join(project_root, "Project TemplateTree app v3", "src")
        
        if template_tree_path not in sys.path:
            sys.path.append(template_tree_path)
        
        try:
            from stamp import TemplateStamp, TemplateCodeParser
        except ImportError:
            logging.warning("Kon stamp module niet importeren voor rapport template info")
            return {}
        
        # Laad field validation config voor code parsing
        field_validation_config = None
        validation_config_path = os.path.join(project_root, "field_validation_v20.json")
        if os.path.exists(validation_config_path):
            with open(validation_config_path, 'r', encoding='utf-8') as f:
                field_validation_config = json.load(f)
        
        # Extracteer stamp informatie
        stamp_data = TemplateStamp.extract_stamp(Path(excel_path), field_validation_config)
        
        if not stamp_data:
            return {}
            
        context_dict, preset_code, parsed_code = stamp_data
        
        # Bouw template informatie op
        template_info = {
            "has_stamp": True,
            "preset_code": preset_code,
            "is_valid": False,
            "context": {},
            "parsed_code": {}
        }
        
        if context_dict:
            template_info["context"] = context_dict.get("context", {})
            template_info["generator_info"] = context_dict.get("generator", {})
        
        if parsed_code:
            template_info["parsed_code"] = parsed_code
            template_info["template_type"] = parsed_code.get("template_type", "unknown")
            template_info["product_types"] = parsed_code.get("product_types", [])
            template_info["institutions"] = parsed_code.get("institutions", [])
            template_info["gs1_mode"] = parsed_code.get("gs1_mode", "none")
            template_info["statistics"] = parsed_code.get("statistics", {})
            
            # Cross-validatie indien beide beschikbaar
            if context_dict and preset_code:
                original_context = context_dict.get("context", {})
                is_valid, errors = TemplateCodeParser.validate_code_against_context(preset_code, original_context)
                template_info["is_valid"] = is_valid
                template_info["validation_errors"] = errors
            else:
                template_info["is_valid"] = True
        
        logging.info(f"Template Generator info geëxtraheerd: {preset_code}")
        return template_info
        
    except Exception as e:
        logging.error(f"Fout bij extracten Template Generator info: {e}")
        return {}

def is_new_template(df: pd.DataFrame) -> bool:
    """
    Bepaalt of een DataFrame een nieuwe GHX template structuur heeft.
    
    Criteria: Moet beide nieuwe template kolommen bevatten
    """
    new_template_columns = ["Is BestelbareEenheid", "Omschrijving Verpakkingseenheid"]
    return all(col in df.columns for col in new_template_columns)

def is_old_template(df: pd.DataFrame) -> bool:
    """
    Bepaalt of een DataFrame een oude template of supplier template is.
    
    Criteria: Mist kritieke nieuwe template kolommen
    """
    return not is_new_template(df)

def determine_template_type(df: pd.DataFrame, excel_path: str = None) -> Tuple[str, Dict[str, Any]]:
    """
    Bepaalt het template type op basis van DataFrame kolommen en extraheert metadata.
    
    Returns:
        Tuple van (template_type, template_info)
        template_type:
            'TG' - Template Generator gegenereerde template
            'DT' - Default Template (standaard GHX template)  
            'AT' - Alternatieve Template (oude of supplier template)
        template_info: Dictionary met template metadata
    """
    # Import de nieuwe template detectie functie uit price_tool
    try:
        from .price_tool import determine_template_type as new_determine_template_type
        from .price_tool import extract_template_generator_context
        
        if excel_path:
            # Gebruik de nieuwe implementatie uit price_tool.py
            template_type = new_determine_template_type(excel_path)
            
            if template_type == 'TG':
                # Gebruik nieuwe TG context extractie
                template_info = extract_template_generator_context(excel_path) or {}
                template_info['has_stamp'] = True
                
                # Log Template Generator info
                config = template_info.get('configuration', {})
                decisions = template_info.get('decisions', {})
                
                template_code = template_info.get('template_code', 'Unknown')
                product_types = config.get('product_types', [])
                institutions = config.get('institutions', [])
                
                logging.info(f"Template Generator gedetecteerd: {template_code}")
                if product_types:
                    logging.info(f"Product types: {', '.join(product_types)}")
                if institutions:
                    logging.info(f"Instellingen: {len(institutions)} instellingen")
                
                return template_type, template_info
            else:
                # DT of AT template
                template_info = {
                    "has_stamp": False,
                    "template_type": "default" if template_type == "DT" else "alternative"
                }
                return template_type, template_info
                
    except ImportError:
        logging.warning("Nieuwe template detectie niet beschikbaar, gebruik legacy detectie")
    
    # Legacy fallback detectie
    if has_template_generator_stamp(df, excel_path):
        template_info = extract_template_generator_info(excel_path) if excel_path else {}
        logging.info("Template Generator stamp gedetecteerd (legacy detectie)")
        return "TG", template_info
    
    # Legacy DT vs AT detectie
    template_info = {
        "has_stamp": False,
        "template_type": "default" if is_new_template(df) else "alternative"
    }
    
    if is_new_template(df):
        logging.info("Template type gedetecteerd: Default Template (DT)")
        return "DT", template_info
    else:
        logging.info("Template type gedetecteerd: Alternatieve Template (AT)")
        return "AT", template_info

def get_template_display_info(template_type: str, template_info: Dict[str, Any]) -> Dict[str, str]:
    """
    Genereert display informatie voor template in rapport.
    
    Args:
        template_type: Template type code ('TG', 'DT', 'AT')
        template_info: Template metadata dictionary
        
    Returns:
        Dictionary met display informatie voor rapport
    """
    display_info = {
        "type_description": "",
        "code_info": "",
        "context_info": "",
        "institution_info": "",
        "statistics_info": ""
    }
    
    try:
        if template_type == "TG":
            # Template Generator info
            template_code = template_info.get("template_code", "UNKNOWN")
            display_info["type_description"] = f"Template Generator Template ({template_code})"
            
            # Configuration info
            config = template_info.get("configuration", {})
            if config:
                template_choice = config.get("template_choice", "standard")
                gs1_mode = config.get("gs1_mode", "none")
                has_chemicals = config.get("has_chemicals", False)
                is_staffel = config.get("is_staffel_file", False)
                
                display_info["code_info"] = f"Type: {template_choice.capitalize()}, GS1: {gs1_mode}"
                
                if has_chemicals or is_staffel:
                    extra_info = []
                    if has_chemicals:
                        extra_info.append("Chemicals")
                    if is_staffel:
                        extra_info.append("Staffel")
                    display_info["code_info"] += f", Extra: {', '.join(extra_info)}"
                
                # Product types
                product_types = config.get("product_types", [])
                if product_types:
                    display_info["context_info"] = f"Product types: {', '.join(product_types).title()}"
                
                # Institutions
                institutions = config.get("institutions", [])
                if institutions:
                    display_info["institution_info"] = f"Instellingen: {len(institutions)} geselecteerd"
            
            # Decisions/Statistics info
            decisions = template_info.get("decisions", {})
            if decisions:
                visible = decisions.get("visible_fields", 0)
                mandatory = decisions.get("mandatory_fields", 0)
                hidden = decisions.get("hidden_fields", 0)
                display_info["statistics_info"] = f"Velden: {visible} zichtbaar, {mandatory} verplicht, {hidden} verborgen"
            
        elif template_type == "DT":
            display_info["type_description"] = "Default Template (Standaard GHX)"
            display_info["context_info"] = "17 verplichte velden, alle product types"
            display_info["statistics_info"] = "Alle kolommen zichtbaar"
            
        elif template_type == "AT":
            display_info["type_description"] = "Alternatieve Template (Supplier/Legacy)"
            display_info["context_info"] = "Aangepaste kolom structuur"
            display_info["statistics_info"] = "Beperkte validatie toegepast"
            
        elif template_type == "O":
            # Legacy support voor oude rapportage
            display_info["type_description"] = "Oude GHX Template / Supplier Template"
            display_info["context_info"] = "Backwards compatibility modus"
    
    except Exception as e:
        logging.error(f"Fout bij genereren template display info: {e}")
        display_info["type_description"] = f"Template Type {template_type}"
    
    return display_info

# --- Configuratie Constanten (Vervangen globale variabelen uit notebook) ---
# Deze kunnen later eventueel uit een centraal config bestand of env variabelen komen

# Configuratie voor validatie-overzichtsbestand (uit notebook Config cel)
ENABLE_VALIDATION_LOG = True  # True = logging aan, False = logging uit
# BELANGRIJK: Pas dit pad aan naar de *daadwerkelijke* locatie waar het logboek moet komen
# in de omgeving waar de code draait! Een hardcoded pad is meestal niet ideaal.
# Voor nu nemen we het pad uit je notebook over als voorbeeld.
VALIDATION_LOG_FILE = SERVER_PATHS.get("validation_log_file", "/tmp/validaties_overzicht.xlsx")

# Constanten voor rapportage limieten (uit notebook Code 5)
ERROR_LIMIT = 50000  # Maximaal aantal errors per sheet
ERROR_START = 0  # Begin vanaf deze rij (voor slicing bij limiet)
ERROR_END = ERROR_LIMIT  # Eindig bij deze rij (voor slicing bij limiet) # Aangepast voor duidelijkheid

# --- Hulpfuncties (Overgenomen uit Code 5) ---


def load_validation_config(json_path):
    """Laad validatieconfiguratie vanuit JSON-bestand."""
    try:
        with open(json_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error(f"Validatie configuratiebestand niet gevonden op {json_path}")
        # Je zou hier kunnen kiezen om een lege config terug te geven of de error te raisen
        # raise
        return (
            {}
        )  # Geeft lege dictionary terug om door te gaan, maar rapport kan incompleet zijn
    except json.JSONDecodeError:
        logging.error(f"Ongeldig JSON-formaat in {json_path}")
        # raise
        return {}


def update_validation_log(
    bestandsnaam,
    template_type,
    present_columns_count,
    percentage_correct,
    total_rows,
    total_cols,
    total_filled_in_present,
    total_errors_in_present,
    total_leeg,
    M_missing,
    ghx_mandatory_fields_list,  # Pass ghx_mandatory_fields list
    total_errors_non_mand=0,
    total_filled_non_mand=0,
    total_leeg_non_mand=0,
):
    """
    Houdt een overzicht bij van alle uitgevoerde validaties in een centraal Excel-bestand.
    Gebruikt nu globale constanten ENABLE_VALIDATION_LOG en VALIDATION_LOG_FILE.
    """
    if not ENABLE_VALIDATION_LOG:
        return

    # Bereken extra statistieken - Nieuwe intuïtieve score berekening
    # Score componenten:
    # 1. Volledigheid: Percentage van verplichte kolommen aanwezig (0-100)
    # 2. Kwaliteit: Percentage van data correct ingevuld zonder rejection errors (0-100)  
    # 3. Template bonus: +5 punten voor nieuwste template
    
    # Volledigheid score (0-40 punten)
    completeness_score = (present_columns_count / len(ghx_mandatory_fields_list)) * 40 if len(ghx_mandatory_fields_list) > 0 else 0
    
    # Kwaliteit score (0-50 punten) - gebaseerd op percentage correct 
    quality_score = (percentage_correct / 100) * 50 if percentage_correct > 0 else 0
    
    # Template bonus (0-15 punten) - Enhanced voor Template Generator
    if template_type == "TG":
        template_bonus = 15  # Template Generator krijgt hoogste bonus
    elif template_type == "N":
        template_bonus = 10  # Nieuwe template krijgt goede bonus
    else:
        template_bonus = 5   # Oude template krijgt basis bonus
    
    # Totaal score (0-100)
    total_score = min(100, completeness_score + quality_score + template_bonus)
    
    # Formateer score als hele getal met beschrijving
    score_int = round(total_score)
    score_grade = "A+" if score_int >= 90 else "A" if score_int >= 80 else "B" if score_int >= 70 else "C" if score_int >= 60 else "D"
    score = f"{score_int}/100 ({score_grade})"
    validation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Bereken percentages
    # We gebruiken len(ghx_mandatory_fields_list) die nu wordt doorgegeven
    total_mandatory_potential_fields = len(ghx_mandatory_fields_list) * total_rows
    perc_filled_mandatory = (
        (total_filled_in_present / total_mandatory_potential_fields * 100)
        if total_mandatory_potential_fields > 0
        else 0
    )
    # % Correct t.o.v. gevulde velden
    perc_errors_of_filled_mandatory = (
        (total_errors_in_present / total_filled_in_present * 100)
        if total_filled_in_present > 0
        else 0
    )
    perc_correct_of_filled_mandatory = 100 - perc_errors_of_filled_mandatory

    # Bereken combinatie data voor niet-verplichte velden
    correct_filled_mandatory = total_filled_in_present - total_errors_in_present
    correct_filled_non_mandatory = total_filled_non_mand - total_errors_non_mand

    # Voorbereid data voor de nieuwe regel
    new_row_data = {
        "Datum": validation_date,
        "Bestandsnaam": bestandsnaam,
        "Score": score,
        "Rijen": total_rows,
        "Kolommen": total_cols,
        "Template Type": "Template Generator" if template_type == "TG" else "Nieuw" if template_type == "N" else "Oud",
        "Verplichte kolommen Aanwezig": present_columns_count,  # Hernoemd voor duidelijkheid
        "Verplichte kolommen Ontbrekend": M_missing,  # Hernoemd voor duidelijkheid
        # Verplichte velden statistieken
        "Verplicht - Gevuld": total_filled_in_present,
        "Verplicht - Correct Gevuld": correct_filled_mandatory,  # Hernoemd
        "Verplicht - Foutief Gevuld": total_errors_in_present,  # Hernoemd
        "Verplicht - Leeg (waar kolom aanwezig)": total_leeg,  # Hernoemd
        "Verplicht - % Gevuld (van totaal mogelijk)": f"{perc_filled_mandatory:.1f}%",  # Hernoemd
        "Verplicht - % Correct (van gevuld)": f"{perc_correct_of_filled_mandatory:.1f}%",  # Hernoemd
        # Niet-verplichte velden statistieken
        "Optioneel - Gevuld": total_filled_non_mand,
        "Optioneel - Correct Gevuld": correct_filled_non_mandatory,  # Hernoemd
        "Optioneel - Foutief Gevuld": total_errors_non_mand,  # Hernoemd
        "Optioneel - Leeg": total_leeg_non_mand,
        # Totalen
        "Totaal velden": total_rows * total_cols,
        "Totaal gevuld": total_filled_in_present + total_filled_non_mand,
        "Totaal correct gevuld": correct_filled_mandatory
        + correct_filled_non_mandatory,  # Hernoemd
        "Totaal foutief gevuld": total_errors_in_present
        + total_errors_non_mand,  # Hernoemd
        "Totaal leeg": total_leeg + total_leeg_non_mand,
        # Oorspronkelijke score (als referentie?)
        "Kwaliteitsscore": f"{percentage_correct}%",  # Hernoemd
    }

    try:
        if os.path.exists(VALIDATION_LOG_FILE):
            try:
                existing_df = pd.read_excel(VALIDATION_LOG_FILE)
                # Zorg dat alle kolommen bestaan, voeg toe indien nodig
                for col in new_row_data.keys():
                    if col not in existing_df.columns:
                        existing_df[col] = pd.NA  # Gebruik NA voor missende waarden
            except Exception as e:
                logging.warning(
                    f"Kon bestaand validatielogboek niet lezen ({VALIDATION_LOG_FILE}): {e}"
                )
                existing_df = pd.DataFrame(columns=list(new_row_data.keys()))
        else:
            existing_df = pd.DataFrame(columns=list(new_row_data.keys()))

        # Voeg de nieuwe regel toe
        new_row_df = pd.DataFrame([new_row_data])

        # Zorg dat kolomvolgorde consistent is
        combined_df = pd.concat([existing_df, new_row_df], ignore_index=True)[
            list(new_row_data.keys())
        ]

        # Sorteer op datum (nieuwste eerst)
        if "Datum" in combined_df.columns:
            combined_df["Datum"] = pd.to_datetime(
                combined_df["Datum"]
            )  # Zorg voor datetime object
            combined_df = combined_df.sort_values(
                by="Datum", ascending=False
            ).reset_index(drop=True)
            # Converteer datum terug naar string voor Excel weergave indien gewenst
            combined_df["Datum"] = combined_df["Datum"].dt.strftime("%Y-%m-%d %H:%M:%S")

        # Schrijf naar Excel met opmaak
        with pd.ExcelWriter(VALIDATION_LOG_FILE, engine="xlsxwriter") as writer:
            combined_df.to_excel(writer, index=False, sheet_name="Validatie Overzicht")

            # Pas kolombreedtes aan (voorbeeld)
            worksheet = writer.sheets["Validatie Overzicht"]
            # Zet breedtes zoals in je notebook of pas aan naar behoefte
            worksheet.set_column("A:A", 20)  # Datum
            worksheet.set_column("B:B", 40)  # Bestandsnaam
            worksheet.set_column("C:C", 12)  # Score
            # ... voeg hier de rest van je kolombreedte instellingen toe ...
            worksheet.set_column("D:W", 18)  # Generieke breedte voor de rest

            # Header opmaak (GHX oranje)
            header_format = writer.book.add_format(
                {
                    "bold": True,
                    "bg_color": "#f79645",
                    "font_color": "white",
                    "border": 1,
                }
            )
            for col_num, value in enumerate(combined_df.columns.values):
                worksheet.write(0, col_num, value, header_format)

            # Voeg tabel stijl toe
            (max_row, max_col) = combined_df.shape
            worksheet.add_table(
                0,
                0,
                max_row,
                max_col - 1,
                {
                    "columns": [{"header": col} for col in combined_df.columns],
                    "style": "Table Style Medium 2",  # Stijl kan aangepast
                    "first_column": True,  # Benadruk eerste kolom
                },
            )

        logging.info(f"Validatie toegevoegd aan logboek: {VALIDATION_LOG_FILE}")

    except Exception as e:
        logging.error(f"Fout bij het bijwerken van het validatielogboek: {e}")


def add_colored_dataset_sheet(
    workbook,
    df,
    validation_results,
    ghx_mandatory_fields,
    original_column_mapping,
    JSON_CONFIG_PATH,
    validation_config=None,
    template_context=None,
    excel_path=None,
):
    """Voeg een sheet toe met de volledige dataset in kleurcodering."""
    # Gebruik de doorgegeven validation_config of val terug op laden van bestand
    if validation_config:
        config = validation_config
    else:
        # Fallback: laad van bestand (backwards compatibility)
        config = load_validation_config(JSON_CONFIG_PATH)
        if not config:  # Als config laden mislukt is
            logging.warning(
                "Kan gekleurde dataset sheet niet toevoegen omdat validatie config mist."
            )
            return

    # Check of het een (vermoedelijk) nieuwe template is door te kijken naar specifieke kolommen
    # Dit is een benadering; een expliciete check is beter indien mogelijk
    is_new_template = all(
        field in df.columns
        for field in [
            "Is BestelbareEenheid",
            "Omschrijving Verpakkingseenheid",
            "Is BasisEenheid",
        ]
    )

    # Dataset Validatie sheet is nu beschikbaar voor ALLE template types
    # Geen beperking meer op basis van is_new_template
    logging.info("Genereren Dataset Validatie sheet voor alle template types.")

    try:
        worksheet = workbook.add_worksheet("7. Dataset Validatie")
        
        # Onderdruk Excel groene driehoekjes
        suppress_excel_errors(worksheet, max_row=len(df)+10, max_col=len(df.columns)+5)

        # Formaten
        correct_format = workbook.add_format(
            {"bg_color": "#FFFFFF", "border": 1, "border_color": "#D3D3D3"}
        )
        error_format = workbook.add_format(
            {"bg_color": "#FF4500", "border": 1, "border_color": "#B22222"}
        )  # Rood voor verplichte fouten
        error_optional_format = workbook.add_format(
            {"bg_color": "#FFE6E6", "border": 1, "border_color": "#FFCCCC"}
        )  # Zachter roze voor niet-verplichte fouten
        empty_mandatory_format = workbook.add_format(
            {"bg_color": "#FFD700", "border": 1, "border_color": "#A9A9A9"}
        )  # Goud/Geel
        header_format = workbook.add_format(
            {
                "bold": True,
                "bg_color": "#f79645",
                "font_color": "white",
                "border": 1,
                "border_color": "#e67e22",
                "font_size": 12,
            }
        )
        uom_relation_error_format = workbook.add_format(
            {"bg_color": "#ADD8E6", "border": 1, "border_color": "#4682B4"}
        )  # Lichtblauw

        # Verbeterde legenda opmaak
        legenda_title_format = workbook.add_format({
            "bold": True,
            "font_size": 12,
            "valign": "vcenter",
            "indent": 1
        })
        
        # Verbeterde legenda item formats - met zwarte randen
        correct_format_legend = workbook.add_format({
            "bg_color": "#FFFFFF", 
            "border": 2, 
            "border_color": "#000000",
            "bold": True,
            "valign": "vcenter",
            "indent": 1
        })
        error_format_legend = workbook.add_format({
            "bg_color": "#FF4500", 
            "border": 2, 
            "border_color": "#000000",
            "bold": True,
            "valign": "vcenter",
            "indent": 1
        })
        error_optional_format_legend = workbook.add_format({
            "bg_color": "#FFE6E6", 
            "border": 2, 
            "border_color": "#000000",
            "bold": True,
            "valign": "vcenter",
            "indent": 1
        })
        empty_mandatory_format_legend = workbook.add_format({
            "bg_color": "#FFD700", 
            "border": 2, 
            "border_color": "#000000",
            "bold": True,
            "valign": "vcenter",
            "indent": 1
        })
        uom_relation_error_format_legend = workbook.add_format({
            "bg_color": "#ADD8E6", 
            "border": 2, 
            "border_color": "#000000",
            "bold": True,
            "valign": "vcenter",
            "indent": 1
        })
        
        # Stel rij hoogtes in (rijen 1-7 = 20)
        for row in range(7):
            worksheet.set_row(row, 20)
            
        # Stel kolom A breedte in (25)
        worksheet.set_column(0, 0, 25)
        
        # Legenda
        worksheet.write("A1", "Legenda:", legenda_title_format)
        worksheet.write("A2", "Correct/Optioneel leeg", correct_format_legend)
        worksheet.write("A3", "Foutief ingevuld (verplicht)", error_format_legend)
        worksheet.write("A4", "Foutief ingevuld/Flags", error_optional_format_legend)
        worksheet.write("A5", "Verplicht veld leeg", empty_mandatory_format_legend)
        worksheet.write("A6", "UOM-relatie conflict", uom_relation_error_format_legend)
        start_row = 7

        # Maak error lookups
        error_lookup = {}  # Voor normale fouten
        flag_lookup = {}  # Voor flags (speciale roze kleur)
        uom_relation_error_lookup = {}  # Voor code 724, 801, 805 fouten (UOM relatie conflicten)

        for error in validation_results:
            if error["GHX Kolom"] == "RED FLAG":
                continue
            # Gebruik dezelfde rij index logica als in validate_dataframe
            row_idx = error["Rij"] - 3
            col_name = error["GHX Kolom"]
            error_code = error.get("code", "")

            if col_name in df.columns:
                col_idx = df.columns.get_loc(col_name)
                if 0 <= row_idx < len(df):
                    # UOM relatie fouten (724, 801, 805) krijgen speciale behandeling
                    # Voor codes 801 en 805 moeten we beide gerelateerde velden kleuren
                    if error_code in ["724", "801", "805"]:
                        if row_idx not in uom_relation_error_lookup:
                            uom_relation_error_lookup[row_idx] = set()
                        uom_relation_error_lookup[row_idx].add(col_idx)
                        
                        # Voor code 801 (UOM match): kleur ook het gerelateerde UOM veld
                        if error_code == "801":
                            if col_name == "UOM Code Verpakkingseenheid" and "UOM Code Basiseenheid" in df.columns:
                                related_col_idx = df.columns.get_loc("UOM Code Basiseenheid")
                                uom_relation_error_lookup[row_idx].add(related_col_idx)
                            elif col_name == "UOM Code Basiseenheid" and "UOM Code Verpakkingseenheid" in df.columns:
                                related_col_idx = df.columns.get_loc("UOM Code Verpakkingseenheid")
                                uom_relation_error_lookup[row_idx].add(related_col_idx)
                        
                        # Voor code 805 (Content match): kleur ook het gerelateerde Inhoud veld
                        elif error_code == "805":
                            if col_name == "Inhoud Verpakkingseenheid" and "Inhoud Basiseenheid" in df.columns:
                                related_col_idx = df.columns.get_loc("Inhoud Basiseenheid")
                                uom_relation_error_lookup[row_idx].add(related_col_idx)
                            elif col_name == "Inhoud Basiseenheid" and "Inhoud Verpakkingseenheid" in df.columns:
                                related_col_idx = df.columns.get_loc("Inhoud Verpakkingseenheid")
                                uom_relation_error_lookup[row_idx].add(related_col_idx)
                    else:
                        # Check of dit een flag is
                        error_type = error.get("type", "")
                        if error_type == "flag":
                            # Flags krijgen speciale behandeling
                            if row_idx not in flag_lookup:
                                flag_lookup[row_idx] = set()
                            flag_lookup[row_idx].add(col_idx)
                        else:
                            # Normale fouten (rejection/correction)
                            if row_idx not in error_lookup:
                                error_lookup[row_idx] = set()
                            error_lookup[row_idx].add(col_idx)

        # Bepaal welke kolommen zichtbaar zijn (Template Generator filtering)
        visible_columns = list(df.columns)
        if template_context and template_context.get("decisions"):
            decisions = template_context.get("decisions", {})
            visible_list = decisions.get("visible_list", [])
            # Filter kolommen gebaseerd op visible_list uit Template Generator  
            visible_columns = [col for col in df.columns if col in visible_list or col == "Legenda:"]
            # Template Generator kolom filtering toegepast
        else:
            # Template Generator filtering overgeslagen
            visible_columns = df.columns
        
        # Filter uit instructie/algemene tekst kolommen die niet in dataset horen
        visible_columns = [col for col in visible_columns if not col.startswith("ALGEMEEN")]
        
        # Schrijf alleen zichtbare headers
        # Voeg eerst de rijnummer kolom toe
        worksheet.write(start_row, 0, "Regelnummer template", header_format)
        
        # Schrijf de rest van de headers vanaf kolom 1
        for col, header in enumerate(visible_columns):
            worksheet.write(start_row, col + 1, str(header), header_format)

        # Schrijf data met kleuren (limiteer rijen)
        max_rows_sheet = min(len(df), ERROR_LIMIT)  # Gebruik limiet
        if len(df) > max_rows_sheet:
            # Plaats mooie waarschuwing in C5:E6 met kleur en rand
            warning_format = workbook.add_format({
                "bold": True, 
                "color": "red", 
                "font_size": 12,
                "valign": "vcenter",
                "align": "center",
                "text_wrap": True,
                "bg_color": "#FFF2CC",  # Lichtgele achtergrond
                "border": 2,
                "border_color": "#E07A00"  # Oranje rand
            })
            worksheet.merge_range(
                "C5:E6",  # C5 tot E6 voor mooie positionering
                f"LET OP: Weergave beperkt tot de eerste {max_rows_sheet} rijen.",
                warning_format
            )

        # SIMPEL: Check hoeveel rijen zijn verwijderd uit originele Excel file
        # Default: data begint op rij 2 (na headers), +1 voor elke verwijderde rij
        data_start_row = 2
        
        # Check template context voor informatue over verwijderde regels
        removed_rows = 0
        if template_context and 'removed_rows_count' in template_context:
            removed_rows = template_context['removed_rows_count']
        
        data_start_row = 2 + removed_rows  # Headers op rij 1, dan +removed rows
        logging.info(f"Sheet 7: Data start berekening = rij 2 (base) + {removed_rows} (verwijderd) = rij {data_start_row}")
        
        for row_idx in range(max_rows_sheet):
            # Schrijf eerst het template rijnummer in kolom A (0) - nu dynamisch
            template_row_number = row_idx + data_start_row
            worksheet.write(start_row + 1 + row_idx, 0, template_row_number, correct_format)
            
            for col_idx, field_name in enumerate(visible_columns):
                # Get original column index for df.iloc
                orig_col_idx = df.columns.get_loc(field_name)
                value = df.iloc[row_idx, orig_col_idx]
                value_str = "" if pd.isna(value) else str(value).strip()
                is_empty = value_str == ""

                is_mandatory = field_name in ghx_mandatory_fields

                # Dependency check (vereenvoudigd uit Code 5)
                has_dependency = False
                # Gebruik validation_config als beschikbaar, anders config
                active_config = validation_config if validation_config else config
                if is_empty and active_config and "fields" in active_config and field_name in active_config["fields"]:
                    field_config = active_config["fields"][field_name]
                    if "depends_on" in field_config:
                        cond = field_config["depends_on"].get("condition")
                        related_fields = field_config["depends_on"].get("fields", [])
                        if cond == "1" and len(related_fields) > 0:
                            related_field_name = related_fields[0]
                            if related_field_name in df.columns:
                                related_value = str(
                                    df.iloc[
                                        row_idx, df.columns.get_loc(related_field_name)
                                    ]
                                ).strip()
                                has_dependency = related_value == "1"

                # Kleur bepalen
                cell_format = correct_format  # Default
                if (
                    row_idx in uom_relation_error_lookup
                    and orig_col_idx in uom_relation_error_lookup[row_idx]
                ):
                    cell_format = uom_relation_error_format
                elif is_empty and (is_mandatory or has_dependency):
                    # PRIORITEIT: Verplichte velden die leeg zijn zijn ALTIJD geel
                    cell_format = empty_mandatory_format
                elif row_idx in flag_lookup and orig_col_idx in flag_lookup[row_idx]:
                    # Flags krijgen altijd roze kleur (error_optional_format)
                    cell_format = error_optional_format  # Roze voor flags
                elif row_idx in error_lookup and orig_col_idx in error_lookup[row_idx]:
                    # Lege optionele velden NOOIT kleuren, ook niet bij fouten
                    if is_empty and not is_mandatory and not has_dependency:
                        cell_format = correct_format  # Wit voor lege optionele velden
                    # Onderscheid maken tussen verplichte en niet-verplichte fouten
                    elif is_mandatory:
                        cell_format = error_format  # Rood voor verplichte fouten
                    else:
                        cell_format = error_optional_format  # Roze voor niet-verplichte fouten

                # Schrijf waarde met bepaalde opmaak (shift 1 kolom naar rechts voor rijnummer kolom)
                worksheet.write(
                    start_row + row_idx + 1, col_idx + 1, value_str, cell_format
                )
            
            # Stel rijhoogte in op 15 voor elke data rij (geen terugloop)
            worksheet.set_row(start_row + row_idx + 1, 15)

        # Stel kolombreedte in - alle kolommen op 30 (zoals template)
        worksheet.set_column(0, 0, 30)  # Rijnummer kolom ook 30
        if len(visible_columns) > 0:
            worksheet.set_column(1, len(visible_columns), 30)  # Data kolommen

        # Voeg Excel AutoFilter toe voor betere filtering mogelijkheden
        # AutoFilter bereik: van header rij tot laatste data rij (inclusief extra rijnummer kolom)
        last_col = len(visible_columns)  # +1 voor rijnummer kolom
        last_row = start_row + max_rows_sheet  # start_row + aantal data rijen
        worksheet.autofilter(start_row, 0, last_row, last_col)

        worksheet.write(
            start_row - 1,
            0,
            "Dataset Validatie:",
            workbook.add_format({"bold": True, "font_size": 12}),
        )

    except Exception as e:
        logging.error(f"Fout tijdens genereren gekleurde dataset sheet: {e}")
        # Optioneel: voeg een sheet toe met de foutmelding
        try:
            error_sheet = workbook.add_worksheet("8. Dataset Fout")
            suppress_excel_errors(error_sheet)
            error_sheet.write(0, 0, f"Kon '7. Dataset Validatie' sheet niet genereren.")
            error_sheet.write(1, 0, f"Foutmelding: {e}")
        except:
            pass  # Voorkom errors in de error handling


# --- Hoofdfunctie voor Rapport Generatie (VOLLEDIGE EN AANGEPASTE VERSIE) ---


def genereer_rapport(
    validation_results: list,
    output_dir: str,
    bestandsnaam: str,
    ghx_mandatory_fields: list,
    original_column_mapping: dict,
    df: pd.DataFrame,
    header_mapping: dict,
    df_original: pd.DataFrame,
    red_flag_messages: list,
    JSON_CONFIG_PATH: str,  # Pad nodig om config te laden
    summary_data: dict,  # VERWIJDERDE PARAMETER TERUGGEZET
    errors_per_field: dict = None,
    validation_config: dict = None,  # Geconverteerde config voor Sheet 9
    template_context: dict = None,  # Template Generator context
    excel_path: str = None,  # Pad naar origineel Excel bestand voor template detectie
    max_rows: int = None,
    total_rows: int = None,
):
    """
    Genereert het volledige Excel validatierapport, inclusief alle sheets,
    gebaseerd op notebook Code 5 en aangepast dashboard layout.
    """
    if errors_per_field is None:
        errors_per_field = {}  # Voorkom None errors

    # Early Template Type Detectie (voorkom UnboundLocalError)
    template_type, template_info = determine_template_type(df, excel_path)
    
    # Quick Mode detectie (voorkom UnboundLocalError)
    quick_mode = (max_rows is not None and max_rows == 5000)

    # Constanten voor rapportage limieten (uit notebook Code 5)
    ERROR_LIMIT = 50000  # Maximaal aantal errors per sheet
    ERROR_START = 0  # Begin vanaf deze rij (voor slicing bij limiet)
    ERROR_END = ERROR_LIMIT  # Eindig bij deze rij (voor slicing bij limiet)

    try:
        # Helper functie voor schone headers - gebruik dezelfde logica als price_tool.py
        def clean_header(header):
            from .price_tool import clean_column_name
            # Verwijder newlines en splits op dash om Nederlandse naam vóór de dash te behouden
            clean = str(header).split("\n")[0].strip()
            # Split op " - " en neem het Nederlandse deel (vóór de dash)
            if " - " in clean:
                clean = clean.split(" - ")[0].strip()
            # Nu pas clean_column_name toe voor consistente normalisatie
            return clean_column_name(clean)
        
        # Helper functie voor kolomkoppen in rapporten (behoudt Nederlandse naam zonder normalisatie)
        def clean_header_for_display(header):
            if pd.isna(header) or not str(header).strip():
                return header
            # Verwijder newlines en neem eerste regel
            clean = str(header).split("\n")[0].strip()
            # Split op " - " en neem het Nederlandse deel (vóór de dash)
            if " - " in clean:
                clean = clean.split(" - ")[0].strip()
            return clean
        
        # Helper functie om error codes naar categorieën te mappen
        def get_error_category(error_code):
            if pd.isna(error_code) or str(error_code).strip() == "":
                return "Onbekend"
            
            code_str = str(error_code).strip()
            try:
                code_int = int(float(code_str))  # Handle both int and float strings
                
                # Specifieke flag codes die verkeerd zouden worden geclassificeerd
                flag_codes = {703, 720, 751, 752, 753, 756, 758, 759, 760, 761, 762, 763, 764, 765, 766, 769, 770, 771, 773, 774, 775}
                
                # Categorisering op basis van code ranges
                if code_int in flag_codes:
                    return "Vlag"
                elif 700 <= code_int <= 749:
                    if code_int == 724:  # Speciale uitzondering voor conflict
                        return "Conflict"
                    return "Afkeuring"
                elif code_int == 772:  # Speciale uitzondering voor correction
                    return "Aanpassing"
                elif 750 <= code_int <= 799:
                    return "Vlag"
                elif 800 <= code_int <= 899:
                    return "Vlag"  # Global flags zijn ook vlaggen
                else:
                    return "Onbekend"
            except (ValueError, TypeError):
                return "Onbekend"
        
        def get_error_category_with_type(row):
            """Bepaal error category op basis van type field (indien beschikbaar) of code."""
            # Probeer eerst het type field te gebruiken (nieuw systeem)
            if 'type' in row and pd.notna(row['type']) and str(row['type']).strip():
                error_type = str(row['type']).strip().lower()
                if error_type == 'flag':
                    return "Vlag"
                elif error_type == 'correction':
                    return "Aanpassing"
                elif error_type == 'rejection':
                    return "Afkeuring"
            
            # Fallback naar oude code-based logica
            return get_error_category(row.get('Foutcode', row.get('code', '')))
        
        def get_error_category_optional(row):
            """Speciale versie voor optionele fouten - gebruikt 'Incorrect' in plaats van 'Afkeuring'."""
            # Probeer eerst het type field te gebruiken (nieuw systeem)
            if 'type' in row and pd.notna(row['type']) and str(row['type']).strip():
                error_type = str(row['type']).strip().lower()
                if error_type == 'flag':
                    return "Vlag"
                elif error_type == 'correction':
                    return "Aanpassing"
                elif error_type == 'rejection':
                    return "Incorrect"  # Voor optionele fouten: "Incorrect" i.p.v. "Afkeuring"
            
            # Fallback naar code-based logica maar met aangepaste terminologie
            error_code = row.get('Foutcode', row.get('code', ''))
            if pd.isna(error_code) or str(error_code).strip() == "":
                return "Onbekend"
            
            code_str = str(error_code).strip()
            try:
                code_int = int(float(code_str))
                
                # Specifieke flag codes
                flag_codes = {703, 720, 751, 752, 753, 756, 758, 759, 760, 761, 762, 763, 764, 765, 766, 769, 770, 771, 773, 774, 775}
                
                if code_int in flag_codes:
                    return "Vlag"
                elif 700 <= code_int <= 749:
                    if code_int == 724:
                        return "Conflict"
                    return "Incorrect"  # Voor optionele fouten
                elif code_int == 772:
                    return "Aanpassing"
                elif 750 <= code_int <= 799:
                    return "Vlag"
                elif 800 <= code_int <= 899:
                    return "Vlag"
                else:
                    return "Onbekend"
            except (ValueError, TypeError):
                return "Onbekend"

        # Bestandsnaam zonder extensie voor output naamgeving
        bestandsnaam_zonder_extensie = os.path.splitext(bestandsnaam)[0]

        # --- Data Voorbereiding & Berekeningen (Begin) ---
        # Voor Quick Mode: gebruik originele total_rows parameter, anders processed data lengte
        if total_rows is None:
            total_rows = len(df)  # Normale modus: gebruik processed data lengte
        # Anders: behoud originele total_rows parameter (Quick Mode)
        
        processed_rows = len(df)  # Aantal verwerkte rijen (voor berekeningen)
        total_cols = len(df.columns)  # Kolommen in verwerkte df
        total_original_cols = len(df_original.columns)  # Kolommen in origineel bestand

        # DEBUG: Log template context
        if template_context:
            logging.info(f"DEBUG Sheet 1: Template context aanwezig, type: {template_context.get('type', 'Unknown')}")
            if template_context.get('type') == 'TG':
                logging.info(f"DEBUG Sheet 1: TG Template gedetecteerd met {template_context.get('visible_fields', '?')} zichtbare velden")
        else:
            logging.info("DEBUG Sheet 1: Geen template context (waarschijnlijk DT/AT template)")
        
        # Gebruik de doorgegeven validation_config of val terug op laden van bestand
        if validation_config:
            config = validation_config
            logging.info(f"DEBUG Sheet 1: validation_config gebruikt (niet van file)")
        else:
            config = load_validation_config(JSON_CONFIG_PATH)
            logging.info(f"DEBUG Sheet 1: config geladen van file: {JSON_CONFIG_PATH}")
            if not config:
                logging.error("Kan rapport niet genereren zonder validatie configuratie.")
                return None

        # Check voor v20 vs v18 structuur voor non_mandatory_fields
        if "field_validations" in config:
            # v20 structuur
            all_fields = list(config.get("field_validations", {}).keys())
        else:
            # v18 structuur (fallback)
            all_fields = list(config.get("fields", {}).keys())
            
        non_mandatory_fields = [
            f for f in all_fields if f not in ghx_mandatory_fields
        ]
        # Voor TG templates: gebruik template_context mandatory_list
        # Voor ALT/DT templates: gebruik ghx_mandatory_fields
        if template_type == "TG" and template_context and "decisions" in template_context:
            template_mandatory_fields = template_context["decisions"]["mandatory_list"]
            present_mandatory_columns = [f for f in template_mandatory_fields if f in df.columns]
            missing_mandatory_columns = [
                f for f in template_mandatory_fields if f not in df.columns
            ]
        else:
            # ALT/DT templates: gebruik ghx_mandatory_fields
            present_mandatory_columns = [f for f in ghx_mandatory_fields if f in df.columns]
            missing_mandatory_columns = [
                f for f in ghx_mandatory_fields if f not in df.columns
            ]
        
        M_found = len(present_mandatory_columns)
        M_missing = len(missing_mandatory_columns)

        # Herbereken filled_counts en empty/errors voor consistentie hier
        filled_counts = {}
        invalid_values_config = config.get("invalid_values", [])
        invalid_values = [str(val).lower() for val in invalid_values_config]
        for f in present_mandatory_columns:
            filled_counts[f] = (
                df[f].notna()
                & (
                    ~df[f]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    .isin(["nan", ""] + invalid_values)
                )
            ).sum()

        total_filled_in_present = sum(
            filled_counts.get(f, 0) for f in present_mandatory_columns
        )
        # Bij Quick Mode: gebruik processed_rows, anders total_rows
        rows_for_calculation = processed_rows if max_rows is not None else total_rows
        empty_in_present = (M_found * rows_for_calculation) - total_filled_in_present

        corrected_errors = {}
        for f in present_mandatory_columns:
            field_filled = filled_counts.get(f, 0)
            field_errors = errors_per_field.get(f, 0)  # Gebruik doorgegeven errors
            corrected_errors[f] = min(field_errors, field_filled)
        total_errors_in_present = sum(corrected_errors.values())
        totaal_juist = total_filled_in_present - total_errors_in_present

        # Bereken percentage fouten van ingevulde verplichte velden
        percentage_incorrect_of_filled_present = (
            (total_errors_in_present / total_filled_in_present * 100)
            if total_filled_in_present > 0
            else 0
        )

        # Statistieken voor Blok 2 ("Actiepunten" uit origineel)
        aantal_leeg_incl_missing = empty_in_present + (M_missing * total_rows)
        
        # Voor TG templates: gebruik template_mandatory_fields count
        # Voor ALT/DT templates: gebruik ghx_mandatory_fields count
        # BELANGRIJK: Gebruik len(df) voor processed data, niet total_rows!
        processed_rows = len(df)
        if template_type == "TG" and template_context and "decisions" in template_context:
            total_possible_mandatory_fields = len(template_context["decisions"]["mandatory_list"]) * processed_rows
        else:
            total_possible_mandatory_fields = len(ghx_mandatory_fields) * processed_rows
        percentage_ingevuld_incl_missing = (
            (total_filled_in_present / total_possible_mandatory_fields * 100)
            if total_possible_mandatory_fields > 0
            else 0
        )

        # Fouten per veld non-mandatory (voor info in Aandachtspunten/Acties blok van 'new')
        present_non_mandatory_columns = [
            f for f in non_mandatory_fields if f in df.columns
        ]
        filled_counts_non_mand = {}
        for f in present_non_mandatory_columns:
            filled_counts_non_mand[f] = (
                df[f].notna()
                & (
                    ~df[f]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    .isin(["nan", ""] + invalid_values)
                )
            ).sum()
        total_filled_non_mand = sum(filled_counts_non_mand.values())

        errors_per_field_non_mand = {}
        df_errors_all = pd.DataFrame(validation_results)
        df_errors = (
            df_errors_all[df_errors_all["GHX Kolom"] != "RED FLAG"].copy()
            if not df_errors_all.empty
            else pd.DataFrame()
        )
        df_errors_mand = pd.DataFrame()  # Initialize as empty
        df_errors_non_mand = pd.DataFrame()  # Initialize as empty

        if not df_errors.empty:
            # Check if 'GHX Kolom' exists before filtering
            if "GHX Kolom" in df_errors.columns:
                # Define mandatory errors dataframe
                df_errors_mand = df_errors[
                    df_errors["GHX Kolom"].isin(ghx_mandatory_fields)
                ].copy()

                # Define non-mandatory errors dataframe
                df_errors_non_mand = df_errors[
                    df_errors["GHX Kolom"].isin(non_mandatory_fields)
                ].copy()

                # Recalculate errors_per_field_non_mand using df_errors_non_mand
                errors_per_field_non_mand = {}  # Reset
                if "Rij" in df_errors_non_mand.columns:
                    for field in present_non_mandatory_columns:
                        errors_for_this_field = df_errors_non_mand[
                            df_errors_non_mand["GHX Kolom"] == field
                        ]
                        unique_rows = errors_for_this_field["Rij"].nunique()
                        errors_per_field_non_mand[field] = min(
                            unique_rows, filled_counts_non_mand.get(field, 0)
                        )
                else:  # Handle case where 'Rij' column is missing
                    logging.warning(
                        "'Rij' kolom niet gevonden in gefilterde non-mandatory errors."
                    )
                    for field in present_non_mandatory_columns:
                        errors_per_field_non_mand[field] = (
                            0  # Or some other default handling
                        )
            else:  # Handle case where 'GHX Kolom' is missing
                logging.warning("'GHX Kolom' niet gevonden in df_errors.")
                for field in present_non_mandatory_columns:
                    errors_per_field_non_mand[field] = 0  # Default if column missing

        total_errors_non_mand = sum(errors_per_field_non_mand.values())

        # BEREKEN HIER DE MISSENDE VARIABELE (Percentage gevuld van AANWEZIGE verplichte velden):
        perc_verpl_gevuld = (
            (total_filled_in_present / (M_found * total_rows) * 100)
            if (M_found * total_rows) > 0
            else 0
        )

        # Score berekening - Enhanced Template Type Detectie (al gedaan aan begin functie)
        template_display_info = get_template_display_info(template_type, template_info)

        # Voor Template Generator: gebruik gefilterde kolom count
        if template_context and template_context.get("decisions"):
            visible_fields_count = template_context["decisions"].get("visible_fields", len(df.columns))
            total_original_cols = visible_fields_count  # Use filtered count for TG templates
        else:
            total_original_cols = len(df.columns)  # Use actual columns for other templates

        percentage_correct = 0
        volledigheids_percentage = 0
        juistheid_percentage = 0
        if total_filled_in_present > 0:
            volledigheids_percentage = (
                (total_filled_in_present / total_possible_mandatory_fields) * 100
                if total_possible_mandatory_fields > 0
                else 0
            )
            juistheid_percentage = (totaal_juist / total_filled_in_present) * 100
            percentage_correct = round(
                (volledigheids_percentage * juistheid_percentage) / 100
            )
        elif M_found > 0 and total_possible_mandatory_fields > 0:
            percentage_correct = 0
        else:
            percentage_correct = 0
        # === NIEUWE INTUÏTIEVE SCORE BEREKENING ===
        # Bereken aantal verwerkte rijen voor penalty berekening
        processed_rows_for_calc = len(df) if len(df) > 0 else 1
        
        # Gebruik nieuwe score functie met voorberekende percentages
        score_result = calculate_new_intuitive_score(
            M_found=M_found,
            total_mandatory=len(ghx_mandatory_fields),
            df_errors_mand=df_errors_mand,
            df_errors_non_mand=df_errors_non_mand,
            total_rows=processed_rows_for_calc,  # Gebruik verwerkte rijen voor score berekening
            template_type=template_type,
            volledigheids_percentage=volledigheids_percentage,
            juistheid_percentage=juistheid_percentage
        )
        
        # Extract values voor filename en display
        M_percentage = score_result['M_percentage']
        J_percentage = score_result['J_percentage']
        score_int_file = score_result['final_score']
        score_grade_file = score_result['grade']
        
        # Nieuwe filename format: TG_M86_J75_65(C) (J% terug zoals gevraagd)
        score_suffix = f"_{template_type}_M{M_percentage}_J{J_percentage}_{score_int_file}({score_grade_file})"

        # --- Output Bestandsnaam ---
        quick_mode_suffix = "_QM" if quick_mode else ""
        output_filename = (
            f"{bestandsnaam_zonder_extensie}_VR{quick_mode_suffix}{score_suffix}.xlsx"
        )
        output_path = os.path.join(output_dir, output_filename)

        logging.info(f"Schrijven rapport naar: {output_path}")
        with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
            workbook = writer.book
            workbook.set_size(2500, 1500)

            # --- Formaten Definiëren ---
            fmt_header_green = workbook.add_format(
                {
                    "bold": True,
                    "font_size": 14,
                    "font_color": "#006100",
                    "bg_color": "#C6EFCE",
                    "border": 1,
                    "valign": "vcenter",
                }
            )
            fmt_header_red = workbook.add_format({
                "bold": True,
                "font_size": 14,
                "font_color": "#FFFFFF",  # Witte tekst
                "bg_color": "#C00000",  # Identieke donkere rood als Foutmeldingen (was #E06666)
                "border": 1,
                "border_color": "#000000",  # Zwarte rand
                "valign": "vcenter",
                "align": "left",
                "indent": 1
            })
            fmt_header_blue = workbook.add_format({
                "bold": True,
                "font_size": 14,
                "font_color": "#FFFFFF",  # Witte tekst
                "bg_color": "#C00000",  # Rood header voor Foutmeldingen volgens spec
                "border": 1,
                "border_color": "#000000",  # Zwarte rand
                "align": "left",
                "valign": "vcenter",
                "indent": 1
            })
            fmt_label_green = workbook.add_format({
                "font_size": 12, 
                "bg_color": "#E2EFDA",  # Groen data achtergrond
                "font_color": "#000000",  # Zwarte tekst
                "border": 1,
                "border_color": "#000000",  # Zwarte rand
                "indent": 1
            })
            fmt_value_green = workbook.add_format({
                "font_size": 12,
                "bg_color": "#E2EFDA",  # Groen data achtergrond
                "font_color": "#000000",  # Zwarte tekst
                "border": 1,
                "border_color": "#000000",  # Zwarte rand
                "align": "right",
                "num_format": "#,##0"
            })
            fmt_label_red = workbook.add_format(
                {"font_size": 12, "bg_color": "#F2DCDB", "border": 1, "indent": 1}
            )  # Zorg dat label format ook bestaat
            fmt_value_red = workbook.add_format(
                {
                    "font_size": 12,
                    "bg_color": "#F2DCDB",
                    "border": 1,
                    "align": "right",
                    "num_format": "#,##0",
                }
            )
            fmt_value_red_perc = workbook.add_format(
                {
                    "font_size": 12,
                    "bg_color": "#F2DCDB",
                    "border": 1,
                    "align": "right",
                    "num_format": "0.00%",
                }
            )
            fmt_attention_text = workbook.add_format(
                {
                    "font_size": 12,
                    "bg_color": "#F2DCDB",
                    "border": 1,
                    "text_wrap": True,
                    "valign": "top",
                    "indent": 1,
                }
            )
            fmt_error_table_header = workbook.add_format(
                {
                    "bold": True,
                    "font_size": 14,
                    "bg_color": "#D9D9D9",
                    "border": 1,
                    "align": "left",
                    "indent": 1,
                }
            )
            fmt_error_table_cell = workbook.add_format({"font_size": 12, "border": 1, "align": "left", "indent": 1, "bg_color": "#F2DCDB"})
            fmt_error_table_cell_right = workbook.add_format({"font_size": 12, "border": 1, "align": "right", "indent": 1, "bg_color": "#F2DCDB"})
            fmt_error_table_code = workbook.add_format(
                {"font_size": 12, "border": 1, "align": "right", "bg_color": "#F2DCDB"}
            )
            fmt_chart_title = workbook.add_format({"bold": True, "font_size": 12})
            fmt_perc_table = workbook.add_format(
                {"border": 1, "font_size": 12, "num_format": "0.00%"}
            )
            fmt_default_table = workbook.add_format({"border": 1, "font_size": 12})
            fmt_header_orange = workbook.add_format(
                {
                    "bold": True,
                    "bg_color": "#f79645",
                    "font_color": "white",
                    "border": 1,
                    "font_size": 14,
                }
            )  # Voor andere tabellen

            # ==================================================================
            # START CODE VOOR SHEET 1: DASHBOARD
            # ==================================================================
            ws_dash = workbook.add_worksheet("1. Dashboard")
            suppress_excel_errors(ws_dash)
            writer.sheets["1. Dashboard"] = ws_dash
            # Verberg rij 1
            ws_dash.set_row(0, None, None, {"hidden": True})  # Verberg rij 1 (index 0)

            # --- Kolombreedtes Instellen - Kolom opschuiving: nieuwe kolom A (gutter) ---
            ws_dash.set_column("A:A", 5)    # NIEUWE lege gutter kolom (5 pixels)
            # ALLE OUDE KOLOMMEN SCHUIVEN 1 NAAR RECHTS:
            # LINKER KANT (B-F): Statistieken + Foutmeldingen (was A-E)
            ws_dash.set_column("B:B", 90)   # Statistieken/ontbrekende (was A: 90 pixels)
            ws_dash.set_column("C:C", 10)   # Statistieken waarden (was B: 10 pixels)  
            ws_dash.set_column("D:D", 5)    # Smaller column D (was C: 5 pixels)
            # FOUTMELDINGEN KOLOMMEN: Aangepaste breedtes voor nieuwe layout (alles +1)
            ws_dash.set_column("E:E", 40)   # Beschrijving deel 1 (was D: 40 pixels)
            ws_dash.set_column("F:F", 40)   # Beschrijving deel 2 (was E: 40 pixels)
            ws_dash.set_column("G:G", 40)   # Beschrijving deel 3 (was F: 40 pixels)
            ws_dash.set_column("H:H", 10)   # Aantal (was G: 10 pixels)
            ws_dash.set_column("I:I", 15)   # Type (was H: 15 pixels)
            ws_dash.set_column("J:J", 15)   # Type Sheet (was I: 15 pixels)
            ws_dash.set_column("K:K", 10)   # Foutcode (was J: 10 pixels)
            ws_dash.set_column("L:L", 20)   # Aandachtspunten deel 5 (was K: 20 pixels)
            ws_dash.set_column("M:M", 45)   # Aandachtspunten deel 6 (was L: 45 pixels)
            ws_dash.set_column("N:N", 10)   # Foutcode kolom aandachtspunten (was M: 10 pixels)

            # --- TOPMARGE & LOGO: Start content op rij 9+ ---
            # Reserveer B2:G6 voor logo headerzone (rijen 1-6)  
            current_row = 8  # Start content op rij 9 (0-based index 8)
            
            # Voeg GAX logo toe op B2 (rij 1, kolom 1)
            try:
                logo_path = SERVER_PATHS.get("logo_path", "")
                # Plaats logo op B2 met aspect ratio lock en niet gekoppeld aan cellen
                ws_dash.insert_image("B2", logo_path, {
                    'positioning': 0,  # Move & size with cells = OFF (absolute positioning)
                    'x_scale': 0.35,   # Schaal logo naar 35% voor kleinere pasvorm (rijen 1-6)
                    'y_scale': 0.35,   # Behoud aspect ratio 
                })
            except Exception as logo_err:
                # Log error maar ga door met rapport generatie
                logging.warning(f"Logo kon niet worden toegevoegd: {logo_err}")
            
            # --- SCORE BADGE RECHTSBOVEN (H2:K6) ---
            # Maak formats voor de score badge
            fmt_score_badge_bg = workbook.add_format({
                'bg_color': '#F2F2F2',  # Zachte neutrale achtergrond
                'border': 1,
                'border_color': '#D0D0D0',  # Subtiele rand
                'align': 'center',
                'valign': 'vcenter'
            })
            
            
            fmt_score_label = workbook.add_format({
                'font_size': 12,  # Klein label
                'font_color': '#1F1F1F',
                'bold': True,
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': '#F2F2F2',
                'border': 1,
                'border_color': '#D0D0D0'
            })
            
            fmt_score_description = workbook.add_format({
                'font_size': 10,  # Kleine toelichting
                'font_color': '#1F1F1F',
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': '#F2F2F2',
                'border': 1,
                'border_color': '#D0D0D0'
            })
            
            # Bereken scores eerst voor weergave (zonder Config sheet links om pop-up te voorkomen)
            # Zorg voor fallback waarden - gebruik try/except voor veilige toegang tot variabelen
            try:
                M_found_safe = M_found
            except NameError:
                M_found_safe = 0
            
            try:
                ghx_mandatory_fields_safe = ghx_mandatory_fields
            except NameError:
                ghx_mandatory_fields_safe = []
            
            try:
                df_errors_mand_safe = df_errors_mand
            except NameError:
                df_errors_mand_safe = pd.DataFrame()
            
            try:
                df_errors_non_mand_safe = df_errors_non_mand
            except NameError:
                df_errors_non_mand_safe = pd.DataFrame()
            
            try:
                total_rows_safe = total_rows
            except NameError:
                total_rows_safe = 0
            
            # === GEBRUIK NIEUWE SCORE VOOR SHEET 1 DISPLAY ===
            # Gebruik dezelfde score als filename (consistent!)
            totale_score_display = score_result['final_score']
            score_grade = score_result['grade']
            
            # Bepaal randkleur: groen voor B/A/A+, oranje voor C/D, rood voor E/F
            if score_grade in ["B", "A", "A+"]:
                border_color = "#4f6229"  # Groen
            elif score_grade in ["C", "D"]:
                border_color = "#FF5E1A"  # Oranje
            else:  # E, F
                border_color = "#c00000"  # Rood
            
            # Update format voor KWALITEITSCORE met dynamische randkleur en tekstkleur
            fmt_score_number = workbook.add_format({
                'font_size': 26,
                'font_color': border_color,  # Tekstkleur matcht randkleur
                'bold': True,
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': '#FFFFFF',
                'top': 2, 'left': 2, 'right': 2,  # Alleen boven/links/rechts rand
                'top_color': border_color,
                'left_color': border_color,
                'right_color': border_color
            })
            
            # Hoofdscore cel E3:F4 (alleen kolommen E en F)
            ws_dash.merge_range("E3:F4", f"KWALITEITSCORE: {totale_score_display}/100 - CIJFER {score_grade}", fmt_score_number)
            
            # Cijfertoekenning regel (E4:F4) - bold, zwart, groter, met dynamische randkleur
            fmt_score_small = workbook.add_format({
                'font_size': 11,
                'bold': True,
                'align': 'center',
                'valign': 'vcenter',
                'font_color': '#000000',
                'bg_color': '#FFFFFF',  # Witte achtergrond
                'bottom': 2, 'left': 2, 'right': 2,  # Alleen onder/links/rechts rand
                'bottom_color': border_color,
                'left_color': border_color,
                'right_color': border_color
            })
            ws_dash.merge_range("E5:F5", "Voor meer informatie over de kwaliteitscore en hoe het berekend wordt, ga naar sheet 2.", fmt_score_small)
            
            # --- NIEUWE LAYOUT: Links Statistieken, Rechts Actiepunten ---
            
            # --- APARTE TEMPLATE TABEL (voor alle template types) ---
            template_table_end_row = current_row - 1  # Default: geen template tabel
            
            # === QUICK MODE TABEL (rij 8-9 indien actief) ===
            quick_mode_active = (max_rows is not None and max_rows == 5000)

            if quick_mode_active:
                # Quick Mode tabel op vaste positie: rij 8-9
                quick_mode_start_row = 7  # 0-based = Excel rij 8
                
                # Formats voor Quick Mode tabel
                fmt_quickmode_header = workbook.add_format({
                    'bold': True,
                    'font_color': '#FFFFFF',
                    'font_size': 14,
                    'bg_color': '#FF0000',  # Rood
                    'border': 1,
                    'border_color': '#000000',
                    'align': 'left',
                    'valign': 'vcenter',
                    'indent': 1
                })
                
                fmt_quickmode_data = workbook.add_format({
                    "font_size": 12, 
                    "bg_color": "#FFE6E6",  # Licht rood
                    "font_color": "#000000",
                    "border": 1,
                    "border_color": "#000000",
                    "indent": 1
                })
                
                # Rij 8: Header (alleen B8:C8)
                ws_dash.merge_range(
                    f"B{quick_mode_start_row + 1}:C{quick_mode_start_row + 1}",
                    "QUICK MODE VALIDATIE",
                    fmt_quickmode_header,
                )
                ws_dash.set_row(quick_mode_start_row, 18)
                
                # Rij 9: Beschrijving (alleen B9:C9)
                if total_rows:
                    quick_text = f"Alleen de eerste {max_rows:,} van {total_rows:,} rijen zijn gevalideerd"
                else:
                    quick_text = f"Alleen de eerste {max_rows:,} rijen zijn gevalideerd"
                
                ws_dash.merge_range(
                    f"B{quick_mode_start_row + 2}:C{quick_mode_start_row + 2}",
                    quick_text,
                    fmt_quickmode_data,
                )
                ws_dash.set_row(quick_mode_start_row + 1, 16)
                
                # Schuif alle andere content 3 rijen naar beneden
                base_content_start_row = 11  # Was 8, nu 11
                logging.info(f"Quick Mode tabel toegevoegd op rijen 8-9. Content start op rij {base_content_start_row}")
            else:
                # Normale modus: content start op rij 8
                base_content_start_row = 8
                logging.info("Normale validatie: geen Quick Mode tabel")

            # Template-tabel ALTIJD tonen (voor TG, TD, ALT) 
            if True:  # Altijd uitvoeren
                # Template start op base_content_start_row (rij 8 normaal, rij 11 met Quick Mode)
                template_start_row = base_content_start_row - 1  # 0-based
                
                # Template tabel header format - zelfde thema als statistieken
                fmt_template_header = workbook.add_format({
                    'bold': True,
                    'font_color': '#FFFFFF',
                    'font_size': 14,
                    'bg_color': '#4F6229',  # Zelfde groen als statistieken
                    'border': 1,
                    'border_color': '#000000',
                    'align': 'left',
                    'valign': 'vcenter',
                    'indent': 1
                })
                
                # Template data format - zelfde als statistieken data
                fmt_template_label = workbook.add_format({
                    "font_size": 12, 
                    "bg_color": "#E2EFDA",  # Zelfde groen als statistieken
                    "font_color": "#000000",
                    "border": 1,
                    "border_color": "#000000",
                    "indent": 1
                })
                fmt_template_value = workbook.add_format({
                    "font_size": 12,
                    "bg_color": "#E2EFDA",  # Zelfde groen als statistieken
                    "font_color": "#000000",
                    "border": 1,
                    "border_color": "#000000",
                    "align": "left",  # Links uitlijnen voor template info
                    "indent": 1  # Inspringen zoals andere tabellen
                })
                
                # Template tabel header - VASTE POSITIE rij 8 (Excel rij 8)
                ws_dash.merge_range(
                    f"B{template_start_row + 1}:C{template_start_row + 1}",  # Excel 1-based, rij 8
                    "Template",
                    fmt_template_header,
                )
                ws_dash.set_row(template_start_row, 18)
                
                # ALTIJD EERSTE REGEL: Bestandsnaam 
                template_filename_row = base_content_start_row
                ws_dash.merge_range(
                    f"B{template_filename_row + 1}:C{template_filename_row + 1}",  # Excel 1-based
                    bestandsnaam,  # Gebruik originele bestandsnaam
                    fmt_template_value,
                )
                
                # ALTIJD TWEEDE REGEL: Template Type (alleen het type, geen code)
                template_type_row = base_content_start_row + 1
                # Template Type informatie genereren - alleen het basis type
                if template_type == "TG":
                    template_type_display = "Template Generator"
                elif template_type == "DT": 
                    template_type_display = "Default Template"
                elif template_type == "AT":
                    template_type_display = "Onbekende Template"
                elif template_type == "N": 
                    template_type_display = "Nieuw GHX Template"
                elif template_type == "O":
                    template_type_display = "Oud/Leverancier Template"
                else:
                    template_type_display = f"Template Type {template_type}"
                
                ws_dash.merge_range(
                    f"B{template_type_row + 1}:C{template_type_row + 1}",  # Excel 1-based
                    template_type_display,
                    fmt_template_value,
                )
                
                # DERDE REGEL: Template Versie (alleen voor TG en DT templates)
                current_template_row = base_content_start_row + 2  # Start na Template Type
                
                # Extracteer en toon versie alleen voor TG en DT templates
                if template_type == "TG" and template_context:
                    # TG: uit A2 cel via template_context
                    version_info = template_context.get("version_info", {})
                    template_version = version_info.get("version", "Onbekend")
                    version_display = f"Versie: {template_version}"
                    ws_dash.merge_range(
                        f"B{current_template_row + 1}:C{current_template_row + 1}",
                        version_display,
                        fmt_template_value,
                    )
                    current_template_row += 1
                elif template_type == "DT":
                    # DT: uit A1 cel 
                    from .price_tool import extract_dt_template_version
                    try:
                        dt_version_info = extract_dt_template_version(excel_path)
                        if dt_version_info:
                            template_version = dt_version_info.get("version", "Onbekend")
                        else:
                            template_version = "Onbekend"
                    except Exception as e:
                        logging.warning(f"Fout bij DT versie extractie: {e}")
                        template_version = "Onbekend"
                    
                    version_display = f"Versie: {template_version}"
                    ws_dash.merge_range(
                        f"B{current_template_row + 1}:C{current_template_row + 1}",
                        version_display,
                        fmt_template_value,
                    )
                    current_template_row += 1
                # AT templates: geen versie regel - "Onbekende Template" is al duidelijk genoeg
                
                # VIERDE REGEL: Generatie Tijd (alleen voor TG templates)
                if template_type == "TG" and template_context:
                    # Extracteer generatie tijd uit version_info
                    version_info = template_context.get("version_info", {})
                    generation_time = version_info.get("release_date")
                    
                    # Als geen release_date, probeer generated veld
                    if not generation_time:
                        generated_text = version_info.get("generated", "")
                        if generated_text:
                            # Extracteer alleen de eerste regel (de datum/tijd)
                            first_line = generated_text.split('\n')[0].strip()
                            # Check of het een datum/tijd format is
                            import re
                            if re.match(r'\d{2}-\d{2}-\d{4} \d{2}:\d{2}', first_line):
                                generation_time = first_line
                    
                    # Toon generatie tijd indien beschikbaar
                    if generation_time:
                        time_display = f"Gegenereerd op: {generation_time}"
                        ws_dash.merge_range(
                            f"B{current_template_row + 1}:C{current_template_row + 1}",
                            time_display,
                            fmt_template_value,
                        )
                        current_template_row += 1
                
                # TG-SPECIFIEKE CONTENT: Template Code en Categorie
                if template_type == "TG" and template_context:
                    # Template Code (zoals S-LM-0-0-0-umcu-V77-M19)  
                    # Probeer eerst uit template_context, anders uit enhanced template display
                    template_code = template_context.get("template_code")
                    if not template_code and template_display_info:
                        # Parse uit type_description als het daar in staat
                        type_desc = template_display_info.get("type_description", "")
                        if "(" in type_desc and ")" in type_desc:
                            # Bijvoorbeeld: "Template Generator (S-LM-0-0-0-umcu-V77-M19)"
                            template_code = type_desc.split("(")[1].split(")")[0]
                    
                    if not template_code:
                        template_code = "Onbekende Template Code"
                        
                    ws_dash.merge_range(
                        f"B{current_template_row + 1}:C{current_template_row + 1}",
                        template_code,
                        fmt_template_value,
                    )
                    current_template_row += 1
                    
                    # Template categorie info - nuttige informatie voor gebruiker
                    # Probeer eerst uit configuration (nieuwe structuur)
                    config = template_context.get("configuration", {})
                    product_types = config.get("product_types", template_context.get("product_types", []))
                    institutions = config.get("institutions", template_context.get("institutions", []))
                    
                    # Categorie informatie (product types)
                    if product_types:
                        if isinstance(product_types, list):
                            # Nederlandse namen voor product types
                            product_names = []
                            for pt in product_types:
                                if pt.lower() == 'lab':
                                    product_names.append('Laboratorium')
                                elif pt.lower() == 'medisch':
                                    product_names.append('Medisch')
                                elif pt.lower() == 'facilitair':
                                    product_names.append('Facilitair')
                                elif pt.lower() == 'overige':
                                    product_names.append('Overige')
                                else:
                                    product_names.append(pt.title())
                            categorie_str = ", ".join(product_names)
                        else:
                            categorie_str = str(product_types).title()
                        
                        ws_dash.merge_range(
                            f"B{current_template_row + 1}:C{current_template_row + 1}",
                            f"Categorie: {categorie_str}",
                            fmt_template_value,
                        )
                        current_template_row += 1
                    
                    # Organisaties informatie - gebruik korte codes indien beschikbaar
                    institution_codes = config.get("institution_codes", template_context.get("institution_codes", []))
                    if institution_codes:
                        # Gebruik korte codes zoals ze in de Template Generator stamp staan
                        if isinstance(institution_codes, list):
                            inst_str = ", ".join([code.upper() for code in institution_codes])
                        else:
                            inst_str = str(institution_codes).upper()
                    elif institutions:
                        # Fallback naar volledige namen
                        if isinstance(institutions, list):
                            inst_str = ", ".join([inst.upper() for inst in institutions])
                        else:
                            inst_str = str(institutions).upper()
                    else:
                        inst_str = None
                        
                    if inst_str:
                        ws_dash.merge_range(
                            f"B{current_template_row + 1}:C{current_template_row + 1}",
                            f"Organisaties: {inst_str}",
                            fmt_template_value,
                        )
                        current_template_row += 1
                    
                    # Template velden info
                    if template_context.get("decisions"):
                        visible_count = template_context["decisions"].get("visible_fields", 0)
                        # Gebruik de mandatory_fields waarde uit Template Generator code (M18=18)
                        mandatory_count = template_context["decisions"].get("mandatory_fields", 0)
                        velden_info = f"Velden: {visible_count} zichtbaar, {mandatory_count} verplicht"
                        ws_dash.merge_range(
                            f"B{current_template_row + 1}:C{current_template_row + 1}",
                            velden_info,
                            fmt_template_value,
                        )
                        current_template_row += 1
                
                # Template tabel eindigt op huidige rij
                template_table_end_row = current_template_row
                
                # Bereken current_row gebaseerd op Template-tabel grootte
                # Voor TG: rij 9 (bestandsnaam) + 10 (template type) + extra regels
                # Voor TD/ALT: rij 9 (bestandsnaam) + 10 (template type)
                current_row = template_table_end_row + 1  # Stats header na Template-tabel + 1 witregel
            
            # Nieuw format voor Statistieken header - groen volgens specificaties
            fmt_header_stats = workbook.add_format({
                'bold': True,
                'font_color': '#FFFFFF',
                'font_size': 14,
                'bg_color': '#4F6229',  # Groen header
                'border': 1,
                'border_color': '#000000',  # Zwarte rand
                'align': 'left',
                'valign': 'vcenter',
                'indent': 1
            })
            
            # LINKER KANT: Statistieken (B{current_row}-C{current_row}, A blijft gutter)
            ws_dash.merge_range(
                f"B{current_row+1}:C{current_row+1}",  # B tot C op huidige rij Excel-style (1-based)
                "Belangrijkste Statistieken",
                fmt_header_stats,
            )
            ws_dash.set_row(current_row + 1, 18)  # Hoogte header rij (correct rij)
            
            # RECHTER KANT: Foutmeldingen header ALTIJD op rij 7 (Excel rij 8) - BLIJFT ONGEWIJZIGD
            fout_header_row = 7  # VAST: rechterkant verandert niet
            ws_dash.merge_range(
                f"E{fout_header_row + 1}:K{fout_header_row + 1}",  # E tot K op rij 8 (Excel 1-based)
                "Foutmeldingen",
                fmt_header_blue,  # Blauwe header voor foutmeldingen
            )
            
            # Voeg grijze subheader toe - ALLEEN voor foutmeldingen rechts
            fmt_subheader_grey = workbook.add_format({
                "bold": True,
                "bg_color": "#D9D9D9",  # Grijs subheader volgens spec
                "font_color": "#000000",  # Zwarte tekst
                "border": 1,
                "border_color": "#000000",  # Zwarte rand
                "font_size": 12,
                "align": "left",
                "valign": "vcenter",
                "indent": 1
            })
            
            # RECHTER KANT: Foutmeldingen subheaders ALTIJD op rij 8 (Excel rij 9) - BLIJFT ONGEWIJZIGD
            fout_subheader_row = 8  # VAST: rechterkant verandert niet
            # Beschrijving spreidt over E, F, G (was D, E, F)
            ws_dash.merge_range(
                f"E{fout_subheader_row + 1}:G{fout_subheader_row + 1}",  # E-G voor Beschrijving op rij 10
                "Beschrijving",
                fmt_subheader_grey
            )
            ws_dash.write(fout_subheader_row, 7, "Aantal", fmt_subheader_grey)         # H op rij 10
            ws_dash.write(fout_subheader_row, 8, "Type", fmt_subheader_grey)           # I op rij 10
            ws_dash.write(fout_subheader_row, 9, "Type (Sheet)", fmt_subheader_grey)   # J op rij 10
            ws_dash.write(fout_subheader_row, 10, "Foutcode", fmt_subheader_grey)      # K op rij 10
            ws_dash.set_row(current_row, 18)  # Normale rijhoogte
            
            # Statistieken data begint direct na header op rij 10 (header is rij 9)
            stats_start_row = current_row + 1  # Rij 10 (direct na header rij 9)
            
            # GEEN current_row increment hier - data moet DIRECT na header
            aantal_velden_totaal = total_rows * total_original_cols
            
            # CORRECTIE: "Aantal aanwezige/afwezige verplichte velden" betekent KOLOMMEN, niet velden
            # Voor alle template types: tel alleen kolommen (niet kolommen * rijen)
            aantal_aanw_verpl_velden = M_found        # Aantal verplichte KOLOMMEN die aanwezig zijn
            aantal_afw_verpl_velden = M_missing       # Aantal verplichte KOLOMMEN die afwezig zijn
            aantal_aanw_lege_verpl_velden = empty_in_present

            # Tel rejection errors (afkeuringen) - alleen regels die door Gatekeeper zouden worden afgewezen
            aantal_afkeuringen = 0
            if not df_errors.empty and "code" in df_errors.columns:
                # Tel unieke rijen met rejection errors (codes 700-749)
                rejection_rows = df_errors[
                    df_errors["code"].apply(lambda x: str(x).strip().isdigit() and 700 <= int(float(str(x).strip())) <= 749)
                ]["Rij"].nunique()
                aantal_afkeuringen = rejection_rows

            # Enhanced Template informatie met parsed code support
            if template_type == "TG":
                # Gebruik enhanced template display info
                template_type_info = template_display_info.get("type_description", "Template Generator")
                
                # Voeg code info toe indien beschikbaar
                if template_display_info.get("code_info"):
                    template_type_info += f" | {template_display_info['code_info']}"
                
                # Voeg context info toe indien beschikbaar
                if template_display_info.get("context_info"):
                    template_type_info += f" | {template_display_info['context_info']}"
                
                # Voeg institution info toe indien beschikbaar
                if template_display_info.get("institution_info"):
                    template_type_info += f" | {template_display_info['institution_info']}"
                
                # Voeg statistics info toe indien beschikbaar
                if template_display_info.get("statistics_info"):
                    template_type_info += f" | {template_display_info['statistics_info']}"
                
                # Voeg ingeklapte velden informatie toe
                collapsed_count = summary_data.get('collapsed_fields_count', 0)
                if collapsed_count > 0:
                    template_type_info += f" | {collapsed_count} velden ingeklapt"
                    
                # Fallback naar legacy template_context indien geen enhanced info
                if not template_display_info.get("type_description") and template_context:
                    template_choice = template_context.get("template_choice", "standard")
                    product_types = template_context.get("product_types", ["facilitair"])
                    institutions = template_context.get("institutions", [])
                    
                    if isinstance(product_types, list):
                        product_types_str = ", ".join(product_types)
                    else:
                        product_types_str = str(product_types)
                    
                    template_type_info = "TG"  # Template Generator (kort)
                        
            elif template_type == "N":
                template_type_info = "DT"  # Default Template (kort)
                    
            elif template_type == "O":
                template_type_info = "ALT"  # Alternatief Template (kort)
            else:
                template_type_info = "UNK"  # Unknown
            
            # Helper functie voor Template Generator header matching
            def normalize_header_for_matching(header):
                """Normalize complex Template Generator headers to match mandatory field names"""
                if pd.isna(header) or not str(header).strip():
                    return header
                
                # Voor Template Generator: neem eerste regel en clean het op
                cleaned = str(header).split("\n")[0].strip()
                
                # Verwijder trailing spaties en extra karakters
                cleaned = cleaned.rstrip()
                
                # Specifieke fixes voor bekende problemen
                # Fix: "verpakkingseenheid" -> "Verpakkingseenheid" (kapitaal V)
                if "verpakkingseenheid" in cleaned.lower():
                    cleaned = cleaned.replace("verpakkingseenheid", "Verpakkingseenheid")
                    cleaned = cleaned.replace("VERPAKKINGSEENHEID", "Verpakkingseenheid")
                
                return cleaned
            
            def find_matching_column(mandatory_field, df_columns):
                """Find a Template Generator column that matches the mandatory field name"""
                # Probeer eerst exacte match
                if mandatory_field in df_columns:
                    return mandatory_field
                    
                # Voor Template Generator: probeer normalized matching
                normalized_mandatory = mandatory_field.strip()
                
                for col in df_columns:
                    normalized_col = normalize_header_for_matching(col)
                    if normalized_col == normalized_mandatory:
                        return col
                        
                    # Extra check: probeer ook zonder haakjes inhoud te matchen
                    # bijv. "Brutoprijs" zou matchen met "Brutoprijs (extra tekst)"
                    base_mandatory = normalized_mandatory.split("(")[0].strip()
                    base_col = normalized_col.split("(")[0].strip() 
                    if base_mandatory and base_col == base_mandatory:
                        return col
                        
                return None

            # Voor Template Generator: maak aparte Template tabel (geen Template info in stats)
            # Voor andere templates: voeg Template Type toe aan statistieken
            if template_type == "TG" and template_context and template_context.get("decisions"):
                # Template Generator: start statistieken ZONDER Template info
                stats_data_original = []
                # Voor TG templates: gebruik alleen mandatory_list uit decisions
                tg_mandatory_fields = template_context["decisions"].get("mandatory_list", [])
                
                # NIEUWE SLIMME MATCHING voor Template Generator headers
                matched_fields = []
                missing_fields = []
                
                for mandatory_field in tg_mandatory_fields:
                    matching_col = find_matching_column(mandatory_field, df.columns)
                    if matching_col:
                        matched_fields.append(mandatory_field)
                        # TG match gevonden voor verplicht veld
                    else:
                        missing_fields.append(mandatory_field)
                        # TG verplicht veld niet gevonden
                
                tg_aanwezige_verpl = len(matched_fields)
                tg_ontbrekende_verpl = len(missing_fields)
                
                # Update ook de globale missing_mandatory_columns voor TG templates
                missing_mandatory_columns = missing_fields
                present_mandatory_columns = matched_fields
                
                # Voor TG templates: gebruik template_context mandatory fields voor berekeningen
                # Update M_found en M_missing met TG specifieke getallen
                M_found = tg_aanwezige_verpl      # Voor consistentie met globale variabelen 
                M_missing = tg_ontbrekende_verpl  # Voor actiepunten en missing kolommen lijst
                
                # Nu gebruiken we dezelfde berekening als voor andere templates (maar met updated M_found/M_missing)
                aantal_aanw_verpl_velden = M_found   # Nu correct omdat M_found is bijgewerkt voor TG
                aantal_afw_verpl_velden = M_missing  # Nu correct omdat M_missing is bijgewerkt voor TG
                
                # Voeg statistieken toe met correcte labels voor Quick Mode
                quick_mode_suffix = " (over de eerste 5000 regels)" if max_rows is not None else ""
                stats_data_original.extend([
                    ("Aantal rijen", total_rows),
                    ("Aantal kolommen", total_original_cols),  # Nu gefilterde kolom count voor TG
                    ("Aantal aanwezige verplichte kolommen", aantal_aanw_verpl_velden),  # Nu consistent
                    ("Aantal afwezige verplichte kolommen", aantal_afw_verpl_velden),    # Nu consistent
                    ("Aantal velden", aantal_velden_totaal),  # Verplaatst naar beneden
                    (f"Aantal gevulde verplichte velden{quick_mode_suffix}", total_filled_in_present),
                    (f"Aantal aanwezige lege verplichte velden{quick_mode_suffix}", aantal_aanw_lege_verpl_velden),
                ])
            else:
                # Voor andere templates: start ZONDER Template Type (die staat nu in Template-tabel)
                stats_data_original = []
                
                # Voeg reguliere statistieken toe met correcte labels voor Quick Mode
                quick_mode_suffix = " (over de eerste 5000 regels)" if max_rows is not None else ""
                stats_data_original.extend([
                    ("Aantal rijen", total_rows),
                    ("Aantal kolommen", total_original_cols),
                    ("Aantal aanwezige verplichte kolommen", aantal_aanw_verpl_velden),
                    ("Aantal afwezige verplichte kolommen", aantal_afw_verpl_velden),
                    ("Aantal velden", aantal_velden_totaal),  # Verplaatst naar beneden
                    (f"Aantal gevulde verplichte velden{quick_mode_suffix}", total_filled_in_present),
                    (f"Aantal aanwezige lege verplichte velden{quick_mode_suffix}", aantal_aanw_lege_verpl_velden),
                ])
            # SIMPELE STATISTIEKEN DATA LOGICA - FINAL CORRECTIE
            # Header staat op current_row+1, data moet DIRECT daaronder op current_row+1  
            data_row = current_row + 1  # Start DIRECT na header 
            
            for i, (key, value) in enumerate(stats_data_original):
                row = data_row + i  # Gewoon i toevoegen aan startpositie
                # Simple mapping: item naar Excel rij
                
                # Schrijf label en waarde
                ws_dash.write(row, 1, key, fmt_label_green)
                if isinstance(value, (int, float)):
                    ws_dash.write_number(row, 2, value, fmt_value_green)
                else:
                    ws_dash.write(row, 2, str(value), fmt_value_green)
            stats_end_row = data_row + len(stats_data_original) - 1

            # Gebruik actions_end_row van de nieuwe A-B Actiepunten voor aandachtspunten positionering

            # --- LINKER KANT: Ontbrekende verplichte kolommen onder Statistieken (A-B) ---
            # Definieer format eerst - met inspringing
            fmt_missing_col_header = workbook.add_format({
                'bold': True, 
                'font_color': '#FFFFFF',  # Witte tekst
                'font_size': 14, 
                'bg_color': '#E26B09',  # Oranje header volgens spec
                'border': 1,
                'border_color': '#000000',  # Zwarte rand
                'align': 'left', 
                'indent': 1
            })
            
            # Positioneer met extra lege rij tussen statistieken en ontbrekende kolommen
            missing_start_row = stats_end_row + 2  # 1 lege rij onder statistieken + 1 voor header
            ws_dash.merge_range(
                f"B{missing_start_row+1}:C{missing_start_row+1}",  # B-C, A blijft gutter
                "Ontbrekende verplichte kolommen",
                fmt_missing_col_header,  # Rode header
            )
            ws_dash.set_row(missing_start_row, 18)
            
            # Data onder header: schrijf de ontbrekende kolommen
            fmt_missing_col_item = workbook.add_format({
                'font_color': '#000000',  # Zwarte tekst
                'bg_color': '#FBD5B5',  # Oranje data achtergrond volgens spec
                'font_size': 12, 
                'border': 1,
                'border_color': '#000000',  # Zwarte rand
                'align': 'left', 
                'indent': 1
            })
            
            missing_data_row = missing_start_row + 1  # Direct onder header
            if M_missing > 0 and missing_mandatory_columns:
                for col_name in missing_mandatory_columns:
                    # Merge rijen B-C net zoals de header
                    ws_dash.merge_range(
                        f"B{missing_data_row+1}:C{missing_data_row+1}",
                        col_name,
                        fmt_missing_col_item
                    )
                    ws_dash.set_row(missing_data_row, 18)
                    missing_data_row += 1
            else:
                # Merge ook de "Geen ontbrekende kolommen" regel
                ws_dash.merge_range(
                    f"B{missing_data_row+1}:C{missing_data_row+1}",
                    "Geen ontbrekende kolommen",
                    fmt_missing_col_item
                )
                missing_data_row += 1
            
            missing_end_row = missing_data_row

            # --- LINKER KANT: Belangrijkste Actiepunten onder Ontbrekende (B-C) ---
            # Header voor Actiepunten - 1 witte regel onder Ontbrekende kolommen
            actions_start_row = missing_end_row + 1  # 1 witte regel tussen
            ws_dash.merge_range(
                f"B{actions_start_row+1}:C{actions_start_row+1}",  # B-C (was A-B)
                "Belangrijkste Actiepunten",
                fmt_missing_col_header,  # Zelfde rode header als Ontbrekende kolommen
            )
            ws_dash.set_row(actions_start_row, 18)
            
            # Data voor Actiepunten - direct onder header
            actions_data_row = actions_start_row + 1  # Direct onder header
            actions_data_original = [
                (
                    "Percentage ingevulde verplichte velden (incl. ontbrekende)",
                    percentage_ingevuld_incl_missing / 100,
                ),
                (f"Aantal regels mogelijk afgewezen door Gatekeeper{quick_mode_suffix}", aantal_afkeuringen),
            ]

            # Format voor Actiepunten data - met inspringing
            fmt_action_label = workbook.add_format({
                'font_color': '#000000',  # Zwarte tekst
                'bg_color': '#FBD5B5',  # Oranje data achtergrond zoals ontbrekende kolommen
                'font_size': 12, 
                'border': 1,
                'border_color': '#000000',  # Zwarte rand
                'align': 'left', 
                'indent': 1
            })
            fmt_action_value = workbook.add_format({
                'font_color': '#000000',  # Zwarte tekst
                'bg_color': '#FBD5B5',  # Oranje data achtergrond
                'font_size': 12, 
                'border': 1,
                'border_color': '#000000',  # Zwarte rand
                'align': 'right'
            })

            for key, value in actions_data_original:
                # Kolom B voor beschrijving, Kolom C voor waarde (was A,B)
                ws_dash.write(actions_data_row, 1, key, fmt_action_label)  # Kolom B (was A)
                
                # Controleer of het de percentage regel is
                if "Percentage" in key:
                    # Formatteer als percentage string
                    value_str = f"{value * 100:.2f}%"
                    ws_dash.write_string(actions_data_row, 2, value_str, fmt_action_value)  # Kolom C (was B)
                else:
                    # Schrijf als getal
                    ws_dash.write_number(actions_data_row, 2, value, fmt_action_value)  # Kolom C (was B)
                    
                ws_dash.set_row(actions_data_row, 18)
                actions_data_row += 1
            
            actions_end_row = actions_data_row

            # Load error code descriptions - support both v18 and v20 structure
            # DEBUG: Log config structure
            logging.info(f"DEBUG Sheet 1: Config keys beschikbaar: {list(config.keys()) if config else 'Config is None'}")
            
            # Voor TG templates: config bevat alleen template settings, niet validation rules
            # We moeten error descriptions direct uit JSON file laden
            if template_context and template_context.get('type') == 'TG':
                # TG Template: laad error descriptions direct uit JSON file
                logging.info("DEBUG Sheet 1: TG Template - laad error descriptions uit JSON file")
                try:
                    import json
                    with open(JSON_CONFIG_PATH, 'r', encoding='utf-8') as f:
                        full_config = json.load(f)
                    
                    if "global_settings" in full_config and "error_code_descriptions" in full_config["global_settings"]:
                        error_code_desc = full_config["global_settings"]["error_code_descriptions"]
                        logging.info(f"DEBUG Sheet 1: {len(error_code_desc)} error codes geladen uit JSON file voor TG")
                    else:
                        error_code_desc = {}
                        logging.warning("DEBUG Sheet 1: Geen error descriptions in JSON file voor TG")
                except Exception as e:
                    logging.error(f"DEBUG Sheet 1: Fout bij laden JSON voor TG: {e}")
                    error_code_desc = {}
            elif "global_settings" in config and "error_code_descriptions" in config["global_settings"]:
                # v20 structure (original JSON)
                error_code_desc = config["global_settings"]["error_code_descriptions"]
                logging.info(f"DEBUG Sheet 1: Gebruikt v20 structure, {len(error_code_desc)} error codes geladen")
            elif "error_code_descriptions" in config:
                # v18 structure (normalized or original v18)
                error_code_desc = config["error_code_descriptions"]
                logging.info(f"DEBUG Sheet 1: Gebruikt v18 structure, {len(error_code_desc)} error codes geladen")
            else:
                # Fallback: empty dict
                error_code_desc = {}
                logging.warning("DEBUG Sheet 1: Geen error code descriptions gevonden in config!")
            
            if "724" not in error_code_desc:
                error_code_desc["724"] = "UOM-relatie conflict"
            if "721" not in error_code_desc:
                error_code_desc["721"] = (
                    "Formaat Omschrijving Verp.eenheid (Waarschuwing)"
                )

            df_foutcodes_top = pd.DataFrame()
            # Voor foutmeldingen tabel - VASTE POSITIES (rechterkant blijft ongewijzigd)
            table_subheader_row = 8  # VAST: rechterkant verandert niet
            table_start_row = 9  # VAST: rechterkant verandert niet
            table_end_row = table_start_row + 1  # Default end row
            if not df_errors.empty:
                # Check of 'code' kolom bestaat voor we verder gaan
                if "code" in df_errors.columns:
                    # Simpel: groepeer alle fouten alleen op code, net als in het notebook
                    df_foutcodes = df_errors.groupby("code").size().reset_index(name="Aantal")
                    
                    # Filter lege codes uit
                    df_foutcodes = df_foutcodes[df_foutcodes["code"] != ""]
                    
                    # Maak beschrijving op basis van de foutcode en verwijder FLAG: prefix
                    # DEBUG: Log foutcodes en beschrijvingen
                    logging.info(f"DEBUG Sheet 1: Aantal foutcodes gevonden: {len(df_foutcodes)}")
                    if not df_foutcodes.empty:
                        logging.info(f"DEBUG Sheet 1: Eerste paar foutcodes: {df_foutcodes['code'].head().tolist()}")
                    
                    df_foutcodes["Beschrijving"] = df_foutcodes["code"].apply(
                        lambda x: error_code_desc.get(str(x).strip(), f"Code: {x}").replace("FLAG: ", "")
                    )
                    
                    # DEBUG: Log beschrijvingen
                    if not df_foutcodes.empty:
                        logging.info(f"DEBUG Sheet 1: Eerste beschrijving: '{df_foutcodes['Beschrijving'].iloc[0] if len(df_foutcodes) > 0 else 'Geen'}'")
                        # Check of beschrijvingen leeg zijn
                        empty_desc = df_foutcodes[df_foutcodes["Beschrijving"].str.strip() == ""]
                        if not empty_desc.empty:
                            logging.warning(f"DEBUG Sheet 1: {len(empty_desc)} lege beschrijvingen gevonden voor codes: {empty_desc['code'].tolist()}")

                    # --- NIEUWE CODE: Bepaal sets van error codes VOOR de helper functie ---
                    mandatory_error_codes = set()
                    if not df_errors_mand.empty and "code" in df_errors_mand.columns:
                        mandatory_error_codes = set(df_errors_mand["code"].unique())

                    non_mandatory_error_codes = set()
                    if not df_errors_non_mand.empty and "code" in df_errors_non_mand.columns:
                        non_mandatory_error_codes = set(df_errors_non_mand["code"].unique())
                    # Gebruik df_errors_non_mand die *eerder* in genereer_rapport is gedefinieerd
                    if (
                        not df_errors_non_mand.empty
                        and "code" in df_errors_non_mand.columns
                    ):
                        non_mandatory_error_codes = set(
                            df_errors_non_mand["code"].unique()
                        )
                    # --- EINDE NIEUWE CODE ---

                    # --- AANGEPASTE HELPER FUNCTIE ---
                    def get_error_type(code):
                        types = set()
                        # Gebruik nu de vooraf berekende sets
                        if code in mandatory_error_codes:
                            types.add("Zie sheet 3")  # Tekst aangepast
                        if code in non_mandatory_error_codes:
                            types.add("Zie sheet 5")  # Tekst aangepast
                        if not types:
                            return ""
                        # Als beide aanwezig zijn, retourneer "Zie sheet 3 & 5", anders de enige aanwezige
                        if len(types) == 2:
                            return "Zie sheet 3 & 5"
                        else:
                            return list(types)[0]  # Retourneer het enige element

                    # --- EINDE AANGEPASTE HELPER ---
                    df_foutcodes["Type (Sheet)"] = df_foutcodes.apply(
                        lambda row: get_error_type(row["code"]), axis=1
                    )  # Nu per foutcode, maar kan verder worden uitgebreid naar veld+code indien nodig
                    
                    # Voeg Type categorisering kolom toe
                    df_foutcodes["Type"] = df_foutcodes["code"].apply(get_error_category)
                    df_foutcodes = df_foutcodes.sort_values(
                        "Aantal", ascending=False
                    ).reset_index(drop=True)
                    df_foutcodes_top = df_foutcodes.head(10)
                    # Herschik en hernoem kolommen pas na het berekenen van Type (Sheet) en Type
                    df_foutcodes_top = df_foutcodes_top[
                        ["Beschrijving", "Aantal", "Type", "Type (Sheet)", "code"]
                    ]
                    df_foutcodes_top = df_foutcodes_top.rename(
                        columns={"code": "Foutcode"}
                    )

                    table_header_row = table_subheader_row + 1  # Start direct na subheader
                    # Data wordt direct geschreven met nieuwe kolom mapping
                    # Nieuwe mapping: Beschrijving=E-G(merged), Aantal=H(7), Type=I(8), Type(Sheet)=J(9), Foutcode=K(10)
                    for r_idx, row_data in df_foutcodes_top.iterrows():
                        current_table_row = table_header_row + r_idx
                        
                        # Set row height for better readability
                        ws_dash.set_row(current_table_row, 18)
                        
                        # Custom kolom mapping voor nieuwe layout
                        for c_idx, cell_value in enumerate(row_data):
                            col_name = df_foutcodes_top.columns[c_idx]
                            
                            # Ensure cell_value is never None or NaN
                            if pd.isna(cell_value) or cell_value is None:
                                cell_value = ""
                            
                            fmt = (
                                fmt_error_table_code
                                if col_name == "Foutcode"
                                else fmt_error_table_cell_right
                                if col_name == "Aantal"
                                else fmt_error_table_cell
                            )
                            
                            try:
                                if col_name == "Beschrijving":
                                    # Beschrijving spreidt over E-G (kolommen 4-6, was 3-5)
                                    ws_dash.merge_range(
                                        f"E{current_table_row+1}:G{current_table_row+1}",
                                        str(cell_value),
                                        fmt
                                    )
                                elif col_name == "Aantal":
                                    # Aantal naar kolom H (7, was 6)
                                    try:
                                        if cell_value != "":
                                            num_val = int(float(str(cell_value)))  # Handle float strings
                                            ws_dash.write_number(current_table_row, 7, num_val, fmt)
                                        else:
                                            ws_dash.write_string(current_table_row, 7, "0", fmt)
                                    except (ValueError, TypeError):
                                        ws_dash.write_string(current_table_row, 7, str(cell_value), fmt)
                                elif col_name == "Type":
                                    # Type naar kolom I (8, was 7)
                                    ws_dash.write_string(current_table_row, 8, str(cell_value), fmt)
                                elif col_name == "Type (Sheet)":
                                    # Type (Sheet) naar kolom J (9, was 8)
                                    ws_dash.write_string(current_table_row, 9, str(cell_value), fmt)
                                elif col_name == "Foutcode":
                                    # Foutcode naar kolom K (10, was 9)
                                    try:
                                        if cell_value != "":
                                            num_val = int(float(str(cell_value)))  # Handle float strings
                                            ws_dash.write_number(current_table_row, 10, num_val, fmt)
                                        else:
                                            ws_dash.write_string(current_table_row, 10, "", fmt)
                                    except (ValueError, TypeError):
                                        ws_dash.write_string(current_table_row, 10, str(cell_value), fmt)
                            except Exception as e:
                                # Fallback: write as string if any formatting fails
                                logging.warning(f"Error formatting cell {col_name} at row {current_table_row}: {e}")
                                ws_dash.write_string(current_table_row, 7 if col_name == "Aantal" else 8 if col_name == "Type" else 9 if col_name == "Type (Sheet)" else 10, str(cell_value), fmt_error_table_cell)
                                
                    table_end_row = table_header_row + len(df_foutcodes_top)
                else:
                    # 'code' kolom mist - schrijf over E-G (merged)
                    ws_dash.merge_range(
                        f"E{table_subheader_row + 2}:G{table_subheader_row + 2}",  # Na subheader, E-G merged (was D-F)
                        "'code' kolom mist in validatieresultaten.",
                        fmt_error_table_cell,
                    )
                    table_end_row = table_subheader_row + 1
            else:
                # Geen fouten - schrijf DOORLOPEND over E-K (hele breedte) 
                # GEBRUIK EEN ANDERE RIJ dan de error data om conflicten te voorkomen
                geen_fouten_row = table_subheader_row + 2  # Dit is rij 10 (Excel rij 11)
                ws_dash.merge_range(
                    f"E{geen_fouten_row + 1}:K{geen_fouten_row + 1}",  # E11:K11 om conflicten te vermijden
                    "Geen fouten gevonden",
                    fmt_error_table_cell
                )
                table_end_row = geen_fouten_row


            # DYNAMISCHE POSITIE voor Aandachtspunten: bereken based op einde van Foutmeldingen data
            # Minimaal 2 regels ruimte tussen Foutmeldingen en Aandachtspunten
            if validation_results:
                # Bereken het einde van de Foutmeldingen tabel
                foutmeldingen_end_row = table_header_row + len(df_foutcodes_top) - 1  # -1 omdat we bij 0 starten
                attention_start_row = foutmeldingen_end_row + 2  # 1 lege regel + 1 voor de header
            else:
                # Als er geen fouten zijn, start vanaf de "Geen fouten gevonden" regel + 2
                foutmeldingen_end_row = table_subheader_row + 3  # "Geen fouten gevonden" is nu op rij 11
                attention_start_row = foutmeldingen_end_row + 2

            # Schrijf hoofdheader voor Aandachtspunten (E-K)
            ws_dash.merge_range(
                f"E{attention_start_row+1}:K{attention_start_row+1}",  # E-K voor Aandachtspunten (was D-J)
                "Aandachtspunten",
                fmt_header_red,  # Behoud donkerrode hoofdheader
            )
            ws_dash.set_row(attention_start_row, 18)  # Hoofdheader hoogte
            
            # Voeg GRIJZE subheaders toe - melding over E-J, foutcode alleen in K (was D-I, J)
            attention_subheader_row = attention_start_row + 1
            ws_dash.merge_range(
                f"E{attention_subheader_row+1}:J{attention_subheader_row+1}",  # E-J voor Melding (was D-I, 6 kolommen)
                "Melding",
                fmt_subheader_grey  # Gebruik grijze subheader zoals bij foutmeldingen
            )
            ws_dash.write(attention_subheader_row, 10, "Foutcode", fmt_subheader_grey)  # K voor Foutcode (was J)
            ws_dash.set_row(attention_subheader_row, 18)  # Normale rijhoogte
            
            attention_data_start_row = attention_subheader_row + 1  # Start van data

            # Format met RODE rand, font size (aanpassen?), wrap, etc.
            fmt_attention_item = workbook.add_format({
                "font_size": 12,
                "bg_color": "#F2DCDB",  # Identieke kleur als Foutmeldingen data (was #F4CCCC)
                "font_color": "#000000",  # Zwarte tekst
                "border": 1,
                "border_color": "#000000",  # Zwarte rand
                "text_wrap": True,
                "align": "left",
                "valign": "top",
                "indent": 1
            })

            # Controleer of er aandachtspunten zijn
            current_attention_row = attention_data_start_row
            if red_flag_messages:
                # Loop door elke individuele melding (nu dict met message + code)
                for item in red_flag_messages:
                    try:
                        if isinstance(item, dict):
                            msg = item.get("message", str(item))
                            code = item.get("code", "")
                        else:
                            # Backward compatibility - als het nog een string is
                            msg = str(item)
                            code = ""
                        
                        # Clean up message and code
                        if pd.isna(msg) or msg is None:
                            msg = ""
                        if pd.isna(code) or code is None:
                            code = ""
                            
                        # Vaste rijhoogte voor alle Aandachtspunten regels
                        ws_dash.set_row(current_attention_row, 18)  # Increased from 16 for better readability

                        # Schrijf bericht over kolommen E-J (laat K vrij voor foutcode, was D-I)
                        ws_dash.merge_range(
                            f"E{current_attention_row+1}:J{current_attention_row+1}",
                            str(msg),
                            fmt_attention_item,
                        )
                        
                        # Format voor foutcode kolom - rechts uitgelijnd en niet bold
                        fmt_code_item = workbook.add_format(
                            {
                                "font_size": 12,
                                "bg_color": "#F2DCDB",  # Licht rood (zelfde als message)
                                "border": 1,
                                "align": "right",  # Rechts uitlijnen voor codes
                                "valign": "vcenter",
                                "bold": False,  # Niet bold
                            }
                        )
                        
                        # Schrijf foutcode in kolom K
                        code_value = str(code) if code else "N/A"
                        ws_dash.write_string(
                            current_attention_row, 10,  # Kolom K (10, was 9)
                            code_value,
                            fmt_code_item
                        )

                        current_attention_row += 1  # Ga naar de volgende rij
                        
                    except Exception as e:
                        logging.warning(f"Error formatting attention point: {e}")
                        # Write fallback message
                        ws_dash.set_row(current_attention_row, 18)
                        ws_dash.merge_range(
                            f"E{current_attention_row+1}:J{current_attention_row+1}",
                            "Error formatting attention point",
                            fmt_attention_item,
                        )
                        ws_dash.write_string(current_attention_row, 10, "ERROR", fmt_attention_item)
                        current_attention_row += 1
            else:
                # Geen meldingen: schrijf over kolom E-J (consistent met de rest)
                ws_dash.set_row(current_attention_row, 18)  # Vaste hoogte 18pt
                ws_dash.merge_range(
                    f"E{current_attention_row+1}:K{current_attention_row+1}",  # E-K doorlopend (hele breedte)
                    "Geen specifieke aandachtspunten gevonden.",
                    fmt_attention_item,
                )
                current_attention_row += 1

            # Onthoud de laatst gebruikte rij-index (0-based)
            attention_end_row = current_attention_row - 1
            # --- Einde Aandachtspunten ---


            # ============================
            # Grafieken Data Voorbereiding
            # ============================
            
            chart_data_start_row = 500
            ws_dash.write(
                chart_data_start_row,
                0,
                "Chart Data Area",
                workbook.add_format({"bold": True}),
            ) 
            
            # 1. Stacked Bar Data
            bar_chart_row = chart_data_start_row + 2
            bar_headers = ["Veld", "Juist", "Foutief", "Leeg", "Kolom Missing"]
            ws_dash.write_row(bar_chart_row, 0, bar_headers)
            bar_chart_data = []
            # CRITICAL: Use processed_rows for chart calculations, not total_rows!
            chart_rows = len(df)  # Use actual processed data length
            for i, f in enumerate(ghx_mandatory_fields):
                row_num = bar_chart_row + 1 + i
                if f not in df.columns:
                    # Voor lege templates, toon als "leeg" (geel) in plaats van "missing" (zwart)
                    if chart_rows == 0:
                        correct, error, empty, missing = 0, 0, 1, 0  # Toon minimaal 1 voor zichtbaarheid
                    else:
                        correct, error, empty, missing = 0, 0, 0, chart_rows
                else:
                    filled = filled_counts.get(f, 0)
                    errors = corrected_errors.get(f, 0)
                    correct = max(0, filled - errors)
                    error = errors
                    empty = chart_rows - filled  # Use processed rows for chart
                    missing = 0
                    
                    # Voor lege templates met kolommen aanwezig, toon als "leeg"
                    if chart_rows == 0:
                        empty = 1  # Toon minimaal 1 voor zichtbaarheid
                ws_dash.write(row_num, 0, f)
                ws_dash.write(row_num, 1, correct)
                ws_dash.write(row_num, 2, error)
                ws_dash.write(row_num, 3, empty)
                ws_dash.write(row_num, 4, missing)
                bar_chart_data.append([f, correct, error, empty, missing])
            last_bar_data_row = bar_chart_row + len(ghx_mandatory_fields)

            # 2. Donut Mandatory Data
            donut_mand_row = last_bar_data_row + 2
            missing_mandatory_count = M_missing * total_rows
            donut_mand_data = [
                ["Status", "Aantal"],
                ["Juist ingevuld", totaal_juist],
                ["Foutief ingevuld", total_errors_in_present],
                ["Leeg", empty_in_present],
                ["Kolom niet aanwezig", missing_mandatory_count],
            ]
            ws_dash.write_row(donut_mand_row, 0, donut_mand_data[0])
            ws_dash.write_row(donut_mand_row + 1, 0, donut_mand_data[1])
            ws_dash.write_row(donut_mand_row + 2, 0, donut_mand_data[2])
            ws_dash.write_row(donut_mand_row + 3, 0, donut_mand_data[3])
            ws_dash.write_row(donut_mand_row + 4, 0, donut_mand_data[4])
            total_donut_mand = sum(item[1] for item in donut_mand_data[1:])

            # 3. Donut All Data
            donut_all_row = donut_mand_row + 6
            total_all_fields_in_config = len(config.get("fields", {}))
            total_all_fields_possible = total_rows * total_all_fields_in_config
            total_all_filled = total_filled_in_present + total_filled_non_mand
            total_all_errors = total_errors_in_present + total_errors_non_mand
            total_all_correct = total_all_filled - total_all_errors
            total_all_empty_or_missing = total_all_fields_possible - total_all_filled

            donut_all_data = [
                ["Status", "Aantal"],
                ["Correct ingevuld", max(0, total_all_correct)],
                ["Foutief ingevuld", total_all_errors],
                ["Leeg / Kolom niet aanwezig", max(0, total_all_empty_or_missing)],
            ]
            ws_dash.write_row(donut_all_row, 0, donut_all_data[0])
            ws_dash.write_row(donut_all_row + 1, 0, donut_all_data[1])
            ws_dash.write_row(donut_all_row + 2, 0, donut_all_data[2])
            ws_dash.write_row(donut_all_row + 3, 0, donut_all_data[3])
            total_donut_all = sum(item[1] for item in donut_all_data[1:])

            # --- VERBETERDE Grafieken Positionering ---
            # Scheid linker en rechter kolom voor betere ruimtebenutting
            left_table_end_rows = [
                template_table_end_row,  # Template tabel (indien aanwezig)
                stats_end_row,      # Statistieken tabel (linksboven)
                missing_end_row,    # Missing data tabel (links midden)  
                actions_end_row,    # Actions tabel (links onder)
            ]
            right_table_end_rows = [
                table_end_row,      # Foutmeldingen tabel (rechts boven)
                attention_end_row   # Aandachtspunten tabel (rechts onder)
            ]
            
            left_max_row = max(left_table_end_rows)
            right_max_row = max(right_table_end_rows)
            
            # Chart positionering volgens gebruikerswens:
            # "2 regels onder belangrijkste actiepunten, tenzij aandachtspunten lager is"
            if attention_end_row > actions_end_row:
                # Aandachtspunten tabel eindigt lager, dus gebruik die als basis
                chart_start_row = attention_end_row + 3  # 3 voor 2 lege regels
            else:
                # Belangrijkste actiepunten eindigt lager of gelijk, gebruik die als basis
                chart_start_row = actions_end_row + 3  # 3 voor 2 lege regels
            
            # Chart positionering logica toegepast

            # Grafiek 1: Stacked Bar Verplichte Velden (MET GECORRIGEERDE LEGENDA)
            stacked_chart = workbook.add_chart({"type": "column", "subtype": "stacked"})
            legend_labels = {
                1: "Juist ingevuld",
                2: "Foutief",
                3: "Leeg",
                4: "Kolom niet aanwezig",
            }
            colors = {1: "#70AD47", 2: "#FF0000", 3: "#FFC000", 4: "#000000"}
            for i in range(1, 5):
                stacked_chart.add_series(
                    {
                        "name": legend_labels[i],  # <-- Correcte naam direct hier
                        "categories": [
                            "1. Dashboard",
                            bar_chart_row + 1,
                            0,
                            last_bar_data_row,
                            0,
                        ],
                        "values": [
                            "1. Dashboard",
                            bar_chart_row + 1,
                            i,
                            last_bar_data_row,
                            i,
                        ],
                        "fill": {"color": colors[i]},
                    }
                )
            stacked_chart.set_title({"name": "Verplichte Kolommen Overzicht"})
            stacked_chart.set_x_axis(
                {"name": "Verplichte Velden", "num_font": {"rotation": -45, "size": 11}}
            )
            stacked_chart.set_y_axis(
                {"name": "Aantal", "major_gridlines": {"visible": False}}
            )
            stacked_chart.set_legend({"position": "bottom", "font": {"size": 11}})
            # Breedte geoptimaliseerd voor A-J kolommen (totaal ~280px * 7 = ~2000px voor goede proportie)  
            stacked_chart.set_size({"width": 2000, "height": 500})  # Optimaal voor A-J breedte
            # Voeg een subtiele rand toe rond de chart
            stacked_chart.set_chartarea({
                'border': {'color': '#D32F2F', 'width': 2},  # Rode rand, 2px
                'fill':   {'color': '#FFFFFF'}  # Witte achtergrond
            })
            ws_dash.insert_chart(f"B{chart_start_row + 1}", stacked_chart)  # Kolom B (na gutter A)

            # Donut charts verwijderd - alleen tabellen blijven bestaan voor overzicht
            # Data blijft beschikbaar in donut_mand_row en donut_all_row tabellen
            
            # --- EINDE DASHBOARD: Nu rijhoogtes forceren voor content rijen (vanaf rij 11) ---
            # Eerste 50 rijen van content (rij 11-60) krijgen hoogte 18
            for row in range(10, 60):  # Rijen 11-60 (0-based: 10-59) - content area
                ws_dash.set_row(row, 18)
            
            # Header area (rijen 1-10) blijft standaard hoogte voor logo ruimte
            for row in range(0, 10):  # Rijen 1-10 (0-based: 0-9) - header area
                ws_dash.set_row(row, None)  # Standaard rijhoogte
            
            pass

            # ==================================================================
            # START CODE VOOR SHEET 2: INLEIDING
            # ==================================================================
            ws_inleiding = workbook.add_worksheet("2. Inleiding")
            suppress_excel_errors(ws_inleiding)
            writer.sheets["2. Inleiding"] = ws_inleiding
            ws_inleiding.hide_gridlines(2)  # Gridlines verbergen
            ws_inleiding.set_column("A:A", 125)  # Kolombreedte aangepast naar 125

            # --- Definieer Formats (ALLE formats hier, font_size 12, indent) ---
            fmt_title = workbook.add_format(
                {  # <<<< DEFINITIE STAAT NU HIER BOVENAAN
                    "font_name": "Arial",
                    "font_size": 20,
                    "bold": True,
                    "align": "left",  # Changed from "center"
                    "valign": "vcenter",
                    "bg_color": "#16365C",  # Gewijzigd naar blauw
                    "font_color": "white",
                    "border": 1,
                }
            )
            fmt_score = workbook.add_format(
                {
                    "font_name": "Arial",
                    "font_size": 12,
                    "text_wrap": True,  # Size 12
                    "align": "left",
                    "valign": "top",
                    "indent": 1,  # Indent 1
                    "bg_color": "#E6F2FF",
                    "border": 1,
                    "border_color": "#CCCCCC",
                }
            )
            fmt_filename = workbook.add_format(
                {"font_size": 12, "indent": 2, "bold": True}
            )  # Size 12, Indent 2, Bold toegevoegd
            # fmt_standard nu size 12 MET INDENT
            fmt_standard = workbook.add_format(
                {
                    "font_size": 12,
                    "text_wrap": True,
                    "align": "left",
                    "valign": "top",
                    "indent": 4,
                }
            )  # << Indent verhoogd naar 4
            fmt_section_header = workbook.add_format(
                {"font_size": 14, "indent": 2, "bold": True}
            )
            # Format for URL (based on standard, maar blauw/onderstreept + indent)
            fmt_url = workbook.add_format(
                {"font_size": 12, "font_color": "blue", "underline": 1, "indent": 4}
            )

            # --- Schrijf Inhoud stap voor stap ---
            current_row_intro = 0  # Start bovenaan

            # Titel (Excel rij 1-3)
            # Gebruik NU de correct gedefinieerde fmt_title9
            ws_inleiding.merge_range(
                f"A{current_row_intro+1}:B{current_row_intro+1}",
                "  GHX TEMPLATE VALIDATIE RAPPORT",
                fmt_title,
            )  # Merge A1:B1
            ws_inleiding.set_row(current_row_intro, 40)  # Stel hoogte in voor titelrij
            current_row_intro = 1  # Start volgende blok op rij 4

            # Extra witregel VOOR het scoreblok (om het op rij 5 te laten beginnen)
            current_row_intro += 1

            # <<<<<< DE TWEEDE (FOUTE) DEFINITIE VAN fmt_title IS HIER VERWIJDERD >>>>>>

            # === GEBRUIK NIEUWE SCORE VOOR SHEET 2 DISPLAY ===
            # Gebruik dezelfde score als filename en Sheet 1 (consistent!)
            score_int_uitleg = score_result['final_score']
            score_grade_uitleg = score_result['grade']
            
            # Bepaal kleuren voor Sheet 2 score display
            if score_grade_uitleg in ["B", "A", "A+"]:
                score_text_color = "#4f6229"  # Groen
                score_bg_color = "#E8F4E8"    # Licht groen
                score_border_color = "#4f6229"  # Groen
            elif score_grade_uitleg in ["C", "D"]:
                score_text_color = "#FF5E1A"  # Oranje
                score_bg_color = "#FFF4E6"    # Licht oranje
                score_border_color = "#FF5E1A"  # Oranje
            else:  # E, F
                score_text_color = "#c00000"  # Rood
                score_bg_color = "#FFE6E6"    # Licht rood
                score_border_color = "#c00000"  # Rood
            
            # Maak aparte formats voor mooiere opmaak
            fmt_score_title = workbook.add_format({
                'bold': True,
                'font_size': 14,
                'font_color': score_text_color,
                'bg_color': score_bg_color,
                'border': 1,
                'border_color': score_border_color,
                'align': 'left',
                'valign': 'vcenter',
                'text_wrap': True,
                'indent': 1
            })
            
            fmt_score_body = workbook.add_format({
                'font_size': 12,
                'font_color': '#000000',
                'bg_color': score_bg_color,  # Gebruik dezelfde achtergrondkleur als de titel
                'border': 1,
                'border_color': score_border_color,  # Gebruik dezelfde randkleur als de titel
                'align': 'left',
                'valign': 'top',
                'text_wrap': True,
                'indent': 1
            })
            
            # Titel apart (bold en groot)
            score_title = f"KWALITEITSSCORE: {score_int_uitleg}/100 - CIJFER {score_grade_uitleg}"
            
            # Gedetailleerde score berekening uitleg
            M_percentage = score_result['M_percentage']
            J_percentage = score_result['J_percentage']
            core_score = score_result['core_score']
            uom_penalties = score_result['uom_penalties']
            template_penalty = score_result['template_penalty']
            
            score_body_tekst = f"""BEREKENING:
• Volledigheid (M): {M_percentage}% ({M_found}/{len(ghx_mandatory_fields)} verplichte velden ingevuld)
• Juistheid (J): {J_percentage}% (correcte data van ingevulde velden)
• Core score: {M_percentage}% × {J_percentage}% = {core_score}%
• Template penalty: {template_penalty} ({template_type} template)
• UOM penalties: {uom_penalties} (foutcodes in UOM kolommen)
• Eindscore: {core_score} + {template_penalty} + {uom_penalties} = {score_int_uitleg}

Kwaliteitscore Uitleg:
• A+ (≥95): Uitstekend - gereed voor Gatekeeper, minimale verbeteringen nodig
• A (90-94): Zeer goed - kleine verbeteringen mogelijk  
• B (80-89): Goed - enkele verbeterpunten aanwezig
• C (70-79): Voldoende - aandacht vereist voor verbeteringen
• D (60-69): Onvoldoende - significante verbeteringen nodig
• E (50-59): Slecht - grote problemen aanwezig
• F (<50): Zeer slecht - uitgebreide herziening vereist"""
            # Titel (bold en groot) - 2 rijen
            ws_inleiding.merge_range(
                f"A{current_row_intro+1}:B{current_row_intro + 2}",
                score_title,
                fmt_score_title,
            )
            current_row_intro += 3  # 2 rijen titel + 1 witregel
            
            # Body tekst (extra ruimte voor volledige uitleg tot regel 20+)
            ws_inleiding.merge_range(
                f"A{current_row_intro+1}:B{current_row_intro + 18}",
                score_body_tekst,
                fmt_score_body,
            )
            current_row_intro += 18

            # Witregel
            current_row_intro += 1

            # Bestandsnaam wordt nu getoond in Sheet 1 Template-tabel
            # Geen bestandsnaam meer in Sheet 2
            
            # Witregel (behouden voor spacing)
            current_row_intro += 1

            # Beknopte introductie - verwijst naar Sheet 1 voor details
            ws_inleiding.write(
                f"A{current_row_intro+1}", "Geachte leverancier,", fmt_standard
            )
            current_row_intro += 1
            ws_inleiding.write(
                f"A{current_row_intro+1}",
                "Hartelijk dank voor de aangeleverde GHX-prijslijsttemplate. In dit rapport vindt u de validatieresultaten en interpretatie van uw gegevens.",
                fmt_standard,
            )
            current_row_intro += 1

            # Witregel voor ademruimte
            current_row_intro += 1

            # Rapport Onderdelen - dynamisch gebaseerd op template type
            ws_inleiding.write(
                f"A{current_row_intro+1}",
                "Dit rapport bestaat uit de volgende onderdelen:",
                fmt_section_header,
            )
            current_row_intro += 1
            
            # Basis onderdelen (altijd aanwezig)
            rapport_onderdelen = [
                "1. Dashboard\n   Belangrijkste statistieken en aandachtspunten in één oogopslag.",
                "2. Inleiding\n   Score-interpretatie en gebruiksinstructies.",
                "3. Verplichte Fouten\n   Gedetailleerde lijst van fouten in verplichte velden.",
                "4. Verplichte %\n   Statistieken over volledigheid verplichte velden.",
                "5. Optionele Fouten\n   Overzicht van fouten in optionele velden.",
                "6. Optionele %\n   Statistieken over volledigheid optionele velden.",
            ]
            
            # Sheet 7 altijd toevoegen (Dataset Validatie)
            rapport_onderdelen.append("7. Dataset Validatie\n   Visueel overzicht dataset met kleurcodering.")
            
            # Conditioneel: voeg Sheet 8 toe voor oude/leverancier templates  
            if template_type in ["O", "AT"]:
                rapport_onderdelen.append("8. Kolom Mapping\n   Mapping tussen GHX-standaard en uw kolomnamen.")
            
            for onderdeel in rapport_onderdelen:
                ws_inleiding.write(
                    f"A{current_row_intro+1}", onderdeel, fmt_standard
                )
                current_row_intro += 1

            # Witregel
            current_row_intro += 1
            
            # Gebruiksinstructies toevoegen
            ws_inleiding.write(
                f"A{current_row_intro+1}",
                "HOE DIT RAPPORT GEBRUIKEN:",
                fmt_section_header,
            )
            current_row_intro += 1
            
            gebruiks_instructies = [
                "1. Bekijk eerst Sheet 1 voor het overzicht en volledige scores",
                "2. Controleer Sheet 3-5 voor specifieke foutmeldingen",  
                "3. Gebruik de aandachtspunten om prioriteiten te stellen"
            ]
            
            for instructie in gebruiks_instructies:
                ws_inleiding.write(
                    f"A{current_row_intro+1}", instructie, fmt_standard
                )
                current_row_intro += 1

            # Witregel
            current_row_intro += 1
            # Nieuwe template link
            ws_inleiding.write(
                f"A{current_row_intro+1}",
                "We vragen u om altijd gebruik te maken van de nieuwste versie van de GHX-template, welke te downloaden is via de volgende link:",
                fmt_standard,
            )
            current_row_intro += 1
            ws_inleiding.write_url(
                f"A{current_row_intro+1}",
                "https://ghxnl.ghxeurope.com/synqeps/webroot/upload/GHXstandaardTemplate2.xlsx",
                fmt_url,
                string="https://ghxnl.ghxeurope.com/synqeps/webroot/upload/GHXstandaardTemplate2.xlsx",
            )
            current_row_intro += 1

            # Witregel
            current_row_intro += 1

            # Beknopte afsluiting
            ws_inleiding.write(
                f"A{current_row_intro+1}",
                "Wij verzoeken u vriendelijk eventuele fouten te corrigeren, ontbrekende informatie aan te vullen, en volledig lege verplichte kolommen te voorzien van data, zodat de prijslijst succesvol kan worden verwerkt.",
                fmt_standard,
            )
            current_row_intro += 1
            current_row_intro += 1  # Witregel
            ws_inleiding.write(
                f"A{current_row_intro+1}", "Met vriendelijke groet,", fmt_standard
            )
            current_row_intro += 1
            current_row_intro += 1  # Witregel
            ws_inleiding.write(
                f"A{current_row_intro+1}", "GHX", fmt_standard
            )
            current_row_intro += 1
            # ==================================================================
            # EINDE CODE VOOR SHEET 2: INLEIDING
            # ==================================================================

            # ==================================================================
            # START CODE VOOR SHEET 3: VERPLICHTE FOUTEN
            # ==================================================================
            ws_mand_err = workbook.add_worksheet("3. Verplichte Fouten")
            suppress_excel_errors(ws_mand_err)
            writer.sheets["3. Verplichte Fouten"] = ws_mand_err
            required_cols_err = [
                "Rij",
                "GHX Kolom",
                "Supplier Kolom",
                "Veldwaarde",
                "Foutmelding",
                "code",
            ]
            if not df_errors_mand.empty and all(
                c in df_errors_mand.columns for c in required_cols_err
            ):
                df_errors_mand_sheet = df_errors_mand[required_cols_err].copy()
                df_errors_mand_sheet = df_errors_mand_sheet.rename(
                    columns={"code": "Foutcode"}
                )
                
                # Voeg Type kolom toe
                df_errors_mand_sheet["Type"] = df_errors_mand_sheet.apply(get_error_category_with_type, axis=1)
                df_errors_mand_sheet = df_errors_mand_sheet.sort_values(
                    by=["Rij", "GHX Kolom"]
                )
                df_errors_mand_sheet = df_errors_mand_sheet.fillna(
                    ""
                )  # Vul NaN etc. met lege string
                
                # Schoon de "Supplier Kolom" headers op (alleen Nederlandse namen)
                if "Supplier Kolom" in df_errors_mand_sheet.columns:
                    df_errors_mand_sheet["Supplier Kolom"] = df_errors_mand_sheet["Supplier Kolom"].apply(
                        clean_header_for_display
                    )

                # Limiet toepassen
                limit_message_format = workbook.add_format(
                    {"bold": True, "color": "red", "font_size": 10}
                )
                # Gebruik een aparte naam voor de DataFrame die daadwerkelijk naar Excel gaat (ivm slicing)
                df_errors_mand_sheet_display = df_errors_mand_sheet
                if len(df_errors_mand_sheet) > ERROR_LIMIT:
                    ws_mand_err.write(
                        0,
                        0,
                        f"LET OP: Weergave beperkt tot de eerste {ERROR_LIMIT} fouten.",
                        limit_message_format,
                    )
                    # Maak een slice en BELANGRIJK: een .copy() om SettingWithCopyWarning te voorkomen
                    df_errors_mand_sheet_display = df_errors_mand_sheet.iloc[
                        ERROR_START:ERROR_END
                    ].copy()
                    startrow_err = 1  # Data start op rij 2 (index 1) omdat rij 1 het limiet-bericht bevat
                else:
                    startrow_err = 0  # Data start op rij 1 (index 0)

                # Schrijf de data naar Excel (BELANGRIJK: ZONDER header nu)
                df_errors_mand_sheet_display.to_excel(
                    writer,
                    sheet_name="3. Verplichte Fouten",
                    startrow=startrow_err + 1,
                    index=False,
                    header=False,
                )

                # Kolombreedtes instellen
                ws_mand_err.set_column(0, 0, 8)  # Rij
                ws_mand_err.set_column(1, 1, 30)  # GHX Kolom
                ws_mand_err.set_column(
                    2, 2, 30
                )  # Supplier Kolom << Kolom die moet wrappen
                ws_mand_err.set_column(3, 3, 45)  # Veldwaarde
                ws_mand_err.set_column(4, 4, 150)  # Foutmelding
                ws_mand_err.set_column(5, 5, 10)  # Foutcode
                ws_mand_err.set_column(6, 6, 12)  # Type

                # Bepaal tabel dimensies gebaseerd op de display DataFrame
                (max_row_disp, max_col_disp) = df_errors_mand_sheet_display.shape
                # Excel rij-index (0-based) van de LAATSTE rij met data
                last_data_row_index = startrow_err + max_row_disp

                # Definieer headers voor tabel stijl
                header_list = [
                    {"header": col} for col in df_errors_mand_sheet_display.columns
                ]

                # Voeg tabel toe (past basis stijl toe)
                # Range is van de header rij (startrow_err) t/m de laatste data rij (last_data_row_index)
                ws_mand_err.add_table(
                    startrow_err,
                    0,
                    last_data_row_index,
                    max_col_disp - 1,
                    {
                        "columns": header_list,
                        "style": "Table Style Medium 10",
                        "header_row": True,  # Laat stijl de header opmaken op rij startrow_err
                    },
                )

                # --- Pas text wrap toe op Kolom C ("Supplier Kolom") NA HET MAKEN VAN DE TABEL ---
                # Definieer een format dat WEL text wrap en top align doet (om overflow te voorkomen)
                # fmt_col_c_wrap_override = workbook.add_format({'valign': 'top', 'text_wrap': True})
                fmt_col_c_wrap_override = workbook.add_format(
                    {"valign": "top"}
                )  # Zet text_wrap weer AAN
                # Loop door de data rijen (excel rij indexen: startrow_err + 1 t/m last_data_row_index)
                # Kolom C heeft index 2
                for row_idx_in_df in range(
                    max_row_disp
                ):  # Loopt van 0 tot aantal data rijen - 1
                    # Bepaal het werkelijke Excel rijnummer (0-based index)
                    excel_row_index = startrow_err + 1 + row_idx_in_df

                    # Kolom C (index 2): Overschrijf de cel met dezelfde waarde maar MET het wrap format
                    # Dit overschrijft de tabel stijl specifiek voor deze cellen
                    value_c = df_errors_mand_sheet_display.iat[row_idx_in_df, 2]
                    ws_mand_err.write(excel_row_index, 2, value_c, fmt_col_c_wrap_override)

                    # Kolom D (index 3): Schrijf expliciet, zet spatie indien leeg
                    fmt_col_d_basic = workbook.add_format({'valign': 'top'}) # Basic format for D
                    value_d = df_errors_mand_sheet_display.iat[row_idx_in_df, 3]
                    if value_d == '': # Check if value is empty string (due to earlier fillna(''))
                        ws_mand_err.write_string(excel_row_index, 3, ' ', fmt_col_d_basic) # Write a space if empty
                    else:
                        ws_mand_err.write(excel_row_index, 3, value_d, fmt_col_d_basic) # Write original value if not empty

                # --- Stel vaste rijhoogte in om auto-resize door wrap te voorkomen ---
                default_row_height = 15
                # Loop door de Excel rij-indexen van de datarijen
                for row_num in range(startrow_err + 1, last_data_row_index + 1):
                    ws_mand_err.set_row(row_num, default_row_height)
                # --- Einde Vaste Rijhoogte --- 
            else:
                # Schrijf 'geen fouten' bericht
                fmt_default_table = workbook.add_format(
                    {"font_size": 10}
                )  # Basic format
                ws_mand_err.write(
                    0, 0, "Geen fouten gevonden in verplichte velden.", fmt_default_table
                )
                ws_mand_err.set_column("A:A", 50)
            # ==================================================================
            # EINDE CODE VOOR SHEET 3: VERPLICHTE FOUTEN
            # ==================================================================

            # ==================================================================
            # START CODE VOOR SHEET 4: VERPLICHTE %
            # ==================================================================
            ws_mand_perc = workbook.add_worksheet("4. Verplichte %")
            suppress_excel_errors(ws_mand_perc)
            writer.sheets["4. Verplichte %"] = ws_mand_perc
            # Bereken df_percentages hier opnieuw of gebruik een doorgegeven versie
            # Voor nu, herbruik berekening van eerder in deze functie
            field_stats_perc = []
            for f in ghx_mandatory_fields:
                aanwezig = "Ja" if f in df.columns else "Nee"
                filled = filled_counts.get(f, 0)
                field_filled_percentage = (
                    (filled / total_rows * 100) if total_rows > 0 else 0
                )
                field_errors = corrected_errors.get(f, 0)
                percentage_fout_field = (
                    (field_errors / filled * 100) if filled > 0 else 0
                )
                field_juist = max(0, filled - field_errors)
                field_stats_perc.append(
                    {
                        "GHX Header": f,
                        "Supplier Header": clean_header(
                            original_column_mapping.get(f, "")
                        ),
                        "Aanwezig": aanwezig,
                        "FilledPercentage": field_filled_percentage
                        / 100,  # Deel door 100 voor format
                        "PercentageFout": percentage_fout_field
                        / 100,  # Deel door 100 voor format
                        "Aantal juist ingevuld": field_juist,
                    }
                )
            df_percentages_sheet = pd.DataFrame(field_stats_perc)
            df_percentages_sheet = df_percentages_sheet[
                [
                    "GHX Header",
                    "Supplier Header",
                    "Aanwezig",
                    "FilledPercentage",
                    "PercentageFout",
                    "Aantal juist ingevuld",
                ]
            ]

            df_percentages_sheet.to_excel(
                writer, sheet_name="4. Verplichte %", index=False
            )
            # Definieer percentage opmaak
            percentage_format = writer.book.add_format({'num_format': '0.00%'})

            ws_mand_perc.set_column(0, 0, 30)
            ws_mand_perc.set_column(1, 1, 30)
            ws_mand_perc.set_column(2, 2, 12)
            ws_mand_perc.set_column(3, 3, 18, percentage_format)  # Filled %
            ws_mand_perc.set_column(4, 4, 18, percentage_format)  # Fout %
            ws_mand_perc.set_column(5, 5, 20)  # Aantal Juist
            # Pas format toe op percentage kolommen
            # (Let op: De set_column hieronder leek overbodig/dubbel in de originele code, ik laat hem weg
            # tenzij er problemen ontstaan)
            # ws_mand_perc.set_column(3, 4, 18)  # fmt_perc_table verwijderd?
            (max_row_mp, max_col_mp) = df_percentages_sheet.shape
            # Header format
            for c_idx, value in enumerate(df_percentages_sheet.columns.values):
                ws_mand_perc.write(0, c_idx, value, fmt_header_orange)
            # Tabel stijl
            ws_mand_perc.add_table(
                0,
                0,
                max_row_mp,
                max_col_mp - 1,
                {
                    "columns": [{"header": col} for col in df_percentages_sheet.columns],
                    "header_row": True,  # Gebruik de geschreven header
                    "style": "Table Style Medium 1",
                },
            )
            # ==================================================================
            # EINDE CODE VOOR SHEET 4: VERPLICHTE %
            # ==================================================================

            # ==================================================================
            # START CODE VOOR SHEET 5: OPTIONELE FOUTEN
            # ==================================================================
            ws_opt_err = workbook.add_worksheet("5. Optionele Fouten")
            suppress_excel_errors(ws_opt_err)
            writer.sheets["5. Optionele Fouten"] = ws_opt_err
            if not df_errors_non_mand.empty and all(
                c in df_errors_non_mand.columns for c in required_cols_err
            ):
                df_errors_non_mand_sheet = df_errors_non_mand[required_cols_err].copy()
                df_errors_non_mand_sheet = df_errors_non_mand_sheet.rename(
                    columns={"code": "Foutcode"}
                )
                
                # Voeg Type kolom toe (speciale versie voor optionele fouten)
                df_errors_non_mand_sheet["Type"] = df_errors_non_mand_sheet.apply(get_error_category_optional, axis=1)
                df_errors_non_mand_sheet = df_errors_non_mand_sheet.sort_values(
                    by=["Rij", "GHX Kolom"]
                )
                df_errors_non_mand_sheet = df_errors_non_mand_sheet.fillna("")
                
                # Schoon de "Supplier Kolom" headers op (alleen Nederlandse namen)
                if "Supplier Kolom" in df_errors_non_mand_sheet.columns:
                    df_errors_non_mand_sheet["Supplier Kolom"] = df_errors_non_mand_sheet["Supplier Kolom"].apply(
                        clean_header_for_display
                    )
                # Limiet
                if len(df_errors_non_mand_sheet) > ERROR_LIMIT:
                    ws_opt_err.write(
                        0,
                        0,
                        f"LET OP: Weergave beperkt tot de eerste {ERROR_LIMIT} fouten.",
                        workbook.add_format({"bold": True, "color": "red"}),
                    )
                    df_errors_non_mand_sheet = df_errors_non_mand_sheet.iloc[
                        ERROR_START:ERROR_END
                    ]
                    startrow_opt_err = 1
                else:
                    startrow_opt_err = 0
                # Schrijf
                df_errors_non_mand_sheet.to_excel(
                    writer,
                    sheet_name="5. Optionele Fouten",
                    startrow=startrow_opt_err,
                    index=False,
                )
                # Opmaak
                ws_opt_err.set_column(0, 0, 8)   # Rij
                ws_opt_err.set_column(1, 1, 30)  # GHX Kolom
                ws_opt_err.set_column(2, 2, 30)  # Supplier Kolom
                ws_opt_err.set_column(3, 3, 45)  # Veldwaarde
                ws_opt_err.set_column(4, 4, 150)  # Foutmelding
                ws_opt_err.set_column(5, 5, 10)  # Foutcode
                ws_opt_err.set_column(6, 6, 12)  # Type
                (max_row_oe, max_col_oe) = df_errors_non_mand_sheet.shape
                ws_opt_err.add_table(
                    startrow_opt_err,
                    0,
                    startrow_opt_err + max_row_oe,
                    max_col_oe - 1,
                    {
                        "columns": [{"header": col} for col in df_errors_non_mand_sheet.columns],
                        "style": "Table Style Medium 7",
                    },
                )
                # --- Pas format toe op Kol C & D NA HET MAKEN VAN DE TABEL ---
                fmt_col_c_no_wrap_oe = workbook.add_format({'valign': 'top'}) # ZONDER text_wrap
                fmt_col_d_basic_oe = workbook.add_format({'valign': 'top'})
                # Kolom C = index 2, Kolom D = index 3 in df_errors_non_mand_sheet
                for row_idx_in_df in range(max_row_oe):
                    excel_row_index = startrow_opt_err + 1 + row_idx_in_df

                    # Kolom C: Schrijf ZONDER wrap
                    value_c = df_errors_non_mand_sheet.iat[row_idx_in_df, 2]
                    ws_opt_err.write(excel_row_index, 2, value_c, fmt_col_c_no_wrap_oe)

                    # Kolom D: Schrijf expliciet, zet spatie indien leeg
                    value_d = df_errors_non_mand_sheet.iat[row_idx_in_df, 3]
                    if value_d == '':
                        ws_opt_err.write_string(excel_row_index, 3, ' ', fmt_col_d_basic_oe)
                    else:
                        ws_opt_err.write(excel_row_index, 3, value_d, fmt_col_d_basic_oe)
                # --- Einde format Kol C & D --- 
                # --- Stel vaste rijhoogte in om auto-resize door wrap te voorkomen ---
                default_row_height = 15
                # Bepaal de index van de laatste datarow voor de loop
                last_data_row_index_oe = startrow_opt_err + max_row_oe
                # Loop door de Excel rij-indexen van de datarijen
                for row_num in range(startrow_opt_err + 1, last_data_row_index_oe + 1):
                    ws_opt_err.set_row(row_num, default_row_height)
                # --- Einde Vaste Rijhoogte --- 
            else:
                # Schrijf 'geen fouten' bericht
                fmt_default_table = workbook.add_format(
                    {"font_size": 10}
                )  # Basic format
                ws_opt_err.write(
                    0, 0, "Geen fouten gevonden in optionele velden.", fmt_default_table
                )
                ws_opt_err.set_column("A:A", 50)

            # ==================================================================
            # EINDE CODE VOOR SHEET 5: OPTIONELE FOUTEN
            # ==================================================================

            # ==================================================================
            # START CODE VOOR SHEET 6: OPTIONELE %
            # ==================================================================
            ws_opt_perc = workbook.add_worksheet("6. Optionele %")
            suppress_excel_errors(ws_opt_perc)
            writer.sheets["6. Optionele %"] = ws_opt_perc
            # Bereken df_percentages_non_mand hier
            field_stats_non_mand_perc = []
            for (
                f
            ) in non_mandatory_fields:  # Loop door *alle* optionele velden uit config
                aanwezig = "Ja" if f in df.columns else "Nee"
                filled_nm = filled_counts_non_mand.get(f, 0)  # 0 als kolom mist
                field_filled_percentage_nm = (
                    (filled_nm / total_rows * 100) if total_rows > 0 else 0
                )
                field_errors_nm = errors_per_field_non_mand.get(
                    f, 0
                )  # 0 als kolom mist
                percentage_fout_field_nm = (
                    (field_errors_nm / filled_nm * 100) if filled_nm > 0 else 0
                )
                field_juist_nm = max(0, filled_nm - field_errors_nm)
                field_stats_non_mand_perc.append(
                    {
                        "GHX Header": f,
                        "Supplier Header": clean_header(
                            original_column_mapping.get(f, "")
                        ),
                        "Aanwezig": aanwezig,
                        "FilledPercentage": field_filled_percentage_nm
                        / 100,  # Deel door 100
                        "PercentageFout": percentage_fout_field_nm
                        / 100,  # Deel door 100
                        "Aantal juist ingevuld": field_juist_nm,
                    }
                )
            df_percentages_non_mand_sheet = pd.DataFrame(field_stats_non_mand_perc)
            
            # Check if DataFrame is not empty before column selection
            if not df_percentages_non_mand_sheet.empty:
                df_percentages_non_mand_sheet = df_percentages_non_mand_sheet[
                    [
                        "GHX Header",
                        "Supplier Header",
                        "Aanwezig",
                        "FilledPercentage",
                        "PercentageFout",
                        "Aantal juist ingevuld",
                    ]
                ]
            else:
                # Create empty DataFrame with correct columns
                df_percentages_non_mand_sheet = pd.DataFrame(columns=[
                    "GHX Header",
                    "Supplier Header", 
                    "Aanwezig",
                    "FilledPercentage",
                    "PercentageFout",
                    "Aantal juist ingevuld"
                ])

            if not df_percentages_non_mand_sheet.empty:
                df_percentages_non_mand_sheet.to_excel(
                    writer, sheet_name="6. Optionele %", index=False
                )
                # Definieer percentage opmaak (als het nog niet bestaat of voor de zekerheid opnieuw)
                percentage_format = writer.book.add_format({'num_format': '0.00%'})

                ws_opt_perc.set_column(0, 0, 30)
                ws_opt_perc.set_column(1, 1, 30)
                ws_opt_perc.set_column(2, 2, 12)
                ws_opt_perc.set_column(3, 3, 18, percentage_format)  # Filled %
                ws_opt_perc.set_column(4, 4, 18, percentage_format)  # Fout %
                ws_opt_perc.set_column(5, 5, 20)  # Aantal Juist
                # De onderstaande regel is nu overbodig door de expliciete format hierboven
                # ws_opt_perc.set_column(3, 4, 18)  # fmt_perc_table verwijderd
                (max_row_op, max_col_op) = df_percentages_non_mand_sheet.shape
                # Header format
                for c_idx, value in enumerate(
                    df_percentages_non_mand_sheet.columns.values
                ):
                    ws_opt_perc.write(0, c_idx, value, fmt_header_orange)
                # Tabel stijl
                ws_opt_perc.add_table(
                    0,
                    0,
                    max_row_op,
                    max_col_op - 1,
                    {
                        "columns": [{"header": col} for col in df_percentages_non_mand_sheet.columns],
                        "header_row": True,
                        "style": "Table Style Medium 1",
                    },
                )
            else:
                ws_opt_perc.write(
                    0,
                    0,
                    "Geen optionele velden gevonden of van toepassing.",
                    fmt_default_table,
                )
                ws_opt_perc.set_column("A:A", 50)

            # ==================================================================
            # EINDE CODE VOOR SHEET 6: OPTIONELE %
            # ==================================================================

            # ==================================================================
            # DISABLED: DATABASE AANPASSING SHEET - BACKUP CODE (was Sheet 7)
            # ==================================================================
            # ws_db = workbook.add_worksheet("7. Database Aanpassing")
            # suppress_excel_errors(ws_db)
            # writer.sheets["7. Database Aanpassing"] = ws_db
            # ws_db.set_column("A:A", 35)
            # ws_db.set_column("B:B", 115)
            # intro_db_text = """Database Aanpassingen\n\nGHX voert momenteel automatische correcties uit op sommige aangeleverde data. Dit gebeurt om de data toch te kunnen verwerken. Het is belangrijk dat u hiervan op de hoogte bent, omdat we naar een strenger validatieproces gaan waarbij deze data in de toekomst mogelijk wordt afgekeurd.\n\nOnderstaande tabel toont de automatische aanpassingen die zijn toegepast op basis van de gevonden fouten in uw aanlevering. Probeer deze punten te corrigeren in toekomstige uploads."""
            # ws_db.merge_range(
            #     "A1:B1",
            #     intro_db_text,
            #     workbook.add_format(
            #         {
            #             "font_size": 11,
            #             "text_wrap": True,
            #             "align": "left",
            #             "valign": "top",
            #         }
            #     ),
            # )  # Simpel format
            # ws_db.set_row(0, 100)
            #
            # db_correction_data = []
            # unique_corrections = set()
            # all_field_names_with_errors = (
            #     set(df_errors["GHX Kolom"].unique()) if not df_errors.empty else set()
            # )
            #
            # for field_name, field_config in config.get("fields", {}).items():
            #     if (
            #         "database_corrections" in field_config
            #         and field_name in all_field_names_with_errors
            #     ):
            #         corrections = field_config["database_corrections"]
            #         if isinstance(corrections, list):
            #             for correction in corrections:
            #                 msg = correction.get("message", "")
            #                 if msg and (field_name, msg) not in unique_corrections:
            #                     db_correction_data.append(
            #                         {"Veld": field_name, "Database Correctie": msg}
            #                     )
            #                     unique_corrections.add((field_name, msg))
            #         elif isinstance(corrections, dict):
            #             msg = corrections.get("message", "")
            #             if msg and (field_name, msg) not in unique_corrections:
            #                 db_correction_data.append(
            #                     {"Veld": field_name, "Database Correctie": msg}
            #                 )
            #                 unique_corrections.add((field_name, msg))
            #
            # db_start_row = 3
            # if db_correction_data:
            #     df_db_corrections = pd.DataFrame(db_correction_data)
            #     df_db_corrections.to_excel(
            #         writer,
            #         sheet_name="7. Database Aanpassing",
            #         startrow=db_start_row,
            #         index=False,
            #     )
            #     (max_row_db, max_col_db) = df_db_corrections.shape
            #     # Header format
            #     for c_idx, value in enumerate(df_db_corrections.columns.values):
            #         ws_db.write(db_start_row, c_idx, value, fmt_header_orange)
            #     # Tabel stijl
            #     ws_db.add_table(
            #         db_start_row,
            #         0,
            #         db_start_row + max_row_db,
            #         max_col_db - 1,
            #         {
            #             "columns": [{"header": col} for col in df_db_corrections.columns],
            #             "header_row": True,
            #             "style": "Table Style Medium 1",
            #         },
            #     )
            # else:
            #     ws_db.write(
            #         db_start_row,
            #         0,
            #         "Geen automatische database aanpassingen toegepast op basis van gevonden fouten.",
            #         fmt_default_table,
            #     )
            # ==================================================================
            # EINDE DATABASE AANPASSING BACKUP CODE  
            # ==================================================================

            # ==================================================================
            # START CODE VOOR SHEET 7: DATASET VALIDATIE
            # ==================================================================
            # Deze functie wordt nu aangeroepen vanuit dit script
            add_colored_dataset_sheet(
                workbook,
                df,
                validation_results,
                ghx_mandatory_fields,
                original_column_mapping,
                JSON_CONFIG_PATH,
                validation_config,
                template_context,
                excel_path,
            )

            # ==================================================================
            # EINDE CODE VOOR SHEET 7: DATASET VALIDATIE
            # ==================================================================

            # ==================================================================
            # START CODE VOOR SHEET 8: KOLOM MAPPING - NIEUWE SIMPELE IMPLEMENTATIE
            # ==================================================================
            # SKIP Sheet 8 voor Template Generator bestanden - kolom mapping is niet relevant
            mapping_data_map = []  # Initialize outside of if/else scope
            ws_map = None  # Initialize ws_map to prevent UnboundLocalError
            
            if (template_context and template_context.get("decisions")) or template_type == "N":
                # Skip Sheet 8 voor:
                # - Template Generator (TG): hebben al correcte kolommen
                # - Nieuwe GHX templates (N): standaard GHX kolommen, geen mapping nodig
                # Alleen oude/leverancier templates (O) krijgen Sheet 8
                pass
            elif template_type in ["O", "AT"]:
                # Import normalize function voor header vergelijking
                from .price_tool import normalize_template_header
                
                ws_map = workbook.add_worksheet("8. Kolom Mapping")
                suppress_excel_errors(ws_map)
                writer.sheets["8. Kolom Mapping"] = ws_map
            mapped_originals = set()
            
            # 1. Toon alle succesvol gemapte headers in GHX template volgorde
            # Gebruik visible_headers volgorde i.p.v. original_column_mapping volgorde
            if validation_config:
                # Check voor v20 vs v18 structuur
                if "field_validations" in validation_config:
                    # v20 structuur - gebruik field_validations volgorde
                    template_ordered_headers = list(validation_config.get("field_validations", {}).keys())
                else:
                    # v18 structuur (fallback)
                    template_ordered_headers = list(validation_config.get("fields", {}).keys())
                
                # Ga door ALLE GHX headers in template volgorde (103 totaal)
                for ghx_header in template_ordered_headers:
                    # Check of deze header gemapt is
                    if ghx_header in original_column_mapping:
                        original_header = original_column_mapping[ghx_header]
                        
                        # Check of dit veld zichtbaar is in Template Generator context
                        is_visible = True
                        if template_context and template_context.get("_decisions"):
                            decisions = template_context.get("_decisions", {})
                            is_visible = decisions.get(ghx_header, {}).get("visible", True)
                        
                        # Voeg toe met supplier header (voor zichtbare velden)
                        if is_visible:
                            mapping_data_map.append({
                                "GHX Header": ghx_header,
                                "Supplier Header": original_header,
                            })
                            # Normaliseer originele header voor vergelijking
                            from .price_tool import normalize_template_header
                            normalized_original = normalize_template_header(original_header)
                            mapped_originals.add(normalized_original)
                        else:
                            # Veld is niet zichtbaar in context - toon als ontbrekend
                            mapping_data_map.append({
                                "GHX Header": ghx_header,
                                "Supplier Header": "— ONTBREKEND (VERBORGEN) —",
                            })
                    else:
                        # Geen mapping gevonden - toon als ontbrekend/optioneel
                        mapping_data_map.append({
                            "GHX Header": ghx_header,
                            "Supplier Header": "— ONTBREKEND (OPTIONEEL) —",
                        })
            else:
                # Fallback naar oude methode als geen validation_config
                for ghx_header, original_header in original_column_mapping.items():
                    # Check of dit veld zichtbaar is in Template Generator context
                    is_visible = True
                    if template_context and template_context.get("_decisions"):
                        decisions = template_context.get("_decisions", {})
                        is_visible = decisions.get(ghx_header, {}).get("visible", True)
                    
                    # Alleen toevoegen als het veld zichtbaar is
                    if is_visible:
                        mapping_data_map.append({
                            "GHX Header": ghx_header,
                            "Supplier Header": original_header,
                        })
                        # Normaliseer originele header voor vergelijking
                        from .price_tool import normalize_template_header
                        normalized_original = normalize_template_header(original_header)
                        mapped_originals.add(normalized_original)
            
            # 2. Toon verplichte velden die ontbreken (gefilterd voor Template Generator)
            if not validation_config:
                logging.warning("validation_config is None, kan Sheet 8 niet volledig genereren.")
            else:
                # Check voor v20 vs v18 structuur
                if "field_validations" in validation_config:
                    # v20 structuur
                    ghx_headers_in_config = list(validation_config.get("field_validations", {}).keys())
                else:
                    # v18 structuur (fallback)  
                    ghx_headers_in_config = list(validation_config.get("fields", {}).keys())
                
                # Filter headers voor Template Generator templates - alleen zichtbare velden
                visible_headers = ghx_headers_in_config
                
                if template_context and template_context.get("decisions"):
                    # Use Template Generator decisions om ingeklapte velden uit te filteren
                    decisions = template_context.get("decisions", {})
                    visible_list = decisions.get("visible_list", [])
                    visible_headers = [header for header in ghx_headers_in_config if header in visible_list]
                    # Template Generator kolom filtering toegepast voor Sheet 8
                else:
                    # Template Generator filtering overgeslagen voor Sheet 8
                    pass
                
                # Toon ALLE GHX headers met mapping status voor AT templates  
                for ghx_header in visible_headers:
                    if ghx_header not in original_column_mapping:
                        # Bepaal status: verplicht of optioneel
                        if ghx_header in ghx_mandatory_fields:
                            status = "--- ONTBREKEND (VERPLICHT) ---"
                        else:
                            status = "--- ONTBREKEND (OPTIONEEL) ---"
                            
                        mapping_data_map.append({
                            "GHX Header": ghx_header,
                            "Supplier Header": status,
                        })
            
            # 3. Vind alle originele headers die NIET gemapt werden
            for original_header in df_original.columns:
                if original_header.lower().startswith("algemeen"):
                    continue  # Skip algemeen kolommen
                    
                # Normaliseer en vergelijk
                normalized_original = normalize_template_header(original_header) 
                if normalized_original not in mapped_originals:
                    mapping_data_map.append({
                        "GHX Header": "--- ONBEKEND / NIET GEMAPT ---",
                        "Supplier Header": normalized_original,
                    })
            mapping_df_sheet = pd.DataFrame(mapping_data_map)

            # Alleen Sheet 8 schrijven voor oude/leverancier templates (O/AT)
            if template_type in ["O", "AT"]:
                mapping_df_sheet.to_excel(
                    writer, sheet_name="8. Kolom Mapping", index=False
                )
                ws_map.set_column(0, 0, 45)
                ws_map.set_column(1, 1, 75)
                (max_row_map, max_col_map) = mapping_df_sheet.shape
                # Header format
                for c_idx, value in enumerate(mapping_df_sheet.columns.values):
                    ws_map.write(0, c_idx, value, fmt_header_orange)
                # Tabel stijl
                ws_map.add_table(
                    0,
                    0,
                    max_row_map,
                    max_col_map - 1,
                    {
                        "columns": [{"header": col} for col in mapping_df_sheet.columns],
                        "header_row": True,
                        "style": "Table Style Medium 1",
                    },
                )

                # ==================================================================
                # EINDE CODE VOOR SHEET 8: KOLOM MAPPING (binnen normale bestanden if-block)
                # ==================================================================


            # ==================================================================
            # EINDE CODE VOOR SHEET 1: DASHBOARD
            # ==================================================================

            # --- Update validatie logboek ---
            # Bereken waarden specifiek voor de log functie
            total_leeg_non_mand = (
                len(present_non_mandatory_columns) * total_rows
            ) - total_filled_non_mand
            update_validation_log(
                bestandsnaam=bestandsnaam,
                template_type=template_type,
                present_columns_count=M_found,
                percentage_correct=percentage_correct,
                total_rows=total_rows,
                total_cols=total_original_cols,
                total_filled_in_present=total_filled_in_present,
                total_errors_in_present=total_errors_in_present,
                total_leeg=empty_in_present,
                M_missing=M_missing,
                ghx_mandatory_fields_list=ghx_mandatory_fields,
                total_errors_non_mand=total_errors_non_mand,
                total_filled_non_mand=total_filled_non_mand,
                total_leeg_non_mand=total_leeg_non_mand,
            )

        # ==================================================================
        # START CODE VOOR VERBORGEN SHEET: CONFIG (SCORELOGICA)
        # ==================================================================
        ws_config = workbook.add_worksheet("Config")
        suppress_excel_errors(ws_config)
        writer.sheets["Config"] = ws_config
        
        # Verberg de Config sheet
        ws_config.hide()
        
        # Maak formats voor Config sheet
        fmt_config_header = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'font_color': '#1F1F1F',
            'bg_color': '#E6E6E6',
            'border': 1,
            'align': 'center'
        })
        
        fmt_config_label = workbook.add_format({
            'font_size': 12,
            'font_color': '#1F1F1F',
            'bold': True,
            'align': 'left'
        })
        
        fmt_config_value = workbook.add_format({
            'font_size': 12,
            'font_color': '#1F1F1F',
            'align': 'center',
            'num_format': '0'
        })
        
        # SCORELOGICA IMPLEMENTATIE
        # Header
        ws_config.merge_range("A1:D1", "KWALITEITSSCORE CONFIGURATIE", fmt_config_header)
        
        # Score berekening (Volledigheid: 0-40, Kwaliteit: 0-45, Template: 0/10, Versie: 0/5)
        ws_config.write("A2", "Totale Score (0-100):", fmt_config_label)
        
        # Bereken volledigheidscore (0-40 punten)
        # Gebaseerd op percentage ingevulde verplichte velden
        if M_found > 0:
            volledigheids_percentage = min(100, (M_found / len(ghx_mandatory_fields)) * 100)
            volledigheids_score = int((volledigheids_percentage / 100) * 40)
        else:
            volledigheids_score = 0
            
        # Bereken kwaliteitscore (0-45 punten)  
        # Gebaseerd op foutpercentage - hoe minder fouten, hoe hoger de score
        if total_rows > 0:
            total_fouten = len(df_errors_mand) + len(df_errors_non_mand)
            fout_percentage = min(100, (total_fouten / total_rows) * 100)
            kwaliteits_score = int(max(0, 45 - (fout_percentage / 100 * 45)))
        else:
            kwaliteits_score = 45  # Perfect als geen data om fouten in te maken
            
        # Template score (10 punten als correct template wordt herkend)
        # Eenvoudige check: als we meer dan 10 verplichte velden hebben gevonden, is template OK
        template_check = len(ghx_mandatory_fields) > 0 and M_found >= len(ghx_mandatory_fields) // 2
        template_score = 10 if template_check else 0
        
        # Versie score (5 punten - kan later uitgebreid worden)
        versie_score = 5  # Standaard 5 punten
        
        # Totale score
        totale_score = volledigheids_score + kwaliteits_score + template_score + versie_score
        
        # Grade mapping
        if totale_score >= 90:
            grade = "A+"
        elif totale_score >= 80:
            grade = "A"
        elif totale_score >= 70:
            grade = "B"
        elif totale_score >= 60:
            grade = "C"
        else:
            grade = "D"
        
        # Schrijf scores naar Config sheet
        ws_config.write("B2", totale_score, fmt_config_value)  # Deze cel wordt gebruikt door score badge
        ws_config.write("B3", grade, fmt_config_value)        # Deze cel wordt gebruikt door score badge
        
        # Detailscores documenteren
        ws_config.write("A4", "SCORE COMPONENTEN:", fmt_config_header)
        
        ws_config.write("A5", "Volledigheid (0-40):", fmt_config_label)
        ws_config.write("B5", volledigheids_score, fmt_config_value)
        ws_config.write("C5", f"({M_found}/{len(ghx_mandatory_fields)} verplichte velden)", fmt_config_label)
        
        ws_config.write("A6", "Kwaliteit (0-45):", fmt_config_label)
        ws_config.write("B6", kwaliteits_score, fmt_config_value)
        ws_config.write("C6", f"({len(df_errors_mand) + len(df_errors_non_mand)} fouten)", fmt_config_label)
        
        ws_config.write("A7", "Template (0/10):", fmt_config_label)
        ws_config.write("B7", template_score, fmt_config_value)
        ws_config.write("C7", "Correct template herkend" if template_check else "Template niet herkend", fmt_config_label)
        
        ws_config.write("A8", "Versie (0/5):", fmt_config_label)
        ws_config.write("B8", versie_score, fmt_config_value)
        ws_config.write("C8", "Huidige versie", fmt_config_label)
        
        # Grade mapping documentatie
        ws_config.write("A10", "GRADE MAPPING:", fmt_config_header)
        ws_config.write("A11", "A+ = 90-100 punten", fmt_config_label)
        ws_config.write("A12", "A  = 80-89 punten", fmt_config_label)
        ws_config.write("A13", "B  = 70-79 punten", fmt_config_label) 
        ws_config.write("A14", "C  = 60-69 punten", fmt_config_label)
        ws_config.write("A15", "D  = 0-59 punten", fmt_config_label)
        
        # Documentatie sectie toevoegen
        ws_config.write("A17", "SCOREBEREKENING DOCUMENTATIE:", fmt_config_header)
        ws_config.write("A18", "Volledigheid (40%):", fmt_config_label)
        ws_config.write("B18", "Gebaseerd op % ingevulde verplichte velden", fmt_config_label)
        ws_config.write("A19", "Kwaliteit (45%):", fmt_config_label)
        ws_config.write("B19", "Gebaseerd op foutpercentage (minder fouten = hogere score)", fmt_config_label)
        ws_config.write("A20", "Template (10%):", fmt_config_label)
        ws_config.write("B20", "10 punten als correct GHX template wordt herkend", fmt_config_label)
        ws_config.write("A21", "Versie (5%):", fmt_config_label)
        ws_config.write("B21", "5 punten standaard voor huidige toolversie", fmt_config_label)
        
        # Kolombreedte instellen
        ws_config.set_column("A:A", 25)
        ws_config.set_column("B:B", 12)  
        ws_config.set_column("C:C", 35)
        ws_config.set_column("D:D", 50)

        logging.info(f"Validatierapport succesvol gegenereerd: '{output_path}'")
        return output_path

    except KeyError as e:
        logging.error(
            f"FOUT (KeyError) bij genereren rapport: Kolom '{e}' niet gevonden. Controleer data/mapping.",
            exc_info=True,
        )
        return None
    except FileNotFoundError as e:  # Vang specifiek FileNotFoundError op
        logging.error(
            f"FOUT: Bestand niet gevonden tijdens rapport generatie: {e}", exc_info=True
        )
        return None
    except Exception as e:
        logging.error(f"Algemene FOUT bij genereren rapport: {e}", exc_info=True)
        return None

    # --- Einde van de genereer_rapport functie ---

    except KeyError as e:
        logging.error(
            f"KeyError bij genereren rapport: Kolom '{e}' niet gevonden. Controleer data of mapping."
        )
        # Debug informatie voor kolommen (uitgecommentarieerd)
        return None  # Geef None terug bij fout
    except Exception as e:
        logging.error(f"Algemene fout bij genereren rapport: {e}")
        import traceback

        traceback.print_exc()  # Print volledige traceback voor debuggen
        return None  # Geef None terug bij fout


# --- streamlit run prijslijst_validatie_app.py ----
