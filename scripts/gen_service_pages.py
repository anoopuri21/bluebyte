#!/usr/bin/env python3
"""Generate cinematic, SEO/AEO service pages from shared chrome."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
HEADER = INDEX[INDEX.find('  <a class="lux-skip"') : INDEX.find("</header>") + len("</header>")]
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

PATHS = {
    "code": '<polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>',
    "monitor": '<rect x="3" y="4" width="18" height="14" rx="2"/><path d="M8 21h8M12 18v3"/>',
    "bag": '<path d="M6 7h15l-1.5 9h-12z"/><path d="M6 7 5 3H2"/><circle cx="9" cy="20" r="1"/><circle cx="18" cy="20" r="1"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3-3"/>',
    "layers": '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
    "cloud": '<path d="M18 10h-1.3A5.5 5.5 0 0 0 7 12.5 4 4 0 0 0 8 20h10a4 4 0 0 0 0-8z"/>',
    "file": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/>',
    "chart": '<path d="M3 3v18h18"/><path d="M7 14v4M12 10v8M17 6v12"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "building": '<rect x="4" y="2" width="16" height="20" rx="1"/><path d="M9 22v-4h6v4M8 6h.01M12 6h.01M16 6h.01M8 10h.01M12 10h.01M16 10h.01M8 14h.01M12 14h.01M16 14h.01"/>',
    "rocket": '<path d="M5 15s1-4 6-7 8-3 8-3-1 5-4 8-7 5-7 5z"/><path d="M9 9 4 4"/><path d="m9 15-3 5 5-3"/>',
    "lock": '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
    "zap": '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
    "layout": '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/>',
    "db": '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v6c0 1.7 4 3 9 3s9-1.3 9-3V5"/><path d="M3 11v6c0 1.7 4 3 9 3s9-1.3 9-3v-6"/>',
    "compass": '<circle cx="12" cy="12" r="10"/><polygon points="16.2 7.8 11 12 16.2 16.2 7.8 12 16.2 7.8"/>',
    "check": '<path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>',
    "cpu": '<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 1v3M15 1v3M9 20v3M15 20v3M1 9h3M1 15h3M20 9h3M20 15h3"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
    "map": '<polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"/><line x1="8" y1="2" x2="8" y2="18"/><line x1="16" y1="6" x2="16" y2="22"/>',
    "heart": '<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.6l-1-1a5.5 5.5 0 0 0-7.8 7.8l1 1L12 21l7.8-7.6 1-1a5.5 5.5 0 0 0 0-7.8z"/>',
    "pen": '<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/>',
}


def ico(name: str) -> str:
    return (
        '<svg class="lux-ico" viewBox="0 0 24 24" aria-hidden="true" fill="none" '
        'stroke="currentColor" stroke-width="1.6" stroke-linecap="round" '
        f'stroke-linejoin="round">{PATHS[name]}</svg>'
    )


# Newest three journal posts only. Older 2025 articles stay off these hubs.
RECENT_BLOGS = [
    (
        "mcp-enterprise-integrations-2026.html",
        "MCP Enterprise Integrations: A Security-First Guide",
        "26 September 2026",
        "2026-09-26",
        "images/blog-mcp-enterprise-2026.webp",
        "How to plan safe enterprise AI tool integrations with clear permissions.",
    ),
    (
        "rag-enterprise-ai-search-2026.html",
        "RAG for Enterprise AI Search: A Practical Build Guide",
        "26 September 2026",
        "2026-09-26",
        "images/blog-rag-enterprise-search-2026.webp",
        "Prepare documents, preserve access rules and measure search quality.",
    ),
    (
        "llm-testing-quality-engineering-2026.html",
        "LLM Testing and Quality Engineering: A 2026 Guide",
        "26 September 2026",
        "2026-09-26",
        "images/blog-llm-quality-engineering-2026.webp",
        "Evaluate responses, build test sets and use release gates for production AI.",
    ),
]


def recent_blogs_schema() -> dict:
    return {
        "@type": "ItemList",
        "name": "Recent studio notes",
        "itemListOrder": "https://schema.org/ItemListOrderDescending",
        "numberOfItems": len(RECENT_BLOGS),
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i,
                "url": "{{SITE_URL}}/" + href.replace(".html", ""),
                "name": title,
            }
            for i, (href, title, _d, _iso, _img, _ex) in enumerate(RECENT_BLOGS, 1)
        ],
    }


def recent_blogs_section() -> str:
    cards = []
    for href, title, date, iso, img, excerpt in RECENT_BLOGS:
        cards.append(
            f"""            <a class="lux-post" href="{href}">
              <img src="{img}" alt="" width="640" height="400" loading="lazy" decoding="async">
              <div class="lux-post-body">
                <time datetime="{iso}">{date}</time>
                <h3>{title}</h3>
                <p>{excerpt}</p>
              </div>
            </a>"""
        )
    joined = "\n".join(cards)
    return f"""      <section id="journal" class="lux-section lux-theme-light" aria-labelledby="journal-title" data-reveal>
        <div class="lux-wrap">
          <p class="lux-kicker">Journal</p>
          <h2 id="journal-title" class="lux-title" data-split>Recent notes from the studio.</h2>
          <p class="lux-lead">Three current pieces on enterprise AI. Written this month, not recycled roundups.</p>
          <div class="lux-posts lux-posts-3">
{joined}
          </div>
          <div class="lux-actions" style="margin-top:1.6rem">
            <a class="lux-btn lux-btn-ink" href="blogs.html">All journal posts</a>
          </div>
        </div>
      </section>
