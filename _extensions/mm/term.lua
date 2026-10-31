-- {{< term overfitting >}}            -> linked term with a hover/focus definition
-- {{< term overfitting "overfit" >}}  -> custom display text
-- {{< term overfitting plural >}}     -> uses the plural form from glossary.yml
local data = dofile(quarto.utils.resolve_path("glossary-data.lua"))
local counter = 0

local function esc(s)
  return (tostring(s):gsub("&", "&amp;"):gsub("<", "&lt;"):gsub(">", "&gt;"):gsub('"', "&quot;"))
end

local function glossary_href()
  local input = quarto.doc.input_file or ""
  local pdir = quarto.project.directory or ""
  local rel = input:sub(#pdir + 2):gsub("\\", "/")
  local depth = select(2, rel:gsub("/", "")) -- number of directories
  return string.rep("../", depth) .. "appendices/glossary.html"
end

return {
  ["term"] = function(args, kwargs, meta)
    local id = pandoc.utils.stringify(args[1] or "")
    local g = data.load()
    local entry = g.terms[id]
    local display
    if args[2] then
      local a2 = pandoc.utils.stringify(args[2])
      if a2 == "plural" and entry and entry.plural then
        display = entry.plural
      else
        display = a2
      end
    end
    if not entry then
      quarto.log.warning("glossary term not found: '" .. id .. "'")
      return pandoc.Str(display or id)
    end
    display = display or entry.term
    if not quarto.doc.is_format("html") then
      return pandoc.Str(display)
    end
    counter = counter + 1
    local tip_id = "mm-tip-" .. id .. "-" .. counter
    local href = glossary_href() .. "#term-" .. id
    local html = '<span class="mm-term-wrap"><a class="mm-term" href="' .. esc(href) .. '" aria-describedby="' .. tip_id .. '">' .. esc(display)
      .. '</a><span class="mm-term-tip" role="tooltip" id="' .. tip_id .. '"><strong>' .. esc(entry.term) .. "</strong>" .. esc(entry.short) .. "</span></span>"
    return pandoc.RawInline("html", html)
  end,
}
