#!/usr/bin/env python3
"""Generate cinematic, SEO/AEO service pages from shared chrome."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")

HEADER = INDEX[INDEX.find("  <a class=\"lux-skip\"") : INDEX.find("</header>") + len("</header>")]
FOOTER = INDEX[INDEX.find("    <!-- footer wrap -->") :]

ALL_SERVICES = [
    ("software-development.html", "Software development"),
    ("web-development.html", "Web development"),
    ("ecommerce.html", "eCommerce"),
    ("digital-marketing.html", "Digital marketing"),
    ("product-engineer.html", "Product engineering"),
    ("cloud-devops.html", "Cloud and DevOps"),
    ("content-management-system.html", "CMS"),
    ("data-science.html", "Data science"),
    ("quality-engineering.html", "Quality engineering"),
]

PAGES = [
    {
        "file": "software-development.html",
        "slug": "software-development",
        "title": "Custom Software Development in Delhi NCR | BlueByte",
        "description": "BlueByte builds custom software in Delhi NCR around your workflows, integrations and growth plans. Request a scoped proposal for web, mobile or internal systems.",
        "service_name": "Custom software development",
        "kicker": "Software",
        "h1": "Custom software development in Delhi NCR.",
        "lead": "BlueByte designs and builds software around how your team actually works: web apps, internal tools and mobile products that stay readable, secure and ready to grow.",
        "intro": [
            "BlueByte IT Solutions is a software development company in Delhi NCR that writes custom applications when off-the-shelf tools start to creak. We start with your workflows, then shape the product, not the other way around.",
            "Startups and established teams come to us for web applications, enterprise systems and mobile apps. The brief is the same in each case: secure, scalable software that meets today and does not trap you tomorrow.",
        ],
        "offers_title": "What we build",
        "offers": [
            ("End-to-end custom systems", "Software designed around your goals, workflows and customers. No generic templates."),
            ("Agile, staged delivery", "Short cycles, visible milestones and room to steer without throwing the plan away."),
            ("The right stack, not a pile", "Modern languages and frameworks where they earn their keep, proven tools where they keep you safe."),
            ("User-centred design", "Interfaces your team will actually use, tested with real tasks before we call them done."),
            ("Systems that connect", "APIs and integrations with the finance, CRM and operations tools you already run."),
            ("Security by default", "Access control, encryption and audit trails treated as product work, not a later patch."),
        ],
        "faqs": [
            ("What custom software does BlueByte build in Delhi?", "Web applications, internal business systems, mobile apps and integrations, scoped to your workflows rather than a packaged product."),
            ("How long does a software project take?", "A focused internal tool can ship in a few weeks. Larger platforms follow a dated plan after discovery, with milestones you can audit."),
            ("Do you take over existing software?", "Yes. We audit the codebase, risk and cost of change, then improve in stages instead of forcing a risky rewrite."),
            ("How is pricing handled?", "After a short brief we send a written proposal: what is included, what is not, and how change requests are priced."),
        ],
    },
    {
        "file": "web-development.html",
        "slug": "web-development",
        "title": "Web Development Company in Delhi NCR | BlueByte",
        "description": "Plan a fast, responsive website or web application with BlueByte, a web development company in Delhi NCR serving businesses across India.",
        "service_name": "Web development",
        "kicker": "Web",
        "h1": "Web development for brands that need to convert.",
        "lead": "BlueByte is a web development company in Delhi NCR. We design and build fast, secure, mobile-ready sites and web apps that are easy to manage and built for search.",
        "intro": [
            "A static brochure site rarely holds attention. BlueByte IT Solutions builds dynamic websites for Delhi NCR businesses that need real-time content, clean integrations and a calm experience on every device.",
            "Whether you are a startup, a store or a growing company, we combine modern frameworks with careful design so the site can change as the business does, without a rebuild every season.",
        ],
        "offers_title": "Website work, in practice",
        "offers": [
            ("Fast by design", "Caching, image discipline and lean code so pages load quickly and bounce rates stay down."),
            ("Built for your brief", "Information architecture, design and development shaped around your brand and audience, not a theme."),
            ("Responsive on every screen", "Layouts that stay readable and usable on phones, tablets and desktops."),
            ("A CMS you will use", "WordPress, a headless CMS or a custom admin so editors can publish without calling engineering."),
            ("Secure, scalable foundations", "Sensible hosting, backups and access control so the site holds as traffic grows."),
            ("Search-ready markup", "Clean HTML, structured data where it helps, and performance that search engines can reward."),
        ],
        "faqs": [
            ("Is BlueByte a web development company in Delhi NCR?", "Yes. We design and develop custom websites and web applications for clients in Delhi, Noida, Gurugram and across India."),
            ("How long does a new website take?", "A marketing site often ships in four to eight weeks. Web applications follow a plan written after discovery."),
            ("Will the site work on mobile?", "Yes. Responsive layout, tap targets and performance on mid-range phones are part of the build, not extras."),
            ("Can you rebuild an existing website?", "We can redesign, migrate content and improve speed or SEO in stages so you do not go dark while we work."),
        ],
    },
    {
        "file": "ecommerce.html",
        "slug": "ecommerce",
        "title": "eCommerce Website and Platform Development | BlueByte",
        "description": "Build an eCommerce store with BlueByte: custom storefronts, Shopify or WooCommerce, payments, inventory and care plans for Delhi NCR and India.",
        "service_name": "eCommerce development",
        "kicker": "Commerce",
        "h1": "eCommerce that sells, then stays up.",
        "lead": "BlueByte designs storefronts around your catalogue, checkout and operations, from first product to sale-day traffic, with integrations that keep orders moving.",
        "intro": [
            "An online store is a system, not a skin. We plan catalogue, search, cart, payment and fulfilment together so shoppers can buy without friction and your team can run the day without spreadsheets.",
            "Shopify, WooCommerce or a custom stack: we pick the platform that fits the catalogue and the team who will live in it, then wire payments, shipping and inventory so nothing is retyped.",
        ],
        "offers_title": "Store capabilities",
        "offers": [
            ("Custom storefronts", "Theme or headless builds that match the brand and still check out in a few taps."),
            ("Platform migration", "Move from a tired cart to Shopify, WooCommerce or a custom platform without losing SEO or order history."),
            ("Speed on sale days", "Performance work so the store holds when a campaign lands."),
            ("Payments and ops", "Gateways, tax, shipping and inventory connected to the tools you already use."),
            ("Headless commerce", "A flexible front end on a stable commerce engine when the brand needs more control."),
            ("Care after launch", "Updates, plugin hygiene and monitoring so the till keeps ringing."),
        ],
        "faqs": [
            ("Which eCommerce platforms do you work with?", "Shopify, WooCommerce and custom storefronts. We recommend based on catalogue size, team skills and the integrations you need."),
            ("Can you migrate my existing store?", "Yes. We map products, customers, redirects and checkout so rankings and order history survive the move."),
            ("Do you handle payments and shipping?", "We integrate the gateways and carriers you choose, plus inventory and GST-ready invoicing where needed."),
            ("How do you keep a store fast?", "Image policy, caching, lean scripts and load tests before campaigns, not after they fail."),
        ],
    },
    {
        "file": "digital-marketing.html",
        "slug": "digital-marketing",
        "title": "Digital Marketing and SEO Services | BlueByte Delhi NCR",
        "description": "BlueByte plans SEO, content and paid channels around your audience. Digital marketing for Delhi NCR businesses that want traffic that can convert.",
        "service_name": "Digital marketing and SEO",
        "kicker": "Growth",
        "h1": "Digital marketing that answers, then converts.",
        "lead": "BlueByte builds search, content and campaign systems for Delhi NCR brands. The goal is qualified traffic and clear reporting, not vanity charts.",
        "intro": [
            "A website without a plan is a quiet room. We combine technical SEO, useful pages and paid media so the right people can find you, then measure what they do next.",
            "Every campaign starts with audience, offer and a number you care about. We then pick channels, write the work, and report in language a founder can read.",
        ],
        "offers_title": "How we grow a channel",
        "offers": [
            ("Search engine optimisation", "On-page, technical and local SEO so Google can understand the business and send intent-rich visits."),
            ("Paid search and ads", "PPC with tight match types, landing pages and budgets you can defend."),
            ("Content that ranks and helps", "Guides and service pages written for people first, structured so search can quote them."),
            ("Social with a job", "Channel plans that support the offer, not a random posting calendar."),
            ("Email and journeys", "Lifecycle mail that follows a real path: welcome, nurture, win-back."),
            ("Analytics you will open", "Dashboards tied to leads and revenue, not only sessions."),
        ],
        "faqs": [
            ("Do you offer SEO for businesses in Delhi NCR?", "Yes. Technical SEO, content and Google Business work for local and national search, with reporting on rankings, traffic and leads."),
            ("How soon will we see results?", "Paid campaigns can move in days. Organic search usually needs a few months of consistent pages and fixes. We set that expectation in writing."),
            ("Do you only run ads?", "No. We prefer a mix: a site that can rank, content that answers questions, and paid media where it earns its cost."),
            ("Will we own the accounts?", "Yes. Analytics, ads and Search Console stay in your name. We work inside them."),
        ],
    },
    {
        "file": "product-engineer.html",
        "slug": "product-engineer",
        "title": "Digital Product Engineering Services | BlueByte",
        "description": "Turn a product idea into a maintainable digital service with BlueByte: discovery, architecture, MVP, engineering and lifecycle care in Delhi NCR.",
        "service_name": "Product engineering",
        "kicker": "Product",
        "h1": "Product engineering from idea to a calm launch.",
        "lead": "BlueByte takes a product from discovery to a maintainable service: research, architecture, MVP, mobile and the care a live system needs.",
        "intro": [
            "Product engineering here means a team that stays with the work. We shape the offer, design the service, write the software and keep it healthy after users arrive.",
            "The aim is a product the market can use, on a budget you can explain. Discovery first, then an MVP that tests the riskiest assumption, then a build that will not collapse at version two.",
        ],
        "offers_title": "The product path",
        "offers": [
            ("Discovery and design", "User evidence, market constraints and a product shape before we spend on code."),
            ("Software engineering", "Architecture and delivery that a new engineer can enter without a guided tour."),
            ("Mobile products", "iOS, Android or a shared codebase when the job is in someone's pocket."),
            ("Prototypes and MVPs", "A thin, honest first release that tests demand instead of decorating a guess."),
            ("Quality in the loop", "Testing planned with the build so launch is not a surprise."),
            ("Lifecycle after launch", "Roadmaps, refactors and product ops so the thing you shipped keeps earning."),
        ],
        "faqs": [
            ("What is product engineering at BlueByte?", "A through-line from research and architecture to MVP, full build and ongoing care, with one team accountable for the outcome."),
            ("Can you start with an MVP?", "Yes. We cut to the smallest release that tests the real risk, then plan the next slice from what users do."),
            ("Do you work with in-house product teams?", "We pair with your PM and design leads, or we can hold the brief when you do not have that bench yet."),
            ("How do you control cost?", "A written scope, staged delivery and a change path. You see the burn before it becomes a story."),
        ],
    },
    {
        "file": "cloud-devops.html",
        "slug": "cloud-devops",
        "title": "Cloud and DevOps Services | BlueByte IT Solutions",
        "description": "Plan cloud migration, infrastructure automation and delivery pipelines with BlueByte. Secure, observable platforms for Delhi NCR teams.",
        "service_name": "Cloud and DevOps",
        "kicker": "Cloud",
        "h1": "Cloud and DevOps that stay quiet in production.",
        "lead": "BlueByte designs cloud platforms and delivery pipelines so releases are boring, costs are visible and recovery is a drill, not a crisis.",
        "intro": [
            "Traditional IT tickets cannot keep up with a product that ships weekly. We help Delhi NCR teams move to cloud platforms, automate the path to production and keep the system observable.",
            "The work is practical: a migration plan, infrastructure as code, CI/CD, cost controls and a security baseline. Development and operations share one way of working.",
        ],
        "offers_title": "Platform work",
        "offers": [
            ("Cloud strategy", "A roadmap for migrate, hybrid or tidy-what-you-have, with cost and risk named up front."),
            ("Migration without drama", "Workloads moved in slices, with rollback, so the business does not pause for a cutover weekend."),
            ("Infrastructure as code", "Environments you can recreate, review and audit, instead of a snowflake server."),
            ("CI and CD", "Pipelines that test and ship on every change worth shipping."),
            ("Cost and security", "Rightsizing, alerts, identity and compliance treated as weekly hygiene."),
            ("Containers and recovery", "Orchestration where it helps, plus backups and drills you have actually run."),
        ],
        "faqs": [
            ("Which clouds do you work with?", "Amazon Web Services, Microsoft Azure and Google Cloud, plus hybrid setups when a system must stay on the premises."),
            ("Can you migrate a live application?", "Yes. We inventory dependencies, move in stages and keep a rollback. The business stays online."),
            ("Do you set up CI/CD from scratch?", "We introduce pipelines, environments and checks that match how your team already commits code."),
            ("Will you help after go-live?", "Managed support is available: monitoring, patches, cost reviews and incident help."),
        ],
    },
    {
        "file": "content-management-system.html",
        "slug": "content-management-system",
        "title": "CMS Development and Integration Services | BlueByte",
        "description": "Choose and customise a CMS that fits your publishing workflow, roles and integrations. WordPress, headless or custom, delivered by BlueByte.",
        "service_name": "CMS development",
        "kicker": "Content",
        "h1": "A CMS your editors will actually open.",
        "lead": "BlueByte designs content systems that match how you publish: WordPress, headless or custom, with roles, SEO-ready markup and the integrations your site needs.",
        "intro": [
            "A content management system should let a marketer change a page without waiting on engineering. We build and customise CMS platforms that are simple to use, safe to share and sturdy under traffic.",
            "Corporate sites, stores and journals all need different editing models. We pick the platform for the workflow, then add roles, previews and the connectors you rely on.",
        ],
        "offers_title": "CMS capabilities",
        "offers": [
            ("Custom CMS builds", "When a packaged tool fights the workflow, we shape one that fits, from small sites to multi-brand systems."),
            ("An editor-first interface", "Clear fields, previews and guardrails so publishing is a calm task."),
            ("Search-friendly output", "Clean URLs, metadata and structured content that SEO work can stand on."),
            ("Roles and governance", "Who can draft, who can publish, and an audit trail when it matters."),
            ("Platforms we know", "WordPress, headless CMS options and custom admin when the brief demands it."),
            ("Integrations", "CRM, DAM, forms, commerce and analytics without copy-paste between tools."),
        ],
        "faqs": [
            ("Which CMS should we choose?", "It depends on editors, languages, integrations and who will maintain it. We recommend after a short workflow review, not from a default."),
            ("Can you work with WordPress?", "Yes. Theme or block builds, custom plugins, and hardening so the site is not a plugin pile."),
            ("Do you build headless CMS setups?", "When the front end needs to live in more than one place, we separate content from presentation and keep editors in one admin."),
            ("Will non-technical staff be able to update pages?", "That is the point. Training and a simple editing model are part of delivery."),
        ],
    },
    {
        "file": "data-science.html",
        "slug": "data-science",
        "title": "Data Science and Analytics Solutions | BlueByte",
        "description": "Make business data useful with analytics engineering, data science and applied machine learning from BlueByte, designed around decisions you can measure.",
        "service_name": "Data science and analytics",
        "kicker": "Data",
        "h1": "Data science that changes a decision.",
        "lead": "BlueByte turns scattered data into models, dashboards and forecasts your team can act on. The test is a clearer choice, not a prettier chart.",
        "intro": [
            "Most companies are rich in files and poor in answers. We help Delhi NCR teams clean the pipes, ask a sharper question and put a model or a dashboard where the decision actually happens.",
            "The work spans analytics engineering, machine learning and visualisation. We only build what someone will use next week.",
        ],
        "offers_title": "How we use data",
        "offers": [
            ("Exploration that names the question", "We find the pattern, then agree what decision it should change."),
            ("Forecasts you can brief", "Demand, churn or risk models with assumptions written in plain language."),
            ("Applied machine learning", "Models in the workflow, with monitoring so they do not silently drift."),
            ("Language and vision", "NLP and computer vision when the input is text or images, not a spreadsheet."),
            ("Pipelines that hold", "Warehouses, quality checks and jobs that run without a hero on call."),
            ("Reporting people open", "Visuals tied to the metric a founder already watches."),
        ],
        "faqs": [
            ("What data science services does BlueByte offer?", "Analytics engineering, forecasting, applied machine learning, NLP, visualisation and the pipelines that keep them honest."),
            ("Do we need a data warehouse first?", "Often yes, even a small one. We will say so if the data is too messy to model well."),
            ("Will models run in our cloud?", "We deploy into your environment where possible, with access control and monitoring you own."),
            ("How do you measure success?", "A decision that changed, a process that shrank, or a forecast that beat the previous guess. We agree the measure before we build."),
        ],
    },
    {
        "file": "quality-engineering.html",
        "slug": "quality-engineering",
        "title": "Software Quality Engineering and Testing | BlueByte",
        "description": "Improve software reliability with risk-based testing, automation and quality engineering from BlueByte, designed around your product and release process.",
        "service_name": "Quality engineering",
        "kicker": "Quality",
        "h1": "Quality engineering that finds issues before users do.",
        "lead": "BlueByte plans testing around risk: function, performance, security and access, with automation where it earns its keep and humans where judgement is required.",
        "intro": [
            "Quality engineering is not a gate at the end. We design checks into the build so defects show up while they are cheap, and releases stay boring.",
            "Functional gaps, slow pages, weak auth and inaccessible screens all count. We cover them with a mix of exploratory work, automated suites and performance tests matched to how you ship.",
        ],
        "offers_title": "What we test for",
        "offers": [
            ("Core behaviour", "Every important path works as specified, with gaps found before customers do."),
            ("Faster, safer releases", "Automation on the boring checks so people can spend time on the risky ones."),
            ("Speed and stability", "Load and endurance tests so the system holds when traffic arrives."),
            ("Security basics that matter", "Auth, injection, secrets and the boring attacks that still work."),
            ("Data you can trust", "Checks on accuracy, migrations and reports that finance will read."),
            ("Access for more people", "Keyboard, contrast, names and structure so the product is usable, not only pretty."),
        ],
        "faqs": [
            ("What is quality engineering at BlueByte?", "Testing designed into the product lifecycle: strategy, automation, performance, security and accessibility, not a last-week scramble."),
            ("Do you only write automated tests?", "No. Automation covers the stable paths. Exploratory testing still catches the strange ones."),
            ("Can you join our CI pipeline?", "Yes. Suites run on pull requests and nightly builds, with failures that point to a cause."),
            ("Do you test mobile and web?", "Both, including device coverage that matches your actual users, not a lab of flagships."),
        ],
    },
]


def related_for(filename: str) -> list[tuple[str, str]]:
    others = [s for s in ALL_SERVICES if s[0] != filename]
    return others[:4]


def schema_block(page: dict) -> str:
    url = "{{SITE_URL}}/" + page["slug"]
    faqs = [
        {
            "@type": "Question",
            "name": item[0],
            "acceptedAnswer": {"@type": "Answer", "text": item[1]},
        }
        for item in page["faqs"]
    ]
    graph = [
        {
            "@type": "Organization",
            "@id": "{{SITE_URL}}/#organization",
            "name": "BlueByte IT Solutions",
            "url": "{{SITE_URL}}/",
        },
        {
            "@type": "WebPage",
            "@id": url + "#webpage",
            "url": url,
            "name": page["title"],
            "description": page["description"],
            "inLanguage": "en-IN",
            "isPartOf": {"@id": "{{SITE_URL}}/#website"},
            "speakable": {
                "@type": "SpeakableSpecification",
                "cssSelector": [".lux-lead", ".lux-prose", ".lux-faq-list"],
            },
            "primaryImageOfPage": {
                "@type": "ImageObject",
                "url": "{{SITE_URL}}/images/og-image.webp",
            },
            "breadcrumb": {"@id": url + "#breadcrumb"},
        },
        {
            "@type": "Service",
            "@id": url + "#service",
            "name": page["service_name"],
            "url": url,
            "description": page["description"],
            "provider": {"@id": "{{SITE_URL}}/#organization"},
            "areaServed": [
                {"@type": "City", "name": "Delhi"},
                {"@type": "AdministrativeArea", "name": "Delhi NCR"},
                {"@type": "Country", "name": "India"},
            ],
            "serviceType": page["service_name"],
        },
        {
            "@type": "BreadcrumbList",
            "@id": url + "#breadcrumb",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "Home",
                    "item": "{{SITE_URL}}/",
                },
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": "Services",
                    "item": "{{SITE_URL}}/",
                },
                {
                    "@type": "ListItem",
                    "position": 3,
                    "name": page["service_name"],
                    "item": url,
                },
            ],
        },
        {"@type": "FAQPage", "mainEntity": faqs},
    ]
    payload = {"@context": "https://schema.org", "@graph": graph}
    dumped = json.dumps(payload, indent=2, ensure_ascii=True)
    return dumped.replace("\\/", "/")


def offers_html(page: dict) -> str:
    cards = []
    for i, (title, text) in enumerate(page["offers"], 1):
        cards.append(
            f"""            <article class="lux-service">
              <span class="lux-service-num">{i:02d}</span>
              <h3>{title}</h3>
              <p>{text}</p>
            </article>"""
        )
    return "\n".join(cards)


def faqs_html(page: dict) -> str:
    blocks = []
    for i, (q, a) in enumerate(page["faqs"]):
        open_attr = " open" if i == 0 else ""
        blocks.append(
            f"""            <details{open_attr}>
              <summary>{q}</summary>
              <p>{a}</p>
            </details>"""
        )
    return "\n".join(blocks)


def related_html(page: dict) -> str:
    chips = []
    for href, label in related_for(page["file"]):
        chips.append(
            f'            <a class="lux-chip" href="{href}">{label} <span aria-hidden="true">→</span></a>'
        )
    return "\n".join(chips)


def page_html(page: dict) -> str:
    schema = schema_block(page)
    intro = "\n".join(f"            <p>{para}</p>" for para in page["intro"])
    return f"""<!DOCTYPE html>
