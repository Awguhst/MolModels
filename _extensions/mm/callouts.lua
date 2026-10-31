-- Molecules & Models callout vocabulary.
--   ::: {.note} / .tip / .pitfall / .prereq / .discussion / .deep-dive
--   ::: {.challenge level=2 title="..."}  with nested  :::: {.solution}
--   ::: {.bridge audience="chem|bio|math|cs"}
--   ::: {.checkpoint title="..."}  (question text, then a task list `- [x]` / `- [ ]` of options,
--                                   each option followed by its feedback paragraph)
--   ::: {.predict}  (a "predict before you run" prompt)
-- Emits semantic, accessible HTML; the CSS lives in assets/scss/mm-light.scss.
-- Only active for HTML output; other formats fall back to plain divs.

local icons = dofile(quarto.utils.resolve_path("icons.lua")).icons

local kinds = {
  prereq      = { label = "Prerequisite" },
  note        = { label = "Note" },
  tip         = { label = "Tip" },
  pitfall     = { label = "Common mistake" },
  challenge   = { label = "Exercise" },
  solution    = { label = "Solution", collapsible = true, cta_show = "Show solution", cta_hide = "Hide solution" },
  discussion  = { label = "Discussion" },
  ["deep-dive"] = { label = "Deep dive", collapsible = true, cta_show = "Show the maths", cta_hide = "Hide the maths" },
  checkpoint  = { label = "Checkpoint" },
  predict     = { label = "Predict before you run" },
}

local bridges = {
  chem = { label = "Chemist's corner", icon = "chem" },
  bio  = { label = "Biologist's corner", icon = "bio" },
  math = { label = "Maths corner", icon = "math" },
  cs   = { label = "For programmers", icon = "cs" },
}

local counter = 0
local function next_id(prefix)
  counter = counter + 1
  return prefix .. "-" .. counter
end

local function esc(s)
  return (tostring(s):gsub("&", "&amp;"):gsub("<", "&lt;"):gsub(">", "&gt;"):gsub('"', "&quot;"))
end

local function raw(html)
  return pandoc.RawBlock("html", html)
end

local function stars(level)
  level = tonumber(level) or 1
  if level < 1 then level = 1 elseif level > 3 then level = 3 end
  local s = string.rep("★", level) .. string.rep("☆", 3 - level)
  local names = { "check understanding", "apply", "stretch" }
  return '<span class="mm-callout-stars" role="img" aria-label="Level ' .. level .. ' of 3: ' .. names[level] .. '">' .. s .. "</span>"
end

local function head_html(kind, icon, label, title, extra, id)
  local h = '<div class="mm-callout-head">' .. icons[icon]
  h = h .. '<span class="mm-callout-label">' .. esc(label) .. "</span>"
  if extra then h = h .. extra end
  if title and title ~= "" then
    h = h .. '<p class="mm-callout-title" id="' .. id .. '">' .. title .. "</p>"
  end
  return h .. "</div>"
end

local function inline_title(div)
  -- titles may contain inline markdown: render the attribute through pandoc
  local t = div.attributes["title"]
  if not t or t == "" then return nil end
  local doc = pandoc.read(t, "markdown")
  local first = doc.blocks[1]
  -- only a plain paragraph is rendered as inline markdown; anything else (e.g. "1. Types" parsing
  -- as an ordered list) is used verbatim as escaped text
  if #doc.blocks ~= 1 or not first or (first.t ~= "Para" and first.t ~= "Plain") then return esc(t) end
  return pandoc.write(pandoc.Pandoc({ pandoc.Plain(first.content) }), "html")
end

-- ---------------------------------------------------------------------------
-- Checkpoint quizzes
-- ---------------------------------------------------------------------------
local function build_checkpoint(div, id, title_html)
  local stem = {}
  local list = nil
  for _, b in ipairs(div.content) do
    if list == nil and b.t == "BulletList" then
      list = b
    elseif list == nil then
      table.insert(stem, b)
    else
      table.insert(stem, b) -- blocks after the list are kept (rare)
    end
  end
  if list == nil then
    quarto.log.warning("checkpoint without an option list: " .. (div.attributes["title"] or ""))
    return nil
  end
  local out = {}
  table.insert(out, raw('<div class="mm-callout mm-callout--checkpoint" role="group" aria-labelledby="' .. id .. '-label">'))
  table.insert(out, raw(head_html("checkpoint", "checkpoint", "Checkpoint", title_html, nil, id .. "-label")))
  table.insert(out, raw('<div class="mm-callout-body">'))
  for _, b in ipairs(stem) do table.insert(out, b) end
  table.insert(out, raw('<ol class="mm-quiz-options" data-mm-quiz="' .. id .. '">'))
  local letters = { "A", "B", "C", "D", "E", "F" }
  local n_correct = 0
  for i, item in ipairs(list.content) do
    local first = item[1]
    local correct = false
    local option_inlines = pandoc.List()
    if first and (first.t == "Plain" or first.t == "Para") then
      local inl = first.content
      local marker = inl[1]
      if marker and marker.t == "Str" and (marker.text == "☒" or marker.text == "☐") then
        correct = marker.text == "☒"
        for k = 2, #inl do option_inlines:insert(inl[k]) end
        if option_inlines[1] and option_inlines[1].t == "Space" then option_inlines:remove(1) end
      else
        quarto.log.warning("checkpoint option without [x]/[ ] marker in: " .. (div.attributes["title"] or ""))
        option_inlines = inl
      end
    end
    if correct then n_correct = n_correct + 1 end
    local feedback = {}
    for k = 2, #item do table.insert(feedback, item[k]) end
    local verdict = correct and "Correct." or "Not quite."
    table.insert(out, raw('<li><details class="mm-quiz-option" data-correct="' .. tostring(correct) .. '"><summary><span class="mm-quiz-letter" aria-hidden="true">' .. letters[i] .. '</span><span class="mm-quiz-text">'))
    table.insert(out, pandoc.Plain(option_inlines))
    table.insert(out, raw('</span></summary><div class="mm-quiz-feedback"><p><span class="mm-quiz-verdict">' .. verdict .. "</span>"))
    -- first feedback paragraph continues inline after the verdict
    if feedback[1] and (feedback[1].t == "Para" or feedback[1].t == "Plain") then
      table.insert(out, pandoc.Plain(feedback[1].content))
      table.insert(out, raw("</p>"))
      for k = 2, #feedback do table.insert(out, feedback[k]) end
    else
      table.insert(out, raw("</p>"))
      for _, fb in ipairs(feedback) do table.insert(out, fb) end
    end
    table.insert(out, raw("</div></details></li>"))
  end
  table.insert(out, raw("</ol>"))
  if n_correct ~= 1 then
    quarto.log.warning("checkpoint '" .. (div.attributes["title"] or "") .. "' has " .. n_correct .. " correct options (expected 1)")
  end
  table.insert(out, raw('<p class="mm-quiz-score" data-mm-quiz-score hidden></p>'))
  table.insert(out, raw("</div></div>"))
  return out
