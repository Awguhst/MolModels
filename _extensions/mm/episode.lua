-- Episode machinery for Molecules & Models:
--   * attaches the self-hosted KaTeX + mm CSS/JS dependencies (correct relative paths on every page)
--   * appends the auto-generated "Key points" card (from front matter `keypoints`)
--   * appends the episode footer: previous/next cards, edit / report links, last updated
-- Course structure (ids, titles, prev/next, git dates) comes from _generated/course.json,
-- which scripts/build_course_data.py writes before each render.

local icons = dofile(quarto.utils.resolve_path("icons.lua")).icons

local function esc(s)
  return (tostring(s):gsub("&", "&amp;"):gsub("<", "&lt;"):gsub(">", "&gt;"):gsub('"', "&quot;"))
end

local function read_course()
  local dir = quarto.project.directory
  if not dir then return nil end
  local f = io.open(dir .. "/_generated/course.json", "r")
  if not f then return nil end
  local txt = f:read("a")
  f:close()
  local ok, data = pcall(pandoc.json.decode, txt)
  if not ok then
    quarto.log.warning("could not parse _generated/course.json")
    return nil
  end
  return data
end

local function str(meta, key)
  local v = meta[key]
  if v == nil then return nil end
  return pandoc.utils.stringify(v)
end

local function page_id(meta)
  local ch = str(meta, "chapter")
  if not ch then return nil end
  local chn = tonumber(ch)
  if not chn then return nil end
  if meta["episode"] then
    return string.format("ch%02d-ep%02d", chn, tonumber(str(meta, "episode")))
  elseif meta["lab"] then
    return string.format("ch%02d-lab%02d", chn, tonumber(str(meta, "lab")))
  elseif meta["checkpoint-quiz"] then
    return string.format("ch%02d-quiz", chn)
  elseif meta["chapter-index"] then
    return string.format("ch%02d", chn)
  end
  return nil
end

local function rel_href(from_file, to_file)
  -- both are project-relative output paths (e.g. part-1/ch02/03-x.html); compute a relative link
  local from_parts, to_parts = {}, {}
  for p in from_file:gmatch("[^/]+") do table.insert(from_parts, p) end
  for p in to_file:gmatch("[^/]+") do table.insert(to_parts, p) end
  table.remove(from_parts) -- drop file name
  local i = 1
  while i <= #from_parts and i <= #to_parts and from_parts[i] == to_parts[i] do i = i + 1 end
  local out = {}
  for _ = i, #from_parts do table.insert(out, "..") end
  for k = i, #to_parts do table.insert(out, to_parts[k]) end
  return table.concat(out, "/")
end

