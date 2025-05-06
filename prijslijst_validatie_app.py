# prijslijst_validatie_app.py

import streamlit as st
import pandas as pd
import os
import tempfile # Nodig om geupload bestand tijdelijk op te slaan
import logging # Om logging uit de tool te zien (optioneel)
import io
import zipfile

# Importeer de hoofdfunctie uit price_tool.py
# Zorg dat validator map bestaat met __init__.py, price_tool.py, rapport_utils.py
try:
    from validator.price_tool import validate_pricelist
except ImportError as e:
    st.error(f"Fout bij importeren validatiemodule: {e}")
    st.error("Zorg ervoor dat de map 'validator' bestaat met daarin __init__.py, price_tool.py en rapport_utils.py.")
    st.stop() # Stop de app als de import faalt

# --- Basis Configuratie ---
# Pad naar de configuratiebestanden (pas aan indien nodig)
# Gaat er hier vanuit dat ze in dezelfde map staan als de app
MAPPING_JSON = "header_mapping.json"
VALIDATION_JSON = "field_validation_v18.json"

# Logging configureren (optioneel, toont logs in console waar Streamlit draait)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Streamlit UI Opzet ---
st.set_page_config(layout="wide") # Gebruik meer schermbreedte
st.title("GHX Prijslijst Validatie Tool")
st.markdown("Upload hier de GHX prijslijst template (.xlsx of .xls) om deze te valideren.")

# Controleer of configuratiebestanden bestaan
if not os.path.exists(MAPPING_JSON):
    st.error(f"Mapping configuratiebestand niet gevonden: {MAPPING_JSON}")
    st.stop()
if not os.path.exists(VALIDATION_JSON):
    st.error(f"Validatie configuratiebestand niet gevonden: {VALIDATION_JSON}")
    st.stop()

# Initialiseer session state voor rapport data als deze nog niet bestaat
if 'report_data' not in st.session_state:
    st.session_state.report_data = {}

# File uploader - Accept multiple files
uploaded_files = st.file_uploader("Kies een of meerdere Excel-bestanden", type=["xlsx", "xls"], accept_multiple_files=True)

# Check if files have been uploaded
if uploaded_files:
    st.info(f"{len(uploaded_files)} bestand(en) geselecteerd.")

    # Knop om validatie te starten
    if st.button(f"Start Validatie & Genereer Rapporten voor {len(uploaded_files)} bestand(en)"):
        # Reset/clear previous report data when starting new validation
        st.session_state.report_data = {}
        # Loop through each uploaded file
        for uploaded_file in uploaded_files:
            st.markdown("***") # Separator line
            st.subheader(f"Bezig met verwerken: {uploaded_file.name}")
            original_filename = uploaded_file.name
            temp_file_path = None # Reset for each file

            try:
                # Create a temporary file for THIS file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    temp_file_path = tmp_file.name

                # Start validation with a spinner for THIS file
                with st.spinner(f"Validatie en rapportage voor '{original_filename}' bezig..."):
                    logging.info(f"Aanroepen validate_pricelist voor {original_filename}...")
                    report_path = validate_pricelist(
                        input_excel_path=temp_file_path,
                        mapping_json_path=MAPPING_JSON,
                        validation_json_path=VALIDATION_JSON,
                        original_input_filename=original_filename,
                    )
                    logging.info(f"validate_pricelist voltooid voor {original_filename}.")

                # Remove the temporary file after validation is done
                if os.path.exists(temp_file_path):
                     os.remove(temp_file_path)

                # Show result and download button for THIS file
                if report_path and os.path.exists(report_path):
                    st.success(f"Validatierapport voor '{original_filename}' succesvol gegenereerd!")
                    try:
                        with open(report_path, "rb") as fp:
                            report_bytes = fp.read()
                        download_filename = os.path.basename(report_path)
                        # IMPORTANT: Use a unique key for each download button
                        st.download_button(
                            label=f"Download Rapport voor '{original_filename}'",
                            data=report_bytes,
                            file_name=download_filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"download_btn_{original_filename}" # Key for button itself (optional but good practice)
                        )
                        # Store report data in session state
                        st.session_state.report_data[original_filename] = {
                            'bytes': report_bytes,
                            'filename': download_filename
                        }
                    except Exception as read_err:
                         st.error(f"Kon rapport '{download_filename}' niet lezen voor download: {read_err}")
                else:
                    st.error(f"Genereren van rapport voor '{original_filename}' mislukt.")

            except FileNotFoundError as e:
                 st.error(f"Bestandsfout bij '{original_filename}': {e}")
            except ImportError as e:
                 st.error(f"Import fout bij '{original_filename}': {e}.")
            except Exception as e:
                st.error(f"Onverwachte fout bij '{original_filename}': {e}")
            finally:
                # Ensure the temporary file for THIS iteration is cleaned up
                 if temp_file_path and os.path.exists(temp_file_path):
                     try:
                         os.remove(temp_file_path)
                         logging.info(f"Tijdelijk bestand {temp_file_path} opgeruimd.")
                     except Exception as del_err:
                         logging.error(f"Kon tijdelijk bestand {temp_file_path} niet verwijderen: {del_err}")

        st.markdown("***") # Separator after all files
        st.success("Alle geselecteerde bestanden zijn verwerkt.")

# --- Display Download Buttons from Session State (outside the main button click logic) ---
if st.session_state.report_data:
    st.markdown("### Beschikbare Rapporten:")
    for original_filename, data in st.session_state.report_data.items():
        st.download_button(
            label=f"Download Rapport voor '{original_filename}'",
            data=data['bytes'],
            file_name=data['filename'],
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"dl_{original_filename}" # Unique key per button
        )

    # Add Download All button if more than one report exists
    if len(st.session_state.report_data) > 1:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for original_filename, data in st.session_state.report_data.items():
                # Use the generated report filename inside the zip
                zip_file.writestr(data['filename'], data['bytes'])

        st.download_button(
            label="Download Alle Rapporten (.zip)",
            data=zip_buffer.getvalue(),
            file_name="validatie_rapporten.zip",
            mime="application/zip",
            key="download_all_zip"
        )

else:
    st.info("Wacht op upload van een of meerdere Excel-bestanden.")