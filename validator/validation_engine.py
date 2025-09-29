"""
Validation Engine Module

Deze module implementeert de kern validatie logica voor prijslijst validatie.
"""

import logging
import pandas as pd
import re
import os
from typing import Dict, Any, List, Tuple, Union, Optional


def validate_pricelist(input_excel_path: str, mapping_json_path: str, validation_json_path: str, 
                      original_input_filename: str, reference_json_path: str = None) -> Optional[str]:
    """
    Hoofd entry point voor prijslijst validatie.
    
    Args:
        input_excel_path: Pad naar input Excel bestand
        mapping_json_path: Pad naar header mapping JSON
        validation_json_path: Pad naar validatie regels JSON  
        original_input_filename: Originele bestandsnaam
        reference_json_path: Pad naar reference lists JSON
        
    Returns:
        Pad naar validatie rapport Excel bestand of None bij fout
    """
    try:
        logging.info(f"Starten prijslijst validatie voor: {original_input_filename}")
        
        # Laad configuraties
        from .config_manager import load_field_mapping
        from .template_detector import determine_template_type
        from .template_context import extract_template_generator_context
        from .data_processor import map_headers, clean_dataframe
        
        # Bepaal template type en context
        template_type = determine_template_type(input_excel_path)
        template_context = {
            'template_type': template_type,
            'excel_path': input_excel_path  # ✅ Excel pad toevoegen voor mandatory fields bepaling
        }
        
        if template_type == "TG":
            # Extraheer Template Generator context
            tg_context = extract_template_generator_context(input_excel_path)
            if tg_context:
                template_context.update(tg_context)
        
        # Laad field mapping configuratie
        field_mapping = load_field_mapping()
        if not field_mapping:
            raise Exception("Kon field mapping configuratie niet laden")
        
        # Laad Excel data
        df = pd.read_excel(input_excel_path)
        logging.info(f"Excel data geladen: {df.shape}")
        
        # Data processing
        df_cleaned = clean_dataframe(df)
        df_mapped, unmapped_columns, original_column_mapping = map_headers(
            df_cleaned, field_mapping
        )
        
        # Validatie uitvoeren
        validation_results, validation_stats, failed_rows, summary_stats = validate_dataframe(
            df_mapped, field_mapping, original_column_mapping, template_context
        )
        
        # Genereer rapport
        report_path = _generate_validation_report(
            validation_results, validation_stats, failed_rows, summary_stats,
            template_context, original_input_filename, unmapped_columns
        )
        
        logging.info(f"Prijslijst validatie voltooid: {len(validation_results)} fouten gevonden")
        return report_path
        
    except Exception as e:
        logging.error(f"Fout bij prijslijst validatie: {e}")
        return None