local function add_katex()
  quarto.doc.add_html_dependency({
    name = "katex",
    version = "0.16.22",
    stylesheets = { "../../assets/katex/katex.min.css" },
    scripts = {
      { path = "../../assets/katex/katex.min.js", attribs = { defer = "" } },
      { path = "../../assets/katex/auto-render.min.js", attribs = { defer = "" } },
    },
    resources = {
      { name = "fonts/KaTeX_AMS-Regular.woff2", path = "../../assets/katex/fonts/KaTeX_AMS-Regular.woff2" },
      { name = "fonts/KaTeX_Caligraphic-Bold.woff2", path = "../../assets/katex/fonts/KaTeX_Caligraphic-Bold.woff2" },
      { name = "fonts/KaTeX_Caligraphic-Regular.woff2", path = "../../assets/katex/fonts/KaTeX_Caligraphic-Regular.woff2" },
      { name = "fonts/KaTeX_Fraktur-Bold.woff2", path = "../../assets/katex/fonts/KaTeX_Fraktur-Bold.woff2" },
      { name = "fonts/KaTeX_Fraktur-Regular.woff2", path = "../../assets/katex/fonts/KaTeX_Fraktur-Regular.woff2" },
      { name = "fonts/KaTeX_Main-Bold.woff2", path = "../../assets/katex/fonts/KaTeX_Main-Bold.woff2" },
      { name = "fonts/KaTeX_Main-BoldItalic.woff2", path = "../../assets/katex/fonts/KaTeX_Main-BoldItalic.woff2" },
      { name = "fonts/KaTeX_Main-Italic.woff2", path = "../../assets/katex/fonts/KaTeX_Main-Italic.woff2" },
      { name = "fonts/KaTeX_Main-Regular.woff2", path = "../../assets/katex/fonts/KaTeX_Main-Regular.woff2" },
      { name = "fonts/KaTeX_Math-BoldItalic.woff2", path = "../../assets/katex/fonts/KaTeX_Math-BoldItalic.woff2" },
      { name = "fonts/KaTeX_Math-Italic.woff2", path = "../../assets/katex/fonts/KaTeX_Math-Italic.woff2" },
      { name = "fonts/KaTeX_SansSerif-Bold.woff2", path = "../../assets/katex/fonts/KaTeX_SansSerif-Bold.woff2" },
      { name = "fonts/KaTeX_SansSerif-Italic.woff2", path = "../../assets/katex/fonts/KaTeX_SansSerif-Italic.woff2" },
      { name = "fonts/KaTeX_SansSerif-Regular.woff2", path = "../../assets/katex/fonts/KaTeX_SansSerif-Regular.woff2" },
      { name = "fonts/KaTeX_Script-Regular.woff2", path = "../../assets/katex/fonts/KaTeX_Script-Regular.woff2" },
      { name = "fonts/KaTeX_Size1-Regular.woff2", path = "../../assets/katex/fonts/KaTeX_Size1-Regular.woff2" },
      { name = "fonts/KaTeX_Size2-Regular.woff2", path = "../../assets/katex/fonts/KaTeX_Size2-Regular.woff2" },
      { name = "fonts/KaTeX_Size3-Regular.woff2", path = "../../assets/katex/fonts/KaTeX_Size3-Regular.woff2" },
      { name = "fonts/KaTeX_Size4-Regular.woff2", path = "../../assets/katex/fonts/KaTeX_Size4-Regular.woff2" },
      { name = "fonts/KaTeX_Typewriter-Regular.woff2", path = "../../assets/katex/fonts/KaTeX_Typewriter-Regular.woff2" },
    },
  })
end

local function has_math(doc)
  -- math.lua has already turned Math nodes into <span class="math ..."> raw HTML; the glossary
  -- shortcode emits the same markup inside a raw block
  local found = false
  doc:walk({
    RawInline = function(r) if r.format == "html" and r.text:find('class="math', 1, true) then found = true end end,
    RawBlock = function(r) if r.format == "html" and r.text:find('class="math', 1, true) then found = true end end,
  })
  return found
end

local function add_dependencies(doc)
  -- pages whose maths arrives through a shortcode (the glossary) opt in with `mm-katex: true`
  if has_math(doc) or doc.meta["mm-katex"] then add_katex() end
  quarto.doc.add_html_dependency({
    name = "mm",
    version = "0.1.0",
    scripts = {
      { path = "../../assets/js/mm.js", attribs = { defer = "" } },
    },
  })
  quarto.doc.include_text("after-body", [[
<script>
document.addEventListener("DOMContentLoaded", function () {
  if (window.renderMathInElement) {
    renderMathInElement(document.body, {
      delimiters: [
        { left: "\\(", right: "\\)", display: false },
        { left: "\\[", right: "\\]", display: true }
      ],
      ignoredClasses: ["sourceCode", "cell-output"],
      throwOnError: false
    });
  }
});
</script>]])
end

