# NightTwin: jury video script (Team TwinPulse)

About 2711 spoken words, **about 22–25 minutes** at a calm pace (the challenge needs at least 20). Speakers: **Manas Saxena** (team leader) and **Manan Gilhotra**.

Every line says **what to have on screen** (🖥) and **what to say** (🎙). The same script drives the produced video (`scripts/make_video.py`), so the two always match.

**Opens on:** *"Every night, somewhere in India, a parent sets an alarm for two in the morning."*  
**Ends on:** *"Tonight, somewhere in India, a two AM alarm will ring. We built NightTwin so that one day, it won't have to."*

## Before you record

1. Open the **live demo** in Chrome, full screen, at least 1440 px wide: https://manangilhotra.github.io/TwinPulse_NewtonSchoolOfTechnology_RishihoodUniversity/ (or run `./run.sh` and open http://localhost:8000).
2. Open `docs/TwinPulse_Presentation.pdf` (or the .pptx) in presentation mode in a second window. Slide numbers below refer to this deck.
3. Record with QuickTime (File → New Screen Recording) or OBS, with an external mic if you have one. Close notifications.
4. Upload to YouTube as **Unlisted** and paste the link into the README's video row.

## How to deliver it

- **The first 20 seconds decide the jury's attention.** Say the opening hook slowly, with a pause after every sentence.
- Say **"synthetic"** whenever you show Ananya or Arjun, and **"real patients"** whenever you quote a result.
- In the live demo, **do the action first, then speak**: click, let the screen change, then narrate.
- End on the last line and *"Thank you"*, not on a fade-out.

## 1. Opening hook  ·  starts ~0:00

**Manas**  
🖥 *Black screen, or the NightTwin title. Say it slowly, with a pause after each sentence.*  
🎙 Every night, somewhere in India, a parent sets an alarm for two in the morning. Not to wake up early. To make sure their child is safe. What if someone could live that night first, five hundred times, before their child ever has to?

## 2. Ananya's night  ·  starts ~0:40

**Manas**  
🖥 *Slide 2 (2:47 AM in Raichur).*  
🎙 It is two forty-seven in the morning, in Raichur, Karnataka. A phone alarm goes off in a small house. Lakshmi wakes up, picks up a glucometer, and gently pricks the finger of her sleeping nine-year-old daughter, Ananya. She has done this almost every night for three years.

**Manas**  
🖥 *Stay on Slide 2. Pause after 'dangerous one'.*  
🎙 Ananya has type 1 diabetes. Insulin keeps her alive, but insulin can also push her blood sugar dangerously low while she sleeps. Parents of children like Ananya describe the same fear again and again: I never know which night is the dangerous one. Ananya and Lakshmi are a composite. But their night is real for thousands of families across India.

**Manan**  
🖥 *Stay on Slide 2. Point to the three numbers on the right as you say them.*  
🎙 The fear is real. In the landmark DCCT trial, fifty-five percent of severe lows happened during sleep. A sudden overnight death, called dead-in-bed syndrome, is linked to around five to six percent of deaths in people with type 1 diabetes under forty. And yet, a low seen one hour early is treated with a glass of juice. One hour. That is what we set out to give back.

## 3. Who we are  ·  starts ~2:20

**Manas**  
🖥 *Slide 1 (title).*  
🎙 We are Team TwinPulse, from Newton School of Technology, Rishihood University: Manas Saxena, our team leader, and Manan Gilhotra. Our project for the Happiest Health Digital Twin Challenge is called NightTwin. NightTwin is a digital twin of a child with diabetes. Before she sleeps, her twin lives the coming night first, five hundred times, so her doctor can see the danger, understand it, and fix it, before it ever happens to the real child.

## 4. The problem in India  ·  starts ~3:20

**Manan**  
🖥 *Slide 3 (India has the most children with type 1 diabetes).*  
🎙 India has more children and teenagers living with type 1 diabetes than any other country on earth: about two point two nine lakh, according to the IDF Diabetes Atlas. Across all ages, the 2025 Atlas counts about nine point four lakh Indians with type 1 diabetes.

