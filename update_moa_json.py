"""Update glycine_ip.json: add procedures for all tests + MOA revision history."""
import json, pathlib

p = pathlib.Path("config/products/glycine_ip.json")
data = json.loads(p.read_bytes().lstrip(b'\xef\xbb\xbf'))

# ── PROCEDURES FOR MAIN TESTS ────────────────────────────────────────────────

PROCEDURES = {
    "Description": (
        "Take about 1.0 g of sample and spread to clean Petri dish. "
        "Check product visually for colour."
    ),
    "Solubility": (
        "Take about 1.0 g of sample into 10 ml of water and check solubility.\n"
        "Take about 10 mg of sample into 100 ml of ethanol and check solubility.\n"
        "Take about 10 mg of sample into 100 ml of ether and check solubility."
    ),
    "Appearance of solution": (
        "Sample Solution: Dissolve 10 gm sample in 100 ml water.\n"
        "Standard Suspension: Dissolve 1.0 gm of hydrazine sulphate in sufficient water to produce "
        "100 ml and set aside for about 6 hours. To 25 ml of this solution add 25 ml of a 10 % w/v "
        "solution of Hexamine, mix well and allow to stand for 24 hours. Keep in a glass container "
        "with a smooth internal surface in which the Suspension does not adhere to the glass. Store "
        "in this manner, the Suspension is stable for about 2 months.\n"
        "Prepare the diluted standard suspension by diluting 15 ml of the well mixed standard "
        "suspension to 1000 ml with water. The standard suspension should be used within 24 hours of "
        "preparation.\n"
        "Opalescence Standards: Prepare opalescence standards OS1 by mixing aliquots of standard "
        "suspension with water as indicated in Table 1. Each opalescence standard should be shaken "
        "well before use.\n"
        "Procedure: Transfer to a flat-bottom test tube of neutral glass, 15 to 25 mm in diameter, a "
        "suitable volume of the solution under examination such that the test-tube is filled to a depth "
        "of 40 mm. Into another matched test-tube add the same volume of the freshly prepared "
        "opalescence standard. After 5 minutes compare the contents of the test tubes against a black "
        "background by viewing under diffused light down the vertical axis of the tubes.\n"
        "Reference Solution (YS7): Prepare by mixing FCS 0.8 ml, CCS 0.2 ml and hydrochloric acid "
        "(1%w/v) 99.0 ml.\n"
        "Method: Transfer to a flat bottom test tube of neutral glass 15 to 25 mm in diameter, a "
        "suitable volume of a liquid been examined such that the test tube is filled to a depth of 40 mm. "
        "Into another matched test tube add the same volume of water or the solvent used for preparing "
        "the solution being examined or of the reference solution stated in the individual monograph."
    ),
    "pH": (
        "Determine the pH of 5% w/v solution of test sample on suitable pH meter."
    ),
    "Chlorides": (
        "Dissolve 2.5 g of the substance in 20 mL of water. Add 10 ml of dilute nitric acid, except "
        "when nitric acid is used in the preparation of the solution, dilute to 50 ml with water and "
        "add 1 ml of 0.1 M silver nitrate. Stir immediately with a glass rod and allow to stand for "
        "5 minutes protected from light. When viewed transversely against a black background any "
        "opalescence produced is not more intense than that obtained by treating a mixture of 10.0 ml "
        "of chloride standard solution and 5 ml of water in the same manner."
    ),
    "Heavy metals": (
        "Refer Method 14.0"
    ),
    "Sulphated ash": (
        "Ignite a silica or platinum crucible at 600 ± 50° for 30 minutes, allow to cool in a "
        "desiccator over silica gel or other suitable desiccant and weigh. Place the prescribed amount of "
        "the substance under examination in the crucible and weigh. Moisten the substance under "
        "examination with a small amount of sulfuric acid (usually 1 ml) and heat gently at as low a "
        "temperature as practicable until the sample is thoroughly charred. After cooling, moisten the "
        "residue with a small amount of sulfuric acid (usually 1 ml), heat gently until white fumes are "
        "no longer evolved and ignite at 600 ± 50° until the residue is completely incinerated. "
        "Ensure that flames are not produced at any time during the procedure. Allow the crucible to cool "
        "in a desiccator over silica gel or other suitable desiccant, weigh it again and calculate the "
        "percentage of residue.\n"
        "If the amount of residue so obtained exceeds the prescribed limit, repeat the moistening with "
        "sulfuric acid and ignition, as previously, for 30 minutes periods until 2 consecutive weighings "
        "do not differ by more than 0.5 mg or until the percentage of residue complies with the "
        "prescribed limit.\n"
        "Sulphated Ash = Weight of residue x 100 / Weight of sample"
    ),
    "Loss on drying": (
        "Mix and accurately weigh the 1.0 g of the substance to be tested. Tare a glass-stoppered, "
        "shallow weighing bottle that has been dried for 30 minutes under the same conditions to be "
        "employed in the determination. Put the test specimen in the bottle, replace the cover, and "
        "accurately weigh the bottle and the contents. By gentle, sidewise shaking, distribute the test "
        "specimen as evenly as practicable to a depth of about 5 mm generally, and not more than 10 mm "
        "in the case of bulky materials. Place the loaded bottle in the drying chamber, removing the "
        "stopper and leaving it also in the chamber. Dry the test specimen at the 105° and for the 2 hours.\n"
        "Calculation: % LOD = Loss of weight x 100 / Weight of sample (g)"
    ),
    "Assay (On dried basis)": (
        "Dissolve 0.15 g in 100 ml of anhydrous glacial acetic acid. Immediately after dissolution "
        "titrate with 0.1 M perchloric acid, using 0.05 ml of crystal violet solution as indicator. "
        "Carry out blank titration.\n"
        "1 mL of 0.1 M perchloric acid is equivalent to 0.00751 g of C₂H₅NO₂.\n"
        "% Assay (on dried basis) = (VS − VB) × M × F × 100 × 100 / "
        "(0.1 × Sample weight in gm × (100 − % LOD))"
    ),
}