"""


PAGES = [
    {
        "file": "software-development.html",
        "slug": "software-development",
        "title": "Custom Software Development Company in Delhi NCR | BlueByte",
        "description": "BlueByte is a custom software development company in Delhi NCR. We design web apps, internal tools and mobile software around your workflows, with a scoped plan before build.",
        "keywords": "custom software development Delhi, software company Delhi NCR, business application development India",
        "service_name": "Custom software development",
        "kicker": "Software",
        "h1": "Custom software development in Delhi NCR.",
        "lead": "BlueByte writes software around how your team already works: web apps, internal systems and mobile products that stay readable, secure and ready to grow.",
        "define_h2": "What is custom software development?",
        "define": "Custom software development is the design and build of an application that matches your process, not a packaged product you have to work around. For Delhi NCR teams that usually means a web app, an internal operations tool or a mobile companion, with integrations into finance, CRM and the rest of the stack you already pay for.",
        "intro": [
            "Off-the-shelf tools run out of road. BlueByte IT Solutions is a software development company in Delhi NCR that starts with workflows, then shapes the product. The result is software your operators will use, not another login they avoid.",
            "Startups and established companies come to us for the same brief: a secure, scalable system that meets this year and does not trap next year. We work in Delhi, Noida, Gurugram and remotely across India.",
        ],
        "image": "images/feature-1.webp",
        "image_alt": "Engineers reviewing custom software architecture in Delhi",
        "audiences": [
            ("rocket", "Founders shipping a first product", "A thin, honest first release that tests demand without a two-year programme."),
            ("building", "Operators drowning in spreadsheets", "Internal tools that replace copy-paste between finance, stock and support."),
            ("users", "Teams with a live system that creaks", "A staged takeover: audit, harden, then improve without a risky rewrite."),
        ],
        "offers_title": "Software we actually ship",
        "offers": [
            ("code", "Web and internal applications", "Browser-based systems your staff can use on a laptop, with roles and an audit trail."),
            ("monitor", "Customer-facing products", "Portals and self-serve flows that cut tickets and keep brand intact."),
            ("layout", "Mobile companions", "iOS and Android when the job happens away from a desk."),
            ("cpu", "Integrations and APIs", "Connect GST, payments, CRM and warehouse tools so data is typed once."),
            ("lock", "Security as product work", "Access control, encryption and logs, not a patch after launch."),
            ("shield", "Care after go-live", "Monitoring, small releases and a team that still answers the phone."),
        ],
        "include_h2": "What a BlueByte software project includes",
        "include": [
            "Discovery workshop and a written scope you can share with finance.",
            "Information architecture, UX and a clickable prototype for the risky screens.",
            "Engineering with code review, tests and a staging environment you can click.",
            "Deployment, handover documentation and a two-week hypercare window.",
            "An optional care plan for patches, small features and uptime watch.",
        ],
        "steps": [
            ("compass", "Map the work", "Users, revenue and the systems you refuse to rip out."),
            ("pen", "Shape the product", "Architecture, UX and a dated plan with milestones."),
            ("code", "Build in slices", "Shippable increments, demos you can click, a changelog in plain language."),
            ("shield", "Launch and watch", "Go-live, measure, patch. The product stays calm after the applause."),
        ],
        "industries": [("fintech.html", "Fintech"), ("real-estate.html", "Real estate"), ("health-pharma.html", "Health"), ("manufacturing-logistics.html", "Logistics")],
        "faqs": [
            ("What custom software does BlueByte build in Delhi?", "Web applications, internal business systems, mobile apps and API integrations, scoped to your workflows rather than a packaged product."),
            ("How long does a custom software project take?", "A focused internal tool can ship in a few weeks. Larger platforms follow a dated plan after discovery, with milestones you can audit."),
            ("Do you take over existing software?", "Yes. We audit the codebase, risk and cost of change, then improve in stages instead of forcing a rewrite."),
            ("How is software development priced?", "After a short brief we send a written proposal. It states what is included, what is not, and how change requests are priced."),
            ("Will we own the source code?", "Yes. Repositories, credentials and documentation stay in your name."),
            ("Do you work outside Delhi NCR?", "Yes. The studio is in Delhi. Delivery is India-wide, with remote rituals that keep the work visible."),
        ],
    },
    {
        "file": "web-development.html",
        "slug": "web-development",
        "title": "Web Development Company in Delhi NCR | BlueByte",
        "description": "BlueByte is a web development company in Delhi NCR. We design fast, SEO-ready websites and web apps for startups and established businesses across India.",
        "keywords": "web development company Delhi NCR, website development Delhi, responsive website design India",
        "service_name": "Web development",
        "kicker": "Web",
        "h1": "Web development for brands that need to convert.",
        "lead": "BlueByte is a web development company in Delhi NCR. We design and build fast, secure, mobile-ready sites and web apps that editors can manage and search engines can read.",
        "define_h2": "What does a web development company in Delhi NCR deliver?",
        "define": "A web development company plans, designs and engineers the public site (and often the web app behind it). At BlueByte that means information architecture, visual design, front-end and back-end engineering, CMS setup, performance, accessibility and the technical SEO that lets Google understand the business. The output is a site that loads on a mid-range phone and can be updated without calling a developer for every headline.",
        "intro": [
            "A static brochure rarely holds attention. We build dynamic websites for Delhi, Noida and Gurugram businesses that need real-time content, clean integrations and a calm experience on every device.",
            "Startups, stores and growing companies get the same standard: modern frameworks where they help, careful HTML where they do not, and a CMS the marketing team will actually open.",
        ],
        "image": "images/about-1.webp",
        "image_alt": "Designer and engineer collaborating on a website layout",
        "audiences": [
            ("rocket", "New brands that need a real site", "A launch website with clear offers, speed and analytics, not a five-page template."),
            ("building", "Companies whose site is five years tired", "A rebuild or migration that keeps URLs, rankings and the content you already paid for."),
            ("bag", "Teams selling online", "Catalogue, checkout and content on one platform, wired to payments and stock."),
        ],
        "offers_title": "Website work, in practice",
        "offers": [
            ("zap", "Fast by design", "Caching, image discipline and lean scripts so bounce rates stay down."),
            ("pen", "Built for your brief", "IA, design and development around your brand, not a bought theme."),
            ("monitor", "Responsive on every screen", "Layouts that stay readable on phones, tablets and desktops."),
            ("file", "A CMS you will use", "WordPress, headless or a custom admin so editors publish without engineering."),
            ("lock", "Secure, scalable hosting", "Backups, access control and a stack that holds when a campaign lands."),
            ("search", "Search-ready markup", "Clean HTML, metadata and structured data where it helps Google quote you."),
        ],
        "include_h2": "What is included in BlueByte web development",
        "include": [
            "Sitemap, wireframes and a design system sized to the site, not a 40-page deck.",
            "Responsive front end, accessible defaults and Core Web Vitals work.",
            "CMS with roles, previews and training for the people who will publish.",
            "On-page SEO: titles, headings, schema, redirects and an XML sitemap.",
            "Analytics, Search Console handover and a short care window after launch.",
        ],
        "steps": [
            ("compass", "Brief and map", "Goals, audiences, must-keep URLs and the pages that earn money."),
            ("layout", "Design the system", "Type, layout and components you can reuse, not one-off artboards."),
            ("code", "Build and connect", "Front end, CMS, forms and the tools marketing already lives in."),
            ("search", "Launch for search", "Redirects, schema, speed pass, then watch Search Console with you."),
        ],
        "industries": [("real-estate.html", "Real estate"), ("education.html", "Education"), ("retail-e-commerce.html", "Retail"), ("health-pharma.html", "Health")],
        "faqs": [
            ("Is BlueByte a web development company in Delhi NCR?", "Yes. We design and develop custom websites and web applications for clients in Delhi, Noida, Gurugram and across India."),
            ("How long does a new website take?", "A marketing site often ships in four to eight weeks. Web applications follow a plan written after discovery."),
            ("Will the website work on mobile?", "Yes. Responsive layout, tap targets and performance on mid-range phones are part of the build, not extras."),
            ("Can you rebuild an existing website without losing SEO?", "We map URLs, set redirects and migrate content so rankings have a chance to hold while the new site goes live."),
            ("Do you use WordPress?", "When it fits. We also build headless and custom stacks when editors, speed or integrations need more control."),
            ("Who writes the content?", "You can. We can. Or we structure the pages and you fill the voice. Technical SEO still sits with us."),
        ],
    },
    {
        "file": "ecommerce.html",
        "slug": "ecommerce",
        "title": "eCommerce Website Development in Delhi NCR | BlueByte",
        "description": "Build or migrate an eCommerce store with BlueByte in Delhi NCR. Shopify, WooCommerce or custom storefronts with payments, inventory and care after launch.",
        "keywords": "eCommerce website development Delhi, Shopify developers India, WooCommerce store development",
        "service_name": "eCommerce development",
        "kicker": "Commerce",
        "h1": "eCommerce that sells, then stays up.",
        "lead": "BlueByte designs storefronts around your catalogue, checkout and operations, from first SKU to sale-day traffic, with integrations that keep orders moving.",
        "define_h2": "What is eCommerce website development?",
        "define": "eCommerce website development is the design of the storefront plus the system behind it: catalogue, search, cart, tax, payment, shipping and inventory. BlueByte builds and migrates Shopify, WooCommerce and custom stores for Delhi NCR brands so shoppers can buy in a few taps and your team is not retyping orders into a spreadsheet.",
        "intro": [
            "A store is a system, not a skin. We plan catalogue, search, cart, payment and fulfilment together so the path to buy is short and the path to pick-pack is clear.",
            "Platform choice follows the catalogue and the people who will live in admin. Then we wire gateways, carriers and stock so nothing is typed twice.",
        ],
        "image": "images/retail-slide.webp",
        "image_alt": "eCommerce storefront and product grid on a laptop",
        "audiences": [
            ("bag", "Brands opening their first store", "A clean catalogue, honest shipping and a checkout that does not surprise anyone."),
            ("building", "Retailers adding a second channel", "Inventory and orders in one place, whether the sale started in-store or online."),
            ("zap", "Stores that buckle on campaign day", "Performance, caching and a platform that holds when the ad budget lands."),
        ],
        "offers_title": "Store capabilities",
        "offers": [
            ("monitor", "Custom storefronts", "Theme or headless builds that match the brand and still check out in a few taps."),
            ("layers", "Platform migration", "Move carts, customers and redirects without throwing SEO or order history away."),
            ("zap", "Speed on sale days", "Image policy, caching and load tests before the campaign, not after it fails."),
            ("lock", "Payments and tax", "Gateways, GST-ready invoices and the carriers you already use."),
            ("cpu", "Headless commerce", "A flexible front end on a stable engine when the brand needs more control."),
            ("shield", "Care after launch", "Plugin hygiene, updates and monitoring so the till keeps ringing."),
        ],
        "include_h2": "What our eCommerce build includes",
        "include": [
            "Catalogue model, variants, and navigation a shopper can scan.",
            "Checkout, payment, shipping rules and order emails you can brand.",
            "Admin training for the people who will change price and stock.",
            "Redirect map if we are migrating, plus analytics on funnel drop-off.",
            "A go-live checklist and a care window through the first campaign.",
        ],
        "steps": [
            ("compass", "Map the catalogue", "SKUs, bundles, regions and the messy bits that break generic themes."),
            ("layout", "Design the path to buy", "Search, PDP, cart and checkout on a phone first."),
            ("code", "Integrate operations", "Payments, tax, warehouse and support tools, tested with real orders."),
            ("zap", "Prove it under load", "Speed pass and a rehearsal before you spend on ads."),
        ],
        "industries": [("retail-e-commerce.html", "Retail"), ("health-pharma.html", "Health"), ("agriculture.html", "Food"), ("automotive.html", "Automotive")],
        "faqs": [
            ("Which eCommerce platforms does BlueByte use?", "Shopify, WooCommerce and custom storefronts. We recommend based on catalogue size, team skills and the integrations you need."),
            ("Can you migrate my existing store?", "Yes. We map products, customers, redirects and checkout so rankings and order history survive the move."),
            ("Do you handle payments and shipping?", "We integrate the gateways and carriers you choose, plus inventory and GST-ready invoicing where needed."),
            ("How do you keep a store fast?", "Image policy, caching, lean scripts and load tests before campaigns."),
            ("Will I be able to add products myself?", "Yes. Admin training is part of delivery. Complex catalogue rules can still be ours to maintain."),
            ("Do you work with Delhi NCR warehouses?", "We integrate the tools they already use. The store sits in your cloud, not ours."),
        ],
    },
    {
        "file": "digital-marketing.html",
        "slug": "digital-marketing",
        "title": "Digital Marketing and SEO Company in Delhi NCR | BlueByte",
        "description": "BlueByte is a digital marketing and SEO company in Delhi NCR. Technical SEO, content and paid channels planned around qualified traffic, not vanity charts.",
        "keywords": "digital marketing company Delhi, SEO services Delhi NCR, Google Business optimisation India",
        "service_name": "Digital marketing and SEO",
        "kicker": "Growth",
        "h1": "Digital marketing that answers, then converts.",
        "lead": "BlueByte builds search, content and campaign systems for Delhi NCR brands. The goal is qualified traffic and reporting a founder can read.",
        "define_h2": "What is digital marketing for a Delhi NCR business?",
        "define": "Digital marketing is the work of being found, understood and chosen online. For most of our clients that mix is technical SEO, useful pages, Google Business, and paid search where it earns its cost. BlueByte plans the mix around one number you care about (leads, booked calls, or revenue), then reports in that language.",
        "intro": [
            "A website without a plan is a quiet room. We combine technical SEO, service pages and paid media so the right people can find you, then we measure what they do next.",
            "Campaigns start with audience, offer and a number. Channels come second. You keep the accounts.",
        ],
        "image": "images/blog-4.webp",
        "image_alt": "Search and content planning for a Delhi brand",
        "audiences": [
            ("search", "Local firms that Google cannot find", "Maps, Google Business and pages that name the service and the city."),
            ("building", "Sites that rank for the wrong words", "A content and technical pass aimed at intent, not traffic for its own sake."),
            ("rocket", "Teams ready to pay for speed", "PPC with landing pages and budgets you can defend in a board pack."),
        ],
        "offers_title": "How we grow a channel",
        "offers": [
            ("search", "Search engine optimisation", "On-page, technical and local SEO so Google can send intent-rich visits."),
            ("zap", "Paid search", "Tight match types, honest landing pages and a weekly read on cost per lead."),
            ("pen", "Content that ranks and helps", "Guides and service pages written for people, structured so search can quote them."),
            ("users", "Social with a job", "Channel plans that support the offer, not a random posting calendar."),
            ("mail", "Email and journeys", "Welcome, nurture and win-back mail that follows a real path."),
            ("chart", "Analytics you will open", "Dashboards tied to leads and revenue, not only sessions."),
        ],
        "include_h2": "What our SEO and marketing retainers include",
        "include": [
            "Technical crawl, keyword map and a 90-day page plan.",
            "On-page work, internal links and schema on the pages that earn.",
            "Google Business, Search Console and analytics in your name.",
            "Monthly notes in plain language: what moved, what we will do next.",
            "Landing page and ad support when paid is part of the mix.",
        ],
        "steps": [
            ("compass", "Audit the gap", "Crawl, rankings, conversion paths and the queries you should own."),
            ("pen", "Fix the pages", "Titles, intent, speed and the internal links Google needs."),
            ("search", "Earn the query", "Content and local signals, shipped on a cadence you can see."),
            ("chart", "Report the number", "Leads and revenue first. Rankings as a supporting chart."),
        ],
        "industries": [("real-estate.html", "Real estate"), ("education.html", "Education"), ("health-pharma.html", "Health"), ("retail-e-commerce.html", "Retail")],
        "faqs": [
            ("Do you offer SEO for businesses in Delhi NCR?", "Yes. Technical SEO, content and Google Business work for local and national search, with reporting on rankings, traffic and leads."),
            ("How soon will we see SEO results?", "Paid campaigns can move in days. Organic search usually needs a few months of consistent pages and fixes. We set that in writing."),
            ("Do you only run ads?", "No. We prefer a mix: a site that can rank, content that answers questions, and paid media where it earns its cost."),
            ("Will we own the ad and analytics accounts?", "Yes. They stay in your name. We work inside them."),
            ("Can you work with our existing website?", "Usually. If the site cannot rank or convert, we will say so before taking a retainer."),
            ("Do you write in English only?", "English is default. Hindi support for local pages is available when the audience needs it."),
        ],
    },
    {
        "file": "product-engineer.html",
        "slug": "product-engineer",
        "title": "Product Engineering Company in Delhi NCR | BlueByte",
        "description": "BlueByte product engineering in Delhi NCR takes an idea from discovery to a maintainable MVP and live service, with architecture, mobile and lifecycle care.",
        "keywords": "product engineering Delhi, MVP development India, digital product design and build",
        "service_name": "Product engineering",
        "kicker": "Product",
        "h1": "Product engineering from idea to a calm launch.",
        "lead": "BlueByte takes a product from discovery to a maintainable service: research, architecture, MVP, mobile and the care a live system needs.",
        "define_h2": "What is product engineering?",
        "define": "Product engineering is a through-line from research to a live digital service, with one team accountable for outcome. At BlueByte that covers discovery, architecture, MVP, full build, mobile where needed, and the roadmap after users arrive. It is not a pile of disconnected vendors.",
        "intro": [
            "The aim is a product the market can use, on a budget you can explain. Discovery first, then an MVP that tests the riskiest assumption, then a build that will not collapse at version two.",
            "We pair with your PM when you have one. We hold the brief when you do not. The studio is in Delhi NCR; delivery is India-wide.",
        ],
        "image": "images/feature-2.webp",
        "image_alt": "Product team reviewing an MVP prototype",
        "audiences": [
            ("rocket", "Founders with a sharp idea", "An MVP that tests the real risk, not a feature list dressed as a product."),
            ("users", "In-house teams that need extra bench", "Senior engineers who join your rituals and leave the repo healthier."),
            ("building", "Businesses modernising a legacy tool", "A staged rebuild that keeps revenue on while the new service takes over."),
        ],
        "offers_title": "The product path",
        "offers": [
            ("compass", "Discovery and design", "User evidence, constraints and a product shape before we spend on code."),
            ("code", "Software engineering", "Architecture a new engineer can enter without a guided tour."),
            ("monitor", "Mobile products", "iOS, Android or a shared codebase when the job is in someone's pocket."),
            ("layers", "Prototypes and MVPs", "A thin first release that tests demand instead of decorating a guess."),
            ("check", "Quality in the loop", "Testing planned with the build so launch is not a surprise."),
            ("shield", "Lifecycle after launch", "Roadmaps, refactors and product ops so the thing you shipped keeps earning."),
        ],
        "include_h2": "What a product engineering engagement includes",
        "include": [
            "Problem framing, user interviews and a one-page product brief.",
            "Architecture options with cost and risk named in plain language.",
            "MVP scope you can fund, plus the later slices we are not doing yet.",
            "Build with demos, tests and a staging URL stakeholders can click.",
            "Launch plan, analytics and a 30-day steer after users arrive.",
        ],
        "steps": [
            ("compass", "Prove the problem", "Who hurts, how often, and what they do today instead."),
            ("pen", "Cut the MVP", "The smallest release that tests the expensive assumption."),
            ("code", "Engineer in the open", "Weekly demos, a repo you own, no mystery sprint."),
            ("chart", "Learn from live use", "Instrumentation, interviews, then the next honest slice."),
        ],
        "industries": [("fintech.html", "Fintech"), ("education.html", "Education"), ("health-pharma.html", "Health"), ("media-entertainment.html", "Media")],
        "faqs": [
            ("What is product engineering at BlueByte?", "A through-line from research and architecture to MVP, full build and ongoing care, with one team accountable for the outcome."),
            ("Can you start with an MVP?", "Yes. We cut to the smallest release that tests the real risk, then plan the next slice from what users do."),
            ("Do you work with in-house product teams?", "We pair with your PM and design leads, or we hold the brief when you do not have that bench yet."),
            ("How do you control cost?", "A written scope, staged delivery and a change path. You see the burn before it becomes a story."),
            ("Will the MVP be throwaway?", "No. We design it to grow. If a spike is truly disposable, we will label it as such."),
            ("Where is the team based?", "Delhi NCR, with delivery across India. Rituals are remote-friendly by default."),
        ],
    },
    {
        "file": "cloud-devops.html",
        "slug": "cloud-devops",
        "title": "Cloud and DevOps Company in Delhi NCR | BlueByte",
        "description": "BlueByte plans cloud migration, infrastructure as code and CI/CD for Delhi NCR teams. AWS, Azure and Google Cloud with cost, security and recovery you can drill.",
        "keywords": "cloud DevOps Delhi, AWS consulting India, CI/CD and infrastructure as code",
        "service_name": "Cloud and DevOps",
        "kicker": "Cloud",
        "h1": "Cloud and DevOps that stay quiet in production.",
        "lead": "BlueByte designs cloud platforms and delivery pipelines so releases are boring, costs are visible and recovery is a drill, not a crisis.",
        "define_h2": "What do Cloud and DevOps services include?",
        "define": "Cloud and DevOps services cover how software is hosted, released and watched. BlueByte helps Delhi NCR teams migrate to AWS, Azure or Google Cloud, describe infrastructure as code, put tests on the path to production, and keep cost and security in a weekly rhythm rather than a yearly panic.",
        "intro": [
            "Ticket queues cannot keep up with a product that ships weekly. We automate the path to production and make the system observable.",
            "The work is practical: a migration plan, IaC, CI/CD, cost controls and a security baseline. Development and operations share one way of working.",
        ],
        "image": "images/feature-3.webp",
        "image_alt": "Cloud architecture and deployment pipeline diagram",
        "audiences": [
            ("building", "Teams still on a single server", "A migration in slices, with rollback, so the business does not pause for a weekend cutover."),
            ("zap", "Squads that fear every release", "Pipelines, environments and checks that match how you already commit code."),
            ("lock", "Companies with a cloud bill they cannot explain", "Rightsizing, alerts and a monthly cost conversation in rupees, not dashboards."),
        ],
        "offers_title": "Platform work",
        "offers": [
            ("compass", "Cloud strategy", "Migrate, hybrid or tidy-what-you-have, with cost and risk named up front."),
            ("cloud", "Migration without drama", "Workloads moved in slices so the business stays online."),
            ("code", "Infrastructure as code", "Environments you can recreate, review and audit."),
            ("check", "CI and CD", "Pipelines that test and ship on every change worth shipping."),
            ("lock", "Cost and security", "Identity, alerts and compliance treated as weekly hygiene."),
            ("shield", "Recovery you have drilled", "Backups, runbooks and a restore you have actually run."),
        ],
        "include_h2": "What a BlueByte cloud engagement includes",
        "include": [
            "Inventory of workloads, dependencies and the data you cannot lose.",
            "Target architecture on AWS, Azure or Google Cloud, with a cost sketch.",
            "IaC, environments and a pipeline from commit to production.",
            "Observability: logs, metrics, traces and an on-call path.",
            "Optional managed care: patches, cost reviews and incident help.",
        ],
        "steps": [
            ("compass", "See the estate", "Servers, SaaS, secrets and the one box nobody wants to reboot."),
            ("pen", "Draw the landing zone", "Accounts, networks, identity and the boring security defaults."),
            ("code", "Move in slices", "One service at a time, with rollback, watched in production."),
            ("chart", "Operate it", "Cost, patches and drills on a cadence, not a heroic weekend."),
        ],
        "industries": [("fintech.html", "Fintech"), ("health-pharma.html", "Health"), ("manufacturing-logistics.html", "Logistics"), ("education.html", "Education")],
        "faqs": [
            ("Which clouds do you work with?", "Amazon Web Services, Microsoft Azure and Google Cloud, plus hybrid setups when a system must stay on the premises."),
            ("Can you migrate a live application?", "Yes. We inventory dependencies, move in stages and keep a rollback. The business stays online."),
            ("Do you set up CI/CD from scratch?", "We introduce pipelines, environments and checks that match how your team already commits code."),
            ("Will you help after go-live?", "Managed support is available: monitoring, patches, cost reviews and incident help."),
            ("Do you lock us into one vendor?", "We recommend a primary cloud. Critical pieces can stay portable when the risk is real."),
            ("Is this only for large enterprises?", "No. Small product teams often need this more. The plan scales to the estate, not the other way around."),
        ],
    },
    {
        "file": "content-management-system.html",
        "slug": "content-management-system",
        "title": "CMS Development Company in Delhi NCR | BlueByte",
        "description": "BlueByte designs CMS platforms in Delhi NCR: WordPress, headless or custom, with roles, SEO-ready markup and the integrations your editors need.",
        "keywords": "CMS development Delhi, WordPress development India, headless CMS implementation",
        "service_name": "CMS development",
        "kicker": "Content",
        "h1": "A CMS your editors will actually open.",
        "lead": "BlueByte designs content systems that match how you publish: WordPress, headless or custom, with roles, SEO-ready markup and the integrations your site needs.",
        "define_h2": "What is CMS development?",
        "define": "CMS development is the design of the system your team uses to publish. BlueByte implements WordPress, headless CMS platforms or a custom admin so a marketer can change a page without waiting on engineering, while the public site stays fast, structured and safe to share across roles.",
        "intro": [
            "Corporate sites, stores and journals need different editing models. We pick the platform for the workflow, then add roles, previews and the connectors you rely on.",
            "The test is simple: can the person who owns the campaign ship a page before lunch, without breaking the header?",
        ],
        "image": "images/about-2.webp",
        "image_alt": "Content editor using a CMS preview on desktop",
        "audiences": [
            ("pen", "Marketing teams stuck in tickets", "Fields, previews and guardrails so publishing is a calm task."),
            ("building", "Multi-brand organisations", "Shared components, localised sites and roles that match the org chart."),
            ("search", "Publishers who care about search", "Clean URLs, metadata and structured content SEO work can stand on."),
        ],
        "offers_title": "CMS capabilities",
        "offers": [
            ("file", "Custom CMS builds", "When a packaged tool fights the workflow, we shape one that fits."),
            ("layout", "Editor-first interface", "Clear fields, previews and limits so drafts cannot wreck the live site."),
            ("search", "Search-friendly output", "URLs, metadata and structured content Google can parse."),
            ("users", "Roles and governance", "Who can draft, who can publish, and an audit trail when it matters."),
            ("cpu", "WordPress and headless", "The right model for editors, speed and the number of front ends you need."),
            ("mail", "Integrations", "CRM, DAM, forms, commerce and analytics without copy-paste."),
        ],
        "include_h2": "What a CMS project includes",
        "include": [
            "Workflow mapping with the people who actually publish.",
            "Content model, roles and a preview that matches production.",
            "Theme or front-end build with accessible, SEO-ready markup.",
            "Training, a short handbook and a care window after go-live.",
            "Migration of existing pages with redirects where URLs change.",
        ],
        "steps": [
            ("compass", "Watch people publish", "The real process, including the unofficial spreadsheet."),
            ("pen", "Model the content", "Types, fields and relationships that match the site, not the CMS brochure."),
            ("layout", "Build the editor", "Admin, preview and the public templates together."),
            ("users", "Train and hand over", "A session with the people who will live in it on Monday."),
        ],
        "industries": [("education.html", "Education"), ("media-entertainment.html", "Media"), ("real-estate.html", "Real estate"), ("health-pharma.html", "Health")],
        "faqs": [
            ("Which CMS should we choose?", "It depends on editors, languages, integrations and who will maintain it. We recommend after a short workflow review, not from a default."),
            ("Can you work with WordPress?", "Yes. Theme or block builds, custom plugins, and hardening so the site is not a plugin pile."),
            ("Do you build headless CMS setups?", "When the front end needs to live in more than one place, we separate content from presentation and keep editors in one admin."),
            ("Will non-technical staff be able to update pages?", "That is the point. Training and a simple editing model are part of delivery."),
            ("Can you migrate from our current CMS?", "Yes. We move content, media and URLs, then leave redirects behind."),
            ("Do you lock us into a proprietary CMS?", "Only if you ask for a custom admin. Otherwise we prefer platforms you can hire for later."),
        ],
    },
    {
        "file": "data-science.html",
        "slug": "data-science",
        "title": "Data Science and Analytics Company in Delhi NCR | BlueByte",
        "description": "BlueByte data science in Delhi NCR: analytics engineering, forecasting and applied machine learning designed around a decision you can measure.",
        "keywords": "data science company Delhi, analytics engineering India, machine learning consultants NCR",
        "service_name": "Data science and analytics",
        "kicker": "Data",
        "h1": "Data science that changes a decision.",
        "lead": "BlueByte turns scattered files into models, dashboards and forecasts your team can act on. The test is a clearer choice, not a prettier chart.",
        "define_h2": "What does a data science team actually do?",
        "define": "A data science team cleans the pipes, asks a sharper question and puts a model or a dashboard where the decision happens. BlueByte does analytics engineering, forecasting, applied machine learning and visualisation for Delhi NCR businesses, and we only build what someone will use next week.",
        "intro": [
            "Most companies are rich in files and poor in answers. We help teams in Delhi NCR name the decision first, then pick the method.",
            "Warehouses, quality checks and jobs that run without a hero on call sit underneath. The chart is the last thing we design.",
        ],
        "image": "images/feature-4.webp",
        "image_alt": "Analytics dashboard used for business decisions",
        "audiences": [
            ("chart", "Leaders who do not trust the numbers", "One warehouse, one definition of revenue, reports that match finance."),
            ("cpu", "Teams ready for a first model", "A forecast or a classifier in the workflow, with monitoring so it does not drift."),
            ("building", "Operators drowning in exports", "Pipelines that replace Friday-night CSV merges."),
        ],
        "offers_title": "How we use data",
        "offers": [
            ("compass", "Exploration that names the question", "Find the pattern, then agree what decision it should change."),
            ("chart", "Forecasts you can brief", "Demand, churn or risk, with assumptions in plain language."),
            ("cpu", "Applied machine learning", "Models in the workflow, watched so they do not silently drift."),
            ("pen", "Language and documents", "NLP when the input is text, tickets or contracts, not a spreadsheet."),
            ("db", "Pipelines that hold", "Warehouses, quality checks and jobs that run on a schedule."),
            ("monitor", "Reporting people open", "Visuals tied to the metric a founder already watches."),
        ],
        "include_h2": "What a data engagement includes",
        "include": [
            "A decision statement we can test, not a vague 'insights' brief.",
            "Source inventory, quality rules and a warehouse or lakehouse sketch.",
            "The smallest model or dashboard that would change next week's meeting.",
            "Deployment into your cloud, with access control you own.",
            "A monitor and a review cadence so the thing does not rot.",
        ],
        "steps": [
            ("compass", "Name the decision", "If we cannot write it in one sentence, we are not ready to model."),
            ("db", "Fix the pipes", "Sources, keys and a place the numbers can live."),
            ("cpu", "Build the smallest useful thing", "A forecast, a flag, or a dashboard. Not all three on day one."),
            ("chart", "Put it in the meeting", "If nobody opens it, we change the output, not the colour palette."),
        ],
        "industries": [("fintech.html", "Fintech"), ("retail-e-commerce.html", "Retail"), ("manufacturing-logistics.html", "Logistics"), ("health-pharma.html", "Health")],
        "faqs": [
            ("What data science services does BlueByte offer?", "Analytics engineering, forecasting, applied machine learning, NLP, visualisation and the pipelines that keep them honest."),
            ("Do we need a data warehouse first?", "Often yes, even a small one. We will say so if the data is too messy to model well."),
            ("Will models run in our cloud?", "We deploy into your environment where possible, with access control and monitoring you own."),
            ("How do you measure success?", "A decision that changed, a process that shrank, or a forecast that beat the previous guess. We agree the measure before we build."),
            ("Do you need our data scientists on the call?", "Helpful, not required. We can work with operations and finance if that is who owns the question."),
            ("Is this AI for its own sake?", "No. If a SQL report solves it, we will recommend the report."),
        ],
    },
    {
        "file": "quality-engineering.html",
        "slug": "quality-engineering",
        "title": "Quality Engineering and Software Testing in Delhi NCR | BlueByte",
        "description": "BlueByte quality engineering in Delhi NCR: risk-based testing, automation, performance and accessibility designed around how you actually ship software.",
        "keywords": "quality engineering Delhi, software testing company India, test automation NCR",
        "service_name": "Quality engineering",
        "kicker": "Quality",
        "h1": "Quality engineering that finds issues before users do.",
        "lead": "BlueByte plans testing around risk: function, performance, security and access, with automation where it earns its keep and humans where judgement is required.",
        "define_h2": "What is quality engineering?",
        "define": "Quality engineering is testing designed into the product lifecycle, not a gate in the last week. BlueByte builds strategy, automation, performance, security and accessibility checks for Delhi NCR product teams so defects show up while they are cheap and releases stay boring.",
        "intro": [
            "Functional gaps, slow pages, weak auth and inaccessible screens all count. We cover them with exploratory work, automated suites and performance tests matched to how you ship.",
            "Automation covers the stable paths. People still hunt the strange ones. Both report into your CI, not a slide deck.",
        ],
        "image": "images/about-3.webp",
        "image_alt": "Quality engineer reviewing test results on a product build",
        "audiences": [
            ("rocket", "Teams that ship every week", "Suites on pull requests so a broken path never reaches production quietly."),
            ("building", "Products with a scary release night", "A risk map, a smoke pack and a performance pass before the window."),
            ("heart", "Services that must be usable by more people", "Keyboard, contrast, names and structure, tested, not hoped for."),
        ],
        "offers_title": "What we test for",
        "offers": [
            ("check", "Core behaviour", "Important paths work as specified, with gaps found before customers do."),
            ("zap", "Faster, safer releases", "Automation on the boring checks so people spend time on the risky ones."),
            ("monitor", "Speed and stability", "Load and endurance so the system holds when traffic arrives."),
            ("lock", "Security basics that still work", "Auth, injection, secrets and the boring attacks that still succeed."),
            ("db", "Data you can trust", "Accuracy, migrations and reports that finance will read."),
            ("users", "Access for more people", "Keyboard, contrast and structure so the product is usable, not only pretty."),
        ],
        "include_h2": "What a quality engineering engagement includes",
        "include": [
            "A risk map of journeys, browsers, devices and the data that must not break.",
            "A test strategy your developers can live with, not a 40-page PDF.",
            "Automated suites in CI, with failures that point to a cause.",
            "Exploratory charters for the paths automation should not fake.",
            "A performance and accessibility pass before you call it done.",
        ],
        "steps": [
            ("compass", "Map the risk", "What hurts users, revenue or reputation if it fails on a Tuesday."),
            ("pen", "Design the net", "What to automate, what to explore, what to watch in production."),
            ("code", "Put it in CI", "Pull-request checks and nightly packs with signal, not noise."),
            ("chart", "Read the failures", "Triage with engineering, then shrink the suite that nobody trusts."),
        ],
        "industries": [("fintech.html", "Fintech"), ("health-pharma.html", "Health"), ("education.html", "Education"), ("retail-e-commerce.html", "Retail")],
        "faqs": [
            ("What is quality engineering at BlueByte?", "Testing designed into the product lifecycle: strategy, automation, performance, security and accessibility, not a last-week scramble."),
            ("Do you only write automated tests?", "No. Automation covers the stable paths. Exploratory testing still catches the strange ones."),
            ("Can you join our CI pipeline?", "Yes. Suites run on pull requests and nightly builds, with failures that point to a cause."),
            ("Do you test mobile and web?", "Both, including device coverage that matches your actual users, not a lab of flagships."),
            ("Can you work with our developers?", "That is the job. Quality sitting in another building is how bugs ship."),
            ("Do you offer a one-off audit?", "Yes. A time-boxed pass is often the right first step before a retainer."),
        ],
    },
]


def related_for(filename: str) -> list[tuple[str, str]]:
    return [s for s in ALL_SERVICES if s[0] != filename][:4]


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
    howto_steps = [
        {
            "@type": "HowToStep",
            "position": i,
            "name": title,
            "text": text,
        }
        for i, (_icon, title, text) in enumerate(page["steps"], 1)
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
            "dateModified": "2026-09-27",
            "isPartOf": {"@id": "{{SITE_URL}}/#website"},
            "speakable": {
                "@type": "SpeakableSpecification",
                "cssSelector": [".lux-lead", ".lux-prose", ".lux-faq-list", "#define"],
            },
            "primaryImageOfPage": {
                "@type": "ImageObject",
                "url": "{{SITE_URL}}/" + page["image"],
            },
            "breadcrumb": {"@id": url + "#breadcrumb"},
            "mainEntity": {"@id": url + "#service"},
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
                {"@type": "City", "name": "Noida"},
                {"@type": "City", "name": "Gurugram"},
                {"@type": "Country", "name": "India"},
            ],
            "serviceType": page["service_name"],
            "hasOfferCatalog": {
                "@type": "OfferCatalog",
                "name": page["offers_title"],
                "itemListElement": [
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": title}}
                    for _ico, title, _t in [(o[0], o[1], o[2]) for o in page["offers"]]
                ],
            },
        },
        {
            "@type": "HowTo",
            "@id": url + "#howto",
            "name": "How BlueByte delivers " + page["service_name"],
            "description": page["lead"],
            "step": howto_steps,
        },
        {
            "@type": "BreadcrumbList",
            "@id": url + "#breadcrumb",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": "{{SITE_URL}}/"},
                {"@type": "ListItem", "position": 2, "name": "Services", "item": "{{SITE_URL}}/#localbusiness"},
                {"@type": "ListItem", "position": 3, "name": page["service_name"], "item": url},
            ],
        },
        {"@type": "FAQPage", "@id": url + "#faq", "mainEntity": faqs},
        recent_blogs_schema(),
    ]
    graph[1]["relatedLink"] = [
        "{{SITE_URL}}/" + href.replace(".html", "") for href, *_ in RECENT_BLOGS
    ]
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=2, ensure_ascii=True).replace("\\/", "/")


def offers_html(page: dict) -> str:
    cards = []
    for name, title, text in page["offers"]:
        cards.append(
            f"""            <article class="lux-service">
              {ico(name)}
              <h3>{title}</h3>
              <p>{text}</p>
            </article>"""
        )
    return "\n".join(cards)


def audience_html(page: dict) -> str:
    blocks = []
    for name, title, text in page["audiences"]:
        blocks.append(
            f"""          <article>
            {ico(name)}
            <h3>{title}</h3>
            <p>{text}</p>
          </article>"""
        )
    return "\n".join(blocks)


def steps_html(page: dict) -> str:
    blocks = []
    for name, title, text in page["steps"]:
        blocks.append(
            f"""            <article class="lux-step">
              {ico(name)}
              <h3>{title}</h3>
              <p>{text}</p>
            </article>"""
        )
    return "\n".join(blocks)


def include_html(page: dict) -> str:
    return "\n".join(f"              <li>{item}</li>" for item in page["include"])


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
    return "\n".join(
        f'            <a class="lux-chip" href="{href}">{label} <span aria-hidden="true">→</span></a>'
        for href, label in related_for(page["file"])
    )


def pills_html(page: dict) -> str:
    return "\n".join(
        f'            <a href="{href}">{label}</a>' for href, label in page["industries"]
    )


def page_html(page: dict) -> str:
    schema = schema_block(page)
    intro = "\n".join(f"              <p>{para}</p>" for para in page["intro"])
    return f"""<!DOCTYPE html>
