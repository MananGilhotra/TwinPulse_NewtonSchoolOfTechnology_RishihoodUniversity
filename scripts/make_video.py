"""Build the narrated walkthrough video (docs/video/NightTwin_Walkthrough.mp4, about 22 minutes).

Needs: macOS `say` (voices Tara and Aman, English India), ffmpeg, pdftoppm, Google Chrome,
and the app running on http://localhost:8000 (./run.sh). Slides come from docs/TwinPulse_Presentation.pdf.
The narration text below is also the team's script if you record with your own voices.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "video", "NightTwin_Walkthrough.mp4")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
APP = os.environ.get("APP_URL", "http://localhost:8000")
VOICES = {"T": "Tara", "A": "Aman"}
RATE = "162"

# Dashboard frames: (name, route, y-offset of the 1080-px crop in a 1920-px-wide capture)
FRAMES = {
    "overview_top": ("overview", 0), "overview_proof": ("overview", 950), "board": ("board", 0),
    "ananya_top": ("patient/TP-001", 0), "ananya_record": ("patient/TP-001", 740),
    "ananya_plan": ("patient/TP-001?snack=15&shift=90&approve=1", 880), "ananya_snack": ("patient/TP-001?snack=15", 880),
    "ananya_timeline": ("patient/TP-001", 1880), "arjun_top": ("patient/TP-002", 0), "arjun_guard": ("patient/TP-002", 1300),
    "sensors": ("sensors", 0), "evidence_top": ("evidence", 0), "evidence_honest": ("evidence", 900), "privacy": ("about", 0),
}

# (image, voice, narration). Images: "slide-NN" (deck page) or a FRAMES key.
SCENES = [
    ("slide-01", "T", "Hello, and thank you for watching. We are Team TwinPulse, from Newton School of Technology, Rishihood University. "
     "This is our submission to the Happiest Health Digital Twin Challenge, 2026. Our project is called NightTwin. "
     "In one sentence: before a child with type 1 diabetes goes to sleep, her digital twin lives the night first, five hundred times, "
     "so that her doctor can see the danger and fix it, before it happens to the real child."),
    ("slide-01", "A", "Over the next twenty minutes we will cover the problem, why it matters so much in India, how our digital twin works, "
     "a live demonstration of the doctor's dashboard, our results on real patients, including what did not work, and finally privacy, impact, and our next steps. "
     "Everything you will see is open source and available in our public GitHub repository, along with a live demo you can open in your browser."),
    ("slide-02", "T", "Let us begin at two forty seven in the morning, in Raichur, in Karnataka. This is a composite story, built from what parents of children with type 1 diabetes describe. "
     "Lakshmi's daughter, Ananya, is nine years old. Every night for three years, Lakshmi has set an alarm to wake up and prick her daughter's finger. "
     "She told us, in effect: I never know which night is the dangerous one."),
    ("slide-02", "A", "Her fear is well founded. In the landmark D C C T trial, fifty five percent of severe low blood sugar episodes happened during sleep. "
     "A sudden overnight death syndrome, known as dead in bed, is thought to follow severe night time lows, and is linked to around five to six percent of deaths in people with type 1 diabetes under the age of forty. "
     "Yet a low that is caught one hour early can be treated with nothing more than a glass of juice."),
    ("slide-03", "T", "Why India? India has more children and teenagers with type 1 diabetes than any other country: about two point two nine lakh, according to the I D F Diabetes Atlas of 2021. "
     "The 2025 Atlas counts about nine point four lakh Indians of all ages living with type 1 diabetes."),
    ("slide-03", "A", "A continuous glucose monitor, a C G M, with low alarms, costs between four thousand and four thousand seven hundred rupees for every fourteen day sensor. "
     "That is more than one lakh rupees a year, which most families simply cannot afford. And many state programmes supply human insulin. "
     "The long acting part of that insulin, called N P H, peaks between one and four in the morning, exactly when the whole family is asleep. "
     "So families choose between a lakh of rupees a year and a two A M alarm. And out of fear of lows, many keep sugars high, which damages the eyes and kidneys over time."),
    ("slide-04", "T", "Our answer is NightTwin, a digital twin that does three things. First, it learns the child. A personal glucose and insulin model is fitted to each child, from that child's own nights: their insulin, meals, play, and glucose readings, together with their health record. "
     "Second, it lives tonight first. At nine P M, the twin simulates the coming night five hundred times. The doctor sees which children are at risk, at what time, and why, and can rehearse a fix on the twin before prescribing it. "
     "Third, it guards the real night. For children who do have a C G M, a model trained on real patients warns roughly an hour before a low, and calls the parent in their own language. "
     "Throughout, the doctor stays in charge. The twin suggests; the doctor decides."),
    ("slide-05", "A", "The challenge asks for the fusion of two data streams, and this is how we do it. The static stream is the electronic health record, stored in the F H I R R4 standard that India's Ayushman Bharat Digital Mission uses. "
     "It includes age and weight, H b A 1 c, haemoglobin, the insulin regimen and daily dose, the history of severe lows, whether the child can still feel a low coming, "
     "and genetic markers: the H L A risk genotype and islet autoantibodies. The dynamic stream comes from wearables: glucose every five minutes from a C G M, or a few finger pricks, insulin doses, meals, and steps and heart rate from a simple fitness band."),
    ("slide-05", "T", "For training and testing we followed the sandbox rules strictly. We used two open datasets of real people with type 1 diabetes, both under a Creative Commons licence. "
     "H U P A U C M, from Spain, has twenty five people with FreeStyle Libre C G M and Fitbit data. T 1 D U O M, from the United Kingdom, has around three months per person with different devices, and we use it only as an external test. "
     "The twelve Indian children you will see in the demo are synthetic. We created them to show the method, and we never use them to claim accuracy."),
    ("slide-06", "A", "Here is the architecture, from left to right. Data comes in from the health record and the wearables. In the preparation layer we build a unified five minute timeline, compute insulin on board and carbohydrates on board, "
     "and infer meals that were never logged, using the clinical five hundred rule. We also personalise each twin on the child's past nights. "
     "Then come three models. Model A is the physiology twin. Model B is the night guard, built with Light G B M. Model C is sensor priority. "
     "A Fast A P I service serves the doctor's dashboard and the family channel. Underneath everything sits a trust layer: parental consent, the clinic as the data fiduciary, doctor in the loop, and published validation."),
    ("slide-07", "T", "What makes this a true digital twin, and not just a classifier, is model A. It is a physiological model of glucose and insulin, based on the Bergman minimal model, which has been used in diabetes research for over forty years. "
     "We extended it with depots for rapid acting insulin and for long acting insulin, either N P H or glargine, with absorption of carbohydrates from the gut, and with an exercise effect that lingers for about four hours. "
     "That last part matters: an evening cricket match can cause a low at two in the morning."),
    ("slide-07", "A", "Each child's twin is fitted on that child's own previous nights, using least squares, with insulin sensitivity anchored to the clinical eighteen hundred rule that doctors already use. "
     "At bedtime the twin takes in today's readings, then runs freely from eleven P M to seven thirty in the morning, five hundred times, with realistic variation in sensitivity and noise. "
     "The result is not a single guess, but a spread of possible nights: the probability of a low, its likely time, and how deep it could go. In this example, Ananya's synthetic twin goes low in fifty eight percent of rehearsed nights. With a bedtime snack and N P H moved ninety minutes later, that drops to fourteen percent."),
    ("overview_top", "T", "Now let us see it working. This is the NightTwin dashboard, designed for a paediatric diabetes clinic, for example at a district hospital or in a state programme. "
     "The overview page states our idea, the scale of the problem, and the three steps. Everything here runs on the same models we just described."),
    ("overview_proof", "A", "Further down, the overview shows our headline evidence, all measured on real patients the model never saw during training: ninety seven percent of night time lows warned at least fifteen minutes ahead, "
     "a median warning of sixty five minutes, about half a false alarm per night, and a four point three times difference in later night lows between the children a trial sensor flags as highest risk and lowest risk. "
     "Below that is the data fusion strip: health record plus wearables, into the twin, and out come risk, explanation, a rehearsed plan, and an alert."),
    ("board", "T", "It is nine P M. This is the Tonight Board. Every enrolled child's twin has already lived tonight five hundred times, and the children are ranked by the share of those nights that go low. "
     "Ananya, Aman, Arjun and Sahil are high risk tonight, and the board suggests calling their families before bed. For each child you can see the likely time of a low, the last glucose reading, whether the family uses a C G M or finger pricks, the insulin regimen, and how much night time they spent low over the last fourteen days. "
     "Filters let the diabetes educator focus on the children who need attention."),
    ("ananya_top", "A", "Let us open Ananya's twin. She is nine, from Raichur, on N P H and regular human insulin from a state programme, and her family can afford only three test strips a day. "
     "At the top right, the headline: fifty eight percent of her five hundred rehearsed nights go low, most often around half past midnight. "
     "The main chart shows tonight, rehearsed five hundred times. The shaded band is the spread of simulated nights, and the dashed red line is seventy milligrams per decilitre, the threshold for a low."),
    ("ananya_top", "T", "On the right, the twin explains why tonight is risky. It removes one factor at a time and lives the night again. Removing part of the dinner insulin dose lowers the risk the most. "
     "The dinner time N P H, which peaks in the early morning hours, and this evening's play also contribute. This is an explanation a doctor can act on, because each factor is something that can actually be changed."),
    ("ananya_record", "A", "Below that is Ananya's health record, read from her F H I R bundle: H b A 1 c, haemoglobin, weight, daily insulin, one severe low in the past year, impaired awareness of lows, her H L A genotype and autoantibodies, and the three strips a day her family can afford. "
     "If haemoglobin is low, the dashboard warns that anaemia can make H b A 1 c read falsely high, a common issue in India. The consent line shows that a parent's verifiable consent is on file. "
     "There is also a fourteen day summary, using the international consensus targets: time in range, time below seventy, and time below fifty four."),
    ("ananya_snack", "T", "Now the most important part: rehearsing a plan on the twin. The doctor can try a bedtime snack, a smaller dinner dose, a smaller N P H dose, or moving N P H later, and the twin re-lives the night for each option. "
     "Here we try only a fifteen gram bedtime snack, a glass of milk and two biscuits. The green band shows the night with the plan. The risk falls, but not all the way."),
    ("ananya_plan", "A", "Now we add the standard clinical fix for night lows on human insulin: moving the evening N P H from dinner time to bedtime, ninety minutes later, so its peak shifts past three in the morning. "
     "With the snack and the N P H change together, the risk of a low tonight falls from fifty eight percent to around fourteen percent. "
     "When the doctor is satisfied, they press approve, and the family receives only the approved action, here as a message in Kannada with an English line below. Families with a feature phone receive it as a voice call."),
    ("ananya_timeline", "T", "At the bottom is the last thirty six hours for Ananya: her finger prick readings, meals, insulin doses, and steps from her band. "
     "Notice that because she has no C G M, the twin sees only a few glucose readings a day. That is exactly the situation of most Indian families, and the twin is built to work with it."),
    ("arjun_top", "A", "Now Arjun. He is fourteen, from Kochi, on glargine and rapid acting insulin, and he has a C G M through a state programme. He plays football most evenings. "
     "His twin goes low in about half of rehearsed nights, and the explanation shows that his dinner insulin and his evening football are the main drivers."),
    ("arjun_guard", "T", "Because Arjun has a C G M, the night guard runs every five minutes through the night. This is a replay of tonight. The black line is his glucose. The red shaded line is the guard's estimated risk of a low within the next two hours. "
     "At eleven thirty five P M, the risk crosses the alert threshold, and his father receives a voice call in Malayalam: Arjun's sugar may go low within the hour, please check now and give juice. "
     "The low actually began at twenty past midnight. That is forty five minutes of warning, enough for a glass of juice instead of an emergency."),
    ("sensors", "A", "Most families have no C G M at all, so we added Sensor Priority. Each finger prick child wears one fourteen day trial sensor. The twin ranks who will have the most night lows, and if a programme has only two C G Ms to give, it shows which two children should receive them. "
     "This turns a scarce resource into the greatest possible safety, and it is based on a result we measured on real patients, which we will show next."),
    ("slide-09", "T", "Let us now look at the evidence. The night guard was trained and tested on real patients. We split the patients into five groups, so that every score is on people the model never saw. "
     "Out of three hundred and fifteen night time lows, ninety seven percent were warned at least fifteen minutes ahead. The median warning was sixty five minutes, and there were about zero point five five false alarms per night."),
    ("slide-10", "A", "We then tested on a completely separate dataset from the United Kingdom, with different devices and different people. There, sixty eight percent of night lows were warned at least fifteen minutes ahead, with a median warning of sixty two minutes. "
     "Performance drops, as you would expect on a new population, and we report that honestly. As an area under the curve, the guard scores zero point nine three for a low within sixty minutes, and zero point eight eight within two hours. "
     "Our glucose forecasts also beat the standard baseline at every horizon: eighteen milligrams per decilitre error at thirty minutes, compared with twenty one for assuming no change, and forty four at two hours, compared with fifty two."),
    ("evidence_top", "T", "The same numbers live inside the dashboard, on the Evidence page. A clinic can choose how sensitive the guard should be. A more sensitive setting catches more lows but wakes parents more often; a stricter setting means fewer alarms. "
     "We think this trade off should be a clinical choice, made openly, rather than hidden inside the model."),
    ("slide-11", "A", "Now, what did not work. When we started, we hoped to tell a mother at bedtime whether tonight would be safe, using only information available at eleven P M. "
     "We tested this on more than a thousand real nights, with a simple glucose rule, with machine learning on all signals, and with our physiology twin. Every method was close to chance, with an area under the curve between zero point five five and zero point six three. "
     "We also found that insulin, meal, step and heart rate features added only about zero point zero one over glucose alone in these datasets."),
    ("evidence_honest", "T", "So we changed the design. The bedtime rehearsal is used to compare plans, to see what makes tonight safer, and not to promise that a night is safe. Warnings come from the in night guard, which does work. "
     "We believe showing this openly is part of doing responsible health A I, and we hope the jury values that."),
    ("slide-12", "A", "What does work without nightly C G M is ranking. Across twenty nine real patients, the time spent below range in the first week on a sensor ranked who would go on to have the most night lows, with a Spearman correlation of zero point six three. "
     "Children in the top third had a low on forty two percent of later nights, compared with ten percent in the bottom third. One trial sensor, costing four to five thousand rupees, can therefore direct a programme's scarce C G Ms to the children who need them most."),
    ("slide-13", "T", "To summarise the product: the doctor's dashboard has the Tonight Board, the twin view with explanations and the health record, the rehearse and approve workflow, the night guard replay, sensor priority, and the evidence page. "
     "It runs with a single command on any laptop, and there is also a live version on GitHub Pages, where the twin runs directly in your browser."),
    ("slide-14", "A", "NightTwin is built for Indian families and clinics. Alerts go out in the family's language, such as Kannada, Hindi or Malayalam, and as voice calls for feature phones. "
     "The twin models the human N P H, regular and premixed insulin that many programmes supply, not only expensive analogues. It understands Indian routines such as late dinners, evening cricket and school tiffin. And all records use F H I R, ready to link with the A B H A health I D."),
    ("privacy", "T", "Children's health data needs special care. Under section nine of India's Digital Personal Data Protection Act, processing a child's data needs verifiable parental consent, and tracking or behavioural monitoring of children is not allowed. "
     "The D P D P Rules of 2025, in the fourth schedule, exempt clinical establishments and healthcare professionals when the processing is limited to providing health services to the child. "
     "So NightTwin is deployed by the clinic, which is the data fiduciary, and we still record parental consent. There is no advertising and no analytics on children's data."),
    ("slide-15", "A", "The doctor stays in the loop at every step. The twin only shows simulated outcomes; only the doctor changes a prescription. NightTwin is decision support, not a diagnosis. "
     "A real deployment would follow the Central Drugs Standard Control Organisation's pathway for medical device software, after a supervised clinical pilot."),
    ("slide-16", "T", "What is the impact? For families with a C G M, about an hour of warning before a night time low, delivered as a voice call. For everyone else, smarter use of scarce sensors. And zero licence cost, because NightTwin is open source under the Apache two point zero licence, so state programmes and N G Os can use it freely. "
     "Our rollout path is: first, a pilot in one paediatric diabetes clinic with families already in a state programme. Second, recalibrating and validating on Indian children's data, measuring night lows, parents' sleep and false alarms. Third, extending the same twin to adults with type 2 diabetes who use insulin or sulfonylureas."),
    ("slide-17", "A", "We are also clear about our limitations. Our models were trained on adults in Spain and tested on adults in the United Kingdom, not on Indian children, so an Indian pilot is essential. "
     "The demo children are synthetic. Bedtime only prediction is weak, as we showed. Our translations are drafts that need review by native speakers. And this is not yet a medical device."),
    ("slide-06", "T", "Before we close, a quick technical summary for the panel. The code is in Python, with Num Py, Sci Py, numba for the fast simulator, Light G B M and scikit learn for the guard, and Fast A P I for the service. "
     "The dashboard is React, with Recharts. Every result can be regenerated from the raw open data with the scripts in our repository, and there is an automated test suite that checks the A P I, the twin's behaviour, and the guard."),
    ("slide-18", "A", "In 1970, NASA saved the crew of Apollo 13 by rehearsing the rescue on a twin of the spacecraft on the ground, before trying it for real. NightTwin does the same for a child's night. "
     "Let the twin face the night first, so that a mother can sleep, and a child wakes up safe."),
    ("slide-18", "T", "Thank you for watching. We are Team TwinPulse, from Newton School of Technology, Rishihood University. "
     "Our code, data sources, results, architecture diagram, presentation and live demo are all linked from our public GitHub repository. We look forward to your questions."),
]


def run(cmd, **kw):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **kw)


def capture_frames(tmp):
    raw = {}
    for name, (route, y) in FRAMES.items():
        if route not in raw:
            path = os.path.join(tmp, f"raw_{len(raw)}.png")
            run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1280,3200",
                 "--force-device-scale-factor=1.5", "--virtual-time-budget=12000", f"--screenshot={path}", f"{APP}/#{route}"])
            raw[route] = path
        im = Image.open(raw[route]).convert("RGB")
        im.crop((0, y, 1920, y + 1080)).save(os.path.join(tmp, f"{name}.png"))


def main():
    for tool in ("say", "ffmpeg", "pdftoppm"):
        if not shutil.which(tool):
            sys.exit(f"missing {tool}")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="nighttwin_video_")
    run(["pdftoppm", "-png", "-scale-to-x", "1920", "-scale-to-y", "1080",
         os.path.join(ROOT, "docs", "TwinPulse_Presentation.pdf"), os.path.join(tmp, "slide")])
    capture_frames(tmp)
    parts = []
    total_words = 0
    for i, (img, voice, text) in enumerate(SCENES):
        total_words += len(text.split())
        aiff = os.path.join(tmp, f"a{i:02d}.aiff")
        run(["say", "-v", VOICES[voice], "-r", RATE, "-o", aiff, text])
        seg = os.path.join(tmp, f"s{i:02d}.mp4")
        run(["ffmpeg", "-y", "-loop", "1", "-framerate", "2", "-i", os.path.join(tmp, f"{img}.png"), "-i", aiff,
             "-af", "apad=pad_dur=0.8", "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p", "-r", "2",
             "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-shortest", seg])
        parts.append(seg)
        print(f"scene {i + 1}/{len(SCENES)}", flush=True)
    lst = os.path.join(tmp, "list.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{p}'\n" for p in parts)
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags", "+faststart", OUT])
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", OUT],
                         capture_output=True, text=True).stdout.strip()
    print(f"{OUT}  {float(dur) / 60:.1f} min, {total_words} words")


if __name__ == "__main__":
    main()