IDENTIFICATION_SUB_PROCEDURES = {
    "By IR Spectrophotometry": (
        "Blank preparation: Take 100 mg of KBr to be analysed. Load blank sample into DRS unit and "
        "take IR by following steps carried out for the background.\n"
        "Standard preparation: Prepare standard by mixing about 100 mg of KBr and 10 mg of standard. "
        "Load standard into DRS unit and take IR.\n"
        "Sample preparation: Prepare sample by mixing about 100 mg of KBr and 10 mg of substance to "
        "be analysed. Load sample into DRS unit and take IR.\n"
        "Procedure: Ensure that instrument is clean and free from dust. Switch ON the instrument and "
        "log in with respective ID as an authorized analyst. Set the desire instrument parameters. "
        "Allow the IR to stabilize; IR takes some time for stabilization. After successful "
        "initialization, Install DRS unit in the IR. Clean the sample holder. Prepare fine powder of "
        "KBr in the mortar. Fill KBr powder into sample holder. Wipe excess powder with tissue paper "
        "and fix it to DRS unit. Select the method of background. Method parameters should be loaded "
        "and change the parameters as require. Now IR is ready; take the KBr in sample holder and scan "
        "the background. Discard KBr and clean the unit, standard and sample. Load into DRS unit and "
        "take IR by following steps. Select IR graph of standard and sample, Purity index or comparison "
        "spectra shall be opened as follow. Compare purity index with established limit to conclude the "
        "IR result."
    ),
    "By Chemical test": (
        "Dissolve 50 mg in 5 ml of water, add 1 ml of sodium hypochlorite solution (3% Cl), boil for "
        "2 minutes, add 1 ml of hydrochloric acid and boil for 4 to 5 minutes. To the resulting "
        "solution add 2 ml of hydrochloric acid and 1 ml of a 2% w/v solution of resorcinol, boil for "
        "1 minute, cool, add 10 ml of water and mix. To 5 ml of this solution add 6 ml of 2 M sodium "
        "hydroxide."
    ),
}

