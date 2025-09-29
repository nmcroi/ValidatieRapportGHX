"""
Data Processor Module

Deze module handelt header mapping, data cleaning en normalisatie af.
"""

import logging
import pandas as pd
import re
from typing import Dict, Any, List, Tuple, Union


def map_headers(df: pd.DataFrame, mapping_config: Dict, return_mapping: bool = False) -> Union[
    Tuple[pd.DataFrame, List[str], Dict[str, str], Dict[str, str]], 
    Tuple[pd.DataFrame, List[str], Dict[str, str]]
]:
    """
    Mapt supplier headers naar gestandaardiseerde GHX headers.
    
    Args:
        df: DataFrame met supplier data
        mapping_config: Mapping configuratie dict
        return_mapping: Of column mapping dict geretourneerd moet worden
        
    Returns:
        Tuple van (mapped_df, unmapped_columns, original_mapping [, reverse_mapping])
    """
    try:
        logging.info(f"Header mapping starten voor {len(df.columns)} kolommen")
        
        # Bereid mapping voor
        field_mapping = mapping_config.get('fields', {})
        mapped_df = df.copy()
        unmapped_columns = []
        original_column_mapping = {}
        reverse_mapping = {}
        
        # Creëer mapping van originele headers naar GHX headers
        for ghx_field_name, field_config in field_mapping.items():
            if not isinstance(field_config, dict):
                continue
                
            col_position = field_config.get('col')
            if col_position is None:
                continue
            
            # Vind overeenkomende kolom in dataframe
            matched_column = None
            
            # Probeer exacte match eerst
            for df_column in df.columns:
                normalized_df_col = normalize_template_header(str(df_column))
                normalized_ghx_field = normalize_template_header(ghx_field_name)
                
                if normalized_df_col == normalized_ghx_field:
                    matched_column = df_column
                    break
            
            # Als geen exacte match, probeer fuzzy matching
            if matched_column is None:
                matched_column = _find_fuzzy_header_match(ghx_field_name, df.columns)
            
            if matched_column is not None:
                # Hernoem kolom
                if str(matched_column) != ghx_field_name:
                    mapped_df = mapped_df.rename(columns={matched_column: ghx_field_name})
                    original_column_mapping[ghx_field_name] = str(matched_column)
                    reverse_mapping[str(matched_column)] = ghx_field_name
                else:
                    original_column_mapping[ghx_field_name] = ghx_field_name
                    reverse_mapping[ghx_field_name] = ghx_field_name
        
        # Identificeer unmapped kolommen
        for original_col in df.columns:
            if str(original_col) not in reverse_mapping:
                unmapped_columns.append(str(original_col))
        
        logging.info(f"Header mapping voltooid: {len(original_column_mapping)} mapped, "
                    f"{len(unmapped_columns)} unmapped")
        
        if return_mapping:
            return mapped_df, unmapped_columns, original_column_mapping, reverse_mapping
        else:
            return mapped_df, unmapped_columns, original_column_mapping
            
    except Exception as e:
        logging.error(f"Fout bij header mapping: {e}")
        if return_mapping:
            return df, list(df.columns), {}, {}
        else:
            return df, list(df.columns), {}


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Voert basis data cleaning uit op DataFrame.
    
    Args:
        df: DataFrame om te cleanen
        
    Returns:
        Gecleanede DataFrame
    """
    try:
        logging.info(f"Data cleaning starten voor DataFrame: {df.shape}")
        cleaned_df = df.copy()
        
        # Verwijder volledig lege rijen
        initial_rows = len(cleaned_df)
        cleaned_df = cleaned_df.dropna(how='all')
        removed_rows = initial_rows - len(cleaned_df)
        if removed_rows > 0:
            logging.info(f"Verwijderd {removed_rows} lege rijen")
        
        # Clean kolom namen
        cleaned_df.columns = [clean_column_name(str(col)) for col in cleaned_df.columns]
        
        # Clean string waarden
        for column in cleaned_df.columns:
            if cleaned_df[column].dtype == 'object':
                cleaned_df[column] = cleaned_df[column].astype(str)
                cleaned_df[column] = cleaned_df[column].apply(_clean_cell_value)
        
        # Vervang 'nan' strings door echte NaN
        cleaned_df = cleaned_df.replace('nan', pd.NA)
        
        logging.info(f"Data cleaning voltooid: {cleaned_df.shape}")
        return cleaned_df
        
    except Exception as e:
        logging.error(f"Fout bij data cleaning: {e}")
        return df


def normalize_template_header(header: str) -> str:
    """
    Normaliseert template header voor vergelijking.
    
    Args:
        header: Header string
        
    Returns:
        Genormaliseerde header string
    """
    try:
        if not header:
            return ""
        
        # Basis cleaning
        normalized = str(header).strip()
        
        # Verwijder common prefixes/suffixes
        prefixes_to_remove = ['ghx_', 'template_', 'field_']
        for prefix in prefixes_to_remove:
            if normalized.lower().startswith(prefix):
                normalized = normalized[len(prefix):]
        
        # Normaliseer spaties en speciale tekens
        normalized = re.sub(r'[_\-\s]+', ' ', normalized)
        
        # Verwijder haakjes en inhoud
        normalized = re.sub(r'\([^)]*\)', '', normalized)
        
        # Extra spaces weghalen
        normalized = ' '.join(normalized.split())
        
        return normalized.strip().lower()
        
    except Exception as e:
        logging.error(f"Fout bij header normalisatie voor '{header}': {e}")
        return str(header).lower()


def clean_column_name(col: str) -> str:
    """
    Cleant kolom namen voor consistentie.
    
    Args:
        col: Kolom naam
        
    Returns:
        Gecleanede kolom naam
    """
    try:
        if not col:
            return ""
        
        # Basis cleaning
        clean_col = str(col).strip()
        
        # Verwijder leading/trailing quotes
        clean_col = clean_col.strip('\'"')
        
        # Vervang problematische karakters
        clean_col = re.sub(r'[\r\n\t]', ' ', clean_col)
        
        # Multiple spaces naar enkele space
        clean_col = ' '.join(clean_col.split())
        
        return clean_col
        
    except Exception as e:
        logging.error(f"Fout bij kolom naam cleaning voor '{col}': {e}")
        return str(col)


def clean_supplier_header(header: str) -> str:
    """
    Specifieke cleaning voor supplier headers.
    
    Args:
        header: Supplier header string
        
    Returns:
        Gecleanede header string
    """
    try:
        if not header:
            return ""
        
        cleaned = str(header).strip()
        
        # Verwijder supplier-specific prefixes
        supplier_prefixes = [
            'supplier_', 'leverancier_', 'vendor_', 'client_'
        ]
        
        for prefix in supplier_prefixes:
            if cleaned.lower().startswith(prefix):
                cleaned = cleaned[len(prefix):]
        
        # Vervang underscores door spaces
        cleaned = cleaned.replace('_', ' ')
        
        # Normaliseer case - Title Case voor headers
        cleaned = ' '.join(word.capitalize() for word in cleaned.split())
        
        return cleaned.strip()
        
    except Exception as e:
        logging.error(f"Fout bij supplier header cleaning voor '{header}': {e}")
        return str(header)


def _find_fuzzy_header_match(target_header: str, available_headers: List[str]) -> str:
    """
    Zoekt fuzzy match voor header in beschikbare headers.
    
    Args:
        target_header: Gewenste header
        available_headers: Lijst van beschikbare headers
        
    Returns:
        Best matching header of None
    """
    try:
        target_normalized = normalize_template_header(target_header)
        
        best_match = None
        best_score = 0.0
        
        for header in available_headers:
            header_normalized = normalize_template_header(str(header))
            
            # Exacte match
            if target_normalized == header_normalized:
                return header
            
            # Substring match
            if target_normalized in header_normalized or header_normalized in target_normalized:
                score = min(len(target_normalized), len(header_normalized)) / max(len(target_normalized), len(header_normalized))
                if score > best_score:
                    best_score = score
                    best_match = header
        
        # Alleen retourneren als redelijke match (>70%)
        if best_score > 0.7:
            logging.info(f"Fuzzy match: '{target_header}' -> '{best_match}' (score: {best_score:.2f})")
            return best_match
        
        return None
        
    except Exception as e:
        logging.error(f"Fout bij fuzzy header matching: {e}")
        return None


def _clean_cell_value(value: Any) -> str:
    """
    Cleant individuele cel waarden.
    
    Args:
        value: Cel waarde
        
    Returns:
        Gecleanede string waarde
    """
    try:
        if pd.isna(value):
            return ""
        
        # Converteer naar string
        str_value = str(value).strip()
        
        # Verwijder leading/trailing quotes
        str_value = str_value.strip('\'"')
        
        # Vervang newlines en tabs
        str_value = re.sub(r'[\r\n\t]+', ' ', str_value)
        
        # Multiple spaces naar enkele space
        str_value = ' '.join(str_value.split())
        
        # Speciale waarden normaliseren
        if str_value.lower() in ['nan', 'null', 'none', 'n/a', '#n/a']:
            return ""
        
        return str_value
        
    except Exception as e:
        logging.error(f"Fout bij cel waarde cleaning: {e}")
        return str(value) if value is not None else ""


def detect_delimiter(file_path: str) -> str:
    """
    Detecteert delimiter voor CSV bestanden.
    
    Args:
        file_path: Pad naar CSV bestand
        
    Returns:
        Gedetecteerde delimiter
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            first_line = file.readline()
            
        # Count mogelijke delimiters
        delimiters = [',', ';', '\t', '|']
        counts = {}
        
        for delimiter in delimiters:
            counts[delimiter] = first_line.count(delimiter)
        
        # Retourneer delimiter met hoogste count
        best_delimiter = max(counts, key=counts.get)
        
        logging.info(f"Gedetecteerde delimiter: '{best_delimiter}' (count: {counts[best_delimiter]})")
        return best_delimiter
        
    except Exception as e:
        logging.error(f"Fout bij delimiter detectie: {e}")
        return ','  # Default fallback


