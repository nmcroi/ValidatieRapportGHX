# validator/price_tool.py

import os
import json
import pandas as pd
import re
from datetime import datetime
from typing import Dict, List, Tuple, Any
import logging

# Importeer de rapporteerfunctie (ervan uitgaande dat die in rapport_utils.py staat)
try:
    from .rapport_utils import genereer_rapport
except ImportError:
    # Fallback voor als het script direct wordt getest (minder relevant voor Streamlit run)
    try:
        from rapport_utils import genereer_rapport
    except ImportError:
        logging.error("Kon genereer_rapport niet importeren. Zorg dat rapport_utils.py bestaat.")
        # Definieer een dummy functie om NameErrors te voorkomen als rapport_utils mist
        def genereer_rapport(*args, **kwargs):
            logging.error("Dummy genereer_rapport aangeroepen omdat import mislukte.")
            print("FOUT: rapport_utils.py of genereer_rapport functie niet gevonden!")
            return None

# -----------------------------
# HELPER FUNCTIES
# -----------------------------

def clean_column_name(col: str) -> str:
    """Schoont een kolomnaam op."""
    if not isinstance(col, str):
        return ''
    # Neem alleen deel voor newline, strip witruimte, maak lowercase
    return col.split('\n')[0].strip().lower()

def map_headers(df: pd.DataFrame, mapping_config: Dict, return_mapping: bool = False) -> Tuple[pd.DataFrame, List[str], Dict[str, str], Dict[str, str]] | Tuple[pd.DataFrame, List[str], Dict[str, str]]:
    """Mapt de headers van het DataFrame naar de GHX standaard headers."""
    # Haal mapping uit configuratie
    header_mapping = {k: v["alternatives"] for k, v in mapping_config.get("standard_headers", {}).items()}

    # Maak een dictionary van originele kolom -> opgeschoonde kolomnaam
    cleaned_columns = {col: clean_column_name(col) for col in df.columns}

    # Maak een reverse mapping: opgeschoonde alternatieve naam -> standaard header
    reverse_mapping = {}
    for std_header, alternatives in header_mapping.items():
        # Voeg de standaard header zelf ook toe als alternatief (lowercase, schoon)
        cleaned_std_header = clean_column_name(std_header)
        if cleaned_std_header not in reverse_mapping: # Voorkom overschrijven door alternatief
             reverse_mapping[cleaned_std_header] = std_header
        # Voeg alternatieven toe
        for alt in alternatives:
            cleaned_alt = clean_column_name(alt)
            reverse_mapping[cleaned_alt] = std_header # Alternatief wijst naar standaard

    mapped_columns = {}
    unrecognized = []
    duplicates = {} # Houd bij welke standaard header duplicaten heeft en wat de originelen waren
    original_column_mapping = {} # Houd bij welke originele kolom naar welke (niet-duplicate) standaard header mapt

    # Houd bij welke standaard headers we al hebben toegewezen om duplicaten te nummeren
    assigned_std_headers_count = {}

    for original_col in df.columns:
        clean_col = cleaned_columns[original_col]
        std_header = reverse_mapping.get(clean_col) # Zoek standaard header

        if std_header:
            # Standaard header gevonden
            count = assigned_std_headers_count.get(std_header, 0)
            if count == 0:
                # Eerste keer dat we deze standaard header zien
                new_header = std_header
                mapped_columns[original_col] = new_header
                original_column_mapping[new_header] = original_col # Map standaard naar origineel
                assigned_std_headers_count[std_header] = 1
            else:
                # Dit is een duplicaat
                count += 1
                new_header = f"{std_header}_DUPLICAAT_{count}"
                duplicates.setdefault(std_header, []).append(original_col) # Noteer origineel bij duplicaat
                mapped_columns[original_col] = new_header # Hernoem kolom in df
                assigned_std_headers_count[std_header] = count
        else:
            # Geen standaard header gevonden, gebruik originele (opgeschoonde?) naam
            # We gebruiken de *originele* naam in mapped_columns om te zorgen dat rename werkt
            mapped_columns[original_col] = original_col
            if not str(original_col).lower().startswith('algemeen'): # Negeer 'algemeen' kolom
                 unrecognized.append(original_col) # Noteer als onherkend (indien niet 'algemeen')

    # Hernoem de kolommen in het DataFrame
    df = df.rename(columns=mapped_columns)

    # Maak dictionary met details over duplicaten (welke _DUPLICAAT_X hoort bij welk origineel)
    duplicate_headers_details = {}
    for header, original_cols_list in duplicates.items():
        # Start nummering duplicaten vanaf _2
        for i, original_col_name in enumerate(original_cols_list):
             duplicate_name = f"{header}_DUPLICAAT_{i+2}"
             duplicate_headers_details[duplicate_name] = original_col_name

    if return_mapping:
        # Geef df, onherkende lijst, details duplicaten, en origineel->standaard mapping terug
        return df, unrecognized, duplicate_headers_details, original_column_mapping
    else:
        # Geef alleen df, onherkende lijst, en details duplicaten terug
        return df, unrecognized, duplicate_headers_details

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Schoont het DataFrame op (logica uit Code 3)."""
    # Check eerst of 'Artikelnummer' kolom bestaat (na mapping)
    if 'Artikelnummer' not in df.columns:
        logging.error("'Artikelnummer' kolom niet gevonden na mapping. Opschonen gestopt.")
        # Overweeg hier een error te raisen of de originele df terug te geven
        # raise ValueError("'Artikelnummer' kolom niet gevonden na mapping.")
        return df # Geeft df terug zoals het was

    # Verwijder rijen waar alles leeg is
    df = df.dropna(how='all')

    # Vind eerste en laatste rij met een geldig Artikelnummer
    first_valid = df['Artikelnummer'].first_valid_index()
    last_valid = df['Artikelnummer'].last_valid_index()

    # Beperk DataFrame tot deze rijen
    if first_valid is not None and last_valid is not None:
        logging.info(f"Data beperkt tot rijen (0-based index): {first_valid} t/m {last_valid}")
        df = df.loc[first_valid:last_valid].reset_index(drop=True)
    else:
        logging.warning("Geen geldige 'Artikelnummer' waarden gevonden, dataframe is mogelijk leeg.")
        return pd.DataFrame(columns=df.columns) # Geeft lege dataframe terug met dezelfde kolommen

    # Verwijder uitleg/instructie rij (check op eerste rij na beperking)
    if not df.empty:
        first_value = str(df.loc[0, 'Artikelnummer']).strip()
        explanation_keywords = [
            "karakters", "characters", "the unique", "explanation", "unique article number",
            "instructie", "instruction", "you, as the", "vul het unieke",
            "assign to", "supplier", "artikelnummer dat u als leverancier"
        ]
        # Check op lengte of keywords
        if (len(first_value) > 70 or # Iets kortere check
            any(keyword in first_value.lower() for keyword in explanation_keywords)):
            logging.info(f"Mogelijke uitleg/instructie rij verwijderd op basis van inhoud: '{first_value[:100]}...'")
            df = df.iloc[1:].reset_index(drop=True)

        # Extra check voor voorbeeld-/demo-rij (op de *nieuwe* eerste rij)
        if not df.empty:
            first_value_after_potential_removal = str(df.loc[0, 'Artikelnummer']).strip()
            voorbeeldwaarden = ["ghx-12345", "voorbeeld", "demo", "example", "test"] # Uitgebreide lijst
            if first_value_after_potential_removal.lower() in voorbeeldwaarden:
                logging.info(f"Mogelijke voorbeeld/demo rij verwijderd op basis van inhoud: '{first_value_after_potential_removal}'")
                df = df.iloc[1:].reset_index(drop=True)

    # Verwijder 'algemeen' kolom indien die nog bestaat (zou niet moeten na mapping, maar voor zekerheid)
    if 'algemeen' in df.columns:
         logging.warning("Kolom 'algemeen' gevonden en verwijderd na mapping.")
         df = df.drop(columns=['algemeen'])
    # Check ook op variaties met hoofdletters etc.
    algemeen_cols = [col for col in df.columns if str(col).strip().lower() == 'algemeen']
    if algemeen_cols:
        logging.warning(f"Kolommen {algemeen_cols} gevonden die lijken op 'algemeen' en worden verwijderd.")
        df = df.drop(columns=algemeen_cols)


    return df

def validate_field(field_name: str, value: Any, field_rules: dict, invalid_values: list, row_data: dict = None) -> list:
    """Valideert een enkele waarde op basis van de regels (uit Code 4)."""
    errors = []
    value_str = str(value).strip() # Werk met de string representatie

    # 1. Leeg check (incl. invalid values)
    is_empty_or_invalid = pd.isnull(value) or value_str == '' or value_str.lower() in invalid_values
    if is_empty_or_invalid:
        # Is het veld verplicht (GHXmandatory of via dependency)?
        is_required = field_rules.get("GHXmandatory", False)
        # Check dependency rule
        if not is_required and "depends_on" in field_rules and row_data:
             dependency = field_rules["depends_on"]
             dep_field = dependency.get("fields", [""])[0]
             dep_cond = dependency.get("condition")
             dep_value = str(row_data.get(dep_field, "")).strip()
             # Als conditie '1' is en de afhankelijke waarde is '1', dan is dit veld ook verplicht
             if dep_cond == "1" and dep_value == "1":
                 is_required = True

        if is_required:
            error_message = field_rules.get("error_messages", {}).get("required", f"Veld '{field_name}' is verplicht maar leeg.")
            error_code = field_rules.get("error_codes", {}).get("required", "73") # Default code voor leeg verplicht
            errors.append({'message': error_message, 'code': error_code})
        return errors # Stop validatie als leeg/invalid

    # 2. String checks (alleen als niet leeg/invalid)
    if field_rules.get("type") == "string":
        min_length = field_rules.get("min_length")
        if min_length and len(value_str) < min_length:
            error_message = field_rules.get("error_messages", {}).get("min_length", f"Waarde '{value_str[:20]}...' is te kort (min {min_length}).")
            error_code = field_rules.get("error_codes", {}).get("min_length", "74")
            errors.append({'message': error_message, 'code': error_code})
        max_length = field_rules.get("max_length")
        if max_length and len(value_str) > max_length:
            error_message = field_rules.get("error_messages", {}).get("max_length", f"Waarde '{value_str[:20]}...' is te lang (max {max_length}).")
            error_code = field_rules.get("error_codes", {}).get("max_length", "75")
            errors.append({'message': error_message, 'code': error_code})
        allowed = field_rules.get("allowed_values")
        if allowed:
            # Normaliseer zowel de waarde als de toegestane waarden voor vergelijking
            normalized_value = value_str.upper()
            allowed_normalized = [str(x).strip().upper() for x in allowed]
            if normalized_value not in allowed_normalized:
                error_message = field_rules.get("error_messages", {}).get("allowed_values", f"Waarde '{value_str}' niet toegestaan. Moet zijn: {', '.join(map(str,allowed))}.")
                error_code = field_rules.get("error_codes", {}).get("allowed_values", "80")
                errors.append({'message': error_message, 'code': error_code})

    # 3. Numeric checks (alleen als niet leeg/invalid)
    if field_rules.get("type") == "numeric":
        # Verwijder duizendtalscheidingstekens voor conversie
        cleaned_value_str = value_str.replace('.', '') # Veronderstelt '.' als duizendtal, pas aan indien nodig
        cleaned_value_str = cleaned_value_str.replace(field_rules.get("decimal_separator", ","), ".") # Vervang decimaal door '.'

        try:
            numeric_value = float(cleaned_value_str)
            # Check max integer digits
            max_int = field_rules.get("max_integer_digits")
            if max_int is not None:
                # Gebruik abs() voor negatieve getallen
                integer_part_str = str(int(abs(numeric_value)))
                if len(integer_part_str) > max_int:
                    error_message = field_rules.get("error_messages", {}).get("max_integer_digits", f"Te veel cijfers voor de komma ({len(integer_part_str)} > {max_int}).")
                    error_code = field_rules.get("error_codes", {}).get("max_integer_digits", "78")
                    errors.append({'message': error_message, 'code': error_code})
            # Check max decimal digits (op basis van originele string na vervanging separator)
            max_dec = field_rules.get("max_decimal_digits")
            if max_dec is not None:
                original_parts = value_str.split(field_rules.get("decimal_separator", ","))
                if len(original_parts) == 2:
                     # Verwijder eventuele spaties of duizendtal-tekens uit decimaal deel
                     decimal_part_cleaned = re.sub(r'[^\d]', '', original_parts[1])
                     # Tel alleen relevante decimalen
                     relevant_decimals = len(decimal_part_cleaned.rstrip('0'))
                     if relevant_decimals > max_dec:
                          error_message = field_rules.get("error_messages", {}).get("max_decimal_digits", f"Te veel decimalen ({len(decimal_part_cleaned)} > {max_dec}).")
                          error_code = field_rules.get("error_codes", {}).get("max_decimal_digits","79")
                          errors.append({'message': error_message, 'code': error_code})
        except (ValueError, TypeError):
            error_message = field_rules.get("error_messages", {}).get("numeric", f"Waarde '{value_str}' is geen geldig getal.")
            error_code = field_rules.get("error_codes", {}).get("numeric", "77")
            errors.append({'message': error_message, 'code': error_code})

    # 4. Regex / invalid_format validatie (alleen als niet leeg/invalid)
    # Let op: Regex wordt toegepast op de originele string waarde
    if "validation" in field_rules and "regex" in field_rules["validation"]:
        pattern = field_rules["validation"]["regex"]
        # Voeg ankers toe als ze ontbreken voor volledige match
        if not pattern.startswith('^'): pattern = '^' + pattern
        if not pattern.endswith('$'): pattern = pattern + '$'
        try:
            if not re.match(pattern, value_str):
                error_message = field_rules.get("error_messages", {}).get("invalid_format", f"Waarde '{value_str}' heeft ongeldig formaat.")
                error_code = field_rules.get("error_codes", {}).get("invalid_format", "95")
                errors.append({'message': error_message, 'code': error_code})
        except re.error as e:
             logging.warning(f"Ongeldige regex voor veld {field_name}: {pattern} - Fout: {e}")


    # 5. Overige validaties (zoals mismatch, etc.)
    # Voorbeeld mismatch validatie (uit Code 4) - NOG NIET GEIMPLEMENTEERD IN DEZE FUNCTIE
    # if "depends_on" in field_rules and row_data:
    #     depends_on = field_rules["depends_on"]
    #     if depends_on.get("condition") == "mismatch":
    #         # Implementeer logica om velden te vergelijken
    #         # fields_to_compare = depends_on.get("fields", [])
    #         # if field_name in fields_to_compare and len(fields_to_compare) > 1: ...
    #         error_message = depends_on.get("error_message", "Waarden komen niet overeen")
    #         error_code = field_rules.get("error_codes", {}).get("mismatch", "81") # Voorbeeld code
    #         errors.append({'message': error_message, 'code': error_code})

    return errors

def validate_uom_relationships(df: pd.DataFrame, validation_results: list, validation_config: dict, original_column_mapping: dict) -> list:
    """
    Controleert relaties tussen UOM Codes, Is BestelbareEenheid en Is BasisEenheid.
    (Grotendeels overgenomen uit Code 4)
    """
    required_cols = [
        "Is BestelbareEenheid", "Is BasisEenheid",
        "UOM Code Verpakkingseenheid", "UOM Code Basiseenheid",
        "Inhoud Verpakkingseenheid"
    ]

    # Als cruciale kolommen ontbreken, sla over (oude template?)
    if not all(col in df.columns for col in required_cols):
        logging.warning("Benodigde UOM-kolommen niet allemaal aanwezig, UOM-relatie validatie overgeslagen.")
        return validation_results

    uom_relation_errors_found = False # Flag om te zien of we code 97 fouten toevoegen
    uom_red_flag_config = None
    for flag_config in validation_config.get("red_flags", []):
         if flag_config.get("condition") == "uom_relation":
             uom_red_flag_config = flag_config
             break

    omschrijving_format_mismatch_count = 0
    rij_offset = 3 # Start rijnummer in Excel (1-based) na header(s) en instructie(s)

    for idx, row in df.iterrows():
        excel_row_num = idx + rij_offset # Werkelijke rijnummer in Excel voor meldingen
        try:
            # Gebruik .get() met default lege string voor robuustheid
            is_besteleenheid = str(row.get("Is BestelbareEenheid", "")).strip()
            is_basiseenheid = str(row.get("Is BasisEenheid", "")).strip()
            uom_verpakking = str(row.get("UOM Code Verpakkingseenheid", "")).strip()
            uom_basis = str(row.get("UOM Code Basiseenheid", "")).strip()
            inhoud_verpakking_str = str(row.get("Inhoud Verpakkingseenheid", "")).strip()
            inhoud_verpakking = None
            if inhoud_verpakking_str and inhoud_verpakking_str.lower() not in ["nan", "none", ""]:
                try:
                    # Vervang eerst komma door punt voor conversie
                    inhoud_verpakking = float(inhoud_verpakking_str.replace(",", "."))
                except (ValueError, TypeError):
                    # Als conversie faalt, log het eventueel maar ga door.
                    # De standaard validatie pikt dit mogelijk al op als 'geen geldig getal'.
                    logging.debug(f"Kon 'Inhoud Verpakkingseenheid' ({inhoud_verpakking_str}) niet converteren naar float op rij {excel_row_num}")
                    pass # Blijft None als conversie faalt

            # --- UOM Checks ---
            supplier_col_map = { # Map naar typische supplier kolom namen indien beschikbaar
                 "Is BestelbareEenheid": original_column_mapping.get("Is BestelbareEenheid", ""),
                 "Is BasisEenheid": original_column_mapping.get("Is BasisEenheid", ""),
                 "UOM Code Verpakkingseenheid": original_column_mapping.get("UOM Code Verpakkingseenheid", ""),
                 "UOM Code Basiseenheid": original_column_mapping.get("UOM Code Basiseenheid", ""),
                 "Inhoud Verpakkingseenheid": original_column_mapping.get("Inhoud Verpakkingseenheid", "")
            }


            # CHECK 1 & 2: Beide 1
            if is_besteleenheid == "1" and is_basiseenheid == "1":
                # Check 1: UOMs gelijk?
                if uom_verpakking and uom_basis and uom_verpakking != uom_basis:
                    uom_relation_errors_found = True
                    validation_results.append({
                        "Rij": excel_row_num, "GHX Kolom": "UOM Code Verpakkingseenheid",
                        "Supplier Kolom": supplier_col_map["UOM Code Verpakkingseenheid"],
                        "Veldwaarde": uom_verpakking,
                        "Foutmelding": f"CONFLICT: Als IsBestelbaar=1 én IsBasis=1, moeten UOMs gelijk zijn (nu: '{uom_verpakking}' vs '{uom_basis}').",
                        "code": "97"
                    })
                # Check 2: Inhoud = 1?
                if inhoud_verpakking is not None and inhoud_verpakking != 1:
                    uom_relation_errors_found = True
                    validation_results.append({
                        "Rij": excel_row_num, "GHX Kolom": "Inhoud Verpakkingseenheid",
                        "Supplier Kolom": supplier_col_map["Inhoud Verpakkingseenheid"],
                        "Veldwaarde": inhoud_verpakking_str,
                        "Foutmelding": "CONFLICT: Als IsBestelbaar=1 én IsBasis=1, moet Inhoud Verpakkingseenheid '1' zijn.",
                        "code": "97"
                    })

            # CHECK 3 & 4: Verschillend (en beide ingevuld)
            elif is_besteleenheid and is_basiseenheid and is_besteleenheid != is_basiseenheid:
                # Check 3: UOMs verschillend?
                if uom_verpakking and uom_basis and uom_verpakking == uom_basis:
                     uom_relation_errors_found = True
                     validation_results.append({
                         "Rij": excel_row_num, "GHX Kolom": "UOM Code Verpakkingseenheid",
                         "Supplier Kolom": supplier_col_map["UOM Code Verpakkingseenheid"],
                         "Veldwaarde": uom_verpakking,
                         "Foutmelding": "CONFLICT: Als IsBestelbaar/IsBasis verschillend zijn, moeten UOMs ook verschillend zijn.",
                         "code": "97"
                     })
                # Check 4: Inhoud != 1?
                if inhoud_verpakking is not None and inhoud_verpakking == 1:
                    uom_relation_errors_found = True
                    validation_results.append({
                        "Rij": excel_row_num, "GHX Kolom": "Inhoud Verpakkingseenheid",
                        "Supplier Kolom": supplier_col_map["Inhoud Verpakkingseenheid"],
                        "Veldwaarde": inhoud_verpakking_str,
                        "Foutmelding": "CONFLICT: Als IsBestelbaar/IsBasis verschillend zijn, mag Inhoud Verpakkingseenheid geen '1' zijn.",
                        "code": "97"
                    })

            # CHECK 5: Omschrijving Verpakkingseenheid consistentie (als Red Flag / Waarschuwing)
            if "Omschrijving Verpakkingseenheid" in df.columns:
                 omschrijving = str(row.get("Omschrijving Verpakkingseenheid", "")).strip()
                 if omschrijving and uom_verpakking and inhoud_verpakking is not None:
                     # Gebruik originele string voor inhoud check, maar zonder '.0' als het een heel getal was
                     inhoud_str_check = inhoud_verpakking_str
                     if inhoud_str_check.endswith('.0'):
                          inhoud_str_check = inhoud_str_check[:-2]

                     # Basis check: bevat omschrijving (ongeacht hoofdletters) de inhoud en de UOM code?
                     if not (inhoud_str_check.lower() in omschrijving.lower() and uom_verpakking.lower() in omschrijving.lower()):
                        omschrijving_format_mismatch_count += 1
                        # We voegen de Red Flag pas na de loop toe als er mismatches zijn

        except Exception as e:
            logging.error(f"Fout tijdens UOM validatie logica voor Excel rij {excel_row_num}: {e}")
            continue

    # --- Na de loop ---

    # Voeg geconsolideerde Red Flag toe voor Omschrijving Verpakkingseenheid mismatch (conform Notebook tekst)
    if omschrijving_format_mismatch_count > 0:
         notebook_omschrijving_message = "Verschillende 'Omschrijving Verpakkingseenheid' velden komen mogelijk niet overeen met de verwachte notatie. Controleer of deze velden de juiste UOM code bevatten."
         validation_results.append({
             "Rij": 0, "GHX Kolom": "RED FLAG",
             "Supplier Kolom": "Omschrijving Verpakkingseenheid",
             "Veldwaarde": "",
             "Foutmelding": notebook_omschrijving_message,
             "code": "94"
         })

    # Voeg Red Flag toe als er UOM-relatie fouten (code 97) waren EN er een config voor is
    if uom_relation_errors_found and uom_red_flag_config:
        message = uom_red_flag_config.get("error_message")
        if message:
            # Voorkom duplicaten van deze specifieke red flag
            flag_exists = any(r.get("GHX Kolom") == "RED FLAG" and r.get("Foutmelding") == message for r in validation_results)
            if not flag_exists:
                validation_results.append({
                    "Rij": 0, "GHX Kolom": "RED FLAG", "Supplier Kolom": "", "Veldwaarde": "",
                    "Foutmelding": message,
                    "code": "" # Geen specifieke code voor deze algemene vlag
                })

    return validation_results


def validate_dataframe(df: pd.DataFrame, validation_config: dict, original_column_mapping: dict) -> Tuple[list, dict, list, dict]:
    """
    Valideert het DataFrame en berekent statistieken.
    Retourneert: (results, filled_percentages, red_flag_messages, errors_per_field)
    """
    results = [] # Lijst met alle individuele fout/warning dicts
    fields_config = validation_config.get("fields", {})
    invalid_values_config = validation_config.get("invalid_values", [])
    invalid_values = [str(val).lower() for val in invalid_values_config]
    filled_counts = {} # Houdt telling bij per veld
    field_validation_results = {} # Houdt per veld een lijst van error dicts bij
    red_flag_messages_list = [] # Verzamelt Red Flag berichten
    total_rows = len(df)
    rij_offset = 3 # Start rijnummer in Excel na header(s)/instructie(s)

    # Initialiseer summary_stats (zal worden geretourneerd als filled_percentages)
    summary_stats = {
        'counts_mandatory': {
            'correct_fields': 0, 
            'incorrect_fields': 0, 
            'not_present_fields': 0, 
            'total_defined_mandatory_fields': 0
        },
        'counts_optional': {
            'filled_occurrences': 0, 
            'empty_occurrences': 0, 
            'total_defined_optional_fields': 0, 
            'total_possible_optional_occurrences': 0
        },
        'total_rows_in_df': total_rows
    }

    # Initialiseer tellers en resultaatlijsten
    for field_name in fields_config:
        # Controleer of 'importance' bestaat en 'Verplicht' is, anders default naar optioneel
        rules = fields_config[field_name]
        is_mandatory = rules.get('importance') == 'Verplicht'
        
        if is_mandatory:
            summary_stats['counts_mandatory']['total_defined_mandatory_fields'] += 1
        else:
            summary_stats['counts_optional']['total_defined_optional_fields'] += 1

        if field_name in df.columns:
            filled_counts[field_name] = 0
            field_validation_results[field_name] = []

    # --- Hoofd loop door rijen ---
    logging.info(f"Start validatie van {total_rows} rijen...")
    for idx, row in df.iterrows():
        excel_row_num = idx + rij_offset
        row_data = row.to_dict() # Voor dependency checks

        # Valideer elk veld in de rij
        for field, rules in fields_config.items():
            if field in df.columns:
                value = row[field]
                value_str = '' if pd.isnull(value) else str(value).strip()

                # Tel gevulde velden
                is_gevuld = value_str != '' and value_str.lower() not in invalid_values
                if is_gevuld:
                    filled_counts[field] = filled_counts.get(field, 0) + 1

                # Voer validatie uit
                errors = validate_field(field, value_str if is_gevuld else value, rules, invalid_values, row_data) # Geef lege waarde door als niet gevuld

                # Verwerk gevonden fouten
                if errors:
                     for err in errors:
                         if err.get("message") and str(err.get("message")).strip():
                             result_item = {
                                 "Rij": excel_row_num,
                                 "GHX Kolom": field,
                                 "Supplier Kolom": original_column_mapping.get(field, field),
                                 "Veldwaarde": value_str, # Altijd de string waarde opslaan
                                 "Foutmelding": err.get('message', ''),
                                 "code": err.get('code', '')
                             }
                             results.append(result_item)
                             if field in field_validation_results:
                                 field_validation_results[field].append(result_item)

        # --- Red Flag Checks per rij (uit JSON config) ---
        # Voorbeeld: Check 'both_empty' conditie
        red_flags_config = validation_config.get("red_flags", [])
        for flag in red_flags_config:
            try:
                condition = flag.get("condition")
                message = flag.get("error_message")
                flag_fields = flag.get("fields", [])

                if condition == "both_empty":
                    # Check alleen als de velden daadwerkelijk bestaan in de dataframe
                    relevant_flag_fields = [f for f in flag_fields if f in df.columns]
                    if len(relevant_flag_fields) == len(flag_fields): # Alleen checken als alle velden aanwezig zijn
                        # Gebruik row_data (dict) voor checken, inclusief check op invalid_values
                        all_empty = all(
                            pd.isnull(row_data.get(f)) or
                            str(row_data.get(f)).strip() == '' or
                            str(row_data.get(f)).strip().lower() in invalid_values
                            for f in relevant_flag_fields
                        )
                        if all_empty:
                            # Voeg alleen toe als het bericht nog niet globaal is toegevoegd
                            if message and message not in red_flag_messages_list:
                                red_flag_messages_list.append(message)
                                logging.debug(f"Red flag '{condition}' getriggerd voor rij {excel_row_num}")
                # Voeg hier checks toe voor andere per-rij condities indien nodig

            except Exception as e:
                logging.error(f"Red flag check error in rij {excel_row_num}: {e}")
                continue

    logging.info("Validatie per rij voltooid.")
    # --- Na de hoofd loop ---

    # 1. Roep UOM validatie aan
    logging.info("Starten UOM relatie validatie...")
    # Geef original_column_mapping mee aan UOM validatie voor betere supplier kolom info
    # Let op: validate_uom_relationships past 'results' direct aan en voegt eventueel RED FLAGS toe
    results = validate_uom_relationships(df, results, validation_config, original_column_mapping) # Pass mapping
    logging.info("UOM relatie validatie voltooid.")


    # 2. Bereken summary_stats NA ALLE validaties ---
    logging.info("Berekenen vullingspercentages...") # Hergebruik logging message, past nu beter
    for field_name, rules in fields_config.items():
        is_mandatory = rules.get('importance') == 'Verplicht'

        if field_name in df.columns:
            if is_mandatory:
                # Heeft dit veld fouten?
                if not field_validation_results.get(field_name): # Geen lijst met errors voor dit veld
                    summary_stats['counts_mandatory']['correct_fields'] += 1
                else:
                    summary_stats['counts_mandatory']['incorrect_fields'] += 1
            else: # Optioneel veld
                filled_in_col = filled_counts.get(field_name, 0)
                summary_stats['counts_optional']['filled_occurrences'] += filled_in_col
                summary_stats['counts_optional']['empty_occurrences'] += (total_rows - filled_in_col)
                summary_stats['counts_optional']['total_possible_optional_occurrences'] += total_rows
        else: # Veld niet in DataFrame (niet in input Excel)
            if is_mandatory:
                summary_stats['counts_mandatory']['not_present_fields'] += 1
            # Voor optionele velden die niet aanwezig zijn, doen we niets met filled/empty occurrences

    filled_percentages = summary_stats # Wijs de berekende statistieken toe aan de return variabele

    logging.info("Verwerken Red Flag berichten...")
    # Verwerk Red Flags die door UOM validatie zijn toegevoegd aan validation_results
    validation_red_flags_dicts = [r for r in results if r.get("GHX Kolom") == "RED FLAG"]
    for flag_dict in validation_red_flags_dicts:
         msg = flag_dict.get("Foutmelding")
         if msg and msg not in red_flag_messages_list:
              red_flag_messages_list.append(msg)

    # Voeg globale staffel check toe als Red Flag
    staffel_check_flag = next((flag for flag in validation_config.get("red_flags", []) if flag.get("condition") == "has_staffel"), None)
    if staffel_check_flag:
         staffel_fields = staffel_check_flag.get("fields", [])
         # Check of een van de staffel kolommen data bevat
         has_staffel_data = any(df[f].notna().any() for f in staffel_fields if f in df.columns)
         if has_staffel_data:
              msg = staffel_check_flag.get("error_message")
              if msg and msg not in red_flag_messages_list:
                   red_flag_messages_list.append(msg)

    # Template check conditie: controleer of alle vereiste kolommen voor de nieuwe template aanwezig zijn
    template_check_flag = next((flag for flag in validation_config.get("red_flags", []) 
                              if flag.get("condition") == "template_check"), None)
    if template_check_flag:
        template_fields = template_check_flag.get("fields", [])
        # Controleer of alle template-specifieke velden aanwezig zijn in de dataframe
        template_fields_missing = [f for f in template_fields if f not in df.columns]
        # Als er velden missen, is het niet de nieuwste template
        if template_fields_missing:
            msg = template_check_flag.get("error_message")
            if msg and msg not in red_flag_messages_list:
                red_flag_messages_list.append(msg)
                logging.info(f"Red flag 'template_check' getriggerd: ontbrekende velden: {template_fields_missing}")

    # Verwijder duplicaten uit de verzamelde lijst
    seen_messages = set()
    unique_red_flags = []
    for msg in red_flag_messages_list:
        if msg not in seen_messages:
            seen_messages.add(msg)
            unique_red_flags.append(msg)
    red_flag_messages = unique_red_flags # Dit is de uiteindelijke lijst

    logging.info(f"Validatie analyse voltooid. Gevonden meldingen: {len(results)}, Unieke Red Flags: {len(red_flag_messages)}")

    # 3. Bereken errors_per_field (aantal unieke rijen met fouten per veld, max = gevuld)
    logging.info("Berekenen fouten per veld...")
    errors_per_field = {}
    for field_name, field_errors_list in field_validation_results.items():
        # Tel alleen unieke rijen met fouten voor dit veld
        unique_error_rows = set(res["Rij"] for res in field_errors_list)
        error_count = len(unique_error_rows)
        # Aantal fouten kan niet groter zijn dan aantal gevulde velden
        errors_per_field[field_name] = min(error_count, filled_counts.get(field_name, 0))

    # Retourneer alle berekende informatie
    return results, filled_percentages, red_flag_messages, errors_per_field


# -----------------------------
# HOOFDFUNCTIE VOOR AANROEP VANUIT STREAMLIT
# -----------------------------

def validate_pricelist(input_excel_path: str, mapping_json_path: str, validation_json_path: str, original_input_filename: str) -> str | None:
    """
    Valideert een Excel prijslijst en genereert een Excel validatierapport.
    Retourneert het pad naar het rapport, of None bij een fout.
    """
    try:
        # 1. Laad configuraties
        logging.info("Laden configuratiebestanden...")
        try:
            with open(mapping_json_path, 'r', encoding='utf-8') as f:
                header_mapping_config = json.load(f)
            with open(validation_json_path, 'r', encoding='utf-8') as f:
                validation_config = json.load(f)
        except FileNotFoundError as e:
            logging.error(f"Configuratiebestand niet gevonden: {e}")
            raise # Gooi error door naar Streamlit app
        except json.JSONDecodeError as e:
            logging.error(f"Fout bij lezen JSON configuratie: {e}")
            raise # Gooi error door

        # Haal mapping dictionary en mandatory fields op
        header_mapping_dict = {k: v["alternatives"] for k, v in header_mapping_config.get("standard_headers", {}).items()}
        ghx_mandatory_fields = [
            f for f, r in validation_config.get("fields", {}).items()
            if isinstance(r, dict) and r.get("GHXmandatory") is True
        ]
        logging.info(f"GHX Verplichte velden geladen: {len(ghx_mandatory_fields)} velden.")

        # 2. Lees Excel in
        logging.info(f"Lezen Excel bestand: {input_excel_path}")
        try:
            string_columns = [field for field, rules in validation_config.get("fields", {}).items()
                              if rules.get("read_as_string")]
            dtype_spec = {col: str for col in string_columns}
            
            # Voeg expliciete dtype mappings toe voor problematische kolomnamen in de originele Excel
            # Voor UNSPSC Code (zowel GHX als supplier-kolomnamen)
            dtype_spec["UNSPSC CODE (UNITED NATIONS STANDARD PRODUCTS AND SERVICES CODE)"] = str
            dtype_spec["UNSPSC Code"] = str
            
            # Voor GTIN en andere kolommen die numeriek lijken maar string moeten zijn
            dtype_spec["BARCODENUMMER (EAN/ GTIN/ HIBC)"] = str
            dtype_spec["GTIN Verpakkingseenheid"] = str
            
            # Lees Excel in met de uitgebreide dtype_spec
            df = pd.read_excel(input_excel_path, dtype=dtype_spec)
            df_original = df.copy()
            logging.info(f"Excel succesvol gelezen: {df.shape[0]} rijen, {df.shape[1]} kolommen.")
        except Exception as e:
            logging.error(f"Fout bij lezen Excel bestand: {e}")
            raise # Gooi error door


        # 3. Headers mappen
        logging.info("Mappen van headers...")
        df, unrecognized, duplicates, original_column_mapping = map_headers(df, header_mapping_config, return_mapping=True)
        logging.info(f"Header mapping voltooid. Onherkend: {len(unrecognized)}, Duplicaten: {len(duplicates)}.")
        if unrecognized:
             logging.warning(f"Onherkende headers gevonden: {unrecognized}")
             # Hier zou je eventueel de lijst 'unrecognized' kunnen teruggeven of loggen


        # 4. Data opschonen
        logging.info("Opschonen DataFrame...")
        df = clean_dataframe(df)
        if df.empty:
             logging.warning("DataFrame is leeg na opschonen.")
             # Overweeg hier te stoppen of een leeg rapport te maken
        else:
             logging.info(f"DataFrame opgeschoond. Resterende rijen: {len(df)}")


        # 5. Valideer data
        logging.info("Starten validatie DataFrame...")
        results, filled_percentages, red_flag_messages, errors_per_field = validate_dataframe(
            df, validation_config, original_column_mapping
        )


        # 6. Bepaal bestandsnaam en output directory voor het rapport
        report_base_name = original_input_filename # Gebruik de doorgegeven originele naam
        # Output directory strategie: submap in dezelfde map als input
        output_dir_base = os.path.dirname(input_excel_path)
        # Maak een submap 'validation_reports' als die nog niet bestaat
        report_subdir = os.path.join(output_dir_base, "validation_reports")
        os.makedirs(report_subdir, exist_ok=True)
        # Voeg timestamp toe aan de mapnaam binnen de submap
        output_dir_timestamped = os.path.join(report_subdir, "report_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
        os.makedirs(output_dir_timestamped, exist_ok=True)
        logging.info(f"Output directory voor rapport: {output_dir_timestamped}")


        # 7. Genereer rapport met alle benodigde argumenten
        logging.info("Genereren validatierapport...")
        # Roep de geïmporteerde functie aan
        output_path = genereer_rapport(
            validation_results=results,
            output_dir=output_dir_timestamped,
            bestandsnaam=report_base_name, # <-- Gebruik nu report_base_name (originele naam)
            ghx_mandatory_fields=ghx_mandatory_fields,
            original_column_mapping=original_column_mapping,
            df=df,
            header_mapping=header_mapping_dict,
            df_original=df_original,
            red_flag_messages=red_flag_messages,
            errors_per_field=errors_per_field,
            JSON_CONFIG_PATH=validation_json_path, # Nodig voor laden config in rapport
            summary_data=filled_percentages,  # Doorgeven van summary_data
        )

        if output_path:
            logging.info(f"Rapport succesvol gegenereerd: {output_path}")
            return output_path
        else:
            logging.error("Genereren van rapport is mislukt (genereer_rapport gaf None terug).")
            return None

    except FileNotFoundError as e:
        logging.error(f"Bestand niet gevonden tijdens validatie: {e}")
        raise
    except ImportError as e:
         logging.error(f"Import fout tijdens validatie: {e}")
         raise
    except Exception as e:
        logging.error(f"Een onverwachte fout is opgetreden tijdens validate_pricelist: {e}", exc_info=True)
        raise # Gooi de error opnieuw op zodat Streamlit het kan tonen