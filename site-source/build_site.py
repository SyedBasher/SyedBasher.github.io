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
n_pub = sec_counts["Published articles"]

research_toc = ''.join(
    f'<a href="#{slug(s)}">{E(s)} <em>{sec_counts[s]}</em></a>' for s in ORDER)


def pub_item(t, d, u):
    det = f'<div class="cite">{E(d)}</div>' if d else ''
    return f'<div class="pub"><div class="t">{link(t, u)}</div>{det}</div>'


research_parts = []
for sec, items in by_sec.items():
    inner = []
    if sec == "Published articles":
        cur = None
        for y, t, d, u in items:
            if y != cur:
                cur = y
                inner.append(f'<h2 class="yearhead">{E(y)}</h2>')
            inner.append(pub_item(t, d, u))
    else:
        for y, t, d, u in items:
            inner.append(pub_item(t, d, u))
    research_parts.append(f"""
    <div class="divider-strong" id="{slug(sec)}"></div>
    <div class="row">
      <div class="rail"><div class="label">{E(sec)}</div></div>
      <div class="body-col">{''.join(inner)}</div>
    </div>""")
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
        '<div class="wr">'
        f'<time datetime="{E(iso_date(dt))}">{E(short_date(dt))}</time>'
        f'<div><div class="t">{link(t, u)}</div>'
        f'<div class="outlet">{E(outlet)}</div></div></div>'
        for dt, t, outlet, u in items)
    writing_parts.append(f'<h2 class="yearhead">{E(yr)}</h2>' + rows)
writing_body = ''.join(writing_parts)


