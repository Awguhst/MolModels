-- Hand TeX maths to the self-hosted KaTeX auto-render (attached in episode.lua) instead of
-- letting pandoc's "plain" math method try to convert it to Unicode (which fails on \frac, \sqrt ...).
-- Readers without JavaScript see the TeX source, which is still legible.
local function Math(m)
  if not quarto.doc.is_format("html") then return nil end
  if m.mathtype == "DisplayMath" then
    return pandoc.RawInline("html", '<span class="math display">\\[' .. m.text .. '\\]</span>')
  end
  return pandoc.RawInline("html", '<span class="math inline">\\(' .. m.text .. '\\)</span>')
end

return {
  { Math = Math },
}
