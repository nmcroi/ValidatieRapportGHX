# rapport_utils.py

import pandas as pd
import logging
import os
import json
import xlsxwriter  # Nodig voor pd.ExcelWriter engine en grafieken
from datetime import datetime
from typing import Dict, List, Tuple, Any  # Type hints zijn goed om te behouden

# --- Configuratie Constanten (Vervangen globale variabelen uit notebook) ---
# Deze kunnen later eventueel uit een centraal config bestand of env variabelen komen

# Configuratie voor validatie-overzichtsbestand (uit notebook Config cel)
ENABLE_VALIDATION_LOG = True  # True = logging aan, False = logging uit
# BELANGRIJK: Pas dit pad aan naar de *daadwerkelijke* locatie waar het logboek moet komen
# in de omgeving waar de code draait! Een hardcoded pad is meestal niet ideaal.
# Voor nu nemen we het pad uit je notebook over als voorbeeld.
VALIDATION_LOG_FILE = "/data/lucee/tomcat/webapps/ROOT/synqeps/webroot/upload/validatiePL_reports/validaties_overzicht.xlsx"


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

    # Bereken extra statistieken
    score = f"{template_type}{present_columns_count}.{percentage_correct}"
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
):
    """Voeg een sheet toe met de volledige dataset in kleurcodering."""
    # ### AANGEPAST: Gebruik de load_validation_config binnen deze module ###
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

        # Formaten
        correct_format = workbook.add_format(
            {"bg_color": "#FFFFFF", "border": 1, "border_color": "#D3D3D3"}
        )
        error_format = workbook.add_format(
            {"bg_color": "#FF4500", "border": 1, "border_color": "#B22222"}
        )  # Was OranjeRood, nu meer rood
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

        # Legenda
        worksheet.write("A1", "Legenda:", workbook.add_format({"bold": True}))
        worksheet.write(
            "A2", "Correct/Optioneel leeg", correct_format
        )  # Aangepast label
        worksheet.write("A3", "Foutief ingevuld", error_format)
        worksheet.write(
            "A4", "Verplicht veld leeg", empty_mandatory_format
        )  # Aangepast label
        worksheet.write("A5", "UOM-relatie conflict", uom_relation_error_format)
        start_row = 6

        # Maak error lookups
        error_lookup = {}  # Voor normale fouten
        uom_relation_error_lookup = {}  # Voor code 97 fouten

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
                    lookup_dict = (
                        uom_relation_error_lookup
                        if error_code == "97"
                        else error_lookup
                    )
                    if row_idx not in lookup_dict:
                        lookup_dict[row_idx] = set()
                    lookup_dict[row_idx].add(col_idx)

        # Schrijf headers
        for col, header in enumerate(df.columns):
            worksheet.write(start_row, col, str(header), header_format)

        # Schrijf data met kleuren (limiteer rijen)
        max_rows_sheet = min(len(df), ERROR_LIMIT)  # Gebruik limiet
        if len(df) > max_rows_sheet:
            worksheet.write(
                start_row - 2,
                0,
                f"LET OP: Weergave beperkt tot de eerste {max_rows_sheet} rijen.",
                workbook.add_format({"bold": True, "color": "red"}),
            )

        for row_idx in range(max_rows_sheet):
            for col_idx, field_name in enumerate(df.columns):
                value = df.iloc[row_idx, col_idx]
                value_str = "" if pd.isna(value) else str(value).strip()
                is_empty = value_str == ""

                is_mandatory = field_name in ghx_mandatory_fields

                # Dependency check (vereenvoudigd uit Code 5)
                has_dependency = False
                if is_empty and field_name in config["fields"]:
                    field_config = config["fields"][field_name]
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
                elif row_idx in error_lookup and col_idx in error_lookup[row_idx]:
                    cell_format = error_format
                elif is_empty and (is_mandatory or has_dependency):
                    cell_format = empty_mandatory_format

                # Schrijf waarde met bepaalde opmaak
                worksheet.write(
                    start_row + row_idx + 1, col_idx, value_str, cell_format
                )

        # Stel kolombreedte in (voorbeeld)
        worksheet.set_column(0, len(df.columns) - 1, 20)

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
        # Helper functie voor schone headers
        def clean_header(header):
            return str(header).split("\n")[0].strip()

        # Bestandsnaam zonder extensie voor output naamgeving
        bestandsnaam_zonder_extensie = os.path.splitext(bestandsnaam)[0]

        # --- Data Voorbereiding & Berekeningen (Begin) ---
        total_rows = len(df)
        total_cols = len(df.columns)  # Kolommen in verwerkte df
        total_original_cols = len(df_original.columns)  # Kolommen in origineel bestand

        config = load_validation_config(JSON_CONFIG_PATH)
        if not config:
            print("FOUT: Kan rapport niet genereren zonder validatie configuratie.")
            return None

        non_mandatory_fields = [
            f for f in config.get("fields", {}) if f not in ghx_mandatory_fields
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

        # Score berekening
        template_type = (
            "N"
            if M_missing == 0
            and all(
                f in df.columns
                for f in ["Is BestelbareEenheid", "Omschrijving Verpakkingseenheid"]
            )
            else "O"
        )

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
        score_suffix = f"_{template_type}{M_found}.{percentage_correct}"

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
                    "font_size": 12,
                    "font_color": "#006100",
                    "bg_color": "#C6EFCE",
                    "border": 1,
                    "valign": "vcenter",
                }
            )
            fmt_header_red = workbook.add_format(
                {
                    "bold": True,
                    "font_size": 12,
                    "font_color": "#9C0006",
                    "bg_color": "#FFC7CE",
                    "border": 1,
                    "valign": "vcenter",
                }
            )
            fmt_header_blue = workbook.add_format(
                {
                    "bold": True,
                    "font_size": 12,
                    "font_color": "#FFFFFF",
                    "bg_color": "#4F81BD",
                    "border": 1,
                    "align": "left",
                    "valign": "vcenter",
                }
            )
            fmt_label_green = workbook.add_format(
                {"font_size": 12, "bg_color": "#E2EFDA", "border": 1, "indent": 1}
            )
            fmt_value_green = workbook.add_format(
                {
                    "font_size": 12,
                    "bg_color": "#E2EFDA",
                    "border": 1,
                    "align": "right",
                    "num_format": "#,##0",
                }
            )
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
                    "font_size": 12,
                    "bg_color": "#D9D9D9",
                    "border": 1,
                    "align": "left",
                }
            )
            fmt_error_table_cell = workbook.add_format({"font_size": 12, "border": 1})
            fmt_error_table_code = workbook.add_format(
                {"font_size": 12, "border": 1, "align": "right"}
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
                    "font_size": 12,
                }
            )  # Voor andere tabellen

            # ==================================================================
            # START CODE VOOR SHEET 1: DASHBOARD
            # ==================================================================
            ws_dash = workbook.add_worksheet("1. Dashboard")
            writer.sheets["1. Dashboard"] = ws_dash
            # Verberg rij 1
            ws_dash.set_row(0, None, None, {"hidden": True})  # Verberg rij 1 (index 0)

            # --- Kolombreedtes Instellen ---
            ws_dash.set_column("A:A", 130)
            ws_dash.set_column("B:B", 8)
            ws_dash.set_column("C:C", 5)
            ws_dash.set_column("D:D", 75)
            ws_dash.set_column(
                "E:E",
            )
            ws_dash.set_column("F:F", 18)
            ws_dash.set_column("G:G", 8)
            # Kolom H en verder eventueel voor grafieken rechts

            # --- Start direct met Blok 1 op rij 3 ---
            current_row = 2  # Start schrijven op rij 3 (0-based index 2)
            ws_dash.merge_range(
                f"A{current_row+1}:B{current_row+1}",
                "Belangrijkste Statistieken",
                fmt_header_green,
            )
            ws_dash.set_row(current_row, 18)  # Hoogte header rij
            current_row += 1  # Ga naar de volgende rij voor de data
            ws_dash.set_row(current_row, 18)
            aantal_velden_totaal = total_rows * total_original_cols
            aantal_aanw_verpl_velden = M_found * total_rows
            aantal_afw_verpl_velden = M_missing * total_rows
            aantal_aanw_lege_verpl_velden = empty_in_present

            stats_data_original = [
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
            ]
            for key, value in stats_data_original:
                ws_dash.write_string(f"A{current_row+1}", key, fmt_label_green)
                ws_dash.write_number(f"B{current_row+1}", value, fmt_value_green)
                current_row += 1
            stats_end_row = current_row

            # --- Blok 2: Belangrijkste Actiepunten (Rood) ---
            current_row += 2  # Witregel tussen blokken
            action_start_row = current_row
            ws_dash.merge_range(
                f"A{current_row+1}:B{current_row+1}",
                "Belangrijkste Actiepunten",
                fmt_header_red,
            )
            ws_dash.set_row(current_row, 18)
            current_row += 1
            actions_data_original = [  # <<< CORRECTE INSPRINGING
                (
                    "Aantal lege verplichte velden (incl. ontbrekende)",
                    aantal_leeg_incl_missing,
                ),
                (
                    "Percentage ingevulde verplichte velden (incl. ontbrekende)",
                    percentage_ingevuld_incl_missing / 100,
                ),  # Deel door 100 blijft
                ("Aantal ontbrekende verplichte kolommen", M_missing),
            ]

            # Definieer een basis format voor de rode waarden (zonder specifiek num_format)
            fmt_value_red_base = workbook.add_format(
                {"font_size": 12, "bg_color": "#F2DCDB", "border": 1, "align": "right"}
            )
            fmt_label_red = workbook.add_format(
                {"font_size": 12, "bg_color": "#F2DCDB", "border": 1, "indent": 1}
            )  # Zorg dat label format ook bestaat

            for key, value in actions_data_original:
                ws_dash.write_string(f"A{current_row+1}", key, fmt_label_red)
                # Controleer of het de percentage regel is
                if "Percentage" in key:  # Check op woord 'Percentage' is robuuster
                    # Formatteer de waarde als string met 2 decimalen en % teken
                    # value bevat al waarde / 100, dus * 100 voor weergave
                    value_str = f"{value * 100:.2f}%"
                    # Schrijf deze string naar de cel met het basis rode format
                    ws_dash.write_string(
                        f"B{current_row+1}", value_str, fmt_value_red_base
                    )  # <-- Gebruik write_string!
                else:
                    # Schrijf andere waarden als getal met het basis rode format
                    ws_dash.write_number(f"B{current_row+1}", value, fmt_value_red_base)
                current_row += 1
            action_end_row = current_row

            # --- Blok 3: Aandachtspunten (Rood) ---
            # Ga één rij verder na het vorige blok.
            current_row += 2
            attention_start_row = current_row  # Startrij voor header

            # Schrijf header voor Aandachtspunten (merged over A:B)
            ws_dash.merge_range(
                f"A{attention_start_row+1}:B{attention_start_row+1}",
                "Aandachtspunten",
                fmt_header_red,
            )
            ws_dash.set_row(attention_start_row, 18)  # Header hoogte
            current_row += 1  # Ga naar de rij onder de header

            # Format met RODE rand, font size (aanpassen?), wrap, etc.
            fmt_attention_item = workbook.add_format(
                {
                    "font_size": 12,  # <<<<<<< Zet eventueel op 12
                    "bg_color": "#F2DCDB",  # Licht rood
                    "border": 1,  # Rand rondom de hele cel
                    "text_wrap": True,  # Zorg dat tekst terugloopt
                    "align": "left",
                    "valign": "top",
                    "indent": 1,
                }
            )

            # Controleer of er aandachtspunten zijn
            if red_flag_messages:
                # Loop door elke individuele melding
                for msg in red_flag_messages:
                    # Schat aantal benodigde regels (100 tekens/regel)
                    estimated_lines = max(1, len(msg) // 100 + msg.count("\n"))

                    # Stel hoogte in: 32pt als > 1 regel nodig, anders 16pt
                    if estimated_lines > 1:
                        ws_dash.set_row(
                            current_row, 32
                        )  # Vaste hoogte (32pt) voor lange tekst
                    else:
                        ws_dash.set_row(
                            current_row, 16
                        )  # Vaste hoogte (16pt) voor korte tekst

                    # Merge cellen A en B en schrijf de tekst
                    ws_dash.merge_range(
                        f"A{current_row+1}:B{current_row+1}",
                        f"{msg}",
                        fmt_attention_item,
                    )

                    current_row += 1  # Ga naar de volgende rij voor de volgende melding
            else:
                # Geen meldingen: ook hier vaste hoogte 16 en rode randen A-G
                ws_dash.set_row(current_row, 16)  # Vaste hoogte 16pt
                ws_dash.merge_range(
                    f"A{current_row+1}:B{current_row+1}",
                    "Geen specifieke aandachtspunten gevonden.",
                    fmt_attention_item,
                )
                # Schrijf ook hier blanco cellen C t/m G met de rode border
                for col_idx in range(2, 7):
                    ws_dash.write_blank(current_row, col_idx, None, fmt_attention_item)
                current_row += 1

            # Onthoud de laatst gebruikte rij-index (0-based)
            attention_end_row = current_row - 1
            col_d_end_row = attention_end_row  # Initialize col_d_end_row here
            # --- Einde Blok 3 ---

            # --- Blok 4: Fout Meldingen Tabel (Blauw, D3:Gxx) ---
            table_start_row = 2
            ws_dash.merge_range(
                f"D{table_start_row+1}:G{table_start_row+1}",
                "Fout Meldingen",
                fmt_header_blue,
            )
            ws_dash.set_row(table_start_row, 18)

            error_code_desc = config.get("error_code_descriptions", {})
            if "97" not in error_code_desc:
                error_code_desc["97"] = "UOM-relatie conflict"
            if "94" not in error_code_desc:
                error_code_desc["94"] = (
                    "Formaat Omschrijving Verp.eenheid (Waarschuwing)"
                )

            df_foutcodes_top = pd.DataFrame()
            table_end_row = table_start_row + 1  # Default end row
            if not df_errors.empty:
                # Check of 'code' kolom bestaat voor we verder gaan
                if "code" in df_errors.columns:
                    # Simpel: groepeer alle fouten alleen op code, net als in het notebook
                    df_foutcodes = df_errors.groupby("code").size().reset_index(name="Aantal")
                    
                    # Filter lege codes uit
                    df_foutcodes = df_foutcodes[df_foutcodes["code"] != ""]
                    
                    # Maak beschrijving op basis van de foutcode
                    df_foutcodes["Beschrijving"] = df_foutcodes["code"].apply(
                        lambda x: error_code_desc.get(str(x).strip(), f"Code: {x}")
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
                    df_foutcodes = df_foutcodes.sort_values(
                        "Aantal", ascending=False
                    ).reset_index(drop=True)
                    df_foutcodes_top = df_foutcodes.head(10)
                    # Herschik en hernoem kolommen pas na het berekenen van Type (Sheet)
                    df_foutcodes_top = df_foutcodes_top[
                        ["Beschrijving", "Aantal", "Type (Sheet)", "code"]
                    ]
                    df_foutcodes_top = df_foutcodes_top.rename(
                        columns={"code": "Foutcode"}
                    )

                    table_header_row = table_start_row + 1
                    # Schrijf header
                    for c_idx, col_name in enumerate(df_foutcodes_top.columns):
                        ws_dash.write(
                            table_header_row,
                            3 + c_idx,
                            col_name,
                            fmt_error_table_header,
                        )
                    # Schrijf data
                    for r_idx, row_data in df_foutcodes_top.iterrows():
                        current_table_row = table_header_row + 1 + r_idx
                        for c_idx, cell_value in enumerate(row_data):
                            fmt = (
                                fmt_error_table_code
                                if df_foutcodes_top.columns[c_idx] == "Foutcode"
                                else fmt_error_table_cell
                            )
                            try:
                                # Probeer integer te maken voor Aantal en Foutcode voor juiste weergave/sortering
                                if df_foutcodes_top.columns[c_idx] in [
                                    "Aantal",
                                    "Foutcode",
                                ]:
                                    num_val = int(cell_value)
                                    ws_dash.write_number(
                                        current_table_row, 3 + c_idx, num_val, fmt
                                    )
                                else:
                                    ws_dash.write_string(
                                        current_table_row,
                                        3 + c_idx,
                                        str(cell_value),
                                        fmt,
                                    )
                            except (
                                ValueError,
                                TypeError,
                            ):  # Fallback naar string als conversie mislukt
                                ws_dash.write_string(
                                    current_table_row, 3 + c_idx, str(cell_value), fmt
                                )
                    table_end_row = table_header_row + len(df_foutcodes_top)
                else:
                    ws_dash.write(
                        table_start_row + 1,
                        3,
                        "'code' kolom mist in validatieresultaten.",
                        fmt_error_table_cell,
                    )
                    table_end_row = table_start_row + 1
            else:
                ws_dash.write(
                    table_start_row + 1, 3, "Geen fouten gevonden", fmt_error_table_cell
                )
                table_end_row = table_start_row + 1

            # --- Ontbrekende verplichte kolommen in Kolom D --- #
            # Definieer formats lijkend op 'Actiepunten' blok
            fmt_missing_col_header = workbook.add_format(
                {'bold': True, 'color': '#C00000', 'font_size': 12, 'bg_color': '#FFC7CE', 'border': 1} # Stijl zoals Actiepunten header
            )
            fmt_missing_col_item = workbook.add_format(
                {'color': '#000000', 'bg_color': '#F2DCDB', 'font_size': 12, 'border': 1, 'align': 'left'} # Stijl zoals Actiepunten data
            )

            # Controleer of er ontbrekende verplichte kolommen zijn
            if M_missing > 0:
                # Bepaal de eindrij van de vorige tabel (Foutmeldingen Samenvatting)
                # De tabel start op 'startrow_err_sum' en heeft 'max_row_err_sum' datarijen
                table_end_row = table_start_row + len(df_foutcodes_top) # Index van laatste rij
                # Bepaal startrij voor de nieuwe lijst in kolom D (minimaal rij 12 = index 11)
                col_d_start_row = action_start_row

                #HIER!!!

                # Schrijf de header
                ws_dash.write(col_d_start_row, 3, "Ontbrekende verplichte kolommen", fmt_missing_col_header)
                # Schrijf de kolomnamen
                current_col_d_row = col_d_start_row + 1
                for col_name in missing_mandatory_columns:
                    ws_dash.write(current_col_d_row, 3, f"{col_name}", fmt_missing_col_item)
                    ws_dash.set_row(current_col_d_row, 18) # Match hoogte Actiepunten rij
                    current_col_d_row += 1
                col_d_end_row = current_col_d_row - 1


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
            chart_start_row = max(attention_end_row, col_d_end_row) + 3

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
            stacked_chart.set_size({"width": 950, "height": 500})
            ws_dash.insert_chart(f"A{chart_start_row + 1}", stacked_chart)

            # Grafiek 2: Donut Verplichte Velden
            donut_chart_mand = workbook.add_chart({"type": "doughnut"})

            # Bepaal dynamisch de categorieën, waarden en punten voor de donut chart
            # op basis van de telling voor 'Kolom niet aanwezig'
            count_not_present_mand = summary_data['counts_mandatory'].get('not_present', 0)

            # Standaardinstellingen (alsof alle 4 categorieën aanwezig zijn)
            categories_end_row_mand = donut_mand_row + 4
            values_end_row_mand = donut_mand_row + 4
            chart_points_mand = [
                {"fill": {"color": colors[1]}},  # Juist ingevuld
                {"fill": {"color": colors[2]}},  # Foutief ingevuld
                {"fill": {"color": colors[3]}},  # Leeg
                {"fill": {"color": colors[4]}},  # Kolom niet aanwezig
            ]

            # Als 'Kolom niet aanwezig' 0 is, pas de ranges en punten aan
            if count_not_present_mand == 0:
                categories_end_row_mand = donut_mand_row + 3  # Neem 3 categorieën
                values_end_row_mand = donut_mand_row + 3      # Neem 3 waarden
                chart_points_mand = chart_points_mand[:-1]    # Verwijder laatste kleurpunt

            donut_chart_mand.add_series(
                {
                    "name": f"Verplichte Velden Status ({total_donut_mand} velden)",
                    "categories": [
                        "1. Dashboard",
                        donut_mand_row + 1,
                        0,
                        categories_end_row_mand,  # Dynamische eindrij
                        0,
                    ],
                    "values": [
                        "1. Dashboard",
                        donut_mand_row + 1,
                        1,
                        values_end_row_mand,    # Dynamische eindrij
                        1,
                    ],
                    "points": chart_points_mand,       # Dynamische puntenlijst
                    "data_labels": {
                        "percentage": True,
                        "font": {"size": 11, "color": "white"},
                    },
                }
            )
            donut_chart_mand.set_title({"name": "Verplichte Velden"})
            donut_chart_mand.set_legend({"position": "bottom", "font": {"size": 11}})
            donut_chart_mand.set_size({"width": 500, "height": 500}) # Vaste grootte
            ws_dash.insert_chart(f"D{chart_start_row + 1}", donut_chart_mand)

            # Grafiek 3: Donut Alle Velden
            donut_chart_all = workbook.add_chart({"type": "doughnut"})
            donut_chart_all.add_series(
                {
                    "name": f"Alle Velden Status ({total_donut_all} velden)",
                    "categories": [
                        "1. Dashboard",
                        donut_all_row + 1,
                        0,
                        donut_all_row + 3,
                        0,
                    ],
                    "values": [
                        "1. Dashboard",
                        donut_all_row + 1,
                        1,
                        donut_all_row + 3,
                        1,
                    ],
                    "points": [
                        {"fill": {"color": colors[1]}},
                        {"fill": {"color": colors[2]}},
                        {"fill": {"color": colors[3]}},
                    ],  # Groen, Rood, Geel
                    "data_labels": {
                        "percentage": True,
                        "font": {"size": 11, "color": "white"},
                    },
                }
            )
            donut_chart_all.set_title(
                {"name": f"Alle Velden ({total_donut_all} velden)"}
            )
            donut_chart_all.set_legend({"position": "bottom", "font": {"size": 11}})
            donut_chart_all.set_size({"width": 500, "height": 500}) # Vaste, identieke grootte
            ws_dash.insert_chart(f"E{chart_start_row + 1}", donut_chart_all)

            # ==================================================================
            # START CODE VOOR SHEET 2: INLEIDING
            # ==================================================================
            ws_inleiding = workbook.add_worksheet("2. Inleiding")
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
                {"font_size": 12, "indent": 2, "bold": True}
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

            # Score Uitleg
            # Zorg dat deze variabelen bestaan vóór dit punt:
            # template_type, M_found, percentage_correct, volledigheids_percentage, juistheid_percentage, ghx_mandatory_fields
            score_uitleg_tekst = f"""SCORE: {template_type}{M_found}.{percentage_correct}%

Deze score bestaat uit drie onderdelen:
- {template_type}: Dit geeft aan of de Nieuwe (N) of Oude (O) GHX template wordt gebruikt
- {M_found}: Het aantal aanwezige verplichte kolommen (van de {len(ghx_mandatory_fields)} totaal)
- {percentage_correct}%: De kwaliteitsscore (volledigheid {volledigheids_percentage:.1f}% × juistheid {juistheid_percentage:.1f}%)"""
            ws_inleiding.merge_range(
                f"A{current_row_intro+1}:A{current_row_intro + 9}",
                score_uitleg_tekst,
                fmt_score,
            )
            current_row_intro += 9

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
                df_errors_mand_sheet = df_errors_mand_sheet.sort_values(
                    by=["Rij", "GHX Kolom"]
                )
                df_errors_mand_sheet = df_errors_mand_sheet.fillna(
                    ""
                )  # Vul NaN etc. met lege string

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
            ws_mand_perc.set_column(0, 0, 30)
            ws_mand_perc.set_column(1, 1, 30)
            ws_mand_perc.set_column(2, 2, 12)
            ws_mand_perc.set_column(3, 3, 18)  # Filled %
            ws_mand_perc.set_column(4, 4, 18)  # Fout %
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
            writer.sheets["5. Optionele Fouten"] = ws_opt_err
            if not df_errors_non_mand.empty and all(
                c in df_errors_non_mand.columns for c in required_cols_err
            ):
                df_errors_non_mand_sheet = df_errors_non_mand[required_cols_err].copy()
                df_errors_non_mand_sheet = df_errors_non_mand_sheet.rename(
                    columns={"code": "Foutcode"}
                )
                df_errors_non_mand_sheet = df_errors_non_mand_sheet.sort_values(
                    by=["Rij", "GHX Kolom"]
                )
                df_errors_non_mand_sheet = df_errors_non_mand_sheet.fillna("")
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
                ws_opt_err.set_column(0, 0, 8)
                ws_opt_err.set_column(1, 1, 30)
                ws_opt_err.set_column(2, 2, 30)
                ws_opt_err.set_column(3, 3, 45)
                ws_opt_err.set_column(4, 4, 70)
                ws_opt_err.set_column(5, 5, 10)
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

            if not df_percentages_non_mand_sheet.empty:
                df_percentages_non_mand_sheet.to_excel(
                    writer, sheet_name="6. Optionele %", index=False
                )
                ws_opt_perc.set_column(0, 0, 30)
                ws_opt_perc.set_column(1, 1, 30)
                ws_opt_perc.set_column(2, 2, 12)
                ws_opt_perc.set_column(3, 3, 18)  # Filled %
                ws_opt_perc.set_column(4, 4, 18)  # Fout %
                ws_opt_perc.set_column(5, 5, 20)  # Aantal Juist
                # Pas format toe
                # Stel alleen breedte in voor percentage kolommen (format komt van tabel stijl)
                ws_opt_perc.set_column(3, 4, 18)  # fmt_perc_table verwijderd
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
            # START CODE VOOR SHEET 8: KOLOM MAPPING
            # ==================================================================
            ws_map = workbook.add_worksheet("8. Kolom Mapping")
            writer.sheets["8. Kolom Mapping"] = ws_map
            # Bereken mapping_df zoals in vorige versie
            ghx_headers_in_config = list(config.get("fields", {}).keys())
            mapping_data_map = []
            mapped_supplier_headers_clean = set()
            for ghx_header in ghx_headers_in_config:
                supplier_header_original = original_column_mapping.get(ghx_header)
                supplier_header_clean = (
                    clean_header(supplier_header_original)
                    if supplier_header_original
                    else ""
                )
                if ghx_header in df.columns:
                    mapping_data_map.append(
                        {
                            "GHX Header": ghx_header,
                            "Supplier Header": supplier_header_clean,
                        }
                    )
                    if supplier_header_clean:
                        mapped_supplier_headers_clean.add(supplier_header_clean)
                elif ghx_header in ghx_mandatory_fields:
                    mapping_data_map.append(
                        {
                            "GHX Header": ghx_header,
                            "Supplier Header": "--- ONTBREKEND (VERPLICHT) ---",
                        }
                    )
            all_original_headers_clean = set(
                clean_header(col)
                for col in df_original.columns
                if not col.lower().startswith("algemeen")
            )
            unmapped_supplier_headers = (
                all_original_headers_clean - mapped_supplier_headers_clean
            )
            for sh in sorted(list(unmapped_supplier_headers)):
                mapping_data_map.append(
                    {
                        "GHX Header": "--- ONBEKEND / NIET GEMAPT ---",
                        "Supplier Header": sh,
                    }
                )
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
