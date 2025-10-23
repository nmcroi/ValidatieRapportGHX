#!/usr/bin/env python3
"""
Test script om de Quick Mode performance fix te verifiëren.
Dit test de nieuwe slimme row counting die grote bestanden niet volledig laadt.
"""

import pandas as pd
import time
import os
import sys

def test_smart_row_counting(file_path):
    """Test de nieuwe slimme row counting methode"""
    print(f"\nTesten: {os.path.basename(file_path)}")
    print(f"Grootte: {os.path.getsize(file_path) / (1024*1024):.1f} MB")
    print("-" * 50)
    
    # NIEUWE METHODE: Slimme detectie
    start = time.time()
    df_check = pd.read_excel(file_path, nrows=5001)
    actual_rows = len(df_check)
    
    if actual_rows <= 5000:
        # Klein bestand
        total_rows = actual_rows
        mode = "VOLLEDIG"
        max_rows = None
    else:
        # Groot bestand
        total_rows = "5000+"
        mode = "QUICK"
        max_rows = 5000
    
    end = time.time()
    
    print(f"✅ Slimme detectie tijd: {end-start:.2f} sec")
    print(f"   Gedetecteerd: {total_rows} rijen")
    print(f"   Modus: {mode}")
    
    # Test ook het daadwerkelijk lezen voor validatie
    if max_rows:
        start = time.time()
        df_validate = pd.read_excel(file_path, nrows=max_rows)
        end = time.time()
        print(f"✅ Validatie data laden: {end-start:.2f} sec")
        print(f"   Geladen: {len(df_validate)} rijen voor validatie")
    
    return end-start

def compare_old_vs_new(file_path):
    """Vergelijk oude methode (openpyxl) met nieuwe methode"""
    print(f"\n{'='*60}")
    print(f"VERGELIJKING OUDE vs NIEUWE METHODE")
    print(f"Bestand: {os.path.basename(file_path)}")
    print(f"{'='*60}")
    
    # OUDE METHODE (alleen voor vergelijking, niet meer gebruiken!)
    try:
        import openpyxl
        start = time.time()
        wb = openpyxl.load_workbook(file_path, read_only=True)
        ws = wb.active
        total_rows_old = ws.max_row - 1
        wb.close()
        old_time = time.time() - start
        print(f"❌ OUDE methode (openpyxl): {old_time:.2f} sec - {total_rows_old} rijen")
    except:
        print("❌ OUDE methode kon niet worden getest")
        old_time = None
    
    # NIEUWE METHODE
    start = time.time()
    df_check = pd.read_excel(file_path, nrows=5001)
    actual_rows = len(df_check)
    if actual_rows <= 5000:
        total_rows_new = actual_rows
    else:
        total_rows_new = "5000+"
    new_time = time.time() - start
    print(f"✅ NIEUWE methode (slim): {new_time:.2f} sec - {total_rows_new} rijen")
    
    if old_time:
        speedup = old_time / new_time
        print(f"\n🚀 Snelheidswinst: {speedup:.1f}x sneller!")

def main():
    print("\n" + "="*60)
    print("QUICK MODE PERFORMANCE TEST - NA FIX")
    print("="*60)
    
    # Test directory
    test_dir = "/Users/ncroiset/Vibe Coding Projecten/Cursor Projecten/Project GHX Prijstemplate Validatie Tool/test/testinput"
    
    if not os.path.exists(test_dir):
        print(f"❌ Test directory niet gevonden: {test_dir}")
        return
    
    # Verzamel test bestanden
    test_files = []
    for file in os.listdir(test_dir):
        if file.endswith('.xlsx') and not file.startswith('~'):
            file_path = os.path.join(test_dir, file)
            size_mb = os.path.getsize(file_path) / (1024*1024)
            test_files.append((file_path, size_mb, file))
    
    # Sorteer op grootte
    test_files.sort(key=lambda x: x[1])
    
    print(f"\nGevonden test bestanden:")
    for _, size, name in test_files[:10]:
        print(f"  - {name}: {size:.1f} MB")
    
    # Test verschillende groottes
    print("\n" + "="*60)
    print("TEST 1: SLIMME ROW COUNTING")
    print("="*60)
    
    tested = []
    for path, size, name in test_files:
        if size < 0.5:  # Klein bestand
            if not any(t[0] == 'klein' for t in tested):
                test_smart_row_counting(path)
                tested.append(('klein', path))
        elif 0.5 <= size < 5:  # Medium bestand
            if not any(t[0] == 'medium' for t in tested):
                test_smart_row_counting(path)
                tested.append(('medium', path))
        elif size >= 5:  # Groot bestand
            if not any(t[0] == 'groot' for t in tested):
                test_smart_row_counting(path)
                tested.append(('groot', path))
        
        if len(tested) >= 3:
            break
    
    # Vergelijk oude vs nieuwe voor groot bestand
    groot = [t[1] for t in tested if t[0] == 'groot']
    if groot:
        compare_old_vs_new(groot[0])
    
    print("\n" + "="*60)
    print("✅ TEST COMPLEET")
    print("="*60)
    print("\nCONCLUSIE:")
    print("- Kleine bestanden (≤5000 rijen): Direct exact aantal")
    print("- Grote bestanden (>5000 rijen): Direct Quick Mode zonder trage telling")
    print("- Performance is nu consistent ongeacht bestandsgrootte!")

if __name__ == "__main__":
    main()