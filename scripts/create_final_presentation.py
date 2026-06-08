"""Create the final project PowerPoint deck.

This script writes a lightweight editable PPTX using the Open XML presentation
format directly. It avoids private data and uses only aggregate project figures.
"""

from __future__ import annotations

import html
import zipfile
from dataclasses import dataclass, field
from pathlib import Path


EMU_PER_INCH = 914400
SLIDE_W = 13.333333
SLIDE_H = 7.5
SLIDE_W_EMU = int(SLIDE_W * EMU_PER_INCH)
SLIDE_H_EMU = int(SLIDE_H * EMU_PER_INCH)

OUT = Path("slides/final_presentation.pptx")
FIG_COUNTS = Path("figures/ma_group_significance_counts.png")
FIG_TOP = Path("figures/ma_top_channel_pvalues.png")

BG = "F7F7F2"
INK = "17202A"
MUTED = "566573"
TEAL = "0B6E69"
BLUE = "4C78A8"
ORANGE = "F58518"
GREEN = "54A24B"
PALE_TEAL = "DDEDEA"
PALE_BLUE = "EAF1F8"
PALE_ORANGE = "FFF0DF"
PALE_GREEN = "EAF4E8"


@dataclass
class TextBox:
    x: float
    y: float
    w: float
    h: float
    lines: list[str]
    size: int = 24
    color: str = INK
    bold: bool = False
    fill: str | None = None
    align: str = "l"


@dataclass
class Rect:
    x: float
    y: float
    w: float
    h: float
    fill: str
    line: str | None = None


@dataclass
class Image:
    path: Path
    x: float
    y: float
    w: float
    h: float


@dataclass
class Slide:
    title: str
    subtitle: str | None = None
    boxes: list[TextBox] = field(default_factory=list)
    rects: list[Rect] = field(default_factory=list)
    images: list[Image] = field(default_factory=list)
    section: str = "Final project"


def emu(value: float) -> int:
    return int(value * EMU_PER_INCH)


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def text_runs(lines: list[str], size: int, color: str, bold: bool) -> str:
    paragraphs = []
    for line in lines:
        bullet = line.startswith("- ")
        text = line[2:] if bullet else line
        mar_l = ' marL="285750" indent="-171450"' if bullet else ""
        paragraphs.append(
            f"""
            <a:p>
              <a:pPr{mar_l}/>
              <a:r>
                <a:rPr lang="en-US" sz="{size * 100}"{' b="1"' if bold else ''}>
                  <a:solidFill><a:srgbClr val="{color}"/></a:solidFill>
                </a:rPr>
                <a:t>{esc(text)}</a:t>
              </a:r>
            </a:p>"""
        )
    return "\n".join(paragraphs)


def shape_xml(idx: int, box: TextBox) -> str:
    fill = (
        f"<a:solidFill><a:srgbClr val=\"{box.fill}\"/></a:solidFill>"
        if box.fill
        else "<a:noFill/>"
    )
    return f"""
    <p:sp>
      <p:nvSpPr>
        <p:cNvPr id="{idx}" name="TextBox {idx}"/>
        <p:cNvSpPr txBox="1"/>
        <p:nvPr/>
      </p:nvSpPr>
      <p:spPr>
        <a:xfrm>
          <a:off x="{emu(box.x)}" y="{emu(box.y)}"/>
          <a:ext cx="{emu(box.w)}" cy="{emu(box.h)}"/>
        </a:xfrm>
        <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
        {fill}
        <a:ln><a:noFill/></a:ln>
      </p:spPr>
      <p:txBody>
        <a:bodyPr wrap="square" lIns="100000" tIns="60000" rIns="100000" bIns="60000"/>
        <a:lstStyle/>
        {text_runs(box.lines, box.size, box.color, box.bold)}
      </p:txBody>
    </p:sp>"""


def rect_xml(idx: int, rect: Rect) -> str:
    line = (
        f"<a:ln w=\"10000\"><a:solidFill><a:srgbClr val=\"{rect.line}\"/></a:solidFill></a:ln>"
        if rect.line
        else "<a:ln><a:noFill/></a:ln>"
    )
    return f"""
    <p:sp>
      <p:nvSpPr>
        <p:cNvPr id="{idx}" name="Rect {idx}"/>
        <p:cNvSpPr/>
        <p:nvPr/>
      </p:nvSpPr>
      <p:spPr>
        <a:xfrm>
          <a:off x="{emu(rect.x)}" y="{emu(rect.y)}"/>
          <a:ext cx="{emu(rect.w)}" cy="{emu(rect.h)}"/>
        </a:xfrm>
        <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
        <a:solidFill><a:srgbClr val="{rect.fill}"/></a:solidFill>
        {line}
      </p:spPr>
      <p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody>
    </p:sp>"""


