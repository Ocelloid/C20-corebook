# AGENTS.md — C20-corebook

> **Changeling: The Dreaming 20th Anniversary Edition** — Russian translation project.
> 482-page tabletop RPG sourcebook (White Wolf / Onyx Path).
> Read this file fully before starting any work.

---

## 1. Project Overview

This repository contains the complete pipeline for translating **Changeling: The Dreaming 20th Anniversary Edition** from English to Russian, plus a published wiki built with Quartz.

- **Source:** `source.pdf` (~52 MB, 482 pages, ~642 images)
- **Translation tool:** Claude in Cursor IDE, ~40 pages/hour
- **Terminology:** Strict glossary of 706 terms (`glossary_terms.csv`)
- **Published wiki:** https://ctd.ocelloid.com (Quartz v4, Vercel)
- **Language of this repo's content:** Russian

---

## 2. Repository Structure

```
C20-corebook/
├── source.pdf                     # Original book — DO NOT MODIFY
├── pages/                         # 482 page_XXX.md — raw extracted text (flat)
├── chapters/                      # 18 sections, each with page subdirs + merged EN files
│   └── XX_section_name/
│       ├── page_XXX/              # page_XXX.md, page_XXX.pdf, images
│       └── XX_section_name.md    # merged English source
├── ru/                            # Russian translations — 18 files (00–17)
├── editing/                       # Manual editing workspace
├── glossary_terms.csv             # Machine-readable glossary (English,Russian)
├── Глоссарий.md                   # Full glossary with contexts and categories
├── Правила перевода.md            # Translation methodology
├── Правила использования Глоссария.md  # Glossary usage prompt
├── Правила пополнения Глоссария.md     # How to add new terms
├── scripts/                       # Python processing pipeline
├── ctd-quartz/                    # Quartz wiki site (separate git repo inside)
├── drive/                         # Logseq vault (untracked, experimental)
├── .cursor/rules/                 # Agent rules (always active)
└── fonts.md                       # PDF font analysis
```

### Data pipeline

```
source.pdf
  → scripts/process_pdf_complete.py
  → pages/page_XXX.md              (extracted text per page)
  → chapters/XX_*/XX_*.md          (merged English by section)
  → ru/XX_*.md                     (Russian translation)
  → ctd-quartz/content/            (wiki notes)
```

---

## 3. Sections (18 total)

| # | Folder | Pages | Status |
|---|--------|-------|--------|
| 00 | credits_and_dedication | 001–007 | Done |
| 01 | contents | 008–011 | Done |
| 02 | book_one_childling | 012–013 | Done |
| 03 | prelude_both_sides_of_the_coin | 014–024 | Done |
| 04 | introduction | 025–030 | Done |
| 05 | chapter_one_a_world_of_darkness | 031–082 | Done |
| 06 | chapter_two_the_kithain | 083–138 | Up to p.119 |
| 07 | chapter_three_character_creation_and_traits | 139–192 | In progress |
| 08 | chapter_four_arts_and_realms | 193–240 | In progress |
| 09 | chapter_five_rules | 241–250 | In progress |
| 10 | chapter_six_systems_and_drama | 251–298 | In progress |
| 11 | chapter_seven_the_dreaming | 299–326 | In progress |
| 12 | chapter_eight_storytelling | 327–344 | In progress |
| 13 | chapter_nine_nightmares_and_stranger_things | 345–391 | In progress |
| 14 | appendix_gallain | 392–452 | In progress |
| 15 | appendix_enchanted | 453–463 | In progress |
| 16 | kickstarter_backers | — | Stub |
| 17 | character_sheets | — | Stub |

Editing progress: **119 / 463 pages (26%)**.

---

## 4. Glossary — CRITICAL

> **Never translate a game term without checking `glossary_terms.csv` first.**
> This is the single most important rule in this project.

### Files

| File | Purpose |
|------|---------|
| `glossary_terms.csv` | 706 terms, `English,Russian` format — for grep/script lookup |
| `Глоссарий.md` | Same terms with category context — for human reading |

### How to check a term

```bash
grep -i "Sovereign" glossary_terms.csv
# → Sovereign,Правление
```

**Check EVERY non-standard English word and every game term before translating.**
Do not rely on memory — the glossary takes precedence.

### Critical terms (common mistakes)

| English | Correct Russian | Wrong |
|---------|----------------|-------|
| Arts | Искусства | ~~Сферы~~ |
| Realms | Королевства | ~~Сферы~~ |
| Cantrips | Заговоры | ~~Заклинания~~ |
| Bunks | Банки | ~~Бунки~~ |
| Sovereign | Правление | ~~Суверен~~ |
| Freehold | Фригольд | ~~Свободное владение~~ |
| Balefire | Огонь Очага | ~~Злой огонь~~ |
| Changeling | Подменыш | — |
| Dreaming | Греза | — |
| Chrysalis | Кризалис | ~~Хризалида~~ |
| Kithain | Китэйн | — |
| Glamour | Гламур | — |
| Banality | Банальность | — |
| Childling | Дитя | — |
| Wilder | Юноша | — |
| Grump | Старец | — |
| Seelie Court | Благой Двор | — |
| Unseelie Court | Неблагой Двор | — |
| Motley | Клика | — |
| Troupe | Труппа | — |
| Storyteller | Рассказчик | — |
| Chronicle | Хроника | — |

