-- Shared loader for glossary.yml (used by the term and glossary shortcodes).
-- The YAML is parsed by pandoc itself (as a metadata block), so no extra dependency is needed.
local M = {}
local cache = nil

local function stringify_md(v)
  -- keep inline markdown (links, code) by writing the metadata inlines back to HTML
  if v == nil then return "" end
  if type(v) == "string" then return v end
  -- the "mathjax" writer method emits <span class="math inline">\(...\)</span> (the "katex" method
  -- omits the delimiters); our self-hosted KaTeX auto-render needs the delimiters, and episode.lua
  -- attaches KaTeX when it sees these spans
  local opts = { html_math_method = "mathjax" }
  local kind = pandoc.utils.type(v)
  if kind == "Inlines" then
    return pandoc.write(pandoc.Pandoc({ pandoc.Plain(v) }), "html", opts)
  elseif kind == "Blocks" then
    return pandoc.write(pandoc.Pandoc(v), "html", opts)
  end
  return pandoc.utils.stringify(v)
end

function M.load()
  if cache then return cache end
  local dir = quarto.project.directory or "."
  local f = io.open(dir .. "/glossary.yml", "r")
  if not f then
    quarto.log.warning("glossary.yml not found")
    cache = { terms = {}, order = {} }
    return cache
  end
  local yaml = f:read("a")
  f:close()
  local doc = pandoc.read("---\n" .. yaml .. "\n---\n", "markdown")
  local terms, order = {}, {}
  local list = doc.meta["terms"]
  if list and pandoc.utils.type(list) == "List" then
    for _, t in ipairs(list) do
      local id = pandoc.utils.stringify(t["id"])
      local entry = {
        id = id,
        term = pandoc.utils.stringify(t["term"]),
        plural = t["plural"] and pandoc.utils.stringify(t["plural"]) or nil,
        short = pandoc.utils.stringify(t["short"] or t["definition"] or ""),
        definition_html = stringify_md(t["definition"]),
        chapter = t["chapter"] and pandoc.utils.stringify(t["chapter"]) or nil,
        see = {},
      }
      if t["see"] and pandoc.utils.type(t["see"]) == "List" then
        for _, s in ipairs(t["see"]) do table.insert(entry.see, pandoc.utils.stringify(s)) end
      end
      terms[id] = entry
      table.insert(order, id)
    end
  end
  table.sort(order, function(a, b) return terms[a].term:lower() < terms[b].term:lower() end)
  cache = { terms = terms, order = order }
  return cache
end

return M
