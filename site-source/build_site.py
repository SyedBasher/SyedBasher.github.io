#!/usr/bin/env python3
"""
Builds syedbasher.github.io from data.json.

Usage:   python3 build_site.py
Output:  writes index.html, research.html, writing.html, advisory.html,
         applied-work.html, about.html, assets/styles.css, sitemap.xml,
         robots.txt, 404.html into the repository root (the parent of this
         folder).

To add a publication or a column, edit data.json and run this script again.
Counts, year headings and jump links all update by themselves.
"""
import json, html, re, os, collections, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = "https://syedbasher.github.io"

D = json.load(open(os.path.join(HERE, 'data.json'), encoding='utf-8'))
E = lambda s: html.escape(s or '', quote=True)


def link(title, url):
    t = E(title)
    return f'<a href="{E(url)}" target="_blank" rel="noopener">{t}</a>' if url else t


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


# --------------------------------------------------------------- research ---
pubs = D['pubs']
ORDER = ["Published articles", "Working papers", "Book chapters and book reviews",
         "Unpublished papers", "Dissertation"]
by_sec = collections.OrderedDict((s, []) for s in ORDER)
for s, y, t, d, u in pubs:
    by_sec[s].append((y, t, d, u))

sec_counts = {s: len(v) for s, v in by_sec.items()}
n_pub = sum(1 for y, *_ in by_sec["Published articles"] if y != "Forthcoming")

research_toc = ' &middot; '.join(
    f'<a href="#{slug(s)}">{E(s)}</a>' for s in ORDER if sec_counts[s])


def pub_item(t, d, u):
    det = f'<br>{E(d)}' if d else ''
    return f'<p class="pub">{link(t, u)}{det}</p>'


research_parts = []
for sec, items in by_sec.items():
    if not items:
        continue
    inner = []
    if sec == "Published articles":
        cur = None
        for y, t, d, u in items:
            if y != cur:
                cur = y
                inner.append(f'<h3 class="year">{E(y)}</h3>')
            inner.append(pub_item(t, d, u))
    else:
        for y, t, d, u in items:
            inner.append(pub_item(t, d, u))
    research_parts.append(f'<h2 id="{slug(sec)}">{E(sec)}</h2>' + ''.join(inner))
research_body = ''.join(research_parts)


# ---------------------------------------------------------------- writing ---
def year_of(s):
    m = re.findall(r'((?:19|20)\d{2})', s)
    return m[-1] if m else ''


def short_date(s):
    p = s.split()
    return f'{p[0]} {p[1][:3]}' if len(p) >= 3 else ''


MONTHS = {m: i for i, m in enumerate(
    ['January', 'February', 'March', 'April', 'May', 'June', 'July',
     'August', 'September', 'October', 'November', 'December'], 1)}


def iso_date(s):
    p = s.split()
    if len(p) >= 3 and p[1] in MONTHS:
        return f'{p[2]}-{MONTHS[p[1]]:02d}-{int(p[0]):02d}'
    return year_of(s)


wr = D['writing']
n_writing = len(wr)
groups = collections.OrderedDict()
for dt, t, outlet, u in wr:
    groups.setdefault(year_of(dt), []).append((dt, t, outlet, u))

writing_parts = []
for yr, items in groups.items():
    rows = ''.join(
        '<p class="wr">'
        f'<time datetime="{E(iso_date(dt))}">{E(short_date(dt))}</time>'
        f'<span>{link(t, u)}. <em>{E(re.sub(r" · with [^·]*", "", outlet))}</em></span></p>'
        for dt, t, outlet, u in items)
    writing_parts.append(f'<h3 class="year">{E(yr)}</h3>' + rows)
writing_body = ''.join(writing_parts)


