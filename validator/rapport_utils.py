# rapport_utils.py

import pandas as pd
import logging
import os
import json
import xlsxwriter  # Nodig voor pd.ExcelWriter engine en grafieken
from datetime import datetime
from typing import Dict, List, Tuple, Any  # Type hints zijn goed om te behouden

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

def has_template_generator_stamp(df: pd.DataFrame) -> bool:
    """
    Detecteert of een DataFrame een Template Generator stamp heeft.
    
    Phase 1: Simpele heuristiek (later vervangen door stamp reading)
    Phase 2: Echte stamp detection uit Excel metadata
    """
    # TODO: Implementeer echte stamp detection
    # Voor nu: simpele heuristiek gebaseerd op kolom patterns
    
    # Template Generator templates hebben vaak unieke kolom combinaties
    tg_indicators = [
        "Context Labels",  # Mogelijk TG kolom
        "Template Preset", # Mogelijk TG kolom  
        "GHX_STAMP",      # Mogelijk TG metadata kolom
    ]
    
    # Check of specifieke TG indicators aanwezig zijn
    has_tg_indicators = any(col in df.columns for col in tg_indicators)
    
    if has_tg_indicators:
        logging.info("Template Generator indicatoren gedetecteerd")
        return True
        
    return False

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

def determine_template_type(df: pd.DataFrame) -> str:
    """
    Bepaalt het template type op basis van DataFrame kolommen.
    
    Returns:
        'TG' - Template Generator gegenereerde template
        'N'  - Nieuwe GHX standaard template  
        'O'  - Oude GHX template of supplier template
    """
    # Prioriteit 1: Template Generator detection
    if has_template_generator_stamp(df):
        logging.info("Template type gedetecteerd: Template Generator (TG)")
        return "TG"
    
    # Prioriteit 2: Nieuwe vs Oude template
    if is_new_template(df):
        logging.info("Template type gedetecteerd: Nieuwe GHX template (N)")
        return "N"
    else:
        logging.info("Template type gedetecteerd: Oude/Supplier template (O)")
        return "O"

# --- Configuratie Constanten (Vervangen globale variabelen uit notebook) ---
# Deze kunnen later eventueel uit een centraal config bestand of env variabelen komen

