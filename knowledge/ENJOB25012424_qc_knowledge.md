# 424 Carbon Steel — QC & Testing Knowledge Base

Technical reference for ENJOB25012424 Carbon Steel piping spool fabrication. Written in English; the chat agent translates to Chinese at answer time for Chinese staff. Each section is self-contained.

---

## 1. Project Overview (Project Overview)

- **Job number:** ENJOB25012424
- **Scope:** Carbon steel pipe spool fabrication (painted/coated). Multi-diameter, multi-line, shop-welded + shop-painted before dispatch.
- **Customer contract:** B1SEHR-5-0008
- **Base pipe material:** ASTM A106 Gr.B (primary), with ASTM A53 Gr.B / API 5L Gr.B allowed as equivalents per WPS
- **Wrought butt-weld fittings:** ASTM A234 WPB
- **Forged fittings and flanges:** ASTM A105
- **ASME P-Number:** P-No 1, Group 1 (and partially Group 2 for thin-wall WPS-001)
- **Paint system:** ISO 12944-5 C5-High (corrosivity class C5, High durability) — blast-clean + primer + intermediate + topcoat
- **Applicable codes and standards:**
  - ASME B31.3 (Process Piping) — design, fabrication, inspection, acceptance
  - ASME BPVC Section IX — welding and welder qualification (WPS/PQR/WPQ)
  - ASME BPVC Section V — NDE methods (Art 2 RT, Art 7 MT, Art 9 VT)
  - ASME B16.25 — butt weld end preparation (bevel geometry)
  - ISO 8501-1 — surface preparation (Sa 2½ blast standard)
  - ISO 8501-3 — weld seam preparation grades before painting
  - ISO 12944-5 — paint systems for corrosivity C5-High
  - ISO 19840 — measurement of dry film thickness (DFT)
  - ISO 4624 — pull-off adhesion test
- **Key ITP document:** ENJOB25012424-ITP-SPL-001, dated 2025-12-25
- **Required WPS / PQR set (latest Rev 4, 2026-03):**
  - WPS-SPL-001 — GTAW (+ SMAW fill/cap option), thin wall / small bore (base metal groove 0–6 mm, fillet unlimited)
  - WPS-SPL-002 — GTAW + SMAW, medium/thick wall (base metal groove 6–25 mm, max pass thickness 13 mm)
  - WPS-SPL-003 — GTAW + SAW, thick wall / large bore (base metal groove 5–32 mm)

---

## 2. Material & Metallurgy (Material & Metallurgy)

### 2.1 Why Carbon Steel Is Different From Duplex
Carbon steel A106-B / A234-WPB / A105 is P-No 1 Group 1 material — a ferritic/pearlitic structure with uniform, well-understood weldability. Unlike duplex stainless, it does NOT require:
- Tight interpass temperature control for phase balance (250 °C max is comfortable, not critical)
- Ferrite phase measurement
- PMI (positive material identification) beyond standard heat-number traceability
- Ferroxyl or passivation testing
- Metallographic (A923) intermetallic screening
- Chloride-free consumables
- Stainless-only tools

Carbon steel DOES require:
- Protection from atmospheric corrosion (painted externally within hours of fabrication)
- Preheat when ambient < 10 °C or condensation risk exists
- Low-hydrogen SMAW consumables (E7015 / E7018) stored and baked per manufacturer
- Adequate surface prep (ISO 8501-1 Sa 2½) for paint adhesion
- Hydrogen-cracking awareness on thick sections under restraint

### 2.2 Acceptance Ranges Used on 424
- **Preheat:** Minimum base metal temperature ≥ 10 °C. Localized preheat may be applied to prevent condensation.
- **Interpass temperature max:** 250 °C (per WPS-001, WPS-002, WPS-003). This is the comfortable CS ceiling, not a metallurgical hard limit like duplex.
- **Heat input:** Not controlled (CS is tolerant; no hard limit in these WPS).
- **PWHT:** None required. The WPS explicitly states "No PWHT". PWHT would only be triggered by ASME B31.3 wall-thickness thresholds or piping class requirements — verify per line list before waiving on a specific spool if in doubt.
- **Hydrogen control:** SMAW electrodes E7015 / E7018 must be stored in holding ovens per manufacturer COA; electrodes re-exposed beyond the allowed time must be baked before reuse.
- **Surface preparation before paint:** ISO 8501-1 Sa 2½ (near-white metal blast), surface profile per paint manufacturer data sheet, dust per ISO 8502-3.
- **DFT acceptance:** per ISO 19840 — no single reading below 80 % NDFT, average ≥ NDFT, maximum per paint system.
- **Adhesion acceptance:** per ISO 4624 pull-off test, minimum value per paint system technical data sheet.

### 2.3 Why Hydrogen Matters on Thick Sections
Carbon steel heat-affected zones can be vulnerable to hydrogen-induced cracking (HIC) when three conditions coincide: (a) diffusible hydrogen from flux/moisture, (b) tensile residual stress, (c) a susceptible microstructure. The mitigations in this project are: low-hydrogen E7015 / E7018 electrodes, baking + holding-oven storage, dry surfaces before welding, and preheat ≥ 10 °C with condensation control. None of the procedures require PWHT, but hydrogen control during welding is mandatory.

