"""
Enhanced column hiding module voor Excel templates.

Biedt robuuste methodes voor het verbergen van kolommen in Excel bestanden.
"""

from enum import Enum
from typing import List, Dict, Any
from pathlib import Path
import zipfile
import tempfile
import shutil
from xml.etree import ElementTree as ET
from openpyxl.worksheet.worksheet import Worksheet


class HideMethod(Enum):
    """Verschillende methodes voor het verbergen van kolommen."""
    BASIC = "basic"
    WIDTH_ZERO = "width_zero"
    XML_PATCH = "xml_patch"
    ALL_METHODS = "all_methods"


class ColumnHider:
    """
    Geavanceerde kolom hiding voor Excel templates.
    """
    
    NS = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    
    def hide_columns(self, 
                    worksheet: Worksheet, 
                    columns_to_hide: List[str],
                    method: HideMethod = HideMethod.ALL_METHODS) -> Dict[str, Any]:
        """
        Verberg kolommen met gespecificeerde methode.
        
        Args:
            worksheet: Excel worksheet object
            columns_to_hide: Lijst van kolom letters (bijv. ['AA', 'AB'])
            method: HideMethod enum voor gewenste methode
            
        Returns:
            Dictionary met resultaten en eventuele fouten
        """
        result = {
            "hidden_columns": [],
            "errors": [],
            "method_used": method.value
        }
        
        try:
            if method == HideMethod.BASIC:
                self._hide_basic(worksheet, columns_to_hide, result)
            elif method == HideMethod.WIDTH_ZERO:
                self._hide_width_zero(worksheet, columns_to_hide, result)
            elif method == HideMethod.XML_PATCH:
                result["errors"].append("XML patch method not available in this context")
            elif method == HideMethod.ALL_METHODS:
                # Alleen basis hiding - width wordt centraal geregeld
                self._hide_basic(worksheet, columns_to_hide, result)
            
        except Exception as e:
            result["errors"].append(f"Fout bij column hiding: {str(e)}")
        
        return result
    
    def _hide_basic(self, worksheet: Worksheet, columns: List[str], result: Dict[str, Any]) -> None:
        """Basis hiding methode via openpyxl."""
        for col in columns:
            try:
                worksheet.column_dimensions[col].hidden = True
                if col not in result["hidden_columns"]:
                    result["hidden_columns"].append(col)
            except Exception as e:
                result["errors"].append(f"Basic hiding gefaald voor {col}: {e}")
    
    def _hide_width_zero(self, worksheet: Worksheet, columns: List[str], result: Dict[str, Any]) -> None:
        """Aanvullende hiding via width=0."""
        for col in columns:
            try:
                # Zet width op minimale waarde maar niet helemaal 0 om layout niet te verstoren
                worksheet.column_dimensions[col].width = 0.1
                # Zorg dat bestFit niet interfereert
                if hasattr(worksheet.column_dimensions[col], 'bestFit'):
                    worksheet.column_dimensions[col].bestFit = False
            except Exception as e:
                result["errors"].append(f"Width minimaliseren gefaald voor {col}: {e}")
    
    @staticmethod
    def col_to_idx(col: str) -> int:
        """Convert kolom letter naar index (A=1, B=2, etc.)"""
        n = 0
        for c in col.upper():
            n = n * 26 + (ord(c) - 64)
        return n


def hide_columns_in_file(file_path: Path, 
                        columns_to_hide: List[str],
                        output_path: Path = None,
                        method: HideMethod = HideMethod.ALL_METHODS) -> Dict[str, Any]:
    """
    Verberg kolommen direct in Excel bestand via XML manipulation.
    
    Args:
        file_path: Pad naar input Excel bestand
        columns_to_hide: Lijst van kolom letters
        output_path: Pad voor output (default: overschrijf input)
        method: Hide methode
        
    Returns:
        Dictionary met resultaten
    """
    if output_path is None:
        output_path = file_path
    
    result = {
        "hidden_columns": [],
        "errors": [],
        "method_used": method.value,
        "xml_patched": False
    }
    
    if method not in [HideMethod.XML_PATCH, HideMethod.ALL_METHODS]:
        result["errors"].append("XML patching only available for XML_PATCH or ALL_METHODS")
        return result
    
    try:
        # Maak temporary kopie voor bewerking
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = Path(temp_dir) / "temp.xlsx"
            shutil.copy2(file_path, temp_file)
            
            # XML manipulation
            _xml_hide_columns(temp_file, columns_to_hide, result)
            
            # Kopieer resultaat naar output
            shutil.copy2(temp_file, output_path)
            
    except Exception as e:
        result["errors"].append(f"XML patching gefaald: {str(e)}")
    
    return result


