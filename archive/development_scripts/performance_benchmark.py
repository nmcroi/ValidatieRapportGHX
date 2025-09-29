#!/usr/bin/env python3
"""
Performance Benchmark Tool voor GHX Prijslijst Validatie Tool
Meet laadtijd, geheugenverbruik en processing performance op verschillende bestandsgroottes.
"""

import time
import psutil
import os
import tempfile
import pandas as pd
import tracemalloc
from typing import Dict, List, Tuple
import logging

# Import de validatie tool
try:
    from validator.price_tool import validate_pricelist
except ImportError as e:
    print(f"Fout bij importeren validatiemodule: {e}")
    print("Zorg ervoor dat de map 'validator' bestaat met daarin __init__.py, price_tool.py en rapport_utils.py.")
    exit(1)

# Configuratie bestanden
MAPPING_JSON = "header_mapping.json"
VALIDATION_JSON = "field_validation_v20.json"
REFERENCE_JSON = "reference_lists.json"

class PerformanceBenchmark:
    def __init__(self):
        self.results = []
        self.process = psutil.Process()
        
    def create_test_excel(self, rows: int, cols: int) -> str:
        """Creëer een test Excel bestand met specifieke grootte"""
        # Basiskolommen volgens GHX template
        base_columns = [
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P'
        ]
        
        # Vul kolommen aan als nodig
        columns = base_columns[:cols] if cols <= len(base_columns) else base_columns + [f'COL{i}' for i in range(len(base_columns), cols)]
        
        # Test data genereren
        data = {}
        for i, col in enumerate(columns):
            if col == 'A':  # Artikel nummer
                data[col] = [f'ART{j:06d}' for j in range(rows)]
            elif col == 'B':  # Prijs
                data[col] = [10.50 + (j * 0.10) for j in range(rows)]
            elif col == 'C':  # GTIN
                data[col] = [f'871234{j:06d}' for j in range(rows)]
            else:
                data[col] = [f'VAL{i}_{j}' for j in range(rows)]
        
        df = pd.DataFrame(data)
        
        # Schrijf naar tijdelijk bestand
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        df.to_excel(temp_file.name, index=False)
        temp_file.close()
        
        return temp_file.name
    
    def measure_memory_usage(self) -> Dict[str, float]:
        """Meet huidig geheugenverbruik"""
        memory_info = self.process.memory_info()
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
            'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
        }
    
    def benchmark_file_size(self, rows: int, cols: int, description: str) -> Dict:
        """Benchmark een specifieke bestandsgrootte"""
        print(f"\n🔍 Testing: {description} ({rows} rows x {cols} cols)")
        
        # Creëer test bestand
        test_file = None
        try:
            test_file = self.create_test_excel(rows, cols)
            file_size_mb = os.path.getsize(test_file) / 1024 / 1024
            
            # Meet geheugen voor validatie
            memory_before = self.measure_memory_usage()
            
            # Start tracemalloc voor gedetailleerde geheugen tracking
            tracemalloc.start()
            
            # Meet tijd
            start_time = time.time()
            
            # Voer validatie uit
            try:
                report_path = validate_pricelist(
                    input_excel_path=test_file,
                    mapping_json_path=MAPPING_JSON,
                    validation_json_path=VALIDATION_JSON,
                    original_input_filename=f"test_{description.replace(' ', '_')}.xlsx",
                    reference_json_path=REFERENCE_JSON,
                )
                validation_success = True
                validation_error = None
            except Exception as e:
                validation_success = False
                validation_error = str(e)
                report_path = None
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Meet geheugen na validatie
            memory_after = self.measure_memory_usage()
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            # Bereken geheugen delta
            memory_delta_mb = memory_after['rss_mb'] - memory_before['rss_mb']
            peak_memory_mb = peak / 1024 / 1024
            
            result = {
                'description': description,
                'rows': rows,
                'cols': cols,
                'file_size_mb': file_size_mb,
                'processing_time_sec': processing_time,
                'memory_before_mb': memory_before['rss_mb'],
                'memory_after_mb': memory_after['rss_mb'],
                'memory_delta_mb': memory_delta_mb,
                'peak_memory_mb': peak_memory_mb,
                'validation_success': validation_success,
                'validation_error': validation_error,
                'report_generated': report_path is not None
            }
            
            # Print resultaat
            print(f"   📁 File size: {file_size_mb:.2f} MB")
            print(f"   ⏱️  Processing time: {processing_time:.2f} seconds")
            print(f"   🧠 Memory delta: {memory_delta_mb:.2f} MB")
            print(f"   📊 Peak memory: {peak_memory_mb:.2f} MB")
            print(f"   ✅ Validation: {'Success' if validation_success else 'Failed'}")
            
            if not validation_success:
                print(f"   ❌ Error: {validation_error}")
            
            # Cleanup report file
            if report_path and os.path.exists(report_path):
                os.remove(report_path)
                
            return result
            
        finally:
            # Cleanup test file
            if test_file and os.path.exists(test_file):
                os.remove(test_file)
    
    def run_benchmark_suite(self):
        """Voer complete benchmark suite uit"""
        print("🚀 Starting GHX Validation Tool Performance Benchmark")
        print("=" * 60)
        
        # Test configuraties: (rows, cols, description)
        test_configs = [
            (100, 10, "Small - 100 products"),
            (500, 15, "Medium - 500 products"),
            (1000, 15, "Large - 1K products"),
            (2500, 15, "Very Large - 2.5K products"),
            (5000, 15, "Extra Large - 5K products"),
            (1000, 25, "Wide - 1K products, 25 cols"),
            (500, 35, "Very Wide - 500 products, 35 cols"),
        ]
        
        # Voer tests uit
        for rows, cols, description in test_configs:
            try:
                result = self.benchmark_file_size(rows, cols, description)
                self.results.append(result)
            except Exception as e:
                print(f"   ❌ Benchmark failed: {e}")
                error_result = {
                    'description': description,
                    'rows': rows,
                    'cols': cols,
                    'error': str(e)
                }
                self.results.append(error_result)
        
        # Genereer rapport
        self.generate_report()
    
    def generate_report(self):
        """Genereer performance rapport"""
        print("\n" + "=" * 60)
        print("📊 PERFORMANCE BENCHMARK RESULTS")
        print("=" * 60)
        
        if not self.results:
            print("Geen resultaten beschikbaar.")
            return
        
        # Creëer DataFrame voor analyse
        successful_results = [r for r in self.results if r.get('validation_success', False)]
        
        if successful_results:
            df = pd.DataFrame(successful_results)
            
            print(f"\n📈 SUMMARY STATISTICS (n={len(successful_results)} successful tests):")
            print(f"   • File sizes: {df['file_size_mb'].min():.2f} - {df['file_size_mb'].max():.2f} MB")
            print(f"   • Processing time: {df['processing_time_sec'].min():.2f} - {df['processing_time_sec'].max():.2f} sec")
            print(f"   • Average processing time: {df['processing_time_sec'].mean():.2f} sec")
            print(f"   • Memory usage: {df['memory_delta_mb'].min():.2f} - {df['memory_delta_mb'].max():.2f} MB")
            print(f"   • Average memory usage: {df['memory_delta_mb'].mean():.2f} MB")
            print(f"   • Peak memory: {df['peak_memory_mb'].min():.2f} - {df['peak_memory_mb'].max():.2f} MB")
            
            # Performance categorieën
            print(f"\n⚡ PERFORMANCE CATEGORIES:")
            fast_threshold = 5.0  # seconds
            memory_threshold = 100.0  # MB
            
            fast_tests = df[df['processing_time_sec'] < fast_threshold]
            slow_tests = df[df['processing_time_sec'] >= fast_threshold]
            
            print(f"   • Fast processing (< {fast_threshold}s): {len(fast_tests)} tests")
            print(f"   • Slow processing (≥ {fast_threshold}s): {len(slow_tests)} tests")
            
            low_memory = df[df['memory_delta_mb'] < memory_threshold]
            high_memory = df[df['memory_delta_mb'] >= memory_threshold]
            
            print(f"   • Low memory usage (< {memory_threshold}MB): {len(low_memory)} tests")
            print(f"   • High memory usage (≥ {memory_threshold}MB): {len(high_memory)} tests")
            
            # Scaling analyse
            if len(df) > 1:
                print(f"\n📊 SCALING ANALYSIS:")
                time_per_row = (df['processing_time_sec'] / df['rows']).mean() * 1000
                memory_per_row = (df['memory_delta_mb'] / df['rows']).mean()
                
                print(f"   • Average time per row: {time_per_row:.2f} ms")
                print(f"   • Average memory per row: {memory_per_row:.3f} MB")
        
        # Toon alle resultaten in detail
        print(f"\n📋 DETAILED RESULTS:")
        print("-" * 80)
        
        for result in self.results:
            if 'error' in result:
                print(f"❌ {result['description']}: ERROR - {result['error']}")
            else:
                success_icon = "✅" if result.get('validation_success') else "❌"
                print(f"{success_icon} {result['description']:<25} | "
                      f"{result.get('file_size_mb', 0):.1f}MB | "
                      f"{result.get('processing_time_sec', 0):.1f}s | "
                      f"{result.get('memory_delta_mb', 0):.1f}MB")
        
        print("\n" + "=" * 60)

def main():
    """Main benchmark functie"""
    # Controleer of configuratiebestanden bestaan
    for config_file in [MAPPING_JSON, VALIDATION_JSON, REFERENCE_JSON]:
        if not os.path.exists(config_file):
            print(f"❌ Configuratiebestand niet gevonden: {config_file}")
            return
    
    # Voer benchmark uit
    benchmark = PerformanceBenchmark()
    benchmark.run_benchmark_suite()

if __name__ == "__main__":
    main()