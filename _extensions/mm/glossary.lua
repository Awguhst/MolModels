-- {{< glossary >}} renders the whole glossary (from glossary.yml) as an A–Z definition list.
local data = dofile(quarto.utils.resolve_path("glossary-data.lua"))

local function esc(s)
  return (tostring(s):gsub("&", "&amp;"):gsub("<", "&lt;"):gsub(">", "&gt;"):gsub('"', "&quot;"))
end

return {
  ["glossary"] = function(args, kwargs, meta)
    local g = data.load()
    if not quarto.doc.is_format("html") then
      local blocks = pandoc.List()
      for _, id in ipairs(g.order) do
        local e = g.terms[id]
        blocks:insert(pandoc.Para({ pandoc.Strong(pandoc.Str(e.term)), pandoc.Str(": " .. e.short) }))
      end
      return blocks
    end
    local letters, seen = {}, {}
    for _, id in ipairs(g.order) do
      local l = g.terms[id].term:sub(1, 1):upper()
      if not seen[l] then seen[l] = true; table.insert(letters, l) end
    end
    local out = { '<nav class="mm-glossary-index" aria-label="Glossary index">' }
    for _, l in ipairs(letters) do
      table.insert(out, '<a href="#letter-' .. l .. '">' .. l .. "</a>")
    end
    table.insert(out, "</nav>")
    table.insert(out, '<dl class="mm-glossary">')
    local current = nil
    for _, id in ipairs(g.order) do
      local e = g.terms[id]
      local l = e.term:sub(1, 1):upper()
      if l ~= current then
        current = l
        table.insert(out, '<dt class="mm-glossary-letter" id="letter-' .. l .. '" aria-label="Letter ' .. l .. '"><span class="mm-chip">' .. l .. "</span></dt>")
      end
      table.insert(out, '<dt id="term-' .. esc(e.id) .. '">' .. esc(e.term) .. "</dt>")
      local dd = "<dd>" .. e.definition_html
      if e.chapter then
        dd = dd .. '<p class="mm-see">Introduced in ' .. esc(e.chapter) .. ".</p>"
      end
      if #e.see > 0 then
        local links = {}
        for _, s in ipairs(e.see) do
          local target = g.terms[s]
          if target then
            table.insert(links, '<a href="#term-' .. esc(s) .. '">' .. esc(target.term) .. "</a>")
          end
        end
        if #links > 0 then dd = dd .. '<p class="mm-see">See also: ' .. table.concat(links, ", ") .. "</p>" end
      end
      table.insert(out, dd .. "</dd>")
    end
    table.insert(out, "</dl>")
    return pandoc.RawBlock("html", table.concat(out, "\n"))
  end,
}