def image_xml(idx: int, image: Image, rel_id: str) -> str:
    return f"""
    <p:pic>
      <p:nvPicPr>
        <p:cNvPr id="{idx}" name="{esc(image.path.name)}"/>
        <p:cNvPicPr/>
        <p:nvPr/>
      </p:nvPicPr>
      <p:blipFill>
        <a:blip r:embed="{rel_id}"/>
        <a:stretch><a:fillRect/></a:stretch>
      </p:blipFill>
      <p:spPr>
        <a:xfrm>
          <a:off x="{emu(image.x)}" y="{emu(image.y)}"/>
          <a:ext cx="{emu(image.w)}" cy="{emu(image.h)}"/>
        </a:xfrm>
        <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
      </p:spPr>
    </p:pic>"""


def slide_xml(slide: Slide, slide_num: int) -> tuple[str, str]:
    rects = [
        Rect(0, 0, SLIDE_W, SLIDE_H, BG),
        Rect(0, 0, 0.18, SLIDE_H, TEAL),
    ] + slide.rects
    boxes = [
        TextBox(0.55, 0.25, 3.0, 0.28, [slide.section.upper()], 9, TEAL, True),
        TextBox(0.55, 0.55, 8.9, 0.78, [slide.title], 28, INK, True),
    ]
    if slide.subtitle:
        boxes.append(TextBox(0.58, 1.22, 9.4, 0.42, [slide.subtitle], 13, MUTED))
    boxes.extend(slide.boxes)
    boxes.append(TextBox(12.25, 7.0, 0.6, 0.25, [str(slide_num)], 9, MUTED))

    parts: list[str] = []
    next_id = 2
    for rect in rects:
        parts.append(rect_xml(next_id, rect))
        next_id += 1
    for box in boxes:
        parts.append(shape_xml(next_id, box))
        next_id += 1
    rels = []
    for i, image in enumerate(slide.images, start=1):
        rel_id = f"rId{i}"
        parts.append(image_xml(next_id, image, rel_id))
        next_id += 1
        rels.append(
            f'<Relationship Id="{rel_id}" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
            f'Target="../media/{image.path.name}"/>'
        )

    xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
       xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
       xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr>
        <a:xfrm>
          <a:off x="0" y="0"/><a:ext cx="{SLIDE_W_EMU}" cy="{SLIDE_H_EMU}"/>
          <a:chOff x="0" y="0"/><a:chExt cx="{SLIDE_W_EMU}" cy="{SLIDE_H_EMU}"/>
        </a:xfrm>
      </p:grpSpPr>
      {''.join(parts)}
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>"""
    rel_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  {''.join(rels)}
</Relationships>"""
    return xml, rel_xml