<html lang="en-IN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta http-equiv="X-UA-Compatible" content="ie=edge">
  <link rel="icon" href="/images/favicon.png" type="image/png">
  <title>{page["title"]}</title>
  <meta name="description" content="{page["description"]}">
  <meta name="keywords" content="{page["keywords"]}">
  <meta name="author" content="BlueByte IT Solutions">
  <meta name="robots" content="index,follow">
  <meta property="og:locale" content="en_IN">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{page["title"]}">
  <meta property="og:description" content="{page["description"]}">
  <meta property="og:site_name" content="BlueByte IT Solutions">
  <meta property="og:image" content="{{{{SITE_URL}}}}/{page["image"]}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{page["title"]}">
  <meta name="twitter:description" content="{page["description"]}">
  <meta name="twitter:image" content="{{{{SITE_URL}}}}/{page["image"]}">
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
      <article>
      <section class="lux-hero lux-hero--page" aria-labelledby="service-hero-title">
        <div class="lux-hero-inner">
          <nav class="lux-crumb" aria-label="Breadcrumb">
            <a href="/">Home</a>
            <span aria-hidden="true">/</span>
            <a href="/#localbusiness">Services</a>
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
          <nav class="lux-toc lux-rise lux-rise-4" aria-label="On this page">
            <a href="#define">Definition</a>
            <a href="#who">Who it is for</a>
            <a href="#offers">What you get</a>
            <a href="#include">Included</a>
            <a href="#method">How we work</a>
            <a href="#faq">Questions</a>
            <a href="#journal">Journal</a>
          </nav>
        </div>
      </section>

      <section id="define" class="lux-section lux-theme-light" aria-labelledby="define-title" data-reveal>
        <div class="lux-wrap lux-about-grid">
          <figure class="lux-frame">
            <img src="{page["image"]}" alt="{page["image_alt"]}" width="560" height="700" loading="eager" decoding="async">
          </figure>
          <div>
            <p class="lux-kicker">Definition</p>
            <h2 id="define-title" class="lux-title">{page["define_h2"]}</h2>
            <div class="lux-prose">
              <p>{page["define"]}</p>
{intro}
            </div>
          </div>
        </div>
      </section>

      <section id="who" class="lux-section lux-theme-light lux-tight" aria-labelledby="who-title" data-reveal>
        <div class="lux-wrap">
          <p class="lux-kicker">Fit</p>
          <h2 id="who-title" class="lux-title" data-split>Who this service is for.</h2>
          <div class="lux-audience">
{audience_html(page)}
          </div>
        </div>
      </section>

      <section id="offers" class="lux-section lux-theme-dark" aria-labelledby="offers-title" data-reveal>
        <div class="lux-wrap">
          <p class="lux-kicker">Capabilities</p>
          <h2 id="offers-title" class="lux-title" data-split>{page["offers_title"]}</h2>
          <div class="lux-service-grid">
{offers_html(page)}
          </div>
        </div>
      </section>

      <section id="include" class="lux-section lux-theme-light" aria-labelledby="include-title" data-reveal>
        <div class="lux-wrap lux-split">
          <div>
            <p class="lux-kicker">Scope</p>
            <h2 id="include-title" class="lux-title">{page["include_h2"]}</h2>
            <p class="lux-lead">A clear list beats a mood board. This is the default. We cut or add in the proposal.</p>
          </div>
          <ul class="lux-include">
{include_html(page)}
          </ul>
        </div>
      </section>

      <section id="method" class="lux-section lux-theme-light lux-tight" aria-labelledby="method-title" data-reveal>
        <div class="lux-wrap">
          <p class="lux-kicker">Method</p>
          <h2 id="method-title" class="lux-title" data-split>How we run the engagement.</h2>
          <p class="lux-lead">Visible work. Dated slices. No mystery sprint.</p>
          <div class="lux-steps">
{steps_html(page)}
          </div>
        </div>
      </section>

      <section class="lux-section lux-theme-dark" aria-labelledby="industries-title" data-reveal>
        <div class="lux-wrap">
          <p class="lux-kicker">Sectors</p>
          <h2 id="industries-title" class="lux-title" data-split>Where this work already lives.</h2>
          <p class="lux-lead">Same craft, different grain. Read how we approach the industries we know.</p>
          <div class="lux-pills">
{pills_html(page)}
          </div>
        </div>
      </section>

      <section id="faq" class="lux-section lux-theme-dark" aria-labelledby="faq-title" data-reveal>
        <div class="lux-wrap">
          <p class="lux-kicker">Questions</p>
          <h2 id="faq-title" class="lux-title" data-split>Answers people type into search.</h2>
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

{recent_blogs_section()}
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
      </article>
    </main>
{FOOTER}
"""


def assert_clean(text: str, name: str) -> None:
    if "\u2014" in text or "\u2013" in text:
        raise SystemExit(f"dash found in {name}")
    if text.count("<h1") != 1:
        raise SystemExit(f"h1 count {text.count('<h1')} in {name}")
    if "lux-service-num" in text or "lux-index" in text:
        raise SystemExit(f"index class found in {name}")


def main() -> None:
    for page in PAGES:
        html = page_html(page)
        assert_clean(html, page["file"])
        raw = html.split('<script type="application/ld+json">', 1)[1].split("</script>", 1)[0]
        json.loads(raw.replace("{{SITE_URL}}", "https://example.com"))
        (ROOT / page["file"]).write_text(html, encoding="utf-8")
        print("wrote", page["file"], html.count("\n"), "lines")


if __name__ == "__main__":
    main()