# --------------------------------------------------------------- advisory ---
PROJECTS = [
 ("2026 · Bangladesh Institute of Development Studies",
  "A macroeconometric model of Bangladesh",
  "Building a macroeconometric framework that brings together the main macroeconomic series and "
  "their estimated relationships, so that alternative developments and policy scenarios can be "
  "examined in one coherent setting rather than argued about in isolation."),
 ("2025–2026 · Economic Research Group and Microcredit Regulatory Authority",
  "Household indebtedness and financial vulnerability in the microfinance sector",
  "Branch and institution-level administrative records used to look at borrowing intensity, "
  "repayment stress and portfolio quality, and to work out where financial vulnerability is "
  "building up quietly enough to be missed."),
 ("2025 · Change Initiative and SOAS",
  "The political economy of debt in Sri Lanka and Bangladesh",
  "A comparative study of public debt and the institutions around it, asking how financing "
  "structures and political constraints shape both debt outcomes and the policy room a "
  "government has left."),
 ("2022 · Asian Development Bank",
  "Bangladesh flash floods 2022: post-disaster needs assessment",
  "Economic analysis contributed to the assessment that followed the 2022 flash floods, "
  "covering losses, recovery needs and the wider economic consequences."),
 ("2022 · KIVU International and Policy Exchange Bangladesh",
  "New sectors in Bangladesh's export diversification",
  "An examination of where export growth might come from beyond the established sectors, using "
  "sector and product evidence to narrow a long list down to candidates worth studying properly."),
 ("2019 · Institute of Water Modelling · World Bank–financed",
  "A hydro-economic model of the Jamuna River",
  "Joint work linking hydrological modelling to economic valuation along the Jamuna, in support "
  "of appraising river management options."),
 ("2010–2012 · Qatar National Food Security Programme",
  "Economic consultant",
  "Analysis of food security and agricultural support in a small, import-dependent economy, "
  "including work on subsidy design and household food expenditure."),
]
projects_body = ''.join(
    f'<div class="entry"><p class="meta">{E(m)}</p><p class="etitle">{E(t)}</p>'
    f'<p>{E(d)}</p></div>' for m, t, d in PROJECTS)


# ------------------------------------------------------------------ about ---
EDU = [("2007", "Ph.D. in Economics",
        "York University, Toronto · Dissertation: <em>Essays on Mixed Oligopoly</em>"),
       ("2001", "M.A. in Economics", "York University, Toronto"),
       ("1999", "M.Sc. in Economics", "North South University, Dhaka"),
       ("1996", "B.B.A. in Finance", "North South University, Dhaka")]

EXP = [("2026–present", "Founder",
        '<a href="https://www.mangroveintel.com/" target="_blank" rel="noopener">Mangrove Intelligence</a>, Dhaka'),
       ("2025–present", "Independent Researcher", "Dhaka"),
       ("2019–2025", "Professor of Economics", "East West University, Dhaka",
        "Acting Director, Center for Urban Studies and Sustainable Development, 2023–2025"),
       ("2015–2019", "Associate Professor of Economics", "East West University, Dhaka",
        "Chair, Department of Economics, 2016–2019"),
       ("2014–2016", "Senior Research Fellow", "Fikra Research &amp; Policy, Doha"),
       ("2010–2012", "Economic Consultant", "Qatar National Food Security Programme"),
       ("2007–2013", "Research Economist",
        "Qatar Central Bank, Department of Research &amp; Monetary Policy"),
       ("2005–2007", "Lecturer (Adjunct)", "University of Guelph-Humber, Toronto"),
       ("2002–2007", "Lecturer (Adjunct)",
        "Schulich School of Business, York University, Toronto")]


def timeline(rows):
    out = []
    for row in rows:
        a, b, c = row[0], row[1], row[2]
        sub = row[3] if len(row) > 3 else ''
        sub_html = f'<br><span class="soft">{E(sub)}</span>' if sub else ''
        out.append(f'<div class="tl"><time>{E(a)}</time>'
                   f'<span><strong>{E(b)}</strong>, {c}{sub_html}</span></div>')
    return ''.join(out)


