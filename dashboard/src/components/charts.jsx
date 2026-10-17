import React from 'react'
import {
  Area, Bar, CartesianGrid, ComposedChart, Line, ReferenceArea, ReferenceLine, ResponsiveContainer,
  Scatter, Tooltip, XAxis, YAxis,
} from 'recharts'
import { hhmm } from '../api.js'

const C = {
  band: '#6366f1', alt: '#10b981', low: '#ef4444', grid: '#e5e7eb', text: '#6b7280', target: '#ecfdf5',
  glucose: '#111827', carbs: '#f59e0b', insulin: '#3b82f6', steps: '#a78bfa', risk: '#ef4444',
}

const tickTime = (t) => (t ? hhmm(t) : '')

export function FanChart({ band, alt, height = 300 }) {
  const byT = {}
  band.forEach((b) => (byT[b.t] = { t: b.t, r95: [b.p5, b.p95], r75: [b.p25, b.p75], med: b.p50 }))
  if (alt) alt.forEach((b) => byT[b.t] && Object.assign(byT[b.t], { a95: [b.p5, b.p95], amed: b.p50 }))
  const data = Object.values(byT)
  return (
    <ResponsiveContainer width="100%" height={height}>
      <ComposedChart data={data} margin={{ top: 10, right: 16, bottom: 0, left: -10 }}>
        <CartesianGrid stroke={C.grid} vertical={false} />
        <ReferenceArea y1={70} y2={180} fill={C.target} fillOpacity={0.6} />
        <XAxis dataKey="t" tickFormatter={tickTime} minTickGap={40} tick={{ fill: C.text, fontSize: 12 }} />
        <YAxis domain={[40, 300]} tick={{ fill: C.text, fontSize: 12 }} />
        <ReferenceLine y={70} stroke={C.low} strokeDasharray="4 4" label={{ value: '70 mg/dL', fill: C.low, fontSize: 11, position: 'insideBottomRight' }} />
        <ReferenceLine x={data.find((d) => d.t.endsWith('23:00'))?.t} stroke="#9ca3af" label={{ value: 'bedtime', fill: C.text, fontSize: 11, position: 'insideTopLeft' }} />
        <Tooltip formatter={(v) => (Array.isArray(v) ? `${Math.round(v[0])}–${Math.round(v[1])}` : Math.round(v))} labelFormatter={tickTime} />
        <Area dataKey="r95" stroke="none" fill={C.band} fillOpacity={alt ? 0.08 : 0.15} name="90% of nights" isAnimationActive={false} />
        <Area dataKey="r75" stroke="none" fill={C.band} fillOpacity={alt ? 0.12 : 0.3} name="half of nights" isAnimationActive={false} />
        <Line dataKey="med" stroke={C.band} dot={false} strokeWidth={2} name="typical night" strokeDasharray={alt ? '5 4' : ''} isAnimationActive={false} />
        {alt && <Area dataKey="a95" stroke="none" fill={C.alt} fillOpacity={0.22} name="with plan (90%)" isAnimationActive={false} />}
        {alt && <Line dataKey="amed" stroke={C.alt} dot={false} strokeWidth={2.5} name="with plan" isAnimationActive={false} />}
      </ComposedChart>
    </ResponsiveContainer>
  )
}

export function Timeline({ series, mode }) {
  const data = series.map((s) => ({ ...s, gdot: mode === 'fingerstick' ? s.g : null, gline: mode === 'cgm' ? s.g : null }))
  return (
    <ResponsiveContainer width="100%" height={260}>
      <ComposedChart data={data} margin={{ top: 10, right: 16, bottom: 0, left: -10 }}>
        <CartesianGrid stroke={C.grid} vertical={false} />
        <ReferenceArea yAxisId="g" y1={70} y2={180} fill={C.target} fillOpacity={0.6} />
        <XAxis dataKey="t" tickFormatter={tickTime} minTickGap={50} tick={{ fill: C.text, fontSize: 12 }} />
        <YAxis yAxisId="g" domain={[40, 350]} tick={{ fill: C.text, fontSize: 12 }} />
        <YAxis yAxisId="s" orientation="right" hide domain={[0, 2500]} />
        <Tooltip labelFormatter={tickTime} />
        <Bar yAxisId="s" dataKey="steps" fill={C.steps} fillOpacity={0.35} name="steps / 5 min" isAnimationActive={false} />
        <ReferenceLine yAxisId="g" y={70} stroke={C.low} strokeDasharray="4 4" />
        {mode === 'cgm' && <Line yAxisId="g" dataKey="gline" stroke={C.glucose} dot={false} strokeWidth={1.8} name="CGM glucose" isAnimationActive={false} connectNulls />}
        {mode === 'fingerstick' && <Scatter yAxisId="g" dataKey="gdot" fill={C.glucose} name="finger-prick" isAnimationActive={false} />}
        <Scatter yAxisId="g" dataKey={(d) => (d.carbs ? 330 : null)} fill={C.carbs} shape="triangle" name="meal" isAnimationActive={false} />
        <Scatter yAxisId="g" dataKey={(d) => (d.bolus || d.long ? 50 : null)} fill={C.insulin} shape="diamond" name="insulin" isAnimationActive={false} />
      </ComposedChart>
    </ResponsiveContainer>
  )
}

