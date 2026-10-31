-- {{< generated ch02-schedule >}} inserts _generated/ch02-schedule.md (written by the pre-render
-- script scripts/build_course_data.py). Unlike Quarto's include directive, which is resolved when the
-- project is scanned (before pre-render scripts run), a shortcode runs during filtering, so a clean
-- clone renders in one go and a missing file degrades to a warning instead of a hard failure.
return {
  ["generated"] = function(args, kwargs, meta)
    local name = pandoc.utils.stringify(args[1] or "")
    local dir = quarto.project.directory or "."
    local path = dir .. "/_generated/" .. name .. ".md"
    local f = io.open(path, "r")
    if not f then
      quarto.log.warning("generated file not found: " .. path .. " (run scripts/build_course_data.py)")
      return pandoc.Div({ pandoc.Para(pandoc.Str("")) }, pandoc.Attr("", { "mm-generated-missing" }))
    end
    local text = f:read("a")
    f:close()
    local doc = pandoc.read(text, "markdown")
    return doc.blocks
  end,
}