def _xml_hide_columns(file_path: Path, columns_to_hide: List[str], result: Dict[str, Any]) -> None:
    """Interne XML manipulation voor column hiding."""
    NS = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    
    def q(tag):
        return f"{{{NS['a']}}}{tag}"
    
    # Lees Excel bestand als ZIP
    with zipfile.ZipFile(file_path, 'r') as zip_read:
        # Zoek worksheet1.xml
        worksheet_path = None
        for name in zip_read.namelist():
            if 'worksheets/sheet1.xml' in name:
                worksheet_path = name
                break
        
        if not worksheet_path:
            result["errors"].append("Sheet1 niet gevonden in Excel bestand")
            return
        
        # Lees worksheet XML
        with zip_read.open(worksheet_path) as ws_file:
            tree = ET.parse(ws_file)
            root = tree.getroot()
        
        # Ensure <cols> node exists
        cols = root.find("a:cols", NS)
        if cols is None:
            cols = ET.Element(q("cols"))
            # Plaats voor sheetData als die bestaat
            sheet_data = root.find("a:sheetData", NS)
            if sheet_data is not None:
                root.insert(list(root).index(sheet_data), cols)
            else:
                root.insert(0, cols)
        
        # Verberg elke kolom
        for col in columns_to_hide:
            idx = ColumnHider.col_to_idx(col)
            _upsert_hidden_col(cols, idx, NS)
            result["hidden_columns"].append(col)
        
        # Schrijf terug naar ZIP
        with tempfile.NamedTemporaryFile(mode='w+b', delete=False) as temp_xml:
            tree.write(temp_xml, encoding='utf-8', xml_declaration=True)
            temp_xml_path = temp_xml.name
        
        # Rebuild ZIP met nieuwe worksheet
        with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zip_write:
            for item in zip_read.namelist():
                if item != worksheet_path:
                    zip_write.writestr(item, zip_read.read(item))
            
            # Voeg aangepaste worksheet toe
            zip_write.write(temp_xml_path, worksheet_path)
        
        # Cleanup
        Path(temp_xml_path).unlink()
        
        result["xml_patched"] = True


def _upsert_hidden_col(cols_node, idx: int, NS: dict) -> None:
    """Voeg hidden kolom definitie toe of update bestaande."""
    def q(tag):
        return f"{{{NS['a']}}}{tag}"
    
    # Zoek bestaande col-range
    for c in list(cols_node.findall("a:col", NS)):
        mn, mx = int(c.get("min")), int(c.get("max"))
        if mn <= idx <= mx:
            if mn == mx == idx:
                # Exacte match - update
                c.set("hidden", "1")
                c.set("width", "0.1")
                return
            else:
                # Split range
                cols_node.remove(c)
                
                # Voeg ranges toe voor, tijdens en na
                if mn < idx:
                    new_col = ET.Element(q("col"))
                    new_col.set("min", str(mn))
                    new_col.set("max", str(idx - 1))
                    for attr, val in c.attrib.items():
                        if attr not in ["min", "max"]:
                            new_col.set(attr, val)
                    cols_node.append(new_col)
                
                # Hidden kolom
                hidden_col = ET.Element(q("col"))
                hidden_col.set("min", str(idx))
                hidden_col.set("max", str(idx))
                hidden_col.set("hidden", "1")
                hidden_col.set("width", "0.1")
                for attr, val in c.attrib.items():
                    if attr not in ["min", "max", "hidden", "width"]:
                        hidden_col.set(attr, val)
                cols_node.append(hidden_col)
                
                if mx > idx:
                    new_col = ET.Element(q("col"))
                    new_col.set("min", str(idx + 1))
                    new_col.set("max", str(mx))
                    for attr, val in c.attrib.items():
                        if attr not in ["min", "max"]:
                            new_col.set(attr, val)
                    cols_node.append(new_col)
                
                return
    
    # Geen bestaande range gevonden - voeg nieuwe toe
    new_col = ET.Element(q("col"))
    new_col.set("min", str(idx))
    new_col.set("max", str(idx))
    new_col.set("hidden", "1")
    new_col.set("width", "0.1")
    cols_node.append(new_col)
