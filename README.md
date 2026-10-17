# TwinPulse: the twin lives the night first

**A physiology-based digital twin that rehearses tonight to prevent night-time hypoglycaemia in Indian children with type 1 diabetes.**

Submission for the Happiest Health Digital Twin Challenge 2026.

| | |
|---|---|
| Team | **TwinPulse** |
| Team members | _TODO: names, roles, year/course_ |
| College / incubator | _TODO_ |
| Demo video (20+ min) | _TODO: unlisted YouTube link_ |
| Architecture diagram | _TODO: docs/TwinPulse_Architecture.pdf_ |
| Presentation | _TODO: docs/TwinPulse_Presentation.pdf_ |
| License | Apache-2.0 (see [LICENSE](LICENSE)) |

---

## 1. Problem and healthcare use case

- India has more children with type 1 diabetes (T1D) than any other country: 2.29 lakh under 20 (IDF Diabetes Atlas 2021). The 2025 Atlas counts 9.4 lakh Indians with T1D.
- Insulin keeps these children alive, and its most feared side effect is low blood sugar (hypoglycaemia). In the DCCT trial, 55% of severe lows happened during sleep. "Dead-in-bed" syndrome, thought to follow severe night lows, is linked to about 5–6% of deaths in people with T1D under 40.
- A CGM with alarms costs about ₹4,000–4,700 per 14-day sensor in India (about ₹1.1–1.2 lakh a year). Most families can't afford one, so parents set 2–3 AM alarms to prick their child's finger.

**TwinPulse gives the paediatric diabetes clinic three tools:**

1. **Tonight Board.** At 9 PM, every child's twin "lives tonight" 500 times. Children are ranked by their risk of a night-time low, so the diabetes educator knows whom to call before bed.
2. **Therapy rehearsal.** The doctor tries changes on the twin and sees how the night's risk moves *before* prescribing. Examples: a 15 g bedtime snack, a smaller dinner dose, or moving NPH insulin from dinner to bedtime. Approved plans go to the family in their language (WhatsApp, or a voice call for feature phones).
3. **Night guard (CGM users).** A real-time model warns 1–2 hours before a low and calls the parent.

## 2. How it works

```
 Health record (FHIR R4)  ─┐
 CGM or finger-pricks      ├─►  Physiology twin  ──►  500 simulated nights ──► risk, timing, depth
 Insulin + meals           │    (personal model,      + what-if rehearsal
 Steps + heart rate (band) ─┘     fitted nightly)
                                         │
 CGM stream ──────────────────────►  Night guard (LightGBM) ──► alert 1–2 h ahead ──► parent call
```

- **Physiology twin** ([twinpulse/twin.py](twinpulse/twin.py)): a Bergman-type glucose–insulin model that includes:
  - subcutaneous rapid insulin and long-acting insulin (NPH or glargine)
  - gut carbohydrate absorption
  - an exercise effect that lingers for about 4 hours (evening play causes delayed night lows)

  It is personalised to each child by least-squares fitting on that child's previous nights, anchored to the clinical 1800 rule. It assimilates the day's glucose readings (CGM or finger-pricks), then runs freely from 23:00 as a 500-member ensemble.
- **Unlogged meals** are inferred from mealtime insulin using the clinical 500 rule.
- **Explanations** come from counterfactuals: the twin removes one factor at a time (evening play, dinner insulin, NPH) and reports how much the risk falls.
- **Night guard** ([scripts/train.py](scripts/train.py)): LightGBM models trained on real CGM + smartwatch data that predict a low within 60/120 minutes, plus glucose forecasts at +30/60/120 minutes.

## 3. Data (sandbox rules: open and synthetic only)