<html lang="en-IN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta http-equiv="X-UA-Compatible" content="ie=edge">
  <link rel="icon" href="/images/favicon.png" type="image/png">
  <title>{page["title"]}</title>
  <meta name="description" content="{page["description"]}">
  <meta name="author" content="BlueByte IT Solutions">
  <meta name="robots" content="index,follow">
  <meta property="og:locale" content="en_IN">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{page["title"]}">
  <meta property="og:description" content="{page["description"]}">
  <meta property="og:site_name" content="BlueByte IT Solutions">
  <meta property="og:image" content="{{{{SITE_URL}}}}/images/og-image.webp">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{page["title"]}">
  <meta name="twitter:description" content="{page["description"]}">
  <meta name="twitter:image" content="{{{{SITE_URL}}}}/images/og-image.webp">
  <meta name="msapplication-TileColor" content="#071315">
  <meta name="theme-color" content="#071315">
  <meta http-equiv="x-dns-prefetch-control" content="on">
  <link rel="canonical" href="{{{{SITE_URL}}}}/{page["slug"]}">
  <meta property="og:url" content="{{{{SITE_URL}}}}/{page["slug"]}">
  <link rel="preload" href="/fonts/Sora-700.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="/fonts/dm-sans-400.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="/css/home.min.css" as="style" fetchpriority="high">
  <link rel="stylesheet" href="/css/home.min.css">
  <link rel="stylesheet" href="/css/home.css">
  <script src="js/analytics.js" defer></script>
  <script src="js/home.js" defer></script>
  <meta name="google-analytics-id" content="{{{{GA_MEASUREMENT_ID}}}}">