### 2.4 Consumable Traceability
Every heat of base material and every lot of filler consumables must have an MTC (Mill Test Certificate) or CoC (Certificate of Conformance) matching the heat / lot number stamped on the product. The traceability chain is: MTC → incoming inspection → material identification (step 20) → weld map at step 120. No PMI is required because the grade is verified by MTC and by visual checks (color, stamp, markings).

---

## 3. Welding (Welding)

### 3.1 WPS Registry

Three approved procedures cover the 424 material thickness range. Selection by wall thickness per ASME IX QW-451.

#### WPS-001 — GTAW root + SMAW fill/cap (thin-wall / small-bore)
- **Procedure No.:** ENJOB25012424-WPS-SPL-001 (source filename in Rev 4 carries the legacy ENJOB25011423 prefix; content is for 424 carbon steel — this is a known file-naming carry-over, not a different procedure)
- **Process:** GTAW (manual) for root, SMAW for filler and cap
- **Joint design:** Groove or groove + fillet, root opening per drawing, no backing
- **Base material:** ASTM A106 Gr.B / A53 Gr.B / API 5L Gr.B to ASTM A234 WPB / A105; P-No 1 Group 1 or 2
- **Thickness range (base metal groove):** 0–6 mm; fillet unlimited
- **Filler metal:** GTAW — AWS ER70S-6, F-No 6, A-No 1, Ø 2.5 mm solid wire; SMAW — AWS E7018, F-No 4, A-No 1, Ø 3.2 mm and Ø 4.0 mm
- **Shielding gas (GTAW):** Argon 99.99 %, 10–14 L/min
- **Backing gas:** None
- **PWHT:** None
- **Preheat:** ≥ 10 °C (condensation control)
- **Interpass temperature max:** 250 °C
- **Position qualified:** 5G groove, uphill progression; fillet all positions
- **Tungsten:** WC20 or WT20, Ø 2.5 mm
- **Technique:** String bead, multi-pass, mechanical grinding for inter-pass cleaning, back gouging by grinding if required

| Pass | Process | Filler Ø | Polarity | Amps | Volts | Travel (cm/min) |
|------|---------|----------|----------|------|-------|-----------------|
| Root | GTAW | Ø 2.5 mm ER70S-6 | DCEN | 90–130 | 11–16 | 10–20 |
| Fill | SMAW | Ø 3.2 mm E7018 | DCEP | 90–130 | 20–25 | 10–20 |
| Cap  | SMAW | Ø 4.0 mm E7018 | DCEP | 130–160 | 20–25 | 10–20 |

#### WPS-002 — GTAW + SMAW (medium/thick wall)
- **Procedure No.:** ENJOB25012424-WPS-SPL-002
- **Supporting PQR:** ENJOB25012424-PQR-SPL-002 (GTAW + SMAW)
- **Process:** GTAW manual root + SMAW manual fill/cap
- **Joint design:** Groove or groove + fillet, root opening 1–3 mm, no backing
- **Base material:** A106 Gr.B / A53 Gr.B / API 5L Gr.B to A234 WPB / A105; P-No 1 Group 1
- **Thickness range (base metal groove):** 6–25 mm; fillet unlimited; maximum pass thickness 13 mm
- **Filler metal:** GTAW — AWS ER70S-6 (SFA 5.18), F-No 6, A-No 1, Ø 2.5 mm solid wire; SMAW — AWS E7015 (SFA 5.1), F-No 4, A-No 1, Ø 3.2 and Ø 4.0 mm
- **Brand qualified:** ATLANTIC / GOLDEN BRIDGE (or equivalent with equal classification + MTC)
- **Shielding gas (GTAW):** Argon 99.99 %, 10–14 L/min
- **Backing gas:** None
- **PWHT:** None (unless triggered by B31.3 thickness rules on a specific spool)
- **Preheat:** ≥ 10 °C
- **Interpass temperature max:** 250 °C
- **Position qualified:** 5G groove, uphill; fillet all positions
- **Cup size:** Ø 8 mm gas cup for GTAW
- **Technique:** String bead, multi-pass, single electrode, mechanical grinding for cleaning, no peening, oscillation width ≤ 2.5 × electrode Ø

| Pass | Process | Filler Ø | Polarity | Amps | Volts | Travel (cm/min) |
|------|---------|----------|----------|------|-------|-----------------|
| Root | GTAW | Ø 2.5 mm ER70S-6 | DCEN | 90–130 | 11–16 | 10–20 |
| Fill | SMAW | Ø 3.2 mm E7015 | DCEP | 90–130 | 20–25 | 10–20 |
| Cap  | SMAW | Ø 4.0 mm E7015 | DCEP | 130–160 | 20–25 | 10–20 |

#### WPS-003 — GTAW + SAW (thick-wall / large-bore option)
- **Procedure No.:** ENJOB25012424-WPS-SPL-003
- **Supporting PQR:** ENJOB25012424-PQR-SPL-003 (GTAW + SAW)
- **Process:** GTAW manual root + SAW mechanised fill/cap
- **Base material:** A106 Gr.B / A53 Gr.B / API 5L Gr.B to A234 WPB / A105; P-No 1 Groups 1–4 qualified
- **Thickness range (base metal groove):** 5–32 mm
- **Shielding:** GTAW Ar 99.99 %; SAW under flux
- **Backing:** SAW deposits onto GTAW root (no separate backing strip)
- **PWHT:** None
- **Preheat:** ≥ 10 °C
- **Interpass temperature max:** 250 °C
- **Notes:** Used for the largest diameters where SAW productivity is beneficial. Verify welder WPQ covers SAW before assigning.