# --------------------------------------------------------------- advisory ---
PROJECTS = [
 ("2026 · Bangladesh Institute of Development Studies",
  "A macroeconometric model of Bangladesh",
  "Building a macroeconometric framework that brings together the main macroeconomic series and "
  "their estimated relationships, so that alternative developments and policy scenarios can be "
  "examined in one coherent setting rather than argued about in isolation."),
 ("2025–2026 · Economic Research Group",
  "Household indebtedness and financial vulnerability in the microfinance sector",
  "Branch and institution-level administrative records used to look at borrowing intensity, "
  "repayment stress and portfolio quality, and to work out where financial vulnerability is "
  "building up quietly enough to be missed."),
 ("2025 · Change Initiative",
  "The political economy of debt in Sri Lanka and Bangladesh",
  "A comparative study of public debt and the institutions around it, asking how financing "
  "structures and political constraints shape both debt outcomes and the policy room a "
  "government has left."),
 ("2022 · Asian Development Bank",
  "Bangladesh flash floods 2022: post-disaster needs assessment",
  "Economic analysis contributed to the assessment that followed the 2022 flash floods, "
  "covering losses, recovery needs and the wider economic consequences."),
 ("2022 · KIVU International",
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
    f'<div class="entry"><div class="meta">{E(m)}</div><h3>{E(t)}</h3>'
    f'<p class="desc">{E(d)}</p></div>' for m, t, d in PROJECTS)


# ------------------------------------------------------------------ about ---
EDU = [("2007", "Ph.D. in Economics",
        "York University, Toronto · Dissertation: <em>Essays on Mixed Oligopoly</em>"),
       ("2001", "M.A. in Economics", "York University, Toronto"),
       ("1999", "M.Sc. in Economics", "North South University, Dhaka"),
       ("1996", "B.B.A. in Finance", "North South University, Dhaka")]

EXP = [("2025–present", "Independent Researcher", "Dhaka"),
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
        sub_html = f'<div class="tlsub">{E(sub)}</div>' if sub else ''
        out.append(f'<div class="tlrow"><time>{E(a)}</time><div>'
                   f'<div class="tlt">{E(b)}</div><div class="tls">{c}</div>'
                   f'{sub_html}</div></div>')
    return ''.join(out)


# ------------------------------------------------------------------- chrome --
NAV = [("index.html", "Home"), ("research.html", "Research"),
       ("writing.html", "Writing"), ("advisory.html", "Advisory"),
       ("about.html", "About")]

PROFILE_LINKS = (
 '<a href="https://scholar.google.com/citations?user=aabMrnUAAAAJ" target="_blank" rel="noopener">Google&nbsp;Scholar</a>'
 '<a href="https://orcid.org/0000-0003-3918-8285" target="_blank" rel="noopener">ORCID</a>'
 '<a href="https://papers.ssrn.com/sol3/cf_dev/AbsByAuth.cfm?per_id=369204" target="_blank" rel="noopener">SSRN</a>'
 '<a href="https://mpra.ub.uni-muenchen.de/view/people/Basher%3D3ASyed_A%3D2E%3D3A%3D3A.html" target="_blank" rel="noopener">RePEc</a>'
 '<a href="https://www.sciencedirect.com/author/14048112000/syed-abul-basher" target="_blank" rel="noopener">Scopus</a>'
 '<a href="https://www.linkedin.com/in/syed-abul-basher-301b14432" target="_blank" rel="noopener">LinkedIn</a>'
 '<a href="https://github.com/SyedBasher" target="_blank" rel="noopener">GitHub</a>')

JSONLD = json.dumps({
    "@context": "https://schema.org",
    "@type": "Person",
    "name": "Syed Abul Basher",
    "url": SITE + "/",
    "jobTitle": "Economist and Independent Researcher",
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
               "https://papers.ssrn.com/sol3/cf_dev/AbsByAuth.cfm?per_id=369204",
               "https://mpra.ub.uni-muenchen.de/view/people/Basher%3D3ASyed_A%3D2E%3D3A%3D3A.html",
               "https://www.sciencedirect.com/author/14048112000/syed-abul-basher",
               "https://www.linkedin.com/in/syed-abul-basher-301b14432",
               "https://github.com/SyedBasher"],
}, indent=2, ensure_ascii=False)

FOOTER = """
  <div class="shell">
    <div class="divider-strong"></div>
    <footer class="site-foot">
      <strong>Syed Abul Basher</strong>
      <div>Economist and independent researcher · Dhaka</div>
      <div class="foot-links">
        <a href="mailto:syed.basher@gmail.com">Email</a>
        <a href="research.html">Research</a>
        <a href="writing.html">Writing</a>
        <a href="advisory.html">Advisory</a>
        <a href="about.html">About</a>
        <a href="Syed_Basher_CV.pdf">CV</a>
      </div>
    </footer>
  </div>"""


def page(filename, title, description, body, active):
    HERE_ATTR = ' class="here" aria-current="page"'
    nav = ''.join(
        '<a href="%s"%s>%s</a>' % (h, HERE_ATTR if h == active else '', n)
        for h, n in NAV)
    canonical = SITE + "/" + ("" if filename == "index.html" else filename)
    return f"""<!doctype html>
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

<meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#111823" media="(prefers-color-scheme: dark)">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<link rel="stylesheet" href="assets/styles.css">
<script type="application/ld+json">
{JSONLD}
</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="topmark"></div>
<div class="shell">
  <header class="masthead">
    <a class="wordmark" href="index.html">Syed Abul Basher<small>Economist · Dhaka</small></a>
    <nav class="mastnav" aria-label="Primary">{nav}</nav>
  </header>
</div>
<main id="main">
{body}
</main>
{FOOTER}
</body>
</html>
"""


# ------------------------------------------------------------------- pages ---
HOME_BODY = f"""
  <div class="shell">
    <div class="hero">
      <div>
        <h1>Syed Abul Basher</h1>
        <p class="role">Economist and independent researcher</p>
        <p class="lede">Welcome to my website. I am an economist based in Dhaka, and this is where I
          keep my published work, the columns I write for the newspapers, and the commissioned
          projects I have worked on and am working on now.</p>
        <p class="lede">Most of my current research is about Bangladesh: questions of regional
          disparity, development questions approached through large micro datasets such as the HIES
          and the Labour Force Survey, the building of large macroeconometric and computable general
          equilibrium models, and the country's persistent energy crisis. I use satellite and
          administrative data a good deal, largely because the official numbers do not always reach
          far enough. I also take on commissioned work for research institutes, development banks and
          public bodies, usually where a model has to be built or a measurement problem sorted out.</p>
        <p class="idlinks">{PROFILE_LINKS}</p>
        <a class="cta" href="Syed_Basher_CV.pdf">Curriculum Vitae — PDF</a>
      </div>
      <div class="hero-aside">
        <img class="portrait" src="assets/portrait.jpg" alt="Syed Abul Basher" width="480" height="600">
        <div class="contact-card">
          <div class="label">Write to me</div>
          <a href="mailto:syed.basher@gmail.com">syed.basher@gmail.com</a>
        </div>
      </div>
    </div>
  </div>

  <div class="band">
    <div class="shell">
      <div class="row">
        <div class="rail"><div class="label">Record</div></div>
        <div class="body-col">
          <div class="record">
            <div><div class="label">Published articles</div><div class="fig">{n_pub}</div>
              <div class="sub">plus working papers, chapters and reviews</div></div>
            <div><div class="label">Journals include</div><div class="fig long">Journal of Population Economics</div>
              <div class="sub">Energy Economics · Journal of Banking &amp; Finance · Empirical Economics</div></div>
            <div><div class="label">Central banking</div><div class="fig">2007–2013</div>
              <div class="sub">Research &amp; Monetary Policy, Qatar Central Bank</div></div>
            <div><div class="label">Advisory</div><div class="fig">BIDS · MRA</div>
              <div class="sub">Current work; earlier Bangladesh Bank and the ADB</div></div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="shell">
    <div class="row">
      <div class="rail"><div class="label">Work</div></div>
      <div class="body-col">
        <div class="split">
          <div>
            <div class="track-kicker">Research</div>
            <h2>Selected recent papers</h2>
            <div class="entries">
              <div class="entry"><div class="meta">2026 · Working paper</div>
                <h3><a href="https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7422080" target="_blank" rel="noopener">Consumer demand systems and the welfare cost of price shocks in Bangladesh</a></h3>
                <div class="by">with Salim Rashid · Evidence from HIES 2022</div></div>
              <div class="entry"><div class="meta">2026 · Kyklos</div>
                <h3><a href="https://onlinelibrary.wiley.com/doi/10.1111/kykl.70020" target="_blank" rel="noopener">Regulatory burdens, corruption, and informal competition</a></h3>
                <div class="by">with Asaf Ibne Salim and Muhammad Nazmul Khan</div></div>
              <div class="entry"><div class="meta">2024 · Journal of Population Economics</div>
                <h3><a href="https://link.springer.com/article/10.1007/s00148-024-01043-6" target="_blank" rel="noopener">Improved estimates of child undernutrition trends using remote-sensed data</a></h3>
                <div class="by">with S. Das, B. Baffour, P. Godwin, A. Richardson and S. Rashid</div></div>
            </div>
            <a class="more" href="research.html">All research and publications</a>
          </div>
          <div>
            <div class="track-kicker">Advisory</div>
            <h2>Selected engagements</h2>
            <div class="entries">
              <div class="entry"><div class="meta">2026 · BIDS</div>
                <h3>A macroeconometric model of Bangladesh</h3>
                <p class="desc">A framework linking the main macroeconomic series and their estimated relationships, so policy scenarios can be examined coherently.</p></div>
              <div class="entry"><div class="meta">2025–26 · Economic Research Group</div>
                <h3>Household indebtedness in the microfinance sector</h3>
                <p class="desc">Borrowing intensity, repayment stress and portfolio quality, read off branch-level administrative records.</p></div>
              <div class="entry"><div class="meta">2022 · Asian Development Bank</div>
                <h3>Flash floods post-disaster needs assessment</h3>
                <p class="desc">Economic analysis of losses and recovery needs following the 2022 flash floods.</p></div>
            </div>
            <a class="more" href="advisory.html">All advisory work</a>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="shell">
    <div class="divider-strong"></div>
    <div class="row">
      <div class="rail"><div class="label">Public writing</div>
        <div class="note">The Financial Express<br>The Daily Star<br>বণিক বার্তা<br>Project Syndicate · VoxEU</div></div>
      <div class="body-col">
        <h2>Commentary</h2>
        <p class="sec-note">From time to time, I write opinion columns for newspapers in Bangla and in
          English as a way of putting my thinking in front of the general reader.</p>
        <div class="currently">
          <div class="cur"><time datetime="2026-04-18">18 Apr 2026</time><p><a href="https://thefinancialexpress.com.bd/columns/bangladeshs-trillion-dollar-trilemma" target="_blank" rel="noopener">Bangladesh's trillion-dollar trilemma</a> · The Financial Express</p></div>
          <div class="cur"><time datetime="2026-03-24">24 Mar 2026</time><p><a href="https://thefinancialexpress.com.bd/views/bangladeshs-unfinished-financial-transition" target="_blank" rel="noopener">Bangladesh's unfinished financial transition</a> · The Financial Express</p></div>
          <div class="cur"><time datetime="2026-03-04">04 Mar 2026</time><p><a href="https://www.bonikbarta.com/editorial/EYl3VkmxlmnkN9Ev" target="_blank" rel="noopener">আমদানি পণ্যের দাম কি সত্যিই বাড়ছে</a> · বণিক বার্তা</p></div>
        </div>
        <a class="more" href="writing.html">All {n_writing} pieces, 2007 to date</a>
      </div>
    </div>
  </div>

  <div class="band">
    <div class="shell">
      <div class="row">
        <div class="rail"><div class="label">Enquiries</div></div>
        <div class="body-col engage">
          <h2>Advisory and commissioned work</h2>
          <p>Alongside my research I do advisory and commissioned work on a regular basis, mainly for
            research institutes, development agencies and public bodies. It usually involves building
            or estimating a model, working with survey and administrative records, or measuring
            something the official statistics do not cover well.</p>
          <p>If you have a project in mind, write to me and I will tell you whether I can help.</p>
          <p class="mail"><a href="mailto:syed.basher@gmail.com">syed.basher@gmail.com</a></p>
        </div>
      </div>
    </div>
  </div>"""

RESEARCH_BODY = f"""
  <div class="shell">
    <div class="hero single">
      <div>
        <h1>Research</h1>
        <p class="lede">Here is a list of my published articles, working papers, book chapters and
          reviews, unpublished papers, and my dissertation. Each entry links to the published version
          where one exists.</p>
        <nav class="toc" aria-label="Sections">{research_toc}</nav>
      </div>
    </div>
{research_body}
  </div>"""

WRITING_BODY = f"""
  <div class="shell">
    <div class="hero single">
      <div>
        <h1>Writing</h1>
        <p class="lede">From time to time, I write opinion columns for newspapers in Bangla and in
          English as a way of putting my thinking in front of the general reader. {n_writing} pieces
          since 2007 are collected here.</p>
      </div>
    </div>
    <div class="divider-strong"></div>
    <div class="row">
      <div class="rail"><div class="label">Archive</div>
        <div class="note">The Financial Express<br>The Daily Star<br>বণিক বার্তা<br>Prothom Alo · কালবেলা<br>Project Syndicate<br>VoxEU · Gulf News</div></div>
      <div class="body-col">{writing_body}</div>
    </div>
  </div>"""

ADVISORY_BODY = f"""
  <div class="shell">
    <div class="hero">
      <div>
        <h1>Advisory work</h1>
        <p class="lede">These are commissioned projects I have worked on for research institutes,
          development agencies and public bodies, with a short note on what each one involved.</p>
        <p class="lede">I am currently working with the Bangladesh Institute of Development Studies
          and the Microcredit Regulatory Authority. Earlier I worked with Bangladesh Bank, and on
          Asian Development Bank and World Bank–financed assignments.</p>
      </div>
      <div class="hero-aside">
        <div class="contact-card flush">
          <div class="label">What I am asked for</div>
          <div class="asked">
            Macro-financial diagnostics<br>Econometric modelling<br>Forecasting and scenarios<br>
            Survey and administrative microdata<br>Geospatial measurement<br>Expert and valuation analysis
          </div>
          <a class="cta" href="mailto:syed.basher@gmail.com">Write to me</a>
        </div>
      </div>
    </div>
    <div class="divider-strong"></div>
    <div class="row">
      <div class="rail"><div class="label">Selected projects</div><div class="note">2010 – 2026</div></div>
      <div class="body-col"><div class="entries">{projects_body}</div></div>
    </div>
  </div>"""

ABOUT_BODY = f"""
  <div class="shell">
    <div class="hero">
      <div>
        <h1>About</h1>
        <div class="prose">
          <p>I am an independent research economist based in Dhaka, with about twenty-five years of
            research experience in energy economics, monetary policy and applied macroeconomics. After
            completing my PhD in Economics at York University in Toronto, I worked from 2007 to 2013
            as a Research Economist in the Department of Research and Monetary Policy at Qatar Central
            Bank, and during that period I also held the position of Economic Consultant to the Qatar
            National Food Security Programme from 2010 to 2012. Both roles involved producing academic
            and policy research for a central bank and a government programme.</p>
          <p>I subsequently served as Senior Research Fellow at Fikra Research &amp; Policy in Doha
            from 2014 to 2016, and at East West University in Dhaka from 2015 to 2025, most recently
            as Professor of Economics and as Acting Director of its Center for Urban Studies and
            Sustainable Development.</p>
          <p>Since 2025 I have been working independently, my time divided between academic research
            and commissioned advisory work for research institutes, development agencies and public
            bodies. I continue to supervise students and to write for the newspapers, in English and
            in Bangla.</p>
        </div>
        <p class="idlinks">{PROFILE_LINKS}</p>
        <a class="cta" href="Syed_Basher_CV.pdf">Curriculum Vitae — PDF</a>
      </div>
      <div class="hero-aside">
        <img class="portrait" src="assets/portrait.jpg" alt="Syed Abul Basher" width="480" height="600">
        <div class="contact-card">
          <div class="label">Write to me</div>
          <a href="mailto:syed.basher@gmail.com">syed.basher@gmail.com</a>
        </div>
      </div>
    </div>
    <div class="divider-strong"></div>
    <div class="row">
      <div class="rail"><div class="label">Education</div></div>
      <div class="body-col">{timeline(EDU)}</div>
    </div>
    <div class="divider-strong"></div>
    <div class="row">
      <div class="rail"><div class="label">Positions</div></div>
      <div class="body-col">{timeline(EXP)}</div>
    </div>
  </div>"""

PAGES = [
 ("index.html", "Syed Abul Basher | Economist and Independent Researcher",
  "Personal website of Syed Abul Basher, economist and independent researcher in Dhaka, working on "
  "Bangladesh's economy, regional and spatial measurement, household welfare, macro-finance, energy "
  "and applied econometrics.", HOME_BODY),
 ("research.html", "Research — Syed Abul Basher",
  f"{n_pub} published articles plus working papers, book chapters, reviews and a dissertation, in "
  "applied economics, energy, macro-finance and the economy of Bangladesh.", RESEARCH_BODY),
 ("writing.html", "Writing — Syed Abul Basher",
  f"{n_writing} newspaper columns and opinion pieces in Bangla and English since 2007, on inflation, "
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
CSS = """/* syedbasher.github.io — generated by site-source/build_site.py */
:root{
  --paper:#ffffff; --band:#f2f4f6;
  --ink:#14202e; --ink-soft:#4c5866; --ink-faint:#6b7580;
  --rule:#d2d7dd; --rule-strong:#14202e;
  --accent:#8c1b2b; --link:#1c4c85;
}
@media (prefers-color-scheme: dark){
  :root{
    --paper:#111823; --band:#18212e;
    --ink:#e9edf2; --ink-soft:#aeb8c3; --ink-faint:#8b95a1;
    --rule:#2a3542; --rule-strong:#8d99a6;
    --accent:#dd8794; --link:#9dc0e8;
  }
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--paper);color:var(--ink);
  font-family:"IBM Plex Sans","Helvetica Neue",Arial,sans-serif;
  font-size:16.5px;line-height:1.66;-webkit-font-smoothing:antialiased}
a{color:var(--link);text-decoration:none}
a:hover{text-decoration:underline;text-decoration-color:var(--accent);
  text-decoration-thickness:1.5px;text-underline-offset:3px}
a:focus-visible{outline:2px solid var(--accent);outline-offset:3px}
h1,h2,h3{font-family:"Source Serif 4",Georgia,"Times New Roman",serif;color:var(--ink);
  margin:0;text-wrap:balance}
p{margin:0}
img{max-width:100%;height:auto}
.skip{position:absolute;left:-9999px;top:0;background:var(--ink);color:var(--paper);
  padding:10px 16px;z-index:100}
.skip:focus{left:12px;top:12px}
[id]{scroll-margin-top:24px}

.topmark{height:3px;background:var(--accent)}
.shell{max-width:1120px;margin:0 auto;padding:0 32px}
.masthead{display:flex;align-items:flex-end;justify-content:space-between;gap:20px;
  flex-wrap:wrap;padding:20px 0 14px;border-bottom:2px solid var(--rule-strong)}
.wordmark{font-family:"Source Serif 4",Georgia,serif;font-size:1.36rem;font-weight:700;
  letter-spacing:-.008em;color:var(--ink);line-height:1.2}
.wordmark:hover{text-decoration:none}
.wordmark small{display:block;font-family:"IBM Plex Mono",monospace;font-size:11px;
  font-weight:500;letter-spacing:.13em;text-transform:uppercase;color:var(--accent);margin-top:5px}
.mastnav{display:flex;gap:21px;flex-wrap:wrap;font-size:.92rem;font-weight:500}
.mastnav a{color:var(--ink-soft);padding-bottom:2px}
.mastnav a.here{color:var(--ink);font-weight:600;box-shadow:inset 0 -2px 0 var(--accent)}

.row{display:grid;grid-template-columns:160px minmax(0,1fr);gap:0 38px}
.rail{border-right:1px solid var(--rule);padding:30px 22px 30px 0}
.body-col{padding:30px 0}
.label{font-family:"IBM Plex Mono",monospace;font-size:10px;letter-spacing:.15em;
  text-transform:uppercase;color:var(--accent);font-weight:600;line-height:1.6}
.rail .note{font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--ink-soft);
  line-height:1.7;margin-top:9px}
.divider-strong{border-top:2px solid var(--rule-strong)}

.hero{display:grid;grid-template-columns:minmax(0,1fr) 236px;gap:52px;
  padding:40px 0 34px;align-items:start}
.hero.single{grid-template-columns:minmax(0,1fr)}
h1{font-size:clamp(2.15rem,4.4vw,2.95rem);line-height:1.08;letter-spacing:-.022em;font-weight:700}
.role{font-size:.98rem;font-weight:500;color:var(--ink-soft);margin-top:10px}
.lede{font-size:1.04rem;line-height:1.74;color:var(--ink-soft);max-width:62ch;margin-top:20px}
.idlinks{display:flex;flex-wrap:wrap;gap:6px 18px;margin-top:22px;font-size:.88rem;font-weight:500}
.cta{display:inline-block;margin-top:16px;font-family:"IBM Plex Mono",monospace;font-size:12px;
  font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--ink);
  border:2px solid var(--rule-strong);padding:10px 17px}
.cta:hover{background:var(--ink);color:var(--paper);text-decoration:none}
.portrait{display:block;width:100%;aspect-ratio:4/5;object-fit:cover;
  border:1px solid var(--rule);background:var(--band)}
.contact-card{margin-top:18px;border-top:2px solid var(--rule-strong);padding-top:12px}
.contact-card.flush{margin-top:0}
.contact-card .label{margin-bottom:6px}
.contact-card > a{font-family:"Source Serif 4",Georgia,serif;font-size:1.06rem;
  font-weight:600;line-height:1.35;word-break:break-word}
.asked{font-size:.9rem;color:var(--ink-soft);line-height:1.65;margin-top:8px}

.record{display:grid;grid-template-columns:repeat(4,1fr);gap:0}
.record > div{padding-right:20px;border-right:1px solid var(--rule)}
.record > div:last-child{border-right:0;padding-right:0}
.record .fig{font-family:"Source Serif 4",Georgia,serif;font-size:1.3rem;font-weight:700;
  line-height:1.22;margin-top:7px;font-variant-numeric:tabular-nums}
.record .fig.long{font-size:1.06rem;line-height:1.3}
.record .sub{font-size:.83rem;color:var(--ink-soft);margin-top:5px;line-height:1.5}

h2{font-size:1.42rem;line-height:1.22;letter-spacing:-.008em;font-weight:700}
.sec-note{color:var(--ink-soft);font-size:.95rem;margin-top:8px;max-width:60ch}

.entries{margin-top:22px;display:flex;flex-direction:column}
.entry{padding:15px 0;border-top:1px solid var(--rule)}
.entry:first-child{border-top:0;padding-top:0}
.entry .meta{font-family:"IBM Plex Mono",monospace;font-size:10px;letter-spacing:.11em;
  text-transform:uppercase;color:var(--accent);font-weight:500}
.entry h3{font-size:1.05rem;line-height:1.4;font-weight:600;margin-top:5px}
.entry h3 a{color:var(--link)}
.entry .by{font-size:.88rem;color:var(--ink-soft);margin-top:4px}
.entry p.desc{font-size:.92rem;color:var(--ink-soft);margin-top:6px;max-width:62ch}

.split{display:grid;grid-template-columns:1fr 1fr;gap:0 40px}
.split > div:last-child{border-left:1px solid var(--rule);padding-left:40px}
.track-kicker{font-family:"IBM Plex Mono",monospace;font-size:10px;letter-spacing:.15em;
  text-transform:uppercase;color:var(--accent);font-weight:600;margin-bottom:8px}
.more{display:inline-block;margin-top:16px;font-size:.88rem;font-weight:500}
.more::after{content:" \\2192"}

.currently{display:flex;flex-direction:column;margin-top:22px}
.cur{display:grid;grid-template-columns:78px minmax(0,1fr);gap:16px;padding:10px 0;
  border-top:1px solid var(--rule);align-items:baseline}
.cur:first-child{border-top:0;padding-top:0}
.cur time{font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--ink-soft);
  font-variant-numeric:tabular-nums}
.cur p{font-size:.95rem;line-height:1.58}

.band{background:var(--band);border-top:2px solid var(--rule-strong);
  border-bottom:2px solid var(--rule-strong)}
.engage h2{font-size:1.32rem}
.engage p{color:var(--ink-soft);margin-top:10px;max-width:60ch}
.engage .mail{margin-top:18px;font-family:"Source Serif 4",Georgia,serif;
  font-size:1.14rem;font-weight:600}

.toc{display:flex;flex-wrap:wrap;gap:8px 10px;margin-top:24px;padding-top:18px;
  border-top:1px solid var(--rule)}
.toc a{font-family:"IBM Plex Mono",monospace;font-size:11.5px;font-weight:600;letter-spacing:.08em;
  text-transform:uppercase;border:1px solid var(--rule);padding:8px 12px;color:var(--link)}
.toc a:hover{border-color:var(--link);text-decoration:none}
.toc a em{font-style:normal;font-weight:500;color:var(--ink-soft);margin-left:6px}

.yearhead{font-family:"IBM Plex Mono",monospace;font-size:12px;font-weight:600;
  letter-spacing:.14em;color:var(--accent);padding:22px 0 8px;
  border-top:1px solid var(--rule);margin-top:12px;font-variant-numeric:tabular-nums}
.yearhead:first-child{margin-top:0;border-top:0;padding-top:0}
.pub{padding:11px 0;border-top:1px solid var(--rule)}
.yearhead + .pub{border-top:0;padding-top:2px}
.pub .t{font-family:"Source Serif 4",Georgia,serif;font-size:1.03rem;font-weight:600;line-height:1.42}
.pub .t a{color:var(--link)}
.pub .cite{font-size:.88rem;color:var(--ink-soft);margin-top:3px;line-height:1.5}

.wr{display:grid;grid-template-columns:74px minmax(0,1fr);gap:18px;padding:11px 0;
  border-top:1px solid var(--rule)}
.yearhead + .wr{border-top:0;padding-top:2px}
.wr time{font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--ink-soft);
  padding-top:3px;font-variant-numeric:tabular-nums}
.wr .t{font-family:"Source Serif 4",Georgia,serif;font-size:1.03rem;font-weight:600;line-height:1.42}
.wr .t a{color:var(--link)}
.wr .outlet{font-size:.87rem;color:var(--ink-soft);margin-top:3px}

.tlrow{display:grid;grid-template-columns:120px minmax(0,1fr);gap:20px;padding:13px 0;
  border-top:1px solid var(--rule)}
.tlrow:first-child{border-top:0;padding-top:0}
.tlrow time{font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--ink-soft);
  padding-top:2px;font-variant-numeric:tabular-nums}
.tlt{font-family:"Source Serif 4",Georgia,serif;font-size:1.03rem;font-weight:600}
.tls{font-size:.9rem;color:var(--ink-soft);margin-top:2px}
.tlsub{font-size:.9rem;color:var(--ink-soft);margin-top:7px;padding-left:13px;
  border-left:2px solid var(--rule)}
.prose{font-size:1.02rem;line-height:1.75;color:var(--ink-soft);max-width:62ch;margin-top:20px}
.prose p + p{margin-top:13px}

.site-foot{padding:24px 0 42px;font-size:.84rem;color:var(--ink-soft)}
.site-foot strong{font-family:"Source Serif 4",Georgia,serif;color:var(--ink);font-size:.98rem}
.foot-links{display:flex;gap:16px;flex-wrap:wrap;margin-top:9px}

@media (max-width:880px){
  .shell{padding:0 20px}
  body{font-size:16px}
  .masthead{align-items:flex-start;padding-top:18px}
  .mastnav{gap:15px;font-size:.86rem}
  .row{grid-template-columns:minmax(0,1fr)}
  .rail{border-right:0;border-bottom:1px solid var(--rule);padding:24px 0 11px}
  .body-col{padding:16px 0 28px}
  .hero{grid-template-columns:minmax(0,1fr);gap:28px;padding:30px 0 26px}
  .hero-aside{max-width:300px}
  h1{font-size:2.1rem}
  h2{font-size:1.3rem}
  .record{grid-template-columns:1fr 1fr;gap:22px 0}
  .record > div{border-right:0;padding-right:14px}
  .split{grid-template-columns:minmax(0,1fr);gap:30px}
  .split > div:last-child{border-left:0;padding-left:0;border-top:1px solid var(--rule);padding-top:28px}
  .cur,.wr,.tlrow{grid-template-columns:minmax(0,1fr);gap:3px}
  .wr time,.tlrow time{padding-top:0}
}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{transition:none!important;animation:none!important}}
@media print{
  .topmark,.mastnav,.skip,.toc,.band{display:none}
  body{font-size:11pt;color:#000;background:#fff}
  a{color:#000;text-decoration:underline}
  .row{grid-template-columns:minmax(0,1fr)}
  .rail{border:0;padding:12px 0 0}
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
  <div class="shell">
    <div class="hero single">
      <div>
        <h1>Page not found</h1>
        <p class="lede">The address you followed does not exist on this site. It may have been
          renamed, or the link that brought you here may be out of date.</p>
        <p class="idlinks"><a href="index.html">Home</a><a href="research.html">Research</a>
          <a href="writing.html">Writing</a><a href="advisory.html">Advisory</a>
          <a href="about.html">About</a></p>
      </div>
    </div>
  </div>""", active=None)

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
