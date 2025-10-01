# 🔄 Sync Handleiding: Template Generator ↔ Validatietool

## 📋 **Wanneer deze handleiding gebruiken**

Gebruik deze handleiding wanneer je wijzigingen maakt in de **Template Generator** die invloed hebben op de **Validatietool**.

---

## 🏥 **SCENARIO 1: Nieuwe Organisatie/Instelling Toevoegen**

### Template Generator wijziging:
✅ Nieuwe instelling toegevoegd aan Template Generator configuratie

### Validatietool sync acties:
1. **Update `institution_codes.json`**:
   ```bash
   nano "Template Generator Files/institution_codes.json"
   ```
   - Voeg nieuwe instelling toe met code, naam en extra mandatory fields
   - Format: `"code": {"name": "Naam", "extra_mandatory_fields": ["veld1"]}`

2. **Test nieuwe code parsing**:
   - Test met Template Generator template die nieuwe code bevat
   - Controleer dat organisatie correct wordt getoond in template tabel

### Voorbeeld:
```json
"nieuw": {
  "name": "Nieuwe Zorginstelling",
  "extra_mandatory_fields": ["Levertijd"]
}
```

---

## 📊 **SCENARIO 2: Field Mapping Wijziging**  

### Template Generator wijziging:
✅ Veld toegevoegd/gewijzigd in field_mapping.json

### Validatietool sync acties:
1. **Kopieer field_mapping.json**:
   ```bash
   # Van Template Generator naar Validatietool
   cp "pad/naar/template-generator/field_mapping.json" "Template Generator Files/field_mapping.json"
   ```

2. **Test field visibility**:
   - Upload Template Generator template
   - Controleer dat nieuwe/gewijzigde velden correct zichtbaar/verborgen zijn
   - Check mandatory field count klopt met stamp (bijv. M18 = 18 velden)

---

## 🆕 **SCENARIO 3: Nieuwe Kolom Toegevoegd**

### Template Generator wijziging:
✅ Nieuwe kolom toegevoegd aan GHX template (zie ook: WORKFLOW_NIEUWE_KOLOM.md)

### Validatietool sync acties:
1. **Update field_mapping.json** (zie Scenario 2)

2. **Update template_versions.json** als nieuwe versie:
   ```json
   "25.2": {
     "release_date": "2025-XX-XX", 
     "total_fields": 104,  // +1 veld
     "mandatory_fields": 17,  // of meer als mandatory
     "features": ["Nieuwe kolom: Veldnaam toegevoegd"]
   }
   ```

3. **Update field_validation_v20.json** indien nodig:
   - Nieuwe validatieregels voor het nieuwe veld
   - Reference lists uitbreiden indien nodig

---

## 📈 **SCENARIO 4: Mandatory Fields Wijziging**

### Template Generator wijziging: 
✅ Veld wordt mandatory/niet-mandatory gemaakt

### Validatietool sync acties:
1. **Update field_mapping.json** (zie Scenario 2)

2. **Test mandatory count**:
   - Genereer Template Generator template
   - Check dat stamp code klopt (bijv. M17 → M18 bij +1 mandatory)
   - Test validatietool toont correcte mandatory count

3. **Update documentatie**:
   - Update README.md met nieuwe mandatory field count
   - Update template_versions.json indien van toepassing

---

## 🔢 **SCENARIO 5: Template Versie Upgrade**

### Template Generator wijziging:
✅ Nieuwe template versie uitgebracht (bijv. v25.1 → v25.2)

### Validatietool sync acties:
1. **Update template_versions.json**:
   - Voeg nieuwe versie toe met correcte field counts
   - Update A2 identifier voor detectie
   - Zet oude versie op status: "legacy"

2. **Test versie detectie**:
   - Upload oude en nieuwe templates
   - Controleer dat correct versienummer wordt getoond in template tabel

---

## ⚠️ **BELANGRIJKE CHECKS NA ELKE SYNC**

### 🧪 **Altijd testen**:
1. **Template Generator templates**: Upload en controleer template tabel info
2. **Nieuwe Generatie templates**: Test A2 versie detectie  
3. **Oude templates**: Controleer dat fallback werkt
4. **Mandatory fields**: Count moet exact kloppen met Template Generator stamp

### 📝 **Documentatie updaten**:
- Update `last_updated` datums in config files
- Commit wijzigingen naar Git met duidelijke message
- Test op verschillende template types voordat je pushed

---

## 🆘 **Troubleshooting**

### Probleem: "Institution code niet herkend"
**Oplossing**: Check `institution_codes.json` en zorg dat nieuwe code is toegevoegd

### Probleem: "Mandatory field count klopt niet" 
**Oplossing**: Update `field_mapping.json` en test opnieuw

### Probleem: "Template versie wordt niet gedetecteerd"
**Oplossing**: Check A2 cel tekst en update `template_versions.json`

---

## 📞 **Contact**

Bij twijfels of problemen: check eerst deze handleiding, dan test grondig!

*Laatste update: 2025-09-25*