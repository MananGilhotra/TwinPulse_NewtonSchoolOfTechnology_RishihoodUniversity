"""NightTwin jury video script: the single source for docs/VIDEO_SCRIPT.md and the narrated video.

Each segment: section, speaker, what to have on screen (cue), what to say (line), and the
image the auto-generated video shows (slide-NN from the deck, or a dashboard frame key from
make_video.FRAMES). Run `python scripts/video_script.py` to regenerate docs/VIDEO_SCRIPT.md.
"""
from __future__ import annotations

import os

LIVE = "https://manangilhotra.github.io/TwinPulse_NewtonSchoolOfTechnology_RishihoodUniversity/"
REPO = "https://github.com/MananGilhotra/TwinPulse_NewtonSchoolOfTechnology_RishihoodUniversity"

SECTIONS = [
    # (title, approx start time)
    ("1. Cold open: 2:47 AM", "0:00"),
    ("2. Who we are", "1:40"),
    ("3. The problem in India", "2:45"),
    ("4. The idea: let the twin live the night first", "4:40"),
    ("5. Meeting the brief: two data streams, one twin", "6:10"),
    ("6. Architecture", "7:40"),
    ("7. Inside the physiology twin", "8:50"),
    ("8. Live demo", "10:30"),
    ("9. Evidence on real patients", "17:20"),
    ("10. Built for India, built to be trusted", "19:40"),
    ("11. Impact, roadmap and honest limits", "21:00"),
    ("12. Try it yourself", "22:20"),
    ("13. Closing", "22:50"),
]