#### WPS Selection Rule
- Groove thickness ≤ 6 mm → WPS-001
- Groove thickness 6–25 mm → WPS-002 (default for most 424 spools)
- Groove thickness > 25 mm and up to 32 mm, especially on large bore where SAW is practical → WPS-003

### 3.2 Welder Qualification (WPQ)
- Every welder who contributes to 424 spools must hold a current WPQ covering the applicable WPS, process (GTAW / SMAW / SAW), position (5G uphill for groove), and diameter/thickness range per ASME IX QW-452.
- WPQ certificates must be on file, with performance test records and unique welder stamp IDs. The stamp ID is recorded on every weld in the welding log and the weld map.
- Continuity must be maintained per QW-322 — a welder who does not use a process for more than 6 months loses qualification in that process.

### 3.3 Weld Counting Rules
Follow the general shop-weld methodology used across ENERXON projects:
- **Butt welds** — count at the main pipe diameter. Pipe-to-pipe, pipe-to-elbow, pipe-to-tee, pipe-to-flange (WN), pipe-to-reducer.
- **Olet welds (sockolets/weldolets)** — count at the BRANCH diameter, not the main pipe. A sockolet 18"×2" is a 2" weld, not 18".
- **Branch socket welds** — count at the branch size (typically 2" or 1").
- **Field welds (open ends)** — NOT counted as shop welds.
- **Reinforcement pads (REPADs)** — supply items, counted separately in BOM but not in the shop weld log.
- **Inch-Dia** = number of welds × pipe diameter (in inches). Used for welding workload estimation.
- **Linear meters** = number of welds × π × pipe OD. Used for consumables and time estimation.

---

## 4. NDT Procedures (NDT)

### 4.1 Visual Testing — VT (Visual Testing)
- **Standard:** ASME B31.3 para 341 (visual examination requirements); ASME Section V Article 9 (examination method).
- **Coverage:** 100 % of all welds, 100 % of all spools.
- **ITP step:** 90
- **Inspector qualification:** QC inspector with VT Level II (or equivalent) per SNT-TC-1A or equivalent company program. Adequate lighting (≥ 1000 lux at the surface) and visual acuity test required.
- **What is checked:** undercut, porosity, lack of fusion (visible), cracks (surface), reinforcement profile and height, arc strikes, spatter, surface irregularities, weld toe transition.
- **Acceptance:** per ASME B31.3 Table 341.3.2. Common limits: no cracks, no lack of fusion, no lack of penetration visible from OD, reinforcement within code limits, undercut ≤ 0.8 mm or 10 % of pipe wall (the lesser) on longitudinal welds.
- **Documentation:** VT report per spool — weld ID, welder ID, process, size, visual condition, defects found, accept/reject, inspector name + date.

### 4.2 Radiographic Testing — RT (Radiographic Testing)
- **Standard:** ASME Section V Article 2; ASME B31.3 Table 341.3.2 acceptance criteria.
- **Source:** X-ray only (per WPS notes — RT "X-ray" is specified for 424, not γ).
- **Coverage:** 100 % of circumferential butt welds, 100 % of applicable spools. This is called out explicitly in the WPS notes.
- **ITP step:** 100 — Hold Point (H + f + W). Client or TPI has the right to witness and must release before next step.
- **Technique:** SWSI or DWSI per pipe size, sensitivity and density per ASME V. IQI selection per ASME V Article 2 Table T-276.
- **Inspector qualification:** Radiographer Level II (for shoot and process), Level II or III interpreter (for film read and acceptance).
- **Acceptance:** per ASME B31.3 Table 341.3.2 for normal fluid service:
  - No cracks
  - No lack of penetration
  - No lack of fusion
  - No elongated slag or porosity in excess of code limits
  - Density 1.8–4.0
- **Action on rejection:** grind out defect, re-weld per WPS, re-RT to acceptance.
- **Documentation:** RT report per spool (or per batch report covering multiple spools) — weld ID, welder ID, film ID, technique, IQI, density per film, defect column (none / porosity / slag / LOP / LOF / crack), accept/reject per film, interpreter signature + level.

### 4.3 Magnetic Particle Testing — MT (Magnetic Particle Testing)
- **Standard:** ASME Section V Article 7; ASME B31.3 acceptance.
- **Coverage:** 100 % of applicable welds — socket welds, fillet welds, branch welds (where applicable), and any weld repair area.
- **ITP step:** 110
- **Technique:** Yoke or prods. Dry or wet particles per procedure. Two perpendicular magnetisation directions to cover all orientations. Lifting force of yoke verified (AC yoke ≥ 4.5 kg / 10 lb, DC ≥ 18 kg / 40 lb for cross-legs up to 150 mm).
- **Inspector qualification:** MT Level II or above.
- **Acceptance:** per ASME B31.3 — no relevant linear indications, no clustered rounded indications exceeding code limits.
- **Action on rejection:** grind out indication, re-weld if required, re-MT after grinding + re-weld.
- **Documentation:** MT report per spool — weld ID, welder ID, size, technique (yoke / prods), particle type (dry / wet), magnetising direction, lifting force verified, indication type, accept/reject.