end

-- ---------------------------------------------------------------------------
-- Generic callouts
-- ---------------------------------------------------------------------------
local function build_callout(div, kind, label, icon, extra_head, collapsible, cta_show, cta_hide)
  local id = next_id("mm-" .. kind)
  local title_html = inline_title(div)
  local classes = "mm-callout mm-callout--" .. kind
  for _, c in ipairs(div.classes) do
    if c ~= kind and c ~= "bridge" and c ~= "callout" then classes = classes .. " " .. c end
  end
  local out = {}
  if collapsible then
    local summary = '<summary>' .. icons[icon] .. '<span class="mm-callout-label">' .. esc(label) .. "</span>"
    if extra_head then summary = summary .. extra_head end
    if title_html then summary = summary .. '<span class="mm-callout-title">' .. title_html .. "</span>" end
    summary = summary .. '<span class="mm-summary-cta"><span class="show">' .. esc(cta_show) .. '</span><span class="hide">' .. esc(cta_hide) .. "</span>" .. icons.chevron .. "</span></summary>"
    table.insert(out, raw('<details class="' .. classes .. '" id="' .. id .. '">' .. summary .. '<div class="mm-callout-body">'))
  else
    local role = ""
    if kind == "note" or kind == "tip" or kind == "pitfall" or kind == "prereq" then role = ' role="note"' end
    table.insert(out, raw('<div class="' .. classes .. '" id="' .. id .. '"' .. role .. ' aria-labelledby="' .. id .. '-label">'))
    table.insert(out, raw(head_html(kind, icon, label, title_html, extra_head, id .. "-label")))
    table.insert(out, raw('<div class="mm-callout-body">'))
  end
  for _, b in ipairs(div.content) do table.insert(out, b) end
  if collapsible then
    table.insert(out, raw("</div></details>"))
  else
    table.insert(out, raw("</div></div>"))
  end
  -- a label id is required even when there is no title: emit a hidden label span
  if not title_html then
    out[2] = raw(tostring(out[2].text):gsub('<span class="mm%-callout%-label">', '<span class="mm-callout-label" id="' .. id .. '-label">', 1))
  end
  return out
end

local function Div(div)
  if not quarto.doc.is_format("html") then return nil end
  local c = div.classes
  if c:includes("bridge") then
    local audience = div.attributes["audience"] or "cs"
    local b = bridges[audience]
    if not b then
      quarto.log.warning("unknown bridge audience '" .. audience .. "', using cs")
      b = bridges.cs
      audience = "cs"
    end
    div.attributes["audience"] = nil
    return build_callout(div, "bridge-" .. audience, b.label, b.icon, nil, false)
  end
  if c:includes("challenge") then
    local level = div.attributes["level"] or "1"
    div.attributes["level"] = nil
    return build_callout(div, "challenge", "Exercise", "challenge", stars(level), false)
  end
  if c:includes("checkpoint") then
    local id = next_id("mm-checkpoint")
    return build_checkpoint(div, id, inline_title(div))
  end
  for kind, spec in pairs(kinds) do
    if c:includes(kind) then
      local icon = kind
      if kind == "predict" then icon = "predict" end
      return build_callout(div, kind, spec.label, icon, nil, spec.collapsible, spec.cta_show, spec.cta_hide)
    end
  end
  return nil
end

-- Quarto parses `.solution` (like `.proof` and `.remark`) into its own "Proof" custom node before any
-- user filter runs. Reclaim those nodes so that solutions render as our collapsed <details> boxes.
local function Proof(p)
  if not quarto.doc.is_format("html") then return nil end
  local kind = pandoc.utils.stringify(p.type or p.name or ""):lower()
  if kind ~= "solution" then return nil end
  local div = p.div
  if div == nil then return nil end
  if pandoc.utils.type(div) ~= "Block" or div.t ~= "Div" then
    -- Quarto may hand us the content as a list of blocks rather than the original Div
    local blocks = pandoc.utils.type(div) == "Blocks" and div or pandoc.Blocks({ div })
    div = pandoc.Div(blocks, pandoc.Attr("", { "solution" }))
  end
  local spec = kinds.solution
  return pandoc.Blocks(build_callout(div, "solution", spec.label, "solution", nil, true, spec.cta_show, spec.cta_hide))
end

return {
  { Div = Div, Proof = Proof },
}