def make_slides() -> list[Slide]:
    return [
        Slide(
            "MA-Related fNIRS Brain Activation Differences",
            "Lower- vs upper-grade children during morphological awareness processing",
            section="Title",
            rects=[
                Rect(8.8, 0, 4.53, 7.5, PALE_TEAL),
                Rect(9.45, 1.0, 2.7, 2.7, TEAL),
                Rect(10.15, 3.7, 1.75, 1.75, ORANGE),
            ],
            boxes=[
                TextBox(
                    0.75,
                    2.0,
                    7.5,
                    1.1,
                    ["MA-Related fNIRS Brain Activation Differences Between Lower- and Upper-Grade Children"],
                    30,
                    INK,
                    True,
                ),
                TextBox(
                    0.78,
                    3.45,
                    6.7,
                    0.8,
                    ["A Python-based fNIRS analysis pipeline using MNE-Python, developed with reference to a MATLAB/nirs-toolbox workflow."],
                    16,
                    MUTED,
                ),
                TextBox(0.78, 6.55, 4.0, 0.35, ["BrainHack final project"], 13, TEAL, True),
            ],
        ),
        Slide(
            "Why MA and fNIRS?",
            "The project connects a developmental language question with reproducible brain data analysis.",
            boxes=[
                TextBox(0.7, 1.8, 3.6, 3.2, [
                    "Morphological awareness",
                    "- Important for children's language and reading development",
                    "- Relevant for comparing developmental stages",
                ], 17, INK, fill=PALE_BLUE),
                TextBox(4.7, 1.8, 3.6, 3.2, [
                    "fNIRS brain data",
                    "- Measures task-related hemodynamic responses",
                    "- Suitable for child participant studies",
                ], 17, INK, fill=PALE_TEAL),
                TextBox(8.7, 1.8, 3.6, 3.2, [
                    "Project question",
                    "- Do grade groups differ during MA processing?",
                    "- Can the analysis be rebuilt in Python?",
                ], 17, INK, fill=PALE_ORANGE),
            ],
        ),
        Slide(
            "Research Question",
            "Do lower- and upper-grade children show different fNIRS activation patterns during MA processing?",
            boxes=[
                TextBox(0.8, 2.0, 5.4, 1.8, ["Primary condition contrast", "MA - Control"], 24, INK, True, PALE_TEAL, "c"),
                TextBox(6.8, 2.0, 5.0, 1.8, ["Primary group contrast", "(G4_6 MA-Control) - (G1_3 MA-Control)"], 20, INK, True, PALE_BLUE),
                TextBox(1.0, 4.7, 10.7, 0.7, ["Main interpretation target: developmental-stage-related differences in MA-related HbO activation."], 18, TEAL, True),
            ],
        ),
        Slide(
            "Data and Conditions",
            "Local SNIRF fNIRS dataset from child participants; raw data are not uploaded to GitHub.",
            rects=[Rect(0.8, 1.8, 3.4, 2.8, PALE_BLUE), Rect(4.7, 1.8, 3.4, 2.8, PALE_TEAL), Rect(8.6, 1.8, 3.4, 2.8, PALE_ORANGE)],
            boxes=[
                TextBox(1.1, 2.05, 2.8, 1.8, ["G1_3", "59 participants", "Grades 1-3"], 20, INK, True),
                TextBox(5.0, 2.05, 2.8, 1.8, ["G4_6", "72 participants", "Grades 4-6"], 20, INK, True),
                TextBox(8.9, 2.05, 2.8, 1.8, ["Total", "131 participants", "SNIRF files"], 20, INK, True),
                TextBox(0.85, 5.05, 10.8, 1.0, ["Event mapping: 1 = MA, 2 = PA, 3 = Control. All participants had complete MA and Control markers."], 17, MUTED),
            ],
        ),
        Slide(
            "New Skills and Tools",
            "The course requirement emphasizes learning a new brain-data-analysis skill.",
            boxes=[
                TextBox(0.8, 1.8, 5.5, 3.8, [
                    "MNE-Python / MNE-NIRS",
                    "- SNIRF loading in Python",
                    "- fNIRS preprocessing",
                    "- Subject-level GLM",
                    "- Group-level MA contrasts",
                ], 17, INK, fill=PALE_TEAL),
                TextBox(6.8, 1.8, 5.2, 3.8, [
                    "MATLAB reference workflow",
                    "- Original nirs-toolbox analysis as reference",
                    "- Short-separation regression alignment",
                    "- Validation plan for preprocessed time series",
                ], 17, INK, fill=PALE_BLUE),
            ],
        ),
        Slide(
            "Python Analysis Pipeline",
            "A script-based workflow preserves the full path from SNIRF files to aggregate figures.",
            boxes=[
                TextBox(0.7, 1.7, 2.55, 2.0, ["1", "Load SNIRF", "Validate MA/Control events"], 16, INK, True, PALE_BLUE),
                TextBox(3.45, 1.7, 2.55, 2.0, ["2", "Preprocess", "OD -> HbO/HbR, trim task window"], 16, INK, True, PALE_TEAL),
                TextBox(6.2, 1.7, 2.55, 2.0, ["3", "First-level GLM", "MA, PA, Control + short regressors"], 16, INK, True, PALE_ORANGE),
                TextBox(8.95, 1.7, 2.55, 2.0, ["4", "Group analysis", "Long-HbO MA-Control comparison"], 16, INK, True, PALE_GREEN),
                TextBox(1.0, 5.0, 10.5, 0.9, ["Scripts: load_data.py -> preprocess_fnirs.py -> first_level_glm.py -> group_analysis.py -> visualization.py"], 16, TEAL, True),
            ],
        ),
        Slide(
            "MATLAB-to-Python Alignment",
            "The MATLAB pipeline is a methodological reference, not the main research question.",
            boxes=[
                TextBox(0.8, 1.75, 5.3, 3.9, [
                    "Aligned in Python",
                    "- Short-separation regressors added",
                    "- Long-HbO-only group analysis",
                    "- Same MA-Control analysis focus",
                ], 17, INK, fill=PALE_GREEN),
                TextBox(6.7, 1.75, 5.4, 3.9, [
                    "Remaining differences",
                    "- MATLAB AR-IRLS vs Python ar1",
                    "- MATLAB mixed-effects model vs current t-tests",
                    "- Possible HRF/model implementation differences",
                ], 17, INK, fill=PALE_ORANGE),
            ],
        ),
        Slide(
            "Pipeline Completion Summary",
            "The current Python workflow runs end to end on the local dataset.",
            boxes=[
                TextBox(0.8, 1.75, 3.6, 2.8, ["SNIRF loading", "131 / 131", "All MA/Control events complete"], 21, INK, True, PALE_BLUE),
                TextBox(4.65, 1.75, 3.6, 2.8, ["Preprocessing", "131 / 131", "13 negative-intensity warnings retained as QC caveat"], 19, INK, True, PALE_TEAL),
                TextBox(8.5, 1.75, 3.6, 2.8, ["First-level GLM", "131 / 131", "Short-separation regressors enabled"], 20, INK, True, PALE_GREEN),
                TextBox(1.0, 5.25, 10.5, 0.7, ["Group-level analysis: 32 long-distance HbO channels, three MA-Control comparisons."], 17, MUTED),
            ],
        ),
        Slide(
            "Group-Level MA Results",
            "No long-HbO channel survived FDR or Bonferroni correction in the current Python analysis.",
            images=[Image(FIG_COUNTS, 0.8, 1.6, 11.3, 5.2)],
        ),
        Slide(
            "Exploratory Top Channels",
            "Top channels are descriptive only; corrected results were not significant.",
            images=[Image(FIG_TOP, 0.55, 1.55, 11.9, 5.3)],
        ),
        Slide(
            "Open Science, Reproducibility, and Privacy",
            "The repository is organized so the process is visible while child-participant data remain protected.",
            boxes=[
                TextBox(0.8, 1.75, 5.5, 3.8, [
                    "Shared in GitHub",
                    "- Analysis scripts",
                    "- Documentation and report draft",
                    "- Aggregate figures",
                    "- Slide outline and deck",
                ], 17, INK, fill=PALE_BLUE),
                TextBox(6.8, 1.75, 5.2, 3.8, [
                    "Excluded from GitHub",
                    "- Raw SNIRF data",
                    "- Subject-level derivatives",
                    "- Participant information",
                    "- Local MATLAB validation exports",
                ], 17, INK, fill=PALE_TEAL),
            ],
        ),
        Slide(
            "Limitations and Next Steps",
            "The main story is MA activation comparison; the method story explains how close Python is to MATLAB.",
            boxes=[
                TextBox(0.8, 1.75, 5.4, 4.2, [
                    "Limitations",
                    "- Python and MATLAB outputs are not yet numerically identical",
                    "- MATLAB preprocessing export still needs to be run",
                    "- Current Python group model is simpler than MATLAB mixed effects",
                ], 17, INK, fill=PALE_ORANGE),
                TextBox(6.8, 1.75, 5.4, 4.2, [
                    "Next steps",
                    "- Validate MATLAB vs MNE preprocessed HbO/HbR time series",
                    "- Consider Python mixed-effects group modeling",
                    "- Finalize website report/notebook",
                    "- Record the final project video",
                ], 17, INK, fill=PALE_GREEN),
            ],
        ),
    ]