### 4.4 Dimensional Inspection (Dimensional Inspection)
- **Standard:** ASME B31.3 para 335 (fabrication); ENJOB25012424 approved spool drawings.
- **Instruments:** calibrated tape measure, digital calipers, squares, levels, protractors, flange-hole templates, all in date.
- **ITP steps:** 130 (pre-paint dimensional) and 180 (final dimensional, after painting)
- **Coverage:** 100 % of spools and straight pipes.
- **Key dimensions recorded:** overall length, face-to-face, face-to-centre, flange bolt-hole orientation (±1.5 mm typical), flange perpendicularity (≤ 0.5 % OD max 2 mm per B31.3 §335.1.1), elbow angles, branch positions, bevel geometry on open (field weld) ends per B16.25.
- **Two dimensional steps (pre-paint and post-paint):** pre-paint catches fabrication issues while rework is cheap; post-paint verifies nothing moved during blast + paint handling.
- **Acceptance:** nominal vs actual vs deviation within drawing tolerance. Out of tolerance → engineering review, cut and re-weld, or rework.
- **Documentation:** dimensional report per spool — drawing no., measured dimensions with nominal / actual / deviation / within tolerance, instruments used + calibration IDs.

### 4.5 What 424 Does NOT Require
The following tests that apply to duplex or high-alloy projects do NOT apply to 424 carbon steel:
- **PT (Penetrant Testing)** — not in the 424 ITP. MT is used instead on non-butt welds because CS is ferromagnetic.
- **PMI (Positive Material Identification)** — not in the 424 ITP. CS grade is verified by MTC and visual markings; alloy confirmation by XRF is not required.
- **Ferrite measurement** — not applicable to CS. Ferrite is a duplex acceptance criterion.
- **Ferroxyl test** — not applicable. Ferroxyl is a post-passivation verification for stainless steels.
- **Metallographic (A923) phase screening** — not applicable. A923 is specific to duplex intermetallic phases.
- **Passivation / pickling** — not applicable. CS is painted, not passivated.

---

## 5. ITP Flow — Inspection & Test Plan (ITP Flow)

The controlling document is **ENJOB25012424-ITP-SPL-001**, dated 2025-12-25. Inspection codes: **H** hold point, **W** witness, **R** document review, **V** verify, **I** inspect, **f** 100 %, **c1** sampling, **X** mandatory supplier action.

### 5.1 ITP Step Table

| # | Step | Code | Sample / Freq | Acceptance reference | Control record |
|---|------|------|---------------|----------------------|----------------|
| 10 | Raw Material Receiving (pipes, fittings, flanges) | I+f+X+W | Each lot | BOM, PO, MTC, project spec | Incoming inspection report |
| 20 | Material Identification & Traceability | I+f | Each lot | Heat-number match to MTC | Traceability log |
| 30 | Review of Fabrication Documents (WPS, PQR, WPQ, NDT, Painting, ITP) | R+f+X | Once before start | ASME B31.3 + IX + project | Approved document register |
| 40 | Welding Equipment & Consumables Verification | V+c1 | Random, before welding | Calibration valid, filler per WPS, low-H storage | Calibration + consumable logs |
| 50 | Pipe Cutting per Spool Drawings | I+c1 | Random, each spool | Length & squareness per drawing | Cutting inspection record |
| 60 | End Preparation / Beveling | I+c1 | Random, each spool | ASME B16.25 bevel geometry | Fit-up checklist |
| 70 | Fit-up & Assembly | I+c1+W | Random, each spool | WPS/drawing alignment, gap, orientation | Fit-up report |
| 80 | Production Welding (GTAW / GTAW+SMAW / GTAW+SAW) | I+c1+W | Random, continuous | WPS-001 / 002 / 003; interpass ≤ 250 °C | Welding log + traveller + consumable record |
| 90 | Visual Testing (VT) | I+f | Each spool, 100 % | B31.3 | VT report |
| 100 | Radiographic Testing (RT, X-ray) | I+f+W+H | Each spool, 100 % applicable welds | ASME V Art 2 + B31.3 | RT report + films |
| 110 | Magnetic Particle Testing (MT) | I+f+W | Each spool, 100 % applicable welds | ASME V Art 7 + B31.3 | MT report |
| 120 | Weld Identification & Stamping | I+f | Each spool | Welder stamp traceable to WPQ | Weld map |
| 130 | Dimensional Inspection (pre-paint) | I+f+W | Each spool | Approved drawings | Dimensional report |
| 140 | Cleaning Prior to Painting (Post-NDT) | V+c1 | Random, each spool | Free of oil, grease, slag, moisture | Cleaning checklist |
| 150 | Surface Preparation — Blasting | I+c1 | Random, each batch | ISO 8501-1 Sa 2½; profile per TDS | Blasting report |
| 160 | Painting Application (Primer / Intermediate / Topcoat) | I+c1 | Random, each coat | ISO 12944-5 C5-High; DFT per system | Painting log |
| 170 | Coating Inspection (DFT / Adhesion) | I+f+W | DFT 100 %, adhesion c1 per batch | ISO 19840 / ISO 4624 / ISO 8501-3 | Coating report |
| 180 | Final Dimensional Inspection (post-paint) | I+f | Each spool | Drawing tolerances | Dimensional report |
| 190 | Spool Marking | I+f | Each spool | Matrix ENJOB25012424-MAT-SPL-001 | Marking log |
| 200 | Final Documentation (Dossier) | R+f+X | Each shipment | Complete records per project | Dossier index |
| 210 | Packing & Dispatch | I+c1+W | Each shipment | Adequate protection & marking | Packing list |
| 220 | Final Dossier (Records) | R+f | Each shipment | MTC, WPS/PQR/WPQ, NDT, paint, dimensional | Dossier index |

