"""
Onderzoek generator_small.xlsx om te zien waarom het niet als TG wordt gedetecteerd.
"""

import pandas as pd
import sys
import os
sys.path.append('/Users/ncroiset/Vibe Coding Projecten/Cursor Projecten/Project PrijsValGem_WS app')

from validator.template_detector import test_template_detection

file_path = "/Users/ncroiset/Vibe Coding Projecten/Cursor Projecten/Project PrijsValGem_WS app/test/testinput/generator_small.xlsx"

print("🔍 ONDERZOEK generator_small.xlsx")
print("="*60)

if os.path.exists(file_path):
    # Check A1 en A2 cellen
    print("📋 A1 en A2 INHOUD:")
    try:
        df = pd.read_excel(file_path, nrows=3, usecols=[0, 1])
        print(f"A1: '{df.iloc[0, 0] if not pd.isna(df.iloc[0, 0]) else 'LEEG'}'")
        print(f"A2: '{df.iloc[1, 0] if len(df) > 1 and not pd.isna(df.iloc[1, 0]) else 'LEEG'}'")
        print(f"A3: '{df.iloc[2, 0] if len(df) > 2 and not pd.isna(df.iloc[2, 0]) else 'LEEG'}'")
        
        if len(df.columns) > 1:
            print(f"B1: '{df.iloc[0, 1] if not pd.isna(df.iloc[0, 1]) else 'LEEG'}'")
    except Exception as e:
        print(f"Fout bij lezen A1/A2: {e}")
    
    # Check kolom headers
    print(f"\n📊 KOLOM HEADERS:")
    try:
        df_headers = pd.read_excel(file_path, nrows=0)
        headers = [str(col).strip().lower() for col in df_headers.columns]
        print(f"Totaal kolommen: {len(headers)}")
        print(f"Eerste 10 headers: {headers[:10]}")
        
        # Check nieuwe generatie markers
        nieuwe_markers = ['is bestelbarereenheid', 'omschrijving verpakkingseenheid']
        gevonden_markers = []
        for marker in nieuwe_markers:
            if any(marker in header for header in headers):
                gevonden_markers.append(marker)
        
        print(f"Gevonden nieuwe generatie markers: {gevonden_markers}")
        
    except Exception as e:
        print(f"Fout bij lezen headers: {e}")
    
    # Template detection test
    print(f"\n🔍 TEMPLATE DETECTION DETAIL:")
    try:
        result = test_template_detection(file_path)
        print(f"Template Type: {result.get('template_type')}")
        print(f"Has TG Stamp: {result.get('has_tg_stamp')}")
        print(f"TG Stamp Value: {result.get('tg_stamp_value')}")
        print(f"Nieuwe Generatie Markers: {result.get('heeft_nieuwe_generatie_markers')}")
        print(f"Gevonden Markers: {result.get('gevonden_markers')}")
    except Exception as e:
        print(f"Fout bij template detection: {e}")
        
else:
    print("❌ Bestand niet gevonden")

print("="*60)