# Configuratie voor validatie-overzichtsbestand (uit notebook Config cel)
ENABLE_VALIDATION_LOG = True  # True = logging aan, False = logging uit
# BELANGRIJK: Pas dit pad aan naar de *daadwerkelijke* locatie waar het logboek moet komen
# in de omgeving waar de code draait! Een hardcoded pad is meestal niet ideaal.
# Voor nu nemen we het pad uit je notebook over als voorbeeld.
VALIDATION_LOG_FILE = "/Users/ghxnielscroiset/Library/CloudStorage/OneDrive-GlobalHealthcareExchange/GHX ValidatieRapporten/validaties_overzicht.xlsx"

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
        print(f"FOUT: Validatie configuratiebestand niet gevonden op {json_path}")
        # Je zou hier kunnen kiezen om een lege config terug te geven of de error te raisen
        # raise
        return (
            {}
        )  # Geeft lege dictionary terug om door te gaan, maar rapport kan incompleet zijn
    except json.JSONDecodeError:
        print(f"FOUT: Ongeldig JSON-formaat in {json_path}")
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
    
    # Template bonus (0-10 punten)  
    template_bonus = 10 if template_type == "N" else 5  # Nieuwe template krijgt bonus
    
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
        "Template Type": "Nieuw" if template_type == "N" else "Oud",
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
                print(
                    f"Waarschuwing: Kon bestaand validatielogboek niet lezen ({VALIDATION_LOG_FILE}): {e}"
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

        print(f"Validatie toegevoegd aan logboek: {VALIDATION_LOG_FILE}")

    except Exception as e:
        print(f"Fout bij het bijwerken van het validatielogboek: {e}")


def add_colored_dataset_sheet(
    workbook,
    df,
    validation_results,
    ghx_mandatory_fields,
    original_column_mapping,
    JSON_CONFIG_PATH,
    validation_config=None,
):
    """Voeg een sheet toe met de volledige dataset in kleurcodering."""
    # Gebruik de doorgegeven validation_config of val terug op laden van bestand
    if validation_config:
        config = validation_config
    else:
        # Fallback: laad van bestand (backwards compatibility)
        config = load_validation_config(JSON_CONFIG_PATH)
        if not config:  # Als config laden mislukt is
            print(
                "WARNING: Kan gekleurde dataset sheet niet toevoegen omdat validatie config mist."
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

    if not is_new_template:
        print(
            "INFO: Gekleurde dataset sheet (9) wordt overgeslagen, lijkt geen nieuwe template te zijn."
        )
        return  # Geen sheet toevoegen als oude template

    try:
        worksheet = workbook.add_worksheet("9. Dataset Validatie")
        
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
        worksheet.write("A4", "Foutief ingevuld (optioneel)", error_optional_format_legend)
        worksheet.write("A5", "Verplicht veld leeg", empty_mandatory_format_legend)
        worksheet.write("A6", "UOM-relatie conflict", uom_relation_error_format_legend)
        start_row = 7

        # Maak error lookups
        error_lookup = {}  # Voor normale fouten
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
                        # Normale fouten
                        if row_idx not in error_lookup:
                            error_lookup[row_idx] = set()
                        error_lookup[row_idx].add(col_idx)

        # Schrijf headers
        for col, header in enumerate(df.columns):
            worksheet.write(start_row, col, str(header), header_format)

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

        for row_idx in range(max_rows_sheet):
            for col_idx, field_name in enumerate(df.columns):
                value = df.iloc[row_idx, col_idx]
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
                    and col_idx in uom_relation_error_lookup[row_idx]
                ):
                    cell_format = uom_relation_error_format
                elif is_empty and (is_mandatory or has_dependency):
                    # PRIORITEIT: Verplichte velden die leeg zijn zijn ALTIJD geel
                    cell_format = empty_mandatory_format
                elif row_idx in error_lookup and col_idx in error_lookup[row_idx]:
                    # Onderscheid maken tussen verplichte en niet-verplichte fouten
                    if is_mandatory:
                        cell_format = error_format  # Rood voor verplichte fouten
                    else:
                        cell_format = error_optional_format  # Roze voor niet-verplichte fouten

                # Schrijf waarde met bepaalde opmaak
                worksheet.write(
                    start_row + row_idx + 1, col_idx, value_str, cell_format
                )

        # Stel kolombreedte in - A is al ingesteld op 25, rest op 20
        if len(df.columns) > 1:
            worksheet.set_column(1, len(df.columns) - 1, 20)

        worksheet.write(
            start_row - 1,
            0,
            "Dataset Validatie:",
            workbook.add_format({"bold": True, "font_size": 12}),
        )

    except Exception as e:
        print(f"Fout tijdens genereren gekleurde dataset sheet: {e}")
        # Optioneel: voeg een sheet toe met de foutmelding
        try:
            error_sheet = workbook.add_worksheet("9. Dataset Fout")
            suppress_excel_errors(error_sheet)
            error_sheet.write(0, 0, f"Kon '9. Dataset Validatie' sheet niet genereren.")
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
):
    """
    Genereert het volledige Excel validatierapport, inclusief alle sheets,
    gebaseerd op notebook Code 5 en aangepast dashboard layout.
    """
    if errors_per_field is None:
        errors_per_field = {}  # Voorkom None errors

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
                
                # Categorisering op basis van code ranges
                if 700 <= code_int <= 749:
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

        # Bestandsnaam zonder extensie voor output naamgeving
        bestandsnaam_zonder_extensie = os.path.splitext(bestandsnaam)[0]

        # --- Data Voorbereiding & Berekeningen (Begin) ---
        total_rows = len(df)
        total_cols = len(df.columns)  # Kolommen in verwerkte df
        total_original_cols = len(df_original.columns)  # Kolommen in origineel bestand

        # Gebruik de doorgegeven validation_config of val terug op laden van bestand
        if validation_config:
            config = validation_config
        else:
            config = load_validation_config(JSON_CONFIG_PATH)
            if not config:
                print("FOUT: Kan rapport niet genereren zonder validatie configuratie.")
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
        empty_in_present = (M_found * total_rows) - total_filled_in_present

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
        total_possible_mandatory_fields = len(ghx_mandatory_fields) * total_rows
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

        # Score berekening - Template Type Detectie
        template_type = determine_template_type(df)  # Nieuwe functie

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
        # Bereken nieuwe score ook hier voor bestandsnaam
        completeness_score_file = (M_found / len(ghx_mandatory_fields)) * 40 if len(ghx_mandatory_fields) > 0 else 0
        quality_score_file = (percentage_correct / 100) * 50 if percentage_correct > 0 else 0
        template_bonus_file = 10 if template_type == "N" else 5
        total_score_file = min(100, completeness_score_file + quality_score_file + template_bonus_file)
        score_int_file = round(total_score_file)
        score_grade_file = "A+" if score_int_file >= 90 else "A" if score_int_file >= 80 else "B" if score_int_file >= 70 else "C" if score_int_file >= 60 else "D"
        
        score_suffix = f"_{template_type}{M_found}_{score_int_file}({score_grade_file})"

        # --- Output Bestandsnaam ---
        output_filename = (
            f"{bestandsnaam_zonder_extensie}_validation_rapport{score_suffix}.xlsx"
        )
        output_path = os.path.join(output_dir, output_filename)

        print(f"Schrijven rapport naar: {output_path}")
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
                logo_path = "/Users/ncroiset/Vibe Coding Projecten/Cursor Projecten/Project PrijsValGem_WS app/static/ghx_logo_2.png"
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
            
            fmt_score_number = workbook.add_format({
                'font_size': 28,  # Groot numeriek cijfer
                'font_color': '#1F1F1F',  # Donkere tekst
                'bold': True,
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': '#F2F2F2',
                'border': 1,
                'border_color': '#D0D0D0'
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
            # Bereken volledigheidscore (0-40 punten)
            if M_found > 0:
                volledigheids_percentage = min(100, (M_found / len(ghx_mandatory_fields)) * 100)
                volledigheids_score_display = int((volledigheids_percentage / 100) * 40)
            else:
                volledigheids_score_display = 0
                
            # Bereken kwaliteitscore (0-45 punten)  
            if total_rows > 0:
                total_fouten_display = len(df_errors_mand) + len(df_errors_non_mand)
                fout_percentage_display = min(100, (total_fouten_display / total_rows) * 100)
                kwaliteits_score_display = int(max(0, 45 - (fout_percentage_display / 100 * 45)))
            else:
                kwaliteits_score_display = 45  # Perfect als geen data
                
            # Template score (10 punten)
            template_check_display = len(ghx_mandatory_fields) > 0 and M_found >= len(ghx_mandatory_fields) // 2
            template_score_display = 10 if template_check_display else 0
            
            # Versie score (5 punten)
            versie_score_display = 5
            
            # Totale score
            totale_score_display = volledigheids_score_display + kwaliteits_score_display + template_score_display + versie_score_display
            
            # Score badge op E2:G4 met SCORE: X/100 format (optie 1)
            score_grade = "A+" if totale_score_display >= 90 else "A" if totale_score_display >= 80 else "B" if totale_score_display >= 70 else "C" if totale_score_display >= 60 else "D"
            
            # Hoofdscore cel E2:G3
            ws_dash.merge_range("E2:G3", f"KWALITEITSCORE: {totale_score_display}/100 - CIJFER {score_grade}", fmt_score_number)
            
            # Cijfertoekenning regel (E4:G4) - bold, zwart, groter
            fmt_score_small = workbook.add_format({
                'font_size': 11,
                'bold': True,
                'align': 'center',
                'valign': 'vcenter',
                'font_color': '#000000'
            })
            ws_dash.merge_range("E4:G4", f"Cijfer: {score_grade} | A+(90+) A(80-89) B(70-79) C(60-69) D(<60)", fmt_score_small)
            
            # --- NIEUWE LAYOUT: Links Statistieken, Rechts Actiepunten ---
            
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
            
            # LINKER KANT: Statistieken (B9-C9, A blijft gutter)
            ws_dash.merge_range(
                f"B{current_row}:C{current_row}",  # B tot C op huidige rij (rij 9, index 8)
                "Belangrijkste Statistieken",
                fmt_header_stats,
            )
            ws_dash.set_row(current_row, 18)  # Hoogte header rij
            
            # RECHTER KANT: Foutmeldingen header (E9-K9) - header over E t/m K
            ws_dash.merge_range(
                f"E{current_row}:K{current_row}",  # E tot K op huidige rij (rij 9, index 8)
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
            
            # RECHTER KANT: Foutmeldingen subheaders (E-K) - direct na main header
            # Remove current_row += 1 to eliminate gap between header and subheader
            # Beschrijving spreidt over E, F, G (was D, E, F)
            ws_dash.merge_range(
                f"E{current_row+1}:G{current_row+1}",  # E-G voor Beschrijving op huidige Excel rij (1-based)
                "Beschrijving",
                fmt_subheader_grey
            )
            ws_dash.write(current_row, 7, "Aantal", fmt_subheader_grey)         # H (was G)
            ws_dash.write(current_row, 8, "Type", fmt_subheader_grey)           # I (was H)
            ws_dash.write(current_row, 9, "Type (Sheet)", fmt_subheader_grey)   # J (was I)  
            ws_dash.write(current_row, 10, "Foutcode", fmt_subheader_grey)      # K (was J)
            ws_dash.set_row(current_row, 18)  # Normale rijhoogte
            
            # Statistieken data begint direct na header op rij 10 (header is rij 9)
            stats_start_row = current_row + 1  # Rij 10 (direct na header rij 9)
            
            # Nu current_row verhogen naar data rows (na subheader)
            current_row += 1  # Move to data rows after subheader
            aantal_velden_totaal = total_rows * total_original_cols
            aantal_aanw_verpl_velden = M_found * total_rows
            aantal_afw_verpl_velden = M_missing * total_rows
            aantal_aanw_lege_verpl_velden = empty_in_present

            # Tel rejection errors (afkeuringen) - alleen regels die door Gatekeeper zouden worden afgewezen
            aantal_afkeuringen = 0
            if not df_errors.empty and "code" in df_errors.columns:
                # Tel unieke rijen met rejection errors (codes 700-749)
                rejection_rows = df_errors[
                    df_errors["code"].apply(lambda x: str(x).strip().isdigit() and 700 <= int(float(str(x).strip())) <= 749)
                ]["Rij"].nunique()
                aantal_afkeuringen = rejection_rows

            # Template context informatie toevoegen
            template_type_info = "Default Template"
            if template_context:
                template_choice = template_context.get("template_choice", "besteleenheid")
                product_type = template_context.get("product_type", "facilitair")
                institutions = template_context.get("institutions", [])
                
                template_type_info = f"Template Generator - {template_choice} ({product_type})"
                if institutions:
                    template_type_info += f" [{', '.join(institutions)}]"
                    
                # Voeg ingeklapte velden informatie toe
                collapsed_count = summary_data.get('collapsed_fields_count', 0)
                if collapsed_count > 0:
                    template_type_info += f" | {collapsed_count} velden ingeklapt"
            
            stats_data_original = [
                ("Template Type", template_type_info),
                ("Aantal rijen", total_rows),
                ("Aantal kolommen", total_original_cols),
                ("Aantal velden", aantal_velden_totaal),
                ("Aantal aanwezige verplichte velden", aantal_aanw_verpl_velden),
                ("Aantal afwezige verplichte velden", aantal_afw_verpl_velden),
                ("Aantal gevulde verplichte velden", total_filled_in_present),
                (
                    "Aantal aanwezige lege verplichte velden",
                    aantal_aanw_lege_verpl_velden,
                ),
                ("Aantal regels mogelijk afgewezen door Gatekeeper", aantal_afkeuringen),
            ]
            # EERSTE PRIORITEIT: Herstel de originele Belangrijkste Statistieken data!
            # Statistieken data CORRECT positioneren: B=labels, C=numbers, A=gutter
            # Start direct na header (zelfde rij als header in 0-based indexing)
            stats_current_row = 8  # Direct na header (Excel rij 9 = 0-based index 8)
            for key, value in stats_data_original:
                ws_dash.write(stats_current_row, 1, key, fmt_label_green)      # Kolom B - Labels (was A)
                
                # Template Type is string, andere waarden zijn numeriek
                if key == "Template Type":
                    ws_dash.write(stats_current_row, 2, value, fmt_value_green)  # String waarde
                else:
                    ws_dash.write_number(stats_current_row, 2, value, fmt_value_green)  # Numerieke waarde
                    
                # Kolom A blijft LEEG als gutter
                stats_current_row += 1
            stats_end_row = stats_current_row

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
            
            # Positioneer op B13 (regel 1078 wijzigen): 1 witte regel onder statistieken
            missing_start_row = stats_end_row + 1  # 1 witte regel onder statistieken
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
                    "Aantal lege verplichte velden (incl. ontbrekende)",
                    aantal_leeg_incl_missing,
                ),
                (
                    "Percentage ingevulde verplichte velden (incl. ontbrekende)",
                    percentage_ingevuld_incl_missing / 100,
                ),
                ("Aantal ontbrekende verplichte kolommen", M_missing),
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
            if "global_settings" in config and "error_code_descriptions" in config["global_settings"]:
                # v20 structure
                error_code_desc = config["global_settings"]["error_code_descriptions"]
            else:
                # v18 structure (fallback)
                error_code_desc = config.get("error_code_descriptions", {})
            
            if "724" not in error_code_desc:
                error_code_desc["724"] = "UOM-relatie conflict"
            if "721" not in error_code_desc:
                error_code_desc["721"] = (
                    "Formaat Omschrijving Verp.eenheid (Waarschuwing)"
                )

            df_foutcodes_top = pd.DataFrame()
            # Voor foutmeldingen tabel
            table_subheader_row = current_row - 1  # De subheader rij voor foutmeldingen (row where subheaders were written)
            table_start_row = current_row + 1  # De rij na de subheader voor foutmeldingen
            table_end_row = table_start_row + 1  # Default end row
            if not df_errors.empty:
                # Check of 'code' kolom bestaat voor we verder gaan
                if "code" in df_errors.columns:
                    # Simpel: groepeer alle fouten alleen op code, net als in het notebook
                    df_foutcodes = df_errors.groupby("code").size().reset_index(name="Aantal")
                    
                    # Filter lege codes uit
                    df_foutcodes = df_foutcodes[df_foutcodes["code"] != ""]
                    
                    # Maak beschrijving op basis van de foutcode en verwijder FLAG: prefix
                    df_foutcodes["Beschrijving"] = df_foutcodes["code"].apply(
                        lambda x: error_code_desc.get(str(x).strip(), f"Code: {x}").replace("FLAG: ", "")
                    )

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
                        
                        # Custom kolom mapping voor nieuwe layout
                        for c_idx, cell_value in enumerate(row_data):
                            col_name = df_foutcodes_top.columns[c_idx]
                            fmt = (
                                fmt_error_table_code
                                if col_name == "Foutcode"
                                else fmt_error_table_cell_right
                                if col_name == "Aantal"
                                else fmt_error_table_cell
                            )
                            
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
                                    num_val = int(cell_value)
                                    ws_dash.write_number(current_table_row, 7, num_val, fmt)
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
                                    num_val = int(cell_value)
                                    ws_dash.write_number(current_table_row, 10, num_val, fmt)
                                except (ValueError, TypeError):
                                    ws_dash.write_string(current_table_row, 10, str(cell_value), fmt)
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
                # Geen fouten - schrijf over E-G (merged)
                ws_dash.merge_range(
                    f"E{table_subheader_row + 2}:G{table_subheader_row + 2}",  # Na subheader, E-G merged (was D-F)
                    "Geen fouten gevonden",
                    fmt_error_table_cell
                )
                table_end_row = table_subheader_row + 1

            # --- Ontbrekende verplichte kolommen in Kolom D --- #
            # Definieer formats als echte tabel headers (rood met witte letters)
            fmt_missing_col_header = workbook.add_format(
                {'bold': True, 'font_color': 'white', 'font_size': 12, 'bg_color': '#D32F2F', 'border': 1} # Zelfde stijl als hoofdheaders
            )
            fmt_missing_col_item = workbook.add_format(
                {'color': '#000000', 'bg_color': '#F2DCDB', 'font_size': 12, 'border': 1, 'align': 'left'} # Stijl zoals Actiepunten data
            )

            # Gebruik table_end_row (einde van Foutmeldingen tabel) voor aandachtspunten positionering
            col_d_end_row = table_end_row  # Voor aandachtspunten positionering

            # --- RECHTER KANT: Aandachtspunten onder Foutmeldingen (D-K) ---
            attention_start_row = col_d_end_row + 1  # 1 witte regel onder Foutmeldingen

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
                    if isinstance(item, dict):
                        msg = item.get("message", str(item))
                        code = item.get("code", "")
                    else:
                        # Backward compatibility - als het nog een string is
                        msg = str(item)
                        code = ""
                    # Vaste rijhoogte voor alle Aandachtspunten regels
                    ws_dash.set_row(current_attention_row, 16)

                    # Schrijf bericht over kolommen E-J (laat K vrij voor foutcode, was D-I)
                    ws_dash.merge_range(
                        f"E{current_attention_row+1}:J{current_attention_row+1}",
                        f"{msg}",
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
                    ws_dash.write(
                        current_attention_row, 10,  # Kolom K (10, was 9)
                        code if code else "N/A",
                        fmt_code_item
                    )

                    current_attention_row += 1  # Ga naar de volgende rij
            else:
                # Geen meldingen: schrijf over kolom D-J
                ws_dash.set_row(current_attention_row, 16)  # Vaste hoogte 16pt
                ws_dash.merge_range(
                    f"D{current_attention_row+1}:J{current_attention_row+1}",  # D-J uniform
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
            for i, f in enumerate(ghx_mandatory_fields):
                row_num = bar_chart_row + 1 + i
                if f not in df.columns:
                    correct, error, empty, missing = 0, 0, 0, total_rows
                else:
                    filled = filled_counts.get(f, 0)
                    errors = corrected_errors.get(f, 0)
                    correct = max(0, filled - errors)
                    error = errors
                    empty = total_rows - filled
                    missing = 0
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

            # --- Grafieken Toevoegen ---
            # Bepaal de laatste rij van beide kanten (links: foutmeldingen, rechts: aandachtspunten)
            left_side_end_row = table_end_row  # Einde van foutmeldingen tabel
            right_side_end_row = attention_end_row  # Einde van aandachtspunten
            chart_start_row = max(left_side_end_row, right_side_end_row) + 4  # 4 voor echt 3 lege regels onder laatste tabel

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
            stacked_chart.set_title({"name": "Verplichte Velden Overzicht"})
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
                    "align": "center",
                    "valign": "vcenter",
                    "bg_color": "#f79645",
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
                "GHX TEMPLATE VALIDATIE RAPPORT",
                fmt_title,
            )  # Merge A1:B1
            ws_inleiding.set_row(current_row_intro, 40)  # Stel hoogte in voor titelrij
            current_row_intro = 1  # Start volgende blok op rij 4

            # Extra witregel VOOR het scoreblok (om het op rij 5 te laten beginnen)
            current_row_intro += 1

            # <<<<<< DE TWEEDE (FOUTE) DEFINITIE VAN fmt_title IS HIER VERWIJDERD >>>>>>

            # Score Uitleg - Gebruik dezelfde scores als in Config sheet en dashboard
            # Deze variabelen zijn al berekend eerder in de functie voor de dashboard badge
            score_int_uitleg = totale_score_display
            score_grade_uitleg = "A+" if totale_score_display >= 90 else "A" if totale_score_display >= 80 else "B" if totale_score_display >= 70 else "C" if totale_score_display >= 60 else "D"
            
            # Maak aparte formats voor mooiere opmaak
            fmt_score_title = workbook.add_format({
                'bold': True,
                'font_size': 14,
                'font_color': '#2E4B1A',
                'bg_color': '#E8F4E8',
                'border': 1,
                'border_color': '#2E4B1A',
                'align': 'left',
                'valign': 'vcenter',
                'text_wrap': True,
                'indent': 1
            })
            
            fmt_score_body = workbook.add_format({
                'font_size': 12,
                'font_color': '#000000',
                'bg_color': '#E2EFDA',  # Zelfde groen als A3/A4 
                'border': 1,
                'border_color': '#2E4B1A',
                'align': 'left',
                'valign': 'top',
                'text_wrap': True,
                'indent': 1
            })
            
            # Titel apart (bold en groot)
            score_title = f"KWALITEITSSCORE: {score_int_uitleg}/100 ({score_grade_uitleg})"
            
            # Body tekst (meer uitgebreid maar gestructureerd)
            score_body_tekst = f"""Deze score wordt berekend op basis van vier componenten:

VOLLEDIGHEID ({volledigheids_score_display}/40 punten)
Gebaseerd op aanwezige verplichte kolommen: {M_found} van {len(ghx_mandatory_fields)} ({(M_found/len(ghx_mandatory_fields)*100):.0f}%)

KWALITEIT ({kwaliteits_score_display}/45 punten)
Gebaseerd op juistheid van data-invulling: {juistheid_percentage:.1f}% correcte waarden

TEMPLATE ({template_score_display}/10 punten)
{"Template herkenning: Juiste GHX velden gevonden" if template_score_display > 0 else "Template herkenning: Onvoldoende GHX velden"}

VERSIE ({versie_score_display}/5 punten)
{"Nieuwste template versie gedetecteerd" if versie_score_display == 5 else "Oudere template versie gedetecteerd" if versie_score_display > 0 else "Template versie onbekend"}

Cijfertoekenning: A+ (90+), A (80-89), B (70-79), C (60-69), D (<60)"""
            # Titel (bold en groot) - 2 rijen
            ws_inleiding.merge_range(
                f"A{current_row_intro+1}:B{current_row_intro + 2}",
                score_title,
                fmt_score_title,
            )
            current_row_intro += 3  # 2 rijen titel + 1 witregel
            
            # Body tekst (uitgebreider) - meer ruimte
            ws_inleiding.merge_range(
                f"A{current_row_intro+1}:B{current_row_intro + 18}",
                score_body_tekst,
                fmt_score_body,
            )
            current_row_intro += 18

            # Witregel
            current_row_intro += 1

            # Bestandsnaam
            ws_inleiding.write(
                f"A{current_row_intro+1}",
                f"VALIDATIE RAPPORT: {bestandsnaam}",
                fmt_filename,
            )
            current_row_intro += 1

            # Witregel
            current_row_intro += 1

            # Introductie tekst
            ws_inleiding.write(
                f"A{current_row_intro+1}", "Geachte leverancier,", fmt_standard
            )  # Met indent 2
            current_row_intro += 1
            ws_inleiding.write(
                f"A{current_row_intro+1}",
                "Hartelijk dank voor de aangeleverde GHX-prijslijsttemplate. Wij hebben uw gegevens ontvangen en in dit rapport vindt u de meest relevante validaties, aandachtspunten en verbeteropties.",
                fmt_standard,
            )  # Met indent 2
            current_row_intro += 1

            # Witregel
            current_row_intro += 1

            # Belangrijkste Punten
            # Zorg dat deze variabelen bestaan: total_rows, total_original_cols
            ws_inleiding.write(
                f"A{current_row_intro+1}",
                "Hieronder vindt u een overzicht van de belangrijkste punten:",
                fmt_section_header,
            )  # Bold, geen indent
            current_row_intro += 1
            ws_inleiding.write(
                f"A{current_row_intro+1}",
                f"• Aantal rijen in de dataset: {total_rows}",
                fmt_standard,
            )  # Met indent 2
            current_row_intro += 1
            ws_inleiding.write(
                f"A{current_row_intro+1}",
                f"• Aantal kolommen in de dataset: {total_original_cols}",
                fmt_standard,
            )  # Met indent 2
            current_row_intro += 1

            # Witregel
            current_row_intro += 1

            # Kolommen
            # Zorg dat deze variabelen bestaan: M_found, M_missing, missing_mandatory_columns
            ws_inleiding.write(
                f"A{current_row_intro+1}", "KOLOMMEN:", fmt_section_header
            )  # Bold, geen indent
            current_row_intro += 1
            ws_inleiding.write(
                f"A{current_row_intro+1}",
                f"- Aantal aanwezige verplichte kolommen: {M_found}",
                fmt_standard,
            )  # Met indent 2
            current_row_intro += 1
            ws_inleiding.write(
                f"A{current_row_intro+1}",
                f"- Aantal ontbrekende verplichte kolommen: {M_missing}",
                fmt_standard,
            )  # Met indent 2
            current_row_intro += 1
            if M_missing > 0:
                missing_cols_list = "\n".join(
                    [f"  - {c}" for c in missing_mandatory_columns]
                )
                ws_inleiding.write(
                    f"A{current_row_intro+1}",
                    f"De ontbrekende verplichte kolommen zijn:\n{missing_cols_list}",
                    fmt_standard,
                )  # Met indent 2
                current_row_intro += missing_cols_list.count("\n") + 1
                ws_inleiding.write(
                    f"A{current_row_intro+1}",
                    "We verzoeken u deze kolommen ook aan te leveren.",
                    fmt_standard,
                )  # Met indent 2
                current_row_intro += 1

            # Witregel
            current_row_intro += 1

            # Velden
            # Zorg dat deze variabelen bestaan: perc_verpl_gevuld, percentage_incorrect_of_filled_present,
            # M_found, total_rows, total_filled_in_present, empty_in_present
            ws_inleiding.write(
                f"A{current_row_intro+1}", "VELDEN:", fmt_section_header
            )  # Bold, geen indent
            current_row_intro += 1
            ws_inleiding.write(
                f"A{current_row_intro+1}",
                f"Van de aanwezige GHX-verplichte velden is {perc_verpl_gevuld:.2f}% gevuld,",
                fmt_standard,
            )  # Met indent 2
            current_row_intro += 1
            ws_inleiding.write(
                f"A{current_row_intro+1}",
                f"waarvan {percentage_incorrect_of_filled_present:.2f}% onjuist is ingevuld.",
                fmt_standard,
            )  # Met indent 2
            current_row_intro += 1
            ws_inleiding.write(
                f"A{current_row_intro+1}",
                f"• Aantal aanwezige verplichte velden: {M_found * total_rows}",
                fmt_standard,
            )  # Met indent 2
            current_row_intro += 1
            ws_inleiding.write(
                f"A{current_row_intro+1}",
                f"• Aantal daadwerkelijk gevulde verplichte velden: {total_filled_in_present}",
                fmt_standard,
            )  # Met indent 2
            current_row_intro += 1
            ws_inleiding.write(
                f"A{current_row_intro+1}",
                f"• Aantal lege verplichte velden: {empty_in_present}",
                fmt_standard,
            )  # Met indent 2
            current_row_intro += 1

            # Witregel
            current_row_intro += 1

            # Rapport Onderdelen
            ws_inleiding.write(
                f"A{current_row_intro+1}",
                "De rest van dit rapport gaat dieper in op alle validaties en de plekken waar er verbeteringen mogelijk zijn.",
                fmt_standard,
            )  # Met indent 2
            current_row_intro += 1
            ws_inleiding.write(
                f"A{current_row_intro+1}",
                "Dit rapport bestaat uit de volgende onderdelen:",
                fmt_section_header,
            )  # Bold, geen indent
            current_row_intro += 1
            rapport_onderdelen = [
                "1. Dashboard\n   Toont de belangrijkste statistieken en aandachtspunten in één oogopslag, inclusief grafieken en tabellen voor snelle analyse.",
                "2. Inleiding\n   Biedt een overzicht van het validatierapport, inclusief belangrijke statistieken zoals het aantal rijen en kolommen in de dataset, evenals een samenvatting van de voornaamste bevindingen en aandachtspunten.",
                "3. Verplichte Fouten\n   Bevat een gedetailleerde lijst van alle aangetroffen fouten in verplichte velden.",
                "4. Verplichte %\n   Toont statistieken over de volledigheid van de verplichte velden.",
                "5. Optionele Fouten\n   Bevat een overzicht van fouten die zijn gevonden in optionele velden.",
                "6. Optionele %\n   Presenteert statistieken over de volledigheid van de optionele velden.",
                "7. Database Aanpassing\n   Hier leest u welke correcties GHX automatisch doorvoert op sommige aangeleverde data. Dit gebeurt om de data toch te kunnen verwerken. Het is belangrijk dat u hiervan op de hoogte bent, omdat we naar een strenger validatieproces gaan waarbij deze data in de toekomst mogelijk wordt afgekeurd.\n\nOnderstaande tabel toont de automatische aanpassingen die zijn toegepast op basis van de gevonden fouten in uw aanlevering. Probeer deze punten te corrigeren in toekomstige uploads.",
                "8. Kolom Mapping\n   Geeft een overzicht van de mapping tussen de standaard GHX-kolomnamen en de originele kolomnamen van uw organisatie.",
                "9. Dataset Validatie\n   Toont een visueel overzicht van de volledige dataset met kleurcodering voor correcte, foutieve en lege velden.",
            ]
            for onderdeel in rapport_onderdelen:
                ws_inleiding.write(
                    f"A{current_row_intro+1}", onderdeel, fmt_standard
                )  # Met indent 2
                # GEEN rijhoogte aanpassing meer
                current_row_intro += 1  # Ga alleen naar volgende rij
                # GEEN extra witregel meer

            # Link Template
            ws_inleiding.write(
                f"A{current_row_intro+1}",
                "We vragen u om altijd gebruik te maken van de nieuwste versie van de GHX-template, welke te downloaden is via de volgende link:",
                fmt_standard,
            )  # Met indent 2
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

            # Slot
            ws_inleiding.write(
                f"A{current_row_intro+1}",
                "Wij verzoeken u vriendelijk eventuele fouten te corrigeren, ontbrekende informatie aan te vullen, en volledig lege verplichte kolommen te voorzien van data, zodat de prijslijst succesvol kan worden verwerkt.",
                fmt_standard,
            )  # Met indent 2
            current_row_intro += 1
            current_row_intro += 1  # Witregel
            ws_inleiding.write(
                f"A{current_row_intro+1}", "Met vriendelijke groet,", fmt_standard
            )  # Met indent 2
            current_row_intro += 1
            current_row_intro += 1  # Witregel
            ws_inleiding.write(
                f"A{current_row_intro+1}", "GHX", fmt_standard
            )  # Met indent 2
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
                df_errors_mand_sheet["Type"] = df_errors_mand_sheet["Foutcode"].apply(get_error_category)
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
                ws_mand_err.set_column(4, 4, 70)  # Foutmelding
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
                
                # Voeg Type kolom toe
                df_errors_non_mand_sheet["Type"] = df_errors_non_mand_sheet["Foutcode"].apply(get_error_category)
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
                ws_opt_err.set_column(4, 4, 70)  # Foutmelding
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
            # START CODE VOOR SHEET 7: DATABASE AANPASSING
            # ==================================================================
            ws_db = workbook.add_worksheet("7. Database Aanpassing")
            suppress_excel_errors(ws_db)
            writer.sheets["7. Database Aanpassing"] = ws_db
            ws_db.set_column("A:A", 35)
            ws_db.set_column("B:B", 115)
            intro_db_text = """Database Aanpassingen\n\nGHX voert momenteel automatische correcties uit op sommige aangeleverde data. Dit gebeurt om de data toch te kunnen verwerken. Het is belangrijk dat u hiervan op de hoogte bent, omdat we naar een strenger validatieproces gaan waarbij deze data in de toekomst mogelijk wordt afgekeurd.\n\nOnderstaande tabel toont de automatische aanpassingen die zijn toegepast op basis van de gevonden fouten in uw aanlevering. Probeer deze punten te corrigeren in toekomstige uploads."""
            ws_db.merge_range(
                "A1:B1",
                intro_db_text,
                workbook.add_format(
                    {
                        "font_size": 11,
                        "text_wrap": True,
                        "align": "left",
                        "valign": "top",
                    }
                ),
            )  # Simpel format
            ws_db.set_row(0, 100)

            db_correction_data = []
            unique_corrections = set()
            all_field_names_with_errors = (
                set(df_errors["GHX Kolom"].unique()) if not df_errors.empty else set()
            )

            for field_name, field_config in config.get("fields", {}).items():
                if (
                    "database_corrections" in field_config
                    and field_name in all_field_names_with_errors
                ):
                    corrections = field_config["database_corrections"]
                    if isinstance(corrections, list):
                        for correction in corrections:
                            msg = correction.get("message", "")
                            if msg and (field_name, msg) not in unique_corrections:
                                db_correction_data.append(
                                    {"Veld": field_name, "Database Correctie": msg}
                                )
                                unique_corrections.add((field_name, msg))
                    elif isinstance(corrections, dict):
                        msg = corrections.get("message", "")
                        if msg and (field_name, msg) not in unique_corrections:
                            db_correction_data.append(
                                {"Veld": field_name, "Database Correctie": msg}
                            )
                            unique_corrections.add((field_name, msg))

            db_start_row = 3
            if db_correction_data:
                df_db_corrections = pd.DataFrame(db_correction_data)
                df_db_corrections.to_excel(
                    writer,
                    sheet_name="7. Database Aanpassing",
                    startrow=db_start_row,
                    index=False,
                )
                (max_row_db, max_col_db) = df_db_corrections.shape
                # Header format
                for c_idx, value in enumerate(df_db_corrections.columns.values):
                    ws_db.write(db_start_row, c_idx, value, fmt_header_orange)
                # Tabel stijl
                ws_db.add_table(
                    db_start_row,
                    0,
                    db_start_row + max_row_db,
                    max_col_db - 1,
                    {
                        "columns": [{"header": col} for col in df_db_corrections.columns],
                        "header_row": True,
                        "style": "Table Style Medium 1",
                    },
                )
            else:
                ws_db.write(
                    db_start_row,
                    0,
                    "Geen automatische database aanpassingen toegepast op basis van gevonden fouten.",
                    fmt_default_table,
                )

            # ==================================================================
            # EINDE CODE VOOR SHEET 7: DATABASE AANPASSING
            # ==================================================================

            # ==================================================================
            # START CODE VOOR SHEET 8: KOLOM MAPPING - NIEUWE SIMPELE IMPLEMENTATIE
            # ==================================================================
            ws_map = workbook.add_worksheet("8. Kolom Mapping")
            suppress_excel_errors(ws_map)
            writer.sheets["8. Kolom Mapping"] = ws_map
            
            # Simpele aanpak: gebruik direct de mapping informatie die we hebben
            mapping_data_map = []
            mapped_originals = set()
            
            # 1. Toon alle succesvol gemapte headers
            for ghx_header, original_header in original_column_mapping.items():
                mapping_data_map.append({
                    "GHX Header": ghx_header,
                    "Supplier Header": original_header,
                })
                # Normaliseer originele header voor vergelijking
                from .price_tool import normalize_template_header
                normalized_original = normalize_template_header(original_header)
                mapped_originals.add(normalized_original)
            
            # 2. Toon verplichte velden die ontbreken
            if not validation_config:
                print("WARNING: validation_config is None, kan Sheet 8 niet volledig genereren.")
            else:
                # Check voor v20 vs v18 structuur
                if "field_validations" in validation_config:
                    # v20 structuur
                    ghx_headers_in_config = list(validation_config.get("field_validations", {}).keys())
                else:
                    # v18 structuur (fallback)  
                    ghx_headers_in_config = list(validation_config.get("fields", {}).keys())
                
                for ghx_header in ghx_headers_in_config:
                    if ghx_header in ghx_mandatory_fields and ghx_header not in original_column_mapping:
                        mapping_data_map.append({
                            "GHX Header": ghx_header,
                            "Supplier Header": "--- ONTBREKEND (VERPLICHT) ---",
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
            # EINDE CODE VOOR SHEET 8: KOLOM MAPPING
            # ==================================================================

            # ==================================================================
            # START CODE VOOR SHEET 9: DATASET VALIDATIE
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
            )

            # ==================================================================
            # EINDE CODE VOOR SHEET 9: DATASET VALIDATIE
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

        print(f"Validatierapport succesvol gegenereerd (in functie): '{output_path}'")
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
        print(
            f"FOUT (KeyError) bij genereren rapport: Kolom '{e}' niet gevonden. Controleer data of mapping."
        )
        # print("Beschikbare kolommen in df_errors:", df_errors.columns.tolist() if not df_errors.empty else "df_errors is leeg")
        # print("Beschikbare kolommen in df:", df.columns.tolist())
        return None  # Geef None terug bij fout
    except Exception as e:
        print(f"Algemene FOUT bij genereren rapport: {e}")
        import traceback

        traceback.print_exc()  # Print volledige traceback voor debuggen
        return None  # Geef None terug bij fout


# --- streamlit run prijslijst_validatie_app.py ----