S = [
    # ---------------- 1. Cold open ----------------
    dict(sec=0, who="Manan", img="slide-02",
         cue="Slide 2 (2:47 AM in Raichur). Start on this slide. Speak slowly; let the quote sit on screen for two seconds before you begin.",
         line="It is two forty-seven in the morning, in Raichur, Karnataka. A phone alarm goes off in a small house. "
              "Lakshmi wakes up, picks up a glucometer, and gently pricks the finger of her sleeping nine-year-old daughter, Ananya. "
              "She has done this almost every night for three years."),
    dict(sec=0, who="Manan", img="slide-02",
         cue="Stay on Slide 2. Pause after 'dangerous one'.",
         line="Ananya has type 1 diabetes. Insulin keeps her alive, but insulin can also push her blood sugar dangerously low while she sleeps. "
              "It is a fear parents of children with type 1 diabetes describe again and again: 'I never know which night is the dangerous one.' "
              "Ananya and Lakshmi are a composite, built from what such families describe. But their night is real, for thousands of families across India."),
    dict(sec=0, who="Manas", img="slide-02",
         cue="Stay on Slide 2. Point to the three numbers on the right as you say them.",
         line="That fear is real. In the landmark DCCT trial, fifty-five percent of severe lows happened during sleep. "
              "A sudden overnight death, called dead-in-bed syndrome, is linked to around five to six percent of deaths in people with type 1 diabetes under forty. "
              "And yet, a low that is seen one hour early is treated with nothing more than a glass of juice. One hour. That is the difference we set out to give back."),

    # ---------------- 2. Who we are ----------------
    dict(sec=1, who="Manan", img="slide-01",
         cue="Switch to Slide 1 (title slide).",
         line="We are Team TwinPulse, from Newton School of Technology, Rishihood University. I am Manan Gilhotra, and with me is Manas Saxena. "
              "Our project for the Happiest Health Digital Twin Challenge is called NightTwin."),
    dict(sec=1, who="Manas", img="slide-01",
         cue="Stay on Slide 1.",
         line="NightTwin is a digital twin of a child with diabetes. Before the child goes to sleep, her twin lives the coming night first, five hundred times, "
              "so that her doctor can see the danger, understand it, and fix it, before it ever happens to the real child. "
              "In the next twenty minutes we will show you the problem, the science, a live demo, our results on real patients, including what did not work, and how this can reach families across India."),

    # ---------------- 3. Problem in India ----------------
    dict(sec=2, who="Manas", img="slide-03",
         cue="Slide 3 (India has the most children with type 1 diabetes).",
         line="Why does this matter so much in India? Because India has more children and teenagers living with type 1 diabetes than any other country on earth: about two point two nine lakh, according to the IDF Diabetes Atlas. "
              "Across all ages, the 2025 Atlas counts about nine point four lakh Indians with type 1 diabetes."),
    dict(sec=2, who="Manan", img="slide-03",
         cue="Stay on Slide 3. Point to the '₹1.1 lakh+' card, then the 'NPH' card.",
         line="The technology that protects children at night already exists. A continuous glucose monitor, a CGM, can sound an alarm when sugar falls. "
              "But in India it costs four to five thousand rupees for every two-week sensor. More than one lakh rupees a year. For most families, that is simply out of reach. "
              "And many state programmes supply human insulin, whose long-acting part, NPH, peaks between one and four in the morning, exactly when the whole family is asleep."),
    dict(sec=2, who="Manan", img="slide-03",
         cue="Stay on Slide 3. Slow down for the last sentence.",
         line="So families are forced into an impossible choice: a lakh of rupees a year, or an alarm at two in the morning, every night, for years. "
              "Some parents, out of sheer fear, keep their child's sugar high to avoid lows, which quietly damages the eyes and kidneys over time. "
              "No child should have to grow up like this. No parent should have to live like this."),

    # ---------------- 4. Idea ----------------
    dict(sec=3, who="Manas", img="slide-04",
         cue="Slide 4 (learn the child, live tonight first, guard the real night).",
         line="In 1970, when Apollo 13 was in trouble, NASA did not experiment on the real spacecraft. They rehearsed the rescue on a twin of it, on the ground, and only then tried it for real. "
              "That idea, rehearse on the twin first, is the heart of NightTwin."),
    dict(sec=3, who="Manas", img="slide-04",
         cue="Stay on Slide 4. Touch each of the three cards as you name them.",
         line="NightTwin does three things. First, it learns the child: a personal physiological model is fitted to each child from her own nights. "
              "Second, it lives tonight first: at nine PM, the twin simulates the coming night five hundred times, and the doctor sees who is at risk, when, and why, and can try a fix on the twin before prescribing it. "
              "Third, it guards the real night: for children with a CGM, a model trained on real patients warns about an hour before a low and calls the parent, in their own language."),
    dict(sec=3, who="Manan", img="slide-04",
         cue="Stay on Slide 4. Point to the line at the bottom of the slide.",
         line="And through all of it, the doctor stays in charge. The twin suggests. The doctor decides. The family only ever receives an action the doctor has approved."),

    # ---------------- 5. Brief / data ----------------
    dict(sec=4, who="Manan", img="slide-05",
         cue="Slide 5 (fusing the health record with wearable streams).",
         line="The challenge asked for a prototype that fuses two data streams and predicts an adverse event. Here is exactly how we do that. "
              "The static stream is the electronic health record, stored as FHIR R4, the same standard India's Ayushman Bharat Digital Mission uses. "
              "It holds demographics, the diagnosis, labs like HbA1c and haemoglobin, the insulin regimen, the history of severe lows, whether the child can still feel a low coming, "
              "and genetic markers: the HLA risk genotype and islet autoantibodies."),
    dict(sec=4, who="Manas", img="slide-05",
         cue="Stay on Slide 5. Point to the dataset table at the bottom.",
         line="The dynamic stream comes from wearables: glucose every five minutes from a CGM, or a few finger-pricks, insulin doses, meals, and steps and heart rate from a simple band. "
              "We followed the sandbox rules strictly. We trained and tested only on open, anonymised data from real people with type 1 diabetes: HUPA-UCM from Spain, and T1D-UOM from the United Kingdom, which we kept aside as an external test. "
              "The twelve Indian children in our demo are synthetic. We built them to show the method, and we never use them to claim accuracy."),

    dict(sec=4, who="Manan", img="slide-05",
         cue="Stay on Slide 5.",
         line="We put real care into making the synthetic children realistic. Each one is generated by the same physiology, with Indian growth references for weight and height, a daily insulin dose that rises in puberty, "
              "and a real Indian day: breakfast at seven thirty, school tiffin, lunch, tea and biscuits in the evening, play on most days, and dinner at nine. "
              "Their insulin regimens are the ones Indian families actually use: NPH and regular human insulin twice a day, premixed thirty-seventy, or glargine with rapid insulin. "
              "And their sensitivity to insulin changes from day to day, as it does with growth, stress and illness, which is exactly why some nights go low and others do not."),

    # ---------------- 6. Architecture ----------------
    dict(sec=5, who="Manas", img="slide-06",
         cue="Slide 6 (architecture). Or open docs/TwinPulse_Architecture.pdf full-screen. Trace left to right with the cursor.",
         line="This is the architecture, from left to right. Data comes in from the health record and the wearables. "
              "We build a single five-minute timeline for each child, compute the insulin and carbohydrates still active in the body, and even infer meals that were never logged, using the clinical five hundred rule."),
    dict(sec=5, who="Manan", img="slide-06",
         cue="Stay on the architecture. Move the cursor over Models A, B and C, then the Trust layer at the bottom.",
         line="Then come three models. Model A is the physiology twin. Model B is the night guard, a LightGBM model. Model C ranks which children need a CGM most. "
              "A FastAPI service feeds the doctor's dashboard and the family channel. And underneath everything sits a trust layer: parental consent, the clinic as the data fiduciary, the doctor in the loop, and every result published openly."),

    # ---------------- 7. Twin science ----------------
    dict(sec=6, who="Manan", img="slide-07",
         cue="Slide 7 (the physiology twin). Point to the purple band, then the green line.",
         line="What makes NightTwin a true digital twin, and not just another classifier, is Model A. It is a physiological model of glucose and insulin, built on the Bergman minimal model that diabetes researchers have trusted for over forty years. "
              "We extended it with depots for rapid insulin and for long-acting NPH or glargine, with carbohydrate absorption, and with an exercise effect that lingers for about four hours, because an evening cricket match can cause a low at two in the morning."),
    dict(sec=6, who="Manas", img="slide-07",
         cue="Stay on Slide 7.",
         line="Each child's twin is fitted to that child's own previous nights, with insulin sensitivity anchored to the eighteen hundred rule that doctors already use. "
              "At bedtime it takes in today's readings, then lives the night from eleven PM to seven thirty, five hundred times, with realistic variation. "
              "So the answer is not a single guess. It is the full range of nights that could happen: how likely a low is, when it is likely, and how deep it could go."),

    # ---------------- 8. Live demo ----------------
    dict(sec=7, who="Manan", img="overview_top",
         cue=f"Switch to the browser. Open the live demo: {LIVE}  (or http://localhost:8000 after ./run.sh). You land on Overview.",
         line="Let us show you NightTwin working. This is our live dashboard, built for a paediatric diabetes clinic, for example in a district hospital or a state programme. "
              "It is running right now, in the browser, with nothing installed."),
    dict(sec=7, who="Manan", img="overview_proof",
         cue="On Overview, scroll down slowly to the 'Tested on real patients' strip and the data-fusion strip.",
         line="The overview carries our promise in one line, and right below it, our proof, measured on real patients the model had never seen: "
              "ninety-seven percent of night-time lows warned at least fifteen minutes ahead, a median warning of sixty-five minutes, and about one false alarm every two nights."),
    dict(sec=7, who="Manas", img="board",
         cue="Click 'Tonight Board' in the navbar. Then click the 'Needs attention' filter chip, then 'All children' again.",
         line="It is nine PM. This is the Tonight Board. Every child's twin has already lived tonight five hundred times, and the children are ranked by how many of those nights go low. "
              "Four children are at high risk tonight, and for each one, NightTwin suggests a call to the family before bed. "
              "For every child we see the likely time of a low, the last glucose reading, whether the family has a CGM or only finger-pricks, the insulin regimen, and how often they went low over the last two weeks."),
    dict(sec=7, who="Manan", img="board",
         cue="Hover over a red 'Call family' button on the Tonight Board.",
         line="Think about what this means for a busy clinic. A diabetes educator responsible for hundreds of children does not need to guess. In two minutes at nine PM, she knows exactly which four families to call tonight, "
              "and what to tell them. That is how a digital twin turns into a phone call that changes a night."),
    dict(sec=7, who="Manas", img="ananya_top",
         cue="Click Ananya's row (top row). Point to the red 58% card, then the purple fan chart.",
         line="Let us open Ananya. Nine years old, from Raichur, on human insulin from a state programme, and her family can afford only three test strips a day. "
              "Fifty-eight percent of her rehearsed nights go low, most often around half past midnight. This band is her night, lived five hundred times. The dashed red line is seventy, the threshold for a low."),
    dict(sec=7, who="Manan", img="ananya_top",
         cue="Point to the 'Why tonight is risky' card on the right; read the top bar.",
         line="And here is something a doctor can actually act on: why tonight is risky. The twin removes one factor at a time and lives the night again. "
              "Her dinner insulin matters most. The dinner-time NPH, peaking in the early morning, and this evening's play add to it. Every reason here is something that can be changed."),
    dict(sec=7, who="Manas", img="ananya_record",
         cue="Scroll the right column to 'Health record' and 'Last 14 days'. Point to 'Impaired hypo awareness' and the consent line.",
         line="Below that is her health record, read from her FHIR bundle: HbA1c, haemoglobin, daily insulin, a severe low last year, impaired awareness of lows, her HLA genotype and autoantibodies. "
              "If a child is anaemic, NightTwin warns that HbA1c can read falsely high, which is common in India. The consent line confirms a parent's verifiable consent. "
              "And the fourteen-day summary uses international targets: time in range, time below seventy, and time below fifty-four."),
    dict(sec=7, who="Manan", img="ananya_snack",
         cue="In 'Rehearse a plan on the twin', click the 'Bedtime snack' chip. Wait for the green band to appear.",
         line="Now, the moment that matters most. We rehearse a plan on the twin. Let us try a simple bedtime snack: a glass of milk and two biscuits. "
              "The green band is her night with the plan. The risk falls. But not enough."),
    dict(sec=7, who="Manan", img="ananya_plan",
         cue="Click the 'Snack + NPH at bedtime' chip. Point to the result line ('58% → 12–14%'). Then click 'Approve plan and send to family'.",
         line="So we add the standard clinical fix for night lows on human insulin: move the evening NPH from dinner to bedtime, so its peak slides past three in the morning. "
              "Fifty-eight percent falls into the low teens. The doctor saw it, on the twin, before touching the real child. "
              "One click to approve, and Lakshmi receives the plan in Kannada. For a family with a basic phone, it arrives as a voice call."),
    dict(sec=7, who="Manas", img="ananya_plan",
         cue="Optional: click 'Reset', then the 'Sports day: dinner dose −20%' chip to show a third option; then click 'Snack + NPH at bedtime' again.",
         line="The doctor can try as many plans as she likes, in seconds: a smaller dinner dose after a sports day, a lower NPH dose, a later NPH, or simply a calmer evening. "
              "Each time, the twin lives the night again, five hundred times. This is what we mean by personalising treatment on a virtual patient, exactly as the challenge describes, before it touches the real one."),
    dict(sec=7, who="Manas", img="ananya_timeline",
         cue="Scroll down to 'Last 36 hours'.",
         line="Notice her last thirty-six hours: only a few finger-prick dots, not a continuous line. That is the reality of most Indian families, and NightTwin is built for that reality, not for an ideal one."),
    dict(sec=7, who="Manas", img="arjun_top",
         cue="Click '← Tonight Board', then click Arjun's row (third row).",
         line="Now Arjun. Fourteen, from Kochi, on glargine, with a CGM through a state programme, and he plays football most evenings. "
              "His twin goes low in about half of rehearsed nights, driven by his dinner insulin and that evening football."),
    dict(sec=7, who="Manan", img="arjun_guard",
         cue="Scroll to 'Night guard: replay of tonight'. Click '▶ Replay night'. Stay silent for three seconds as the line draws, then speak as the red alert line appears.",
         line="Because Arjun has a CGM, the night guard watches every five minutes. Let us replay tonight. "
              "Watch the red line: the guard's estimate of a low within two hours. At eleven thirty-five PM, it crosses the threshold, and his father's phone rings, in Malayalam. "
              "'Arjun's sugar may go low within the hour. Please check now, and give juice.' The low actually began at twenty past midnight. Forty-five minutes of warning. A glass of juice, instead of an emergency."),
    dict(sec=7, who="Manas", img="arjun_guard",
         cue="Stay on the replay. Point to the risk line and the alert marker.",
         line="How does the guard decide? It reads the last two hours of glucose and how fast it is falling, the insulin and carbohydrates still active, recent steps, and heart rate against the child's own usual level. "
              "We smooth the risk over fifteen minutes, so a single noisy reading never wakes a family, and we only alert while sugar is still above seventy, so the call comes before the low, not during it."),
    dict(sec=7, who="Manas", img="sensors",
         cue="Click 'Sensor Priority' in the navbar. Change 'CGMs available' from 2 to 3 and back.",
         line="But most families have no CGM at all. So we asked: if a programme has only a few sensors, who should get them? "
              "Each child wears one two-week trial sensor. The twin ranks who will have the most night lows, and shows exactly which children should receive a CGM. Scarce sensors, used where they save the most."),
    dict(sec=7, who="Manan", img="evidence_top",
         cue="Click 'Evidence' in the navbar. Click 'More sensitive', then 'Fewer alarms', then back to 'Balanced (default)'.",
         line="Every number on this page comes from real patients. And a clinic can choose how sensitive the guard should be. "
              "More sensitive catches more lows but wakes parents more often. Fewer alarms means more sleep but less warning. We believe that trade-off belongs to the clinician, openly, not hidden inside a model."),

    # ---------------- 9. Evidence ----------------
    dict(sec=8, who="Manas", img="slide-09",
         cue="Back to the slides: Slide 9 (night guard).",
         line="Now, the evidence. We split real patients into five groups, so every score is on people the model never saw during training. "
              "Out of three hundred and fifteen real night-time lows, ninety-seven percent were warned at least fifteen minutes ahead. The median warning was sixty-five minutes, with about point five five false alarms per night."),
    dict(sec=8, who="Manan", img="slide-10",
         cue="Slide 10 (results charts). Point to the light-purple 'External test (UK)' bars.",
         line="Then we tested on a completely different country, different devices, different people: the UK dataset. There, sixty-eight percent of night lows were warned at least fifteen minutes ahead, with a median of sixty-two minutes. "
              "Performance drops on a new population, as it should, and we show it to you as it is. Our glucose forecasts also beat the standard baseline at every horizon, from thirty minutes to two hours."),
    dict(sec=8, who="Manas", img="slide-10",
         cue="Stay on Slide 10. Point to the right-hand chart (forecast error).",
         line="Beyond alerts, the model also forecasts glucose itself. Thirty minutes ahead, its error is about eighteen milligrams per decilitre, against twenty-one for simply assuming nothing changes. "
              "Two hours ahead, forty-four, against fifty-two. On the clinical Clarke error grid, nearly ninety-eight percent of thirty-minute forecasts fall in the safe zones. "
              "And as an area under the curve, the night guard scores zero point nine three for a low within the hour."),
    dict(sec=8, who="Manas", img="slide-11",
         cue="Slide 11 (what did not work). Point to the orange bars.",
         line="And now the part we are most proud to show you: what did not work. We began with a dream, to tell a mother at bedtime whether tonight would be safe. "
              "We tested that on over a thousand real nights, with simple rules, with machine learning, and with our own physiology twin. Every method was close to chance."),
    dict(sec=8, who="Manan", img="evidence_honest",
         cue="Optional: show the 'What we could not do' card on the Evidence page; otherwise stay on Slide 11.",
         line="We could have hidden that. We chose not to. Instead, we changed the design. The bedtime rehearsal is used to compare plans, to see what makes tonight safer, never to promise a night is safe. "
              "And the warnings come from the in-night guard, which does work. In healthcare, honesty is not a weakness of a model. It is a feature."),
    dict(sec=8, who="Manas", img="slide-12",
         cue="Slide 12 (sensor priority evidence). Point to 42% and 10%.",
         line="What does work without nightly CGM is ranking. Across twenty-nine real patients, one week on a sensor ranked who would go on to have the most night lows. "
              "Children in the top third went low on forty-two percent of later nights. The bottom third, on ten percent. A four-to-five-thousand-rupee trial sensor can direct a programme's scarce CGMs to the children who need them most."),

    # ---------------- 10. India & trust ----------------
    dict(sec=9, who="Manan", img="slide-14",
         cue="Slide 14 (built for Indian families and clinics).",
         line="NightTwin is built for India from the ground up. Alerts go out in the family's own language, Kannada, Hindi, Malayalam and more, and as voice calls that work on any feature phone. "
              "It models the human insulin our programmes actually supply, not just expensive analogues. It understands late dinners, evening cricket and school tiffin. And every record is FHIR, ready to link with ABHA."),
    dict(sec=9, who="Manas", img="privacy",
         cue="Switch to the browser: click 'Privacy & India' in the navbar.",
         line="And we take children's data seriously. Under section nine of the DPDP Act, a child's data needs verifiable parental consent, and tracking or behavioural monitoring of children is not allowed. "
              "The DPDP Rules of 2025 exempt clinics and healthcare professionals when they are providing health services to the child. So NightTwin is deployed by the clinic, as the data fiduciary, and we still record parental consent. No advertising. No analytics on children."),
    dict(sec=9, who="Manan", img="slide-15",
         cue="Slide 15 (privacy, safety and regulation).",
         line="The doctor stays in the loop at every single step. NightTwin is decision support, not a diagnosis, and a real deployment would follow CDSCO's pathway for medical-device software after a supervised clinical pilot."),

    # ---------------- 11. Impact ----------------
    dict(sec=10, who="Manas", img="slide-16",
         cue="Slide 16 (impact and how it scales).",
         line="What does this mean for a family? About an hour of warning before a night-time low, as a phone call. For families without a CGM, a fairer chance at one. "
              "And zero licence cost: NightTwin is open source under Apache 2.0, so any state programme or NGO can use it freely. "
              "Our path is clear: a pilot in one paediatric diabetes clinic, then validation on Indian children, and then the same twin for adults with type 2 diabetes on insulin, where night lows are just as dangerous."),
    dict(sec=10, who="Manan", img="slide-17",
         cue="Slide 17 (limitations).",
         line="We are also clear about our limits. Our models were trained on adults in Spain and tested in the UK, not on Indian children, so an Indian pilot is essential. "
              "Our demo children are synthetic, our translations need native review, and NightTwin is not yet a medical device. Each of these has a clear next step, and we are ready to take it."),

    dict(sec=10, who="Manas", img="slide-16",
         cue="Stay on Slide 16. Point to 'Rollout path'.",
         line="In a pilot, we will measure what families actually feel: fewer night-time lows, fewer alarms that turn out to be nothing, and something no glucose chart can show, how many nights a parent gets to sleep. "
              "Because if NightTwin works, its most important result will not be an area under a curve. It will be a mother who finally sleeps through the night."),

    # ---------------- 12. Try it ----------------
    dict(sec=11, who="Manas", img="overview_top",
         cue=f"Show the GitHub repo page: {REPO}  Scroll past the README table (team, live demo, video, PDFs).",
         line="Everything you have seen is open. Our public GitHub repository has the code, the data sources, every result, the architecture diagram and this presentation. "
              "The live demo runs in any browser. And one command, run dot s h, sets up everything on a laptop. Every number can be regenerated from the raw open data, and an automated test suite checks the API, the twin and the guard."),

    dict(sec=11, who="Manan", img="slide-06",
         cue="Optional: show the repo's README 'Technical stack' section, or stay on the architecture slide.",
         line="For the technical panel: the twin and the models are written in Python, with NumPy, SciPy and numba for a fast simulator, and LightGBM with scikit-learn for the guard. "
              "The service is FastAPI, the dashboard is React with Recharts, and we ported the twin to JavaScript so it can re-live a night inside the browser in about a fifth of a second. "
              "Health records are FHIR R4, and the whole project is released under the Apache 2.0 licence."),

    # ---------------- 13. Closing ----------------
    dict(sec=12, who="Manan", img="slide-18",
         cue="Slide 18 (closing). Look at the camera if you are on video. Slow down.",
         line="Let us go back to Raichur, to two forty-seven in the morning. Tonight, Ananya's twin has already lived this night, five hundred times. "
              "Her doctor saw the danger at nine PM, and fixed it with a glass of milk and a change in timing. Tonight, Lakshmi's alarm does not need to ring."),
    dict(sec=12, who="Manas", img="slide-18",
         cue="Stay on Slide 18. Pause one beat before 'Thank you'.",
         line="NASA rehearsed a rescue on a twin to bring three astronauts home. We built NightTwin to bring every child safely to morning. "
              "Let the twin face the night first, so a mother can sleep, and a child wakes up safe. "
              "We are Team TwinPulse, from Newton School of Technology, Rishihood University. Thank you."),
]