### Fairy terminology

- ✅ **фея, фейский, фейская, фейское** 
- ❌ ~~фейри, фейрийский, фэйрийский~~

---

## 5. Translation Workflow

### Where to work

- **Source (read only):** `chapters/XX_*/XX_*.md` — merged English text
- **Output (write here):** `ru/XX_*.md` — Russian translation
- **Reference per page:** `chapters/XX_*/page_XXX/page_XXX.md`

### Rules

1. **Translate 2 pages at a time** — prevents context overload
2. **Always check glossary** before translating any game term
3. **Join broken sentences** — PDF extraction splits lines mid-sentence; fix them
4. **Check page boundaries** — a sentence from page N may continue on page N+1; check both pages before writing
5. **Do not summarize** in chat — just translate and append to the `ru/` file
6. **Append, do not rewrite** — always add new text at the end of the `ru/` file

### Handling broken sentences (example)

```
# WRONG — two separate lines from PDF extraction:
"...central Asian and Middle Eastern cultural references"
"from books. Thus we can build a bridge..."

# CORRECT — joined:
"...central Asian and Middle Eastern cultural references from books. Thus we can build a bridge..."
```

### Typical prompt pattern

```
Continue translating section 08 from the next pair of pages.
Check every non-standard term in the glossary.
Append new text at the end of the ru/ file.
```

### Full rules reference

- `.cursor/rules/translation-workflow.mdc` — step-by-step process
- `.cursor/rules/changeling-translation.mdc` — terminology rules (always active)
- `Правила перевода.md` — detailed methodology

---

## 6. Quartz Wiki Site

**URL:** https://ctd.ocelloid.com  
**Location:** `ctd-quartz/` (separate git repository, not a submodule)  
**Framework:** Quartz v4.5.1, deployed on Vercel

### Key config (`ctd-quartz/quartz.config.ts`)

- `pageTitle: "CtD"`
- `baseUrl: "ctd.ocelloid.com"`
- ObsidianFlavoredMarkdown with wikilinks enabled
- Analytics: Plausible

### Content structure (`ctd-quartz/content/` — 44 notes)

```
content/
├── index.md                        # Introduction (from 04_introduction)
├── Подменыши.md, Греза.md, Лексикон.md
├── География/
│   ├── Королевство Конкордия.md
│   ├── Конкордия/ (8 kingdom notes)
│   └── Европа/ (Albion, Iberia, Neustria...)
└── Общество подменышей/
    ├── Дворы.md, Дома.md, Мир Тьмы.md
    ├── Обличья/ (Дитя, Юноша, Старец)
    └── Роды/ (15 kith notes: Satyr, Boggan, Troll...)
```

Notes use wikilinks: `[[Подменыши|фей]]`, frontmatter `title:`.

### Build & serve locally

```bash
cd ctd-quartz
npx quartz build --serve -d content
```

### Wikilink helper

```bash
python ctd-quartz/obsidian_link_creator.py
```

Auto-generates wikilinks with Russian inflections and aliases.

---

## 7. Python Scripts (`scripts/`)

```bash
pip install -r scripts/requirements.txt
# Dependencies: PyMuPDF, Pillow, markdown, tqdm
```

| Script | Purpose |
|--------|---------|
| `process_pdf_complete.py` | Full pipeline: split + extract text + images |
| `split_pdf_pages.py` | Split source.pdf into 482 page PDFs |
| `extract_text.py` | Extract text from page PDFs → pages/ |
| `extract_images.py` | Extract images from page PDFs |
| `copy_pages.py` | Distribute pages/ into chapters/ structure |
| `merge_sections.py` | Merge per-page MDs into one section file |
| `clean_section_files.py` | Remove duplicate headers from merged files |
| `glossary_tools.py analyze` | Analyze glossary structure |
| `glossary_tools.py validate` | Validate glossary entries |
| `glossary_tools.py fix` | Auto-fix all glossary issues |
| `check_pdf.py` | Analyze source PDF metadata |
| `extract_fonts.py` | Extract font info from PDFs |

---

## 8. Do NOT Touch

| Path | Reason |
|------|--------|
| `source.pdf` | Original book — never modify |
| `pages/` | Generated from PDF — regenerate with scripts if needed |
| `chapters/*/page_XXX/` | Generated per-page data |
| `chapters/*/XX_*.md` | Generated merged English — source reference only |
| `ctd-quartz/node_modules/` | npm packages |
| `ctd-quartz/.quartz-cache/` | Build cache |
| `.obsidian/` | Obsidian vault config |
| `drive/` | Logseq vault (untracked, experimental) |

---

## 9. Working Language

- **All agent responses:** Russian
- **File content:** Russian (translations, wiki notes)
- **Code and filenames:** English
- **Glossary CSV:** English → Russian mapping

---

## 10. Quick Start Checklist

When starting any translation work:

- [ ] Open `glossary_terms.csv` in a side panel for reference
- [ ] Identify which section to continue (`ru/` files — check last translated page)
- [ ] Read both source pages (EN) fully before translating
- [ ] grep every game term before writing its translation
- [ ] Check for sentence breaks at page boundaries
- [ ] Append to `ru/XX_*.md` — never overwrite existing content
