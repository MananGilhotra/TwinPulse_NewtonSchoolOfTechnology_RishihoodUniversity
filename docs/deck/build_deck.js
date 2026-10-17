// Builds docs/TwinPulse_Presentation.pptx from the project's real metrics and figures.
// Usage: cd docs/deck && npm install && TEAM="Name A, Name B" COLLEGE="Your College" node build_deck.js
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");

const ROOT = path.resolve(__dirname, "..", "..");
const FIG = (f) => path.join(ROOT, "docs", "figures", f);
const SHOT = (f) => path.join(ROOT, "docs", "screenshots", f);
const M = JSON.parse(fs.readFileSync(path.join(ROOT, "reports", "metrics.json")));
const X = JSON.parse(fs.readFileSync(path.join(ROOT, "reports", "metrics_extra.json")));
const TEAM = process.env.TEAM || "Team TwinPulse";
const PROJECT = "NightTwin";
const MEMBERS = process.env.MEMBERS || "Manan Gilhotra (team leader) · Manas Saxena";
const COLLEGE = process.env.COLLEGE || "Newton School of Technology, Rishihood University";
const OUT = path.join(ROOT, "docs", "TwinPulse_Presentation.pptx");

const THEME = {
  name: "TwinPulse Night",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "0F172A", lt1: "FFFFFF", dk2: "334155", lt2: "F1F5F9",
    accent1: "4F46E5", accent2: "F59E0B", accent3: "059669", accent4: "DC2626", accent5: "A5B4FC", accent6: "0891B2",
    hlink: "4F46E5", folHlink: "6D28D9",
  },
};
const HEX = THEME.colors;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
pres.title = "NightTwin by Team TwinPulse: the twin lives the night first";
pres.author = "Team TwinPulse";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;
const W = 13.333;

// ---------- layouts ----------
pres.defineSlideMaster({
  title: "TITLE_DARK",
  background: { color: HEX.dk1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.7, y: 2.2, w: 8.6, h: 1.9, fontSize: 46, bold: true, color: C.background1, valign: "top", align: "left", fontFace: THEME.headFontFace }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.7, y: 4.25, w: 8.4, h: 1.2, fontSize: 18, color: C.accent5, valign: "top", align: "left" }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: HEX.lt1 },
  margin: [0.5, 0.6, 0.6, 0.6],
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.35, w: 12.1, h: 0.85, fontSize: 32, bold: true, color: C.text1, valign: "middle", align: "left", fontFace: THEME.headFontFace }, text: "" } },
    { text: { text: "NightTwin by Team TwinPulse · Newton School of Technology, Rishihood University", options: { x: 0.6, y: 7.05, w: 8, h: 0.3, fontSize: 10, color: C.text2 } } },
  ],
  slideNumber: { x: 12.2, y: 7.05, w: 0.6, h: 0.3, fontSize: 10, color: C.text2, align: "right" },
});
pres.defineSlideMaster({
  title: "CONTENT_DARK",
  background: { color: HEX.dk1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.35, w: 12.1, h: 0.85, fontSize: 32, bold: true, color: C.background1, valign: "middle", align: "left", fontFace: THEME.headFontFace }, text: "" } },
    { text: { text: "NightTwin by Team TwinPulse · Newton School of Technology, Rishihood University", options: { x: 0.6, y: 7.05, w: 8, h: 0.3, fontSize: 10, color: C.accent5 } } },
  ],
  slideNumber: { x: 12.2, y: 7.05, w: 0.6, h: 0.3, fontSize: 10, color: C.accent5, align: "right" },
});

