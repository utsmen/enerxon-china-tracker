# 423 Duplex SS — QC & Testing Knowledge Base

Technical reference for ENJOB25011423 Duplex S32205 piping spool fabrication. Written in English; to be translated to Chinese at runtime by the chat agent. Each section is self-contained.

---

## 1. Project Overview (项目概述)

- **Job number:** ENJOB25011423
- **Scope:** Duplex stainless steel pipe spool fabrication — 202 spools + 13 straight pipes (215 items total)
- **Base material:** ASTM A790 UNS S32205 (Duplex 2205), P-No. 10H Group 1
- **Forged fittings:** ASTM A182 F51 (flanges, SW fittings)
- **Wrought BW fittings:** ASTM A815 S31803
- **Applicable codes and standards:**
  - ASME B31.3 (Process Piping) — design, fabrication, inspection, acceptance
  - ASME BPVC Section IX — welding and welder qualification (WPS/PQR/WPQ)
  - ASME BPVC Section V — NDE methods (Art 2 RT, Art 6 PT, Art 9 VT)
  - ASME B16.25 — butt weld end preparation (bevel geometry)
  - ASTM A923 — detecting intermetallic phases in duplex (Method A screen)
  - ASTM E562 — manual point count (ferrite volume fraction reference)
  - ASTM A799 / A800 / AWS A4.2 — ferrite measurement on duplex weld metal
  - ASTM A380 / A967 — cleaning, descaling, passivation, ferroxyl test
  - ASTM E1476 — PMI (standard guide for metals identification)
  - NORSOK M-601 — welding and inspection of piping
  - NORSOK M-630 — material data sheets (weld dressing guidance)
  - SSPC-SP1 — solvent cleaning (pre-pickling)
- **Key ITP document:** ENJOB25011423-ITP-SPL-001 Rev 2, dated 2025-12-10
- **Flow after welding revision:** Rev B (station plan issued 2026-04-05)

---

## 2. Material & Metallurgy (材料冶金)

### 2.1 Why Duplex Is Sensitive
Duplex S32205 is a ~50/50 austenite/ferrite microstructure. Its corrosion performance and toughness depend on keeping that phase balance intact through welding and post-weld processing. Three failure mechanisms dominate:

1. **Phase imbalance** — excessive ferrite (> ~70%) from fast cooling, or excessive austenite (< ~30%) from slow cooling or over-alloyed filler distribution, degrades both toughness and pitting resistance.
2. **Intermetallic precipitation (sigma, chi)** — forms between ~650–950 °C on slow cooling. Causes brittleness and preferential corrosion. Controlled by limiting interpass temperature and heat input, and screened by ASTM A923.
3. **Iron contamination** — free iron embedded on the surface from carbon-steel tools, grinding discs, or brushes initiates pitting/crevice corrosion. Verified by ferroxyl test after passivation.

### 2.2 Acceptance Ranges Used on 423
- **Ferrite content (project acceptance, confirmed by Danny 2026-04-05):** weld metal **35–65 %**, HAZ **30–70 %**. Measured with calibrated Fischer Feritscope FMP30 before pickling/passivation. This supersedes the single 30–65 % band in ENJOB25011423-ITP-SPL-001 Rev 2 step 150; the ITP is to be re-aligned to these values.
- **PMI (finished weldment):** Cr ≥ 21.5 %, Mo ≥ 2.8 % (Station 06b acceptance, ASTM E1476). Full 2205 certified reference material (CRM) used for instrument validation.
- **Preheat:** > 10 °C (per WPS-001 and WPS-002).
- **Interpass temperature max:** 150 °C (per WPS-001 and WPS-002; ASME IX QW-406).
- **Heat input limits (qualified in PQR, enforced by WPS):**
  - GTAW: 10.08 kJ/cm max (ENJOB25011423-PQR-SPL-001)
  - SAW fill/cap: 21.60 kJ/cm max (ENJOB25011423-PQR-SPL-002)
- **PQR ferrite verification at qualification:** 45 % (GTAW coupon), 50 % (GTAW+SAW coupon) — both satisfactory.
- **Intermetallic phase screen:** ASTM A923 Method A (metallographic replica with Beraha etch) — no sigma or chi phase allowed. Performed at Station 02 (Metallographic).

### 2.3 Why Ferroxyl Matters
Duplex passive film is only protective if the surface is free of embedded iron. Electrolytic pickling/passivation strips oxides and rebuilds the Cr-rich passive layer; the ferroxyl test (potassium ferricyanide in dilute nitric acid, ASTM A380 §7.3.4) will turn blue on any free iron. A blue reaction = reject = return to passivation. It IS the passivation verification test and cannot be moved earlier in the flow.

### 2.4 Contamination Controls (Chloride-Free Chain)
- PT consumables: Cl + F + S total < 50 ppm, batch COA required (ASME V Art 6 note).
- Electrolyte: phosphoric-based, Cl and F free, COA.
- Final rinse water: DI/RO, conductivity < 30 µS/cm.
- No PVC plastic film (contains chlorinated plasticiser) — PE/PP only.
- No carbon-steel tools, clamps, lifting gear, brushes, or grinding discs at any stage. Stainless-only or nylon.
- Marking: vibro-peen (low-stress dot peen) only — no sharp V-stamps, as they are crack initiation sites on duplex.

---

## 3. Welding (焊接)

### 3.1 WPS Registry

Two approved welding procedures are used on 423. Both are controlled by wall thickness per ASME IX QW-451.

#### WPS-001 — GTAW (thin-wall / small-bore)
- **Procedure No.:** ENJOB25011423-WPS-SPL-001
- **Supporting PQR:** ENJOB25011423-PQR-SPL-001 (dated 2025-04-22)
- **Process:** GTAW, manual
- **Joint design:** Single-V groove, root spacing 1–3 mm, no backing
- **Base material range:** ASTM A790 S32205, P-No. 10H Grp 1 to P-No. 10H Grp 1; PQR coupon 7.11 mm wall × Ø 168.3 mm
- **Filler metal:** SFA 5.9, AWS ER2209, F-No. 6, A-No. 8, Ø 2.5 mm solid rod
- **Shielding gas:** Argon 99.99 %, 10–14 L/min
- **Backing (purge) gas:** Argon 99.99 %, 18–22 L/min
- **PWHT:** None
- **Preheat:** > 10 °C
- **Interpass temp max:** 150 °C
- **Electrical:** DC, DCEN (electrode negative); see pass table below
- **Position qualified:** 5G (uphill progression)
- **Technique:** Weave bead, weave width ≤ 2.5 × electrode Ø; multi-pass; tungsten extension 3–5 mm; arc length 1–3 mm; wind speed ≤ 1 m/s; back purge maintained; inter-pass cleaning by stainless-dedicated angle grinder.

| Pass | Process | Filler Ø | Polarity | Amps max | Volts max | Travel max (cm/min) | Heat input max (kJ/cm) |
|------|---------|----------|----------|----------|-----------|----------------------|------------------------|
| Root | GTAW | Ø 2.5 mm ER2209 | DCEN | 120 | 14 | 10 | 10.08 |
| Fill | GTAW | Ø 2.5 mm ER2209 | DCEN | 120 | 14 | 10 | 10.08 |
| Cap  | GTAW | Ø 2.5 mm ER2209 | DCEN | 120 | 14 | 10 | 10.08 |

PQR qualification results: tensile 735 / 740 MPa (base metal ductile failure), four side/face-bend specimens accepted (QW-462.2), RT satisfactory, ferrite 45 % satisfactory.

#### WPS-002 — GTAW + SAW (thick-wall / large-bore)
- **Procedure No.:** ENJOB25011423-WPS-SPL-002
- **Supporting PQR:** ENJOB25011423-PQR-SPL-002 (dated 2026-03-05)
- **Processes:** GTAW (manual) root + SAW (machine) fill and cap
- **Joint design:** Groove or groove-plus-fillet, 2 ± 1 mm root face and land, root spacing 1–3 mm, backing on deposited metal / base metal
- **Base material range:** ASTM A790 S32205, P-No. 10H Grp 1 to P-No. 10H Grp 1; PQR coupon 12 mm wall × Ø 273.1 mm. Covers STD, XS and thick-wall per WPS wall-thickness control.
- **Filler metal (GTAW root):** SFA 5.9, ER2209, Ø 2.5 mm solid rod
- **Filler metal (SAW fill/cap):** SFA 5.39, ER2209, Ø 2.5 / 3.2 mm solid wire, flux type F690AZ (trade name JINWEI)
- **Shielding gas (GTAW):** Argon 99.99 %, 10–14 L/min
- **Backing (purge) gas:** Argon 99.99 %, 18–22 L/min
- **PWHT:** None
- **Preheat:** > 10 °C
- **Interpass temp max:** 150 °C
- **Maximum pass thickness:** 2.5–3.5 mm
- **Positions qualified:** 5G + 1G (uphill progression for GTAW root; SAW per machine setup)
- **Technique:** GTAW root = weave bead; SAW fill/cap = string bead; multi-pass; single electrode; oscillation width ≤ 2.5 × electrode Ø; back purge maintained until root + 2 mm deposit; back-side cleaning by stainless-dedicated angle grinder.

