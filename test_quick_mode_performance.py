#!/usr/bin/env python3
"""
Test script om Quick Mode performance te analyseren.
Dit script identificeert waarom grote bestanden trager zijn dan kleine in Quick Mode.
"""

import pandas as pd
import openpyxl
import time
import sys
import os
from typing import Dict, Tuple

def measure_time(func):
    """Decorator om functies te timen"""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"  {func.__name__}: {end - start:.2f} seconden")
        return result
    return wrapper

@measure_time
def count_rows_openpyxl(file_path: str) -> int:
    """Tel rijen met openpyxl (zoals in de app)"""
    wb = openpyxl.load_workbook(file_path, read_only=True)
    ws = wb.active
    total_rows = ws.max_row - 1  # -1 voor header
    wb.close()
    return total_rows

@measure_time
def read_first_5000_rows_basic(file_path: str) -> pd.DataFrame:
    """Lees alleen eerste 5000 rijen met pandas nrows"""
    return pd.read_excel(file_path, nrows=5000)

@measure_time
def read_first_5000_rows_with_dtype(file_path: str) -> pd.DataFrame:
    """Lees eerste 5000 rijen met dtype specificaties (zoals in de app)"""
    dtype_spec = {
        "UNSPSC CODE (UNITED NATIONS STANDARD PRODUCTS AND SERVICES CODE)": str,
        "UNSPSC Code": str,
        "BARCODENUMMER (EAN/ GTIN/ HIBC)": str,
        "GTIN Verpakkingseenheid": str,
    }
    return pd.read_excel(file_path, dtype=dtype_spec, nrows=5000)

@measure_time
def read_full_file_basic(file_path: str) -> pd.DataFrame:
    """Lees volledig bestand zonder limitaties"""
    return pd.read_excel(file_path)

@measure_time
def read_with_xlsxwriter_engine(file_path: str, nrows: int = 5000) -> pd.DataFrame:
    """Test met verschillende Excel engine"""
    return pd.read_excel(file_path, nrows=nrows, engine='openpyxl')

def analyze_file(file_path: str) -> Dict:
    """Analyseer een Excel bestand op verschillende manieren"""
    
    print(f"\n{'='*60}")
    print(f"Analyseren van: {os.path.basename(file_path)}")
    print(f"Bestandsgrootte: {os.path.getsize(file_path) / (1024*1024):.1f} MB")
    print(f"{'='*60}")
    
    results = {}
    
    # 1. Tel rijen
    print("\n1. RIJEN TELLEN:")
    row_count = count_rows_openpyxl(file_path)
    print(f"   Totaal aantal rijen: {row_count:,}")
    results['row_count'] = row_count
    
    # 2. Lees eerste 5000 rijen - verschillende methodes
    print("\n2. EERSTE 5000 RIJEN LEZEN:")
    
    print("\n   a) Basis pandas read (nrows=5000):")
    df_basic = read_first_5000_rows_basic(file_path)
    print(f"      Shape: {df_basic.shape}")
    
    print("\n   b) Met dtype specificaties (zoals in app):")
    df_dtype = read_first_5000_rows_with_dtype(file_path)
    print(f"      Shape: {df_dtype.shape}")
    
    print("\n   c) Met openpyxl engine expliciet:")
    df_engine = read_with_xlsxwriter_engine(file_path, 5000)
    print(f"      Shape: {df_engine.shape}")
    
    # 3. Vergelijk met volledig lezen (alleen voor kleine bestanden)
    if row_count < 10000:
        print("\n3. VOLLEDIG BESTAND LEZEN (ter vergelijking):")
        df_full = read_full_file_basic(file_path)
        print(f"   Shape: {df_full.shape}")
    else:
        print(f"\n3. VOLLEDIG BESTAND LEZEN: Overgeslagen (>{row_count:,} rijen)")
    
    return results

def test_incremental_read(file_path: str):
    """Test incrementeel lezen om te zien waar performance degradatie begint"""
    print(f"\n{'='*60}")
    print(f"INCREMENTELE READ TEST")
    print(f"{'='*60}")
    
    test_sizes = [100, 500, 1000, 2000, 3000, 4000, 5000]
    
    for size in test_sizes:
        start = time.time()
        df = pd.read_excel(file_path, nrows=size)
        end = time.time()
        print(f"  {size:5d} rijen: {end-start:6.2f} sec - Shape: {df.shape}")
        
        # Probeer garbage collection om memory te clearen
        del df
        import gc
        gc.collect()

def main():
    """Main test functie"""
    
    print("\n" + "="*60)
    print("QUICK MODE PERFORMANCE ANALYSE")
    print("="*60)
    
    # Test bestanden
    test_files = []
    
    # Zoek naar test bestanden
    test_dir = "/Users/ncroiset/Vibe Coding Projecten/Cursor Projecten/Project GHX Prijstemplate Validatie Tool/test/testinput"
    
    if os.path.exists(test_dir):
        for file in os.listdir(test_dir):
            if file.endswith('.xlsx') and not file.startswith('~'):
                file_path = os.path.join(test_dir, file)
                size_mb = os.path.getsize(file_path) / (1024*1024)
                test_files.append((file_path, size_mb))
    
    # Sorteer op grootte
    test_files.sort(key=lambda x: x[1])
    
    print(f"\nGevonden test bestanden:")
    for path, size in test_files[:5]:  # Max 5 bestanden
        print(f"  - {os.path.basename(path)}: {size:.1f} MB")
    
    # Selecteer klein en groot bestand voor vergelijking
    small_file = None
    large_file = None
    
    for path, size in test_files:
        if size < 1 and not small_file:
            small_file = path
        elif size > 10 and not large_file:
            large_file = path
    
    if small_file:
        print(f"\nKlein bestand geselecteerd: {os.path.basename(small_file)}")
        analyze_file(small_file)
        test_incremental_read(small_file)
    
    if large_file:
        print(f"\nGroot bestand geselecteerd: {os.path.basename(large_file)}")
        analyze_file(large_file)
        test_incremental_read(large_file)
    
    if not small_file and not large_file:
        print("\nGeen geschikte test bestanden gevonden!")
        print("Plaats Excel bestanden in de test/testinput directory")

if __name__ == "__main__":
    main()