def validate_dataframe(df: pd.DataFrame, validation_config: Dict, original_column_mapping: Dict, 
                      template_context: Dict[str, Any] = None) -> Tuple[List, Dict, List, Dict]:
    """
    Valideert DataFrame tegen validatie regels.
    
    Args:
        df: DataFrame om te valideren
        validation_config: Validatie configuratie
        original_column_mapping: Mapping van GHX naar originele kolom namen
        template_context: Template context voor conditional validation
        
    Returns:
        Tuple van (validation_results, validation_stats, failed_rows, summary_stats)
    """
    try:
        logging.info(f"DataFrame validatie starten: {df.shape}")
        
        from .field_logic import should_validate_field
        from .mandatory_fields import determine_mandatory_fields_for_template
        
        validation_results = []
        validation_stats = {}
        failed_rows = []
        summary_stats = {
            'total_rows': len(df),
            'total_fields': len(df.columns),
            'validated_fields': 0,
            'total_errors': 0,
            'rows_with_errors': 0,
            'mandatory_field_errors': 0
        }
        
        # Bepaal mandatory fields voor dit template
        if template_context and 'excel_path' in template_context:
            excel_path = template_context['excel_path']
            mandatory_fields = determine_mandatory_fields_for_template(excel_path)
        else:
            # Fallback: gebruik basis mandatory fields
            from .mandatory_fields import get_fallback_mandatory_fields
            mandatory_fields = get_fallback_mandatory_fields()
        
        logging.info(f"Validatie met {len(mandatory_fields)} mandatory fields")
        
        # Filter mandatory fields to only those present in DataFrame
        present_mandatory_fields = [field for field in mandatory_fields if field in df.columns]
        missing_mandatory_fields = [field for field in mandatory_fields if field not in df.columns]
        
        logging.info(f"Mandatory fields: {len(mandatory_fields)} totaal, {len(present_mandatory_fields)} aanwezig, {len(missing_mandatory_fields)} ontbrekend")
        
        # Valideer elke rij
        rows_with_errors = set()
        
        for index, row in df.iterrows():
            row_errors = []
            
            # Valideer mandatory fields (alleen die aanwezig zijn)
            for field_name in present_mandatory_fields:
                if should_validate_field(field_name, template_context or {}):
                    field_errors = _validate_mandatory_field(
                        field_name, row.get(field_name), index + 1, 
                        validation_config.get('fields', {}).get(field_name, {})
                    )
                    row_errors.extend(field_errors)
                    if field_errors:
                        summary_stats['mandatory_field_errors'] += len(field_errors)
            
            # Valideer alle velden tegen regels
            for field_name in df.columns:
                if should_validate_field(field_name, template_context or {}):
                    summary_stats['validated_fields'] += 1
                    
                    # Get field config - check multiple possible keys
                    fields = validation_config.get('fields', {})
                    if not fields:
                        fields = validation_config.get('field_validations', {})
                    
                    field_config = fields.get(field_name, {})
                    field_errors = validate_field_v20_native(
                        field_name, row.get(field_name), field_config, 
                        [], {'row_index': index + 1}
                    )
                    row_errors.extend(field_errors)
            
            # Bewaar rij fouten
            if row_errors:
                validation_results.extend(row_errors)
                failed_rows.append({
                    'row_index': index + 1,
                    'errors': row_errors,
                    'error_count': len(row_errors)
                })
                rows_with_errors.add(index + 1)
        
        # Update statistieken
        summary_stats['total_errors'] = len(validation_results)
        summary_stats['rows_with_errors'] = len(rows_with_errors)
        
        # Validatie statistieken per veld
        field_error_counts = {}
        for error in validation_results:
            field_name = error.get('field', 'Unknown')
            field_error_counts[field_name] = field_error_counts.get(field_name, 0) + 1
        
        validation_stats['field_error_counts'] = field_error_counts
        validation_stats['mandatory_fields'] = present_mandatory_fields
        validation_stats['missing_mandatory_fields'] = missing_mandatory_fields
        validation_stats['total_mandatory_fields'] = mandatory_fields
        
        logging.info(f"DataFrame validatie voltooid: {len(validation_results)} fouten, "
                    f"{len(rows_with_errors)} rijen met fouten")
        
        return validation_results, validation_stats, failed_rows, summary_stats
        
    except Exception as e:
        logging.error(f"Fout bij DataFrame validatie: {e}")
        return [], {}, [], {'total_rows': len(df), 'total_errors': 0}


def validate_field_v20_native(field_name: str, value: Any, field_config: Dict, 
                             invalid_values: List, row_data: Dict = None, 
                             reference_lists: Dict = None) -> List:
    """
    Valideert een veld tegen V20 native configuratie.
    
    Args:
        field_name: Naam van het veld
        value: Waarde om te valideren
        field_config: V20 field configuratie
        invalid_values: Lijst van invalid waarden
        row_data: Extra rij data
        reference_lists: Reference lists voor lookup validatie
        
    Returns:
        Lijst van validatie fouten
    """
    try:
        errors = []
        
        if not isinstance(field_config, dict):
            return errors
        
        validation_rules = field_config.get('validation', {})
        if not validation_rules:
            return errors
        
        row_index = row_data.get('row_index', 0) if row_data else 0
        
        # Skip validatie voor lege waarden tenzij required
        if pd.isna(value) or str(value).strip() == '':
            if validation_rules.get('required', False):
                errors.append({
                    'field': field_name,
                    'row': row_index,
                    'error_type': 'required_field_missing',
                    'message': f"Verplicht veld '{field_name}' is leeg",
                    'value': value
                })
            return errors
        
        value_str = str(value).strip()
        
        # Data type validatie
        data_type = validation_rules.get('data_type', 'text')
        if not _validate_data_type(value_str, data_type):
            errors.append({
                'field': field_name,
                'row': row_index,
                'error_type': 'invalid_data_type',
                'message': f"Waarde '{value_str}' heeft niet het juiste data type ({data_type})",
                'value': value
            })
        
        # Min/max length validatie
        min_length = validation_rules.get('min_length')
        max_length = validation_rules.get('max_length')
        
        if min_length and len(value_str) < min_length:
            errors.append({
                'field': field_name,
                'row': row_index,
                'error_type': 'too_short',
                'message': f"Waarde '{value_str}' is te kort (min {min_length} karakters)",
                'value': value
            })
        
        if max_length and len(value_str) > max_length:
            errors.append({
                'field': field_name,
                'row': row_index,
                'error_type': 'too_long',
                'message': f"Waarde '{value_str}' is te lang (max {max_length} karakters)",
                'value': value
            })
        
        # Pattern validatie
        pattern = validation_rules.get('pattern')
        if pattern and not re.match(pattern, value_str):
            errors.append({
                'field': field_name,
                'row': row_index,
                'error_type': 'pattern_mismatch',
                'message': f"Waarde '{value_str}' voldoet niet aan het vereiste patroon",
                'value': value
            })
        
        # Reference list validatie
        reference_list = validation_rules.get('reference_list')
        if reference_list and reference_lists and reference_list in reference_lists:
            allowed_values = reference_lists[reference_list]
            if value_str not in allowed_values:
                errors.append({
                    'field': field_name,
                    'row': row_index,
                    'error_type': 'invalid_reference_value',
                    'message': f"Waarde '{value_str}' staat niet in toegestane waardenlijst",
                    'value': value
                })
        
        # Min/max value validatie (voor numerieke velden)
        if data_type in ['numeric', 'integer']:
            try:
                numeric_value = float(value_str.replace(',', '.'))
                
                min_value = validation_rules.get('min_value')
                max_value = validation_rules.get('max_value')
                
                if min_value is not None and numeric_value < min_value:
                    errors.append({
                        'field': field_name,
                        'row': row_index,
                        'error_type': 'value_too_low',
                        'message': f"Waarde {numeric_value} is te laag (min {min_value})",
                        'value': value
                    })
                
                if max_value is not None and numeric_value > max_value:
                    errors.append({
                        'field': field_name,
                        'row': row_index,
                        'error_type': 'value_too_high',
                        'message': f"Waarde {numeric_value} is te hoog (max {max_value})",
                        'value': value
                    })
                    
            except ValueError:
                pass  # Data type error al gevangen hierboven
        
        return errors
        
    except Exception as e:
        logging.error(f"Fout bij field validatie voor '{field_name}': {e}")
        return [{
            'field': field_name,
            'row': row_data.get('row_index', 0) if row_data else 0,
            'error_type': 'validation_error',
            'message': f"Validatie fout: {str(e)}",
            'value': value
        }]