def write_markdown(path):
    words = sum(len(x["line"].split()) for x in S)
    lines = [
        "# NightTwin: jury video script (Team TwinPulse)",
        "",
        f"About {words} spoken words, which is **about 22–24 minutes** at a calm pace (the challenge needs at least 20). "
        "Speakers: **Manan Gilhotra** (team leader) and **Manas Saxena**.",
        "",
        "Every line below says **what to have on screen** (🖥) and **what to say** (🎙). "
        "The same script drives the auto-generated narrated video (`scripts/make_video.py`), so the two always match.",
        "",
        "## Before you record",
        "",
        f"1. Open the **live demo** in Chrome, full screen, at least 1440 px wide: {LIVE} (or run `./run.sh` and open http://localhost:8000).",
        "2. Open `docs/TwinPulse_Presentation.pdf` (or the .pptx) in presentation mode in a second window. Slide numbers below refer to this deck.",
        "3. Record with QuickTime (File → New Screen Recording) or OBS, with an external mic if you have one. Close notifications.",
        "4. Upload to YouTube as **Unlisted** and paste the link into the README's video row. Keep the release video as a backup.",
        "",
        "## How to deliver it",
        "",
        "- **The first 90 seconds decide the jury's attention.** Read the cold open slowly, almost quietly, and pause after *\"which night is the dangerous one.\"*",
        "- Say **\"synthetic\"** whenever you show Ananya or Arjun, and **\"real patients\"** whenever you quote a result. That honesty is what makes the jury trust the rest.",
        "- During the live demo, **do the action first, then speak**: click, let the screen change, then narrate.",
        "- Smile on the closing lines. End on *\"Thank you\"*, not on a fade-out.",
        "",
    ]
    for si, (title, t) in enumerate(SECTIONS):
        lines += [f"## {title}  ·  starts ~{t}", ""]
        for x in S:
            if x["sec"] != si:
                continue
            lines += [f"**{x['who']}**  ", f"🖥 *{x['cue']}*  ", f"🎙 {x['line']}", ""]
    lines += [
        "## Coverage checklist (what the jury must see)",
        "",
        "| Brief requirement | Where in the video |",
        "|---|---|",
        "| Specific condition prevalent in India | Section 3 |",
        "| Static EHR stream (demographics, diagnoses, labs, **genetic markers**) | Sections 5, 8 (health record card) |",
        "| Dynamic wearable stream (CGM, steps, heart rate) | Sections 5, 8 (timeline, night guard) |",
        "| Model that ingests both and **predicts an adverse event in advance** | Sections 7, 8 (guard replay: 45 min warning), 9 |",
        "| Doctor-facing UI dashboard | Section 8 (Tonight Board, twin view, rehearse, approve) |",
        "| Synthetic/open data only (sandbox rules) | Section 5 |",
        "| Architecture | Section 6 |",
        "| Results and outcome | Section 9 |",
        "| Real-world healthcare impact | Sections 10–11 |",
        "| Open-source licence, repo, presentation | Section 12 |",
        "",
    ]
    with open(path, "w") as f:
        f.write("\n".join(lines))
    return words


if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    w = write_markdown(os.path.join(root, "docs", "VIDEO_SCRIPT.md"))
    print(f"docs/VIDEO_SCRIPT.md written: {len(S)} segments, {w} words")