**Manan**  
🖥 *Stay on Slide 3. Point to the '₹1.1 lakh+' card, then the 'NPH' card.*  
🎙 The technology that protects children at night already exists. A continuous glucose monitor, a CGM, can sound an alarm when sugar falls. But in India it costs four to five thousand rupees for every two-week sensor. More than one lakh rupees a year. For most families, that is out of reach. And many state programmes supply human insulin, whose long-acting part, NPH, peaks between one and four in the morning, exactly when the family is asleep.

**Manas**  
🖥 *Stay on Slide 3. Slow down for the last sentence.*  
🎙 So families face an impossible choice: a lakh of rupees a year, or an alarm at two in the morning, every night, for years. Some parents, out of fear, keep their child's sugar high to avoid lows, which quietly damages the eyes and kidneys over time. No child should grow up like this. No parent should have to live like this.

## 5. The idea: let the twin live the night first  ·  starts ~5:10

**Manas**  
🖥 *Slide 4 (learn the child, live tonight first, guard the real night).*  
🎙 In 1970, when Apollo 13 was in trouble, NASA did not experiment on the real spacecraft. They rehearsed the rescue on a twin of it, on the ground, and only then tried it for real. That idea, rehearse on the twin first, is the heart of NightTwin.

**Manas**  
🖥 *Stay on Slide 4. Touch each of the three cards as you name them.*  
🎙 NightTwin does three things. First, it learns the child: a personal physiological model is fitted to each child from her own nights. Second, it lives tonight first: at nine PM the twin simulates the coming night five hundred times, so the doctor sees who is at risk, when, and why, and can try a fix on the twin before prescribing it. Third, it guards the real night: for children with a CGM, a model trained on real patients warns about an hour before a low, and calls the parent in their own language. And through all of it, the doctor stays in charge. The twin suggests. The doctor decides.

## 6. Meeting the brief: two data streams, one twin  ·  starts ~6:50

**Manan**  
🖥 *Slide 5 (fusing the health record with wearable streams).*  
🎙 The challenge asked for a prototype that fuses two data streams and predicts an adverse event. Here is exactly how we do it. The static stream is the electronic health record, stored as FHIR R4, the standard India's Ayushman Bharat Digital Mission uses. It holds demographics, the diagnosis, labs like HbA1c and haemoglobin, the insulin regimen, the history of severe lows, whether the child can still feel a low coming, and genetic markers: the HLA risk genotype and islet autoantibodies.

**Manan**  
🖥 *Stay on Slide 5. Point to the dataset table at the bottom.*  
🎙 The dynamic stream comes from wearables: glucose every five minutes from a CGM, or a few finger-pricks, insulin doses, meals, and steps and heart rate from a simple band. We followed the sandbox rules strictly. We trained and tested only on open, anonymised data from real people with type 1 diabetes: HUPA-UCM from Spain, and T1D-UOM from the United Kingdom, kept aside as an external test. The twelve Indian children in our demo are synthetic, generated with Indian routines and the insulin regimens Indian families actually use. We never use them to claim accuracy.

## 7. Architecture and the physiology twin  ·  starts ~8:40

**Manas**  
🖥 *Slide 6 (architecture), or docs/TwinPulse_Architecture.pdf. Trace left to right with the cursor.*  
🎙 This is the architecture, from left to right. Data comes in from the health record and the wearables. We build one five-minute timeline per child, compute the insulin and carbohydrates still active in the body, and infer meals that were never logged. Then come three models. Model A is the physiology twin. Model B is the night guard, a LightGBM model. Model C ranks which children need a CGM most. A FastAPI service feeds the doctor's dashboard and the family channel, and underneath sits a trust layer: consent, doctor in the loop, and every result published openly.

**Manan**  
🖥 *Slide 7 (the physiology twin). Point to the purple band, then the green line.*  
🎙 What makes NightTwin a true digital twin, and not just another classifier, is Model A: a physiological model of glucose and insulin, built on the Bergman minimal model that diabetes researchers have trusted for over forty years. We extended it with rapid and long-acting insulin, carbohydrate absorption, and an exercise effect that lingers for hours, because an evening cricket match can cause a low at two in the morning. Each child's twin is fitted to her own previous nights. At bedtime it takes in today's readings and lives the night five hundred times. So the answer is not a single guess. It is the full range of nights that could happen: how likely a low is, when, and how deep.