def _validate_mandatory_field(field_name: str, value: Any, row_index: int, field_config: Dict) -> List:
    """
    Valideert mandatory field specifiek.
    
    Args:
        field_name: Naam van mandatory field
        value: Waarde om te valideren
        row_index: Rij nummer
        field_config: Field configuratie
        
    Returns:
        Lijst van validatie fouten
    """
    try:
        errors = []
        
        # Check of waarde leeg is
        if pd.isna(value) or str(value).strip() == '':
            errors.append({
                'field': field_name,
                'row': row_index,
                'error_type': 'mandatory_field_empty',
                'message': f"Verplicht veld '{field_name}' mag niet leeg zijn",
                'value': value,
                'severity': 'high'
            })
        
        return errors
        
    except Exception as e:
        logging.error(f"Fout bij mandatory field validatie: {e}")
        return []


def _validate_data_type(value: str, expected_type: str) -> bool:
    """
    Valideert of waarde het juiste data type heeft.
    
    Args:
        value: Waarde om te valideren
        expected_type: Verwachte data type ('text', 'numeric', 'integer', 'date', 'boolean')
        
    Returns:
        True als data type correct is
    """
    try:
        if expected_type == 'text':
            return True  # Alles kan text zijn
        
        elif expected_type == 'numeric':
            try:
                float(value.replace(',', '.'))
                return True
            except ValueError:
                return False
        
        elif expected_type == 'integer':
            try:
                int(float(value.replace(',', '.')))
                return True
            except ValueError:
                return False
        
        elif expected_type == 'date':
            try:
                pd.to_datetime(value)
                return True
            except (ValueError, TypeError):
                return False
        
        elif expected_type == 'boolean':
            return value.lower() in ['true', 'false', '1', '0', 'ja', 'nee', 'yes', 'no']
        
        return True  # Onbekende types accepteren
        
    except Exception as e:
        logging.error(f"Fout bij data type validatie: {e}")
        return True


def _generate_validation_report(validation_results: List, validation_stats: Dict, 
                               failed_rows: List, summary_stats: Dict,
                               template_context: Dict, original_filename: str,
                               unmapped_columns: List) -> str:
    """
    Genereert Excel validatie rapport.
    
    Args:
        validation_results: Lijst van validatie fouten
        validation_stats: Validatie statistieken
        failed_rows: Rijen met fouten
        summary_stats: Samenvatting statistieken
        template_context: Template context info
        original_filename: Originele bestandsnaam
        unmapped_columns: Unmapped kolommen
        
    Returns:
        Pad naar gegenereerd rapport bestand
    """
    try:
        # Bepaal output directory
        output_dir = os.path.join(os.getcwd(), "validation_reports")
        os.makedirs(output_dir, exist_ok=True)
        
        # Genereer rapport bestandsnaam
        base_name = os.path.splitext(original_filename)[0]
        report_filename = f"{base_name}_validation_report.xlsx"
        report_path = os.path.join(output_dir, report_filename)
        
        # Creëer Excel rapport met meerdere sheets
        with pd.ExcelWriter(report_path, engine='openpyxl') as writer:
            # Sheet 1: Samenvatting
            _create_summary_sheet(writer, template_context, summary_stats, validation_stats)
            
            # Sheet 2: Fouten details
            if validation_results:
                _create_errors_sheet(writer, validation_results)
            
            # Sheet 3: Probleem rijen
            if failed_rows:
                _create_failed_rows_sheet(writer, failed_rows)
            
            # Sheet 4: Unmapped kolommen
            if unmapped_columns:
                _create_unmapped_columns_sheet(writer, unmapped_columns)
        
        logging.info(f"Validatie rapport gegenereerd: {report_path}")
        return report_path
        
    except Exception as e:
        logging.error(f"Fout bij genereren validatie rapport: {e}")
        return None


