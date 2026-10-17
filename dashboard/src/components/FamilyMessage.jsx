import React from 'react'

// Draft translations: have native speakers review before any real use.
const NIGHT = {
  Kannada: (n) => `ಎಚ್ಚರಿಕೆ: ${n} ಅವರ ಸಕ್ಕರೆ ಮುಂದಿನ ಒಂದು ಗಂಟೆಯಲ್ಲಿ ಕಡಿಮೆಯಾಗಬಹುದು. ದಯವಿಟ್ಟು ಈಗ ಪರೀಕ್ಷಿಸಿ ಮತ್ತು ಜ್ಯೂಸ್ ಕೊಡಿ.`,
  Hindi: (n) => `चेतावनी: ${n} की शुगर अगले एक घंटे में कम हो सकती है। कृपया अभी जाँच करें और जूस दें।`,
  Malayalam: (n) => `മുന്നറിയിപ്പ്: ${n}-ന്റെ ഷുഗർ അടുത്ത ഒരു മണിക്കൂറിൽ കുറയാം. ദയവായി ഇപ്പോൾ പരിശോധിച്ച് ജ്യൂസ് കൊടുക്കുക.`,
}
const PLAN = {
  Kannada: (n) => `ಡಾಕ್ಟರ್ ಸಂದೇಶ: ಇಂದು ರಾತ್ರಿ ${n} ಮಲಗುವ ಮುನ್ನ ಒಂದು ಲೋಟ ಹಾಲು ಮತ್ತು 2 ಬಿಸ್ಕತ್ತು ಕೊಡಿ.`,
  Hindi: (n) => `डॉक्टर का संदेश: आज रात सोने से पहले ${n} को एक गिलास दूध और 2 बिस्किट दें।`,
  Malayalam: (n) => `ഡോക്ടറുടെ സന്ദേശം: ഇന്ന് രാത്രി ഉറങ്ങുന്നതിന് മുമ്പ് ${n}-ന് ഒരു ഗ്ലാസ് പാലും 2 ബിസ്കറ്റും കൊടുക്കുക.`,
}

function planEnglish(n, plan) {
  const parts = []
  if (plan.snack_g) parts.push(`give ${n} a bedtime snack (${plan.snack_g} g, e.g. a glass of milk and 2 biscuits)`)
  if (plan.long_acting_shift_min) parts.push(`give the evening long-acting insulin ${plan.long_acting_shift_min} minutes later than usual`)
  if (plan.long_acting_pct) parts.push(`reduce the evening long-acting insulin by ${-plan.long_acting_pct}%`)
  if (plan.dinner_rapid_pct) parts.push(`reduce the dinner insulin by ${-plan.dinner_rapid_pct}%`)
  if (plan.skip_play) parts.push('keep the evening calm')
  return `Doctor's plan for tonight: ${parts.join('; ') || 'no change'}.`
}

export default function FamilyMessage({ meta, kind, plan }) {
  const lang = meta.language
  const local = (kind === 'night' ? NIGHT : PLAN)[lang]
  const english = kind === 'night'
    ? `Alert: ${meta.name}'s sugar may go low within the hour. Please check now and give juice.`
    : planEnglish(meta.name, plan)
  const call = meta.phone === 'feature phone' || kind === 'night'
  return (
    <div className="phone">
      <div className="phone-top">{call ? '📞 Incoming voice call · NightTwin' : '💬 WhatsApp · NightTwin'}</div>
      <div className="phone-to">To {meta.parent} · {meta.phone}</div>
      {local && <div className={`phone-msg lang-${lang}`}>{local(meta.name)}</div>}
      <div className="phone-msg en">{english}</div>
      {call && <div className="muted small">Voice call in {lang} works on any phone, including feature phones.</div>}
    </div>
  )
}