| Pass | Process | Filler Ø | Polarity | Amps max | Volts max | Travel max (cm/min) | Heat input max (kJ/cm) |
|------|---------|----------|----------|----------|-----------|----------------------|------------------------|
| Root | GTAW | Ø 2.5 mm ER2209 | DCEN | 120 | 14 | 10 | 10.08 |
| Fill | SAW  | Ø 2.5/3.2 mm ER2209 + F690AZ | DCEP | 450 | 32 | 40 | 21.60 |
| Cap  | SAW  | Ø 2.5/3.2 mm ER2209 + F690AZ | DCEP | 450 | 32 | 40 | 21.60 |

PQR qualification results: tensile 775 / 785 MPa (base metal ductile failure), four side-bend specimens accepted (QW-462.2), RT satisfactory, ferrite 50 % satisfactory.

#### WPS Selection Rule
WPS selection is controlled by wall thickness. In practice:
- Small bore and thin-wall joints (typically ≤ 2″ branches, Ø ≤ 168 mm small-bore pipe, wall ≤ ~8 mm): **WPS-001 GTAW**.
- Large-bore thick-wall butt welds (typically ≥ 14″ pipe, 12 mm wall and above, STD / XS / thicker): **WPS-002 GTAW+SAW** (GTAW root + SAW fill/cap).
The welding engineer confirms the WPS on the weld map for each joint before fit-up.

### 3.2 Welder Qualification (WPQ)
- Welders must hold a current ASME IX WPQ covering the WPS, position, diameter and thickness to be welded. F-No. 6 essential-variable coverage applies (ER2209 and equivalent).
- Qualification reference test welds: Welder Zhang Lei (stamp SC03) on PQR-001; Welder Zhang Yong (stamp SH02) on PQR-002.
- Retest triggers:
  - > 6 months since last weld in the qualified process, or
  - Failed production weld traced to workmanship, or
  - Change in an ASME IX essential variable outside the WPS range.
- Welder ID stamped on weld map and traceable from production weld back to WPQ via heat number, traveller, and welding log.

### 3.3 Weld Counting Rules
- **Butt welds (对接焊缝):** full circumferential welds joining two BW components (pipe–pipe, pipe–elbow, pipe–tee, pipe–WN flange, pipe–reducer, elbow–flange). Weld diameter = pipe diameter. Large bore (≥ 14″) uses WPS-002; small bore (≤ 3″) uses WPS-001.
- **Olet welds (支管座焊缝):** sockolet or weldolet onto the main pipe. Weld diameter is the **branch** size, not the main pipe (e.g., an 18″×2″ sockolet is counted at 2″, assigned to a 2″ welder, welded by WPS-001 GTAW).
- **Branch socket welds (小口径支管承插焊缝):** SW joints on small-bore branch piping coming off an olet (pipe–sockolet, pipe–SW flange, pipe–SW elbow, pipe–SW tee). Weld Ø = branch pipe (2″ or 1″), full GTAW per WPS-001.
- **Field welds are NOT counted** as shop welds. Open ends on the spool are field joints to be made during site erection.
- **Reinforcing pads (REPADs)** are supply items only in the weld summary; their perimeter fillet is a fillet weld and not a pressure-retaining butt weld.

**Formulas:**
- Inch-diameter = Σ (Welds × Pipe Ø in inches)
- Linear metres = Σ (Welds × π × OD) / 1000, with OD in mm (NPS → OD: 24″ = 609.6, 18″ = 457.2, 16″ = 406.4, 14″ = 355.6, 3″ = 88.9, 2″ = 60.3, 1″ = 33.4)

**423 weld totals (204 spools, as counted by the fabrication matrix):**

| Weld Ø | Welds | Inch-Dia | Linear (m) |
|--------|-------|----------|------------|
| 24″ (DN600) | 149 | 3,576 | 285.4 |
| 18″ (DN450) | 74  | 1,332 | 106.3 |
| 16″ (DN400) | 39  | 624   | 49.8  |
| 14″ (DN350) | 125 | 1,750 | 139.6 |
| 3″  (DN80)  | 2   | 6     | 0.6   |
| 2″  (DN50)  | 501 | 1,002 | 94.9  |
| **Total**   | **890** | **8,290** | **676.6** |

### 3.4 Welder Field Rules — Absolute Principles for Duplex S32205

Field-validated welder guidance for 423. These are the practical discipline rules that must be followed in parallel with the WPS parameters in Section 3.1. Originally compiled from a field review of a real production batch where arc strikes (IMG_1277) and back-purge contamination (IMG_1265/66/72 internal oxidation, IMG_1286/87 small-bore branch discoloration) were found and corrected.

#### 3.4.1 Four Absolute Principles

**① Arc strikes are strictly prohibited**
Arc strikes on the base-material surface cause localised rapid quenching, producing very high ferrite (> 80 %) and nitride precipitation. This is a prohibited metallurgical defect in duplex stainless and cannot be "touched up" visually — it must be ground out and PT inspected. Arc initiation and crater-stop must be INSIDE the groove only. Never strike or test the arc on the pipe outer surface or HAZ. Reference case on 423: IMG_1277 in the production batch — required grinding and PT inspection after detection.

**② Interpass temperature ≤ 150 °C — strictly enforced**
Exceeding 150 °C disturbs the austenite/ferrite phase balance and increases sigma-phase precipitation risk. After every pass, temperature must be verified with a calibrated temperature crayon (Tempilstik) or infrared thermometer. **Do not rely on experience or feel.** Practical quick-check: if the joint feels uncomfortably hot to the touch, stop and wait — but this is only a secondary confirmation, not a replacement for measurement.

**③ Heat input 0.5 – 2.5 kJ/mm**
- **Too high** (> 2.5 kJ/mm): slow cooling → ferrite too low (< 35 %) → higher sigma-phase risk, loss of toughness.
- **Too low** (< 0.5 kJ/mm): fast cooling → ferrite too high (> 65 %) → nitrogen loss, embrittlement.
- Duplex has a very narrow process window. Weld strictly per the WPS; never improvise amps/volts/travel speed.
- SAW especially can drift above 2.5 kJ/mm if not watched; measure and record on every pass.

**④ Ferrite content 35 – 65 % (weld) / 30 – 70 % (HAZ)**
This is the **only** true metallurgical indicator for duplex steel.
- Heat-tint colour is NOT a metallurgical indicator (see clarification below).
- Ferrite below 35 % → SCC (stress corrosion cracking) risk.
- Ferrite above 65 % → embrittlement and reduced toughness.
- Measure with Fischer Feritscope FMP30 per ITP step 150, 6 points per weld (3 cap + 3 HAZ, 120° intervals).

#### 3.4.2 Back Purging / Root Shielding Gas

This was the single biggest issue found in the reference production batch (internal root oxidation IMG_1265/66/72; severe branch-weld discoloration IMG_1286/87). Back-purge discipline is non-negotiable:

- **Backing gas:** pure Argon 99.99 %, OR **Argon + 2 % N₂** (Ar + 2 % N₂ is recommended for duplex because the small nitrogen addition compensates nitrogen loss from the weld pool and helps restore austenite; either is acceptable but must be controlled end-to-end).
- **Oxygen content before arc strike:** verify with an **oxygen analyser** at the vent, below the project specification limit (for 423 the project limit is **< 0.1 %**, per NORSOK M-601 and Section 7.3). **Do not estimate by time alone** — measure every joint.
- **Purge volume:** purge for a minimum of **5 – 10 times the internal pipe volume** before starting the root pass.
- **Positive pressure maintained throughout welding** and until the weld has cooled below **300 °C** on the root side. Do not shut the purge off the moment the cap is complete.
- **Pipe end sealing:** water-soluble purge paper, aluminium foil tape, or inflatable purge plugs. Ends must be reliably sealed so the argon does not escape. Water-soluble paper is ideal because it dissolves during hydrotest.
- **Per-joint record:** purge time, gas flow rate, O₂ reading at start of welding, and maintenance during welding must be written on the welding log for every weld.