### 5.2 Hold Points (client release required before proceeding)
- **Step 100 — RT.** RT must be accepted and released before the spool moves to step 110 (MT).

### 5.3 Witness Points (client right to attend on notice)
- 10 (Raw Material Receiving), 70 (Fit-up), 80 (Welding), 100 (RT), 110 (MT), 130 (Dimensional pre-paint), 170 (DFT/Adhesion), 210 (Packing).

### 5.4 Review Points (client document review)
- 30 (WPS/PQR/WPQ/NDT/Painting/ITP review), 200 and 220 (Dossier).

### 5.5 Mapping to Tracker `project_steps`
The tracker website `enerxon-china-tracker.onrender.com` stores the checklist for 424 in the `project_steps` table. QC reports link back to the step via the `itp_step` field on `qc_report_defs` in `project_settings`. The 9 QC reports configured for 424 are: **cutting, fitup, welding_log, vt, rt, mt, dimensional (pre-paint), dft, dimensional (post-paint)**. The date on each report comes from `progress.completed_at` (checklist tick), not the form-fill date. The chat agent reads the current step numbering live from the DB, so the mapping stays self-consistent.

---

## 6. Surface Preparation & Coating (Surface & Coating)

### 6.1 Process Flow (after NDT release)

```
[after RT and MT accepted]
    ↓
140  Cleaning Prior to Painting   — solvent/mechanical, free of oil, grease, slag, moisture
    ↓
150  Surface Preparation — Blasting   — ISO 8501-1 Sa 2½, surface profile per paint TDS
    ↓
160  Painting Application   — primer → intermediate → topcoat per ISO 12944-5 C5-High
    ↓
170  Coating Inspection   — DFT 100 %, adhesion sampling, visual per ISO 8501-3
    ↓
180  Final Dimensional Inspection (post-paint)
    ↓
190  Spool Marking   — stencil or marker per matrix ENJOB25012424-MAT-SPL-001
    ↓
200  Dossier compilation
    ↓
210  Packing & Dispatch
```

### 6.2 Surface Preparation Acceptance
- **Blast standard:** ISO 8501-1 Sa 2½ (near-white metal blast) — nearly all mill scale, rust, and old paint removed.
- **Surface profile:** per paint manufacturer TDS, typically Ra 40–75 μm or Rz 50–100 μm.
- **Dust on prepared surface:** ISO 8502-3 rating 2 or better (no loose dust).
- **Re-blast trigger:** ISO 8501-1 drop, flash rust, oil/grease contamination after blast, or exceeding the allowed hold time before primer.
- **Ambient conditions at blast and paint:** substrate temperature ≥ 3 °C above dew point, relative humidity within paint TDS range.

### 6.3 Painting Acceptance
- **System:** ISO 12944-5 C5-High — high-durability system for corrosivity category C5 (industrial / marine). Specific product stack is per the approved painting procedure.
- **Paint application:** airless spray preferred, brush for stripe coats on edges and welds, each coat within the recoat window per TDS.
- **Stripe coats:** applied by brush on edges, welds, bolt holes, corners, and hard-to-reach areas before each full coat.

### 6.4 DFT Acceptance (ISO 19840)
- **Measurement:** calibrated electronic DFT gauge (Elcometer or equivalent), calibrated on the day of use with reference foils.
- **Number of readings:** minimum 5 per spot area, minimum 10 spot areas per spool for typical sizes; more for larger surfaces per ISO 19840 Table 2.
- **Acceptance (ISO 19840 "80-20 rule"):**
  - No single reading below 80 % of NDFT (nominal dry film thickness).
  - Average spot value ≥ NDFT.
  - Maximum DFT ≤ maximum stated in the paint system specification.
- **Non-conformance:** apply additional topcoat until DFT within range; blast and re-paint if maximum exceeded significantly.
- **Documentation:** DFT report per spool — paint product + batch, specified NDFT, spot readings, average / min / max, pass/fail per ISO 19840, ambient conditions (air and surface temp, RH, dew point).

### 6.5 Adhesion Testing (ISO 4624)
- **Method:** pull-off adhesion test with calibrated dolly tester (portable adhesion tester).
- **Frequency:** sampling per batch (`c1` in the ITP).
- **Acceptance:** minimum pull-off value per paint system TDS; most C5-High systems require ≥ 5 MPa or failure cohesively in the coating, not adhesively at the substrate.
- **Documentation:** adhesion report with location, pull-off value, failure mode (adhesive / cohesive / mixed), accept/reject.

---

## 7. Cutting & Fit-up (Cutting & Fit-up)

