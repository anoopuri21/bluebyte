#!/usr/bin/env python3
"""Generate remaining cinematic pages and wrap blog articles."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
HEADER = INDEX[INDEX.find('  <a class="lux-skip"') : INDEX.find("</header>") + len("</header>")]
FOOTER = INDEX[INDEX.find("    <!-- footer wrap -->") :]

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_service_pages import ico  # noqa: E402


def clean_dashes(text: str) -> str:
    return (
        text.replace("\u2014", ",")
        .replace("\u2013", ",")
        .replace("Brainstroming", "Brainstorming")
        .replace("Contact with our team", "Visit our studio")
    )


def head(
    title: str,
    description: str,
    slug: str,
    image: str,
    schema: str,
    keywords: str = "",
    og_type: str = "website",
) -> str:
    kw = f'\n  <meta name="keywords" content="{keywords}">' if keywords else ""
    return f"""<!DOCTYPE html>
<html lang="en-IN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta http-equiv="X-UA-Compatible" content="ie=edge">
  <link rel="icon" href="/images/favicon.png" type="image/png">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <meta name="author" content="BlueByte IT Solutions">
  <meta name="robots" content="index,follow">{kw}
  <meta property="og:locale" content="en_IN">
  <meta property="og:type" content="{og_type}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:site_name" content="BlueByte IT Solutions">
  <meta property="og:image" content="{{{{SITE_URL}}}}/{image}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{description}">
  <meta name="twitter:image" content="{{{{SITE_URL}}}}/{image}">
  <meta name="msapplication-TileColor" content="#071315">
  <meta name="theme-color" content="#071315">
  <link rel="canonical" href="{{{{SITE_URL}}}}/{slug}">
  <meta property="og:url" content="{{{{SITE_URL}}}}/{slug}">
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
"""


def dumps(obj) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=True).replace("\\/", "/")


def webpage_schema(slug: str, title: str, description: str, image: str, extra=None) -> str:
    url = "{{SITE_URL}}/" + slug
    graph = [
        {"@type": "Organization", "@id": "{{SITE_URL}}/#organization", "name": "BlueByte IT Solutions", "url": "{{SITE_URL}}/"},
        {
            "@type": "WebPage",
            "@id": url + "#webpage",
            "url": url,
            "name": title,
            "description": description,
            "inLanguage": "en-IN",
            "dateModified": "2026-09-27",
            "isPartOf": {"@id": "{{SITE_URL}}/#website"},
            "speakable": {"@type": "SpeakableSpecification", "cssSelector": [".lux-lead", ".lux-prose", ".lux-faq-list"]},
            "primaryImageOfPage": {"@type": "ImageObject", "url": "{{SITE_URL}}/" + image},
        },
    ]
    if extra:
        graph.extend(extra)
    return dumps({"@context": "https://schema.org", "@graph": graph})


def faqs_html(items):
    out = []
    for i, (q, a) in enumerate(items):
        op = " open" if i == 0 else ""
        out.append(f'            <details{op}>\n              <summary>{q}</summary>\n              <p>{a}</p>\n            </details>')
    return "\n".join(out)


def offer_cards(items):
    return "\n".join(
        f'            <article class="lux-service">\n              {ico(n)}\n              <h3>{t}</h3>\n              <p>{p}</p>\n            </article>'
        for n, t, p in items
    )


def audience_cards(items):
    return "\n".join(
        f'          <article>\n            {ico(n)}\n            <h3>{t}</h3>\n            <p>{p}</p>\n          </article>'
        for n, t, p in items
    )


def steps_html(items):
    return "\n".join(
        f'            <article class="lux-step">\n              {ico(n)}\n              <h3>{t}</h3>\n              <p>{p}</p>\n            </article>'
        for n, t, p in items
    )


INDUSTRIES = [
    {
        "file": "fintech.html", "slug": "fintech", "name": "Fintech",
        "title": "Fintech Software Development in Delhi NCR | BlueByte",
        "description": "BlueByte builds fintech software in Delhi NCR: digital banking, payments, wallets and compliance-aware platforms with security designed in.",
        "kicker": "Finance",
        "h1": "Fintech software that treats trust as a feature.",
        "lead": "BlueByte designs financial products for banks, lenders and fintech startups in Delhi NCR. Secure workflows, clear audit trails and interfaces people will actually complete.",
        "define_h2": "What is fintech software development?",
        "define": "Fintech software development is the design of digital money products: onboarding, payments, ledgers, reporting and the controls a regulated firm needs. BlueByte builds these systems for Delhi NCR teams that cannot afford a pretty app with a leaky back end.",
        "intro": "From digital banking and payment gateways to wealth tools and RegTech, we combine compliance-aware architecture with calm UX so customers finish the journey and operations can explain every rupee.",
        "image": "images/fintech-slide.webp",
        "image_alt": "Digital banking and payments product interface",
        "audiences": [
            ("building", "Licensed institutions", "Core journeys, portals and integrations that sit beside what you already run."),
            ("rocket", "Fintech startups", "An MVP that can open an account, move money and leave an audit trail."),
            ("lock", "Risk and ops leaders", "Logs, roles and reports that stand up in a review, not only in a demo."),
        ],
        "offers": [
            ("monitor", "Digital banking journeys", "Onboarding, accounts and servicing that stay readable on a phone."),
            ("bag", "Payments and wallets", "Gateway integrations, reconciliation and failure paths that make sense."),
            ("shield", "RegTech and compliance", "Checks, evidence and workflows your compliance team can own."),
            ("chart", "Wealth and reporting", "Portfolios, statements and the numbers finance will sign."),
            ("lock", "Security by design", "Identity, encryption and monitoring treated as product work."),
            ("cloud", "Cloud platforms", "Environments you can recreate, with cost and access you can see."),
        ],
        "faqs": [
            ("Do you build fintech software in Delhi NCR?", "Yes. We design and engineer digital banking, payments, wallets and related platforms for teams in Delhi, Noida, Gurugram and across India."),
            ("Can you work with our compliance requirements?", "We design for audit trails, roles and evidence. Your counsel remains the authority on licence and policy."),
            ("Do you integrate existing payment gateways?", "Yes. We connect the gateways and ledgers you already use rather than inventing a parallel stack."),
            ("Will the product work on mobile?", "Customer journeys are designed for phones first. Internal tools follow the desks that use them."),
            ("How do you handle security?", "Access control, encryption, logging and reviews are part of the build, not a late patch."),
        ],
        "services": [("software-development.html", "Software"), ("cloud-devops.html", "Cloud"), ("quality-engineering.html", "Quality")],
    },
    {
        "file": "education.html", "slug": "education", "name": "Education",
        "title": "Education Software and EdTech Development | BlueByte",
        "description": "BlueByte builds education software in Delhi NCR: learning platforms, school portals and tools for classes, homework and student engagement.",
        "kicker": "Education",
        "h1": "Education software that stays simple for teachers.",
        "lead": "BlueByte designs learning platforms and school systems that teachers will open on a Monday morning, not only in a pitch.",
        "define_h2": "What is education technology development?",
        "define": "Education technology development is software for teaching, enrolment, content and assessment. BlueByte builds these products for schools, coaching firms and EdTech startups in Delhi NCR, with access, privacy and slow networks in mind.",
        "intro": "We design class tools, parent portals and content systems that reduce admin rather than adding another login. If a teacher needs a handbook to take attendance, we failed.",
        "image": "images/education-slide.webp",
        "image_alt": "Students and teachers using a digital learning platform",
        "audiences": [
            ("users", "Schools and colleges", "Portals for enrolment, timetable, fees and parent updates."),
            ("rocket", "EdTech product teams", "A learning product with a clear first lesson, not a feature pile."),
            ("pen", "Publishers and institutes", "Content systems that authors can update without engineering."),
        ],
        "offers": [
            ("monitor", "Learning platforms", "Courses, progress and assessments that work on modest phones."),
            ("users", "School administration", "Admissions, fees, attendance and the reports the office already runs."),
            ("file", "Content and CMS", "Lessons and resources editors can publish before the next period."),
            ("mail", "Parent communication", "Notices and progress without a separate app nobody installs."),
            ("chart", "Progress analytics", "Simple views of who is stuck, not a dashboard of vanity metrics."),
            ("lock", "Access and privacy", "Roles for staff, students and parents, with data handled carefully."),
        ],
        "faqs": [
            ("Do you build education software in India?", "Yes. Learning platforms, school portals and content tools for institutes and EdTech teams, with the studio in Delhi NCR."),
            ("Will it work on low-cost phones?", "That is a design constraint, not a later optimisation. We test on mid-range Android."),
            ("Can teachers update content themselves?", "Yes, when we include a CMS. Training is part of delivery."),
            ("Do you integrate existing SIS or fee tools?", "We connect the systems you already pay for wherever they offer a sane API."),
            ("How do you think about student data?", "Least privilege, clear roles and no surprise sharing. Policy still sits with you."),
        ],
        "services": [("web-development.html", "Web"), ("content-management-system.html", "CMS"), ("product-engineer.html", "Product")],
    },
    {
        "file": "automotive.html", "slug": "automotive", "name": "Automotive",
        "title": "Automotive Software Development in Delhi NCR | BlueByte",
        "description": "BlueByte builds automotive software for dealers, fleets and workshops in Delhi NCR: booking, inventory, driver apps and service operations.",
        "kicker": "Mobility",
        "h1": "Automotive software for the people who keep vehicles moving.",
        "lead": "BlueByte designs tools for dealers, fleets and workshops: bookings, parts, drivers and service, without a cockpit of unused charts.",
        "define_h2": "What is automotive software development?",
        "define": "Automotive software here means the digital layer around selling, servicing and running vehicles. BlueByte builds dealer sites, fleet tools and workshop systems for Delhi NCR operators who need fewer spreadsheets, not another unused portal.",
        "intro": "From service bookings to parts and driver apps, we model the real yard: late arrivals, missing parts, and the WhatsApp group that currently runs the day.",
        "image": "images/automotive-slide.webp",
        "image_alt": "Workshop and fleet operations software on a tablet",
        "audiences": [
            ("building", "Dealers and OEMs", "Inventory, leads and service booking on one calm site."),
            ("map", "Fleet operators", "Vehicle, driver and trip data on a screen a dispatcher will use."),
            ("check", "Workshops", "Job cards, parts and customer updates without carbon copies."),
        ],
        "offers": [
            ("monitor", "Dealer websites and CRM", "Stock, enquiries and follow-up that sales will actually update."),
            ("map", "Fleet operations", "Vehicles, routes and exceptions in one place."),
            ("check", "Service and workshop", "Bookings, job status and parts, visible to the bay and the customer."),
            ("cpu", "Integrations", "DMS, telematics and accounting connected instead of retyped."),
            ("monitor", "Driver and customer apps", "Simple tasks, offline-tolerant where the yard has poor signal."),
            ("chart", "Operations reporting", "Turnaround, utilisation and the numbers a GM already asks for."),
        ],
        "faqs": [
            ("Do you build automotive software in Delhi NCR?", "Yes. Dealer, fleet and workshop systems for operators in Delhi and across India."),
            ("Can you connect our existing DMS?", "If it has an API or a sane export, we integrate. If not, we will say so before promising a live sync."),
            ("Will workshop staff use it?", "We design for the bay, not only the boardroom. Training happens on the floor."),
            ("Do you build customer-facing booking sites?", "Yes. Service booking and stock search that work on a phone."),
            ("How long does a first release take?", "A focused booking or inventory slice can ship in weeks. Wider operations follow a dated plan."),
        ],
        "services": [("software-development.html", "Software"), ("web-development.html", "Web"), ("product-engineer.html", "Product")],
    },
    {
        "file": "real-estate.html", "slug": "real-estate", "name": "Real estate",
        "title": "Real Estate Website and Software Development | BlueByte",
        "description": "BlueByte builds real estate websites and software in Delhi NCR: listings, lead capture, CRM and property sites that help buyers enquire without friction.",
        "kicker": "Property",
        "h1": "Real estate sites that help people enquire, not bounce.",
        "lead": "BlueByte designs listing platforms, developer sites and sales tools for Delhi NCR property teams. Fast galleries, honest filters and leads that reach a human.",
        "define_h2": "What does real estate web development include?",
        "define": "Real estate web development covers property listing, search, enquiry and the CRM behind it. BlueByte builds these products for developers, brokers and asset managers in Delhi NCR so a buyer can find a unit on a phone and a sales desk can follow up the same day.",
        "intro": "We have shipped live property sites including Eshal Home Builders and Atharva Realty. The work is practical: media that loads, filters that match how people search, and enquiries that do not disappear into a shared inbox.",
        "image": "images/vip-villa.webp",
        "image_alt": "Property listing website showing residential projects",
        "audiences": [
            ("building", "Developers", "Project sites with typical units, availability and a path to book a visit."),
            ("users", "Brokers and agencies", "Listings, capture and follow-up without a dozen WhatsApp forwards."),
            ("search", "Marketing teams", "Pages that can rank for localities and project names, with speed intact."),
        ],
        "offers": [
            ("monitor", "Listing platforms", "Search, filters, maps and PDPs that hold on a mid-range phone."),
            ("mail", "Lead capture and CRM", "Enquiries routed, tagged and visible to the desk that must call."),
            ("pen", "Project microsites", "One project, one story, one clear call to visit."),
            ("cpu", "Virtual tours", "Embeds that do not wreck page speed."),
            ("chart", "Campaign landing pages", "Locality and offer pages marketing can launch without a ticket."),
            ("search", "SEO for property search", "Clean URLs, schema and content that name the place and the product."),
        ],
        "faqs": [
            ("Do you build real estate websites in Delhi NCR?", "Yes. Developer sites, listing platforms and lead systems for property teams in Delhi, Noida, Gurugram and beyond."),
            ("Can you migrate our current listings?", "Yes. We move inventory, media and redirects so search traffic is not thrown away."),
            ("Will sales get leads in real time?", "That is the point. We connect forms to the CRM or inbox the desk already lives in."),
            ("Do you work with channel partners?", "We can add partner logins and inventories when the process is clear."),
            ("Have you shipped live property sites?", "Yes. See Eshal Home Builders and Atharva Realty in our portfolio."),
        ],
        "services": [("web-development.html", "Web"), ("digital-marketing.html", "SEO"), ("content-management-system.html", "CMS")],
    },
    {
        "file": "agriculture.html", "slug": "agriculture", "name": "Agriculture",
        "title": "Agriculture Software and AgriTech Development | BlueByte",
        "description": "BlueByte builds agriculture software in Delhi NCR: farm operations, traceability, marketplace and data tools that work with patchy connectivity.",
        "kicker": "AgriTech",
        "h1": "Agriculture software that survives the field.",
        "lead": "BlueByte designs AgriTech for operators who work with weather, labour and weak signal, not only a laptop in Gurugram.",
        "define_h2": "What is agriculture software development?",
        "define": "Agriculture software covers farm operations, input tracking, traceability and the markets around food. BlueByte builds these tools so field staff can capture data offline and managers can see yield, waste and cost without a weekly spreadsheet merge.",
        "intro": "We design for patchy networks, mixed literacy and the seasonality of the work. If it only works on office Wi-Fi, it is not farm software.",
        "image": "images/agriculture-slide.webp",
        "image_alt": "Farm operations dashboard and field data capture",
        "audiences": [
            ("map", "Farms and FPOs", "Plots, inputs, labour and harvest in one place."),
            ("bag", "Agri marketplaces", "Catalogue, orders and quality notes that match how trade actually happens."),
            ("chart", "Food processors", "Traceability from lot to dispatch, with the documents a buyer asks for."),
        ],
        "offers": [
            ("map", "Farm operations", "Plots, tasks and inputs that a supervisor can update in the field."),
            ("chart", "Yield and waste", "Simple measures that change a decision, not a wall of charts."),
            ("bag", "Marketplaces", "Listings, orders and settlements for produce and inputs."),
            ("db", "Traceability", "Lots, tests and dispatch history a buyer can follow."),
            ("cpu", "Data capture", "Offline-tolerant forms, photos and sync when signal returns."),
            ("cloud", "Integrations", "ERP, weighing and logistics tools connected where they exist."),
        ],
        "faqs": [
            ("Do you build AgriTech in India?", "Yes. Farm, marketplace and traceability software, with the studio in Delhi NCR."),
            ("Will it work without reliable internet?", "We design capture to queue and sync. Dashboards can wait for a connection."),
            ("Can field staff use it in local languages?", "When the brief needs it. We plan copy and UI for the people who tap the screen."),
            ("Do you connect weighing or ERP systems?", "Where APIs or files exist, we integrate rather than retyping."),
            ("Who is this not for?", "A slide-ware demo with no operator behind it. We need a real workflow to design against."),
        ],
        "services": [("software-development.html", "Software"), ("data-science.html", "Data"), ("product-engineer.html", "Product")],
    },
    {
        "file": "health-pharma.html", "slug": "health-pharma", "name": "Health and pharma",
        "title": "Healthcare and Pharma Software Development | BlueByte",
        "description": "BlueByte builds healthcare and pharma software in Delhi NCR: clinic systems, patient apps and careful handling of records, appointments and operations.",
        "kicker": "Health",
        "h1": "Health software that is careful with people and records.",
        "lead": "BlueByte designs clinic, pharmacy and patient products with privacy, appointments and operations in the same brief.",
        "define_h2": "What is healthcare software development?",
        "define": "Healthcare software development is the design of systems around care, records and pharmacy operations. BlueByte builds appointment tools, patient apps and internal systems for Delhi NCR providers who need fewer paper files and no drama around access.",
        "intro": "We treat records as sensitive by default: roles, audit trails and the minimum data for the job. Clinical policy remains yours. Our job is software that does not make care harder.",
        "image": "images/health-pharma-slide.webp",
        "image_alt": "Clinic appointment and records software interface",
        "audiences": [
            ("heart", "Clinics and hospitals", "Appointments, records and billing without a second paper register."),
            ("bag", "Pharmacies", "Stock, prescriptions and fulfilment that match the counter."),
            ("users", "Digital health products", "Patient apps with a clear first task and honest consent."),
        ],
        "offers": [
            ("check", "Appointments and OPD", "Booking, reminders and the queue the desk already runs."),
            ("file", "Records and access", "Roles, audit trails and the least data required."),
            ("bag", "Pharmacy operations", "Stock, expiry and billing connected to the counter."),
            ("monitor", "Patient apps", "Results, visits and messages that do not require a tutorial."),
            ("lock", "Privacy defaults", "Encryption, access logs and no surprise sharing."),
            ("cloud", "Hosting you can explain", "Environments, backups and a restore you have drilled."),
        ],
        "faqs": [
            ("Do you build healthcare software in Delhi NCR?", "Yes. Clinic, pharmacy and patient products for providers and health startups."),
            ("Do you claim medical device certification?", "No. We build software. Regulatory status of a product remains your responsibility with counsel."),
            ("How do you handle patient data?", "Least privilege, encryption, logs. Hosting stays in an environment you control."),
            ("Can you integrate lab or pharmacy systems?", "Where interfaces exist, we connect them. We do not invent a parallel clinical record without a plan."),
            ("Will staff be trained?", "Yes. Delivery includes sessions with the people who will live in the system."),
        ],
        "services": [("software-development.html", "Software"), ("quality-engineering.html", "Quality"), ("cloud-devops.html", "Cloud")],
    },
    {
        "file": "retail-e-commerce.html", "slug": "retail-e-commerce", "name": "Retail and eCommerce",
        "title": "Retail and eCommerce Software Development | BlueByte",
        "description": "BlueByte builds retail and eCommerce software in Delhi NCR: storefronts, inventory and omnichannel operations that hold on sale days.",
        "kicker": "Retail",
        "h1": "Retail systems that sell in-store and online without two truths.",
        "lead": "BlueByte designs storefronts and operations for Delhi NCR retailers who need one inventory, one order story and a site that holds when a campaign lands.",
        "define_h2": "What is retail and eCommerce software?",
        "define": "Retail and eCommerce software covers the storefront plus inventory, orders and the desk that picks them. BlueByte builds Shopify, WooCommerce and custom stacks so a sale in the shop and a sale on the phone do not fight each other.",
        "intro": "We have shipped live commerce including Femora. The work is catalogue, checkout, stock and care after launch, not a theme with a plugin pile.",
        "image": "images/retail-slide.webp",
        "image_alt": "Retail eCommerce storefront and product catalogue",
        "audiences": [
            ("bag", "D2C brands", "A store that can take an order tonight and still look considered."),
            ("building", "Multi-store retailers", "Inventory and orders that match the shop floor."),
            ("zap", "Teams with campaign calendars", "Performance work before the ad spend, not after the site tips over."),
        ],
        "offers": [
            ("monitor", "Storefronts", "Shopify, WooCommerce or custom, with checkout that finishes."),
            ("db", "Inventory", "One stock number, visible to web and store."),
            ("mail", "Orders and service", "Status, returns and the inbox support already uses."),
            ("zap", "Sale-day speed", "Caching, images and a rehearsal under load."),
            ("search", "Findability", "Search, filters and SEO that name the product correctly."),
            ("cpu", "Integrations", "Payments, GST, warehouse and CRM connected."),
        ],
        "faqs": [
            ("Do you build eCommerce for Delhi NCR retailers?", "Yes. Storefronts, inventory and care plans for D2C and multi-store teams."),
            ("Shopify or WooCommerce?", "Whichever fits the catalogue and the people who will live in admin. We will say if custom is the better call."),
            ("Can you connect our warehouse?", "If they expose an API or files, we integrate rather than invent a second stock book."),
            ("Will the store hold on a flash sale?", "We test before you spend. That is part of go-live, not a hope."),
            ("See related work?", "Femora is live. More in the portfolio."),
        ],
        "services": [("ecommerce.html", "eCommerce"), ("digital-marketing.html", "SEO"), ("web-development.html", "Web")],
    },
    {
        "file": "media-entertainment.html", "slug": "media-entertainment", "name": "Media and entertainment",
        "title": "Media and Entertainment Software Development | BlueByte",
        "description": "BlueByte builds media and entertainment software in Delhi NCR: content sites, streaming-ready platforms and publishing tools editors can run.",
        "kicker": "Media",
        "h1": "Media platforms that publish on time and play without fuss.",
        "lead": "BlueByte designs content sites, catalogues and publishing tools for Delhi NCR media teams who cannot wait on engineering for every headline.",
        "define_h2": "What is media software development?",
        "define": "Media software covers publishing, catalogues, video delivery and the CMS behind them. BlueByte builds these products so editors can ship, audiences can play, and the stack does not melt when a story spikes.",
        "intro": "We care about preview, roles, CDN-friendly media and pages that stay fast with large images. Drama belongs on screen, not in deploy.",
        "image": "images/media-slide.webp",
        "image_alt": "Media publishing and video content platform",
        "audiences": [
            ("pen", "Publishers", "A CMS with preview, roles and URLs that SEO can live with."),
            ("monitor", "Streaming and VOD teams", "Catalogues, players and the metadata a viewer needs to start."),
            ("users", "Studios and labels", "Portfolios and campaign sites that load, even with heavy stills."),
        ],
        "offers": [
            ("file", "Publishing CMS", "Schedules, previews and roles that match the newsroom."),
            ("monitor", "Catalogues and players", "Metadata, playback and pages that do not block on a 12MB hero."),
            ("search", "Discoverability", "Internal search and public SEO for titles and talent."),
            ("zap", "Spike traffic", "Caching and CDN patterns before a release drops."),
            ("users", "Membership", "Accounts, entitlements and the boring billing around them."),
            ("layout", "Campaign sites", "Time-boxed microsites marketing can launch without a rewrite."),
        ],
        "faqs": [
            ("Do you build media platforms in Delhi NCR?", "Yes. Publishing, catalogues and campaign sites for media and entertainment teams."),
            ("Can editors publish without developers?", "That is the test of the CMS. Training is included."),
            ("Do you build streaming infrastructure from scratch?", "We integrate proven delivery and players. We do not pretend to be a CDN."),
            ("Will pages stay fast with video and stills?", "Image policy, lazy loading and a CDN. Heavy art is planned, not dumped."),
            ("Can you migrate a WordPress newsroom?", "Yes, including redirects so old URLs keep working."),
        ],
        "services": [("content-management-system.html", "CMS"), ("web-development.html", "Web"), ("cloud-devops.html", "Cloud")],
    },
    {
        "file": "manufacturing-logistics.html", "slug": "manufacturing-logistics", "name": "Manufacturing and logistics",
        "title": "Manufacturing and Logistics Software | BlueByte",
        "description": "BlueByte builds manufacturing and logistics software in Delhi NCR: inventory, dispatch, tracking and plant tools on a single, calm screen.",
        "kicker": "Operations",
        "h1": "Manufacturing and logistics software on one calm screen.",
        "lead": "BlueByte designs inventory, dispatch and plant tools for Delhi NCR operators who are tired of three systems and a whiteboard.",
        "define_h2": "What is manufacturing and logistics software?",
        "define": "This is software for stock, machines, trucks and the people who move them. BlueByte builds operations tools so a supervisor can see what is late, what is missing and what left the gate, without exporting to Excel first.",
        "intro": "We start on the floor: job cards, weighbridges, drivers. Then we connect ERP where it helps. If a forklift operator needs a training course to tap a status, we redesign.",
        "image": "images/logistics-slide.webp",
        "image_alt": "Logistics tracking and warehouse operations dashboard",
        "audiences": [
            ("building", "Plants", "Job status, downtime and the materials the line is waiting on."),
            ("map", "Fleet and 3PL", "Vehicles, consignments and exceptions a dispatcher can act on."),
            ("db", "Warehouse teams", "Locations, picks and the counts that finance will argue about."),
        ],
        "offers": [
            ("db", "Inventory", "Locations, lots and counts that match the rack."),
            ("map", "Dispatch and tracking", "Consignments, ETAs and the exception list."),
            ("cpu", "Plant operations", "Jobs, downtime and the reasons the line stopped."),
            ("check", "Quality checks", "Simple captures at the bay, not a form designed in an office."),
            ("chart", "Operations reporting", "Fill rate, turnaround and the few numbers a GM wants."),
            ("cloud", "Integrations", "ERP, weighing and telematics connected where they exist."),
        ],
        "faqs": [
            ("Do you build logistics software in Delhi NCR?", "Yes. Inventory, dispatch and plant tools for manufacturers and 3PLs."),
            ("Can you replace our ERP?", "Usually no, and we will say so. We sit beside ERP and remove the spreadsheets around it."),
            ("Will warehouse staff use it?", "We design for the floor, with large targets and short flows. Training happens there."),
            ("Do you support GPS tracking?", "We integrate providers you already have rather than selling a tracker."),
            ("How do you go live without stopping the plant?", "Slices. One process at a time, with the old path available until the new one is trusted."),
        ],
        "services": [("software-development.html", "Software"), ("data-science.html", "Data"), ("cloud-devops.html", "Cloud")],
    },
]


BLOGS = [
    ("mcp-enterprise-integrations-2026.html", "MCP Enterprise Integrations: A Security-First Guide", "26 September 2026", "images/blog-mcp-enterprise-2026.webp", "How to plan safe enterprise AI tool integrations with clear permissions."),
    ("rag-enterprise-ai-search-2026.html", "RAG for Enterprise AI Search: A Practical Build Guide", "26 September 2026", "images/blog-rag-enterprise-search-2026.webp", "Prepare documents, preserve access rules and measure search quality."),
    ("llm-testing-quality-engineering-2026.html", "LLM Testing and Quality Engineering: A 2026 Guide", "26 September 2026", "images/blog-llm-quality-engineering-2026.webp", "Evaluate responses, build test sets and use release gates for production AI."),
    ("genai-cloud-operations-2026.html", "Generative AI Cloud Operations: Cost and Reliability", "26 September 2026", "images/blog-genai-cloud-operations-2026.webp", "Keep generative workloads reliable without surprising the finance team."),
    ("a2a-agent-interoperability-2026.html", "A2A Protocol in 2026: A Practical Integration Guide", "26 September 2026", "images/blog-a2a-agent-interoperability-2026.webp", "Plan multi-agent interoperability without losing control of identity."),
    ("agentic-ai-autonomous-systems-it-service-providers.html", "Agentic AI and Autonomous Systems: A Practical Guide", "26 September 2026", "images/agentic-ai-operations.webp", "Where autonomous systems help IT service work, and where they should not."),
    ("best-technology-for-ecommerce-in-2026.html", "The best technology for eCommerce in 2026", "07 September 2025", "images/blog-ecommerce-stack.webp", "Platforms and tools that still earn their place in a store stack."),
    ("top-frontend-technologies-to-use-in-2026.html", "Frontend technologies to consider in 2026", "07 September 2025", "images/blog-frontend-techs.webp", "Frameworks and tools for speed, UX and search."),
    ("what-is-web-development-complete-beginner-guide-2026.html", "What is web development? A complete beginner guide (2026)", "26 August 2025", "images/blog-web-development-guide-2026.png", "How sites are built and a calm roadmap for beginners."),
    ("5-must-have-integrations-for-ecommerce-success.html", "5 must-have integrations for eCommerce success", "26 August 2025", "images/blog-4.webp", "The connections that keep orders moving behind a storefront."),
    ("future-proofing-legacy-apps.html", "Future-proofing legacy apps: composable architecture", "26 August 2025", "images/blog-2.webp", "How to modernise without a risky all-at-once rewrite."),
    ("the-ultimate-guide-to-healthcare-app-development-cost.html", "Healthcare app development cost: key factors", "26 August 2025", "images/blog-3.webp", "What actually moves the cost of a healthcare app."),
]


WORK = [
    ("Eshal Home Builders", "Real estate", "images/eshalHome.jpg", "https://www.eshalhomebuilders.com/", "A property site for a Delhi developer: projects, enquiries and a path to visit."),
    ("Atharva Realty", "Real estate", "images/august-villa.jpg", "https://www.atharvarealty.com/", "Listings and campaign pages for a realty brand that needed to look considered and load quickly."),
    ("Femora", "eCommerce", "images/femora.jpg", "https://www.femora.in/", "A kitchenware storefront built to sell, with catalogue and checkout the team can run."),
    ("Audit Vantage Solutions", "Professional services", "images/auditVantageSolutions.jpg", "https://auditvantagesolutions.com/", "A services site that explains the offer without a brochure PDF as the homepage."),
    ("Studio Rigu", "Brand", "images/studio-rigu.jpg", "https://www.studiorigu.com/", "A studio presence with stills that stay fast and a contact path that is hard to miss."),
    ("AutoKame", "Automotive", "images/autokame.jpg", "https://autokame.co.in/", "An automotive brand site for people comparing vehicles on a phone."),
]


def industry_html(page: dict) -> str:
    extras = [
        {
            "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in page["faqs"]],
        }
    ]
    schema = webpage_schema(page["slug"], page["title"], page["description"], page["image"], extras)
    intro = page["intro"]
    related = "\n".join(f'            <a class="lux-chip" href="{h}">{l} <span aria-hidden="true">→</span></a>' for h, l in page["services"])
    others = [i for i in INDUSTRIES if i["file"] != page["file"]][:4]
    pills = "\n".join(f'            <a href="{i["file"]}">{i["name"]}</a>' for i in others)
    body = f"""{HEADER}
    <main id="main" class="lux-main">
      <article>
      <section class="lux-hero lux-hero--page" aria-labelledby="ind-hero">
        <div class="lux-hero-inner">
          <nav class="lux-crumb" aria-label="Breadcrumb">
            <a href="/">Home</a>
            <span aria-hidden="true">/</span>
            <span>Industries</span>
            <span aria-hidden="true">/</span>
            <span aria-current="page">{page["name"]}</span>
          </nav>
          <p class="lux-kicker lux-rise">{page["kicker"]} · Delhi NCR</p>
          <h1 id="ind-hero" data-split>{page["h1"]}</h1>
          <p class="lux-lead lux-rise lux-rise-2">{page["lead"]}</p>
          <div class="lux-actions lux-rise lux-rise-3">
            <a class="lux-btn lux-btn-gold" href="contact.html">Request a proposal</a>
            <a class="lux-btn lux-btn-ghost" href="portfolio.html">See related work</a>
          </div>
        </div>
      </section>
      <section class="lux-section lux-theme-light" data-reveal>
        <div class="lux-wrap lux-about-grid">
          <figure class="lux-frame">
            <img src="{page["image"]}" alt="{page["image_alt"]}" width="560" height="700" loading="eager" decoding="async">
          </figure>
          <div>
            <p class="lux-kicker">Definition</p>
            <h2 class="lux-title">{page["define_h2"]}</h2>
            <div class="lux-prose">
              <p>{page["define"]}</p>
              <p>{intro}</p>
            </div>
          </div>
        </div>
      </section>
      <section class="lux-section lux-theme-light lux-tight" data-reveal>
        <div class="lux-wrap">
          <p class="lux-kicker">Fit</p>
          <h2 class="lux-title" data-split>Who this is for.</h2>
          <div class="lux-audience">
{audience_cards(page["audiences"])}
          </div>
        </div>
      </section>
      <section class="lux-section lux-theme-dark" data-reveal>
        <div class="lux-wrap">
          <p class="lux-kicker">Capabilities</p>
          <h2 class="lux-title" data-split>What we build in {page["name"].lower()}.</h2>
          <div class="lux-service-grid">
{offer_cards(page["offers"])}
          </div>
        </div>
      </section>
      <section class="lux-section lux-theme-light" data-reveal>
        <div class="lux-wrap">
          <p class="lux-kicker">Method</p>
          <h2 class="lux-title" data-split>How an industry engagement runs.</h2>
          <div class="lux-steps">
{steps_html([
    ("compass", "Learn the grain", "The process, the jargon and the constraint you cannot drop."),
    ("pen", "Shape a slice", "The smallest release that would change a week on the floor."),
    ("code", "Build in the open", "Demos you can click, with the integrations named."),
    ("shield", "Hand over and watch", "Training, care and a path for the next slice."),
])}
          </div>
        </div>
      </section>
      <section class="lux-section lux-theme-dark" data-reveal>
        <div class="lux-wrap">
          <p class="lux-kicker">Also</p>
          <h2 class="lux-title">Related industries and services.</h2>
          <div class="lux-pills">{pills}
          </div>
          <div class="lux-related">
{related}
          </div>
        </div>
      </section>
      <section class="lux-section lux-theme-dark" data-reveal>
        <div class="lux-wrap">
          <p class="lux-kicker">Questions</p>
          <h2 class="lux-title" data-split>Answers people search for.</h2>
          <div class="lux-faq-list">
{faqs_html(page["faqs"])}
          </div>
        </div>
      </section>
      <section class="lux-section lux-cta lux-theme-dark" data-reveal>
        <div class="lux-wrap lux-cta-inner">
          <p class="lux-kicker">Begin</p>
          <h2 class="lux-title" data-split>Building in {page["name"].lower()}?</h2>
          <p class="lux-lead">Send the brief. We will answer with a next step, not a generic deck.</p>
          <div class="lux-actions">
            <a class="lux-btn lux-btn-gold" href="contact.html">Let's connect</a>
            <a class="lux-btn lux-btn-ghost" href="https://wa.me/918178838292" target="_blank" rel="noopener noreferrer">WhatsApp us</a>
          </div>
        </div>
      </section>
      </article>
    </main>
{FOOTER}"""
    return head(page["title"], page["description"], page["slug"], page["image"], schema, page["name"].lower() + " software Delhi NCR") + body


def write(name: str, html: str) -> None:
    html = clean_dashes(html)
    if "\u2014" in html or "\u2013" in html:
        raise SystemExit("dash in " + name)
    if html.count("<h1") != 1:
        raise SystemExit("h1 in " + name)
    json.loads(html.split('<script type="application/ld+json">', 1)[1].split("</script>", 1)[0].replace("{{SITE_URL}}", "https://example.com"))
    (ROOT / name).write_text(html, encoding="utf-8")
    print("wrote", name, html.count("\n"))


def gen_about():
    title = "About BlueByte IT Solutions | Software Team in Delhi NCR"
    desc = "BlueByte is a Delhi NCR software studio. We design custom software, websites, mobile products and cloud work with senior people on the brief."
    faqs = [
        ("Where is BlueByte based?", "The studio is in Uttam Nagar, New Delhi. We work with teams across Delhi NCR and the rest of India."),
        ("What does BlueByte actually do?", "Custom software, web and mobile products, eCommerce, cloud, CMS, data and quality engineering. See Services for the list."),
        ("Do you only work with large companies?", "No. Startups get a tight first slice. Larger organisations get architecture and care. The standard of craft is the same."),
        ("How do we start?", "Send a brief via the contact form or WhatsApp. We reply with questions or a scoped next step."),
    ]
    extra = [{"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}]
    schema = webpage_schema("about", title, desc, "images/about-1.webp", extra)
    html = head(title, desc, "about", "images/about-1.webp", schema, "IT company Delhi NCR, software studio Delhi") + f"""{HEADER}
    <main id="main" class="lux-main">
      <article>
      <section class="lux-hero lux-hero--page" aria-labelledby="about-hero">
        <div class="lux-hero-inner">
          <nav class="lux-crumb" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><span aria-current="page">About</span></nav>
          <p class="lux-kicker lux-rise">The studio</p>
          <h1 id="about-hero" data-split>A Delhi NCR software studio with a calm bias for shipping.</h1>
          <p class="lux-lead lux-rise lux-rise-2">BlueByte IT Solutions designs and builds digital products for businesses that are tired of decoration. Senior people on the work. Clear artefacts. Software that still looks considered a year later.</p>
          <div class="lux-actions lux-rise lux-rise-3">
            <a class="lux-btn lux-btn-gold" href="contact.html">Start a brief</a>
            <a class="lux-btn lux-btn-ghost" href="portfolio.html">Selected work</a>
          </div>
        </div>
      </section>
      <section class="lux-section lux-theme-light" data-reveal>
        <div class="lux-wrap lux-about-grid">
          <figure class="lux-frame"><img src="images/about-1.webp" alt="BlueByte team at work in Delhi" width="560" height="700" decoding="async"></figure>
          <div>
            <p class="lux-kicker">Who we are</p>
            <h2 class="lux-title">A technology partner, not a slide factory.</h2>
            <div class="lux-prose">
              <p>BlueByte is an IT company in Delhi NCR. We write custom software, websites, mobile apps and the cloud work that keeps them quiet in production. Clients are startups and established firms who want a team that answers the brief.</p>
              <p>We are not the cheapest shop in the city, and we do not pretend to be a thousand-person factory. You get a small senior group, visible progress and documentation a new hire can enter.</p>
              <p>The studio sits in Uttam Nagar, New Delhi. Delivery is India-wide. English is the working language. Hindi is available when the product needs it.</p>
            </div>
          </div>
        </div>
      </section>
      <section class="lux-section lux-theme-light lux-tight" data-reveal>
        <div class="lux-wrap">
          <p class="lux-kicker">Mission</p>
          <h2 class="lux-title" data-split>Ship software people can defend.</h2>
          <p class="lux-lead">Fewer meetings. Clearer artefacts. A product that converts, holds and can be explained to finance.</p>
          <div class="lux-audience">
            <article>{ico("compass")}<h3>Listen first</h3><p>Users, revenue and constraints before a colour palette.</p></article>
            <article>{ico("pen")}<h3>Craft in the open</h3><p>Readable code, tests and a staging URL stakeholders can click.</p></article>
            <article>{ico("shield")}<h3>Stay after launch</h3><p>Care, performance and SEO so the thing keeps earning.</p></article>
          </div>
        </div>
      </section>
      <section class="lux-section lux-theme-dark" data-reveal>
        <div class="lux-wrap">
          <p class="lux-kicker">Questions</p>
          <h2 class="lux-title">Straightforward answers.</h2>
          <div class="lux-faq-list">{faqs_html(faqs)}</div>
        </div>
      </section>
      <section class="lux-section lux-cta lux-theme-dark" data-reveal>
        <div class="lux-wrap lux-cta-inner">
          <p class="lux-kicker">Begin</p>
          <h2 class="lux-title" data-split>Want to know if we fit?</h2>
          <p class="lux-lead">Send two paragraphs. We will tell you honestly if we are the right studio.</p>
          <div class="lux-actions">
            <a class="lux-btn lux-btn-gold" href="contact.html">Let's connect</a>
            <a class="lux-btn lux-btn-ghost" href="https://wa.me/918178838292" target="_blank" rel="noopener noreferrer">WhatsApp us</a>
          </div>
        </div>
      </section>
      </article>
    </main>
{FOOTER}"""
    write("about.html", html)


def gen_contact():
    title = "Contact BlueByte IT Solutions | Delhi NCR Software Team"
    desc = "Contact BlueByte in Delhi NCR about custom software, websites, mobile apps or cloud work. Phone, email, WhatsApp or the form. Studio in Uttam Nagar."
    extra = [{
        "@type": "ContactPage",
        "@id": "{{SITE_URL}}/contact#contactpage",
        "url": "{{SITE_URL}}/contact",
        "name": title,
        "description": desc,
    }]
    schema = webpage_schema("contact", title, desc, "images/contact.webp", extra)
    html = head(title, desc, "contact", "images/contact.webp", schema, "contact BlueByte Delhi, software company Uttam Nagar") + f"""{HEADER}
    <main id="main" class="lux-main">
      <section class="lux-hero lux-hero--page" aria-labelledby="contact-hero">
        <div class="lux-hero-inner">
          <nav class="lux-crumb" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><span aria-current="page">Contact</span></nav>
          <p class="lux-kicker lux-rise">Delhi NCR</p>
          <h1 id="contact-hero" data-split>Tell us what you are building.</h1>
          <p class="lux-lead lux-rise lux-rise-2">A short brief is enough. We reply with questions or a scoped next step, not a 40-page deck.</p>
        </div>
      </section>
      <section class="lux-section lux-theme-light" data-reveal>
        <div class="lux-wrap lux-split">
          <div>
            <p class="lux-kicker">Studio</p>
            <h2 class="lux-title">Write, call or visit.</h2>
            <div class="lux-prose">
              <p><strong>Phone.</strong> <a href="tel:+918178838292">+91 81788 38292</a></p>
              <p><strong>Email.</strong> <a href="mailto:info@bluebyteitsolutions.com">info@bluebyteitsolutions.com</a></p>
              <p><strong>WhatsApp.</strong> <a href="https://wa.me/918178838292" rel="noopener noreferrer" target="_blank">Message the studio</a></p>
              <p><strong>Address.</strong> MS 83, Mohan Garden, Uttam Nagar, New Delhi 110059, India.</p>
            </div>
          </div>
          <div>
            <h2 class="lux-title" style="font-size:1.5rem">Send a brief</h2>
            <form class="lux-form" method="post" action="/api/contact">
              <div class="lux-honeypot" aria-hidden="true">
                <label for="website">Leave this field empty</label>
                <input type="text" id="website" name="website" tabindex="-1" autocomplete="off">
              </div>
              <div class="lux-form-row">
                <div>
                  <label for="firstName">First name</label>
                  <input class="form-control form-control-lg" id="firstName" name="firstName" required>
                </div>
                <div>
                  <label for="lastName">Last name</label>
                  <input class="form-control form-control-lg" id="lastName" name="lastName" required>
                </div>
              </div>
              <div>
                <label for="email">Email</label>
                <input class="form-control form-control-lg" id="email" name="email" type="email" required>
              </div>
              <div>
                <label for="phone">Phone</label>
                <input class="form-control form-control-lg" id="phone" name="phone" type="tel">
              </div>
              <div>
                <label for="message">How can we help?</label>
                <textarea class="form-control form-control-lg" id="message" name="message" rows="5" required></textarea>
              </div>
              <button class="lux-btn lux-btn-ink" type="submit" name="submit">Send message</button>
              <div id="formResult"></div>
            </form>
            <script>
              (function () {{
                var box = document.getElementById('formResult');
                if (!box) return;
                var params = new URLSearchParams(window.location.search);
                if (params.get('sent') === '1') {{
                  box.innerHTML = '<div class="alert alert-success" role="alert">Thank you. Your message has been sent. We will reply shortly.</div>';
                }} else if (params.get('error') === '1') {{
                  box.innerHTML = '<div class="alert alert-danger" role="alert">We could not send that just now. Try again, or email <a href="mailto:info@bluebyteitsolutions.com">info@bluebyteitsolutions.com</a>.</div>';
                }}
              }})();
            </script>
          </div>
        </div>
      </section>
      <section class="lux-section lux-theme-light lux-tight" data-reveal>
        <div class="lux-wrap">
          <p class="lux-kicker">Map</p>
          <h2 class="lux-title">BlueByte IT Solutions, New Delhi</h2>
          <div class="lux-map">
            <iframe title="BlueByte IT Solutions on Google Maps" src="https://www.google.com/maps/embed?pb=!1m14!1m8!1m3!1d3502.026104965128!2d77.0335781!3d28.6289797!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x390d05713cbc05f9%3A0x29ec332097ea9861!2sBluebyte%20It%20Solutions%20%7C%20Best%20web%20development%20company%20in%20Delhi%20NCR!5e0!3m2!1sen!2sin!4v1768916285907!5m2!1sen!2sin" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>
          </div>
        </div>
      </section>
    </main>
{FOOTER}"""
    write("contact.html", html)


def gen_blogs():
    title = "Software, AI and Web Development Insights | BlueByte"
    desc = "Practical articles from BlueByte on software, web, eCommerce, cloud and AI, written for product and business teams in India."
    schema = webpage_schema("blogs", title, desc, "images/blog-4.webp")
    cards = []
    for href, t, date, img, ex in BLOGS:
        cards.append(f'''            <a class="lux-post" href="{href}">
              <img src="{img}" alt="" width="640" height="400" loading="lazy" decoding="async">
              <div class="lux-post-body">
                <time>{date}</time>
                <h3>{t}</h3>
                <p>{ex}</p>
              </div>
            </a>''')
    html = head(title, desc, "blogs", "images/blog-4.webp", schema, "BlueByte blog, software insights") + f"""{HEADER}
    <main id="main" class="lux-main">
      <section class="lux-hero lux-hero--page" aria-labelledby="blog-hero">
        <div class="lux-hero-inner">
          <nav class="lux-crumb" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><span aria-current="page">Journal</span></nav>
          <p class="lux-kicker lux-rise">Journal</p>
          <h1 id="blog-hero" data-split>Notes from the studio, not recycled slogans.</h1>
          <p class="lux-lead lux-rise lux-rise-2">Practical writing on web, commerce, cloud and AI for teams who have to ship.</p>
        </div>
      </section>
      <section class="lux-section lux-theme-light" data-reveal>
        <div class="lux-wrap">
          <div class="lux-posts">
{chr(10).join(cards)}
          </div>
        </div>
      </section>
    </main>
{FOOTER}"""
    write("blogs.html", html)


def gen_work(filename: str, slug: str, title: str, desc: str, h1: str, lead: str, kicker: str):
    schema = webpage_schema(slug, title, desc, WORK[0][2])
    cards = []
    for name, sector, img, url, blurb in WORK:
        cards.append(f'''            <a class="lux-work-card" href="{url}" rel="noopener noreferrer" target="_blank">
              <img src="{img}" alt="{name} website" width="800" height="560" loading="lazy" decoding="async">
              <div class="lux-work-copy">
                <span>{sector}</span>
                <h3>{name}</h3>
                <p class="mb-0">{blurb}</p>
              </div>
            </a>''')
    html = head(title, desc, slug, WORK[0][2], schema) + f"""{HEADER}
    <main id="main" class="lux-main">
      <section class="lux-hero lux-hero--page" aria-labelledby="work-hero">
        <div class="lux-hero-inner">
          <nav class="lux-crumb" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><span aria-current="page">{kicker}</span></nav>
          <p class="lux-kicker lux-rise">{kicker}</p>
          <h1 id="work-hero" data-split>{h1}</h1>
          <p class="lux-lead lux-rise lux-rise-2">{lead}</p>
          <div class="lux-actions lux-rise lux-rise-3">
            <a class="lux-btn lux-btn-gold" href="contact.html">Start a brief</a>
          </div>
        </div>
      </section>
      <section class="lux-section lux-theme-dark" data-reveal>
        <div class="lux-wrap">
          <div class="lux-work-grid-4">
{chr(10).join(cards)}
          </div>
        </div>
      </section>
    </main>
{FOOTER}"""
    write(filename, html)


def gen_404():
    title = "Page not found | BlueByte IT Solutions"
    desc = "This page does not exist. Return to BlueByte IT Solutions for software, web development and digital product work in Delhi NCR."
    schema = webpage_schema("404", title, desc, "images/og-image.webp")
    html = head(title, desc, "404", "images/og-image.webp", schema) + f"""{HEADER}
    <main id="main" class="lux-main">
      <section class="lux-hero lux-hero--page lux-404" aria-labelledby="err-hero">
        <div class="lux-hero-inner" style="text-align:center;margin-left:auto;margin-right:auto">
          <p class="lux-kicker lux-rise">404</p>
          <h1 id="err-hero" data-split>This page is not here.</h1>
          <p class="lux-lead lux-rise lux-rise-2">It may have moved, or the link is tired. The studio is still open.</p>
          <div class="lux-actions lux-rise lux-rise-3" style="justify-content:center">
            <a class="lux-btn lux-btn-gold" href="/">Back to home</a>
            <a class="lux-btn lux-btn-ghost" href="contact.html">Contact</a>
          </div>
        </div>
      </section>
    </main>
{FOOTER}"""
    # robots noindex for 404
    html = html.replace('content="index,follow"', 'content="noindex,follow"')
    write("404.html", html)


def wrap_blogs():
    for href, title, date, img, excerpt in BLOGS:
        src = ROOT / href
        if not src.exists():
            print("skip missing", href)
            continue
        raw = src.read_text(encoding="utf-8")
        m = re.search(r"<article[^>]*>([\s\S]*?)</article>", raw)
        if not m:
            print("no article", href)
            continue
        inner = m.group(1)
        inner = re.sub(r'class="[^"]*"', "", inner)
        inner = clean_dashes(inner)
        h1m = re.search(r"<h1[^>]*>(.*?)</h1>", raw, re.S)
        h1 = re.sub("<[^>]+>", "", h1m.group(1) if h1m else title)
        h1 = re.sub(r"\s+", " ", h1).strip()
        dm = re.search(r'name="description"[^>]*content="([^"]+)"', raw)
        if not dm:
            dm = re.search(r'<meta name="description"\s+content="([^"]+)"', raw)
        desc = dm.group(1) if dm else excerpt
        slug = href.replace(".html", "")
        tm = re.search(r"<title>(.*?)</title>", raw, re.S)
        page_title = re.sub("<[^>]+>", "", tm.group(1) if tm else title)
        page_title = re.sub(r"\s+", " ", page_title).strip()
        extra = [{
            "@type": "Article",
            "headline": h1,
            "datePublished": date,
            "description": desc,
            "author": {"@type": "Organization", "name": "BlueByte IT Solutions"},
            "publisher": {"@id": "{{SITE_URL}}/#organization"},
            "image": "{{SITE_URL}}/" + img,
            "mainEntityOfPage": "{{SITE_URL}}/" + slug,
        }]
        schema = webpage_schema(slug, page_title, desc, img, extra)
        html = head(page_title, desc, slug, img, schema, og_type="article") + f"""{HEADER}
    <main id="main" class="lux-main">
      <article>
      <section class="lux-hero lux-hero--page" aria-labelledby="post-hero">
        <div class="lux-hero-inner">
          <nav class="lux-crumb" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><a href="blogs.html">Journal</a><span aria-hidden="true">/</span><span aria-current="page">Article</span></nav>
          <p class="lux-kicker lux-rise">{date}</p>
          <h1 id="post-hero">{h1}</h1>
          <p class="lux-lead lux-rise lux-rise-2">{excerpt}</p>
        </div>
      </section>
      <section class="lux-section lux-theme-light">
        <div class="lux-wrap">
          <div class="lux-article">
            {inner}
          </div>
          <div class="lux-actions" style="margin-top:2.5rem">
            <a class="lux-btn lux-btn-ink" href="blogs.html">More articles</a>
            <a class="lux-btn lux-btn-gold" href="contact.html">Talk to the studio</a>
          </div>
        </div>
      </section>
      </article>
    </main>
{FOOTER}"""
        write(href, html)


def main() -> None:
    for page in INDUSTRIES:
        write(page["file"], industry_html(page))
    gen_about()
    gen_contact()
    gen_blogs()
    gen_work(
        "portfolio.html",
        "portfolio",
        "Software and Web Development Portfolio | BlueByte",
        "Selected BlueByte websites and digital products, with the craft behind each delivery.",
        "Selected work, on the live web.",
        "Property, commerce, services and mobility. Each built to look expensive and behave simply.",
        "Portfolio",
    )
    gen_work(
        "case-studies.html",
        "case-studies",
        "Client Case Studies | BlueByte IT Solutions",
        "BlueByte project stories: goals, approach and the digital products we shipped.",
        "Stories behind the work.",
        "Not a trophy wall. A short account of what we were asked to do, and what shipped.",
        "Case studies",
    )
    gen_404()
    wrap_blogs()


if __name__ == "__main__":
    main()