**Important clarification — heat tint vs metallurgy.** Heat-tint colour (straw → brown → blue → dark grey / black) is a SURFACE indicator of gas shielding quality and a discipline check. It is NOT a direct indicator of sigma / chi phase precipitation, and pickling per ASTM A380 can fully restore the surface corrosion resistance of heat-tinted areas. However, dark discoloration is clear evidence that back-purge was inadequate during welding, which is a process discipline failure that must be corrected at the source — not hidden by downstream pickling. If the inside of a joint comes out dark, the root cause is back-purge contamination or insufficient flow, and the welder / procedure must be addressed before the next joint.

#### 3.4.3 GTAW Root + Fill — Field Key Points

1. **Filler metal:** AWS **ER2209** Ø 2.4 mm (or Ø 2.5 mm per WPS-001). Using ER308L, ER316L, or any 304/316 filler is strictly prohibited — the filler must over-match in nitrogen and nickel to maintain phase balance.
2. **Shielding gas (torch side):** pure Argon 99.99 %, flow rate 10 – 15 L/min.
3. **Tungsten electrode:** 2 % ceriated (grey band) Ø 2.4 mm, ground longitudinally (grooves parallel to the axis of the tungsten, not across). Thoriated tungsten is acceptable but ceriated is preferred for cleaner arc starts and longer tip life on duplex.
4. **Minimum two passes on every joint:** after the root pass, at least one hot / cover pass is required so the root is reheated. This reheat is what helps restore the austenite phase in the root bead and is essential for phase balance. Single-pass root-only joints are prohibited on 423.
5. **Interpass cleaning:** stainless-steel wire brush only, dedicated to duplex work and never used on carbon steel. Carbon-steel brushes are strictly prohibited — they embed iron into the surface and cause pitting. Grinding between passes, if required, must use stainless-only flap discs / wheels.
6. **Arc start and stop:** always inside the groove. At the end of each pass, fill the crater (taper down amps or use the foot pedal to walk out the arc) to prevent crater cracking — duplex is sensitive to crater cracks.
7. **Tack welds:** made with the same filler (ER2209) and the same back-purge discipline as the root pass. Tacks must be ground flush or fully consumed into the root; never leave a tack with its own start/stop signature in the finished weld.

#### 3.4.4 GTAW Root + SAW Fill / Cap — Field Key Points (WPS-002)

1. **GTAW root:** as Section 3.4.3 — ER2209, pure Ar torch gas, full back-purge, minimum hot pass on top of the root before transitioning.
2. **SAW transition:** only after the GTAW root AND at least one GTAW hot pass are complete. Never go straight from bare GTAW root to SAW fill — the transition thermal shock plus SAW heat will disturb the root phase balance.
3. **SAW wire:** ER2209 matched with a **duplex-specific basic flux** — qualified products include Lincoln 880M, ESAB OK 10.93, or equivalent. Standard carbon-steel SAW fluxes are prohibited.
4. **Flux must be dry:** bake new / re-exposed flux at 300 – 350 °C for 2 hours before use. Keep in a heated holding oven at 100 – 150 °C during production. Moisture in SAW flux is a direct source of hydrogen and porosity and will also oxidise the weld pool — a very common SAW failure mode on duplex.
5. **Heat input control:** SAW can easily exceed 2.5 kJ/mm if the operator increases amps or slows travel to build a bigger bead. **Heat input must stay ≤ 2.5 kJ/mm (PQR-002 qualified limit is 21.60 kJ/cm ≈ 2.16 kJ/mm).** Measure every pass.
6. **Interpass temperature:** measure after every SAW pass; start the next pass only when the joint has cooled to ≤ 150 °C. SAW deposits a lot of heat per pass, so the cooling wait between SAW passes is typically longer than GTAW.
7. **Bead strategy:** narrow multi-pass welds are **strongly preferred** over wide weave beads. Narrow beads give better phase balance (faster cooling per bead), less heat accumulation, and better refinement of the underlying passes on reheat. Wide weave beads are a common cause of high-ferrite problems on duplex SAW.

#### 3.4.5 Things to Avoid When Welding Duplex Spools

Non-negotiable "do-not" list for duplex fabrication — every welder and fitter must know these:

- **No carbon-steel tools, brushes, clamps, or grinding discs anywhere near duplex.** Iron contamination is a point-corrosion initiator and will show up on the Ferroxyl test. Stainless-only or aluminium-oxide discs.
- **No marker pens containing halogens** (most general-purpose marker inks). Use duplex-approved low-halogen markers only. Clean off any marks before welding in the HAZ zone.
- **No arc strikes outside the groove.** See 3.4.1 ①.
- **No single-pass roots.** Always follow with at least a hot pass for phase recovery. See 3.4.3 ④.
- **No wrong filler.** ER2209 only. Never ER308L / ER316L / ER309L — these are austenitic and will unbalance the weld. See 3.4.3 ①.
- **No incorrect interpass temperature.** Strictly ≤ 150 °C. Measure, don't guess. See 3.4.1 ②.
- **No back-purge shortcuts.** Always measure O₂, always time the purge volume, always seal the ends, always maintain positive pressure until the root is below 300 °C. See 3.4.2.
- **No PVC plastic, PVC tape, or chlorinated markers.** Chloride contamination causes pitting and stress corrosion cracking on duplex. PE/PP only for any film or plug material in contact with the pipe.
- **No oxy-fuel flame cutting on duplex pipe.** Use plasma, abrasive saw, or mechanical cutting only. Oxy-fuel introduces iron-rich oxide contamination in the cut area.
- **No carbon-steel clamps or fixtures touching the pipe.** Rent / build dedicated stainless-faced fixtures, or use thick rubber / PE spacers between any CS clamp and the duplex pipe.
- **No grinding the HAZ after welding unless absolutely necessary** — NORSOK M-630 prefers as-welded surfaces. If grinding is done, it must use stainless-dedicated flap discs and be followed by pickling + passivation + ferroxyl.
- **No leaving hot work near duplex pipe** — sparks from CS work done nearby will contaminate the duplex surface. Erect a physical barrier or schedule duplex and CS work in different zones.
- **No reusing consumables once the flux can / electrode can has been opened beyond the manufacturer's exposure time.** Bake or discard per flux/electrode data sheet.
- **No welding on a wet, oily, painted, marked, or otherwise contaminated surface.** Wipe with IPA, dry, and visually verify before striking the arc.
- **No V-stamps or hard-punch markings on the pipe body.** They are crack initiation sites on duplex. Vibro-peen only, away from weld and HAZ (see Section 6 Finishing).

#### 3.4.6 Field Inspection Checklist (per joint)

Quick field checklist welders and QC should follow for each 423 duplex weld:

- [ ] Joint groove clean, dry, no oil / marker / oxide / iron contamination
- [ ] Fit-up within spec (root gap 1–3 mm, bevel, hi-lo, cleanliness)
- [ ] Both pipe ends sealed (water-soluble paper / tape / plugs) for back purge
- [ ] Back purge started, O₂ measured at vent, below 0.1 % before arc strike
- [ ] Back purge volume ≥ 5–10 × internal pipe volume, time logged
- [ ] Preheat ≥ 10 °C verified (condensation removed in cold conditions)
- [ ] Filler metal is ER2209, correct diameter, lot number logged
- [ ] Tungsten is 2 % ceriated Ø 2.4 mm, longitudinally ground
- [ ] Shielding gas pure Ar 99.99 % at 10–15 L/min, verified
- [ ] Arc strike inside groove only — never on base material surface
- [ ] Interpass ≤ 150 °C verified with crayon or IR thermometer after every pass
- [ ] Hot pass completed on top of GTAW root before any SAW transition
- [ ] Stainless-only wire brush for interpass cleaning
- [ ] Crater filled at every arc-stop
- [ ] Heat input in range 0.5–2.5 kJ/mm per pass, recorded
- [ ] Back purge maintained until root cooled below 300 °C
- [ ] Weld ID stamp and welder stamp applied per weld map
- [ ] Back purge time, flow, O₂ reading, ferrite reading recorded on welding log

---

## 4. NDT Procedures (无损检测)