// ---------- helpers ----------
let n = 0;
const id = (s) => `${s}-${++n}`;
function txt(slide, text, o) {
  slide.addText(text, { isTextBox: true, objectName: id("text"), fontSize: 16, color: C.text1, valign: "top", margin: 0, ...o });
}
function card(slide, x, y, w, h, fill = C.background2) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.12, fill: { color: fill }, line: { color: fill }, objectName: id("card") });
}
function badge(slide, x, y, label, fill = C.accent1, size = 0.5) {
  slide.addShape(pres.shapes.OVAL, { x, y, w: size, h: size, fill: { color: fill }, line: { color: fill }, objectName: id("badge") });
  slide.addText(label, { x, y, w: size, h: size, isTextBox: true, align: "center", valign: "middle", fontSize: 16, bold: true, color: C.background1, margin: 0, objectName: id("badge-label") });
}
function stat(slide, x, y, w, big, label, color = C.accent1, dark = false, size = 48) {
  txt(slide, big, { x, y, w, h: 0.95, fontSize: size, bold: true, color, fontFace: THEME.headFontFace, fit: "none" });
  txt(slide, label, { x, y: y + 0.95, w, h: 0.75, fontSize: 14, color: dark ? C.accent5 : C.text2 });
}
function img(slide, file, x, y, w, ratio, alt) {
  slide.addImage({ path: file, x, y, w, h: w / ratio, altText: alt, objectName: id("image") });
}
function bullets(slide, items, o) {
  slide.addText(items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1, paraSpaceAfter: 6 } })),
    { isTextBox: true, objectName: id("list"), fontSize: 16, color: C.text1, valign: "top", margin: 0, ...o });
}
const pct = (v) => `${Math.round(v * 100)}%`;
const chartBase = {
  catAxisLabelColor: "475569", valAxisLabelColor: "475569", catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt",
  dataLabelFontFace: "+mn-lt", titleFontFace: "+mn-lt", catAxisLabelFontSize: 12, valAxisLabelFontSize: 11, dataLabelFontSize: 12,
  valGridLine: { color: "E2E8F0", size: 0.75 }, catGridLine: { style: "none" }, showValue: true, dataLabelColor: "0F172A",
};
const ue = X.guard_events.unseen_patients["0.2"];
const ex = X.guard_events.external["0.2"];
const sr = X.sensor_ranking;
const ana = { base: 0.58, plan: 0.14 };

// ---------- 1. title ----------
pres.addSection({ title: "Opening" });
let s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: "Opening" });
txt(s, "TEAM TWINPULSE · HAPPIEST HEALTH DIGITAL TWIN CHALLENGE 2026", { x: 0.7, y: 1.55, w: 9, h: 0.4, fontSize: 14, bold: true, color: C.accent2, charSpacing: 3 });
s.addText("NightTwin: the twin lives the night first", { placeholder: "title" });
s.addText("A physiology-based digital twin that rehearses tonight to prevent night-time hypoglycaemia in Indian children with type 1 diabetes", { placeholder: "body" });
txt(s, [TEAM, COLLEGE].filter(Boolean).join(" · "), { x: 0.7, y: 5.95, w: 9, h: 0.4, fontSize: 16, color: C.background1 });
txt(s, MEMBERS, { x: 0.7, y: 6.4, w: 9, h: 0.4, fontSize: 14, color: C.accent5 });
s.addShape(pres.shapes.OVAL, { x: 9.9, y: 1.7, w: 2.6, h: 2.6, fill: { color: C.accent2 }, line: { color: C.accent2 }, objectName: "moon" });
s.addShape(pres.shapes.OVAL, { x: 10.6, y: 1.45, w: 2.4, h: 2.4, fill: { color: C.text1 }, line: { color: C.text1 }, objectName: "moon-shadow" });
txt(s, "21:00 → 07:00\n500 nights rehearsed\nbefore one is lived", { x: 9.6, y: 4.7, w: 3.2, h: 1.3, fontSize: 16, color: C.accent5, align: "right" });
s.addNotes("Hello, we are Team TwinPulse from Newton School of Technology, Rishihood University. Our project, NightTwin, is a digital twin that lives the night first: before a child with type 1 diabetes goes to sleep, her twin rehearses tonight 500 times, so the doctor can see the danger and fix it before it happens.");

// ---------- 2. story ----------
s = pres.addSlide({ masterName: "CONTENT_DARK", sectionTitle: "Opening" });
s.addText("2:47 AM in Raichur", { placeholder: "title" });
card(s, 0.6, 1.5, 7.4, 4.9, "1E293B");
txt(s, "“Every night for three years I set an alarm to prick her finger. I never know which night is the dangerous one.”",
  { x: 1.0, y: 1.9, w: 6.6, h: 2.6, fontSize: 26, italic: true, color: C.background1, fontFace: THEME.headFontFace });