ADDITIONAL_PROCEDURES = {
    "Sieve analysis": (
        "Assemble the sieves in consecutive order by opening size, with the coarsest sieve at the top, "
        "and place a solid-collecting pan below the bottom sieve. Place 100.0 g of the test sample on "
        "the top sieve, and close the sieve with solid cover. Securely fasten the assembly to the sieve "
        "shaker, and operate the shaker for 15 minutes. After 15 minutes examine the sample."
    ),
    "Bulk Density": (
        "Take 50 ml of measuring cylinder tare weight it and pass the powder to the measuring cylinder "
        "until 50 ml marked label. Weigh the measuring cylinder with powder fill up to 50 ml, and note "
        "the weight.\n"
        "Calculation: weight of sample (g) / volume of sample (ml)"
    ),
    "Elemental impurities by AAS (As per ICH Q3D)": (
        "Sample Solution: Weigh 10.0 g of sample and transfer in 100 ml dried volumetric flask. Add "
        "20 ml of Nitric acid (1:1) and 20 ml of HCl (1:1). Digest the solution in digester. Make up "
        "the volume with water.\n"
        "Standard Solutions: Prepare 5-point calibration standards from 1000 ppm stock solutions for "
        "each element using water as diluent.\n"
        "Procedure: Inject sample and standard solutions in the AAS instrument under specified "
        "conditions for each element. Record the content of element (μg/g or ppm). Instrument "
        "shall calculate content of element automatically from linearity curve of standard solutions.\n"
        "Calculation: Content (μg/g or ppm) = Content of specific element (μg/g) × SD / W\n"
        "Where SD = Volume; W = Weight of sample"
    ),
    "Foreign matter": (
        "Take 5.0 g of sample and spread on a white paper uniformly. Observe material for absence of "
        "any foreign particle."
    ),
    "Ethylene oxide": (
        "This test is carried out by outside laboratory using GC HS / GC MS."
    ),
    "OVI/Residual solvent": (
        "Preparation of standard: Weigh 300 mg of methanol standard in volumetric flask of 100 ml, "
        "add 20 mL of Dimethyl Formamide and mix well and fill the volumetric flask up to the mark "
        "with Dimethyl Formamide and mix well.\n"
        "Preparation of Sample: Take 500 mg of test sample (Glycine) in volumetric flask of 100 ml, "
        "add 10 mL of Dimethyl Formamide and mix well and fill the volumetric flask up to the mark "
        "with Dimethyl Formamide and mix well.\n"
        "Procedure: Mode: GC; Injector: Headspace; Injection Type: Split ratio, 1:5; Detector: Flame "
        "Ionization; Column: 0.32-mm x 30-m capillary fused silica coated with 1.8 μm layer of "
        "phase G43.\n"
        "Calculation: % Methanol = (Area of methanol in Glycine / Area of methanol in Standard) × "
        "(Concentration of methanol in Standard / Concentration of methanol in sample) × 10⁶"
    ),
}

MICRO_PROCEDURES = {
    "Bacterial endotoxin test": (
        "Prepare the solutions and dilutions with water BET. If necessary, adjust the pH of the "
        "solution under examination to 6.0 to 8.0 using sterile 0.1 M hydrochloric acid BET, "
        "0.1 M sodium hydroxide BET or a suitable buffer prepared with water BET.\n"
        "Prepare replicates of solutions A to D: Solution A = Test solution at or below MVD; "
        "Solution B = Test solution spiked with CSE (Positive Product Control); "
        "Solution C = Standard CSE in water BET; Solution D = Water BET (Negative Control).\n"
        "Method: Into each receptacle add appropriate volumes of NC, standard CSE, test solution, "
        "and PPC. Add an equal volume of appropriately constituted lysate. Mix gently and incubate "
        "at 37°C ± 1°C undisturbed for 60 ± 2 minutes. A positive reaction is "
        "characterised by the formation of a firm gel that retains its integrity when inverted 180°. "
        "A negative result is characterised by absence of such a gel."
    ),
    "Pathogen in general": (
        "Refer to pathogen-specific sub-tests below (Escherichia coli, Salmonella, "
        "Pseudomonas aeruginosa, Staphylococcus aureus, Coliforms)."
    ),
    "TAMC": (
        "Aseptically transfer powder equivalent to 10.0 g to a sterile 100 ml volumetric flask, "
        "add about 70 ml of sterile phosphate buffer pH 7.2 and shake until a uniform suspension is "
        "obtained, dilute to 100 ml with phosphate buffer. Immediately transfer aseptically 1 ml into "
        "each of two sterile Petri-dishes. Add 15 to 20 ml of Casein Soya bean digest agar medium "
        "previously sterilized at 15 lbs pressure and cooled to 45°C. Cover, mix and allow to "
        "solidify at room temperature. Invert and incubate for 96 to 120 hours at 30°C to 35°C. "
        "Count the number of colonies; average colonies multiplied by dilution factor gives cfu/g."
    ),
    "TYMC": (
        "Aseptically transfer powder equivalent to 10.0 g to a sterile 100 ml volumetric flask, add "
        "about 70 ml of sterile phosphate buffer pH 7.2 and shake until a uniform suspension is "
        "obtained, dilute to 100 ml. Transfer aseptically 1 ml into each of two sterile Petri-dishes. "
        "Add 15 to 20 ml of Sabouraud Dextrose Agar medium previously sterilized and cooled to 45°C. "
        "Mix, solidify, invert and incubate for 5 days at 20°C to 25°C. Count the number of "
        "fungal colonies; average colonies multiplied by dilution factor gives fungi/g."
    ),
    "Escherichia coli": (
        "Aseptically transfer 10 ml of pre-treated sample in 90 ml Soya bean Casein digest broth "
        "and mix. Incubate at 30°C to 35°C for 18 to 24 hours. If growth is present, "
        "transfer 1 ml to 100 ml of MacConkey broth and incubate at 42°C to 44°C for 24 to "
        "48 hours. Sub culture on MacConkey agar at 30°C to 35°C for 18 to 72 hours. Growth "
        "of brick red colonies indicates possible presence of E. coli. Confirmed by identification tests."
    ),
    "Salmonella": (
        "Aseptically transfer 10 ml of pre-treated sample in 90 ml Soya bean Casein digest broth and "
        "mix. Incubate at 30°C to 35°C for 18 to 24 hours. Transfer 0.1 ml to 10 ml of "
        "Rappaport Vassiliadis Salmonella Enrichment Broth and incubate at 30°C to 35°C for "
        "18 to 24 hours. Sub culture on Xylose Lysine Deoxycholate Agar at 30°C to 35°C for "
        "18 to 48 hours. Red colonies with or without black centres indicate possible presence of "
        "Salmonella. Confirmed by identification tests."
    ),
    "Pseudomonas aeruginosa": (
        "Aseptically transfer 10 ml of pre-treated sample in 90 ml Soya bean Casein digest broth and "
        "mix. Incubate at 30°C to 35°C for 18 to 24 hours. If growth is present, sub culture "
        "on Cetrimide agar at 30°C to 35°C for 18 to 24 hours. Growth of colonies indicates "
        "possible presence of Pseudomonas. Confirmed by identification tests."
    ),
    "Staphylococcus aureus": (
        "Aseptically transfer 10 ml of pre-treated sample in 90 ml Soya bean Casein digest broth and "
        "mix. Incubate at 30°C to 35°C for 18 to 24 hours. If growth is present, sub culture "
        "on Mannitol agar at 30°C to 35°C for 18 to 24 hours. Growth of colonies indicates "
        "possible presence of Staphylococcus. Confirmed by identification tests."
    ),
    "Coliforms": (
        "Aseptically transfer 10 ml of pre-treated sample in 90 ml Soya bean Casein digest broth and "
        "mix. Incubate at 30°C to 35°C for 18 to 24 hours. If growth is present, sub culture "
        "on LST broth tubes containing Durham's vial at 35°C for 24 hours. Gas production indicates "
        "possible presence of Coliforms. Confirmed by identification tests."
    ),
}