### 4.1 Visual Testing — VT (目视检测)
- **Standard:** ASME B31.3 acceptance criteria, examination per ASME V Art 9.
- **Coverage:** 100 % of production welds, all spools.
- **ITP step:** 110 (after welding, before NDT).
- **Acceptance criteria (B31.3 Normal Fluid Service):** no cracks, no lack of fusion, no incomplete penetration (for BW welds accessible to VT), no porosity exposed at surface, weld reinforcement within code limits, no arc strikes on base metal, undercut ≤ 1 mm and ≤ specified fraction of wall, no visible slag or spatter left on surface.
- **Typical findings:** surface porosity cluster, undercut at toe, arc strikes from tack or carbon-steel clamp contact, excessive reinforcement.
- **Documentation:** VT report per weld, covering weld ID, welder ID, weld type (BW/SW/fillet), size/schedule, process, surface condition, checks list (undercut/porosity/fusion/cracks/reinforcement/arc strikes/spatter/profile), ACC / REJ, remarks. Report numbered per ENJOB25011423 report series.
- **Examiner:** QC inspector (no specific level required by B31.3 for VT when performed by QC, but examiner must be qualified per employer's written practice).

### 4.2 Radiographic Testing — RT (射线检测)
- **Standard:** ASME Section V Article 2; acceptance per ASME B31.3 (Normal Fluid Service unless project calls out Severe Cyclic).
- **Technique on 423:** X-ray only per ITP step 120 note. (γ sources not used on 423.) Single-wall single-image (SWSI) or double-wall single-image (DWSI) depending on geometry and accessibility.
- **Coverage:** 100 % of applicable butt welds (all BW production welds on spools).
- **ITP step:** 120. Witness point (W) — client has notification rights only.
- **Shift:** RT is performed on the night shift with the factory evacuated, for radiation safety. Two independent Level II operators work the night shift; the day crew is not on site during RT.
- **IQI:** wire or hole-type per ASME V Art 2 Table T-276; designation selected per material thickness range.
- **Film density:** 1.8–4.0 through the area of interest (ASME V).
- **Sensitivity:** required sensitivity per IQI designation achieved and documented on each film.
- **Acceptance criteria (ASME B31.3 Table 341.3.2):** no cracks, no lack of fusion, no incomplete penetration (except for single-sided welds without backing, which have a specific allowance), rounded indications within code limits, slag inclusions within code size/length limits, no burn-through on root.
- **Typical findings:** lack of root fusion (especially on GTAW root with inadequate back purge), elongated slag (SAW fill), isolated porosity, tungsten inclusion (GTAW).
- **Documentation:** RT report per weld with film ID, SFD, source, technique, IQI designation, achieved sensitivity, film density, indication types/length, ACC / REJ. Films archived. **Level II or Level III interpreter signature required**, QC inspector review, TPI witness.

### 4.3 Liquid Penetrant Testing — PT (渗透检测)
- **Standard:** ASME Section V Article 6; acceptance per ASME B31.3 Table 341.3.2.
- **Coverage:** 100 % of applicable welds on duplex spools — SW welds, fillet welds, branch welds, and all repair areas. Butt welds that receive RT do not normally receive PT unless the surface has been ground and re-inspection is required.
- **ITP step:** 130 (after RT, or on joint types where RT is not applicable).
- **Consumables:** low-halogen only. Penetrant, remover, and developer must each carry a batch COA confirming Cl + F + S total < 50 ppm (ASME V Art 6 T-641 note on austenitic and duplex stainless steels).
- **Technique:** visible, solvent-removable (colour-contrast) is standard on 423. Fluorescent method permitted if project approves.
- **Dwell times:** per Article 6 T-672 — 5 min minimum penetrant dwell; 10 min minimum developer dwell; adjusted per product COA and surface temperature.
- **Surface temperature:** 5–50 °C (standard range); outside this band requires qualification per Article 6.
- **Acceptance criteria (B31.3 Table 341.3.2):**
  - No cracks (any linear indication).
  - Rounded indications acceptable within size/spacing limits.
  - Linear indications (length > 3 × width) are rejectable.
- **Typical findings:** tight toe crack at weld termination, porosity exposed after grinding, crater crack at arc stop.
- **Documentation:** PT report per weld — weld ID, welder ID, size, technique, penetrant type + batch, dwell times, surface temp, indication type (linear / rounded / none), ACC / REJ. **Examiner must be Level II or higher.** Because PT is performed in the dirty zone (Station 03), spools then cross the hard barrier into the clean zone before degreasing.

### 4.4 Positive Material Identification — PMI (材质鉴定)
- **Standard:** ASME B31.3 §323.2.4; method guidance ASTM E1476.
- **Instrument:** handheld XRF analyser (2205 CRM standard block used for daily calibration check). Serial, model, calibration certificate, and cal date recorded on every report.
- **Timing — two stages:**
  1. **Incoming PMI (ITP step 20):** verify every heat of base material and consumables before cut and release to production. Confirms UNS S32205 on pipe/fittings/flanges and ER2209 on filler metal.
  2. **Finished-spool PMI (ITP step 140) / Station 06b:** performed after pickling/passivation on a clean surface. XRF reads directly without grinding, avoiding iron contamination from abrasive discs.
- **Coverage:** 100 % on incoming (each heat / lot) and 100 % on finished spools (every spool; one reading each on base metal and deposited weld metal as minimum; project may specify per-weld).
- **Acceptance (duplex 2205 finished weldment):** Cr ≥ 21.5 %, Mo ≥ 2.8 %, with Ni, Mn, Fe consistent with 2205. Reject any reading that the analyser reports as not matching 2205 grade library.
- **Typical findings:** mismatched filler (ER309 or 316L used by mistake), carbon-steel contamination in the PMI window from weld spatter, incorrect heat on traveller.
- **Documentation:** PMI report per test point — item description, heat, grade, test location (base / weld / HAZ), elemental %, grade confirmed, ACC / REJ, instrument serial + cal date. Operator signs, QC reviews, TPI witnesses.

### 4.5 Ferrite Measurement (铁素体测量)
- **Standard:** ASTM A799 / A800, AWS A4.2; reference ASTM E562 (manual point count) for calibration of the gauge against metallographic sections.
- **Instrument:** Fischer Feritscope FMP30 (or equivalent), calibrated with duplex ferrite number (FN) standards. Reports in % ferrite (converted internally from FN for duplex).
- **Coverage:** every weld on every duplex spool.
- **Measurement points:** 6 per weld recommended — 3 on the weld cap and 3 on the HAZ, at 120° intervals around the circumference. Record individual readings and average.
- **When:** ITP step 150, before pickling and passivation (oxide scale biases the reading).
- **Acceptance (confirmed by Danny 2026-04-05):** weld metal **35–65 %**, HAZ **30–70 %**. Reject if outside the band; escalate to welding engineer for possible re-weld. This supersedes the single 30–65 % band shown in ITP Rev 2; the ITP will be re-aligned.
- **Typical findings:** high ferrite (> 65 %) from fast cooling on small-bore GTAW with minimal interpass — correction is slower cooling, higher interpass (still ≤ 150 °C), or re-weld; low ferrite (< 30 %) from excessive heat input or too many passes — correction is heat-input control or re-weld.
- **Documentation:** Ferrite report per weld — weld ID, welder ID, size, 6 readings, average, ACC / REJ, instrument serial + cal date.

### 4.6 Ferroxyl Test — Free Iron Detection (铁氰化钾测试)
- **Standard:** ASTM A380 §7.3.4, ASTM A967.
- **Purpose:** verify no free iron contamination remains on the passivated duplex surface. It is the formal verification of the pickling/passivation step.
- **Reagent:** potassium ferricyanide K₃[Fe(CN)₆] ~3 g/L in dilute nitric acid ~10 g/L in DI water. **Fresh solution every 4 hours** — discard older reagent.
- **ITP step:** 200 (Post-Passivation Inspection); Station 07 of the Rev B flow.
- **Coverage:** 100 % — every spool.
- **Technique:** spray or brush on test areas (welds, HAZ, and accessible base metal near welds). Observe for 6 minutes. Any blue spot indicates ferricyanide reaction with Fe²⁺ → free iron present → reject.
- **Acceptance:** no blue reaction at 6 min.
- **Action on failure:** return spool to Station 05 (electrolytic pickling/passivation), re-test after re-passivation. Repeat until accepted. Document as an NCR if repeats exceed allowable.
- **Documentation:** Ferroxyl report per spool — test area locations, surface condition, observation time, copper/blue deposit observed Y/N, ACC / REJ, reagent batch and preparation time, photo evidence.
- **Rinse immediately after test:** the ferroxyl reagent itself is acidic and contains ferricyanide; rinse the tested surface with DI water after the result is read, so reagent residue does not remain on the spool.

### 4.7 Dimensional Inspection (尺寸检验)
- **Standard:** ASME B31.3 para 335 (fabrication), ASME B16.25 (bevel ends), ENJOB25011423 approved spool drawings.
- **Instruments:** calibrated tape measure, digital calipers, squares, levels, protractors, flange-hole templates. All instruments with calibration sticker in date.
- **ITP step:** 170 (Final Dimensional Inspection). Hold point (H + W).
- **Coverage:** 100 % of spools and straight pipes.
- **Key dimensions recorded:**
  - Overall length, width, height envelope.
  - Face-to-face and face-to-centre of each flanged branch.
  - Flange bolt-hole orientation (±1.5 mm typical, confirm per drawing note).
  - Flange face perpendicularity (≤ 0.5 % OD, max 2 mm per B31.3 §335.1.1).
  - Elbow angle accuracy and fitting orientation.
  - Branch dimensions (centre-to-end for each branch).
  - Bevel geometry on open (field weld) ends per B16.25.
- **Acceptance:** nominal vs actual vs deviation within drawing tolerance. Any dimension outside tolerance requires engineering review, cut and re-weld, or rework.
- **Documentation:** Dimensional report per spool — drawing number, all measured dimensions with nominal / actual / deviation / within tolerance Y-N, instruments used with calibration IDs. Straight pipes: length, squareness, bevel (if bevelled) — dimensional report still required per the report matrix in Section 8.

### 4.8 Metallographic Examination (金相检验)
- **Standard:** ASTM A923 Method A (intermetallic phase screen for duplex).
- **Technique:** in-place metallographic replica using portable polishing kit + Beraha's reagent etch + microscope inspection (or replica film transported to a lab microscope).
- **ITP step:** not listed as a separate numbered step in ENJOB25011423-ITP-SPL-001 Rev 2 but performed as Station 02 of the Rev B flow after welding, immediately after RT and before PT.
- **Coverage (confirmed by Danny 2026-04-05):** **sampling — a few replicas per welder** (not 100 %). The intent is to screen each welder's technique for intermetallic phases, not every weld. Exact sample count per welder to be set by the QC manager in the work pack; typical practice is 2–3 replicas per welder across their produced welds, biased toward thicker/higher-heat-input joints.
- **Acceptance:** no sigma phase, no chi phase, no carbide precipitation along phase boundaries; phase balance visually within 30–70 % austenite / ferrite range (A923 Method A is a screen, not a quantitative measurement).
- **Action on failure:** A923 Method A flag → escalate to engineering; may require Method B impact test or Method C corrosion test on a sacrificial coupon; if confirmed, re-weld with corrected heat input.
- **Documentation:** metallographic report per weld with replica photo, etch details, observations, ACC / REJ.

---

## 5. ITP Flow — Inspection & Test Plan (检验与试验计划)

The controlling document is **ENJOB25011423-ITP-SPL-001 Rev 2, dated 2025-12-10**. Inspection codes used: **H** hold point, **W** witness, **R** document review, **V** verify, **I** inspect, **f** 100 %, **c1** sampling, **X** mandatory supplier action. A hold point cannot be released without client authorisation.

### 5.1 ITP Step Table

| # | Step | Code | Sample / Freq | Acceptance reference | Control record |
|---|------|------|---------------|----------------------|----------------|
| 10 | Raw Material Receiving (pipes, fittings, flanges) | H+f+X+W | Each lot | BOM, PO, MTC, B31.3 | Incoming inspection report |
| 20 | Incoming PMI Verification (base + consumables) | H+f | Each heat / lot | B31.3 §323.2.4; confirm S32205, ER2209 | Incoming PMI report |
| 30 | Material Identification & Traceability | H+f+W | Each batch | Heat-number linkage to MTC | Traceability log |
| 40 | Material Segregation & Contamination Control | I+f | Continuous | No CS tools, Cl-free markers | Contamination checklist |
| 50 | Review of Fabrication Documents (WPS, PQR, WPQ, NDT, ITP) | R+f+X | Once before start | B31.3, ASME IX | Approved document register |
| 60 | Welding Equipment & Consumables Verification | V+c1 | Before welding, 100 % | Calibration valid, ER2209 per WPS | Calibration + consumable logs |
| 70 | Pipe Cutting per Spool Drawings | H+c1 | Each spool, 100 % | Length, squareness, no thermal damage | Cutting inspection record |
| 80 | End Preparation / Beveling | W+c1 | Each spool, 100 % | ASME B16.25, SS grinding discs only | Fit-up checklist |
| 90 | Fit-up & Assembly | H+c1 | Each spool, 100 % | WPS/drawing alignment, gap, orientation; no CS contact | Fit-up report |
| 100 | Production Welding (GTAW / GTAW+SAW) | H+c1 | Continuous, 100 % | WPS-SPL-001 / WPS-SPL-002; interpass ≤ 150 °C | Welding log + traveller + interpass + heat input records |
| 110 | Visual Testing (VT) | H+f | Each spool | B31.3 | VT report |
| 120 | Radiographic Testing (RT, X-ray) | H+f+W | Each spool, 100 % applicable welds | ASME V / B31.3 | RT report + films |
| 130 | Liquid Penetrant Testing (PT) | H+f+W | Each spool, 100 % applicable welds | ASME V Art 6 + B31.3; Cl-free consumables | PT report |
| 140 | PMI on Finished Spools | H+f+W | Each spool | S32205 verification | PMI report |
| 150 | Ferrite Content Measurement | H+f | Each spool | Weld 35–65 %, HAZ 30–70 % (project, 2026-04-05) | Ferrite report |
| 160 | Weld Identification & Stamping (low-stress only) | I+f | Each spool | WPQ traceable | Weld map |
| 170 | Dimensional Inspection (Final) | H+f+W | Each spool | Drawings + B16.25 | Dimensional report |
| 180 | Cleaning (Pre-Pickling) | I+f | Each spool | SSPC-SP1 | Cleaning record |
| 190 | Pickling & Passivation | f | Each spool | ASTM A380 / A967 | Passivation record |
| 200 | Post-Passivation Inspection incl. Ferroxyl | H+f+W | Each spool | ASTM A380 / A967 | Inspection record + ferroxyl result |
| 210 | Final Marking & Identification | H+f+X | Each spool | ENJOB25011423-MAT-SPL-001 matrix, Cl-free markers | Marking log |
| 220 | Packing & Dispatch | c1 | Each shipment, 100 % | Packing spec, no CS contact | Packing list / checklist |
| 230 | Final Documentation (Dossier) | R+f+X | Each shipment | Complete MTC / WPS / PQR / WPQ / NDT / PMI / Ferrite / Dimensional / Pickling / Marking | Dossier index |

### 5.2 Hold Points (client release required before proceeding)
Steps 10, 20, 30, 70 (via H+c1), 90, 100, 110, 120, 130, 140, 150, 170, 200, 210.

### 5.3 Witness Points (client right to attend on notice)
Steps 10, 30, 120, 130, 140, 170, 200.

### 5.4 Review Points (client document review)
Steps 50, 230.

### 5.5 Mapping to Tracker `project_steps`
The tracker website (`enerxon-china-tracker.onrender.com`) stores the checklist for 423 in the `project_steps` table. Each website step corresponds to a production milestone; QC reports link back to the step via the `itp_step` field on `qc_report_defs` in `project_settings`. The 10 QC reports configured for 423 are: **cutting, fitup, welding_log, vt, rt, pt, pmi, ferrite, dimensional, ferroxyl**. The `qc/seed` endpoint auto-populates report skeletons from the DXF extract. The date that appears on each report is taken from `progress.completed_at` (the checklist tick date), not the form-fill date. The chat agent reads the current step_number list live from the DB, so the mapping stays self-consistent even if the QC manager edits it via the ⚙ settings panel.

---

## 6. Finishing & Surface (后处理表面)

Rev B finishing campaign — 12 stations + RT night shift. 10 day-shift workers + 2 RT night operators, 14-day pipelined schedule, steady state from Day 5 at ~15 spools/day throughput. All equipment and consumables must follow the chloride-free chain described in Section 2.4.

### 6.1 Station Flow
```
1  RT (night, factory evacuated) — γ/X-ray, films, ASME V Art 2
    ↓ (next day)
2  Metallographic — replica + Beraha, ASTM A923 Method A
    ↓
3  PT — low-halogen, 2×3 m drip pool
    ↓
   [HARD BARRIER — dirty → clean, no PPE/tools/gloves cross]
    ↓
4  Pre-Passivation Degrease — IPA wipe weld + HAZ + 25 mm around
    ↓
5  Electrolytic Pickling/Passivation — 3 × Cougartron FURY (2 active + 1 spare)
    Phosphoric Cl/F-free electrolyte, pH 6–8 neutralise rinse
    ↓
6  Ferrite Test — Feritscope FMP30, 6 points per weld
    ↓
6b PMI — handheld XRF, Cr ≥ 21.5 %, Mo ≥ 2.8 %, 2205 CRM
    ↓
7  Ferroxyl Test — K-ferricyanide fresh every 4 h, blue → reject → back to [5]
    ↓
8  Final Cleaning Pool — HP wash 80–120 bar → neutral Cl-free cleaner → DI rinse
   (conductivity < 30 µS/cm) → oil-free air dry → white-glove test
    ↓  (13 straight pipes enter the flow here, bypassing [1]–[7])
9  Photo Documentation — photos per weld and per spool
    ↓
10 Marking — vibro-peen only (no V-stamps), located away from weld and HAZ
    ↓
11 Packing — 3 layers: PE film → bubble wrap → ENERXON branded outer cover;
   polyester slings at CoG, silica gel inside, flange and bevel caps fitted
    ↓
12 Container Loading — 40' OT, HDPE floor + HDPE wall/inter-spool pads,
   polyester straps only (no chain, no wire), corner protectors
```

### 6.2 Key Technical Decisions
- **RT on night shift, factory evacuated** — radiation safety. Two Level II operators independent of day crew.
- **PMI after passivation, not before** — clean surface gives reliable XRF, and grinding for PMI would introduce iron contamination.
- **Ferroxyl must stay after passivation** — it IS the passivation verification test.
- **Conditional pre-PT grinding** — only when paint, marker, heavy spatter, or rough cap is present. Stainless-only discs, light pass ≤ 0.5 mm. NORSOK M-630 prefers as-welded. Downstream passivation + ferroxyl compensate for any minor Fe pickup.
- **3 electrolytic machines** — 606 welds × ~1.5 min/weld ≈ 15 h on a single machine = bottleneck. 2 parallel + 1 spare gives ~8 h/day with failure buffer.
- **Marking vibro-peen only** — sharp V-stamps are crack initiation sites on duplex.
- **Straight pipes (13)** skip stations [1]–[7] and enter directly at Final Cleaning Pool [8]. They have no production welds.
- **Photo counts:** per-weld photos at Metallographic, PT, Ferrite, PMI, Ferroxyl; per-spool photos at pre-packing (marking + full spool + placard); container photos (empty / mid-load / full / sealed).

### 6.3 Surface Acceptance Criteria
- **Pre-pickling cleanliness:** SSPC-SP1 — visibly free of oil, grease, soil, paint, marker, chalk, and loose contaminants.
- **Post-passivation surface:** uniform matte to semi-bright finish, no heat-tint colour remaining on welds or HAZ, no etch pits, no embedded grit.
- **Ferroxyl:** no blue reaction at 6 min (100 % accepted).
- **Final rinse water:** DI/RO, conductivity < 30 µS/cm, confirmed at each rinse cycle.
- **White-glove test:** white cotton glove wiped over weld area and random base-metal spots — no visible soil transfer.
- **Final dryness:** no residual moisture inside or outside the spool; oil-free compressed air drying mandatory before photo documentation.

---

## 7. Cutting & Fit-up (切割与组对)

### 7.1 Cutting (ITP step 70)
- **Method:** mechanical sawing or plasma with stainless-dedicated cutting wheels; no carbon-steel contaminated wheels. Thermal damage must be avoided — the heat-affected zone from improper cutting can alter duplex phase balance and must be ground out or removed by additional cut-back.
- **Kerf allowance:** 50 mm nominal for planning (project convention from the production pipeline).
- **Tolerance:** per ENJOB25011423 spool drawings and B31.3. Length and squareness checked on every cut piece.
- **Reaction if out of tolerance:** recut or rework; cut piece may be used on a shorter spool if length permits.

### 7.2 End Preparation / Beveling (ITP step 80)
- **Standard:** ASME B16.25.
- **Bevel geometry (standard Figure 1 / 2 per B16.25 depending on wall):**
  - For wall ≤ 22 mm: single-V, 37.5° ± 2.5° included half-angle (75° included), root face (land) 1.6 ± 0.8 mm.
  - For wall > 22 mm: compound bevel per B16.25 Figure 3.
- **Root face / gap used on 423 PQR joints:** root face and land 2 ± 1 mm, root spacing 1–3 mm (from WPS-001 and WPS-002 detail).
- **Tools:** stainless-only grinding discs for finishing the bevel and land. Never use a carbon-steel-contaminated grinder.
- **Reaction if out of tolerance:** re-bevel.

### 7.3 Fit-up (ITP step 90)
- **Alignment / hi-lo:** per WPS and drawings. Industry rule used as a working guide on 423: internal mismatch ≤ 1.5 mm or 20 % of the thinner wall, whichever is less (B31.3 §328.4.3). Confirm against project-specific drawing note before production.
- **Root gap:** 1–3 mm (per WPS-001 / WPS-002).
- **Tack welds:** made with the qualified WPS, same filler, tack length and spacing per welder practice; tack quality included in fit-up check.
- **Joint cleanliness:** wiped clean, free of oil, moisture, marker, and surface oxide; purge dam installed if the joint will receive Argon back purge.
- **Back purge preparation:** dams installed; purge Argon 99.99 % at 18–22 L/min; vent maintained; **O₂ content in the purge atmosphere verified < 0.1 % before starting root pass** (NORSOK M-601 duplex standard, adopted as the project limit — confirmed by Danny 2026-04-05). Measured with an oxygen analyser at the vent before striking the arc.
- **No carbon-steel contact:** no CS clamps, CS fixtures, or CS tack plates. SS or SS-protected fixtures only.
- **Reaction if out of tolerance:** adjust fit-up before tacking; re-tack if tacks are out of alignment.

---

## 8. Documentation & Certification (文件与认证)

### 8.1 EN 10204 Type 3.1 Traceability
Every spool dossier must provide a complete, unbroken chain of traceability:
- Heat number on pipe / fitting / flange → MTC Type 3.1 from mill (with chemistry and mechanical tests).
- Heat number linked to cut piece and to the spool via the traveller / heat-map and fit-up record.
- Consumable (ER2209, F690AZ flux) batch / heat linked to welds via the welding log.
- Welder ID on each weld linked to WPQ via the weld map.

### 8.2 Report Numbering Convention
Report series: `ENJOB25011423-REC-SPL-NNN-NNN` where the first NNN is a per-report-type base sequence and the last NNN is the consecutive report number within that type. Example: `ENJOB25011423-REC-SPL-001-001`. The first component is fixed by project; the last is auto-incremented.

### 8.3 Mandatory Report Matrix per Spool Type

| Report | 423 Spool | 423 Straight Pipe |
|--------|-----------|-------------------|
| Cutting Inspection | ✓ | ✓ |
| Fit-up Report | ✓ | — |
| Welding Log | ✓ | — |
| Visual (VT) | ✓ | — |
| Radiographic (RT) | ✓ | — |
| Penetrant (PT) | ✓ | — |
| PMI | ✓ | — |
| Ferrite | ✓ | — |
| Weld Map | ✓ | — |
| Dimensional | ✓ | ✓ |
| Pickling / Passivation record | ✓ | — |
| Ferroxyl | ✓ | — |

Straight pipes (13 items) need only cutting and dimensional reports: no production welds, therefore no fit-up, welding log, VT, RT, PT, PMI, ferrite, passivation, or ferroxyl. They still enter the final cleaning pool for surface cleanliness.

### 8.4 Common Header (ALL Reports)
1. Report No.
2. Date (from checklist step completion, not form fill date)
3. Project Name / Job No. (ENJOB25011423)
4. Contract / PO No.
5. Client Name
6. Drawing / ISO No.
7. Spool No. / Mark No.
8. Material Specification & Grade (ASTM A790 S32205)
9. Applicable Procedure No. + Rev (WPS-SPL-001 or WPS-SPL-002)
10. ENERXON logo + IQNet + ISO 9001 certifications
11. Page ___ of ___

### 8.5 Signature Requirements per Report

| Report | Examiner | QC Review | TPI |
|--------|----------|-----------|-----|
| VT | QC Inspector | — | Witness |
| RT | Level II/III Interpreter | QC Inspector | Witness |
| PT | Level II+ Examiner | QC Inspector | Witness |
| Fit-up | QC Inspector | — | Hold |
| Welding Log | Welder + QC | — | Witness |
| PMI | PMI Technician | QC Inspector | Witness |
| Ferrite | Technician | QC Inspector | Witness |
| Dimensional | QC Inspector | — | Witness |
| Passivation | Operator + QC | — | Witness |
| Ferroxyl | QC Inspector | — | Witness |

### 8.6 MTC Handling and Rebranding
Factory MTCs (from Chinese mills) are rebranded from factory letterhead to ENERXON layout for the customer dossier. Rebranding rules:
- Logo and company stamp are swapped (factory → ENERXON).
- Chinese original text is retained unless specifically asked to remove.
- Factory stamp is kept transparent-overlay (not deleted).
- MTC pages are assembled in heat-number order behind each spool section of the dossier, with page break rules that keep one heat MTC intact across pages.
- Never use openpyxl `insert_rows` on complex MTC templates; work from a reference layout instead (learned from prior rebranding incidents).

### 8.7 Final Dossier (ITP step 230)
- Complete MTCs.
- WPS, PQR, WPQ for every welder who contributed to the shipment.
- VT, RT (with films), PT reports.
- PMI reports (incoming + finished).
- Ferrite reports.
- Metallographic (A923 Method A) sample reports — a few replicas per welder.
- Dimensional reports.
- Pickling / passivation records.
- Ferroxyl results.
- Marking log.
- Packing list.
- Dossier index front page.

Shipment is held until the dossier is complete.

---

## 9. Common Questions & Answers (常见问答)

**Q1. What is the ferrite acceptance range for 423?**
A. Project acceptance (confirmed 2026-04-05): **weld metal 35–65 %, HAZ 30–70 %**. Measured with a calibrated Fischer Feritscope FMP30 before pickling/passivation, taking at least 6 readings per weld (3 on cap, 3 on HAZ). This supersedes the single 30–65 % band shown in ITP Rev 2; the ITP will be re-aligned at its next revision.

**Q2. What is the maximum interpass temperature on 423 welds?**
A. 150 °C maximum, per both WPS-SPL-001 (GTAW) and WPS-SPL-002 (GTAW+SAW), as required by ASME IX QW-406 preheat/interpass controls and duplex metallurgy. If interpass is exceeded, stop welding and let the joint cool before the next pass.

**Q3. What WPS do we use for 8-inch duplex butt welds?**
A. WPS selection is by wall thickness, not nominal diameter. An 8″ pipe with standard wall (~8.2 mm) typically falls in the GTAW range and is welded with WPS-SPL-001. Thick-wall 8″ (XS and heavier) is welded with WPS-SPL-002 GTAW root + SAW fill/cap. The welding engineer confirms the WPS on the weld map for each joint.

**Q4. What is the RT coverage on 423?**
A. 100 % of applicable production butt welds on spools, X-ray only, per ITP step 120 and ASME V Art 2. RT is performed on the night shift with the factory evacuated for radiation safety. Straight pipes do not have production welds and therefore do not receive RT.

**Q5. How long does passivation take?**
A. Electrolytic pickling/passivation with a Cougartron FURY takes about 1.5 minutes per weld. 606 welds divided across 2 parallel machines gives ~8 hours of process time per day during steady state, with a 3rd machine held as spare. The spool then moves to ferrite, PMI, and ferroxyl within the same day.

**Q6. What happens if the ferroxyl test fails?**
A. Any blue spot observed within the 6-minute observation window means free iron is present. The spool returns to Station 05 (electrolytic passivation) for re-treatment and is re-tested. Repeat until accepted. Record as an NCR if more than one repeat is needed on the same spool.

**Q7. When do we do PMI on duplex?**
A. Twice: (1) incoming PMI on every heat of base metal and consumables before release to production (ITP step 20); (2) finished-spool PMI after passivation on a clean surface (ITP step 140 / Station 06b). Acceptance on the finished spool is Cr ≥ 21.5 % and Mo ≥ 2.8 %.

**Q8. Why is PMI performed after passivation, not before?**
A. Passivated surface is clean and stable, so the XRF reads without grinding. Grinding before PMI would introduce iron contamination from the disc, defeating the purpose of the later ferroxyl test. Ferrite, PMI, and ferroxyl share one QC inspector at one bench in the Rev B flow.

**Q9. Why are chloride-free materials required for PT?**
A. Duplex stainless is highly susceptible to chloride stress-corrosion cracking. PT consumables (penetrant, remover, developer) must carry a batch COA confirming Cl + F + S total < 50 ppm, per ASME V Art 6 T-641 note. Tap water, bleach, HCl, and PVC plastic are forbidden in the PT area for the same reason.

**Q10. What heat input limit applies on 423?**
A. Qualified by PQR and enforced by WPS: **GTAW 10.08 kJ/cm max** (both root and fill/cap in WPS-001; root only in WPS-002). **SAW 21.60 kJ/cm max** (fill and cap in WPS-002). Heat input is calculated as (60 × Amps × Volts) / (Travel cm/min × 1000) in kJ/mm, or (Amps × Volts × 60) / (Travel cm/min) in J/cm. Welders record amps, volts, travel per pass in the welding log.

**Q11. What is the inter-pass cleaning method?**
A. Stainless-dedicated angle grinder (SS grinding wheels only), per WPS-001 and WPS-002 technique note. Carbon-steel brushes or contaminated discs are forbidden.

**Q12. Why is marking done with vibro-peen and not V-stamp?**
A. Sharp V-stamp hard-striking introduces a stress-concentration notch that can act as a crack initiation site in duplex under service loads, especially in chloride environments. Low-stress vibro-peen produces a dot pattern without deep deformation. Marking location must also be **away from the weld and HAZ** and applied with chloride-free markers during intermediate steps.

**Q13. What sigma-phase check is done on 423?**
A. ASTM A923 Method A (metallographic replica + Beraha etch) at Station 02, immediately after RT and before PT. Any sigma or chi phase observation is escalated to engineering, which may trigger A923 Method B (impact) or Method C (corrosion) confirmation on a sacrificial coupon, and may lead to re-weld.

**Q14. Are straight pipes tracked the same as spools in the tracker?**
A. No — straight pipes have `spool_type = STRAIGHT` in the database. QC reports with `spool_only: true` (fit-up, welding log, VT, RT, PT, PMI, ferrite, weld map, passivation, ferroxyl) are automatically hidden for straight pipes. They receive only cutting and dimensional reports, and they enter the finishing flow at Station 08 (Final Cleaning Pool), bypassing NDT stations.

**Q15. What is the filler metal on 423?**
A. **AWS ER2209** for both WPS. Format depends on process: Ø 2.5 mm solid rod (SFA 5.9) for GTAW root, and Ø 2.5 / 3.2 mm solid wire (SFA 5.39) with flux type F690AZ (trade name JINWEI) for SAW fill/cap. F-No. 6, A-No. 8.

**Q16. What purge gas is used and why?**
A. Argon 99.99 %, flow 18–22 L/min as back-purge on the root side and 10–14 L/min as GTAW shielding. Argon prevents root-side oxidation ("sugaring") of the duplex weld, which would otherwise destroy corrosion resistance of the inside surface. The root is not allowed to be welded until back-purge O₂ content is **< 0.1 %** (NORSOK M-601, adopted as the 423 project limit). Verified with an oxygen analyser at the vent before striking the arc.

**Q17. What is the hold point before dispatch?**
A. ITP step 200 (Post-Passivation Inspection incl. Ferroxyl) and step 210 (Final Marking) are both hold points. The final documentation review (step 230) is a dossier hold — shipment cannot leave until the dossier is complete. The client has notification and witness rights at all hold points.

**Q18. How are spools marked for traceability?**
A. Spool marking follows the matrix ENJOB25011423-MAT-SPL-001 at ITP step 210. Only vibro-peen or etching machines are permitted. Chloride-free markers are used for intermediate workflow marks. All marking is placed away from welds and HAZ.

**Q19. What does the "ACC / REJ" on a report mean?**
A. **ACC = Accepted (合格)**, **REJ = Rejected (不合格)**. These are the only result codes used on 423 reports and PDFs. Never use PASS / FAIL / OK / NG — the project standard is ACC / REJ throughout.

**Q20. Do we need hardness testing on 423?**
A. **No — hardness testing is not required on 423** (confirmed by Danny 2026-04-05). It is not an ITP step and is not required in the final dossier for this project. The mention in the legacy dossier list is dropped for 423. If a future duplex project is in sour service per NACE MR0175, hardness would be added with a ≤ 28 HRC / ≤ 320 HV10 limit, but that does not apply here.

**Q21. What happens if VT finds arc strikes on the base metal?**
A. Arc strikes are a reject condition on duplex. Light arc strikes are ground out with stainless-only discs, PT-tested to confirm removal, and the ground area is re-inspected dimensionally to confirm no wall thinning below the minimum. Severe arc strikes require engineering review.

**Q22. How are NCRs (non-conformance reports) handled during finishing?**
A. Every finishing station has a defined reaction:
- Ferrite out of range → isolate, escalate to welding engineer, possible re-weld.
- Metallographic sigma/chi → isolate, escalate.
- PT crack-like indication → grind, re-PT; if fail, re-weld.
- Ferroxyl blue spots → return to [4]/[5] for re-passivation, retest.
- Electrolytic machine failure → switch to spare unit, repair failed unit.
- Feritscope failure → switch to backup, recalibrate.
All NCRs are recorded with photo evidence and linked to the spool dossier.

**Q23. What is the minimum data recorded on the welding log?**
A. Weld No., Welder ID + stamp, date, pipe size and wall, WPS No., process per pass, filler metal spec + heat, shielding / purge gas, preheat temperature, interpass temperature (must be ≤ 150 °C), polarity, amps, volts, travel speed, pass sequence, ACC / REJ.

**Q24. Who signs the RT report?**
A. **Level II or Level III interpreter** signs as examiner. QC inspector reviews and signs. TPI witnesses as applicable. The operators who run the X-ray machine during night shift must hold RT Level II with a valid radiation license.

**Q25. What backing plate is used for 423 groove welds?**
A. **No consumable backing plate.** WPS-SPL-001 is "without backing" (open root with Argon purge). WPS-SPL-002 lists backing on "deposited metal / base metal" — which means the SAW fill passes deposit onto the already-welded GTAW root, not onto a separate backing strip. An Argon back purge supports the GTAW root in both cases.

---

## 10. Glossary (术语表)

| English | 中文 |
|---------|------|
| Acceptance criteria | 验收标准 |
| ACC (accepted) | 合格 |
| Argon back purge | 氩气背面保护 |
| Arc strike | 电弧擦伤 |
| Austenite | 奥氏体 |
| Base metal | 母材 |
| Bend test (guided) | 导向弯曲试验 |
| Bevel | 坡口 |
| Branch socket weld | 小口径支管承插焊缝 |
| Butt weld (BW) | 对接焊缝 |
| Calibration | 校准 |
| Certificate of Analysis (COA) | 分析证书 |
| Certified Reference Material (CRM) | 标准物质（标准块） |
| Chloride | 氯化物 |
| Clean zone / dirty zone | 清洁区 / 污染区 |
| Consumable | 焊材 |
| Cover pass / cap | 盖面焊 |
| Crack indication | 裂纹指示 |
| Deionised water (DI) | 去离子水 |
| Dimensional inspection | 尺寸检验 |
| Duplex stainless steel | 双相不锈钢 |
| EN 10204 3.1 certificate | EN 10204 3.1 证书 |
| ER2209 filler | ER2209 焊丝 |
| Ferrite content | 铁素体含量 |
| Ferrite measurement (Feritscope) | 铁素体测量仪 |
| Ferroxyl test (potassium ferricyanide) | 铁氰化钾测试 |
| Field weld | 现场焊缝 |
| Filler pass | 填充焊 |
| Fit-up | 组对 |
| Flux (SAW) | 焊剂 |
| Free iron contamination | 游离铁污染 |
| Grinding disc (stainless only) | 不锈钢专用砂轮片 |
| GTAW (TIG) | 钨极惰性气体保护焊（氩弧焊） |
| Hard stamping (forbidden) | 硬冲压（禁止） |
| Hazard / safety | 安全 |
| HAZ — Heat-Affected Zone | 热影响区 |
| Heat input | 热输入 |
| Heat number | 炉号 |
| Hi-lo (internal mismatch) | 错边量 |
| Hold point | 停检点 |
| Incoming inspection | 进货检验 |
| Indication (linear / rounded) | 缺陷指示（线性 / 圆形） |
| Inch-diameter | 英寸径 |
| Interpass temperature | 层间温度 |
| Intermetallic phase (sigma, chi) | 金属间相（σ、χ 相） |
| IQI (image quality indicator) | 像质计 |
| ITP — Inspection and Test Plan | 检验试验计划 |
| Level II NDT | 无损检测二级 |
| Linear meters (of weld) | 线性米数 |
| Low-stress stamping (vibro-peen) | 低应力打标（振动笔） |
| LP / PT — Liquid Penetrant Test | 液体渗透检测 |
| Marking matrix | 标记矩阵 |
| Metallographic replica (A923) | 金相复型 |
| MT — Magnetic Particle Test (not on 423) | 磁粉检测（423 项目不适用） |
| MTC — Material Test Certificate | 材质证书 |
| NCR — Non-Conformance Report | 不合格报告 |
| NDE / NDT | 无损检测 |
| Olet weld (sockolet / weldolet) | 支管座焊缝 |
| P-No. (ASME IX) | P 号 |
| Passivation | 钝化 |
| Penetrant dwell time | 渗透停留时间 |
| Pickling | 酸洗 |
| Pipe schedule / wall thickness | 管道壁厚 |
| PMI — Positive Material Identification | 材质鉴定 |
| PO — Purchase Order | 采购订单 |
| PQR — Procedure Qualification Record | 焊接工艺评定 |
| Preheat | 预热 |
| PREN (pitting resistance equivalent) | 点蚀当量 |
| Procedure | 工艺 |
| Purge gas | 保护气（背面） |
| PWHT — Post Weld Heat Treatment (none on 423) | 焊后热处理（423 无） |
| QC inspector | 质量控制检查员 |
| Radiographic Testing (RT) | 射线检测 |
| REJ (rejected) | 不合格 |
| Repair weld | 返修焊 |
| Review point (R) | 审查点 |
| Root face / land | 钝边 |
| Root gap / spacing | 根部间隙 |
| Root pass | 打底焊 |
| SAW — Submerged Arc Welding | 埋弧焊 |
| Sensitivity (RT) | 灵敏度 |
| Shielding gas | 保护气体 |
| Shop weld | 车间焊缝 |
| Sigma phase | σ 相 |
| Signature (examiner) | 签字（检查员） |
| Slip-on (SO) flange | 滑套法兰 |
| SMAW (stick welding) | 手工电弧焊 |
| Socket weld (SW) | 承插焊 |
| Sockolet | 承插式支管台 |
| Spool | 管段（管件） |
| Stainless steel (duplex 2205) | 双相不锈钢 2205 |
| Straight pipe | 直管 |
| Tack weld | 定位焊 |
| Tensile test | 拉伸试验 |
| TIG — Tungsten Inert Gas (= GTAW) | 钨极惰性气体保护焊 |
| TPI — Third Party Inspector | 第三方检验 |
| Traceability | 追溯性 |
| Travel speed | 焊接速度 |
| Tungsten electrode | 钨极 |
| UNS S32205 | UNS S32205（双相 2205） |
| Visual Testing (VT) | 目视检测 |
| Weave bead | 摆动焊道 |
| Weld cap | 盖面焊缝 |
| Weldolet | 对焊式支管台 |
| Weld map | 焊缝图 |
| Welder qualification (WPQ) | 焊工资格评定 |
| Welding log | 焊接记录 |
| WN flange — Weld Neck | 对焊法兰 |
| Witness point (W) | 见证点 |
| WPS — Welding Procedure Specification | 焊接工艺规程 |
| X-ray | X 射线 |
| XRF analyser (PMI instrument) | X 射线荧光分析仪 |

---

## Resolved Project Decisions (Danny, 2026-04-05)

1. **Ferrite acceptance band.** Project values are **weld 35–65 %, HAZ 30–70 %**. Supersedes the single 30–65 % band shown in ITP Rev 2. The ITP will be re-aligned at next revision.
2. **Metallographic (A923 Method A) coverage.** **Sampling — a few replicas per welder** (not 100 %). Intent is to screen each welder's technique for intermetallic phases. Exact count per welder is set by the QC manager in the work pack.
3. **Back-purge O₂ limit.** **< 0.1 %** (NORSOK M-601), adopted as the 423 project limit. Verified with an oxygen analyser at the vent before striking the arc.
4. **Hardness testing.** **Not required on 423.** Not an ITP step, not in the final dossier. Does not apply to this project (no sour service per NACE MR0175).

## Source Documents

- `ENJOB25011423-ITP-SPL-001 Rev 2 (2025-12-10)` — ITP Bilingual PDF (6 pages), at `.../423/Manufacturing/ITP/ITP ENJOB25011423 - Bilingual.pdf`
- `ENJOB25011423-WPS-SPL-001 GTAW.pdf` + supporting `ENJOB25011423-PQR-SPL-001 (2025-04-22)`, at `.../423/Manufacturing/WPS/Rev4/`
- `ENJOB25011423-WPS-SPL-002 GTAW+SAW.pdf` + supporting `ENJOB25011423-PQR-SPL-002 (2026-03-05)`, at `.../423/Manufacturing/WPS/Rev4/`
- `423_Flow_Plan_EN_CN.md / .pdf` Rev B (2026-04-05), and all Station_01…Station_12 files, at `.../423/Manufacturing/Flow after welding/`
- Agent memory: `project_423_finishing_procedures`, `reference_qc_report_fields`, `reference_shop_welds_methodology`, `reference_duplex_pipe_fittings`, `reference_tracker_architecture`

## Items Still Open

1. Confirmation of current `project_steps` row numbers in the tracker against `deploy_project.py` — step numbering is project-specific and editable (the chat agent reads this live from the DB, so it is self-resolving at query time).
2. Exact hi-lo (internal mismatch) tolerance on the approved 423 drawings — working value used here is B31.3 §328.4.3 default; confirm against drawing note at next QC review.

(Items 1–3 from the previous list were resolved by Danny on 2026-04-05 — see "Resolved Project Decisions" above.)