txt(s, "Composite story, for illustration", { x: 1.0, y: 5.7, w: 6, h: 0.4, fontSize: 12, color: C.accent5 });
stat(s, 8.6, 1.5, 4.2, "55%", "of severe lows in type 1 diabetes happen during sleep (DCCT)", C.accent2, true);
stat(s, 8.6, 3.35, 4.2, "5–6%", "of deaths in people with T1D under 40 are linked to “dead-in-bed” syndrome", C.accent2, true);
stat(s, 8.6, 5.2, 4.2, "~1 hour", "of warning is enough to treat a low with a glass of juice", C.accent2, true);
s.addNotes("Picture Lakshmi in Raichur. Her daughter Ananya has type 1 diabetes. Every night she sets an alarm to check her. In the landmark DCCT trial, 55 percent of severe lows happened during sleep, and dead-in-bed syndrome is linked to 5 to 6 percent of deaths in people with type 1 diabetes under 40. A low caught an hour early is treated with a glass of juice. A low caught late can mean a seizure.");

// ---------- 3. India problem ----------
pres.addSection({ title: "Problem" });
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Problem" });
s.addText("India has the most children with type 1 diabetes, and the least protection at night", { placeholder: "title", fontSize: 28 });
[["2.29 lakh", "Indian children and teens with T1D: the most of any country (IDF Atlas 2021)", C.accent1],
 ["9.4 lakh", "Indians of all ages with T1D (IDF Atlas 2025)", C.accent1],
 ["₹1.1 lakh+", "a year for a CGM with low alarms (₹4–4.7k per 14-day sensor)", C.accent4],
 ["NPH", "Cheaper human insulin many programmes supply peaks between 1 and 4 AM, when everyone is asleep", C.accent2]].forEach(([b, l, c], i) => {
  const x = 0.6 + i * 3.08;
  card(s, x, 1.65, 2.85, 3.1);
  stat(s, x + 0.25, 1.9, 2.45, b, l, c, false, 32);
});
txt(s, "Families choose between ₹1 lakh a year and a 2 AM finger-prick alarm. Fear of lows pushes sugars high, which harms eyes and kidneys later. Clinics have no way to tell which nights are dangerous.",
  { x: 0.6, y: 5.15, w: 12.1, h: 1.2, fontSize: 18, color: C.text2 });
s.addNotes("India has 2.29 lakh children and teens with type 1 diabetes, the most of any country. A CGM with alarms costs over a lakh a year, so most families use finger-pricks. Many state programmes give human NPH insulin, which peaks between 1 and 4 AM, exactly when the family is asleep.");

// ---------- 4. solution ----------
pres.addSection({ title: "Solution" });
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Solution" });
s.addText("NightTwin: learn the child, live tonight first, guard the real night", { placeholder: "title", fontSize: 28 });
[["1", "Learn the child", "A personal glucose–insulin model is fitted to each child's own nights: insulin, meals, play, CGM or finger-pricks, plus the FHIR health record."],
 ["2", "Live tonight first", "At 9 PM the twin simulates tonight 500 times. The doctor sees who is at risk, when and why, and rehearses a fix on the twin before prescribing it."],
 ["3", "Guard the real night", "For CGM users, a model trained on real patients warns about an hour before a low and calls the parent in their own language."]].forEach(([k, t, b], i) => {
  const x = 0.6 + i * 4.1;
  card(s, x, 1.7, 3.8, 4.4);
  badge(s, x + 0.3, 2.0, k, C.accent1, 0.6);
  txt(s, t, { x: x + 0.3, y: 2.85, w: 3.2, h: 0.5, fontSize: 22, bold: true, fontFace: THEME.headFontFace });
  txt(s, b, { x: x + 0.3, y: 3.5, w: 3.2, h: 2.4, fontSize: 16, color: C.text2 });
});
txt(s, "Decision support for clinicians. The doctor approves every change; families receive only approved actions.", { x: 0.6, y: 6.35, w: 12, h: 0.4, fontSize: 14, italic: true, color: C.text2 });
s.addNotes("NightTwin does three things. It learns each child as a personal physiology model. At 9 PM it lives tonight 500 times, so the doctor sees the risk and rehearses fixes. And for children with a CGM, it guards the real night, warning about an hour before a low.");

// ---------- 5. data fusion ----------
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Solution" });
s.addText("Fusing the health record with wearable streams", { placeholder: "title" });
const fuse = [["Static: health record (FHIR R4)", ["Age, weight, HbA1c, haemoglobin", "Insulin regimen and daily dose", "Past severe lows, hypo awareness", "HLA genotype, islet autoantibodies"], C.accent6],
  ["Dynamic: wearables", ["CGM every 5 min, or finger-pricks", "Insulin doses and meals", "Steps and heart rate from a band", "Sleep window"], C.accent1],
  ["Twin output", ["Tonight's risk, time and depth of a low", "Factor-by-factor explanation", "Rehearsed plan, doctor-approved", "Real-time alert to the parent"], C.accent3]];