export function GuardChart({ series, upTo, threshold, alertAt, onsetAt }) {
  const data = series.map((s, i) => (i <= upTo ? s : { t: s.t }))
  const alertT = series.find((s) => s.t.endsWith(alertAt))?.t
  const onsetT = series.find((s) => s.t.endsWith(onsetAt))?.t
  return (
    <ResponsiveContainer width="100%" height={280}>
      <ComposedChart data={data} margin={{ top: 10, right: 16, bottom: 0, left: -10 }}>
        <CartesianGrid stroke={C.grid} vertical={false} />
        <ReferenceArea yAxisId="g" y1={70} y2={180} fill={C.target} fillOpacity={0.6} />
        <XAxis dataKey="t" tickFormatter={tickTime} minTickGap={40} tick={{ fill: C.text, fontSize: 12 }} />
        <YAxis yAxisId="g" domain={[40, 250]} tick={{ fill: C.text, fontSize: 12 }} />
        <YAxis yAxisId="p" orientation="right" domain={[0, 1]} tickFormatter={(v) => `${v * 100}%`} tick={{ fill: C.risk, fontSize: 12 }} />
        <Tooltip labelFormatter={tickTime} formatter={(v, n) => (n.includes('risk') ? `${Math.round(v * 100)}%` : Math.round(v))} />
        <ReferenceLine yAxisId="g" y={70} stroke={C.low} strokeDasharray="4 4" />
        <ReferenceLine yAxisId="p" y={threshold} stroke={C.risk} strokeOpacity={0.4} strokeDasharray="2 4" />
        {alertT && series.findIndex((s) => s.t === alertT) <= upTo && (
          <ReferenceLine yAxisId="g" x={alertT} stroke={C.risk} strokeWidth={2} label={{ value: `alert ${alertAt}`, fill: C.risk, fontSize: 12, position: 'insideTopRight' }} />
        )}
        {onsetT && series.findIndex((s) => s.t === onsetT) <= upTo && (
          <ReferenceLine yAxisId="g" x={onsetT} stroke="#111827" strokeDasharray="3 3" label={{ value: `low ${onsetAt}`, fill: '#111827', fontSize: 12, position: 'insideBottomRight' }} />
        )}
        <Area yAxisId="p" dataKey="p120" stroke={C.risk} fill={C.risk} fillOpacity={0.12} name="risk of a low in 2 h" isAnimationActive={false} />
        <Line yAxisId="g" dataKey="cgm" stroke={C.glucose} dot={false} strokeWidth={2} name="CGM glucose" isAnimationActive={false} />
      </ComposedChart>
    </ResponsiveContainer>
  )
}

export function HourBars({ rows }) {
  return (
    <ResponsiveContainer width="100%" height={160}>
      <ComposedChart data={rows} margin={{ top: 6, right: 8, bottom: 0, left: -20 }}>
        <XAxis dataKey="hour" tick={{ fill: C.text, fontSize: 11 }} interval={2} tickFormatter={(h) => `${h}h`} />
        <YAxis tickFormatter={(v) => `${Math.round(v * 100)}%`} tick={{ fill: C.text, fontSize: 11 }} />
        <Tooltip formatter={(v) => `${(v * 100).toFixed(1)}% of time below 70`} labelFormatter={(h) => `${h}:00`} />
        <Bar dataKey="tbr" fill={C.low} radius={[3, 3, 0, 0]} isAnimationActive={false} />
      </ComposedChart>
    </ResponsiveContainer>
  )
}
