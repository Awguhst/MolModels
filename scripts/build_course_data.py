#!/usr/bin/env python
"""Pre-render step: derive everything navigational from the chapter front matter.

Reads
    course.yml                         parts, appendices, sidebar resources
    part-*/ch*/_metadata.yml           chapter number/title/stub flag
    part-*/ch*/NN-*.qmd                episode front matter
    part-*/ch*/labs/lab-NN-*.qmd       lab front matter
    part-*/ch*/checkpoint.qmd          chapter quiz (optional)
Writes
    _generated/course.json             consumed by the mm Lua filter and scripts/post_render.py
    _sidebar.yml                       Quarto sidebar (merged via metadata-files in _quarto.yml)
    _generated/chNN-hero.md            chapter hero strip (included by the chapter index page)
    _generated/chNN-schedule.md        schedule table (Episode | Cumulative time | Questions)
    _generated/chNN-labs.md            lab cards with Colab / download / solutions buttons
    _generated/chNN-keypoints.md       key points of every episode in the chapter
    _generated/all-keypoints.md        the same, for every built chapter
    _generated/metro.md                the roadmap "metro map" SVG for the home page
    _generated/home-parts.md           part list for the home page

Run directly (python scripts/build_course_data.py) or let Quarto run it as a pre-render script.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
GEN = ROOT / "_generated"
GEN.mkdir(exist_ok=True)

ACCENT_VAR = {"violet": "--mm-accent-1", "amber": "--mm-accent-2", "green": "--mm-accent-3", "coral": "--mm-accent-4"}


# --------------------------------------------------------------------------- helpers
def read_front_matter(path: Path) -> dict:
    text = path.read_text(encoding="utf8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return {}
    data = yaml.safe_load(m.group(1)) or {}
    if not isinstance(data, dict):
        return {}
    return data


def git_date(path: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", str(path.relative_to(ROOT))],
            cwd=ROOT, capture_output=True, text=True, timeout=20, check=False,
        )
        d = out.stdout.strip()
        return d or None
    except (OSError, subprocess.SubprocessError):
        return None


def updated_date(path: Path) -> str:
    d = git_date(path)
    if d:
        return d
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%d")


def html_path(qmd: Path) -> str:
    rel = qmd.relative_to(ROOT).as_posix()
    return re.sub(r"\.(qmd|ipynb)$", ".html", rel)


def md_inline(s: str) -> str:
    """Tiny markdown-to-HTML for front-matter strings (code spans and emphasis only)."""
    s = escape(str(s), quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", s)
    return s


def fmt_minutes(m: int) -> str:
    if m < 60:
        return f"{m} min"
    h, r = divmod(m, 60)
    return f"{h} h {r:02d} min" if r else f"{h} h"


# --------------------------------------------------------------------------- discovery
def discover() -> dict:
    course_cfg = yaml.safe_load((ROOT / "course.yml").read_text(encoding="utf8"))
    parts = []
    chapters: dict[str, dict] = {}
    pages: dict[str, dict] = {}
    sequence: list[str] = []

    for p in course_cfg["parts"]:
        pdir = ROOT / p["dir"]
        part = {
            "number": p["number"], "title": p["title"], "short": p["short"], "roman": p["roman"],
            "accent": p["accent"], "dir": p["dir"], "href": f"{p['dir']}/index.html", "chapters": [],
        }
        parts.append(part)
        for cdir in sorted(d for d in pdir.glob("ch*") if d.is_dir()):
            meta_file = cdir / "_metadata.yml"
            if not meta_file.exists():
                continue
            meta = yaml.safe_load(meta_file.read_text(encoding="utf8")) or {}
            idx = cdir / "index.qmd"
            idx_fm = read_front_matter(idx) if idx.exists() else {}
            chn = int(meta["chapter"])
            cid = f"ch{chn:02d}"
            chapter = {
                "id": cid, "number": chn, "title": meta.get("chapter-title", idx_fm.get("title", cid)),
                "short": meta.get("chapter-short", meta.get("chapter-title", cid)),
                "part": p["number"], "dir": cdir.relative_to(ROOT).as_posix(), "href": html_path(idx),
                "stub": bool(meta.get("stub", False)), "summary": idx_fm.get("summary", ""),
                "pages": [], "episodes": [], "labs": [], "teaching": 0, "exercises": 0,
            }
            chapters[cid] = chapter
            part["chapters"].append(cid)
            # chapter index page
            pages[cid] = {
                "id": cid, "kind": "index", "chapter": cid, "part": p["number"], "label": f"Chapter {chn}",
                "title": chapter["title"], "href": chapter["href"], "source": idx.relative_to(ROOT).as_posix(),
                "updated": updated_date(idx) if idx.exists() else None, "stub": chapter["stub"],
            }
            chapter["pages"].append(cid)
            # episodes
            for ep in sorted(cdir.glob("[0-9][0-9]-*.qmd")):
                fm = read_front_matter(ep)
                if "episode" not in fm:
                    continue
                epn = int(fm["episode"])
                eid = f"{cid}-ep{epn:02d}"
                page = {
                    "id": eid, "kind": "episode", "chapter": cid, "part": p["number"], "number": epn,
                    "label": f"{chn}.{epn}", "title": fm.get("title", eid), "href": html_path(ep),
                    "source": ep.relative_to(ROOT).as_posix(), "teaching": int(fm.get("teaching", 0)),
                    "exercises": int(fm.get("exercises", 0)), "level": fm.get("level", "beginner"),
                    "questions": fm.get("questions", []) or [], "objectives": fm.get("objectives", []) or [],
                    "keypoints": fm.get("keypoints", []) or [], "prerequisites": fm.get("prerequisites", []) or [],
                    "updated": updated_date(ep),
                }
                pages[eid] = page
                chapter["pages"].append(eid)
                chapter["episodes"].append(eid)
                chapter["teaching"] += page["teaching"]
                chapter["exercises"] += page["exercises"]
            # labs
            for lab in sorted((cdir / "labs").glob("lab-*.qmd")):
                fm = read_front_matter(lab)
                if "lab" not in fm:
                    continue
                ln = int(fm["lab"])
                lid = f"{cid}-lab{ln:02d}"
                nb = fm.get("notebook")
                page = {
                    "id": lid, "kind": "lab", "chapter": cid, "part": p["number"], "number": ln, "label": f"Lab {ln}",
                    "title": fm.get("title", lid), "href": html_path(lab), "source": lab.relative_to(ROOT).as_posix(),
                    "duration": fm.get("duration", ""), "minutes": int(fm.get("minutes", 0)), "level": fm.get("level", "beginner"),
                    "objectives": fm.get("objectives", []) or [], "summary": fm.get("summary", ""),
                    "notebook": nb, "updated": updated_date(lab),
                    "dataset": fm.get("dataset", ""),
                }
                if nb:
                    page["student_ipynb"] = f"{chapter['dir']}/labs/{nb}.ipynb"
                    page["solutions_html"] = f"{chapter['dir']}/labs/{nb}-solutions.html"
                pages[lid] = page
                chapter["pages"].append(lid)
                chapter["labs"].append(lid)
            # checkpoint quiz
            quiz = cdir / "checkpoint.qmd"
            if quiz.exists():
                fm = read_front_matter(quiz)
                qid = f"{cid}-quiz"
                pages[qid] = {
                    "id": qid, "kind": "quiz", "chapter": cid, "part": p["number"], "label": None,
                    "title": fm.get("title", "Chapter checkpoint"), "href": html_path(quiz),
                    "source": quiz.relative_to(ROOT).as_posix(), "updated": updated_date(quiz),
                }
                chapter["pages"].append(qid)
            # key points summary page (thin page that includes the generated list)
            kp = cdir / "key-points.qmd"
            if kp.exists():
                kid = f"{cid}-keypoints"
                pages[kid] = {
                    "id": kid, "kind": "keypoints", "chapter": cid, "part": p["number"], "label": None,
                    "title": f"Chapter {chn} key points", "href": html_path(kp),
                    "source": kp.relative_to(ROOT).as_posix(), "updated": updated_date(kp),
                }
                chapter["pages"].append(kid)
            sequence.extend(chapter["pages"])

    # prev / next
    for i, pid in enumerate(sequence):
        pages[pid]["prev"] = sequence[i - 1] if i > 0 else None
        pages[pid]["next"] = sequence[i + 1] if i + 1 < len(sequence) else None

    return {
        "generated": datetime.now(tz=timezone.utc).isoformat(timespec="seconds"),
        "parts": parts, "chapters": chapters, "pages": pages, "sequence": sequence,
        "appendices": course_cfg["appendices"], "resources": course_cfg["resources"],
    }


# --------------------------------------------------------------------------- writers
def write_sidebar(course: dict) -> None:
    contents = []
    for part in course["parts"]:
        pitems = []
        for cid in part["chapters"]:
            ch = course["chapters"][cid]
            if ch["stub"]:
                pitems.append({"text": f"{ch['number']} {ch['title']} (soon)", "href": ch["dir"] + "/index.qmd"})
                continue
            sub = []
            for pid in ch["pages"]:
                pg = course["pages"][pid]
                if pg["kind"] == "index":
                    continue
                if pg["kind"] == "episode":
                    text = f"{pg['label']} {pg['title']}"
                elif pg["kind"] == "lab":
                    text = f"Lab {pg['number']}: {pg['title']}"
                elif pg["kind"] == "quiz":
                    text = "Chapter checkpoint"
                else:
                    text = pg["title"]
                sub.append({"text": text, "href": pg["source"]})
            pitems.append({"section": f"{ch['number']} {ch['title']}", "href": ch["dir"] + "/index.qmd", "contents": sub})
        contents.append({"section": f"Part {part['roman']}: {part['short']}", "href": part["dir"] + "/index.qmd", "contents": pitems})
    app = []
    for a in course["appendices"]:
        text = f"{a['letter']}. {a['title']}" + (" (soon)" if a.get("stub") else "")
        app.append({"text": text, "href": a["file"]})
    contents.append({"section": "Appendices", "href": "appendices/index.qmd", "contents": app})
    contents.append({"section": "Resources", "contents": [{"text": r["text"], "href": r["file"]} for r in course["resources"]]})
    sidebar = {
        "website": {
            "sidebar": {
                "style": "docked",
                "collapse-level": 1,
                "search": False,
                "contents": contents,
            }
        }
    }
    header = "# GENERATED by scripts/build_course_data.py — do not edit by hand.\n"
    (ROOT / "_sidebar.yml").write_text(header + yaml.safe_dump(sidebar, sort_keys=False, allow_unicode=True), encoding="utf8")


def write_chapter_includes(course: dict) -> None:
    all_kp = ["<!-- GENERATED by scripts/build_course_data.py -->", ""]
    for cid, ch in course["chapters"].items():
        part = course["parts"][ch["part"] - 1]
        if ch["stub"]:
            hero = [
                "<!-- GENERATED by scripts/build_course_data.py -->",
                '<div class="mm-hero mm-hero--stub">',
                f'<p class="mm-kicker">Chapter {ch["number"]} of {escape(part["short"])}</p>',
                f'<h1 class="title">{escape(ch["title"])} <span class="mm-chip">soon</span></h1>',
                f'<p>{md_inline(ch["summary"])}</p>' if ch["summary"] else "",
                "</div>",
            ]
            (GEN / f"{cid}-hero.md").write_text("\n".join(h for h in hero if h) + "\n", encoding="utf8")
            continue
        n_ep = len(ch["episodes"])
        total = ch["teaching"] + ch["exercises"]
        lab_minutes = sum(course["pages"][l].get("minutes", 0) for l in ch["labs"])
        # hero
        hero = [
            "<!-- GENERATED by scripts/build_course_data.py -->",
            '<div class="mm-hero">',
            f'<p class="mm-kicker">Chapter {ch["number"]} of {escape(part["short"])}</p>',
            f'<h1 class="title">{escape(ch["title"])}</h1>',
            f'<p>{md_inline(ch["summary"])}</p>' if ch["summary"] else "",
            '<p class="mm-meta-line">'
            f'<span>{n_ep} episodes</span><span>{fmt_minutes(ch["teaching"])} of teaching</span><span>{fmt_minutes(ch["exercises"])} of exercises</span>'
            + (f'<span>{len(ch["labs"])} lab{"s" if len(ch["labs"]) != 1 else ""}, {fmt_minutes(lab_minutes)}</span>' if ch["labs"] else "")
            + f'<span>about {fmt_minutes(total + lab_minutes)} in all</span></p>',
            "</div>",
        ]
        (GEN / f"{cid}-hero.md").write_text("\n".join(h for h in hero if h) + "\n", encoding="utf8")
        # schedule
        rows = ['<!-- GENERATED by scripts/build_course_data.py -->', '<table class="mm-schedule">',
                '<thead><tr><th scope="col">Episode</th><th scope="col">Cumulative time</th><th scope="col">Questions</th></tr></thead><tbody>']
        cum = 0
        for pid in ch["pages"]:
            pg = course["pages"][pid]
            if pg["kind"] == "episode":
                cum += pg["teaching"] + pg["exercises"]
                qs = "".join(f"<li>{md_inline(q)}</li>" for q in pg["questions"])
                rows.append(
                    f'<tr><td class="mm-sched-ep"><span class="mm-ep-num">{pg["label"]}</span><a href="{escape(Path(pg["href"]).name)}">{escape(pg["title"])}</a>'
                    f'<br><span class="mm-small">{pg["teaching"]} min teaching + {pg["exercises"]} min exercises</span></td>'
                    f'<td class="mm-sched-time">{fmt_minutes(cum)}</td><td class="mm-sched-q"><ul>{qs}</ul></td></tr>'
                )
            elif pg["kind"] == "lab":
                cum += pg.get("minutes", 0)
                rows.append(
                    f'<tr class="mm-sched-lab"><td class="mm-sched-ep"><span class="mm-ep-num">Lab {pg["number"]}</span><a href="labs/{escape(Path(pg["href"]).name)}">{escape(pg["title"])}</a>'
                    f'<br><span class="mm-small">{escape(pg["duration"])}</span></td>'
                    f'<td class="mm-sched-time">{fmt_minutes(cum)}</td><td class="mm-sched-q">{md_inline(pg["summary"])}</td></tr>'
                )
            elif pg["kind"] == "quiz":
                rows.append(
                    f'<tr><td class="mm-sched-ep"><span class="mm-ep-num">Quiz</span><a href="{escape(Path(pg["href"]).name)}">{escape(pg["title"])}</a></td>'
                    f'<td class="mm-sched-time">{fmt_minutes(cum)}</td><td class="mm-sched-q">Ten questions covering the whole chapter.</td></tr>'
                )
        rows.append("</tbody></table>")
        (GEN / f"{cid}-schedule.md").write_text("\n".join(rows) + "\n", encoding="utf8")
        # labs
        cards = ['<!-- GENERATED by scripts/build_course_data.py -->', '<div class="mm-cards">']
        for lid in ch["labs"]:
            pg = course["pages"][lid]
            nb = pg.get("notebook")
            btns = ""
            if nb:
                colab = f"https://colab.research.google.com/github/{{GITHUB_REPO}}/blob/{{GITHUB_BRANCH}}/{pg['student_ipynb']}"
                btns = (
                    f'<a class="mm-btn mm-btn-sm mm-btn-primary" href="{colab}" data-mm-colab>Open in Colab</a>'
                    f'<a class="mm-btn mm-btn-sm" href="labs/{nb}.ipynb" download>Download .ipynb</a>'
                    f'<a class="mm-btn mm-btn-sm" href="labs/{nb}-solutions.html">View solutions</a>'
                )
            cards.append(
                f'<div class="mm-card mm-lab-card"><p class="mm-kicker">Lab {pg["number"]}, {escape(pg["duration"])}</p>'
                f'<h3><a href="labs/{escape(Path(pg["href"]).name)}">{escape(pg["title"])}</a></h3>'
                f'<p>{md_inline(pg["summary"])}</p>'
                + (f'<p class="mm-small">Dataset: {md_inline(pg["dataset"])}</p>' if pg.get("dataset") else "")
                + f'<div class="mm-card-actions">{btns}</div></div>'
            )
        cards.append("</div>")
        (GEN / f"{cid}-labs.md").write_text("\n".join(cards) + "\n", encoding="utf8")
        # key points
        kp = ['<!-- GENERATED by scripts/build_course_data.py -->']
        kp_all = [f'### Chapter {ch["number"]}: {ch["title"]}', ""]
        for eid in ch["episodes"]:
            pg = course["pages"][eid]
            rel_from_chapter = Path(pg["href"]).name
            rel_from_root = pg["href"]
            kp.append(f'#### {pg["label"]} [{pg["title"]}]({rel_from_chapter})')
            kp_all.append(f'#### {pg["label"]} [{pg["title"]}](/{rel_from_root})')
            kp.append("")
            kp_all.append("")
            for k in pg["keypoints"]:
                kp.append(f"- {k}")
                kp_all.append(f"- {k}")
            kp.append("")
            kp_all.append("")
        (GEN / f"{cid}-keypoints.md").write_text("\n".join(kp) + "\n", encoding="utf8")
        all_kp.extend(kp_all)
    (GEN / "all-keypoints.md").write_text("\n".join(all_kp) + "\n", encoding="utf8")


def write_metro(course: dict) -> None:
    """Roadmap as a metro map: one coloured line per Part, chapters as stations.

    The stretch of each line that reaches written chapters is "lit" (full colour, a soft glow, and a
    pulse of light that travels along it); planned stretches are unlit. All motion is CSS or SVG
    animation, so the map works without JavaScript, and assets/scss/_mm-rules.scss switches it off
    for readers who ask for reduced motion.
    """
    x0, spacing, row_h, top = 70, 170, 118, 56
    width = x0 + 4 * spacing + 90
    height = top + row_h * (len(course["parts"]) - 1) + 80
    out = [
        "<!-- GENERATED by scripts/build_course_data.py -->",
        '<div class="mm-metro">',
        f'<svg viewBox="0 0 {width} {height}" aria-labelledby="mm-metro-title mm-metro-desc" xmlns="http://www.w3.org/2000/svg">',
        '<title id="mm-metro-title">Course roadmap</title>',
        '<desc id="mm-metro-desc">Four coloured lines, one per Part, with chapters as stations. Lit, filled stations are available; dashed stations are coming soon.</desc>',
        '<defs><filter id="mm-glow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="4"/></filter></defs>',
    ]
    for i, part in enumerate(course["parts"]):
        y = top + i * row_h
        colour = f"var({ACCENT_VAR[part['accent']]})"
        chapters = [course["chapters"][c] for c in part["chapters"]]
        n = len(chapters)
        x_start, x_end = x0 - 14, x0 + (n - 1) * spacing
        built = [j for j, ch in enumerate(chapters) if not ch["stub"]]
        # the lit stretch runs from the start of the line to the last written chapter
        last_built = max(built) if built else None
        lit_end = None if last_built is None else (x_end + 14 if last_built == n - 1 else x0 + last_built * spacing)
        out.append(f'<g class="mm-part" style="color:{colour};--i:{i}">')
        out.append(f'<text class="mm-line-label" x="{x0 + 4}" y="{y - 26}" fill="currentColor">Part {part["roman"]}: {escape(part["title"])}</text>')
        if lit_end is not None:
            lit_d = f"M{x_start} {y} H{lit_end}"
            out.append(f'<path class="mm-metro-halo" pathLength="1" stroke="currentColor" filter="url(#mm-glow)" d="{lit_d}"/>')
            out.append(f'<path class="mm-metro-line lit" pathLength="1" stroke="currentColor" d="{lit_d}"/>')
            if lit_end < x_end + 14:
                out.append(f'<path class="mm-metro-line unlit" pathLength="1" stroke="currentColor" d="M{lit_end} {y} H{x_end + 14}"/>')
        else:
            out.append(f'<path class="mm-metro-line unlit" pathLength="1" stroke="currentColor" d="M{x_start} {y} H{x_end + 14}"/>')
        if i + 1 < len(course["parts"]):
            # transfer connector: out past the last station label, down, back left between the two rows,
            # and down into the start of the next line (clear of both rows' labels)
            ny = y + row_h
            out.append(
                f'<path class="mm-metro-link" pathLength="1" stroke="currentColor" '
                f'd="M{x_end + 14} {y} h24 q16 0 16 16 v34 q0 16 -16 16 H{x0 + 2} q-16 0 -16 16 V{ny}"/>'
            )
        for j, ch in enumerate(chapters):
            x = x0 + j * spacing
            cls = "mm-station " + ("soon" if ch["stub"] else "built")
            desc = f'<desc>Chapter {ch["number"]}: {escape(ch["title"])}' + (", coming soon" if ch["stub"] else "") + "</desc>"
            words, lines, cur = ch["short"].split(), [], ""
            for w in words:
                if len(cur) + len(w) + 1 > 18 and cur:
                    lines.append(cur)
                    cur = w
                else:
                    cur = (cur + " " + w).strip()
            if cur:
                lines.append(cur)
            tspans = "".join(f'<tspan x="{x}" dy="{0 if k == 0 else 14}">{escape(l)}</tspan>' for k, l in enumerate(lines))
            halo = f'<circle class="mm-station-halo" filter="url(#mm-glow)" cx="{x}" cy="{y}" r="17" fill="currentColor"/>' if not ch["stub"] else ""
            out.append(
                f'<a class="{cls}" href="{ch["href"]}" style="--j:{j}">{desc}{halo}'
                f'<circle class="mm-station-dot" cx="{x}" cy="{y}" r="12" stroke="currentColor"/>'
                f'<text class="mm-station-num" x="{x}" y="{y + 4}" text-anchor="middle">{ch["number"]}</text>'
                f'<text class="mm-station-label" x="{x}" y="{y + 32}" text-anchor="middle">{tspans}</text>'
                "</a>"
            )
        if lit_end is not None:
            # a pulse of light travelling along the lit stretch, then resting, every six seconds
            motion = (f'<animateMotion path="M{x_start} {y} H{lit_end}" begin="2s" dur="6s" repeatCount="indefinite" '
                      'calcMode="linear" keyPoints="0;1;1" keyTimes="0;0.5;1"/>')
            fade = ('<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;0.06;0.44;0.52;1" '
                    'begin="2s" dur="6s" repeatCount="indefinite"/>')
            out.append(f'<circle class="mm-metro-spark-glow" filter="url(#mm-glow)" r="11" fill="currentColor" opacity="0">{motion}{fade}</circle>')
            out.append(f'<circle class="mm-metro-spark" r="4" opacity="0">{motion}{fade}</circle>')
        out.append("</g>")
    out.append("</svg></div>")
    legend = (
        '<p class="mm-metro-legend"><span><i class="built"></i> available now</span><span><i class="soon"></i> coming soon</span>'
        '<span>Click a station to open the chapter.</span><span class="mm-metro-hint">Swipe sideways to see the whole map.</span></p>'
    )
    out.append(legend)
    (GEN / "metro.md").write_text("\n".join(out) + "\n", encoding="utf8")
    # part list for the home page
    pl = ['<!-- GENERATED by scripts/build_course_data.py -->', '<ul class="mm-part-list">']
    for part in course["parts"]:
        chs = ", ".join(
            (f'<a href="{course["chapters"][c]["href"]}">{course["chapters"][c]["number"]} {escape(course["chapters"][c]["short"])}</a>'
             if not course["chapters"][c]["stub"] else f'<span class="mm-small">{course["chapters"][c]["number"]} {escape(course["chapters"][c]["short"])}</span>')
            for c in part["chapters"]
        )
        pl.append(f'<li><span class="mm-part-swatch" style="background:var({ACCENT_VAR[part["accent"]]})"></span><span><strong>Part {part["roman"]}: {escape(part["title"])}.</strong> {chs}</span></li>')
    pl.append("</ul>")
    (GEN / "home-parts.md").write_text("\n".join(pl) + "\n", encoding="utf8")


def main() -> int:
    course = discover()
    (GEN / "course.json").write_text(json.dumps(course, indent=1, ensure_ascii=False), encoding="utf8")
    write_sidebar(course)
    write_chapter_includes(course)
    write_metro(course)
    n_ep = sum(1 for p in course["pages"].values() if p["kind"] == "episode")
    if os.environ.get("QUARTO_PROJECT_SCRIPT_QUIET") != "1":
        print(f"[build_course_data] {len(course['chapters'])} chapters, {n_ep} episodes, {len(course['pages'])} pages -> _generated/, _sidebar.yml")
    return 0


if __name__ == "__main__":
    sys.exit(main())