## 8. Live demo  ·  starts ~11:00

**Manas**  
🖥 *Switch to the browser. Open the live demo: https://manangilhotra.github.io/TwinPulse_NewtonSchoolOfTechnology_RishihoodUniversity/  (or http://localhost:8000 after ./run.sh).*  
🎙 Let us show you NightTwin working. This is our live dashboard, built for a paediatric diabetes clinic, in a district hospital or a state programme. It is running right now, in the browser, with nothing installed. Everything you are about to see is clickable, by you, today.

**Manas**  
🖥 *On Overview, scroll to the 'Tested on real patients' strip and the data-fusion strip.*  
🎙 Right on the front page is our proof, measured on real patients the model had never seen: ninety-seven percent of night-time lows warned at least fifteen minutes ahead, a median warning of sixty-five minutes, and about one false alarm every two nights. And below it, the fusion: the health record, plus the wearables, into the twin. Out comes the risk, the reason, a plan, and an alert.

**Manan**  
🖥 *Click 'Tonight Board'. Click 'Needs attention', then 'All children'. Hover a red 'Call family' button.*  
🎙 It is nine PM. This is the Tonight Board. Every child's twin has already lived tonight five hundred times, and children are ranked by how many of those nights go low. Four children are at high risk tonight. For a diabetes educator responsible for hundreds of children, there is no more guessing: in two minutes she knows exactly which four families to call before bed, and why.

**Manan**  
🖥 *Click Ananya's row. Point to the red 58% card, then hover over the purple band.*  
🎙 Let us open Ananya. Nine years old, from Raichur, on human insulin from a state programme, and her family can afford only three test strips a day. Fifty-eight percent of her rehearsed nights go low, most often around half past midnight. This band is her night, lived five hundred times. The dashed red line is seventy, the threshold for a low.

**Manas**  
🖥 *Point to 'Why tonight is risky'; read the top bar.*  
🎙 And here is something a doctor can act on: why tonight is risky. The twin removes one factor at a time and lives the night again. Her dinner insulin matters most. The dinner-time NPH, peaking in the early morning, and this evening's play add to it. Every reason here is something that can be changed.

**Manan**  
🖥 *Scroll the right column to 'Health record' and 'Last 14 days'.*  
🎙 Below is her health record, read from her FHIR bundle: HbA1c, haemoglobin, daily insulin, a severe low last year, impaired awareness of lows, her HLA genotype and autoantibodies. If a child is anaemic, NightTwin warns that HbA1c can read falsely high, which is common in India. The consent line confirms a parent's verifiable consent, and the fourteen-day summary uses international targets: time in range, time below seventy, and time below fifty-four.

**Manas**  
🖥 *In 'Rehearse a plan on the twin', click 'Bedtime snack'. Wait for the green band.*  
🎙 Now the moment that matters most. We rehearse a plan on the twin. A simple bedtime snack: a glass of milk and two biscuits. The green band is her night with the plan. The risk falls. But not enough.

**Manas**  
🖥 *Click 'Snack + NPH at bedtime'. Point to the result line. Click 'Approve plan and send to family'.*  
🎙 So we add the standard clinical fix for night lows on human insulin: move the evening NPH from dinner to bedtime, so its peak slides past three in the morning. Fifty-eight percent falls into the low teens. The doctor saw it on the twin, before touching the real child. One click to approve, and Lakshmi receives the plan in Kannada. On a basic phone, it arrives as a voice call.

**Manan**  
🖥 *Click 'Reset', then 'Sports day: dinner dose −20%'. Then scroll to 'Last 36 hours'.*  
🎙 The doctor can try as many plans as she likes, in seconds: a smaller dinner dose after a sports day, a lower or later NPH, or simply a calmer evening. Each time, the twin lives the night again. This is personalising treatment on a virtual patient, exactly as the challenge describes. And notice her last thirty-six hours: only a few finger-prick dots, not a continuous line. That is the reality of most Indian families, and NightTwin is built for it.