| Data | Use | Licence |
|---|---|---|
| [HUPA-UCM](https://data.mendeley.com/datasets/3hbcscwz44/1): 25 adults with T1D, Spain. FreeStyle Libre 2 CGM + Fitbit (heart rate, steps) + insulin + carbs | Training and patient-held-out validation | CC BY 4.0 |
| [T1D-UOM](https://doi.org/10.5281/zenodo.15806142): T1D adults, UK, 3 months each. CGM + insulin (pump and injections) + food + Garmin activity/heart rate + sleep | External validation | CC BY 4.0 |
| Synthetic Indian children ([twinpulse/synth.py](twinpulse/synth.py)): 12 children, 14 days each. Indian routine, NPH/Regular, premixed or glargine regimens; FHIR R4 records with HbA1c, haemoglobin, HLA genotype, autoantibodies, consent | Dashboard demo only, never used for scoring | Generated |

## 4. Results (real patients only)

Patients were split into 5 groups so every score is on people the model never saw. T1D-UOM is an external test.

| Night guard (CGM) | Unseen patients AUROC | External AUROC |
|---|---|---|
| Low within 60 min, 22:00–06:00 | **0.93** | 0.90 |
| Low within 2 h, 22:00–06:00 | **0.88** | 0.78 |

| Glucose forecast RMSE (mg/dL) | Assume no change | Extend trend | TwinPulse | Clarke A+B |
|---|---|---|---|---|
| 30 min | 21.2 | 23.5 | **18.1** | 97.6% |
| 60 min | 34.8 | 44.9 | **30.4** | 94.4% |
| 120 min | 51.7 | 78.8 | **44.4** | 91.1% |

**What did not work, reported honestly:**

- **Bedtime-only prediction is close to chance.** Predicting a low between 00:00 and 06:00 from information at 23:00 scored about 0.55–0.63 AUROC across all methods (rule, ML, physiology twin) on 1,046 real nights. So TwinPulse uses the bedtime rehearsal to *compare plans*, not to promise a night is safe.
- **Extra signals add little.** Insulin, meal, step and heart-rate features add about 0.01 AUROC over glucose alone in these datasets.
- **What does work without nightly CGM:** a child's first week of sensor data ranks which patients will have the most night lows later (Spearman 0.63, 29 real patients). A ₹4–5k trial sensor can therefore direct scarce state-programme CGMs to the children at highest risk.

## 5. Tech stack

Python 3.12 · pandas · NumPy · SciPy · numba · LightGBM · scikit-learn · FastAPI · React 18 + Vite + Recharts · FHIR R4 JSON

## 6. Run it

```bash
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/download_data.py          # real open datasets (needed only to retrain)
.venv/bin/python -m twinpulse.data                 # unified 5-minute tables
.venv/bin/python -c "import sys; sys.path.insert(0,'.'); from twinpulse.data import load_all; from twinpulse.features import nightly_table, realtime_table; d=load_all(); nightly_table(d).to_parquet('data/processed/nights.parquet'); realtime_table(d).to_parquet('data/processed/realtime.parquet')"
.venv/bin/python scripts/train.py                  # metrics -> reports/metrics.json, models -> models/
.venv/bin/python scripts/eval_twin.py              # physiology twin walk-forward test
.venv/bin/python -m twinpulse.synth                # synthetic Indian demo cohort
.venv/bin/uvicorn api.main:app --port 8000         # API
cd dashboard && npm install && npm run dev         # dashboard on http://localhost:5173
```

The trained models and the synthetic demo cohort are committed, so the API and dashboard run without downloading anything.

## 7. Privacy, safety and India fit

- **DPDP Act 2023, children's data.**
  - Section 9 requires verifiable parental consent and bans tracking or behavioural monitoring of children.
  - The DPDP Rules 2025 (Fourth Schedule) exempt clinical establishments and healthcare professionals when processing is limited to providing health services to the child.
  - TwinPulse is therefore deployed by the clinic, which is the data fiduciary. Parental consent is still recorded, and there is no advertising or analytics.
- **The doctor stays in charge.** The twin only shows simulated outcomes; families receive only doctor-approved actions.
- **ABDM-ready.** Health records are FHIR R4, with a placeholder for ABHA linkage.
- **Built for Indian care.** It models the human NPH/Regular insulin that many state programmes supply.

## 8. Limitations and next steps

- Models were trained and validated on adults in Spain and the UK, not Indian children. Next step: a pilot with an Indian paediatric diabetes clinic.
- Demo children are synthetic. Translations are drafts for native-speaker review.
- Not a medical device. A real deployment would follow CDSCO's medical device software pathway.

## 9. References

- IDF Diabetes Atlas, 10th ed. (2021) and 11th ed. (2025).
- Hidalgo et al., HUPA-UCM diabetes dataset, *Data in Brief* 55 (2024) 110559.
- Alsuhaymi et al., A Longitudinal Multimodal Dataset of Type 1 Diabetes, *Scientific Data* 12, 1379 (2025).
- Battelino et al., International Consensus on Time in Range, *Diabetes Care* 2019.
- Cappon et al., ReplayBG: a digital twin-based methodology for T1D, *IEEE TBME* 2023 (the methodological inspiration for the twin).
- Bergman et al., minimal model of glucose kinetics, 1979.