def standardize_data_types(df: pd.DataFrame, field_config: Dict[str, Any]) -> pd.DataFrame:
    """
    Standaardiseert data types op basis van field configuratie.
    
    Args:
        df: DataFrame om te standaardiseren
        field_config: Field configuratie met data type info
        
    Returns:
        DataFrame met gestandaardiseerde data types
    """
    try:
        standardized_df = df.copy()
        
        for column in standardized_df.columns:
            if column in field_config:
                config = field_config[column]
                if isinstance(config, dict) and 'validation' in config:
                    validation = config['validation']
                    data_type = validation.get('data_type', 'text')
                    
                    try:
                        if data_type == 'numeric':
                            standardized_df[column] = pd.to_numeric(standardized_df[column], errors='coerce')
                        elif data_type == 'integer':
                            standardized_df[column] = pd.to_numeric(standardized_df[column], errors='coerce').astype('Int64')
                        elif data_type == 'date':
                            standardized_df[column] = pd.to_datetime(standardized_df[column], errors='coerce')
                        elif data_type == 'boolean':
                            standardized_df[column] = standardized_df[column].astype(str).str.lower().isin(['true', '1', 'ja', 'yes'])
                        # 'text' blijft string (default)
                        
                    except Exception as e:
                        logging.warning(f"Kon data type niet standaardiseren voor kolom '{column}': {e}")
        
        logging.info(f"Data type standaardisatie voltooid voor {len(standardized_df.columns)} kolommen")
        return standardized_df
        
    except Exception as e:
        logging.error(f"Fout bij data type standaardisatie: {e}")
        return df