# ------------------------------------------------------------------- chrome --
# The portrait committed to the repository is a grey placeholder. Set this to
# True once assets/portrait.jpg is a real photograph (4:5, about 800x1000 px).
SHOW_PORTRAIT = False

NAV = [("index.html", "Home"), ("research.html", "Research"),
       ("writing.html", "Writing"), ("advisory.html", "Advisory"),
       ("about.html", "About")]

PROFILE_LINKS = (
 '<a href="https://scholar.google.com/citations?user=aabMrnUAAAAJ" target="_blank" rel="noopener">Google&nbsp;Scholar</a>'
 '<a href="https://orcid.org/0000-0003-3918-8285" target="_blank" rel="noopener">ORCID</a>'
 '<a href="https://papers.ssrn.com/sol3/cf_dev/AbsByAuth.cfm?per_id=369204" target="_blank" rel="noopener">SSRN</a>')

JSONLD = json.dumps({
    "@context": "https://schema.org",
    "@type": "Person",
    "name": "Syed Abul Basher",
    "url": SITE + "/",
    "jobTitle": ["Economist and Independent Researcher",
                 "Founder, Mangrove Intelligence"],
    "worksFor": {"@type": "Organization", "name": "Mangrove Intelligence",
                 "url": "https://www.mangroveintel.com/"},
    "address": {"@type": "PostalAddress", "addressLocality": "Dhaka",
                "addressCountry": "BD"},
    "email": "mailto:syed.basher@gmail.com",
    "alumniOf": [{"@type": "CollegeOrUniversity", "name": "York University"},
                 {"@type": "CollegeOrUniversity", "name": "North South University"}],
    "knowsAbout": ["Energy economics", "Monetary policy", "Applied macroeconomics",
                   "Panel econometrics", "Regional and spatial economics",
                   "Household demand and welfare", "Bangladesh economy"],
    "sameAs": ["https://scholar.google.com/citations?user=aabMrnUAAAAJ",
               "https://orcid.org/0000-0003-3918-8285",
               "https://papers.ssrn.com/sol3/cf_dev/AbsByAuth.cfm?per_id=369204"],
}, indent=2, ensure_ascii=False)

FOOTER = """
  <footer class="site-foot">
    <div class="wrap">
      Syed Abul Basher &middot; Dhaka, Bangladesh &middot;
      <a href="mailto:syed.basher@gmail.com">syed.basher@gmail.com</a>
    </div>
  </footer>"""


def curly(h):
    """Typographic apostrophes and single quotes in visible text only."""
    out = []
    for seg in re.split(r'(<script.*?</script>|<[^>]+>)', h, flags=re.S):
        if not seg.startswith('<'):
            seg = re.sub(r"(?<=\w)(?:&#x27;|')", '\u2019', seg)
            seg = re.sub(r"(?:&#x27;|')(?=\w)", '\u2018', seg)
            seg = re.sub(r"&#x27;|'", '\u2019', seg)
        out.append(seg)
    return ''.join(out)


def page(filename, title, description, body, active):
    HERE_ATTR = ' class="here" aria-current="page"'
    name_link = '' if filename == "index.html" else '<a class="name" href="index.html">Syed Abul Basher</a>'
    nav = ''.join(
        '<a href="%s"%s>%s</a>' % (h, HERE_ATTR if h == active else '', n)
        for h, n in NAV)
    canonical = SITE + "/" + ("" if filename == "index.html" else filename)
    return curly(f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(description)}">
<meta name="author" content="Syed Abul Basher">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{canonical}">

<meta property="og:type" content="website">
<meta property="og:site_name" content="Syed Abul Basher">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(description)}">
<meta property="og:url" content="{canonical}">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{E(title)}">
<meta name="twitter:description" content="{E(description)}">

<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="assets/styles.css">
<script type="application/ld+json">
{JSONLD}
</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top">
  <div class="wrap">
    {name_link}
    <nav aria-label="Primary">{nav}</nav>
  </div>