fuse.forEach(([t, items, c], i) => {
  const x = 0.6 + i * 4.25;
  card(s, x, 1.6, 3.75, 3.2);
  txt(s, t, { x: x + 0.25, y: 1.8, w: 3.3, h: 0.5, fontSize: 18, bold: true, color: c });
  bullets(s, items, { x: x + 0.25, y: 2.4, w: 3.3, h: 2.3, fontSize: 15 });
  if (i < 2) txt(s, i === 0 ? "+" : "→", { x: x + 3.78, y: 2.85, w: 0.45, h: 0.6, fontSize: 30, bold: true, color: C.accent1, align: "center" });
});
s.addTable([
  [{ text: "Dataset", options: { bold: true, color: HEX.lt1, fill: { color: HEX.dk1 } } }, { text: "What it contains", options: { bold: true, color: HEX.lt1, fill: { color: HEX.dk1 } } }, { text: "Role", options: { bold: true, color: HEX.lt1, fill: { color: HEX.dk1 } } }],
  ["HUPA-UCM (Spain, CC BY 4.0)", "25 people with T1D: Libre 2 CGM, Fitbit heart rate and steps, insulin, carbs", "Training + patient-held-out validation"],
  ["T1D-UOM (UK, CC BY 4.0)", "T1D, 3 months each: CGM, pump and injected insulin, food, Garmin activity, sleep", "External test"],
  ["Synthetic Indian cohort", "12 children, 14 days, Indian routines, NPH/premixed/glargine, FHIR records", "Dashboard demo only"],
], { x: 0.6, y: 5.0, w: 12.1, colW: [3.2, 6.4, 2.5], fontSize: 12, color: HEX.dk2, border: { type: "solid", color: "E2E8F0", pt: 0.75 }, rowH: 0.36, objectName: "data-table" });
s.addNotes("The twin fuses two streams, as the challenge asks. The static health record, in FHIR R4 format, gives regimen, HbA1c, haemoglobin, hypo history and genetic markers. The dynamic stream gives glucose, insulin, meals, steps and heart rate. We train and validate only on open real-patient data, and use synthetic Indian children only for the demo.");

// ---------- 6. architecture ----------
pres.addSection({ title: "How it works" });
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "How it works" });
s.addText("Architecture", { placeholder: "title" });
img(s, FIG("architecture.png"), 1.6, 1.2, 10.1, 2475 / 1395, "NightTwin architecture: data, preparation, models, API, users, trust layer");
s.addNotes("Data flows from the health record and wearables into a unified 5-minute timeline. Three models sit on top: the physiology twin, the LightGBM night guard, and sensor priority. A FastAPI service serves the doctor dashboard and the family channel, and a trust layer covers consent, privacy and doctor-in-the-loop.");

// ---------- 7. physiology twin ----------
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "How it works" });
s.addText("The physiology twin: a personal model of each child", { placeholder: "title" });
img(s, FIG("tonight_rehearsal.png"), 0.6, 1.4, 7.9, 1574 / 646, "Ananya's night simulated 500 times; risk falls from 58% to 14% with a plan");
bullets(s, [
  "Bergman glucose–insulin model with rapid and long-acting (NPH or glargine) insulin depots, gut absorption and a 4-hour exercise effect",
  "Fitted on the child's own past nights; insulin sensitivity anchored to the clinical 1800 rule",
  "Unlogged meals inferred from mealtime insulin (500 rule)",
  "Assimilates today's readings, then runs 23:00–07:30 as a 500-member ensemble",
], { x: 8.8, y: 1.45, w: 3.95, h: 4.6, fontSize: 15 });
txt(s, "Synthetic patient · the method, not an accuracy claim", { x: 0.6, y: 4.85, w: 7.9, h: 0.35, fontSize: 12, italic: true, color: C.text2 });
s.addNotes("The twin is a real physiological model, the Bergman minimal model with insulin depots for both rapid and NPH insulin, carbohydrate absorption and a lingering exercise effect. It is fitted to each child's own past nights. At bedtime it runs 500 times with realistic variation, giving the probability, timing and depth of a low.");

