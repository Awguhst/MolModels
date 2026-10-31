-- Small, original inline SVG icons (16px grid, stroke = currentColor).
local function svg(paths, extra)
  return '<svg class="mm-callout-icon' .. (extra or '') .. '" viewBox="0 0 16 16" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">' .. paths .. '</svg>'
end

local M = {}

M.icons = {
  note       = svg('<circle cx="8" cy="8" r="6.25"/><path d="M8 7.2v4"/><circle cx="8" cy="4.9" r=".6" fill="currentColor" stroke="none"/>'),
  tip        = svg('<path d="M6 12.5h4M6.6 14.2h2.8M5.2 9.8A4 4 0 1 1 10.8 9.8c-.6.6-.8 1.1-.8 1.7H6c0-.6-.2-1.1-.8-1.7z"/>'),
  pitfall    = svg('<path d="M8 2.4 14 13H2z"/><path d="M8 6.6v3.2"/><circle cx="8" cy="11.6" r=".6" fill="currentColor" stroke="none"/>'),
  challenge  = svg('<path d="M3 14V2.5h8.5L9.8 5.2l1.7 2.7H3"/>'),
  solution   = svg('<circle cx="8" cy="8" r="6.25"/><path d="m5.2 8.3 1.9 1.9 3.8-4"/>'),
  discussion = svg('<path d="M2.5 3.5h8v5.5H6L3.5 11V9h-1z"/><path d="M11 6h2.5v5.5h-1V13L10 11.5H7.5"/>'),
  prereq     = svg('<path d="M6.5 9.5a2.5 2.5 0 0 0 3.5 0l2-2a2.5 2.5 0 0 0-3.5-3.5l-1 1"/><path d="M9.5 6.5a2.5 2.5 0 0 0-3.5 0l-2 2a2.5 2.5 0 0 0 3.5 3.5l1-1"/>'),
  ["deep-dive"] = svg('<path d="M8 2.5 14 5.5 8 8.5 2 5.5z"/><path d="m2 8.5 6 3 6-3"/><path d="m2 11.5 6 3 6-3"/>'),
  instructor = svg('<path d="M1.75 8s2.25-4.25 6.25-4.25S14.25 8 14.25 8 12 12.25 8 12.25 1.75 8 1.75 8z"/><circle cx="8" cy="8" r="2"/>'),
  checkpoint = svg('<path d="M3.5 14V2.5"/><path d="M3.5 3h8.5l-1.8 2.8L12 8.5H3.5"/>'),
  chem       = svg('<path d="M6 2.5h4M7 2.5v4.2L3.2 12.4A1.2 1.2 0 0 0 4.2 14h7.6a1.2 1.2 0 0 0 1-1.6L9 6.7V2.5"/><path d="M5 10.5h6"/>'),
  bio        = svg('<path d="M4.5 2c0 4 7 4 7 8s-7 4-7 4"/><path d="M11.5 2c0 4-7 4-7 8s7 4 7 4"/><path d="M5.2 5h5.6M5.2 11h5.6"/>'),
  math       = svg('<path d="M12 3.5H4.5L8.5 8l-4 4.5H12"/>'),
  cs         = svg('<path d="m5.5 4.5-3.5 3.5 3.5 3.5M10.5 4.5l3.5 3.5-3.5 3.5"/><path d="m9 3-2 10"/>'),
  predict    = svg('<circle cx="8" cy="8" r="6.25"/><path d="M8 4.5V8l2.3 1.6"/>'),
  clock      = svg('<circle cx="8" cy="8" r="6.25"/><path d="M8 4.5V8l2.3 1.6"/>', ' mm-icon-inline'),
  level      = svg('<path d="M2.5 13V9.5M6.2 13V6.5M9.8 13V4M13.5 13V2.5"/>', ' mm-icon-inline'),
  chevron    = '<svg viewBox="0 0 16 16" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="m3.5 6 4.5 4.5L12.5 6"/></svg>',
  arrowl     = '<svg viewBox="0 0 16 16" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M13 8H3M7 4 3 8l4 4"/></svg>',
  arrowr     = '<svg viewBox="0 0 16 16" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M3 8h10M9 4l4 4-4 4"/></svg>',
  check      = '<svg viewBox="0 0 16 16" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="m3 8.5 3 3 7-7"/></svg>',
  edit       = '<svg viewBox="0 0 16 16" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M11.5 2.5 13.5 4.5 6 12H4v-2z"/><path d="M2.5 14h11"/></svg>',
  issue      = '<svg viewBox="0 0 16 16" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="8" r="6.25"/><path d="M8 5v3.5"/><circle cx="8" cy="11" r=".6" fill="currentColor" stroke="none"/></svg>',
  history    = '<svg viewBox="0 0 16 16" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M2.5 8a5.5 5.5 0 1 0 1.6-3.9"/><path d="M2.5 2.5v2.5H5"/><path d="M8 5v3l2 1.3"/></svg>',
  colab      = '<svg viewBox="0 0 16 16" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><path d="M5.2 5.2a3 3 0 1 0 0 5.6M10.8 5.2a3 3 0 1 1 0 5.6"/></svg>',
  download   = '<svg viewBox="0 0 16 16" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M8 2.5v8M4.5 7 8 10.5 11.5 7"/><path d="M3 13.5h10"/></svg>',
  eye        = '<svg viewBox="0 0 16 16" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M1.75 8s2.25-4.25 6.25-4.25S14.25 8 14.25 8 12 12.25 8 12.25 1.75 8 1.75 8z"/><circle cx="8" cy="8" r="2"/></svg>',
}

return M