**Manan**  
🖥 *Click '← Tonight Board', then Arjun's row.*  
🎙 Now Arjun. Fourteen, from Kochi, on glargine, with a CGM through a state programme, and he plays football most evenings. His twin goes low in about half of rehearsed nights, driven by his dinner insulin and that evening football.

**Manas**  
🖥 *Scroll to 'Night guard: replay of tonight'. Click 'Replay night' and let it draw.*  
🎙 Because Arjun has a CGM, the night guard watches every five minutes. Let us replay tonight. The red line is the guard's estimate of a low within two hours. At eleven thirty-five PM it crosses the threshold, and his father's phone rings, in Malayalam: Arjun's sugar may go low within the hour. Please check now, and give juice. The low actually began at twenty past midnight. Forty-five minutes of warning. A glass of juice, instead of an emergency.

**Manan**  
🖥 *Stay on the replay. Hover along the risk line.*  
🎙 How does it decide? It reads the last two hours of glucose and how fast it is falling, the insulin and carbohydrates still active, recent steps, and heart rate against the child's own usual level. We smooth the risk over fifteen minutes so one noisy reading never wakes a family, and we only alert while sugar is still above seventy, so the call comes before the low, not during it.

**Manan**  
🖥 *Click 'Sensor Priority'. Change 'CGMs available' from 2 to 3 and back.*  
🎙 But most families have no CGM at all. So we asked: if a programme has only a few sensors, who should get them? Each child wears one two-week trial sensor, and the twin ranks who will have the most night lows. Scarce sensors, used where they save the most.

**Manas**  
🖥 *Click 'Evidence'. Click 'More sensitive', then 'Fewer alarms', then 'Balanced (default)'.*  
🎙 Every number on this page comes from real patients, and a clinic can choose how sensitive the guard should be. More sensitive catches more lows but wakes parents more often. Fewer alarms means more sleep but less warning. That trade-off belongs to the clinician, openly, not hidden inside a model.

## 9. Evidence on real patients  ·  starts ~18:20

**Manan**  
🖥 *Slide 9 (night guard).*  
🎙 Now, the evidence. We split real patients into five groups, so every score is on people the model never saw during training. Out of three hundred and fifteen real night-time lows, ninety-seven percent were warned at least fifteen minutes ahead, with a median warning of sixty-five minutes and about point five five false alarms per night.

**Manas**  
🖥 *Slide 10 (results charts). Point to the 'External test (UK)' bars, then the forecast chart.*  
🎙 Then we tested on a different country, different devices, different people: the UK dataset. There, sixty-eight percent of night lows were warned at least fifteen minutes ahead. Performance drops on a new population, as it should, and we show it to you as it is. The model also forecasts glucose itself, beating the standard baseline at every horizon from thirty minutes to two hours, with nearly ninety-eight percent of thirty-minute forecasts in the clinically safe zones of the Clarke error grid.

**Manan**  
🖥 *Slide 11 (what did not work). Point to the orange bars.*  
🎙 And now the part we are most proud to show: what did not work. We began with a dream, to tell a mother at bedtime whether tonight would be safe. We tested that on over a thousand real nights, with simple rules, with machine learning, and with our own physiology twin. Every method was close to chance.

**Manas**  
🖥 *Optional: show the 'What we could not do' card on the Evidence page; otherwise stay on Slide 11.*  
🎙 We could have hidden that. We chose not to. Instead, we changed the design. The bedtime rehearsal is used to compare plans, never to promise that a night is safe, and the warnings come from the in-night guard, which does work. In healthcare, honesty is not a weakness of a model. It is a feature.

**Manan**  
🖥 *Slide 12 (sensor priority evidence). Point to 42% and 10%.*  
🎙 What does work without nightly CGM is ranking. Across twenty-nine real patients, one week on a sensor ranked who would have the most night lows later. The top third went low on forty-two percent of later nights; the bottom third, on ten percent. A four-to-five-thousand-rupee trial sensor can point scarce CGMs to the children who need them most.

## 10. Built for India, built to be trusted  ·  starts ~20:40