// ---------- 8. rehearse ----------
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "How it works" });
s.addText("Rehearse the fix on the twin before prescribing it", { placeholder: "title" });
img(s, SHOT("patient_ananya_crop.png"), 0.6, 1.35, 7.6, 2160 / 1500, "Ananya's twin page in the dashboard");
stat(s, 8.6, 1.4, 4.2, `${pct(ana.base)} → ${pct(ana.plan)}`, "Ananya's simulated risk of a night low, before and after: 15 g bedtime snack + NPH moved 90 min later", C.accent3);
bullets(s, ["Bedtime snack (15 or 30 g)", "Smaller dinner insulin dose after a sports day", "Move NPH from dinner to bedtime", "Explanations: the twin removes one factor at a time and re-lives the night"], { x: 8.6, y: 3.55, w: 4.2, h: 2.6, fontSize: 15 });
s.addNotes("This is the heart of the twin. The doctor tries a plan, for example a bedtime snack and moving NPH 90 minutes later, and the twin re-lives the night. For Ananya, the share of rehearsed nights with a low drops from 58 to 14 percent. Only after seeing this does the doctor approve the plan.");

// ---------- 9. night guard ----------
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "How it works" });
s.addText("Night guard: wake the parent before the low, not after", { placeholder: "title" });
img(s, FIG("guard_replay.png"), 0.6, 1.4, 8.1, 1574 / 614, "Arjun's night replay: alert before the low");
stat(s, 9.1, 1.4, 3.7, pct(ue.caught_15min_ahead), `of ${ue.night_lows} real night-time lows warned at least 15 min ahead (unseen patients)`, C.accent3);
stat(s, 9.1, 3.3, 3.7, `${Math.round(ue.median_warning_min)} min`, "median warning", C.accent1);
stat(s, 9.1, 5.0, 3.7, ue.false_alarms_per_night.toFixed(2), "false alarms per night", C.accent2);
txt(s, "LightGBM on glucose history, insulin and carbs on board, steps and heart rate; 15-minute smoothing. Alert goes as a voice call in the family's language.",
  { x: 0.6, y: 4.75, w: 8.1, h: 1.0, fontSize: 15, color: C.text2 });
s.addNotes(`For families with a CGM, the night guard runs every five minutes. On real patients it never saw, it warned about ${pct(ue.caught_15min_ahead)} of night-time lows at least 15 minutes ahead, with a median warning of ${Math.round(ue.median_warning_min)} minutes and about one false alarm every two nights.`);

// ---------- 10. results ----------
pres.addSection({ title: "Evidence" });
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Evidence" });
s.addText("Results on real patients the model never saw", { placeholder: "title" });
s.addChart(pres.charts.BAR, [
  { name: "Unseen patients (Spain)", labels: ["Lows warned ≥15 min ahead (%)", "Median warning (min)"], values: [Math.round(ue.caught_15min_ahead * 100), Math.round(ue.median_warning_min)] },
  { name: "External test (UK)", labels: ["Lows warned ≥15 min ahead (%)", "Median warning (min)"], values: [Math.round(ex.caught_15min_ahead * 100), Math.round(ex.median_warning_min)] },
], { ...chartBase, x: 0.6, y: 1.4, w: 6.0, h: 4.6, barDir: "col", chartColors: [HEX.accent1, HEX.accent5], showLegend: true, legendPos: "b", legendFontFace: "+mn-lt", legendFontSize: 12,
  showTitle: true, title: "Night guard", titleFontSize: 16, titleColor: "0F172A", dataLabelPosition: "outEnd", valAxisHidden: true, objectName: "chart-guard" });
const fc = M.realtime.forecast;
s.addChart(pres.charts.BAR, [
  { name: "Assume no change", labels: ["30 min", "60 min", "2 h"], values: ["30min", "60min", "120min"].map((h) => +fc[h].persistence.rmse.toFixed(1)) },
  { name: "NightTwin", labels: ["30 min", "60 min", "2 h"], values: ["30min", "60min", "120min"].map((h) => +fc[h].full_twin.rmse.toFixed(1)) },
], { ...chartBase, x: 6.9, y: 1.4, w: 5.85, h: 4.6, barDir: "col", chartColors: ["CBD5E1", HEX.accent1], showLegend: true, legendPos: "b", legendFontFace: "+mn-lt", legendFontSize: 12,
  showTitle: true, title: "Glucose forecast error, RMSE mg/dL (lower is better)", titleFontSize: 16, titleColor: "0F172A", dataLabelPosition: "outEnd", valAxisHidden: true, objectName: "chart-forecast" });
