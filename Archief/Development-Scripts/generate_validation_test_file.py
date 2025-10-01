#!/usr/bin/env python3
"""
Genereert een comprehensive test Excel bestand voor alle validatie regels.
Dit bestand bevat voorbeelden van alle mogelijke fouten en validatie situaties.
"""

import pandas as pd
import json
from datetime import datetime, timedelta

def load_validation_config():
    """Laad de field validation config."""
    with open('field_validation_v20.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def create_test_data():
    """Creëert test data voor alle validatie scenario's."""
    
    # Basis template headers (alle verplichte velden)
    headers = [
        "Artikelnummer", "Artikelnaam", "Artikelomschrijving", "Artikelomschrijving Taal Code",
        "Brutoprijs", "Nettoprijs", "Is BestelbareEenheid", "Is BasisEenheid",
        "Omschrijving Verpakkingseenheid", "UOM Code Verpakkingseenheid", 
        "Inhoud Verpakkingseenheid", "UOM Code Basiseenheid", "Inhoud Basiseenheid",
        "UOM Code Inhoud Basiseenheid", "Omrekenfactor", "GTIN Verpakkingseenheid",
        "Aanvullende Productidentificatie", "GHX BTW Code", "UNSPSC Code",
        "Startdatum Prijs Artikel", "Einddatum Prijs Artikel", "Hoogte", "Breedte", "Diepte",
        "GMDN Code", "EMDN Code", "Code voor Aanvullende Productclassificatie", "Risicoklasse"
    ]
    
    # Test cases - elke rij test verschillende validatie regels
    test_rows = []
    
    # RIJ 1: PERFECT RECORD (geen fouten)
    test_rows.append({
        "Artikelnummer": "PROD-12345-PERFECT",
        "Artikelnaam": "Perfect Product Test",
        "Artikelomschrijving": "Dit is een perfect product voor testing doeleinden",
        "Artikelomschrijving Taal Code": "NL",
        "Brutoprijs": "12.50",
        "Nettoprijs": "10.00",
        "Is BestelbareEenheid": "1",
        "Is BasisEenheid": "1", 
        "Omschrijving Verpakkingseenheid": "1 ST",
        "UOM Code Verpakkingseenheid": "PCE",
        "Inhoud Verpakkingseenheid": "1",
        "UOM Code Basiseenheid": "PCE",
        "Inhoud Basiseenheid": "1",
        "UOM Code Inhoud Basiseenheid": "PCE",
        "Omrekenfactor": "1",
        "GTIN Verpakkingseenheid": "1234567890123",
        "Aanvullende Productidentificatie": "HIBC123",
        "GHX BTW Code": "21",
        "UNSPSC Code": "12345678",
        "Startdatum Prijs Artikel": "2024-01-01",
        "Einddatum Prijs Artikel": "2024-12-31",
        "Hoogte": "10",
        "Breedte": "5", 
        "Diepte": "3",
        "GMDN Code": "",
        "EMDN Code": "",
        "Code voor Aanvullende Productclassificatie": "",
        "Risicoklasse": ""
    })
    
    # RIJ 2: LEGE VERPLICHTE VELDEN (code 700)
    test_rows.append({
        "Artikelnummer": "",  # LEEG - code 700
        "Artikelnaam": "",    # LEEG - code 700
        "Artikelomschrijving": "",
        "Artikelomschrijving Taal Code": "",
        "Brutoprijs": "",     # LEEG - code 700
        "Nettoprijs": "",     # LEEG - code 700
        "Is BestelbareEenheid": "",  # LEEG - code 700
        "Is BasisEenheid": "",       # LEEG - code 700
        "Omschrijving Verpakkingseenheid": "",  # LEEG - code 700
        "UOM Code Verpakkingseenheid": "",      # LEEG - code 700
        "Inhoud Verpakkingseenheid": "",        # LEEG - code 700
        "UOM Code Basiseenheid": "",            # LEEG - code 700
        "Inhoud Basiseenheid": "",              # LEEG - code 700
        "UOM Code Inhoud Basiseenheid": "",     # LEEG - code 700
        "Omrekenfactor": "",                    # LEEG - code 700
        "GTIN Verpakkingseenheid": "",
        "Aanvullende Productidentificatie": "",  # BEIDE LEEG - code 800 (aandachtspunt)
        "GHX BTW Code": "",                     # LEEG - code 700
        "UNSPSC Code": "",                      # LEEG - code 700
        "Startdatum Prijs Artikel": "",         # LEEG - code 700
        "Einddatum Prijs Artikel": "",          # LEEG - code 700
        "Hoogte": "",
        "Breedte": "",
        "Diepte": "",
        "GMDN Code": "",
        "EMDN Code": "",
        "Code voor Aanvullende Productclassificatie": "",
        "Risicoklasse": ""
    })
    
    # RIJ 3: TE KORTE WAARDEN (code 701)
    test_rows.append({
        "Artikelnummer": "AB",  # TE KORT - code 701 (min 3)
        "Artikelnaam": "XY",    # TE KORT - code 701 (min 3)
        "Artikelomschrijving": "OK lang genoeg",
        "Artikelomschrijving Taal Code": "NL",
        "Brutoprijs": "5.00",
        "Nettoprijs": "4.00",
        "Is BestelbareEenheid": "1",
        "Is BasisEenheid": "0",
        "Omschrijving Verpakkingseenheid": "10 ST",
        "UOM Code Verpakkingseenheid": "PCE",
        "Inhoud Verpakkingseenheid": "10",
        "UOM Code Basiseenheid": "PCE",
        "Inhoud Basiseenheid": "1",
        "UOM Code Inhoud Basiseenheid": "PCE",
        "Omrekenfactor": "10",
        "GTIN Verpakkingseenheid": "9876543210987",
        "Aanvullende Productidentificatie": "",
        "GHX BTW Code": "21",
        "UNSPSC Code": "87654321",
        "Startdatum Prijs Artikel": "2024-01-01",
        "Einddatum Prijs Artikel": "2024-12-31",
        "Hoogte": "15",
        "Breedte": "8",
        "Diepte": "4",
        "GMDN Code": "",
        "EMDN Code": "",
        "Code voor Aanvullende Productclassificatie": "",
        "Risicoklasse": ""
    })
    
    # RIJ 4: TE LANGE WAARDEN (code 702)
    test_rows.append({
        "Artikelnummer": "PRODUCT-12345-EXTREMELY-LONG-ARTICLE-NUMBER-EXCEEDING-LIMITS-DEFINITELY",  # TE LANG - code 702 (max 46)
        "Artikelnaam": "Dit is een extreem lange artikelnaam die de toegestane lengte ver overschrijdt en daarom afgekeurd zou moeten worden door het validatie systeem",  # TE LANG - code 702 (max 90)
        "Artikelomschrijving": "Dit is OK",
        "Artikelomschrijving Taal Code": "NL",
        "Brutoprijs": "15.00",
        "Nettoprijs": "12.00",
        "Is BestelbareEenheid": "0",
        "Is BasisEenheid": "1",
        "Omschrijving Verpakkingseenheid": "Dit is veel te lang voor een verpakkingseenheid beschrijving",  # TE LANG - code 702 (max 25)
        "UOM Code Verpakkingseenheid": "PCE",
        "Inhoud Verpakkingseenheid": "1",
        "UOM Code Basiseenheid": "PCE",
        "Inhoud Basiseenheid": "1",
        "UOM Code Inhoud Basiseenheid": "PCE",
        "Omrekenfactor": "1",
        "GTIN Verpakkingseenheid": "",
        "Aanvullende Productidentificatie": "HIBC456",
        "GHX BTW Code": "21",
        "UNSPSC Code": "11111111",
        "Startdatum Prijs Artikel": "2024-01-01",
        "Einddatum Prijs Artikel": "2024-12-31",
        "Hoogte": "",
        "Breedte": "",
        "Diepte": "",
        "GMDN Code": "",
        "EMDN Code": "",
        "Code voor Aanvullende Productclassificatie": "",
        "Risicoklasse": ""
    })
    
    # RIJ 5: DUPLICAAT ARTIKELNUMMER (code 703)
    test_rows.append({
        "Artikelnummer": "PROD-12345-PERFECT",  # DUPLICAAT van rij 1 - code 703
        "Artikelnaam": "Duplicate Product",
        "Artikelomschrijving": "Dit heeft hetzelfde artikelnummer",
        "Artikelomschrijving Taal Code": "EN",
        "Brutoprijs": "20.00",
        "Nettoprijs": "16.00",
        "Is BestelbareEenheid": "1",
        "Is BasisEenheid": "0",
        "Omschrijving Verpakkingseenheid": "5 ST",
        "UOM Code Verpakkingseenheid": "PCE",
        "Inhoud Verpakkingseenheid": "5",
        "UOM Code Basiseenheid": "PCE",
        "Inhoud Basiseenheid": "1",
        "UOM Code Inhoud Basiseenheid": "PCE",
        "Omrekenfactor": "5",
        "GTIN Verpakkingseenheid": "5555555555555",
        "Aanvullende Productidentificatie": "",
        "GHX BTW Code": "21",
        "UNSPSC Code": "55555555",
        "Startdatum Prijs Artikel": "2024-01-01",
        "Einddatum Prijs Artikel": "2024-12-31",
        "Hoogte": "",
        "Breedte": "",
        "Diepte": "",
        "GMDN Code": "",
        "EMDN Code": "",
        "Code voor Aanvullende Productclassificatie": "",
        "Risicoklasse": ""
    })
    
    # RIJ 6: NIET-NUMERIEKE WAARDEN (code 704)
    test_rows.append({
        "Artikelnummer": "PROD-NUMERIC-TEST",
        "Artikelnaam": "Numeriek Test Product",
        "Artikelomschrijving": "",
        "Artikelomschrijving Taal Code": "",
        "Brutoprijs": "NIET-NUMERIEK",      # NIET NUMERIEK - code 704
        "Nettoprijs": "abc123",             # NIET NUMERIEK - code 704
        "Is BestelbareEenheid": "ja",       # NIET BOOLEAN - code 715
        "Is BasisEenheid": "nee",           # NIET BOOLEAN - code 715
        "Omschrijving Verpakkingseenheid": "WRONG 999",  # Format mismatch - code 803
        "UOM Code Verpakkingseenheid": "PCE",
        "Inhoud Verpakkingseenheid": "text", # NIET NUMERIEK - code 704
        "UOM Code Basiseenheid": "PCE", 
        "Inhoud Basiseenheid": "xyz",        # NIET NUMERIEK - code 704
        "UOM Code Inhoud Basiseenheid": "PCE",
        "Omrekenfactor": "not-a-number",     # NIET NUMERIEK - code 704
        "GTIN Verpakkingseenheid": "",
        "Aanvullende Productidentificatie": "",
        "GHX BTW Code": "21",
        "UNSPSC Code": "66666666",
        "Startdatum Prijs Artikel": "2024-01-01",
        "Einddatum Prijs Artikel": "2024-12-31",
        "Hoogte": "",
        "Breedte": "",
        "Diepte": "",
        "GMDN Code": "",
        "EMDN Code": "",
        "Code voor Aanvullende Productclassificatie": "",
        "Risicoklasse": ""
    })
    
    # RIJ 7: ONGELDIGE LIJST WAARDEN (code 707)
    test_rows.append({
        "Artikelnummer": "PROD-LIST-TEST", 
        "Artikelnaam": "Lijst Validatie Test",
        "Artikelomschrijving": "Test voor ongeldige lijst waarden",
        "Artikelomschrijving Taal Code": "XX",  # ONGELDIGE TAALCODE - code 707
        "Brutoprijs": "25.00",
        "Nettoprijs": "20.00",
        "Is BestelbareEenheid": "1",
        "Is BasisEenheid": "1",
        "Omschrijving Verpakkingseenheid": "1 ST",
        "UOM Code Verpakkingseenheid": "INVALID_UOM",  # ONGELDIGE UOM - code 707
        "Inhoud Verpakkingseenheid": "1",
        "UOM Code Basiseenheid": "WRONG_UOM",          # ONGELDIGE UOM - code 707
        "Inhoud Basiseenheid": "1",
        "UOM Code Inhoud Basiseenheid": "BAD_UOM",     # ONGELDIGE UOM - code 707
        "Omrekenfactor": "1",
        "GTIN Verpakkingseenheid": "",
        "Aanvullende Productidentificatie": "",
        "GHX BTW Code": "999",  # ONGELDIGE BTW CODE - code 707
        "UNSPSC Code": "77777777",
        "Startdatum Prijs Artikel": "2024-01-01", 
        "Einddatum Prijs Artikel": "2024-12-31",
        "Hoogte": "",
        "Breedte": "",
        "Diepte": "",
        "GMDN Code": "",
        "EMDN Code": "",
        "Code voor Aanvullende Productclassificatie": "",
        "Risicoklasse": ""
    })
    
    # RIJ 8: UOM CONFLICT - BEIDE 1 MAAR VERSCHILLENDE UOM (code 801)
    test_rows.append({
        "Artikelnummer": "PROD-UOM-CONFLICT",
        "Artikelnaam": "UOM Conflict Test",
        "Artikelomschrijving": "",
        "Artikelomschrijving Taal Code": "",
        "Brutoprijs": "30.00",
        "Nettoprijs": "25.00",
        "Is BestelbareEenheid": "1",         # BEIDE 1
        "Is BasisEenheid": "1",              # BEIDE 1
        "Omschrijving Verpakkingseenheid": "1 ST",
        "UOM Code Verpakkingseenheid": "PCE", # VERSCHILLEND - code 801
        "Inhoud Verpakkingseenheid": "2",     # NIET 1 terwijl beide=1 - code 805
        "UOM Code Basiseenheid": "KGM",       # VERSCHILLEND - code 801
        "Inhoud Basiseenheid": "3",           # NIET 1 terwijl beide=1 - code 805
        "UOM Code Inhoud Basiseenheid": "PCE",
        "Omrekenfactor": "1",
        "GTIN Verpakkingseenheid": "",
        "Aanvullende Productidentificatie": "",  # BEIDE LEEG - code 800
        "GHX BTW Code": "21",
        "UNSPSC Code": "88888888",
        "Startdatum Prijs Artikel": "2024-01-01",
        "Einddatum Prijs Artikel": "2024-12-31",
        "Hoogte": "10",  # INCOMPLETE SET - code 804
        "Breedte": "",   # ONTBREEKT
        "Diepte": "",    # ONTBREEKT  
        "GMDN Code": "",
        "EMDN Code": "",
        "Code voor Aanvullende Productclassificatie": "",
        "Risicoklasse": ""
    })
    
    # RIJ 9: MEDISCHE PRODUCTEN - RISICOKLASSE CONFLICT (code 726/727)
    test_rows.append({
        "Artikelnummer": "PROD-MEDICAL-TEST",
        "Artikelnaam": "Medisch Product Test",
        "Artikelomschrijving": "",
        "Artikelomschrijving Taal Code": "",
        "Brutoprijs": "100.00",
        "Nettoprijs": "85.00",
        "Is BestelbareEenheid": "0",
        "Is BasisEenheid": "1",
        "Omschrijving Verpakkingseenheid": "1 ST",
        "UOM Code Verpakkingseenheid": "PCE",
        "Inhoud Verpakkingseenheid": "1",
        "UOM Code Basiseenheid": "PCE",
        "Inhoud Basiseenheid": "1",
        "UOM Code Inhoud Basiseenheid": "PCE",
        "Omrekenfactor": "1",
        "GTIN Verpakkingseenheid": "2222222222222",
        "Aanvullende Productidentificatie": "",
        "GHX BTW Code": "21",
        "UNSPSC Code": "42111111",  # MEDICAL PRODUCT
        "Startdatum Prijs Artikel": "2024-01-01",
        "Einddatum Prijs Artikel": "2024-12-31",
        "Hoogte": "",
        "Breedte": "",
        "Diepte": "",
        "GMDN Code": "",    # LEEG terwijl medisch product
        "EMDN Code": "",    # LEEG terwijl medisch product
        "Code voor Aanvullende Productclassificatie": "76",  # MDR/IVDR
        "Risicoklasse": "INVALID_RISK_CLASS"  # ONGELDIGE COMBO - code 726
    })
    
    # RIJ 10: DATUM PROBLEMEN
    test_rows.append({
        "Artikelnummer": "PROD-DATE-TEST",
        "Artikelnaam": "Datum Test Product",
        "Artikelomschrijving": "",
        "Artikelomschrijving Taal Code": "",
        "Brutoprijs": "50.00",
        "Nettoprijs": "40.00",
        "Is BestelbareEenheid": "1",
        "Is BasisEenheid": "0",
        "Omschrijving Verpakkingseenheid": "20 WRONG",  # Format mismatch
        "UOM Code Verpakkingseenheid": "PCE",
        "Inhoud Verpakkingseenheid": "20",
        "UOM Code Basiseenheid": "PCE",
        "Inhoud Basiseenheid": "1",
        "UOM Code Inhoud Basiseenheid": "PCE",
        "Omrekenfactor": "20",
        "GTIN Verpakkingseenheid": "",
        "Aanvullende Productidentificatie": "HIBC789",
        "GHX BTW Code": "21",
        "UNSPSC Code": "99999999",
        "Startdatum Prijs Artikel": "2024-12-31",  # START NA EIND
        "Einddatum Prijs Artikel": "2024-01-01",   # EIND VOOR START
        "Hoogte": "5",
        "Breedte": "5", 
        "Diepte": "",  # INCOMPLETE SET - code 804
        "GMDN Code": "",
        "EMDN Code": "",
        "Code voor Aanvullende Productclassificatie": "",
        "Risicoklasse": ""
    })
    
    return headers, test_rows

def main():
    """Hoofdfunctie om het test bestand te genereren."""
    print("🧪 Genereren comprehensive validatie test bestand...")
    
    # Laad config
    try:
        config = load_validation_config()
        print(f"✅ JSON v{config['version']} configuratie geladen")
    except Exception as e:
        print(f"❌ Fout bij laden configuratie: {e}")
        return
    
    # Genereer test data
    headers, test_rows = create_test_data()
    
    # Maak DataFrame
    df = pd.DataFrame(test_rows, columns=headers)
    
    # Voeg beschrijvende eerste rij toe
    description_row = {col: f"Test scenario voor {col}" for col in headers}
    description_row["Artikelnummer"] = "BESCHRIJVING: Dit bestand test alle validatie regels"
    description_row["Artikelnaam"] = "Elke rij test specifieke validatie scenario's"
    
    # Insert beschrijving als eerste rij
    df = pd.concat([pd.DataFrame([description_row]), df], ignore_index=True)
    
    # Genereer bestandsnaam met timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"COMPREHENSIVE_VALIDATION_TEST_{timestamp}.xlsx"
    
    # Schrijf naar Excel
    try:
        df.to_excel(filename, index=False, engine='openpyxl')
        print(f"✅ Test bestand gegenereerd: {filename}")
        print(f"📊 {len(df)} rijen, {len(headers)} kolommen")
        print(f"🎯 Test scenario's:")
        print("   • Rij 1: Perfecte data (geen fouten)")
        print("   • Rij 2: Lege verplichte velden (code 700)")
        print("   • Rij 3: Te korte waarden (code 701)")  
        print("   • Rij 4: Te lange waarden (code 702)")
        print("   • Rij 5: Duplicaat artikelnummer (code 703)")
        print("   • Rij 6: Niet-numerieke waarden (code 704)")
        print("   • Rij 7: Ongeldige lijst waarden (code 707)")
        print("   • Rij 8: UOM conflicten (codes 801, 805)")
        print("   • Rij 9: Medische product issues")
        print("   • Rij 10: Datum problemen")
        print("   🎯 Alle 7 aandachtspunten worden getriggerd!")
        return filename
        
    except Exception as e:
        print(f"❌ Fout bij schrijven Excel: {e}")
        return None

if __name__ == "__main__":
    result = main()
    if result:
        print(f"\n🚀 Klaar! Test met: {result}")