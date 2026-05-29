---
name: sci-paper-writing
description: >
  Produce publication-quality scientific research papers following top-tier conference conventions (CVPR, ICCV, NeurIPS, ICML, ICLR, ACL, EMNLP).
  This skill should be used when the user asks to write, draft, generate, or format a scientific research paper, empirical study, or academic manuscript.
  Triggers include: "draft a research paper", "generate an academic paper", "format my manuscript", "help with my thesis chapter",
  or any request involving scientific writing with sections like Introduction, Method, Experiments, and References.
  Supports DOCX, PDF, and PPTX outputs. Defaults to DOCX for collaborative drafting and PDF for camera-ready submission.
agent_created: true
---

# SCI Paper Writing Skill

## Overview

Produce complete, publication-quality scientific research papers with proper structure, typography, figures, tables, equations, and references. The skill follows conventions extracted from the ResNet paper (He et al., CVPR 2016 Best Paper) and generalized for computer vision, machine learning, and broader scientific domains.

## Workflow Decision Tree

```
User request to write/format a scientific paper
├── Determine target venue and output format
│   ├── Default: DOCX (collaborative drafting)
│   └── Camera-ready: PDF (LaTeX template)
│   └── Oral presentation: PPTX (slides derived from paper)
├── Load reference contracts
│   ├── references/structure_contract.md   → Section hierarchy, narrative arcs
│   ├── references/style_contract.md       → Typography, layout, math notation
│   ├── references/figure_table_guidelines.md → Figures, tables, equations rules
│   └── references/latex_template.md       → LaTeX template with packages, figures, tables, bibliography
├── Execute writing pipeline
│   ├── Phase 1: Plan (venue, page limit, section budget)
│   ├── Phase 2: Chart assets (generate all figures and tables)
│   ├── Phase 3: Draft all sections (narrative logic per contract)
│   ├── Phase 4: Polish (typography, cross-references, formatting)
│   └── Phase 5: Convert to requested output format
└── Deliver complete paper with all required sections and visual elements
```

## Phase 1: Plan

Before writing, establish three parameters:

| Parameter | Decision | Notes |
|:---|:---|:---|
| Target venue | CVPR/ICCV/ECCV / NeurIPS/ICML/ICLR / ACL/EMNLP / Other | Determines page limit, columns, abstract length |
| Output format | DOCX / PDF / PPTX | DOCX for drafting, PDF for submission, PPTX for talks |
| Page budget | 8-12 pages (full paper) | Allocate: Intro 15-20%, Method 30-40%, Experiments 35-45% |

Venue-specific parameters:

| Venue | Page limit | Columns | Abstract length |
|:---|:---|:---|:---|
| CVPR/ICCV/ECCV | 8 + refs | 2 | ~150 words |
| NeurIPS/ICML | 9 + refs | 1 | ~200 words |
| ICLR | 8 + refs | 2 | ~150 words |
| ACL/EMNLP | 8 + refs | 2 | ~150 words |

## Phase 2: Chart Assets

Generate ALL figures and tables before drafting text. Every visual element must be referenced in the text BEFORE it appears.

**Required figures** (typical count: 3-7):
- System architecture / conceptual diagram
- Training curves (loss + accuracy)
- Performance comparison bar charts
- Ablation study results
- Temporal or qualitative analysis

**Required tables** (typical count: 2-4):
- Architecture specification table
- Main results comparison table
- Ablation study table
- Cross-dataset generalization table

**Chart generation rules** (see references/figure_table_guidelines.md for full details):
- Use colorblind-safe palette: #E41A1C, #4DAF4A, #377EB8, #984EA3, #FF7F00
- Figure captions BELOW the figure
- Table captions ABOVE the table
- Best results in tables in **bold**
- Figure fonts >= 8pt for readability
- Prefer vector formats (SVG, PDF) over raster

## Phase 3: Draft All Sections

Follow the complete section hierarchy. ALL sections must be present. Do NOT skip any subsection.