</header>
<main id="main" class="wrap">
{body}
</main>
{FOOTER}
</body>
</html>
""")


# ------------------------------------------------------------------- pages ---
PORTRAIT = ('<img class="portrait" src="assets/portrait.jpg" alt="Syed Abul Basher" '
            'width="480" height="600">') if SHOW_PORTRAIT else ''

HOME_BODY = f"""
  <section class="intro{' with-photo' if SHOW_PORTRAIT else ''}">
    {PORTRAIT}
    <div>
      <h1>Syed Abul Basher</h1>
      <p class="role">Economist and independent researcher</p>
      <p>Founder, <a href="https://www.mangroveintel.com/" target="_blank"
        rel="noopener">Mangrove Intelligence</a></p>
      <p class="contact"><strong>Email</strong><br>
        <a href="mailto:syed.basher@gmail.com">syed.basher@gmail.com</a></p>
      <p class="contact"><strong>Links</strong><br>{PROFILE_LINKS}<a href="Syed_Basher_CV.pdf">CV</a></p>
    </div>
  </section>

  <section>
    <p>My current research focuses mainly on economic questions related to Bangladesh: regional
      disparity, household welfare and prices, the energy sector, and the building of economy-wide
      models, both computable general equilibrium and macroeconometric. The empirical work draws on
      official statistics as well as household surveys, administrative records and satellite
      images. For many years I have also worked on oil prices, exchange rates, food security and
      the economies of the Gulf.</p>
  </section>

  <section class="mangrove">
    <h2>Mangrove Intelligence</h2>
    <p>Mangrove Intelligence is the company I founded in 2026 to build data and analytical products
      on the Bangladesh economy: databases, indicators and regular forecasts that are kept up to date
      rather than delivered once and filed away. It also takes on economy-wide modelling and analysis
      for organisations that need it.</p>
    <p><a href="https://www.mangroveintel.com/" target="_blank" rel="noopener">Visit
      Mangrove Intelligence</a></p>
  </section>

  <section>
    <h2>Recent papers</h2>
    <p class="pub"><a href="https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5284307"
      target="_blank" rel="noopener">Panel econometric approaches to purchasing power parity: A
      survey of methods and findings</a><br><em>Journal of Economic Surveys</em>, forthcoming.</p>
    <p class="pub"><a href="https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7422080"
      target="_blank" rel="noopener">Consumer demand systems and the welfare cost of price shocks in
      Bangladesh: Evidence from HIES 2022</a><br>with Salim Rashid. Working paper, 2026.</p>
    <p class="pub"><a href="https://onlinelibrary.wiley.com/doi/10.1111/kykl.70020"
      target="_blank" rel="noopener">Regulatory burdens, corruption, and informal competition:
      Determinants of incorporation in Bangladesh</a><br>with Asaf Ibne Salim and Muhammad Nazmul
      Khan. <em>Kyklos</em>, 2026.</p>
    <p class="pub"><a href="https://link.springer.com/article/10.1007/s00148-024-01043-6"
      target="_blank" rel="noopener">Improved estimates of child undernutrition trends in
      micro-level administrative units in Bangladesh using remote-sensed data</a><br>with S. Das,
      B. Baffour, P. Godwin, A. Richardson and S. Rashid. <em>Journal of Population Economics</em>,
      2024.</p>
    <p><a href="research.html">All research and publications</a></p>
  </section>"""

RESEARCH_BODY = f"""
  <h1>Research</h1>
  <p class="toc">{research_toc}</p>
{research_body}"""

WRITING_BODY = f"""
  <h1>Writing</h1>
  <p>From time to time, I write opinion columns for newspapers in Bangla and in English as a way of
    putting my thinking in front of the general reader.</p>
{writing_body}"""

ADVISORY_BODY = f"""
  <h1>Advisory work</h1>
  <p>Commissioned projects for research institutes, development agencies and public bodies. I am
    currently working with the Bangladesh Institute of Development Studies and the Microcredit
    Regulatory Authority, and earlier worked with Bangladesh Bank and on Asian Development Bank and
    World Bank&ndash;financed assignments.</p>
  <p>Databases, indicators and other work that has to be kept current are built through
    <a href="https://www.mangroveintel.com/" target="_blank" rel="noopener">Mangrove Intelligence</a>.
    To discuss a project, write to
    <a href="mailto:syed.basher@gmail.com">syed.basher@gmail.com</a>.</p>
  <h2>Selected projects</h2>
  {projects_body}"""

ABOUT_BODY = f"""
  <h1>About</h1>
  <p>I am an independent research economist based in Dhaka, with about twenty-five years of
    research experience in energy economics, monetary policy and applied macroeconomics. After
    completing my PhD in Economics at York University in Toronto, I worked from 2007 to 2013 as a
    Research Economist in the Department of Research and Monetary Policy at Qatar Central Bank, and
    during that period I also held the position of Economic Consultant to the Qatar National Food
    Security Programme from 2010 to 2012. Both roles involved producing academic and policy research
    for a central bank and a government programme.</p>
  <p>I subsequently served as Senior Research Fellow at Fikra Research &amp; Policy in Doha from 2014
    to 2016, and at East West University in Dhaka from 2015 to 2025, most recently as Professor of
    Economics and as Acting Director of its Center for Urban Studies and Sustainable Development.</p>
  <p>Since 2025 I have been working independently, my time divided between academic research and
    commissioned advisory work for research institutes, development agencies and public bodies. I
    continue to supervise students and to write for the newspapers, in English and in Bangla.</p>
  <p>In 2026 I founded <a href="https://www.mangroveintel.com/" target="_blank"
    rel="noopener">Mangrove Intelligence</a>, which builds data and analytical products on the
    Bangladesh economy. It grew out of the same frustration that runs through much of my research:
    that the numbers a decision actually turns on are often not collected, or not published in a form
    anyone can use.</p>
  <p><a href="Syed_Basher_CV.pdf">Curriculum Vitae (PDF)</a></p>
  <h2>Education</h2>
  {timeline(EDU)}
  <h2>Positions</h2>
  {timeline(EXP)}"""

PAGES = [
 ("index.html", "Syed Abul Basher | Economist and Independent Researcher",
  "Personal website of Syed Abul Basher, economist and independent researcher in Dhaka, working on "
  "Bangladesh's economy, regional and spatial measurement, household welfare, macro-finance, energy "
  "and applied econometrics.", HOME_BODY),
 ("research.html", "Research — Syed Abul Basher",
  f"{n_pub} published articles plus working papers, book chapters, reviews and a dissertation, in "
  "applied economics, energy, macro-finance and the economy of Bangladesh.", RESEARCH_BODY),
 ("writing.html", "Writing — Syed Abul Basher",
  f"{n_writing} newspaper columns and opinion pieces in Bangla and English since 1999, on inflation, "
  "the exchange rate, public debt, energy and economic measurement.", WRITING_BODY),
 ("advisory.html", "Advisory Work — Syed Abul Basher",
  "Commissioned economic analysis for research institutes, development agencies and public bodies, "
  "including BIDS, the Microcredit Regulatory Authority, Bangladesh Bank and the Asian Development "
  "Bank.", ADVISORY_BODY),
 ("about.html", "About — Syed Abul Basher",
  "Education, positions and career of Syed Abul Basher — York University, Qatar Central Bank, Fikra "
  "Research & Policy and East West University.", ABOUT_BODY),
]


# -------------------------------------------------------------------- css ---
CSS = """/* syedbasher.github.io - generated by site-source/build_site.py */
@font-face{font-family:"Termes";src:url("fonts/termes-regular.woff2") format("woff2");
  font-weight:400;font-style:normal;font-display:swap}