def content_types(n_slides: int, images: list[Path]) -> str:
    slide_overrides = "\n".join(
        f'<Override PartName="/ppt/slides/slide{i}.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for i in range(1, n_slides + 1)
    )
    image_defaults = ""
    if any(image.suffix.lower() == ".png" for image in images):
        image_defaults += '<Default Extension="png" ContentType="image/png"/>'
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  {image_defaults}
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  {slide_overrides}
</Types>"""


def root_rels() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""


def presentation_xml(n_slides: int) -> str:
    slide_ids = "\n".join(
        f'<p:sldId id="{255 + i}" r:id="rId{i}"/>'
        for i in range(1, n_slides + 1)
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
                xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
                xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId{n_slides + 1}"/></p:sldMasterIdLst>
  <p:sldIdLst>{slide_ids}</p:sldIdLst>
  <p:sldSz cx="{SLIDE_W_EMU}" cy="{SLIDE_H_EMU}" type="wide"/>
  <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>"""


def presentation_rels(n_slides: int) -> str:
    rels = [
        f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>'
        for i in range(1, n_slides + 1)
    ]
    rels.append(
        f'<Relationship Id="rId{n_slides + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>'
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  {''.join(rels)}
</Relationships>"""


def slide_master_xml() -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld><p:spTree>
    <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
    <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{SLIDE_W_EMU}" cy="{SLIDE_H_EMU}"/><a:chOff x="0" y="0"/><a:chExt cx="{SLIDE_W_EMU}" cy="{SLIDE_H_EMU}"/></a:xfrm></p:grpSpPr>
  </p:spTree></p:cSld>
  <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
  <p:sldLayoutIdLst><p:sldLayoutId id="1" r:id="rId1"/></p:sldLayoutIdLst>
  <p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles>
</p:sldMaster>"""


def slide_layout_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank" preserve="1">
  <p:cSld name="Blank"><p:spTree>
    <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
    <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
  </p:spTree></p:cSld>
</p:sldLayout>"""


def theme_xml() -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="MA fNIRS Theme">
  <a:themeElements>
    <a:clrScheme name="MA fNIRS">
      <a:dk1><a:srgbClr val="{INK}"/></a:dk1><a:lt1><a:srgbClr val="{BG}"/></a:lt1>
      <a:dk2><a:srgbClr val="{MUTED}"/></a:dk2><a:lt2><a:srgbClr val="FFFFFF"/></a:lt2>
      <a:accent1><a:srgbClr val="{TEAL}"/></a:accent1><a:accent2><a:srgbClr val="{BLUE}"/></a:accent2>
      <a:accent3><a:srgbClr val="{ORANGE}"/></a:accent3><a:accent4><a:srgbClr val="{GREEN}"/></a:accent4>
      <a:accent5><a:srgbClr val="7A5195"/></a:accent5><a:accent6><a:srgbClr val="BC5090"/></a:accent6>
      <a:hlink><a:srgbClr val="{BLUE}"/></a:hlink><a:folHlink><a:srgbClr val="7A5195"/></a:folHlink>
    </a:clrScheme>
    <a:fontScheme name="Aptos"><a:majorFont><a:latin typeface="Aptos Display"/></a:majorFont><a:minorFont><a:latin typeface="Aptos"/></a:minorFont></a:fontScheme>
    <a:fmtScheme name="Simple"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst><a:lnStyleLst><a:ln w="10000"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst><a:effectStyleLst><a:effectStyle/></a:effectStyleLst><a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst></a:fmtScheme>
  </a:themeElements>
</a:theme>"""


def doc_props() -> tuple[str, str]:
    core = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
                   xmlns:dc="http://purl.org/dc/elements/1.1/"
                   xmlns:dcterms="http://purl.org/dc/terms/"
                   xmlns:dcmitype="http://purl.org/dc/dcmitype/"
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>MA-Related fNIRS Brain Activation Differences</dc:title>
  <dc:creator>BrainHack final project</dc:creator>
</cp:coreProperties>"""
    app = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
            xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Python Open XML generator</Application>
</Properties>"""
    return core, app


def build_pptx() -> None:
    slides = make_slides()
    images = sorted({image.path for slide in slides for image in slide.images})
    for image in images:
        if not image.exists():
            raise FileNotFoundError(f"Missing figure: {image}")
    OUT.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED) as pptx:
        pptx.writestr("[Content_Types].xml", content_types(len(slides), images))
        pptx.writestr("_rels/.rels", root_rels())
        pptx.writestr("ppt/presentation.xml", presentation_xml(len(slides)))
        pptx.writestr("ppt/_rels/presentation.xml.rels", presentation_rels(len(slides)))
        pptx.writestr("ppt/slideMasters/slideMaster1.xml", slide_master_xml())
        pptx.writestr(
            "ppt/slideMasters/_rels/slideMaster1.xml.rels",
            """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>
</Relationships>""",
        )
        pptx.writestr("ppt/slideLayouts/slideLayout1.xml", slide_layout_xml())
        pptx.writestr("ppt/theme/theme1.xml", theme_xml())
        core, app = doc_props()
        pptx.writestr("docProps/core.xml", core)
        pptx.writestr("docProps/app.xml", app)

        for i, slide in enumerate(slides, start=1):
            xml, rels = slide_xml(slide, i)
            pptx.writestr(f"ppt/slides/slide{i}.xml", xml)
            pptx.writestr(f"ppt/slides/_rels/slide{i}.xml.rels", rels)
        for image in images:
            pptx.write(image, f"ppt/media/{image.name}")

    print(f"Wrote {OUT}")


if __name__ == "__main__":
    build_pptx()