```
Title (centered, 17pt bold)
├── Authors & Affiliations (centered)
├── Abstract (single-column, 1 paragraph, ~150-200 words)
├── 1. Introduction (1-1.5 pages, 5-7 paragraphs)
│   ├── P1: Domain context
│   ├── P2: Sub-domain & trend
│   ├── P3: The problem / gap
│   ├── P4: Empirical evidence of the gap
│   ├── P5: Proposed solution (high-level)
│   ├── P6: Contribution list (3-5 items)
│   └── P7: Paper roadmap (optional)
├── 2. Related Work (0.5-1 page, thematic subsections)
│   └── Theme A / Theme B / Theme C (not chronological)
├── 3. Method / Approach (2-3 pages) ← MUST HAVE ALL SUBSECTIONS
│   ├── 3.1 Core Formulation
│   ├── 3.2 Key Mechanism
│   ├── 3.3 Architecture / Design
│   └── 3.4 Implementation Details
├── 4. Experiments / Results (2.5-3.5 pages) ← MUST HAVE ALL SUBSECTIONS
│   ├── 4.1 Main Benchmark
│   ├── 4.2 Secondary Benchmark & Analysis
│   └── 4.3 Extension / Application
├── 5. Conclusion (0.3-0.5 pages)
│   ├── Summary
│   ├── Limitations (required since 2022)
│   └── Future Work (optional)
├── References (1 page, numbered [1]-[N])
└── Appendices A-C (optional)
```

**Critical rules** (see references/structure_contract.md for full narrative logic):
- Introduction must execute the "funnel" narrative arc: broad → narrow → contribution
- Related Work must be organized by theme, not by chronology
- Method section MUST have subsections 3.1-3.4; Experiments MUST have 4.1-4.3
- Every experimental claim follows Claim → Evidence → Interpretation pattern
- All figures/tables referenced BEFORE they appear on the page

## Phase 4: Polish

Apply typography and formatting per references/style_contract.md:

**Typography**:
- Body: Times New Roman 10pt (or NimbusRomNo9L-Regu equivalent)
- Headings: Bold, 12pt (section) / 10pt (subsection)
- Math: Computer Modern (CMMI, CMSY, CMR, CMEX)
- Line spacing: ~1.2x
- Paragraph indent: 1 em (first line)

**Layout** (double-column conference format):
- Paper: US Letter (8.5" x 11")
- Columns: 2, each ~3.25" (8.25 cm)
- Margins: 0.75" left/right, 0.75-1.0" top, 1.0-1.25" bottom

**Mathematical notation**:
- Scalars: italic lowercase ($x$, $\alpha$)
- Vectors: bold lowercase (**x**, **y**)
- Matrices: bold uppercase (**W**, **H**)
- Sets: calligraphic ($\mathcal{H}$, $\mathcal{F}$)
- Display equations: centered, numbered right: `(1)`, `(2)`, ...

**Citations**:
- In-text: `[n]` where n is reference number
- Multiple: `[1, 9]`, `[2-5]` (consecutive range)
- Reference list: `[n] Author(s). Title. Venue, Year.`
- Full author list for <=6 authors; "et al." for >=7

## Phase 5: Convert to Output Format

| Format | Tool/Method | Layout | Best For |
|:---|:---|:---|:---|
| DOCX | C# + OpenXML SDK or python-docx | Single column only | Collaborative drafting; advisor review |
| PDF | LaTeX (IEEEtran / CVPR / NeurIPS template) | True double column | Camera-ready submission |
| PPTX | Derive from paper sections | Slide layout | Oral presentation |

### Single-Column vs Double-Column

| Venue | Columns | Recommended Output | Figure Width |
|:---|:---|:---|:---|
| CVPR/ICCV/ECCV | 2 | LaTeX PDF | 3.25" (single), 6.75" (spanning) |
| NeurIPS/ICML | 1 | LaTeX PDF or DOCX | 5.5" |
| ICLR | 2 | LaTeX PDF | 3.25" (single), 6.75" (spanning) |
| ACL/EMNLP | 2 | LaTeX PDF | 3.25" (single), 6.75" (spanning) |

**Important**: python-docx does NOT natively support double-column layout. If the target venue requires double-column (CVPR, ICLR, ACL), generate a single-column DOCX for drafting, then convert to LaTeX for camera-ready submission. Do NOT attempt to fake double-column in DOCX — it will not match the venue template.