<script type="application/ld+json">
{schema}
</script>
</head>
<body>
{HEADER}
    <main id="main" class="lux-main">
      <section class="lux-hero lux-hero--page" aria-labelledby="service-hero-title">
        <div class="lux-hero-inner">
          <nav class="lux-crumb" aria-label="Breadcrumb">
            <a href="/">Home</a>
            <span aria-hidden="true">/</span>
            <span>Services</span>
            <span aria-hidden="true">/</span>
            <span aria-current="page">{page["service_name"]}</span>
          </nav>
          <p class="lux-kicker lux-rise">{page["kicker"]} · Delhi NCR</p>
          <h1 id="service-hero-title" data-split>{page["h1"]}</h1>
          <p class="lux-lead lux-rise lux-rise-2">{page["lead"]}</p>
          <div class="lux-actions lux-rise lux-rise-3">
            <a class="lux-btn lux-btn-gold" href="contact.html">Request a proposal</a>
            <a class="lux-btn lux-btn-ghost" href="tel:+918178838292">Talk to our experts</a>
          </div>
        </div>
      </section>

      <section class="lux-section lux-theme-light" aria-labelledby="intro-title" data-reveal>
        <div class="lux-wrap lux-split">
          <div>
            <p class="lux-kicker">Overview</p>
            <h2 id="intro-title" class="lux-title" data-split>A direct answer, then the work.</h2>
          </div>
          <div class="lux-prose">
{intro}
          </div>
        </div>
      </section>

      <section class="lux-section lux-theme-dark" aria-labelledby="offers-title" data-reveal>
        <div class="lux-wrap">
          <p class="lux-kicker">Capabilities</p>
          <h2 id="offers-title" class="lux-title" data-split>{page["offers_title"]}</h2>
          <div class="lux-service-grid">
{offers_html(page)}
          </div>
        </div>
      </section>

      <section class="lux-section lux-theme-light" aria-labelledby="method-title" data-reveal>
        <div class="lux-wrap">
          <p class="lux-kicker">Method</p>
          <h2 id="method-title" class="lux-title" data-split>Four measured steps.</h2>
          <p class="lux-lead">We keep the sequence short, visible and easy to steer.</p>
          <div class="lux-steps">
            <article class="lux-step">
              <h3>Discover</h3>
              <p>Goals, users and constraints on the table before a line of code is promised.</p>
            </article>
            <article class="lux-step">
              <h3>Shape</h3>
              <p>Architecture, experience and a dated plan you can share internally.</p>
            </article>
            <article class="lux-step">
              <h3>Build</h3>
              <p>Staged delivery with reviews, tests and a changelog a non-engineer can read.</p>
            </article>
            <article class="lux-step">
              <h3>Care</h3>
              <p>Launch, measure, patch. The product stays calm after the applause.</p>
            </article>
          </div>
        </div>
      </section>

      <section class="lux-section lux-theme-dark" aria-labelledby="faq-title" data-reveal>
        <div class="lux-wrap">
          <p class="lux-kicker">Questions</p>
          <h2 id="faq-title" class="lux-title" data-split>Answers search and people both need.</h2>
          <div class="lux-faq-list">
{faqs_html(page)}
          </div>
        </div>
      </section>

      <section class="lux-section lux-theme-light" aria-labelledby="more-title" data-reveal>
        <div class="lux-wrap">
          <p class="lux-kicker">Also in the studio</p>
          <h2 id="more-title" class="lux-title" data-split>Related services.</h2>
          <div class="lux-related">
{related_html(page)}
          </div>
        </div>
      </section>

      <section class="lux-section lux-cta lux-theme-dark" aria-labelledby="cta-title" data-reveal>
        <div class="lux-wrap lux-cta-inner">
          <p class="lux-kicker">Begin</p>
          <h2 id="cta-title" class="lux-title" data-split>Ready to talk about this work?</h2>
          <p class="lux-lead">Send the brief. We will answer with a clear next step, not a deck full of fog.</p>
          <div class="lux-actions">
            <a class="lux-btn lux-btn-gold" href="contact.html">Let's connect</a>
            <a class="lux-btn lux-btn-ghost" href="https://wa.me/918178838292" target="_blank" rel="noopener noreferrer">WhatsApp us</a>
          </div>
        </div>
      </section>
    </main>
{FOOTER}
"""


def assert_clean(text: str, name: str) -> None:
    if "\u2014" in text or "\u2013" in text:
        raise SystemExit(f"dash found in {name}")
    if text.count("<h1") != 1:
        raise SystemExit(f"h1 count {text.count('<h1')} in {name}")


def main() -> None:
    for page in PAGES:
        html = page_html(page)
        assert_clean(html, page["file"])
        json.loads(
            html.split('<script type="application/ld+json">', 1)[1]
            .split("</script>", 1)[0]
            .replace("{{SITE_URL}}", "https://example.com")
            .replace("{{GA_MEASUREMENT_ID}}", "")
        )
        (ROOT / page["file"]).write_text(html, encoding="utf-8")
        print("wrote", page["file"], html.count("\n"), "lines")


if __name__ == "__main__":
    main()