txt(s, `Night-guard AUROC: ${M.realtime.low_next60.night_22_06_full_twin.auroc.toFixed(2)} for a low within 60 min, ${M.realtime.low_next120.night_22_06_full_twin.auroc.toFixed(2)} within 2 h. Clarke error grid A+B at 30 min: ${((fc["30min"].full_twin.clarke.A + fc["30min"].full_twin.clarke.B) * 100).toFixed(1)}%. Patients split into 5 groups, so every score is on people the model never saw.`,
  { x: 0.6, y: 6.15, w: 12.1, h: 0.7, fontSize: 14, color: C.text2 });
s.addNotes("All numbers here are on real people with type 1 diabetes the model never saw, and confirmed on a separate UK dataset with different devices. The guard performs well. Our glucose forecasts beat the standard baseline at every horizon.");

// ---------- 11. honest ----------
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Evidence" });
s.addText("What did not work, and what we did about it", { placeholder: "title" });
const n_ = M.night;
s.addChart(pres.charts.BAR, [{
  name: "AUROC", labels: ["Night guard: low within 60 min", "Night guard: low within 2 h", "Bedtime: glucose rule", "Bedtime: ML, all signals", "Bedtime: physiology twin", "Bedtime: finger-prick + band"],
  values: [M.realtime.low_next60.night_22_06_full_twin.auroc, M.realtime.low_next120.night_22_06_full_twin.auroc, n_.cv.rule_bedtime_bg.auroc, n_.cv.full_twin.auroc, X.twin_bedtime["HUPA-UCM"].twin_auroc, n_.cv.fingerstick_band.auroc].map((v) => +v.toFixed(2)),
}], { ...chartBase, x: 0.6, y: 1.4, w: 7.2, h: 5.1, barDir: "bar", chartColors: [HEX.accent3, HEX.accent3, HEX.accent2, HEX.accent2, HEX.accent2, HEX.accent2], dataLabelFormatCode: "0.00", valAxisLabelFormatCode: "0.00", valAxisMinVal: 0.5, valAxisMaxVal: 1.0, dataLabelPosition: "outEnd",
  showLegend: false, showTitle: true, title: "AUROC on unseen patients (0.5 = coin toss)", titleFontSize: 14, titleColor: "0F172A", catAxisOrientation: "maxMin", objectName: "chart-honest" });
bullets(s, [
  `Predicting the whole night from bedtime alone was close to chance (0.55–0.63) on ${n_.n_nights} real nights, whatever the method`,
  "So the bedtime rehearsal is used to compare plans, not to promise a night is safe",
  "Warnings rely on the in-night guard",
  "Insulin, meal, step and heart-rate features add only ~0.01 AUROC over glucose alone in these datasets",
], { x: 8.2, y: 1.5, w: 4.55, h: 5.0, fontSize: 15 });
s.addNotes("We want to be honest. We first hoped to tell a mother at bedtime whether tonight is safe. On over a thousand real nights, bedtime-only prediction was close to chance for every method, including our physiology twin. So we changed the design: rehearsal compares plans, and warnings come from the in-night guard, which works.");

// ---------- 12. sensor priority ----------
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Evidence" });
s.addText("No CGM for everyone? Give it to the children who need it most", { placeholder: "title", fontSize: 28 });
s.addChart(pres.charts.SCATTER, [
  { name: "Week 1 time below 70 (%)", values: sr.table.map((r) => +(r.week1_tbr * 100).toFixed(2)) },
  { name: "Later nights with a low (%)", values: sr.table.map((r) => +(r.later_night_low_rate * 100).toFixed(1)) },
], { ...chartBase, x: 0.6, y: 1.4, w: 6.6, h: 5.0, chartColors: [HEX.accent1], lineSize: 0, lineDataSymbol: "circle", lineDataSymbolSize: 9, showValue: false, showLegend: false,
  showTitle: true, title: `Week-1 trial sensor vs later night lows (${sr.patients} real patients)`, titleFontSize: 14, titleColor: "0F172A",
  showValAxisTitle: true, valAxisTitle: "Later: % of nights with a low", valAxisTitleFontSize: 12, valAxisTitleColor: "475569",
  showCatAxisTitle: true, catAxisTitle: "Week 1: % time below 70 mg/dL", catAxisTitleFontSize: 12, catAxisTitleColor: "475569", objectName: "chart-sensor" });
