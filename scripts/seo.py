#!/usr/bin/env python3
"""Domain-aware SEO build and audit helper for this static site.

Build/deploy with:
    SITE_URL=https://www.example.com python3 scripts/seo.py build
Optional analytics:
    SITE_URL=https://www.example.com GA_MEASUREMENT_ID=G-XXXXXXXXXX python3 scripts/seo.py build
The generated static site is written to ./dist (the Wrangler assets directory).
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
ORIGIN_TOKEN = "{{SITE_URL}}"
GA_TOKEN = "{{GA_MEASUREMENT_ID}}"
BRAND = "BlueByte IT Solutions"

# Page intent, not keyword stuffing. Keep this as the single source for page-level SEO.
PAGES: dict[str, dict[str, str]] = {
    "index": {
        "title": "IT Company in Delhi | Software & Web Development | BlueByte",
        "description": "BlueByte IT Solutions builds custom software, websites and mobile apps for businesses in Delhi NCR and across India. Talk with our team about your next digital product.",
        "image": "images/og-image.webp", "kind": "home",
    },
    "about": {
        "title": "About BlueByte IT Solutions | Software Team in Delhi NCR",
        "description": "Meet BlueByte IT Solutions, a Delhi NCR software team focused on custom software, web and mobile products, cloud engineering and practical digital transformation.",
        "image": "images/about-1.webp",
    },
    "contact": {
        "title": "Contact BlueByte IT Solutions | Delhi NCR Software Team",
        "description": "Contact BlueByte IT Solutions in Delhi NCR about custom software, web or mobile development, cloud engineering and digital transformation projects.",
        "image": "images/contact.webp",
    },
    "blogs": {
        "title": "Software, AI & Web Development Insights | BlueByte",
        "description": "Explore practical articles from BlueByte on software development, web technologies, eCommerce, cloud and AI for product and business teams.",
        "image": "images/blog-ecommerce-stack.webp",
    },
    "portfolio": {
        "title": "Our Work | Software & Web Development Portfolio | BlueByte",
        "description": "Explore selected BlueByte websites and digital products, including the project goals, design decisions and engineering work behind each delivery.",
        "image": "images/og-image.webp",
    },
    "case-studies": {
        "title": "Client Case Studies | BlueByte IT Solutions",
        "description": "Read BlueByte project case studies covering client goals, delivery approaches and digital products across web, software and online services.",
        "image": "images/og-image.webp",
    },
    "web-development": {
        "title": "Web Development Company in Delhi NCR | BlueByte",
        "description": "Plan a fast, responsive website or web application with BlueByte. We design and develop custom web experiences for businesses in Delhi NCR and across India.",
        "image": "images/banner-bg-11.png", "service": "Web development",
    },
    "software-development": {
        "title": "Custom Software Development in Delhi NCR | BlueByte",
        "description": "BlueByte builds custom software and business applications around your workflows, integrations and growth needs, with delivery options for teams in Delhi NCR and India.",
        "image": "images/banner-bg-11.png", "service": "Custom software development",
    },
    "product-engineer": {
        "title": "Digital Product Engineering Services | BlueByte",
        "description": "Turn a product idea into a maintainable digital service with BlueByte product engineering, from discovery and architecture through implementation and iteration.",
        "image": "images/banner-bg-11.png", "service": "Product engineering",
    },
    "quality-engineering": {
        "title": "Software Quality Engineering & Testing | BlueByte",
        "description": "Improve software reliability with risk-based testing, quality engineering and automation designed around your product, users and release process.",
        "image": "images/banner-bg-11.png", "service": "Quality engineering",
    },
    "cloud-devops": {
        "title": "Cloud & DevOps Services | BlueByte IT Solutions",
        "description": "Plan cloud migration, infrastructure automation and delivery pipelines with BlueByte. Build a secure, observable cloud platform matched to your technical needs.",
        "image": "images/banner-bg-11.png", "service": "Cloud and DevOps",
    },
    "ecommerce": {
        "title": "eCommerce Website & Platform Development | BlueByte",
        "description": "Build an eCommerce store around your catalog, customer journey and operations with BlueByte, including custom storefronts, integrations and platform development.",
        "image": "images/banner-bg-11.png", "service": "eCommerce development",
    },
    "content-management-system": {
        "title": "CMS Development & Integration Services | BlueByte",
        "description": "Choose and customise a content management system that fits your publishing workflow, integrations and governance needs, from BlueByte's CMS team.",
        "image": "images/banner-bg-11.png", "service": "Content management systems",
    },
    "digital-marketing": {
        "title": "Digital Marketing & SEO Services | BlueByte Delhi NCR",
        "description": "Build a measurable digital marketing plan with BlueByte, combining technical SEO, useful content and channel strategy around your audience and business goals.",
        "image": "images/banner-bg-11.png", "service": "Digital marketing",
    },
    "data-science": {
        "title": "Data Science & Analytics Solutions | BlueByte",
        "description": "Make business data more useful with analytics engineering, data science and applied machine learning designed around clear decisions and measurable needs.",
        "image": "images/banner-bg-11.png", "service": "Data science",
    },
    "agriculture": {
        "title": "Agriculture Software & Digital Solutions | BlueByte",
        "description": "Explore software options for farm operations, crop data, supply chains and agricultural commerce, designed around the needs of agribusiness teams.",
        "image": "images/agriculture-slide.webp", "service": "Agriculture technology",
    },
    "automotive": {
        "title": "Automotive Software & Digital Solutions | BlueByte",
        "description": "BlueByte helps automotive businesses plan digital products, connected workflows and customer-facing platforms around their operational requirements.",
        "image": "images/automotive-slide.webp", "service": "Automotive software",
    },
    "education": {
        "title": "Education Software & Digital Learning Solutions | BlueByte",
        "description": "Explore education technology for digital learning, administration and student services, built around the needs of schools, educators and learners.",
        "image": "images/education-slide.webp", "service": "Education technology",
    },
    "fintech": {
        "title": "FinTech Software Development & Engineering | BlueByte",
        "description": "Design financial technology around secure workflows, integrations and user needs, from digital platforms and payment experiences to custom software.",
        "image": "images/fintech-slide.webp", "service": "Financial technology",
    },
    "health-pharma": {
        "title": "Healthcare & Pharma Software Solutions | BlueByte",
        "description": "Plan healthcare and pharmaceutical software around clinical, operational and patient-facing workflows, with security and integration needs considered early.",
        "image": "images/health-pharma-slide.webp", "service": "Healthcare and pharmaceutical software",
    },
    "manufacturing-logistics": {
        "title": "Manufacturing & Logistics Software | BlueByte",
        "description": "Connect manufacturing and logistics workflows with purpose-built software for operations, inventory, supply chains and business systems.",
        "image": "images/logistics-slide.webp", "service": "Manufacturing and logistics software",
    },
    "media-entertainment": {
        "title": "Media & Entertainment Software Solutions | BlueByte",
        "description": "Develop digital media products, content platforms and audience experiences with technology planned for your publishing and distribution workflows.",
        "image": "images/media-slide.webp", "service": "Media and entertainment software",
    },
    "real-estate": {
        "title": "Real Estate Website & Software Development | BlueByte",
        "description": "Create real estate websites and digital tools for property discovery, lead management and customer service, tailored to your team and portfolio.",
        "image": "images/og-image.webp", "service": "Real estate software",
    },
    "retail-e-commerce": {
        "title": "Retail & eCommerce Software Development | BlueByte",
        "description": "Plan retail and eCommerce platforms around product discovery, order operations and customer experience, with integrations that support your business.",
        "image": "images/retail-slide.webp", "service": "Retail and eCommerce software",
    },
    "the-ultimate-guide-to-healthcare-app-development-cost": {
        "title": "Healthcare App Development Cost: Key Factors | BlueByte",
        "description": "Understand the main factors that shape healthcare app development costs, from product scope and integrations to security, compliance and ongoing support.",
        "image": "images/about-video.webp", "kind": "article",
    },
    "what-is-web-development-complete-beginner-guide-2026": {
        "title": "What Is Web Development? A Beginner's Guide (2026)",
        "description": "Learn what web development includes, how frontend and backend work together, which skills matter and how beginners can start building web projects.",
        "image": "images/blog-web-development-guide-2026.png", "kind": "article",
    },
    "5-must-have-integrations-for-ecommerce-success": {
        "title": "5 eCommerce Integrations That Support Online Stores | BlueByte",
        "description": "See how payment, CRM, inventory, email marketing and analytics integrations can support eCommerce operations, and what to consider before choosing tools.",
        "image": "images/blog-ecommerce-stack.webp", "kind": "article",
    },
    "best-technology-for-ecommerce-in-2026": {
        "title": "eCommerce Technology in 2026: Platforms & Tools | BlueByte",
        "description": "Compare eCommerce platform, frontend, backend, AI and payment technology choices using practical criteria for your store, team and growth plans.",
        "image": "images/blog-ecommerce-stack.webp", "kind": "article",
    },
    "top-frontend-technologies-to-use-in-2026": {
        "title": "Frontend Technologies to Consider in 2026 | BlueByte",
        "description": "Compare frontend frameworks and tools for 2026 by rendering approach, performance, team experience, accessibility and long-term maintenance.",
        "image": "images/blog-frontend-techs.webp", "kind": "article",
    },
    "future-proofing-legacy-apps": {
        "title": "Modernising Legacy Applications with Composable Architecture",
        "description": "Learn how modular architecture can support gradual legacy application modernisation, reduce change risk and make room for new capabilities.",
        "image": "images/auth-bg-2.webp", "kind": "article",
    },
    "agentic-ai-autonomous-systems-it-service-providers": {
        "title": "Agentic AI & Autonomous Systems: A Practical Guide | BlueByte",
        "description": "Understand agentic AI systems, where bounded autonomy can help IT service teams, and the safeguards, approvals and evaluation needed before deployment.",
        "image": "images/agentic-ai-operations.webp", "kind": "article",
    },
    "mcp-enterprise-integrations-2026": {
        "title": "MCP Enterprise Integrations: Security Guide (2026)",
        "description": "Learn what changed in the 2026 Model Context Protocol spec and how to connect AI to enterprise tools with clear permissions, approvals and monitoring.",
        "image": "images/blog-mcp-enterprise-2026.webp", "kind": "article",
        "datePublished": "2026-09-26",
    },
    "rag-enterprise-ai-search-2026": {
        "title": "RAG for Enterprise AI Search: A 2026 Build Guide",
        "description": "Build enterprise RAG search with permission-aware retrieval, useful citations and measurable answer quality using this practical AI implementation guide.",
        "image": "images/blog-rag-enterprise-search-2026.webp", "kind": "article",
        "datePublished": "2026-09-26",
    },
    "llm-testing-quality-engineering-2026": {
        "title": "LLM Testing & Quality Engineering: 2026 Guide",
        "description": "Use risk-based LLM testing, repeatable AI evaluation and prompt-injection checks to improve generative AI application quality before release.",
        "image": "images/blog-llm-quality-engineering-2026.webp", "kind": "article",
        "datePublished": "2026-09-26",
    },
    "genai-cloud-operations-2026": {
        "title": "Generative AI Cloud Operations: Cost & Reliability",
        "description": "Plan generative AI cloud deployment with practical controls for inference spend, latency, scaling, observability and safe releases.",
        "image": "images/blog-genai-cloud-operations-2026.webp", "kind": "article",
        "datePublished": "2026-09-26",
    },
    "a2a-agent-interoperability-2026": {
        "title": "A2A Protocol in 2026: Multi-Agent AI Integration",
        "description": "Understand the 2026 A2A Protocol v1.0 and plan secure multi-agent integration with capability discovery, task boundaries and contract tests.",
        "image": "images/blog-a2a-agent-interoperability-2026.webp", "kind": "article",
        "datePublished": "2026-09-26",
    },
}

# Meaningful page-level headings; service headings are promoted from the existing hero copy.
HEADINGS = {
    "404": "Page not found",
    "blogs": "Software, AI & Digital Product Insights",
    "contact": "Contact BlueByte IT Solutions",
    "portfolio": "Selected Digital Product Work",
    "case-studies": "Client Case Studies",
    "agentic-ai-autonomous-systems-it-service-providers": "Agentic AI and Autonomous Systems: A Practical Guide",
    "top-frontend-technologies-to-use-in-2026": "Frontend Technologies to Consider in 2026",
    "mcp-enterprise-integrations-2026": "MCP Enterprise Integrations: A Security-First Guide",
    "rag-enterprise-ai-search-2026": "RAG for Enterprise AI Search: A Practical Build Guide",
    "llm-testing-quality-engineering-2026": "LLM Testing and Quality Engineering: A 2026 Guide",
    "genai-cloud-operations-2026": "Generative AI Cloud Operations: Cost and Reliability",
    "a2a-agent-interoperability-2026": "A2A Protocol in 2026: A Practical Integration Guide",
}


def replace_attr(tag: str, name: str, value: str) -> str:
    escaped = html.escape(value, quote=True)
    pattern = re.compile(rf'\b{re.escape(name)}\s*=\s*(["\']).*?\1', re.I | re.S)
    if pattern.search(tag):
        return pattern.sub(f'{name}="{escaped}"', tag, count=1)
    return tag[:-1].rstrip() + f' {name}="{escaped}">'


def set_meta(head: str, key: str, value: str, *, prop: bool = False) -> str:
    attr = "property" if prop else "name"
    pattern = re.compile(rf'<meta\b(?=[^>]*\b{attr}\s*=\s*["\']{re.escape(key)}["\'])[^>]*>', re.I)
    match = pattern.search(head)
    if match:
        updated = replace_attr(match.group(0), "content", value)
        return head[:match.start()] + updated + head[match.end():]
    return head.replace("</head>", f'  <meta {attr}="{key}" content="{html.escape(value, quote=True)}">\n</head>', 1)


def page_path(slug: str) -> str:
    return "/" if slug == "index" else f"/{slug}"


def json_ld(slug: str, meta: dict[str, str]) -> str:
    canonical = ORIGIN_TOKEN + ("/" if slug == "index" else f"/{slug}")
    image_url = ORIGIN_TOKEN + "/" + meta["image"]
    org_id = ORIGIN_TOKEN + "/#organization"
    site_id = ORIGIN_TOKEN + "/#website"
    webpage = {
        "@type": "WebPage", "@id": canonical + "#webpage", "url": canonical,
        "name": meta["title"], "description": meta["description"],
        "inLanguage": "en-IN", "isPartOf": {"@id": site_id},
        "primaryImageOfPage": {"@type": "ImageObject", "url": image_url},
    }
    graph: list[dict] = []
    if meta.get("kind") == "home":
        graph.extend([
            {
                "@type": "Organization", "@id": org_id, "name": BRAND,
                "url": ORIGIN_TOKEN + "/", "logo": {
                    "@type": "ImageObject", "url": ORIGIN_TOKEN + "/images/logo.webp",
                },
                "email": "info@bluebyteitinfosystem.com", "telephone": "+91-8178838292",
                "sameAs": [
                    "https://www.facebook.com/profile.php?id=61580436123773",
                    "https://www.linkedin.com/company/110187139",
                    "https://www.instagram.com/bluebyteitsolutions",
                ],
            },
            {
                "@type": "LocalBusiness", "@id": ORIGIN_TOKEN + "/#localbusiness",
                "name": BRAND, "url": ORIGIN_TOKEN + "/", "image": image_url,
                "telephone": "+91-8178838292", "email": "info@bluebyteitinfosystem.com",
                "address": {
                    "@type": "PostalAddress", "streetAddress": "MS 83, Mohan Garden",
                    "addressLocality": "Uttam Nagar", "addressRegion": "Delhi",
                    "postalCode": "110059", "addressCountry": "IN",
                },
            },
            {"@type": "WebSite", "@id": site_id, "url": ORIGIN_TOKEN + "/", "name": BRAND,
             "publisher": {"@id": org_id}, "inLanguage": "en-IN"},
        ])
        webpage["about"] = {"@id": org_id}
    else:
        graph.append({"@type": "Organization", "@id": org_id, "name": BRAND, "url": ORIGIN_TOKEN + "/"})
        if meta.get("kind") == "article":
            article = {
                "@type": "BlogPosting", "@id": canonical + "#article",
                "headline": meta["title"], "description": meta["description"],
                "image": [image_url], "mainEntityOfPage": {"@id": canonical + "#webpage"},
                "author": {"@id": org_id}, "publisher": {"@id": org_id},
                "inLanguage": "en-IN",
            }
            if meta.get("datePublished"):
                article["datePublished"] = meta["datePublished"]
                article["dateModified"] = meta["datePublished"]
            graph.append(article)
        elif meta.get("service"):
            graph.append({
                "@type": "Service", "@id": canonical + "#service",
                "name": meta["service"], "url": canonical,
                "provider": {"@id": org_id}, "areaServed": {"@type": "Country", "name": "India"},
            })
    graph.append(webpage)
    return '<script type="application/ld+json">\n' + json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=2) + "\n</script>"


def promote_or_set_h1(source: str, slug: str) -> str:
    desired = HEADINGS.get(slug)
    # Repair the copied ecommerce article currently published at the agentic-AI URL.
    if slug == "agentic-ai-autonomous-systems-it-service-providers":
        source = re.sub(
            r'(<h1\b[^>]*>).*?(</h1>)',
            r'\1Agentic AI and Autonomous Systems: A Practical Guide\2', source,
            count=1, flags=re.I | re.S,
        )
        source = re.sub(
            r'<p\b([^>]*)>Choosing the best technology for ecommerce.*?</p>',
            r'<p\1>Agentic AI describes software that can work toward a defined goal by interpreting context, choosing from approved tools and taking bounded steps. In IT service operations, a carefully scoped agent may help triage requests, gather diagnostic context or prepare a change for human review. It is not a substitute for clear ownership, tested runbooks or accountable engineers.</p>',
            source, count=1, flags=re.I | re.S,
        )
        source = re.sub(
            r'<p\b([^>]*)>We.ll break down the leading ecommerce platforms.*?</p>',
            r'<p\1>This guide explains how agentic workflows differ from scripts and chat assistants, where autonomy may be useful, and how teams can introduce permissions, approval gates, monitoring and evaluation before connecting an AI system to production tools.</p>',
            source, count=1, flags=re.I | re.S,
        )
        article = re.search(r'<article\b[^>]*>.*?</article>', source, re.I | re.S)
        if article:
            inner = '''<article class="prose dark:prose-invert single-article mb-5">
                  <h2 class="display4-size text-gray-900 fw-600">What makes an AI system agentic?</h2>
                  <p class="text-gray-900 fw-400">A conventional automation follows a known sequence of rules. A conversational assistant responds to a prompt but usually leaves the next action to a person. An agentic system adds a goal-directed loop: it can interpret a task, select from a limited set of tools, observe the result and decide whether another permitted step is needed. The model may help choose actions, but the surrounding software must enforce what it is allowed to do.</p>
                  <h2 class="display4-size text-gray-900 fw-600">Potential IT service management use cases</h2>
                  <p class="text-gray-900 fw-400">A bounded agent can be considered for repetitive, well-documented work such as classifying incoming tickets, collecting information from approved monitoring systems, summarising an incident timeline or drafting a response for an engineer. These are candidate workflows, not guaranteed outcomes. Start with read-only access and human-reviewed recommendations before considering any action that changes a system or affects a customer.</p>
                  <h2 class="display4-size text-gray-900 fw-600">Design permissions and approval gates first</h2>
                  <p class="text-gray-900 fw-400">Give each workflow only the tools and data it needs. Separate read and write permissions, validate tool inputs, restrict access to sensitive records and require explicit approval for high-impact actions. Keep an auditable record of the request, context, tool calls, outputs and human decisions. Define a safe stop or hand-off path for uncertain, conflicting or out-of-scope requests.</p>
                  <h2 class="display4-size text-gray-900 fw-600">Evaluate failure modes, not just successful demos</h2>
                  <p class="text-gray-900 fw-400">Test against representative requests as well as ambiguous, adversarial and incomplete inputs. Measure task completion, factual and routing accuracy, escalation quality, latency, cost and the rate of actions reversed by a human. Re-run the evaluation when prompts, models, tools or source data change. A reliable system should make uncertainty visible and fail safely rather than improvise beyond its permissions.</p>
                  <h2 class="display4-size text-gray-900 fw-600">A practical path to adoption</h2>
                  <p class="text-gray-900 fw-400">Choose one narrow workflow with a clear owner and baseline. Map its data, systems, permissions and exception cases; build a prototype using non-production or read-only integrations; then run it in shadow mode beside the existing process. Expand access only after security, operations and service owners agree on evidence, rollback procedures and ongoing monitoring. For many teams, a conventional script or search assistant will be simpler and safer than an autonomous agent.</p>
                  <h2 class="display4-size text-gray-900 fw-600">Key takeaway</h2>
                  <p class="text-gray-900 fw-400">Treat agentic AI as a controlled software workflow, not an unbounded digital employee. Clear task boundaries, least-privilege tools, human accountability and continuous evaluation are prerequisites for responsibly testing autonomy in IT services.</p>
                </article>'''
            source = source[:article.start()] + inner + source[article.end():]
        # Remove an unrelated, copied ecommerce Article/Breadcrumb/FAQ schema; the build inserts accurate BlogPosting data.
        source = re.sub(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>.*?</script>', '', source, flags=re.I | re.S)
    if len(re.findall(r'<h1\b', source, re.I)):
        if desired and slug not in ("agentic-ai-autonomous-systems-it-service-providers",):
            source = re.sub(r'(<h1\b[^>]*>).*?(</h1>)', lambda m: m.group(1) + html.escape(desired) + m.group(2), source, count=1, flags=re.I | re.S)
        return source
    # The first h2 is the existing visible hero/page heading on these pages. Promote it, preserving its classes.
    if desired:
        text = re.escape(desired)
        # Where a dedicated page heading is supplied, replace the hero copy as well as its level.
        match = re.search(r'<h2\b[^>]*>.*?</h2>', source, re.I | re.S)
        if match and slug in HEADINGS:
            tag = re.sub(r'^<h2\b', '<h1', match.group(0), count=1, flags=re.I)
            tag = re.sub(r'</h2>$', '</h1>', tag, count=1, flags=re.I)
            tag = re.sub(r'(?<=>).*?(?=</h1>)', html.escape(desired), tag, count=1, flags=re.I | re.S)
            return source[:match.start()] + tag + source[match.end():]
    return re.sub(r'<h2\b', '<h1', source, count=1, flags=re.I).replace('</h2>', '</h1>', 1) if re.search(r'<h2\b', source, re.I) else source


def update_page(slug: str, path: Path) -> None:
    meta = PAGES.get(slug)
    if not meta:
        return
    source = path.read_text(encoding="utf-8", errors="replace")
    source = promote_or_set_h1(source, slug)
    # Replace legacy, duplicated or mismatched embedded schemas with one source of truth.
    source = re.sub(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>.*?</script>\s*', '', source, flags=re.I | re.S)
    source = re.sub(r'(<html\b[^>]*\blang=["\'])[^"\']*(["\'])', r'\1en-IN\2', source, count=1, flags=re.I)
    source = source.replace("The best technolgy for ecommerce in 2026", "The best technology for eCommerce in 2026")
    source = source.replace("The best technolgy for ecommerce", "The best technology for eCommerce")
    source = source.replace("Choosing the Right Frontend Technology in 2025", "Choosing the Right Frontend Technology in 2026")
    source = source.replace("About Bluebyte IT Solutions", "About BlueByte IT Solutions")
    if slug == "agentic-ai-autonomous-systems-it-service-providers":
        def repair_ai_image(match: re.Match[str]) -> str:
            tag = match.group(0)
            tag = re.sub(r'\bsrc="[^"]+"', 'src="images/agentic-ai-operations.webp"', tag, count=1)
            tag = re.sub(r'\balt="[^"]*"', 'alt="IT engineer overseeing a governed AI workflow"', tag, count=1)
            tag = re.sub(r'\bwidth="[^"]*"', 'width="1264"', tag, count=1)
            tag = re.sub(r'\bheight="[^"]*"', 'height="848"', tag, count=1)
            return tag
        source = re.sub(r'<img\b[^>]*src="images/(?:blog-ecommerce-stack|agentic-ai-operations)\.webp"[^>]*>', repair_ai_image, source, count=1, flags=re.I)
    if slug == "best-technology-for-ecommerce-in-2026":
        source = source.replace('src="images/agentic-ai-operations.webp" alt="IT engineer overseeing a governed AI workflow"', 'src="images/blog-ecommerce-stack.webp" alt="The best technology for eCommerce in 2026"')
        source = source.replace(
            "We'll break down the leading ecommerce platforms that are winning in 2025 and explore how AI and machine learning tools are helping stores boost their revenue.",
            "We compare common platform approaches and explore how AI-assisted discovery, product data, mobile experiences and payment choices affect an online store's architecture and operations.",
        )
    if slug == "top-frontend-technologies-to-use-in-2026":
        current_and_replacements = {
            "The frontend\n          landscape is evolving at lightning speed, and 2025 is no exception. Businesses and developers alike are\n          seeking faster, scalable, and more user-friendly web experiences. Whether you're building a corporate website,\n          SaaS product, or eCommerce platform, the right frontend technology stack can make or break your digital\n          success.": "Frontend tools and rendering approaches continue to evolve. For 2026 projects, choose technology by evaluating page rendering needs, accessibility, performance budgets, team experience and long-term maintenance—not by popularity alone.",
            "As a full-stack\n          developer and digital strategist, I've analyzed the most impactful frameworks, libraries, and tools that will\n          dominate in 2025. Here's an expert breakdown to help you future-proof your projects.": "This guide compares several widely used options and explains the trade-offs to review before adopting them. Confirm current framework versions, support policies and hosting requirements against the official project documentation before committing.",
            "React has been leading the frontend world for years, and in 2025, it continues to hold strong. With its component-based architecture, virtual DOM, and huge ecosystem, React is perfect for building interactive and SEO-friendly web applications. Backed by Meta and a massive developer community, React remains the go-to choice for startups and enterprises.": "React is a JavaScript library for building component-based interfaces. Its ecosystem and flexible rendering choices can suit interactive products, but teams should decide how routing, server rendering, data loading and accessibility will be handled rather than assuming the library provides every feature by itself.",
            "Why React in 2025?": "When React Fits",
            "Angular, powered by Google, is thriving in 2025 for large-scale and enterprise-level applications. Its TypeScript-first approach, structured architecture, and built-in features make it highly reliable. Businesses focusing on robust security, scalability, and maintainability continue to choose Angular.": "Angular is a TypeScript-based application framework with conventions and tooling for larger applications. Its integrated approach can help teams that value a structured framework; weigh its learning curve, release cadence and ecosystem against the needs of your project.",
            "Why Angular in 2025?": "When Angular Fits",
            "Vue.js is lightweight, developer-friendly, and loved for its simplicity. In 2025, Vue is gaining more adoption thanks to its progressive architecture that allows developers to integrate it gradually. Vue is excellent for businesses aiming at cost-effective, performance-focused solutions without compromising user experience.": "Vue can be adopted progressively, from small interface enhancements to larger applications. Consider the skills already on your team, the ecosystem choices you need and how the application will be tested and maintained.",
            "Why Vue.js in 2025?": "When Vue Fits",
            "Svelte is disrupting the frontend world by compiling code at build time, which results in faster performance and smaller bundle sizes. With SvelteKit maturing in 2025, developers can now build scalable apps with SSR and routing built-in.": "Svelte uses a compiler-based approach to generate interface code, while SvelteKit adds application features such as routing and server rendering. Measure the output and runtime behaviour of your own pages; performance depends on implementation and content, not framework choice alone.",
            "Why Svelte in 2025?": "When Svelte Fits",
            "While React is a library, Next.js has emerged as the framework of choice in 2025 for server-side rendering (SSR), static site generation (SSG), and SEO optimization. Businesses looking to dominate Google rankings are increasingly choosing Next.js.": "Next.js is a React framework with server-rendering and static-generation options. It may fit projects that need those delivery models, but search visibility still depends on useful content, crawlable pages, technical quality and user experience—not the framework alone.",
            "Why Next.js in 2025?": "When Next.js Fits",
            "Astro is designed for content-heavy sites like blogs, eCommerce, and marketing websites. By default, it ships zero JavaScript to the browser, making websites blazing fast. In 2025, Astro is growing rapidly as brands prioritize speed, SEO, and accessibility.": "Astro is designed for content-focused sites and can keep client-side JavaScript limited when pages do not need interactive components. Review its integrations, rendering model and deployment constraints before choosing it for an application with substantial client-side behaviour.",
            "Why Astro in 2025?": "When Astro Fits",
            "No frontend stack is complete without CSS, and Tailwind CSS remains the most developer-loved framework in 2025. With its utility-first approach, Tailwind helps developers build modern, responsive, and consistent UIs faster than ever.": "Tailwind CSS is a utility-first styling framework. It can suit teams that prefer composing styles from classes, provided the project establishes clear component conventions, accessibility checks and a maintainable design system.",
            "Why Tailwind CSS in 2025?": "When Tailwind CSS Fits",
            "The best frontend technology in 2025 depends on your business goals:": "A practical 2026 choice depends on your product requirements:",
            "Want speed and SEO -> Next.js or Astro": "Content-focused pages with little client interaction -> Astro or static rendering",
            "Need enterprise reliability -> Angular": "A structured TypeScript application framework -> Angular",
            "Seeking flexibility and simplicity -> Vue or Svelte": "Progressive adoption or a compiler-based approach -> Vue or Svelte",
            "Looking for global adoption and talent pool -> React": "An existing React team needing server-rendered routes -> React with a suitable framework",
            "We recommend focusing not just on framework popularity, but also on scalability, SEO impact, and long-term maintainability. A future-proof frontend choice ensures better customer engagement, higher search rankings, and stronger ROI. By aligning your business goals with the right frontend stack, you're not just building a website - <strong>you're building a digital experience that lasts</strong>. ": "Compare accessibility, real-user performance, bundle size, rendering requirements, hosting, security updates and team familiarity in a small prototype. No framework guarantees search rankings or return on investment; the right choice is the one your team can operate and improve for your users.",
            '<a href="https://www.apsense.com/user/anoopuri21" class="btn btn-primary">Check Other blog</a>': '<a href="blogs.html" class="btn btn-primary">More articles from BlueByte</a>',
        }
        for old, new in current_and_replacements.items():
            source = source.replace(old, new)
    if slug == "blogs" and "agentic-ai-autonomous-systems-it-service-providers.html" not in source:
        card = '''
            <div class="col-lg-4" data-aos="fade-up" data-aos-duration="400" data-aos-delay="200">
              <a href="agentic-ai-autonomous-systems-it-service-providers.html" class="border border-gray-200 rounded-4 overflow-hidden d-flex flex-column shadow-hover-lg">
                <div class="post-image overflow-hidden"><img loading="lazy" src="images/agentic-ai-operations.webp" alt="IT engineer overseeing a governed AI workflow" class="w-100 img-fluid scale-img"></div>
                <div class="post-content p-3"><div class="d-flex flex-column px-1">
                  <h2 class="display4-size text-gray-900 fw-600 mb-1">Agentic AI and Autonomous Systems: A Practical Guide</h2>
                  <p class="text-gray-900 fw-400 text-gray-700 mt-1 pe-lg-5">A practical guide to bounded autonomy, permissions, human approval and evaluation for IT service workflows.</p>
                </div></div>
              </a>
            </div>'''
        source = source.replace('<div class="row gy-4">', '<div class="row gy-4">' + card, 1)
    source = re.sub(r'&copy;\s*2025', '&copy; 2026', source, flags=re.I)

    head_match = re.search(r'<head\b[^>]*>.*?</head>', source, re.I | re.S)
    if not head_match:
        raise ValueError(f"No <head> found in {path.name}")
    head = head_match.group(0)
    head = re.sub(r'<title\b[^>]*>.*?</title>', f'<title>{html.escape(meta["title"])}</title>', head, count=1, flags=re.I | re.S)
    head = re.sub(r'<meta\b(?=[^>]*\bname\s*=\s*["\']keywords["\'])[^>]*>\s*', '', head, flags=re.I)
    head = re.sub(r'<link\b(?=[^>]*\brel\s*=\s*["\']alternate["\'])[^>]*>\s*', '', head, flags=re.I)
    head = re.sub(r'<meta\b(?=[^>]*\bname\s*=\s*["\']msapplication-(?:config|TileImage)["\'])[^>]*>\s*', '', head, flags=re.I)
    head = re.sub(r'<meta\b(?=[^>]*\bproperty\s*=\s*["\'](?:og:image:secure_url|og:image:width|og:image:height|twitter:image|og:url)["\'])[^>]*>\s*', '', head, flags=re.I)
    head = re.sub(r'<meta\b(?=[^>]*\bname\s*=\s*["\'](?:twitter:site|twitter:creator)["\'])[^>]*>\s*', '', head, flags=re.I)
    head = re.sub(r'<link\b(?=[^>]*\bproperty\s*=\s*["\']image_src["\'])[^>]*>\s*', '', head, flags=re.I)
    head = re.sub(r'<link\b(?=[^>]*\brel\s*=\s*["\']canonical["\'])[^>]*>\s*', '', head, flags=re.I)
    head = re.sub(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>.*?</script>\s*', '', head, flags=re.I | re.S)
    head = set_meta(head, "description", meta["description"])
    head = set_meta(head, "robots", "noindex,follow" if slug == "404" else "index,follow")
    head = set_meta(head, "author", BRAND)
    head = set_meta(head, "google-analytics-id", GA_TOKEN)
    head = set_meta(head, "og:type", "article" if meta.get("kind") == "article" else "website", prop=True)
    head = set_meta(head, "og:locale", "en_IN", prop=True)
    head = set_meta(head, "og:title", meta["title"], prop=True)
    head = set_meta(head, "og:description", meta["description"], prop=True)
    head = set_meta(head, "og:site_name", BRAND, prop=True)
    head = set_meta(head, "og:image", ORIGIN_TOKEN + "/" + meta["image"], prop=True)
    head = set_meta(head, "twitter:card", "summary_large_image")
    head = set_meta(head, "twitter:title", meta["title"])
    head = set_meta(head, "twitter:description", meta["description"])
    head = set_meta(head, "twitter:image", ORIGIN_TOKEN + "/" + meta["image"])
    if slug != "404":
        canonical = ORIGIN_TOKEN + ("/" if slug == "index" else f"/{slug}")
        head = head.replace("</head>", f'  <link rel="canonical" href="{canonical}">\n</head>', 1)
        head = set_meta(head, "og:url", canonical, prop=True)
    # Local files stay same-origin and work unchanged on preview, staging and custom domains.
    head = head.replace("https://www.bluebyteitsolutions.com/", "/")
    head = re.sub(r'<link\b(?=[^>]*\brel\s*=\s*["\'](?:shortcut icon|icon)["\'])[^>]*>', '<link rel="icon" href="/images/favicon.png" type="image/png">', head, count=1, flags=re.I)
    head = re.sub(r'<link\b(?=[^>]*\bhref=["\']/(?:fonts/Sora-700|fonts/dm-sans-400)\.woff2["\'])[^>]*>\s*', '', head, flags=re.I)
    head = head.replace("</head>", '  <link rel="preload" href="/fonts/Sora-700.woff2" as="font" type="font/woff2" crossorigin>\n  <link rel="preload" href="/fonts/dm-sans-400.woff2" as="font" type="font/woff2" crossorigin>\n</head>', 1)
    if slug == "index":
        # The hero video poster is the LCP fallback. Preload the local file, not the social card on a fixed host.
        head = re.sub(r'<link\b(?=[^>]*\bas\s*=\s*["\']image["\'])[^>]*>', '', head, flags=re.I)
        head = head.replace("</head>", '  <link rel="preload" as="image" href="/images/og-image.webp" fetchpriority="high">\n</head>', 1)
    elif meta.get("service"):
        head = head.replace("https://www.bluebyteitsolutions.com/images/banner-bg-1.webp", "/images/banner-bg-1.webp")
    if slug != "404":
        head = head.replace("</head>", json_ld(slug, meta) + "\n</head>", 1)
    source = source[:head_match.start()] + head + source[head_match.end():]
    # SEO document URLs need an absolute configured origin; clickable site navigation stays same-origin.
    source = source.replace("https://www.bluebyteitsolutions.com", ORIGIN_TOKEN)
    source = re.sub(
        r'(<a\b[^>]*\bhref=["\'])' + re.escape(ORIGIN_TOKEN) + r'(/[^"\']*)(["\'])',
        r'\1\2\3', source, flags=re.I,
    )
    # Repair malformed anchors left by the previous transformation before securing external links.
    source = re.sub(
        r'<\s+rel=["\']noopener noreferrer["\']>\s+href=["\']([^"\']+)["\']([^>]*)>',
        lambda m: f'<a href="{m.group(1)}"{m.group(2)} rel="noopener noreferrer">',
        source, flags=re.I,
    )
    def secure_blank_anchor(match: re.Match[str]) -> str:
        tag = match.group(0)
        if re.search(r'\btarget=["\']_blank["\']', tag, re.I) and not re.search(r'\brel=', tag, re.I):
            return tag[:-1] + ' rel="noopener noreferrer">'
        return tag
    source = re.sub(r'<a\b[^>]*>', secure_blank_anchor, source, flags=re.I)
    # Keep the floating WhatsApp control self-contained so the icon never depends on a third-party image host.
    whatsapp_icon = '''<svg width="32" height="32" viewBox="0 0 32 32" aria-hidden="true" focusable="false"><path d="M16 3.5a12.2 12.2 0 0 0-10.5 18.4L4 28l6.3-1.6A12.2 12.2 0 1 0 16 3.5Z" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/><path d="M11.2 9.3c-.4-.8-.8-.8-1.2-.8h-.8c-.3 0-.7.1-1 .5-.4.4-1.3 1.3-1.3 3.1s1.3 3.6 1.5 3.8c.2.3 2.6 4.1 6.4 5.6 3.1 1.2 3.8 1 4.5.9.7-.1 2.3-.9 2.6-1.8.3-.9.3-1.6.2-1.8-.1-.2-.4-.3-.8-.5-.4-.2-2.3-1.1-2.7-1.2-.4-.1-.6-.2-.9.2-.3.4-1 1.2-1.2 1.5-.2.3-.4.3-.8.1-.4-.2-1.6-.6-3.1-1.9-1.1-1-1.9-2.3-2.1-2.7-.2-.4 0-.6.2-.8.2-.2.4-.5.6-.7.2-.2.3-.4.4-.6.1-.3 0-.5 0-.7-.1-.2-.9-2.1-1.2-2.8Z" fill="#fff"/></svg>'''
    source = re.sub(
        r'(<a\b(?=[^>]*\bclass=["\'][^"\']*\bwhatsapp-float\b[^"\']*["\'])[^>]*>)\s*<img\b[^>]*>\s*</a>',
        lambda m: m.group(1) + whatsapp_icon + '</a>',
        source, flags=re.I | re.S,
    )
    source = re.sub(r"[ \t]+(?=\r?$)", "", source, flags=re.M)
    path.write_text(source, encoding="utf-8")


IMAGE_DIMENSIONS: dict[str, tuple[int, int]] = {}


def append_attribute(tag: str, name: str, value: str) -> str:
    closing = "/>" if re.search(r"\s*/>$", tag) else ">"
    body = tag[:-2].rstrip() if closing == "/>" else tag[:-1].rstrip()
    return f'{body} {name}="{value}"{closing}'


def add_image_dimensions(path: Path) -> None:
    source = path.read_text(encoding="utf-8", errors="replace")
    def update(match: re.Match[str]) -> str:
        tag = match.group(0)
        src_match = re.search(r'\bsrc\s*=\s*(["\'])(.*?)\1', tag, re.I | re.S)
        if not src_match or not src_match.group(2).startswith("images/"):
            return tag
        asset_name = src_match.group(2).split("?", 1)[0]
        if asset_name not in IMAGE_DIMENSIONS:
            asset = ROOT / asset_name
            if not asset.is_file():
                return tag
            try:
                values = subprocess.run(["identify", "-ping", "-format", "%w %h", str(asset)], capture_output=True, text=True, timeout=4, check=True).stdout.split()
                IMAGE_DIMENSIONS[asset_name] = (int(values[0]), int(values[1]))
            except (OSError, subprocess.SubprocessError, ValueError, IndexError):
                return tag
        width, height = IMAGE_DIMENSIONS[asset_name]
        if not re.search(r'\bwidth\s*=', tag, re.I):
            tag = append_attribute(tag, "width", str(width))
        if not re.search(r'\bheight\s*=', tag, re.I):
            tag = append_attribute(tag, "height", str(height))
        if re.search(r'\bdecoding\s*=', tag, re.I):
            tag = re.sub(r'\bdecoding\s*=\s*["\'][^"\']*["\']', 'decoding="async"', tag, count=1, flags=re.I)
        else:
            tag = append_attribute(tag, "decoding", "async")
        return tag
    updated = re.sub(r'<img\b[^>]*>', update, source, flags=re.I | re.S)
    if updated != source:
        path.write_text(updated, encoding="utf-8")


def render_crawl_files(origin: str) -> tuple[str, str, str]:
    entries = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for slug in sorted(PAGES):
        if slug == "404":
            continue
        loc = origin + ("/" if slug == "index" else f"/{slug}")
        entries.extend(["  <url>", f"    <loc>{html.escape(loc)}</loc>", "  </url>"])
    entries.append("</urlset>")
    robots = "User-agent: *\nAllow: /\nDisallow: /private/\nDisallow: /temp/\n\n" + f"Sitemap: {origin}/sitemap.xml\n"
    redirects = [
        "/best-technolgy-for-ecommerce-in-2025 /best-technology-for-ecommerce-in-2026 301",
        "/best-technology-for-ecommerce-in-2025 /best-technology-for-ecommerce-in-2026 301",
        "/top-frontend-technologies-to-use-in-2025 /top-frontend-technologies-to-use-in-2026 301",
        "/best-technolgy-for-ecommerce-in-2025.html /best-technology-for-ecommerce-in-2026 301",
        "/best-technology-for-ecommerce-in-2025.html /best-technology-for-ecommerce-in-2026 301",
        "/top-frontend-technologies-to-use-in-2025.html /top-frontend-technologies-to-use-in-2026 301",
        "/index.html / 301",
    ]
    redirects.extend(f"/{slug}.html /{slug} 301" for slug in sorted(PAGES) if slug not in {"404", "index"})
    return "\n".join(entries) + "\n", robots, "\n".join(redirects) + "\n"


def apply_sources() -> None:
    for path in sorted(ROOT.glob("*.html")):
        slug = path.stem
        if slug == "404":
            PAGES[slug] = {
                "title": "Page Not Found | BlueByte IT Solutions",
                "description": "The page you requested could not be found. Visit BlueByte IT Solutions to explore our software, web development and digital product services.",
                "image": "images/og-image.webp",
            }
        if slug in PAGES:
            update_page(slug, path)
            add_image_dimensions(path)
    sitemap, robots, redirects = render_crawl_files(ORIGIN_TOKEN)
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (ROOT / "robots.txt").write_text(robots, encoding="utf-8")
    (ROOT / "_redirects").write_text(redirects, encoding="utf-8")
    # Set the canonical host only in one environment-backed build setting, not in server redirects.
    htaccess = ROOT / ".htaccess"
    if htaccess.exists():
        text = htaccess.read_text(encoding="utf-8", errors="replace")
        text = re.sub(
            r"# 1\. Canonicalization: Force HTTPS \+ www.*?RewriteRule \^ https://www\.bluebyteitsolutions\.com%\{REQUEST_URI\} \[L,R=301\]",
            "# 1. Canonicalization: Force HTTPS while preserving the configured host\nRewriteCond %{HTTPS} off [OR]\nRewriteCond %{HTTP:X-Forwarded-Proto} !https [NC]\nRewriteCond %{REQUEST_URI} !^/\\.well-known/(acme-challenge|cpanel-dcv|pki-validation)/ [NC]\nRewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]",
            text, flags=re.S,
        )
        text = re.sub(
            r"# Fix typo URL variant\nRewriteRule .*?\n",
            "# Redirect the retired 2025 misspellings and slugs to the current article URLs\nRewriteRule ^best-technolgy-for-ecommerce-in-2025/?$ /best-technology-for-ecommerce-in-2026 [R=301,L,NC]\nRewriteRule ^best-technology-for-ecommerce-in-2025/?$ /best-technology-for-ecommerce-in-2026 [R=301,L,NC]\nRewriteRule ^top-frontend-technologies-to-use-in-2025/?$ /top-frontend-technologies-to-use-in-2026 [R=301,L,NC]\n",
            text, count=1, flags=re.S,
        )
        text = text.replace("RewriteCond %{HTTPS} off [OR]\nRewriteCond %{HTTP:X-Forwarded-Proto} !https [NC]", "RewriteCond %{HTTPS} off\nRewriteCond %{HTTP:X-Forwarded-Proto} !https [NC]")
        text = text.replace("max-age=31536000, public, immutable", "max-age=604800, public, stale-while-revalidate=86400")
        htaccess.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))
    # The standalone JSON-LD file is retained for consumers, without unsupported review/rating markup.
    graph = json_ld("index", PAGES["index"])
    schema_text = re.sub(r'<script[^>]*>(.*?)</script>', r'\1', graph, flags=re.S).strip()
    (ROOT / "schema.jsonld").write_text(schema_text + "\n", encoding="utf-8")
    # Make both LLM discovery files use the same configurable preferred URLs as the build.
    for path in (ROOT / "llms.txt", ROOT / ".well-known" / "llms.txt", ROOT / "knowledge"):
        if path.exists():
            text = path.read_text(encoding="utf-8", errors="replace")
            text = text.replace("https://www.bluebyteitsolutions.com", ORIGIN_TOKEN)
            path.write_text(text, encoding="utf-8")


def validate_site_url() -> str:
    value = os.environ.get("SITE_URL", "").strip().rstrip("/")
    parsed = urlparse(value)
    if not value or parsed.scheme not in {"https", "http"} or not parsed.netloc or parsed.path:
        raise SystemExit("Set SITE_URL to the canonical origin, e.g. SITE_URL=https://www.example.com")
    if any(char in value for char in "<>\"' "):
        raise SystemExit("SITE_URL must be a valid origin without spaces or quotes")
    return value


def build() -> None:
    origin = validate_site_url()
    apply_sources()
    if DIST.exists():
        shutil.rmtree(DIST)
    ignored = shutil.ignore_patterns(".git", ".wrangler", "dist", "node_modules", "__pycache__", ".env", ".env.*", "scripts")
    shutil.copytree(ROOT, DIST, ignore=ignored)
    ga_id = os.environ.get("GA_MEASUREMENT_ID", "").strip()
    if ga_id and not re.fullmatch(r"G-[A-Z0-9]+", ga_id):
        raise SystemExit("GA_MEASUREMENT_ID must look like G-XXXXXXXXXX")
    for path in DIST.rglob("*"):
        if not path.is_file() or path.suffix.lower() in {".webp", ".png", ".jpg", ".jpeg", ".gif", ".mp4", ".webm", ".woff", ".woff2", ".ttf", ".eot"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if ORIGIN_TOKEN in text or GA_TOKEN in text:
            path.write_text(text.replace(ORIGIN_TOKEN, origin).replace(GA_TOKEN, ga_id), encoding="utf-8")
    sitemap = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for page in sorted(PAGES):
        if page == "404":
            continue
        loc = origin + ("/" if page == "index" else f"/{page}")
        sitemap.extend(["  <url>", f"    <loc>{html.escape(loc)}</loc>", "  </url>"])
    sitemap.append("</urlset>")
    (DIST / "sitemap.xml").write_text("\n".join(sitemap) + "\n", encoding="utf-8")
    (DIST / "robots.txt").write_text(
        "User-agent: *\nAllow: /\nDisallow: /private/\nDisallow: /temp/\n\n"
        f"Sitemap: {origin}/sitemap.xml\n", encoding="utf-8"
    )
    print(f"Built {sum(1 for p in DIST.glob('*.html') if p.stem != '404')} indexable pages for {origin} -> {DIST.relative_to(ROOT)}")
    check()


def check() -> None:
    if not DIST.is_dir():
        raise SystemExit("dist/ is missing; run the build command first")
    if not os.environ.get("SITE_URL") and (DIST / "index.html").is_file():
        built_index = (DIST / "index.html").read_text(encoding="utf-8", errors="replace")
        built_canonical = re.search(r"<link\b(?=[^>]*\brel=[\"']canonical[\"'])[^>]*\bhref=[\"']([^\"']*)", built_index, re.I)
        if built_canonical:
            parsed = urlparse(built_canonical.group(1))
            if parsed.scheme and parsed.netloc:
                os.environ["SITE_URL"] = f"{parsed.scheme}://{parsed.netloc}"
    problems: list[str] = []
    pages = sorted(p for p in DIST.glob("*.html") if p.stem != "404")
    expected = {page for page in PAGES if page != "404"}
    if {p.stem for p in pages} != expected:
        problems.append("The indexable HTML page set does not match the SEO manifest")
    for path in pages:
        text = path.read_text(encoding="utf-8", errors="replace")
        title = re.search(r"<title>(.*?)</title>", text, re.I | re.S)
        description = re.search(r'<meta\b(?=[^>]*\bname=["\']description["\'])[^>]*\bcontent=["\']([^"\']*)', text, re.I)
        canonical = re.search(r'<link\b(?=[^>]*\brel=["\']canonical["\'])[^>]*\bhref=["\']([^"\']*)', text, re.I)
        og_urls = re.findall(r'<meta\b(?=[^>]*\bproperty=["\']og:url["\'])[^>]*\bcontent=["\']([^"\']*)', text, re.I)
        h1_count = len(re.findall(r"<h1\b", text, re.I))
        schemas = re.findall(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', text, re.I | re.S)
        if not title or not title.group(1).strip():
            problems.append(f"{path.name}: missing title")
        if not description or len(html.unescape(description.group(1)).strip()) < 50:
            problems.append(f"{path.name}: missing/short meta description")
        if not canonical or not canonical.group(1).startswith(os.environ.get("SITE_URL", "https://www.bluebyteitsolutions.com").rstrip("/")):
            problems.append(f"{path.name}: missing or wrong canonical")
        if len(og_urls) != 1 or (canonical and og_urls and og_urls[0] != canonical.group(1)):
            problems.append(f"{path.name}: og:url must match the canonical URL exactly once")
        if re.search(r'<a\b[^>]*\bhref=["\']' + re.escape(validate_site_url()) + r'(?:/|["\'])', text, re.I):
            problems.append(f"{path.name}: internal navigation should remain same-origin paths")
        if h1_count != 1:
            problems.append(f"{path.name}: expected one H1, found {h1_count}")
        for block in schemas:
            try:
                json.loads(block)
            except json.JSONDecodeError as exc:
                problems.append(f"{path.name}: invalid JSON-LD ({exc})")
        if "{{SITE_URL}}" in text or "{{GA_MEASUREMENT_ID}}" in text:
            problems.append(f"{path.name}: unresolved build token")
        # Relative/local asset paths referenced in source markup must exist in the built output.
        for attr in ("src", "href", "poster"):
            for ref in re.findall(rf'\b{attr}=["\']([^"\']+)', text, re.I):
                if ref.startswith(("http://", "https://", "//", "#", "mailto:", "tel:", "data:", "javascript:")):
                    continue
                path_part = ref.split("#", 1)[0].split("?", 1)[0]
                if not path_part or path_part.startswith("/") and not path_part.startswith("//"):
                    path_part = path_part.lstrip("/")
                if path_part and not (DIST / path_part).is_file() and not re.fullmatch(r"[a-z][a-z0-9+.-]*:", path_part, re.I):
                    # Ignore same-page fragment-only references and extensionless HTML routes.
                    if not Path(path_part).suffix and (DIST / (path_part + ".html")).is_file():
                        continue
                    problems.append(f"{path.name}: missing local {attr} {ref}")
    try:
        sitemap_root = ET.parse(DIST / "sitemap.xml").getroot()
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = [n.text for n in sitemap_root.findall("s:url/s:loc", ns)]
        if len(locs) != len(pages):
            problems.append(f"sitemap has {len(locs)} URLs, expected {len(pages)}")
        for loc in locs:
            if not loc or not loc.startswith(validate_site_url()):
                problems.append(f"sitemap has non-canonical URL: {loc}")
    except (ET.ParseError, OSError) as exc:
        problems.append(f"invalid sitemap.xml: {exc}")
    if "Sitemap: " + validate_site_url() + "/sitemap.xml" not in (DIST / "robots.txt").read_text(encoding="utf-8"):
        problems.append("robots.txt does not point to the built sitemap")
    if problems:
        print("SEO validation failed:", file=sys.stderr)
        for problem in problems:
            print(f" - {problem}", file=sys.stderr)
        raise SystemExit(1)
    print(f"SEO checks passed: {len(pages)} pages, canonical URLs, one H1/page, valid JSON-LD, local assets and sitemap.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("apply", "build", "check"), help="apply source SEO, build dist, or audit dist")
    args = parser.parse_args()
    if args.command == "apply":
        apply_sources()
        print("Applied page metadata, content and performance fixes to source HTML.")
    elif args.command == "build":
        build()
    else:
        check()


if __name__ == "__main__":
    main()
