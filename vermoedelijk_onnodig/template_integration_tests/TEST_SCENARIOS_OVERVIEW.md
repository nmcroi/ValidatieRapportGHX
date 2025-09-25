# Template Integration Test Scenarios

## Generated Test Templates (11 september 2025)

### 🧪 Template Generator Templates (met stamp)

1. **NFU Scenario** - `TEST_NFU_SCENARIO.xlsx`
   - **Preset Code:** `S-M-0-0-0-0-5-V72-M5`
   - **Template:** Standard (GHXstandaardTemplate v25.1.xlsx)
   - **Instellingen:** Alle 5 NFU ziekenhuizen
   - **Product types:** Medisch
   - **Visible fields:** 72 van 103
   - **Mandatory fields:** 5
   - **Test focus:** NFU instelling detection, medische product context

2. **Staffel Scenario** - `TEST_STAFFEL_SCENARIO.xlsx` 
   - **Preset Code:** `F-F-0-0-1-0-2-V57-M5`
   - **Template:** Staffel (template_staffel.xlsx)
   - **Instellingen:** Hospital Logistics, Zorgservice XL
   - **Product types:** Facilitair
   - **Visible fields:** 57 van 103 
   - **Mandatory fields:** 5
   - **Test focus:** Staffel template detection, field collapsing

3. **GS1 Scenario** - `TEST_GS1_SCENARIO.xlsx`
   - **Preset Code:** `S-X-0-1-0-1-2-V101-M8`
   - **Template:** Standard + GS1 modus
   - **Instellingen:** Amsterdam UMC, UU
   - **Product types:** Medisch + Lab (mixed)
   - **GS1 mode:** gs1 (sync enabled)
   - **Chemicals:** Yes
   - **Visible fields:** 101 van 103 (bijna alles zichtbaar!)
   - **Mandatory fields:** 8
   - **Test focus:** GS1 context, chemical fields, mixed product types

### 📋 Reference Templates (zonder stamp)

4. **Default Template** - `TEST_DEFAULT_TEMPLATE.xlsx`
   - **Template:** GHXstandaardTemplate v25.1.xlsx (clean)
   - **Test focus:** Default template detection, baseline validation

5. **Old Supplier Template** - `TEST_OLD_SUPPLIER_TEMPLATE.xlsx`
   - **Template:** GHXstandaardTemplate v24.07B.xlsx (archief)
   - **Test focus:** Legacy template detection, backward compatibility

## Test Plan

### Phase 1: Stamp Detection
- [ ] Template Generator templates: stamp gedetecteerd?
- [ ] Default template: geen stamp, default modus?
- [ ] Old supplier template: geen stamp, default modus?

### Phase 2: Context Recognition
- [ ] NFU scenario: juiste instelling mandatory fields?
- [ ] GS1 scenario: GS1 fields visible/mandatory?
- [ ] Staffel scenario: staffel columns visible?

### Phase 3: Field Statistics
- [ ] Template Generator: alleen visible fields in stats?
- [ ] Collapsed fields uitgesloten van counts?
- [ ] Mandatory field counts correct?

### Phase 4: Template-Aware Validation
- [ ] Verschillende validation regels per template type?
- [ ] Context-specific error messages?
- [ ] Institution-specific mandatory field validation?