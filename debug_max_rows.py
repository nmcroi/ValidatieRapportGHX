#!/usr/bin/env python3
"""
Debug script om te testen wat er gebeurt met max_rows parameter
"""

import pandas as pd
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_max_rows_logic():
    """Test de max_rows logica"""
    
    # Test bestand pad (vervang met je grote bestand)
    test_file = "/Users/ncroiset/Vibe Coding Projecten/Cursor Projecten/Project GHX Prijstemplate Validatie Tool/test/testinput/generator_large.xlsx"
    
    # Test verschillende max_rows waarden
    test_cases = [
        ("max_rows=None", None),
        ("max_rows=5000", 5000),
        ("max_rows=1000", 1000),
    ]
    
    for test_name, max_rows in test_cases:
        print(f"\n{'='*50}")
        print(f"Test: {test_name}")
        print(f"{'='*50}")
        
        start_time = time.time()
        
        try:
            if max_rows is not None:
                print(f"Leest met nrows={max_rows}")
                df = pd.read_excel(test_file, nrows=max_rows)
            else:
                print("Leest VOLLEDIGE bestand (geen nrows limit)")
                df = pd.read_excel(test_file)
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            print(f"✓ Succes: {df.shape} in {elapsed:.2f} seconden")
            
        except Exception as e:
            end_time = time.time()
            elapsed = end_time - start_time
            print(f"✗ Fout: {e} na {elapsed:.2f} seconden")

if __name__ == "__main__":
    test_max_rows_logic()