@font-face{font-family:"Termes";src:url("fonts/termes-italic.woff2") format("woff2");
  font-weight:400;font-style:italic;font-display:swap}
@font-face{font-family:"Termes";src:url("fonts/termes-bold.woff2") format("woff2");
  font-weight:700;font-style:normal;font-display:swap}
@font-face{font-family:"Termes";src:url("fonts/termes-bolditalic.woff2") format("woff2");
  font-weight:700;font-style:italic;font-display:swap}
/* Bengali text anywhere on the site is set in Tiro Bangla */
@font-face{font-family:"Tiro Bangla";src:url("fonts/tiro-bangla-400.woff2") format("woff2");
  font-weight:400;font-style:normal;font-display:swap;
  unicode-range:U+0951-0952,U+0964-0965,U+0980-09FE,U+1CD0,U+1CF7,U+200C-200D,U+20B9,U+25CC}
@font-face{font-family:"Tiro Bangla";src:url("fonts/tiro-bangla-400-italic.woff2") format("woff2");
  font-weight:400;font-style:italic;font-display:swap;
  unicode-range:U+0951-0952,U+0964-0965,U+0980-09FE,U+1CD0,U+1CF7,U+200C-200D,U+20B9,U+25CC}

:root{
  --bg:#fefdef; --ink:#27323d; --soft:#5a6672; --rule:#dcdac2;
  --green:#1f4d3a; --link:#1e6a4c; --tint:#eaf1e1; --bar:#1f4d3a; --onbar:#fefdef;
}
@media (prefers-color-scheme: dark){
  :root{--bg:#121a16;--ink:#e6e9df;--soft:#a9b3aa;--rule:#2f3d35;
    --green:#8fcaa8;--link:#8fcaa8;--tint:#1a2820;--bar:#0c120f;--onbar:#e6e9df}
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:"Tiro Bangla","Termes","Times New Roman",Times,"Liberation Serif",Georgia,serif;
  font-size:18px;line-height:1.55}
a{color:var(--link);text-decoration:underline;text-decoration-thickness:1px;
  text-underline-offset:3px;text-decoration-color:color-mix(in srgb,var(--link) 40%,transparent)}
a:hover{text-decoration-color:var(--link);text-decoration-thickness:2px}
a:focus-visible{outline:2px solid var(--link);outline-offset:2px}
h1,h2,h3{margin:0;font-weight:700;line-height:1.25;color:var(--green)}
h1{font-size:2rem;margin-bottom:12px}
h2{font-size:1.3rem;margin:36px 0 12px;padding-bottom:5px;border-bottom:2px solid var(--rule)}
h3.year{font-size:1rem;margin:24px 0 6px;letter-spacing:.04em}
p{margin:0 0 12px}
img{max-width:100%;height:auto}
.wrap{max-width:760px;margin:0 auto;padding:0 24px}
.skip{position:absolute;left:-9999px;top:0;background:var(--green);color:var(--bg);padding:8px 14px}
.skip:focus{left:10px;top:10px}

.top{background:var(--bg);border-top:6px solid var(--bar);border-bottom:1px solid var(--rule);padding:14px 0}
.top .wrap{display:flex;justify-content:space-between;align-items:baseline;
  flex-wrap:wrap;gap:8px 24px}
.top nav{margin-left:auto}
.name{font-size:1.25rem;font-weight:700;color:var(--green);text-decoration:none}
nav a{margin-left:20px;font-size:1rem;color:var(--ink);text-decoration:none;
  padding-bottom:2px;border-bottom:2px solid transparent}
nav a:hover{border-bottom-color:var(--rule)}
nav a.here{color:var(--green);font-weight:700;border-bottom-color:var(--green)}

main{padding-top:38px;padding-bottom:34px}
.intro{display:flex;gap:30px;align-items:flex-start;margin-bottom:22px}
.intro > div{flex:1;min-width:0}
.portrait{width:190px;flex:none;border:1px solid var(--rule)}
.role{color:var(--soft);margin-bottom:4px}
.contact{margin-top:14px;margin-bottom:0}
.contact strong{color:var(--green);font-size:.82rem;letter-spacing:.1em;text-transform:uppercase}
.contact a + a::before{content:"\\00b7";color:var(--soft);margin:0 .5em;display:inline-block;
  text-decoration:none}
.toc{color:var(--soft)}

.mangrove{background:var(--tint);border-left:5px solid var(--green);
  padding:18px 24px 8px;margin:30px 0 8px}
.mangrove h2{margin:0 0 8px;padding:0;border:0;font-size:1.25rem}

.pub{margin-bottom:12px}
.entry{margin-bottom:16px}
.entry p{margin-bottom:2px}
.entry .meta{color:var(--soft);font-size:.95rem}
.entry .etitle{font-weight:700;color:var(--green)}
.wr{display:flex;gap:14px;margin-bottom:8px}
.wr time{flex:none;width:58px;color:var(--soft);font-size:.95rem}
.tl{display:flex;gap:14px;margin-bottom:8px}
.tl time{flex:none;width:112px;color:var(--soft);font-size:.95rem}
.soft{color:var(--soft)}

.site-foot{background:var(--bar);color:var(--onbar);padding:20px 0 28px;font-size:.95rem}
.site-foot a{color:var(--onbar);text-decoration-color:color-mix(in srgb,var(--onbar) 50%,transparent)}

@media (max-width:640px){
  body{font-size:17px}
  .intro.with-photo{flex-direction:column}
  .portrait{width:150px}
  nav a{margin-left:0;margin-right:16px}
  .wr,.tl{flex-direction:column;gap:0}
  .wr time,.tl time{width:auto}
  .mangrove{padding:16px 18px 6px}
}
@media print{
  .top nav,.skip{display:none}
  body{font-size:11pt;color:#000;background:#fff}
  a{color:#000;text-decoration:underline}
  .site-foot{background:none;color:#000}
}
"""

REDIRECT = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Advisory Work — Syed Abul Basher</title>
<link rel="canonical" href="{site}/advisory.html">
<meta http-equiv="refresh" content="0; url=advisory.html">
<meta name="robots" content="noindex, follow">
</head>
<body><p>This page has moved to <a href="advisory.html">advisory.html</a>.</p></body>
</html>
""".format(site=SITE)

NOT_FOUND = page("404.html", "Page not found — Syed Abul Basher",
                 "The page you asked for does not exist on this site.", """
  <h1>Page not found</h1>
  <p>The address you followed does not exist on this site. It may have been renamed, or the link
    that brought you here may be out of date.</p>
  <p><a href="index.html">Home</a> &middot; <a href="research.html">Research</a> &middot;
    <a href="writing.html">Writing</a> &middot; <a href="advisory.html">Advisory</a> &middot;
    <a href="about.html">About</a></p>""", active=None)

today = datetime.date.today().isoformat()
SITEMAP = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + ''.join(
               f'  <url><loc>{SITE}/{"" if f == "index.html" else f}</loc>'
               f'<lastmod>{today}</lastmod>'
               f'<priority>{"1.0" if f == "index.html" else "0.8"}</priority></url>\n'
               for f, *_ in PAGES)
           + '</urlset>\n')

ROBOTS = f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n"


# ------------------------------------------------------------------ write ---
def write(rel, text):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(text)
    print(f'  {rel:28s} {len(text):>7,d} bytes')


print('Building site into', ROOT)
for fname, title, desc, body in PAGES:
    write(fname, page(fname, title, desc, body, active=fname))
write('applied-work.html', REDIRECT)
write('404.html', NOT_FOUND)
write('assets/styles.css', CSS)
write('sitemap.xml', SITEMAP)
write('robots.txt', ROBOTS)
write('.nojekyll', '')
print(f'\nDone. {n_pub} published articles, {len(pubs)} publications in all, '
      f'{n_writing} columns.')