stat(s, 7.7, 1.5, 2.4, pct(sr.top_third_later_rate), "of later nights had a low: top third by week-1 risk", C.accent4);
stat(s, 10.3, 1.5, 2.4, pct(sr.bottom_third_later_rate), "bottom third", C.accent3);
txt(s, `Spearman ${sr.spearman_week1_tbr_vs_later.toFixed(2)}. One ₹4–5k trial sensor per child, instead of ₹1.1 lakh a year for everyone, points a state programme's scarce CGMs at the children most at risk. The Sensor Priority screen does exactly this.`,
  { x: 7.7, y: 3.6, w: 5.0, h: 2.6, fontSize: 16, color: C.text2 });
s.addNotes("Without nightly CGM we cannot guard every night. So NightTwin helps share scarce sensors fairly. On real patients, one week of sensor data ranked who would have the most night lows later: 42 percent of later nights for the top third, versus 10 percent for the bottom third.");

// ---------- 13. dashboard ----------
pres.addSection({ title: "Product" });
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Product" });
s.addText("The doctor's dashboard", { placeholder: "title" });
img(s, SHOT("board_crop.png"), 0.6, 1.35, 7.0, 2160 / 1350, "Tonight Board ranking children by risk");
bullets(s, ["Tonight Board at 9 PM: every child ranked by risk; call the red rows", "Twin view: rehearsed night, why it is risky, FHIR record, 14-day time in range", "Rehearse, approve, send to family", "Night guard replay", "Sensor Priority and Evidence pages"],
  { x: 7.9, y: 1.45, w: 4.85, h: 4.8, fontSize: 16 });
s.addNotes("The dashboard is built for a busy paediatric diabetes clinic. At 9 PM the Tonight Board ranks every child. One click opens the child's twin, with the rehearsed night, the reasons, the health record and the 14-day summary.");

// ---------- 14. family + India ----------
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Product" });
s.addText("Built for Indian families and clinics", { placeholder: "title" });
img(s, SHOT("patient_arjun_crop.png"), 0.6, 1.35, 7.2, 1350 / 960, "Night guard replay with a Malayalam voice alert");
[["Language", "Alerts in Kannada, Hindi, Malayalam… by voice call that works on feature phones"],
 ["Insulin reality", "Models human NPH/Regular and premixed insulin, not only analogues"],
 ["Routines", "Late dinners, evening cricket, school tiffin"],
 ["ABDM-ready", "FHIR R4 records with room for ABHA linkage"]].forEach(([t, b], i) => {
  const y = 1.4 + i * 1.3;
  badge(s, 8.2, y + 0.05, String(i + 1), C.accent1, 0.45);
  txt(s, t, { x: 8.85, y, w: 3.9, h: 0.4, fontSize: 17, bold: true });
  txt(s, b, { x: 8.85, y: y + 0.42, w: 3.9, h: 0.8, fontSize: 14, color: C.text2 });
});
s.addNotes("NightTwin is designed for India: alerts in the family's language, voice calls for feature phones, models of the human insulin our programmes supply, Indian routines like late dinners and evening cricket, and FHIR records ready for ABDM.");

// ---------- 15. privacy ----------
pres.addSection({ title: "Trust and impact" });
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Trust and impact" });
s.addText("Privacy, safety and regulation", { placeholder: "title" });
[["Children's data (DPDP Act 2023)", "Section 9: verifiable parental consent; no tracking or behavioural monitoring of children. The DPDP Rules 2025 (Fourth Schedule) exempt clinics and healthcare professionals for health services to the child, so NightTwin is deployed by the clinic as data fiduciary, with consent recorded anyway.", C.accent1],
 ["Doctor in the loop", "The twin only shows simulated outcomes. The doctor approves every change; families receive only approved actions. No advertising or analytics on children's data.", C.accent3],
 ["Path to the clinic", "Decision support, not a diagnosis. A real deployment would follow CDSCO's medical device software pathway after a supervised clinical pilot.", C.accent2]].forEach(([t, b, c], i) => {
  const x = 0.6 + i * 4.1;
  card(s, x, 1.6, 3.8, 4.7);
  badge(s, x + 0.3, 1.9, ["§", "✓", "→"][i], c, 0.6);
  txt(s, t, { x: x + 0.3, y: 2.75, w: 3.2, h: 0.8, fontSize: 19, bold: true });
  txt(s, b, { x: x + 0.3, y: 3.6, w: 3.2, h: 2.6, fontSize: 14, color: C.text2 });
});
s.addNotes("Children's health data needs extra care. Under the DPDP Act, children's data needs verifiable parental consent, and the 2025 Rules exempt clinics providing health services, so NightTwin is deployed by the clinic. The doctor stays in charge of every decision.");

