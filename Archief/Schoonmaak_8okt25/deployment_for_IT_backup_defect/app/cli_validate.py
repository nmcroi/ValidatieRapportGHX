#!/usr/bin/env python3
# app/cli_validate.py

import argparse, os, sys, traceback

def main():
    parser = argparse.ArgumentParser(description="Valideer prijslijst (CLI).")
    parser.add_argument("--input", required=True, help="Pad naar input .xlsx")
    parser.add_argument("--output", required=True, help="Map voor rapport-output")
    parser.add_argument("--config", required=False, default=os.path.join(os.path.dirname(__file__), "config"),
                        help="Pad naar config-map met header_mapping.json, field_validation_v20.json en reference_lists.json")
    args = parser.parse_args()

    # Absoluut maken
    input_xlsx  = os.path.abspath(args.input)
    output_dir  = os.path.abspath(args.output)
    config_dir  = os.path.abspath(args.config)

    # Bestanden in config
    mapping_json     = os.path.join(config_dir, "header_mapping.json")
    validation_json  = os.path.join(config_dir, "field_validation_v20.json")
    reference_json   = os.path.join(config_dir, "reference_lists.json")
    original_name    = os.path.basename(input_xlsx)

    # Controles
    if not os.path.isfile(input_xlsx):
        print(f"Inputbestand niet gevonden: {input_xlsx}", file=sys.stderr); return 2
    if not os.path.isfile(mapping_json):
        print(f"header_mapping.json niet gevonden: {mapping_json}", file=sys.stderr); return 2
    if not os.path.isfile(validation_json):
        print(f"field_validation_v20.json niet gevonden: {validation_json}", file=sys.stderr); return 2
    if not os.path.isfile(reference_json):
        print(f"reference_lists.json niet gevonden: {reference_json}", file=sys.stderr); return 2
    os.makedirs(output_dir, exist_ok=True)

    # Import en run
    try:
        # project root toevoegen aan sys.path
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        from validator.price_tool import validate_pricelist
        import shutil

        report_path = validate_pricelist(
            input_excel_path=input_xlsx,
            mapping_json_path=mapping_json,
            validation_json_path=validation_json,
            reference_json_path=reference_json,
            original_input_filename=original_name
        )
        if not report_path or not os.path.isfile(report_path):
            print("Validatie voltooid maar geen rapport gevonden/geretourneerd.", file=sys.stderr)
            return 3

        # Doelpad: <output_dir>/<input_basename>_rapport.xlsx
        base_no_ext = os.path.splitext(os.path.basename(input_xlsx))[0]
        target_path = os.path.join(output_dir, f"{base_no_ext}_rapport.xlsx")

        # Kopieer/overschrijf
        os.makedirs(output_dir, exist_ok=True)
        try:
            shutil.copy2(report_path, target_path)
        except Exception as e:
            print(f"Kon rapport niet kopiëren naar {target_path}: {e}", file=sys.stderr)
            return 4

        print(f"REPORT_PATH={target_path}")
        return 0


    except Exception as e:
        print(f"Fout tijdens validatie: {e}", file=sys.stderr)
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
