# syedbasher.github.io

Personal website of Syed Abul Basher. Plain static HTML and CSS, no JavaScript,
no build dependencies beyond Python 3.

---

## Two things to add before you publish

1. **`Syed_Basher_CV.pdf`** — put it in the repository root, spelled exactly like that
   (capitals matter; GitHub Pages is case-sensitive). Every "Curriculum Vitae — PDF"
   button and the CV link in the footer already point at it. Replacing the file later
   updates the site automatically; nothing needs rebuilding.

2. **`assets/portrait.jpg`** — the zip contains a plain grey placeholder so the pages
   never look broken. Replace it with your photograph, cropped to 4:5 (portrait). The
   one on your Google Sites page works well; around 800×1000 pixels is plenty. Keep the
   filename the same and the page picks it up.

`assets/favicon.svg` in this zip is a simple placeholder. If you would rather keep the
favicon already in your repository, just delete this one from the zip before uploading.

---

## What is in here

| File | What it is |
|---|---|
| `index.html` | Home |
| `research.html` | Full publication list — 73 published articles and 92 entries in all |
| `writing.html` | 62 newspaper columns, 2007 to date |
| `advisory.html` | Advisory and commissioned work |
| `about.html` | Education and positions |
| `applied-work.html` | Redirects to `advisory.html`, so old links keep working |
| `404.html` | Not-found page, styled like the rest of the site |
| `assets/styles.css` | The whole stylesheet |
| `sitemap.xml`, `robots.txt` | For search engines |
| `.nojekyll` | Tells GitHub Pages to serve the files as they are |
| `site-source/` | The data file and the build script (see below) |

Every HTML page is generated. **Do not edit the HTML by hand** — your changes would be
overwritten the next time the site is built. Edit `site-source/data.json` instead.

---

## Adding a publication or a column

Open `site-source/data.json`. It has two lists.

A publication is five fields:

```json
["Published articles", "2026", "Title of the paper",
 "with A. Coauthor. Journal Name, Vol. 12, pp. 1–20.",
 "https://doi.org/..."]
```

The first field must be one of: `Published articles`, `Working papers`,
`Book chapters and book reviews`, `Unpublished papers`, `Dissertation`.
The year is used only for `Published articles`; leave it `""` elsewhere.
Leave the URL `""` if there is nothing to link to — the title then appears as plain text.

A column is four fields:

```json
["18 April 2026", "Title of the column", "The Financial Express · with A. Coauthor",
 "https://..."]
```

Both lists are in the order they appear on the site, newest first.

Then rebuild:

```bash
cd site-source
python3 build_site.py
```

The counts on the homepage and the section chips on the research page (`PUBLISHED
ARTICLES 73`) are computed from the data, so adding an entry moves 73 to 74 by itself.
Year headings appear and disappear on their own too. Commit the regenerated HTML along
with the changed `data.json`.

To change wording that is not a list entry — the About text, the advisory project
descriptions, the homepage introduction — edit `build_site.py` and rebuild. The prose
sits in clearly named blocks near the top and middle of that file.

---

## Publishing

Upload everything to the repository root and GitHub Pages serves it. No workflow, no
Actions, no Jekyll build. A new commit is usually live within a minute, though Pages
caches files for about ten minutes, so a replaced PDF or photograph can take that long
to appear.

---

## Notes on how it is built

- **No JavaScript.** The previous version of the site patched navigation and publication
  links into the page at runtime, which meant crawlers that do not execute scripts saw a
  bibliography with no links. Everything is now in the HTML as delivered.
- **Fonts** are Source Serif 4, IBM Plex Sans and IBM Plex Mono, loaded from Google Fonts
  with `preconnect` so the request starts immediately. Each has a real fallback stack, so
  the page stays readable if the fonts fail to load.
- **Dark mode** follows the reader's system setting. Both palettes are defined in
  `assets/styles.css` as custom properties at the top of the file; change a colour once
  there and it changes everywhere.
- **Print** styles are included, so the research page prints as a clean bibliography.
- Each page carries a canonical URL, Open Graph and Twitter card tags, and a JSON-LD
  `Person` block listing your Scholar, ORCID, SSRN, RePEc, Scopus, LinkedIn and GitHub
  profiles. That last part is what search engines and AI assistants use to connect the
  site to your publication record.
