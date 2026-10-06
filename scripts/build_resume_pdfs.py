#!/usr/bin/env python3
"""Build the three resume PDFs in public/ from src/data/resume.json.

    python3 -m venv .venv-resume && .venv-resume/bin/pip install reportlab
    .venv-resume/bin/python scripts/build_resume_pdfs.py

resume.json is the single source for /resume and these PDFs, so a title or
bullet change is one edit. Before this script existed the PDFs were made by
hand outside the repo and went stale (they still said Senior after the Staff
promotion while the site said Staff).

Outputs:
  public/Chris_De_La_Garza_Resume.pdf        full, dark
  public/Chris_De_La_Garza_Resume_Light.pdf  full, light
  public/Chris_De_La_Garza_Resume_1Page.pdf  one page, light, onepage bullets only
"""
import json
import re
import sys
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (HRFlowable, KeepTogether, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "src/data/resume.json").read_text())

THEMES = {
    "light": dict(bg=None, text="#333333", strong="#111111", dim="#777777",
                  accent="#2e7d32", rule="#2e7d32", sep="#dddddd"),
    "dark": dict(bg="#101010", text="#d6d6d6", strong="#f2f2f2", dim="#8c8c8c",
                 accent="#d9a520", rule="#3a9a6a", sep="#2a2a2a"),
}


def inline(s, t):
    """resume.json inline markup -> ReportLab paragraph markup."""
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\[([^\]]+)\]\((https?:[^)]+)\)",
               lambda m: f'<link href="{m.group(2)}">{m.group(1)}</link>', s)
    return s


def styles(t, compact):
    base = 8.4 if compact else 9.4
    lead = base * (1.24 if compact else 1.32)
    k = 0.92 if compact else 1.0  # shrinks headings on the 1-page cut
    def mk(name, **kw):
        opts = dict(fontName="Helvetica", fontSize=base, leading=lead,
                    textColor=HexColor(t["text"]), alignment=TA_LEFT)
        opts.update(kw)
        return ParagraphStyle(name, **opts)
    return dict(
        name=mk("name", fontName="Helvetica-Bold", fontSize=24 * k, leading=28 * k,
                textColor=HexColor(t["strong"])),
        title=mk("title", fontSize=12.5, leading=16, textColor=HexColor(t["accent"])),
        contact=mk("contact", fontSize=8.6, leading=11, textColor=HexColor(t["dim"])),
        honors=mk("honors", fontName="Helvetica-Bold", fontSize=9.6, leading=13,
                  textColor=HexColor(t["accent"])),
        body=mk("body"),
        section=mk("section", fontName="Helvetica-Bold", fontSize=9.6, leading=12,
                   textColor=HexColor(t["accent"]), spaceBefore=4, spaceAfter=4),
        company=mk("company", fontName="Helvetica-Bold", fontSize=11.5 * k, leading=14 * k,
                   textColor=HexColor(t["accent"])),
        role=mk("role", fontName="Helvetica-Bold", fontSize=10 * k, leading=13 * k,
                textColor=HexColor(t["strong"])),
        dates=mk("dates", fontSize=8.6, leading=11, textColor=HexColor(t["dim"]),
                 spaceAfter=2),
        bullet=mk("bullet", leftIndent=12, firstLineIndent=-8, spaceAfter=1),
        stack=mk("stack", spaceAfter=2),
    )