# ── Apply procedures to tests ────────────────────────────────────────────────

for test in data["tests"]:
    name = test["name"]
    if name in PROCEDURES:
        test["procedure"] = PROCEDURES[name]
    # Handle Identification sub_tests
    if name == "Identification":
        for sub in test.get("sub_tests", []):
            sub_name = sub["name"]
            # Match by partial name
            for key, proc in IDENTIFICATION_SUB_PROCEDURES.items():
                if key.lower() in sub_name.lower():
                    sub["procedure"] = proc
                    break

for test in data["additional_tests"]:
    name = test["name"]
    if name in ADDITIONAL_PROCEDURES:
        test["procedure"] = ADDITIONAL_PROCEDURES[name]
    # Also handle sub-tests (elemental elements + Foreign matter/OVI/EO)
    for sub in test.get("sub_tests", []):
        sub_name = sub["name"]
        if sub_name in ADDITIONAL_PROCEDURES:
            sub["procedure"] = ADDITIONAL_PROCEDURES[sub_name]

for test in data["microbiological_tests"]:
    name = test["name"]
    if name in MICRO_PROCEDURES:
        test["procedure"] = MICRO_PROCEDURES[name]

# ── MOA revision history ─────────────────────────────────────────────────────

data["moa_revision_history"] = [
    {
        "document_no": "MOA/FG00038/01 (R-00)",
        "revision_made": "New MOA prepared",
        "change_control_no": "-------",
        "effective_date": "2021-04-21"
    },
    {
        "document_no": "MOA/FG00038/01 (R-01)",
        "revision_made": "Format revised as per revised SOP QC 12. Some contents revised as per FSSAI requirement.",
        "change_control_no": "CC/2022/03",
        "effective_date": "2022-06-01"
    },
    {
        "document_no": "MOA/FG00038/01(R-02)",
        "revision_made": "Elemental impurity by AAS added. Ethylene oxide test added.",
        "change_control_no": "CC/2023/010",
        "effective_date": "2023-06-01"
    }
]

# ── Write back ───────────────────────────────────────────────────────────────

p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
print("Updated glycine_ip.json successfully")

# Verify
data2 = json.loads(p.read_text(encoding="utf-8"))
for t in data2["tests"]:
    has_proc = bool(t.get("procedure"))
    print(f"  {t['name']}: procedure={'YES' if has_proc else 'NO'}")
print(f"  moa_revision_history: {len(data2.get('moa_revision_history', []))} entries")
