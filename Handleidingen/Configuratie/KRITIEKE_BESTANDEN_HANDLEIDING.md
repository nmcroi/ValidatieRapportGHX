# 🔥 KRITIEKE BESTANDEN HANDLEIDING

## Template Generator Files - Essentiële Synchronisatie

Deze handleiding beschrijft de **3 kritieke bestanden** in de Template Generator Files map die **altijd up-to-date** moeten zijn met de **Project TemplateTree app v3** voor correcte validatie.

---

## 🎯 **OVERZICHT KRITIEKE BESTANDEN**

### 1. **`field_mapping.json`** 
- **Prioriteit:** 🔥 KRITIEK
- **Gebruikt door:** `validator/price_tool.py:329`
- **Functie:** `load_field_mapping()`
- **Doel:** Field configuratie en visibility rules voor Template Generator templates

### 2. **`institution_codes.json`**
- **Prioriteit:** 🔥 KRITIEK  
- **Gebruikt door:** `validator/config_manager.py:49`
- **Functie:** `load_institution_codes()`
- **Doel:** Institution mapping voor correcte template contextualisering

### 3. **`template_versions.json`**
- **Prioriteit:** 🟡 MONITORING
- **Status:** Documentatie verwijzingen, potentiële toekomstige functionaliteit
- **Doel:** Versie tracking voor Template Generator templates

---

## 🔄 **SYNCHRONISATIE PROTOCOL**

### **BRON:** Project TemplateTree app v3
### **DOEL:** Template Generator Files (validatie tool)

| Bestand | Synchronisatie Frequentie | Impact bij Outdated |
|---------|---------------------------|---------------------|
| `field_mapping.json` | **Bij elke TG wijziging** | ❌ TG validatie valt uit |
| `institution_codes.json` | **Bij nieuwe instellingen** | ❌ Verkeerde institution mapping |
| `template_versions.json` | **Bij versie releases** | ⚠️ Mogelijke detectie problemen |

---

## 📋 **SYNCHRONISATIE CHECKLIST**

### **Template Generator Updates:**
- [ ] **Nieuwe field toegevoegd/verwijderd** → Update `field_mapping.json`
- [ ] **Field visibility gewijzigd** → Update `field_mapping.json`
- [ ] **Nieuwe instelling toegevoegd** → Update `institution_codes.json`
- [ ] **Template versie released** → Update `template_versions.json`

### **Validatie Impact Check:**
- [ ] Test TG template validatie na update
- [ ] Controleer institution herkenning
- [ ] Verificeer field counts in rapporten

---

## 🚨 **WAARSCHUWINGEN**

### **NOOIT HANDMATIG BEWERKEN:**
Deze bestanden moeten **alleen gekopieerd** worden vanuit Project TemplateTree app v3. Handmatige wijzigingen kunnen leiden tot:
- ❌ Incorrecte validatie resultaten
- ❌ Template detectie problemen  
- ❌ Verkeerde statistieken in rapporten

### **BACKUP VOOR UPDATES:**
```bash
# Maak backup voor update
cp field_mapping.json field_mapping.json.backup
cp institution_codes.json institution_codes.json.backup
cp template_versions.json template_versions.json.backup
```

---

## 🔍 **VERIFICATIE PROCEDURES**

### **Na Synchronisatie Test:**
1. **Start validatie tool:** `streamlit run prijslijst_validatie_app.py`
2. **Upload TG template** van verschillende versies
3. **Controleer debug output:** Template type detectie correct?
4. **Verificeer rapport:** Field counts kloppen?

### **Error Indicators:**
- `Field mapping niet gevonden` → field_mapping.json probleem
- `Institution codes niet geladen` → institution_codes.json probleem  
- `Template type: Unknown` → Mogelijk template_versions.json issue

---

## 📁 **BESTANDSLOCATIES**

### **Validatie Tool:**
```
Template Generator Files/
├── field_mapping.json          # 🔥 KRITIEK
├── institution_codes.json      # 🔥 KRITIEK  
├── template_versions.json      # 🟡 MONITORING
└── KRITIEKE_BESTANDEN_HANDLEIDING.md
```

### **Bron (Project TemplateTree app v3):**
```
[Pad naar Project TemplateTree app v3]/
├── field_mapping.json
├── institution_codes.json
└── template_versions.json
```

---

## 🤝 **VERANTWOORDELIJKHEDEN**

- **Template Generator Team:** Updates naar Project TemplateTree app v3
- **Validatie Tool Maintainer:** Synchronisatie naar Template Generator Files
- **QA:** Verificatie na elke synchronisatie

---

## 📞 **SUPPORT**

Bij problemen met synchronisatie:
1. Check deze handleiding
2. Controleer bestandspaden
3. Test met bekende template  
4. Contact: Niels Croiset

---

*Laatste update: 1 oktober 2025*
*Versie: 1.0*