**DOCX generation specifics**:
- Use OpenXML SDK (C#) for full control over styling
- Define custom styles for Title, Heading1, Heading2, BodyText, Abstract, Caption
- Insert figures as Drawing objects with proper sizing
- Build tables with TableGrid and exact twips-based column widths
- Add header (paper title) and footer (page numbers)

### Figure Embedding — MANDATORY Rules

Every figure in the paper must satisfy ALL three conditions simultaneously:

1. **Textual reference**: The text must say "... as shown in Fig. N ..." BEFORE the figure appears
2. **Physical embed**: The image file must be inserted into the document using `doc.add_picture(path, width=...)` — NOT just referenced
3. **Caption follow**: Immediately after the embedded image, add the caption paragraph below it

**Insertion order must match citation order in the text**:

| Step | Text Location | Action | Example |
|:---|:---|:---|:---|
| 1 | Intro P4 mentions "Fig. 2" | Immediately after that paragraph, call `add_picture(fig2_path)` | Training curves |
| 2 | Intro P5 mentions "Fig. 1" | Immediately after that paragraph, call `add_picture(fig1_path)` | Architecture diagram |
| 3 | Sec 4.1 mentions "Fig. 3" | After the results paragraph, call `add_picture(fig3_path)` | Performance comparison |
| 4 | Sec 4.2 mentions "Fig. 4" | After the analysis paragraph, call `add_picture(fig4_path)` | Ablation study |
| 5 | Sec 4.3 mentions "Fig. 5" | After the extension paragraph, call `add_picture(fig5_path)` | Inference analysis |

**Image width guidelines**:
- Single-column layout: `width=Inches(3.25)`
- Double-column layout (full width): `width=Inches(6.75)`
- Standard default: `width=Inches(5.5)`

**CRITICAL**: Do NOT only write text references like "see Fig. 2" without embedding the actual image. The document must contain the visual element physically.

## Content Completeness Checklist

Before delivering, verify ALL of the following:

### Sections
- [ ] Title, Authors, Affiliations
- [ ] Abstract (single paragraph, ~150-200 words, contains background/problem/method/results/significance)
- [ ] 1. Introduction (5-7 paragraphs, funnel narrative)
- [ ] 2. Related Work (thematic subsections, explicit differentiation)
- [ ] 3. Method (ALL subsections: 3.1, 3.2, 3.3, 3.4)
- [ ] 4. Experiments (ALL subsections: 4.1, 4.2, 4.3)
- [ ] 5. Conclusion (summary + limitations)
- [ ] References (numbered [1]-[N], complete bibliography)

### Visual Elements
- [ ] ALL figures referenced in text BEFORE appearing
- [ ] ALL figures PHYSICALLY EMBEDDED in the document (not just text references)
- [ ] Figure image files exist at the specified paths before embedding
- [ ] Figure insertion order matches citation order in the text
- [ ] Figure width appropriate for layout (single-col 3.25", double-col 6.75")
- [ ] Figure captions BELOW each figure, self-contained
- [ ] ALL tables referenced in text BEFORE appearing
- [ ] Table captions ABOVE each table
- [ ] ALL equations numbered sequentially
- [ ] Best results in tables in **bold**
- [ ] Figure fonts >= 8pt

### Page Count
- [ ] Total pages match target venue (8-12 pages for full paper)
- [ ] No section unreasonably short or skipped
- [ ] Figures and tables distributed, not crammed

### Enhanced Features (v1.5+)
- [ ] Experimental data uploaded and charts auto-generated (if using data_to_charts.py)
- [ ] References auto-fetched from CrossRef/Semantic Scholar (if using reference_fetcher.py)
- [ ] DOCX pre-validation passed (if using docx_validator.py)
- [ ] LaTeX conversion completed (if using docx_to_latex.py)
- [ ] Interactive HTML generated (if using docx_to_html.py)
- [ ] Venue recommendation reviewed (if using venue_recommender.py)

## Enhanced Features (v1.5+)

The skill includes 6 additional scripts that extend the core workflow:

### 1. data_to_charts.py — Experimental Data → Publication Charts

Upload CSV/JSON experimental data, automatically infer chart type and generate SCI-quality figures.

```bash
python scripts/data_to_charts.py results.csv --output-dir ./charts --dpi 300
```

**Auto-detection rules**:
| Data Pattern | Detected Type | Output |
|:---|:---|:---|
| epoch/iteration + loss/accuracy | Training Curve | Line plot with smoothing |
| category labels + numeric metrics | Comparison Bar | Grouped bar chart |
| "ablation" / "variant" labels | Ablation Study | Single bar with baseline highlight |
| Two numeric columns | Scatter Plot | Scatter + trend line |

### 2. reference_fetcher.py — Auto Literature Retrieval

Fetch real references from CrossRef and Semantic Scholar by DOI, title, or keywords.

```bash
python scripts/reference_fetcher.py --doi "10.1109/CVPR.2016.90"
python scripts/reference_fetcher.py --query "deep reinforcement learning" -n 10
python scripts/reference_fetcher.py --file refs_queries.txt --expand
```

**Multi-round progressive search** (per references/search-strategy.md):
- Round 1: Exact DOI/Title lookup → direct fetch
- Round 2: Keyword search → top-N results
- Round 3: Citation network expansion → related papers

### 3. docx_validator.py — Automated Quality Inspection

Scan DOCX and validate 6 dimensions before submission.

```bash
python scripts/docx_validator.py paper.docx
python scripts/docx_validator.py paper.docx --format json --output report.json
```

| Check | What it validates | Severity |
|:---|:---|:---:|
| Image Embedding | All "Fig. N" refs have physical images | ERROR |
| Table Bold | Best results in comparison tables are bold | WARNING |
| Reference Continuity | [1]-[N] sequential without gaps | ERROR |
| Equation Numbering | (1), (2), (3)... sequential | WARNING |
| Caption Placement | Figure captions below, table captions above | INFO |
| Section Completeness | Method has 3.1-3.4, Experiments has 4.1-4.3 | ERROR |

### 4. docx_to_latex.py — Camera-Ready LaTeX Conversion

Convert DOCX to LaTeX using venue-specific templates.

```bash
python scripts/docx_to_latex.py paper.docx --venue cvpr
python scripts/docx_to_latex.py paper.docx --venue neurips --output paper.tex
```

**Supported venues**: CVPR, NeurIPS, ICML, ICLR, ACL
**Fallback**: When pandoc is unavailable, uses native python-docx parser

### 5. docx_to_html.py — Interactive Web Paper

Convert paper to interactive HTML with dark mode, figure zoom, equation expand, reference jumps.

```bash
python scripts/docx_to_html.py paper.docx --theme dark
```

**Interactive features**:
- Dark/light mode toggle (persisted in localStorage)
- Click figures to zoom in/out
- Click equations to expand/collapse details
- Click [N] references to jump to bibliography
- Hover table rows for highlight
- Responsive design (mobile/tablet)

### 6. venue_recommender.py — Smart Venue Recommendation

Recommend top-5 conferences/journals based on paper topic and results.

```bash
python scripts/venue_recommender.py --topic "deep RL for bipedal locomotion"
python scripts/venue_recommender.py --topic "NLP" --results "SOTA on GLUE 89.4%"
```

**Database**: 15 venues (CVPR, NeurIPS, ICML, ICLR, ACL, EMNLP, AAAI, IJCAI, RSS, CoRL, ICRA, TMLR, Nature MI, IEEE T-PAMI)

## References

This skill includes the following reference documents. Load the relevant file when the user request touches that domain:

- **references/structure_contract.md** — Section hierarchy, narrative arc per section, paragraph-level patterns (Claim-Evidence-Interpretation), citation density rules, cross-reference conventions.
- **references/style_contract.md** — Typography system (fonts, sizes, weights), page layout (double-column vs single-column), heading hierarchy, mathematical notation conventions, color palette, header/footer rules, citation and reference formatting.
- **references/figure_table_guidelines.md** — Figure numbering and caption placement, caption writing rules, figure layout specs, **figure embedding rules** (physical embed vs text reference), figure types, table formatting, equation environment rules, visual asset workflow, common anti-patterns.
- **references/code_templates.py** — Production-ready python-docx code skeletons: `setup_document()`, `add_figure()`, `add_table_with_caption()`, `add_equation()`, `add_section_heading()`, `set_header_footer()`. Copy these functions into your generation script.
- **references/latex_template.md** — LaTeX template reference for camera-ready PDF output. Covers document classes per venue, minimal double-column template, essential packages, pgfplots figure generation, table best practices with booktabs, bibliography style, and compilation commands.

## Example Trigger Phrases

- "Write a research paper about X"
- "Draft an empirical study on Y"
- "Help me format my manuscript for Z conference"
- "Generate a paper with Introduction, Method, Experiments"
- "Create an academic paper in Word format"
- "Write my thesis chapter on machine learning"
- "Produce a camera-ready PDF for CVPR"