**Manas**  
🖥 *Slide 14 (built for Indian families and clinics).*  
🎙 NightTwin is built for India from the ground up. Alerts go out in the family's own language, Kannada, Hindi, Malayalam and more, as voice calls that work on any feature phone. It models the human insulin our programmes actually supply, not just expensive analogues. It understands late dinners, evening cricket and school tiffin. And every record is FHIR, ready to link with ABHA.

**Manan**  
🖥 *Switch to the browser: click 'Privacy & India'.*  
🎙 And we take children's data seriously. Under section nine of the DPDP Act, a child's data needs verifiable parental consent, and tracking or behavioural monitoring of children is not allowed. The DPDP Rules of 2025 exempt clinics when they are providing health services to the child. So NightTwin is deployed by the clinic, as the data fiduciary, with parental consent recorded. No advertising. No analytics on children. NightTwin is decision support, not a diagnosis, and a real deployment would follow CDSCO's pathway for medical-device software after a supervised pilot.

## 11. Impact, roadmap and honest limits  ·  starts ~22:00

**Manas**  
🖥 *Slide 16 (impact and how it scales).*  
🎙 What does this mean for a family? About an hour of warning before a night-time low, as a phone call. For families without a CGM, a fairer chance at one. And zero licence cost: NightTwin is open source under Apache 2.0, so any state programme or NGO can use it freely. Our path: a pilot in one paediatric diabetes clinic, validation on Indian children, and then the same twin for adults with type 2 diabetes on insulin, where night lows are just as dangerous. And if it works, its most important result will not be a number on a chart. It will be a mother who finally sleeps through the night.

**Manan**  
🖥 *Slide 17 (limitations).*  
🎙 We are also clear about our limits. Our models were trained on adults in Spain and tested in the UK, not on Indian children, so an Indian pilot is essential. Our demo children are synthetic, our translations need native review, and NightTwin is not yet a medical device. Each of these has a clear next step, and we are ready to take it.

## 12. Everything in the repository  ·  starts ~23:20

**Manan**  
🖥 *Show the GitHub repo page: https://github.com/MananGilhotra/TwinPulse_NewtonSchoolOfTechnology_RishihoodUniversity  Scroll through the README.*  
🎙 Everything you have seen is open, in our public GitHub repository. The readme has our team and college, the project title, the problem and use case, the technical stack and models, the open-source licence, the architecture diagram, the presentation, this video, and a live demo link. Under the hood: Python with NumPy, SciPy and numba for the physiology twin, LightGBM and scikit-learn for the guard, FastAPI, and a React dashboard, with the twin also ported to JavaScript so it runs in your browser. One command, run dot s h, sets it all up, and every result can be regenerated from the raw open data.

## 13. Closing  ·  starts ~24:00

**Manas**  
🖥 *Slide 18 (closing). Look at the camera if you are on video. Slow down.*  
🎙 Let us go back to Raichur, to two forty-seven in the morning. Tonight, Ananya's twin has already lived this night, five hundred times. Her doctor saw the danger at nine PM, and fixed it with a glass of milk and a change in timing. Tonight, Lakshmi's alarm does not need to ring.

**Manas**  
🖥 *End card. Pause one beat before the last line.*  
🎙 NASA rehearsed a rescue on a twin to bring three astronauts home. We built NightTwin to bring every child safely to morning. Tonight, somewhere in India, a two AM alarm will ring. We built NightTwin so that one day, it won't have to. Let the twin face the night first. We are Team TwinPulse. Thank you.

## Coverage checklist

| Submission / brief item | Where in the video |
|---|---|
| Team details and college | Section 3, Section 12 |
| Project title | Section 3 |
| Problem statement and healthcare use case | Sections 2, 4, 5 |
| Technical stack, AI/ML models | Sections 7, 12 |
| Static EHR stream incl. genetic markers + dynamic wearable stream | Section 6, demo (health record, timeline) |
| Predicts an adverse event in advance | Section 8 (night guard replay, 45 min warning), Section 9 |
| Doctor-facing dashboard | Section 8 |
| Open/synthetic data only | Section 6 |
| Architecture | Section 7 |
| Presentation, results and outcome | Sections 9–11 |
| Open-source licence | Sections 11, 12 |