### 7.1 Cutting (ITP step 50)
- **Methods allowed:** mechanical sawing, abrasive cutting, or plasma — no oxy-fuel on fittings, thermal methods must be followed by mechanical cleanup of heat-affected zone.
- **Tolerance:** length per drawing ± project tolerance; squareness per B31.3 and drawing note.
- **Inspection:** random (c1) per ITP step 50, dimensional check on each cut.
- **Documentation:** cutting inspection record per spool — drawing no., cut lengths, actual, deviation, within tolerance.

### 7.2 End Preparation / Beveling (ITP step 60)
- **Standard:** ASME B16.25 (butt weld end preparation).
- **Typical geometry:** 30° ± 2.5° single-V bevel, 1.5 mm ± 0.8 mm root face for pipe wall 6 mm and above; special bevels per drawing note for special joints.
- **Tools:** mechanical bevel machines (Protem / Climax style) or plasma followed by grinding.
- **Inspection:** visual and gauge check (bevel protractor, profile gauge), random per spool.
- **Internal mismatch (hi-lo):** B31.3 §328.4.3 default (typically 1.5 mm or 20 % of the thinner wall, whichever is less) unless drawing note specifies tighter.

### 7.3 Fit-up & Assembly (ITP step 70)
- **Alignment:** per WPS and drawing; offset within code limits.
- **Root opening:** per WPS-002 / WPS-003 (1–3 mm) or as specified on drawing.
- **Joint cleanliness:** wiped clean, free of oil, moisture, marker, and surface oxide / mill scale on the groove faces.
- **Tack welds:** made with the same filler metal and process as the root pass; removed or blended into the root pass during welding.
- **Preheat before welding:** base metal ≥ 10 °C; localized preheat may be applied in cold / humid conditions to prevent condensation on the joint.
- **Hold point:** inspection (`I+c1+W`) at step 70 — client has right to witness.
- **Documentation:** fit-up report per spool — joint ID, wall, joint type (BW / SW / Fillet), bevel angle, root face, root gap, hi-lo, tack weld condition, joint cleanliness, accept/reject.

---

## 8. Documentation & Certification (Documentation & Certification)

### 8.1 EN 10204 Type 3.1 Traceability
Each fabricated spool is traceable from base material heat numbers (MTCs) through the weld map (showing which welder welded each weld) to the final NDE reports. The final dossier is issued as an EN 10204 Type 3.1 certificate set when requested by the client.

### 8.2 Report Numbering Convention
Record numbers follow the format `ENJOB25012424-REC-<SPOOL_ID>-<SEQ>` where `<SEQ>` is the ITP step or the QC report sequence in the project-specific registry. The tracker generates these automatically via `get_record_number()`.

### 8.3 Mandatory Report Matrix per Spool Type

| Report | Spool (welded) | Straight Pipe |
|--------|----------------|---------------|
| Cutting | ✓ | ✓ |
| Fit-up | ✓ | — |
| Welding Log | ✓ | — |
| VT | ✓ | — |
| RT | ✓ | — |
| MT | ✓ | — |
| Weld Map | ✓ | — |
| Dimensional (pre-paint) | ✓ | ✓ |
| DFT / Coating | ✓ | ✓ |
| Dimensional (post-paint) | ✓ | ✓ |

Straight pipes skip welding / NDE reports but still require cutting + dimensional + coating reports.

### 8.4 Common Header (ALL Reports)
1. Report No. (e.g., `ENJOB25012424-REC-SPL-001-001`)
2. Date (from checklist step completion, not form fill date)
3. Project name / Job No. (`ENJOB25012424`)
4. Contract / PO No. (`B1SEHR-5-0008`)
5. Client name
6. Drawing / ISO No.
7. Spool No. / Mark No.
8. Material specification & grade (A106-B / A234-WPB / A105)
9. Applicable procedure No. + Rev (WPS-001 / 002 / 003; ITP-SPL-001)
10. ENERXON logo + IQNet + ISO 9001 + EN 10204 Type 3.1 certification bar
11. Page _ of _

### 8.5 Signature Requirements per Report

| Report | Examiner | QC Review | TPI |
|--------|----------|-----------|-----|
| Cutting | QC Inspector | — | Witness |
| Fit-up | QC Inspector | — | Witness |
| Welding Log | Welder + QC Inspector | — | Witness |
| VT | QC Inspector (VT Level II) | — | Witness |
| RT | Level II/III Interpreter | QC Inspector | Witness (hold point) |
| MT | Level II Examiner | QC Inspector | Witness |
| Dimensional | QC Inspector | — | Witness |
| DFT / Coating | NACE / FROSIO Inspector | QC Inspector | Witness |

### 8.6 Final Dossier (ITP step 200 / 220)
Per shipment, the dossier shall include:
- Complete MTCs for every heat of base material, filler metal, and consumables.
- WPS, PQR, and WPQ for every welder who contributed to the shipment.
- VT, RT (with films), MT reports.
- Welding logs and weld map.
- Dimensional reports (pre-paint and post-paint).
- Paint surface prep records, painting log, DFT report, adhesion report.
- Marking log.
- Packing list.
- Dossier index front page (ENERXON-branded).

Shipment is held at step 200 until the dossier is complete.

---

## 9. Common Questions & Answers (Q&A)

**Q1. What material is used in 424?**
A. Carbon steel. Base pipe is ASTM A106 Gr.B (with A53 Gr.B or API 5L Gr.B as allowed equivalents). Butt-weld fittings are ASTM A234 WPB. Forged fittings and flanges are ASTM A105. All P-No 1 Group 1 (Group 2 on some thin-wall).