// ---------- 16. impact ----------
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Trust and impact" });
s.addText("Impact and how it scales", { placeholder: "title" });
stat(s, 0.6, 1.5, 3.8, "~1 hour", "of warning before a night-time low for CGM families, as a voice call", C.accent3);
stat(s, 4.75, 1.5, 3.8, "4.3×", "more night lows in the top third flagged by a trial sensor, so scarce CGMs go further", C.accent1);
stat(s, 8.9, 1.5, 3.8, "₹0", "licence cost: open source (Apache-2.0), deployable by state programmes and NGOs", C.accent2);
card(s, 0.6, 3.8, 12.1, 2.6);
txt(s, "Rollout path", { x: 0.9, y: 4.0, w: 4, h: 0.45, fontSize: 18, bold: true });
bullets(s, ["Pilot in one paediatric diabetes clinic with families already on a state T1D programme", "Recalibrate and validate on Indian children's data; measure night lows, parent sleep and false alarms", "Extend the same twin to adults with T2D on insulin or sulfonylureas"],
  { x: 0.9, y: 4.55, w: 11.5, h: 1.7, fontSize: 16 });
s.addNotes("The impact is measurable: about an hour of warning for CGM families, smarter use of scarce sensors for everyone else, and zero licence cost. Our rollout path starts with a clinic pilot, then validation on Indian children, then extension to adults with type 2 diabetes on insulin.");

// ---------- 17. limits ----------
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Trust and impact" });
s.addText("Limitations we know about", { placeholder: "title" });
[["Training population", "Models trained on adults in Spain and tested on adults in the UK, not Indian children. An Indian pilot is the next step."],
 ["Synthetic demo", "The 12 Indian children in the dashboard are synthetic. They show the method; they are never used for accuracy numbers."],
 ["Bedtime prediction", "Bedtime-only risk is weak on real data. We use it to compare plans, not to promise safety."],
 ["Translations and regulation", "Translations are drafts for native-speaker review. Not a medical device yet."]].forEach(([t, b], i) => {
  const x = 0.6 + (i % 2) * 6.15, y = 1.55 + Math.floor(i / 2) * 2.6;
  card(s, x, y, 5.95, 2.35);
  txt(s, t, { x: x + 0.3, y: y + 0.25, w: 5.3, h: 0.45, fontSize: 19, bold: true });
  txt(s, b, { x: x + 0.3, y: y + 0.85, w: 5.3, h: 1.3, fontSize: 15, color: C.text2 });
});
s.addNotes("We are open about our limits: the models were trained on adults abroad, the demo children are synthetic, bedtime prediction is weak, and this is not yet a medical device. Each has a clear next step.");

// ---------- 18. close ----------
pres.addSection({ title: "Close" });
s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: "Close" });
s.addText("Let the twin face the night first", { placeholder: "title" });
s.addText("So a mother can sleep, and a child wakes up safe", { placeholder: "body" });
txt(s, [TEAM, COLLEGE].filter(Boolean).join(" · ") + "\n" + MEMBERS, { x: 0.7, y: 5.3, w: 8.5, h: 0.75, fontSize: 16, color: C.background1 });
txt(s, "Live demo: manangilhotra.github.io/TwinPulse_NewtonSchoolOfTechnology_RishihoodUniversity", { x: 0.7, y: 6.15, w: 8.5, h: 0.4, fontSize: 14, color: C.accent5 });
s.addShape(pres.shapes.OVAL, { x: 9.9, y: 1.7, w: 2.6, h: 2.6, fill: { color: C.accent2 }, line: { color: C.accent2 }, objectName: "moon-close" });
s.addShape(pres.shapes.OVAL, { x: 10.6, y: 1.45, w: 2.4, h: 2.4, fill: { color: C.text1 }, line: { color: C.text1 }, objectName: "moon-close-shadow" });
s.addNotes("In 1970, NASA rehearsed the Apollo 13 rescue on a twin of the spacecraft before trying it for real. NightTwin does the same for a child's night. Thank you.");

(async () => {
  await pres.writeFile({ fileName: OUT });
  // Optional: write the theme colours into the file (needs a theme helper; scheme colours fall back otherwise).
  if (process.env.PPTX_SKILL) {
    const { applyTheme } = require(process.env.PPTX_SKILL + "/scripts/apply_theme.js");
    await applyTheme(OUT, THEME);
  }
  console.log(OUT);
})();
