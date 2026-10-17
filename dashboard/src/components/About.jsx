import Icon from './Icon.jsx'
import React from 'react'

export default function About() {
  return (
    <div className="about">
      <div className="eyebrow-dark">Built to be trusted</div>
      <h1>Privacy, safety and India</h1>
      <div className="grid2">
        <div className="card">
          <div className="card-title">Children's data (DPDP Act 2023)</div>
          <ul>
            <li>Section 9 requires verifiable parental consent and bars tracking or behavioural monitoring of children.</li>
            <li>The DPDP Rules 2025 (Fourth Schedule) exempt clinical establishments and healthcare professionals when processing is limited to providing health services to the child.</li>
            <li>So NightTwin is deployed <b>by the clinic</b>, which is the data fiduciary. We still record parental consent, and there is no advertising or analytics on children's data.</li>
          </ul>
        </div>
        <div className="card">
          <div className="card-title">Doctor stays in charge</div>
          <ul>
            <li>The twin shows simulated outcomes. Only the doctor changes a prescription.</li>
            <li>Families receive only doctor-approved actions, in their own language, by WhatsApp or voice call.</li>
            <li>Decision support, not diagnosis. A real deployment would follow India's CDSCO medical device software pathway.</li>
          </ul>
        </div>
        <div className="card">
          <div className="card-title">Built for Indian care</div>
          <ul>
            <li>Health records in FHIR R4 (ABDM's standard), ready for ABHA linkage.</li>
            <li>Models the human NPH and Regular insulin many state programmes supply, not just analogue insulin.</li>
            <li>Indian routines: late dinners, evening play, school tiffin.</li>
            <li>Families without CGM: finger-pricks + a basic band, with a 14-day trial sensor to rank who needs continuous monitoring most.</li>
          </ul>
        </div>
        <div className="card">
          <div className="card-title">Honest limits</div>
          <ul>
            <li>Models were trained on adults in Spain and validated on adults in the UK, not on Indian children. The next step is a pilot with an Indian paediatric clinic.</li>
            <li>Demo children are synthetic.</li>
            <li>Bedtime-only prediction is weak (see Evidence).</li>
            <li>Translations are drafts for native-speaker review.</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