**Q2. Do we need PWHT?**
A. No. The WPS explicitly states "No PWHT" for all 424 procedures. PWHT would only be triggered by ASME B31.3 wall-thickness thresholds or specific piping-class requirements — verify per line list before waiving on a specific thick-wall spool if in doubt.

**Q3. What's the maximum interpass temperature?**
A. 250 °C, per WPS-001, WPS-002, and WPS-003. This is the comfortable CS ceiling; going above risks grain coarsening but not phase instability like duplex.

**Q4. What preheat is required?**
A. Base metal temperature ≥ 10 °C. Localized preheat may be applied in cold or humid conditions to prevent condensation on the joint before welding.

**Q5. What filler metals are used?**
A. GTAW root: AWS ER70S-6, Ø 2.5 mm solid wire, F-No 6, A-No 1. SMAW fill and cap: AWS E7015 or E7018 (low-hydrogen basic), Ø 3.2 mm and Ø 4.0 mm, F-No 4, A-No 1. SAW (WPS-003 only): corresponding ER70S-6-class wire and basic flux.

**Q6. Do we do PT on 424?**
A. No. Carbon steel is ferromagnetic, so MT (magnetic particle) is used instead of PT (liquid penetrant) on socket welds, fillet welds, branch welds, and repair areas. PT is only used on non-magnetic materials like duplex (that's the 423 project).

**Q7. Do we measure ferrite on 424?**
A. No. Ferrite content is a duplex stainless acceptance criterion (related to the austenite/ferrite phase balance). Carbon steel has a single ferritic/pearlitic structure — no ferrite measurement applies.

**Q8. Do we do PMI on 424?**
A. No. Positive Material Identification by XRF is not required on plain carbon steel. The grade is verified by MTC heat-number traceability and visual confirmation of markings on the material.

**Q9. Do we do ferroxyl testing on 424?**
A. No. Ferroxyl (ASTM A380) is a post-passivation verification test for stainless steels to detect free iron. Carbon steel is painted for corrosion protection, not passivated, so ferroxyl does not apply.

**Q10. What's the surface prep standard before painting?**
A. ISO 8501-1 **Sa 2½** (near-white metal blast). Surface profile per the paint manufacturer's technical data sheet, typically Ra 40–75 μm. Dust on prepared surface must be ISO 8502-3 rating 2 or better. The blasted surface must receive the primer before any flash rust appears.

**Q11. What paint system is used?**
A. ISO 12944-5 **C5-High** — high-durability paint system for corrosivity category C5 (industrial / marine). Primer → intermediate → topcoat per the approved painting procedure; stripe coats by brush on welds, edges, bolt holes, and hard-to-reach areas before each full coat.

**Q12. What's the DFT acceptance rule?**
A. Per ISO 19840 ("80-20 rule"): no single DFT reading below 80 % of NDFT, average spot value ≥ NDFT, maximum DFT within the paint system limit. Measurements with a calibrated electronic gauge, minimum 5 readings per spot, minimum 10 spots per spool for typical sizes.

**Q13. What's the RT coverage?**
A. 100 % of circumferential butt welds, X-ray only (not γ), per ASME Section V Article 2. Acceptance per ASME B31.3 Table 341.3.2. RT is ITP step 100 and is a hold point — the spool cannot proceed until the RT is accepted and released.

**Q14. What's the MT coverage?**
A. 100 % of applicable welds — socket welds, fillet welds, branch welds, and any weld repair area. Butt welds are covered by RT, so MT is focused on the welds RT cannot reach geometrically. Per ASME Section V Article 7.

**Q15. How is welder traceability handled?**
A. Every welder has a unique welder stamp ID recorded on their WPQ. The stamp is applied near every weld (step 120 Weld Identification & Stamping) and recorded in the welding log + weld map. Each weld can be traced from the final dossier back to the exact welder, the date, the filler lot, and the WPS used.

**Q16. What's the difference between the two dimensional inspection steps?**
A. Step 130 is pre-paint — catches fabrication dimensional issues while they are cheap to fix (no painted surface to damage). Step 180 is post-paint — verifies nothing shifted during blasting, painting, or handling between the two steps. Both are 100 % coverage, 100 % of spools.

**Q17. Does 424 have a finishing line like 423?**
A. No. The 423 duplex project has a 12-station post-weld finishing line (metallographic, PT, degrease, pickling/passivation, ferrite, PMI, ferroxyl, final cleaning, photo, marking, packing, container). 424 has a simpler flow: NDT → clean → blast → paint → DFT → final dimensional → mark → dossier → pack. No passivation, no ferroxyl, no PMI, no ferrite.

**Q18. Why three WPSs (001, 002, 003)?**
A. To cover the full thickness range efficiently. WPS-001 is for the thinnest walls (≤ 6 mm) where GTAW root + SMAW fill is fast and clean. WPS-002 is for medium/thick walls (6–25 mm) where SMAW is the productive choice for fill and cap passes. WPS-003 adds SAW for thick-wall large-bore (5–32 mm) where mechanised SAW beats manual SMAW on productivity. Selection is by groove thickness per ASME IX QW-451.

**Q19. Is hydrogen cracking a risk on 424?**
A. On thick sections under restraint, yes. Mitigations in this project: low-hydrogen SMAW electrodes (E7015 / E7018), bake and holding-oven storage per manufacturer, dry surfaces before welding, preheat ≥ 10 °C with condensation control. PWHT is not required, so hydrogen control during welding itself is the mandatory barrier.

**Q20. Do we need hardness testing on 424?**
A. Not as a project-wide requirement in the 424 ITP. Hardness would only apply on specific spools if triggered by NACE MR0175 sour-service requirements on the line list — verify per line class.

---

## 10. Glossary (Glossary)

| English | Chinese term | Description |
|---------|-------------|-------------|
| Carbon Steel | Carbon Steel | CS — iron-carbon alloy, ferritic/pearlitic structure |
| A106 Gr.B | A106 Gr.B | Seamless carbon steel pipe for high-temp service |
| A234 WPB | A234 WPB | Wrought carbon steel butt-weld fittings |
| A105 | A105 | Forged carbon steel flanges and forged fittings |
| P-No 1 | P-No 1 | ASME IX base metal grouping for plain carbon steel |
| GTAW | GTAW | Gas Tungsten Arc Welding (TIG) |
| SMAW | SMAW | Shielded Metal Arc Welding (stick / MMA) |
| SAW | SAW | Submerged Arc Welding (mechanised, flux) |
| ER70S-6 | ER70S-6 | AWS solid wire filler for GTAW / GMAW on CS |
| E7015 | E7015 | AWS low-hydrogen basic SMAW electrode |
| E7018 | E7018 | AWS low-hydrogen iron-powder basic SMAW electrode |
| DCEN | DCEN | Direct Current Electrode Negative (straight polarity) |
| DCEP | DCEP | Direct Current Electrode Positive (reverse polarity) |
| Butt Weld | Butt Weld | Full circumferential weld |
| Socket Weld | Socket Weld | Small-bore pipe inserted into fitting |
| Fillet Weld | Fillet Weld | Corner/T joint weld |
| Preheat | Preheat | Minimum base metal temperature before welding |
| Interpass | Interpass | Maximum temperature between passes |
| PWHT | PWHT | Post-Weld Heat Treatment (not required on 424) |
| NDE / NDT | NDE / NDT | Non-Destructive Examination / Testing |
| VT | VT | Visual Testing |
| RT | RT | Radiographic Testing |
| MT | MT | Magnetic Particle Testing |
| Hold Point | Hold Point | ITP point that requires client release |
| Witness Point | Witness Point | Client right to attend on notice |
| ISO 8501-1 Sa 2½ | ISO 8501-1 Sa 2½ | Near-white metal blast cleaning standard |
| ISO 12944-5 | ISO 12944-5 | Paint system specification for steel in atmospheric environments |
| C5-High | C5-High | Corrosivity category C5 (industrial / marine), High durability |
| DFT | DFT | Dry Film Thickness of paint |
| NDFT | NDFT | Nominal Dry Film Thickness (spec value) |
| ISO 19840 | ISO 19840 | DFT measurement and acceptance rules |
| ISO 4624 | ISO 4624 | Pull-off adhesion test method |
| MTC | MTC | Mill Test Certificate (EN 10204 3.1) |
| WPS | WPS | Welding Procedure Specification |
| PQR | PQR | Procedure Qualification Record |
| WPQ | WPQ | Welder Performance Qualification |
| ITP | ITP | Inspection and Test Plan |
| TPI | TPI | Third Party Inspector (client / independent) |

---

## Source Documents

- `ENJOB25012424-ITP-SPL-001` — `/Users/danny/.../424/WPS:PQR/ITP/ITP ENJOB25012424.pdf` (dated 2025-12-25)
- `ENJOB25012424-WPS-SPL-002 CS GTAW+SMAW` (Rev 4) + `-PQR-SPL-002` — `/Users/danny/.../424/WPS:PQR/rev 4/R4 English/`
- `ENJOB25012424-WPS-SPL-003 CS GTAW+SAW` (Rev 4) + `-PQR-SPL-003` — `/Users/danny/.../424/WPS:PQR/rev 4/R4 English/`
- `ENJOB25011423-WPS-SPL-001 CS GTAW` (Rev 4, CS content despite 423 filename prefix) + supporting PQR-SPL-001 — `/Users/danny/.../424/WPS:PQR/rev 4/R4 English/`
- Agent memory: `project_qc_reporting_system`, `reference_qc_report_fields`, `reference_shop_welds_methodology`, `reference_tracker_architecture`, `project_chat_assistant`

## Items Still Open

1. Confirm the file-naming anomaly on WPS-001 (Rev 4 carries the ENJOB25011423 prefix but is used for 424 CS). Either rename the file to `ENJOB25012424-WPS-SPL-001 CS GTAW.pdf` for consistency, or issue a formal note that the document applies to both projects.
2. Line-list check on whether any specific 424 spools trigger ASME B31.3 PWHT thresholds by wall thickness — if yes, list those lines and add PWHT to their specific procedure.
3. Confirm `project_steps` numbering for 424 in the tracker DB aligns with this ITP (the chat agent reads step numbers live, so this is self-resolving at query time but worth verifying at the next QC review).
4. Confirm the paint product stack (specific primer / intermediate / topcoat brands and NDFT values) from the approved painting procedure and add to Section 6.3 once finalized.