local function keypoints_block(meta)
  local kp = meta["keypoints"]
  if not kp or pandoc.utils.type(kp) ~= "List" or #kp == 0 then return {} end
  local items = pandoc.List()
  for _, k in ipairs(kp) do
    local inl = pandoc.utils.blocks_to_inlines(pandoc.read(pandoc.utils.stringify(k), "markdown").blocks)
    items:insert({ pandoc.Plain(inl) })
  end
  local header = pandoc.Header(2, pandoc.Str("Key points"), pandoc.Attr("key-points", { "mm-keypoints-title" }))
  local div = pandoc.Div({ header, pandoc.BulletList(items) }, pandoc.Attr("", { "mm-keypoints" }))
  return { div }
end

local function card(dir, item, href)
  if not item then
    return '<span class="mm-pager-empty" aria-hidden="true"></span>'
  end
  local arrow = dir == "prev" and icons.arrowl or icons.arrowr
  local label = dir == "prev" and "Previous" or "Next"
  -- JSON null is a truthy userdata value in Pandoc; only numbered pages have labels.
  local num = type(item.label) == "string" and item.label ~= "" and (esc(item.label) .. " ") or ""
  return '<a class="mm-pager-' .. dir .. '" href="' .. esc(href) .. '" rel="' .. dir .. '"><span class="mm-pager-dir">'
    .. (dir == "prev" and (arrow .. label) or (label .. arrow)) .. '</span><span class="mm-pager-title">' .. num .. esc(item.title) .. "</span></a>"
end

local function footer_block(meta, course, id)
  local parts = {}
  local item = course and course.pages and course.pages[id]
  local input = quarto.doc.input_file or ""
  local pdir = quarto.project.directory or ""
  local rel = input:sub(#pdir + 2):gsub("\\", "/")
  local repo = str(meta, "github-repo") or "YOUR-USER/molecules-and-models"
  local branch = str(meta, "github-branch") or "main"
  table.insert(parts, '<div class="mm-footer">')
  if item then
    local prev = item.prev and course.pages[item.prev] or nil
    local nxt = item.next and course.pages[item.next] or nil
    local prev_href = prev and rel_href(item.href, prev.href) or nil
    local next_href = nxt and rel_href(item.href, nxt.href) or nil
    table.insert(parts, '<nav class="mm-pager" aria-label="Previous and next">' .. card("prev", prev, prev_href) .. card("next", nxt, next_href) .. "</nav>")
  end
  local meta_parts = {}
  table.insert(meta_parts, '<a href="https://github.com/' .. esc(repo) .. '/edit/' .. esc(branch) .. "/" .. esc(rel) .. '">' .. icons.edit .. "Edit this page</a>")
  table.insert(meta_parts, '<a href="https://github.com/' .. esc(repo) .. '/issues/new?title=' .. esc("Problem in " .. rel) .. '&amp;body=' .. esc("Page: " .. rel .. "%0A%0ADescribe the problem:") .. '">' .. icons.issue .. "Report a problem</a>")
  if item and item.updated then
    table.insert(meta_parts, '<span>' .. icons.history .. "Last updated " .. esc(item.updated) .. "</span>")
  end
  table.insert(parts, '<div class="mm-meta">' .. table.concat(meta_parts, "") .. "</div>")
  table.insert(parts, "</div>")
  return { pandoc.RawBlock("html", table.concat(parts, "\n")) }
end

local function Pandoc(doc)
  if not quarto.doc.is_format("html") then return nil end
  add_dependencies(doc)
  local meta = doc.meta
  local course = read_course()
  local id = page_id(meta)
  local blocks = doc.blocks
  -- "Where this is going" paragraphs are written by authors; the key points card comes after them.
  if meta["episode"] then
    for _, b in ipairs(keypoints_block(meta)) do blocks:insert(b) end
  end
  if id or meta["episode"] or meta["lab"] then
    for _, b in ipairs(footer_block(meta, course, id or "")) do blocks:insert(b) end
  elseif str(meta, "mm-footer") == "true" then
    for _, b in ipairs(footer_block(meta, course, "")) do blocks:insert(b) end
  end
  doc.blocks = blocks
  return doc
end

return {
  { Pandoc = Pandoc },
}
