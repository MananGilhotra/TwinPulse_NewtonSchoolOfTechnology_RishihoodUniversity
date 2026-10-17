import React, { useId } from 'react'

// NightTwin mark: a crescent moon (the night) crossed by a pulse line (the twin keeping watch).
export default function Logo({ size = 36 }) {
  const id = useId().replace(/:/g, '')
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" role="img" aria-label="NightTwin logo">
      <defs>
        <linearGradient id={`bg${id}`} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#4f46e5" />
          <stop offset="1" stopColor="#1e1b4b" />
        </linearGradient>
        <linearGradient id={`moon${id}`} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#fde68a" />
          <stop offset="1" stopColor="#f59e0b" />
        </linearGradient>
        <mask id={`cut${id}`}>
          <rect width="64" height="64" fill="#fff" />
          <circle cx="40" cy="23" r="15" fill="#000" />
        </mask>
      </defs>
      <rect width="64" height="64" rx="16" fill={`url(#bg${id})`} />
      <circle cx="30" cy="31" r="17" fill={`url(#moon${id})`} mask={`url(#cut${id})`} />
      <circle cx="47" cy="15" r="1.6" fill="#c7d2fe" />
      <circle cx="53" cy="24" r="1.1" fill="#c7d2fe" />
      <path d="M7 41 H22 L26 33 L31 49 L36 36 L39 41 H57" fill="none" stroke="#fff" strokeWidth="3.2"
        strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}