def build(out, theme, onepage):
    t = THEMES[theme]
    S = styles(t, compact=onepage)
    d = DATA
    story = []

    story += [
        Paragraph(d["name"], S["name"]),
        Paragraph(d["title"], S["title"]),
        Paragraph(" · ".join([d["email"], d["linkedin"], f"github.com/{d['github']}",
                              d["location_short"]]), S["contact"]),
        Spacer(1, 3),
        Paragraph("  |  ".join(d["honors"]), S["honors"]),
        Spacer(1, 4),
        HRFlowable(width="100%", thickness=1.2, color=HexColor(t["rule"]), spaceAfter=6),
        Paragraph(d["summary"], S["body"]),
        HRFlowable(width="100%", thickness=0.5, color=HexColor(t["dim"]),
                   spaceBefore=6, spaceAfter=6),
        Paragraph("[ EXPERIENCE ]", S["section"]),
    ]

    for j, job in enumerate(d["experience"]):
        block = [Paragraph(job["company"], S["company"])]
        for role in job["roles"]:
            bullets = [b for b in role["bullets"] if b.get("onepage") or not onepage]
            if not bullets:
                continue
            block += [Paragraph(role["title"], S["role"]), Paragraph(role["dates"], S["dates"])]
            if role.get("intro") and not onepage:
                block.append(Paragraph(inline(role["intro"], t), S["body"]))
            block += [Paragraph("– " + inline(b["text"], t), S["bullet"]) for b in bullets]
            block.append(Spacer(1, 1 if onepage else 3))
        story.append(KeepTogether(block))
        if j < len(d["experience"]) - 1:
            story.append(HRFlowable(width="100%", thickness=0.4, color=HexColor(t["sep"]),
                                    spaceBefore=1 if onepage else 2,
                                    spaceAfter=2 if onepage else 4))

    story += [
        HRFlowable(width="100%", thickness=0.5, color=HexColor(t["dim"]),
                   spaceBefore=4, spaceAfter=4),
        Paragraph("[ TECH STACK ]", S["section"]),
    ]
    for g in d["stack"]:
        story.append(Paragraph(
            f'<font name="Helvetica-Bold" color="{t["accent"]}">{inline(g["group"], t)}:</font> '
            + " · ".join(inline(x, t) for x in g["items"]), S["stack"]))

    e = d["education"]
    edu = [Paragraph(f"<b>{inline(e['school'], t)}</b>", S["body"]),
           Paragraph(f"{inline(e['degree'], t)} · {e['years']}", S["body"]),
           Paragraph(inline(e["honors"], t), S["body"])]
    certs = [Paragraph(f'<font name="Helvetica-Bold" color="{t["accent"]}">Certifications</font>', S["body"])]
    certs += [Paragraph("&gt; " + inline(c, t), S["body"]) for c in d["certifications"]]
    table = Table([[edu, certs]], colWidths=["62%", "38%"])
    table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                               ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    story += [
        HRFlowable(width="100%", thickness=0.5, color=HexColor(t["dim"]),
                   spaceBefore=4, spaceAfter=4),
        Paragraph("[ EDUCATION &amp; CERTIFICATIONS ]", S["section"]),
    ]
    if onepage:
        # One line on the 1-page cut; the two-column table costs three lines.
        story.append(Paragraph(
            f"<b>{inline(e['school'], t)}</b> · {inline(e['degree'], t)} · {e['years']}"
            f'  |  <font name="Helvetica-Bold" color="{t["accent"]}">Certification:</font> '
            + ", ".join(inline(c, t) for c in d["certifications"]), S["body"]))
    else:
        story.append(table)

    def paint(canvas, doc):
        if t["bg"]:
            canvas.saveState()
            canvas.setFillColor(HexColor(t["bg"]))
            canvas.rect(0, 0, LETTER[0], LETTER[1], stroke=0, fill=1)
            canvas.restoreState()

    margin = 0.55 * inch if onepage else 0.75 * inch
    doc = SimpleDocTemplate(str(out), pagesize=LETTER, leftMargin=margin, rightMargin=margin,
                            topMargin=margin, bottomMargin=margin,
                            title=f"{d['name']} — Resume", author=d["name"])
    doc.build(story, onFirstPage=paint, onLaterPages=paint)
    return doc.page


if __name__ == "__main__":
    pub = ROOT / "public"
    results = {
        "Chris_De_La_Garza_Resume.pdf": build(pub / "Chris_De_La_Garza_Resume.pdf", "dark", False),
        "Chris_De_La_Garza_Resume_Light.pdf": build(pub / "Chris_De_La_Garza_Resume_Light.pdf", "light", False),
        "Chris_De_La_Garza_Resume_1Page.pdf": build(pub / "Chris_De_La_Garza_Resume_1Page.pdf", "light", True),
    }
    for name, pages in results.items():
        print(f"{name}: {pages} page(s)")
    if results["Chris_De_La_Garza_Resume_1Page.pdf"] != 1:
        sys.exit("1-page resume spilled onto a second page: trim onepage bullets in resume.json")
