# Structure & Narrative Contract — NLP / ACL Venues

Extracted from representative NLP papers — BERT (Devlin et al., NAACL 2019) and
Transformer (Vaswani et al., NeurIPS 2017) — and cross-referenced with the
official ACL formatting guidelines (acl-org.github.io/ACLPUB).

> **When to use**: User specifies an NLP venue (ACL, EMNLP, NAACL, TACL) or
> a NeurIPS submission with NLP content.
> **When NOT to use**: CV venues (use structure_contract_cv.md instead).

---

## 1. Official ACL Formatting Requirements

These are from the official [ACLPUB formatting guide](https://acl-org.github.io/ACLPUB/formatting.html).
Violating these will cause desk rejection.

### Paper Geometry

| Setting | Value |
|:---|:---|
| Paper size | A4 (21cm × 29.7cm) — **NOT** US Letter |
| Margins | 2.5cm on all sides |
| Columns | 2 (default) |
| Body font | Times Roman |
| Body font size | 11pt |
| Line spacing | Single (1.0) |
| Title | 15pt bold, Title Case |
| Author names | 12pt bold, centered |
| Abstract | 10pt, ≤200 words, plain text only |

### Required Sections (ACL-specific)

| Section | Required? | Page count | Rules |
|:---|:---|:---|:---|
| Abstract | Yes | — | ≤200 words, no LaTeX commands |
| Limitations | **Yes (mandatory)** | Not counted | After Conclusion, before References. NO extra experiments, figures, or tables. |
| Ethical Considerations | Encouraged | Not counted | Same position as Limitations. No extra experiments. |
| Acknowledgments | Final version only | Not counted | Review version must omit |
| Appendices | Optional | Not counted | After References |

### Citation Format

| Rule | ACL |
|:---|:---|
| Style | **Author-year** (APA-like) — NOT numbered `[n]` |
| In-text | `Gusfield (1997)` or `(Gusfield, 1997)` |
| Multiple authors | `(Author et al., Year)` for 3+ authors |
| DOI | **MANDATORY** for every reference |
| Reference list order | Alphabetical by first author surname |

### Page Limits

| Paper type | Review | Final |
|:---|:---|:---|
| Long paper | 8 pages | 9 pages |
| Short paper | 4 pages | 5 pages |
| References | Unlimited | Unlimited |

---

## 2. NLP Paper Section Hierarchy

Based on BERT (NAACL 2019) and Transformer (NeurIPS 2017), NLP papers do **NOT**
follow the rigid "Method 3.1-3.4 / Experiments 4.1-4.3" pattern common to CV.
Instead, the structure is more flexible:

### Typical NLP Paper Structure

```
Title (15pt bold, Title Case, centered)
├── Authors & Affiliations (12pt bold, centered)
├── Abstract (≤200 words, 10pt)
│   └── Problem + Method + Key Results + Significance
├── 1. Introduction (1-1.5 pages)
│   ├── P1: Domain consensus / widely accepted fact
│   ├── P2: Existing methods and their limitations
│   ├── P3: Core gap or inefficiency (often computational/semantic)
│   ├── P4: Proposed approach (conceptual level)
│   ├── P5: Key contributions (3-5 bullets)
│   └── P6: Paper outline (optional)
├── 2. Related Work / Background (0.5-1 page)
│   └── Organized by METHODOLOGY PARADIGM, not by task:
│       ├── Paradigm A: supervised / feature-based / rule-based
│       ├── Paradigm B: unsupervised / fine-tuning / pre-training
│       └── Paradigm C: emerging / transfer learning / hybrid
├── 3. Method / Model (2-3 pages) ← Flexible naming
│   ├── 3.1 Problem Formulation (task definition + notation)
│   ├── 3.2 Model Architecture (core design)
│   ├── 3.3 Training / Optimization (loss function, optimizer, regularization)
│   └── 3.4 Implementation Details (hardware, hyperparameters)
├── 4. Experiments / Results (2-3 pages)
│   ├── 4.1 Main Benchmark (primary dataset, SOTA comparison)
│   ├── 4.2 Analysis / Ablation (what matters, what doesn't)
│   └── 4.3 Additional Tasks / Generalization (if applicable)
├── 5. Conclusion (0.3-0.5 pages)
│   ├── Summary of findings
│   ├── Limitations ← MANDATORY for ACL venues
│   └── Future work (optional)
├── Ethical Considerations (encouraged, not counted)
├── Acknowledgments (final version only)
├── References (alphabetical, author-year format, DOI required)
└── Appendices (optional, not counted)
```

### Key Structural Differences from CV Papers

| Dimension | CV (ResNet → structure_contract_cv.md) | NLP (BERT/Transformer) |
|:---|:---|:---|
| Introduction opening | From experimental phenomenon: "Deeper networks are harder to train" | From domain consensus: "Language model pre-training has been shown to be effective" or "RNNs have been firmly established as SOTA" |
| Related Work | Often by task (detection, segmentation, tracking) | By **methodology paradigm** (supervised, pre-training, transfer) |
| Method section numbering | Fixed 3.1-3.4 | Flexible; can be named after the proposed method (e.g., "3. BERT") |
| Training details | Typically under Method/Implementation | Often a **separate sub-section** or even separate top-level section (Transformer has "5. Training") |
| Ablation studies | Usually under Experiments (Section 4.2) | Can be a **separate top-level section** (BERT has "5. Ablation Studies") |
| Limitations | Optional/rare | **MANDATORY** for ACL venues |
| Ethical considerations | Rarely required | **Encouraged** by ACL |
| Math/Formulas | Architecture diagrams dominate | **Formula-heavy**: equations for loss, attention, probability distributions |
| Paper size | US Letter (CVPR) | **A4** (ACL/EMNLP/NAACL) |
| Citation style | Numbered `[n]` | **Author-year** `(Author, Year)` |

---

## 3. Narrative Logic — How NLP Introductions Work

### The NLP Introduction Arc

Unlike CV's "funnel" (broad field → sub-field → gap → contribution), NLP
introductions tend to follow a **consensus → limitation → solution** pattern:

```
BERT Introduction pattern (abstracted from actual paragraphs):

P1 [Consensus]: "X has been shown to be effective for Y."
    → Establishes what the field agrees on

P2 [Methods gap]: "Existing approaches fall into two categories: A and B.
    A does this but can't do that. B does that but can't do this."
    → Identifies structural limitations in existing paradigms

P3 [Core problem]: "Therefore, there is a need for C that combines the
    strengths of both while avoiding their weaknesses."
    → States the fundamental challenge

P4 [Proposed solution]: "We propose [Method Name], which addresses this
    by [key innovation 1], [key innovation 2], and [key innovation 3]."
    → Introduces the method

P5 [Contributions]: "Our contributions are: (1) ..., (2) ..., (3) ..."
    → Explicit numbered list (very common in NLP)

P6 [Roadmap]: "The rest of this paper is organized as follows..."
    → Optional but common
```

### Transformer Introduction Pattern

```
P1: "RNNs have been firmly established as SOTA for sequence transduction..."
    → Acknowledges existing paradigm

P2: "This inherently sequential nature precludes parallelization..."
    → Identifies fundamental limitation (computational, not performance)

P3: [Implied gap] → We propose a new architecture that doesn't use recurrence

P4: "The Transformer is the first transduction model relying entirely
    on self-attention..."
    → Clear "first-of-its-kind" positioning
```

### Rules for NLP Introductions

1. **Start with consensus, not surprise.** Don't say "surprisingly, X fails" — say "X has been widely used, but it struggles with Y."
2. **Identify structural limitations**, not just performance gaps. The limitation should be fundamental (sequential computation, unidirectionality, fixed context).
3. **Contributions as numbered list.** NLP papers almost always use "Our contributions are: (1)...(2)...(3)..." — more explicit than CV.
4. **Task definition early.** Define the task formally (input → output) in the Introduction or early Method section.
5. **Formula may appear in Introduction.** Unlike CV (formulas only in Method), NLP papers sometimes include a key equation in the Introduction to illustrate the core idea.

---

## 4. Related Work Organization — NLP Convention

NLP papers organize Related Work by **methodology paradigm**, not by task:

### BERT's Related Work Structure (as example)

```
2. Related Work
   2.1 Unsupervised Feature-based Approaches
       → Word embeddings → sentence embeddings → ELMo (bidirectional LSTM)
       → Limitation: "shallow bidirectional", not true deep bidirection

   2.2 Unsupervised Fine-tuning Approaches
       → Early work → recent advances → OpenAI GPT
       → Limitation: "left-to-right only", unidirectional

   2.3 Transfer Learning from Supervised Data
       → NLP: NLI → MT transfer
       → CV: ImageNet → downstream (cross-domain analogy)
```

### Rules for NLP Related Work

1. **Group by paradigm**, not by task. "Pre-training methods", "Attention mechanisms", "Sequence modeling" — not "Machine translation", "Question answering", "Summarization".
2. **Each paradigm ends with its limitation** — the limitation should directly motivate your work.
3. **3-4 paradigms max.** Too many = unfocused.
4. **Include at least one cross-domain analogy** (e.g., "similar to how ImageNet pre-training revolutionized CV...").

---

## 5. Method Section — NLP Conventions

NLP Method sections are **less rigid** than CV. Key differences:

| Aspect | CV (ResNet) | NLP (BERT/Transformer) |
|:---|:---|:---|
| Section name | "3. Method" or "3. Approach" | Can be method name: "3. BERT", "3. Transformer" |
| First subsection | Architecture overview | **Problem formulation** (task definition + notation) |
| Visual element | Architecture diagram (Fig. 1) | Formula + architecture diagram |
| Training details | Under Implementation (3.4) | **Prominent**: can be own subsection or top-level section |
| Formula density | Moderate | **High**: attention, loss, probability |

### Required Elements in NLP Method Section

1. **Task definition with notation**: "Given input X = (x₁, ..., xₙ), the model predicts Y..."
2. **Core innovation explained conceptually** before mathematically
3. **Key equations with proper numbering**: `(1)`, `(2)`, ...
4. **Training procedure**: loss function, optimizer, learning rate schedule, batch size
5. **Implementation**: hardware (GPU type/count), training time, library versions

---

## 6. Experiments — NLP Conventions

### Common NLP Evaluation Patterns

| Pattern | Example | When to use |
|:---|:---|:---|
| SOTA comparison table | GLUE benchmark (BERT) | Multiple tasks, single metric per task |
| Ablation analysis | Effect of pre-training tasks (BERT §5.1) | Understanding which components matter |
| Scaling analysis | Effect of model size (BERT §5.2) | Showing model scales well |
| Generalization test | English constituency parsing (Transformer §6.3) | Showing method is not task-specific |
| Qualitative analysis | Attention visualization | Understanding what the model learns |

### NLP-Specific Evaluation Considerations

1. **Statistical significance**: Include standard deviation or confidence intervals. More common in NLP than CV.
2. **Multiple benchmarks**: NLP papers typically evaluate on 3-5 different benchmarks (GLUE, SQuAD, SWAG, etc.)
3. **Human evaluation**: Common for generation tasks (BLEU + human judgment)
4. **Error analysis**: Qualitative examples of model outputs are standard

---

## 7. Writing Style Conventions

### Language and Tone

| Element | NLP Convention |
|:---|:---|
| Method naming | Capitalized proper noun: "BERT", "Transformer", "ELMo" |
| Task naming | "machine translation", "question answering" (lowercase) |
| Dataset naming | "GLUE benchmark", "SQuAD v1.1" |
| First person | "We propose..." (acceptable and common) |
| Acronyms | Define on first use: "Bidirectional Encoder Representations from Transformers (BERT)" |

### Formula Conventions

- Display equations: centered, numbered right `(1)`, `(2)`, ...
- Inline variables: `$x$`, `$\alpha$`, `$\mathcal{L}$`
- Attention notation: `$\text{Attention}(Q, K, V) = \text{softmax}(\frac{QK^T}{\sqrt{d_k}})V$`
- Probability notation: `$P(y|x)$`, `$\mathbb{E}_{x \sim \mathcal{D}}[\cdot]$`

---

## 8. Verification Checklist

When generating an NLP paper, verify ALL of the following:

### Format (ACL Official)
- [ ] Paper size: A4 (NOT US Letter)
- [ ] Margins: 2.5cm on all sides
- [ ] Body font: Times Roman, 11pt
- [ ] Abstract: ≤200 words, plain text only
- [ ] Citations: author-year format (NOT [n])
- [ ] Every reference has DOI
- [ ] Limitations section: present, after Conclusion, no extra experiments

### Structure
- [ ] Introduction starts from domain consensus (not experimental phenomenon)
- [ ] Contributions listed as numbered items (1)...(2)...(3)...
- [ ] Related Work organized by methodology paradigm (not by task)
- [ ] Each paradigm subsection ends with its limitation → motivates your work
- [ ] Task formally defined with notation before Method details
- [ ] Training details explicitly stated (optimizer, LR, batch size, hardware)
- [ ] Ablation studies clearly separated from main results

### Visual Elements
- [ ] All figures referenced before appearing
- [ ] All figures physically embedded in document
- [ ] Figure captions below figures
- [ ] Table captions above tables
- [ ] Best results in tables in bold
- [ ] Formulas numbered sequentially (1), (2), (3)...

### Content Quality
- [ ] Method limitation is fundamental (structural), not superficial (hyperparameter)
- [ ] SOTA comparison includes recent (≤2 years) baselines
- [ ] Ablation isolates one variable at a time
- [ ] Statistical significance reported where applicable

---

## 9. References

This contract is based on:

1. **BERT** (Devlin et al., NAACL 2019): Introduction structure, Related Work organization, Method/BERT section, separate Ablation Studies chapter, separate Appendix with detailed configurations.
2. **Transformer** (Vaswani et al., NeurIPS 2017): Introduction structure, Background chapter (serving as Related Work), Model Architecture with multi-level subsections, separate Training chapter, Why Self-Attention motivational section.
3. **ACL Official Formatting Guide** (acl-org.github.io/ACLPUB): Paper geometry (A4, 2.5cm margins), font specifications (Times Roman 11pt), mandatory Limitations, author-year citations, DOI requirement, page limits.