def _create_summary_sheet(writer, template_context: Dict, summary_stats: Dict, validation_stats: Dict):
    """Creëert samenvatting sheet in Excel rapport."""
    try:
        # Template informatie
        template_info = []
        stamp_data = template_context.get('stamp_data', {})
        
        if template_context.get('template_type') == 'TG':
            template_info = [
                ['Template Type', 'TG'],  # ✅ Template Type toevoegen voor consistentie
                ['Template', os.path.basename(template_context.get('excel_path', ''))],
                ['Template Generator', stamp_data.get('raw_code', '')],
                ['Categorieën', ', '.join(stamp_data.get('product_types', []))],
                ['Organisaties', ', '.join(stamp_data.get('institutions', []))],
                ['Velden', f"{stamp_data.get('visible_fields', 0)} zichtbaar, {stamp_data.get('mandatory_fields', 0)} verplicht"]
            ]
        else:
            template_info = [
                ['Template Type', template_context.get('template_type', 'Onbekend')],
                ['Bestand', os.path.basename(template_context.get('excel_path', ''))]
            ]
        
        # Statistieken
        present_mandatory_count = len(validation_stats.get('mandatory_fields', []))
        missing_mandatory_count = len(validation_stats.get('missing_mandatory_fields', []))
        
        stats_info = [
            ['Aantal rijen', summary_stats.get('total_rows', 0)],
            ['Aantal kolommen', summary_stats.get('total_fields', 0)],
            ['Aantal velden', summary_stats.get('total_fields', 0)],
            ['Aantal aanwezige verplichte kolommen', present_mandatory_count],
            ['Aantal afwezige verplichte kolommen', missing_mandatory_count],
            ['Aantal gevulde verplichte velden', summary_stats.get('total_rows', 0) * present_mandatory_count - summary_stats.get('mandatory_field_errors', 0)],
            ['Aantal aanwezige lege verplichte velden', summary_stats.get('mandatory_field_errors', 0)],
            ['Aantal regels mogelijk afgewezen door Gatekeeper', summary_stats.get('rows_with_errors', 0)]
        ]
        
        # Maak DataFrame en schrijf naar Excel
        template_df = pd.DataFrame(template_info)
        stats_df = pd.DataFrame(stats_info)
        
        # Headers toevoegen
        summary_data = []
        summary_data.append(['Template'])
        summary_data.extend(template_info)
        summary_data.append([''])
        summary_data.append(['Belangrijkste Statistieken'])
        summary_data.extend(stats_info)
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Samenvatting', index=False, header=False)
        
    except Exception as e:
        logging.error(f"Fout bij maken summary sheet: {e}")


def _create_errors_sheet(writer, validation_results: List):
    """Creëert fouten details sheet."""
    try:
        errors_df = pd.DataFrame(validation_results)
        errors_df.to_excel(writer, sheet_name='Fouten Details', index=False)
    except Exception as e:
        logging.error(f"Fout bij maken errors sheet: {e}")


def _create_failed_rows_sheet(writer, failed_rows: List):
    """Creëert probleem rijen sheet.""" 
    try:
        failed_df = pd.DataFrame([{
            'Rij': row['row_index'],
            'Aantal Fouten': row['error_count']
        } for row in failed_rows])
        failed_df.to_excel(writer, sheet_name='Probleem Rijen', index=False)
    except Exception as e:
        logging.error(f"Fout bij maken failed rows sheet: {e}")


def _create_unmapped_columns_sheet(writer, unmapped_columns: List):
    """Creëert unmapped kolommen sheet."""
    try:
        unmapped_df = pd.DataFrame({
            'Unmapped Kolommen': unmapped_columns
        })
        unmapped_df.to_excel(writer, sheet_name='Unmapped Kolommen', index=False)
    except Exception as e:
        logging.error(f"Fout bij maken unmapped columns sheet: {e}")