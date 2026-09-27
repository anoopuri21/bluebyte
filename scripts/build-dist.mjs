#!/usr/bin/env node
/**
 * Build script for the Cloudflare Workers deployment.
 *
 * This repository is a hand-written static HTML site that lives at the
 * repository root. There is no bundler, so "building" simply means assembling
 * the publishable files into ./dist, which is the directory named by
 * `assets.directory` in wrangler.jsonc.
 *
 * `wrangler deploy` runs this automatically via the `build.command` setting,
 * so `npx wrangler deploy` is enough - no separate build command has to be
 * configured in Cloudflare Workers Builds.
 *
 * The copy is deliberately conservative: everything at the repo root is copied
 * EXCEPT the entries in IGNORE below and any dotfile/dot-directory that is not
 * explicitly allow-listed. That keeps new pages and assets flowing to
 * production automatically while never publishing .git, .env, .dev.vars or
 * server-side code.
 *
 * It also appends a Cache-Control rule per HTML page to dist/_headers, which
 * cannot live on the /* block - see appendHtmlCacheRules() below.
 *
 * Build tokens {{SITE_URL}} and {{GA_MEASUREMENT_ID}} in the source markup are
 * resolved here, on the copies in dist/ only (the source keeps the tokens).
 * Override them per build without editing this file:
 *
 *   SITE_URL=https://www.bluebyteitsolutions.com \
 *   GA_MEASUREMENT_ID=G-XXXXXXXXXX \
 *   npx wrangler deploy
 *
 * In Cloudflare Workers Builds those go in the project's *build* environment
 * variables, not in .dev.vars and not in wrangler.jsonc.
 *
 * Requires Node 16.7+ (uses fs.cpSync). No dependencies.
 */

import {
  appendFileSync,
  cpSync,
  existsSync,
  readFileSync,
  rmSync,
  readdirSync,
  writeFileSync,
} from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const DIST = path.join(ROOT, "dist");

/**
 * Build tokens left in the source markup. `scripts/seo.py apply` deliberately
 * rewrites the real origin back into {{SITE_URL}}, so the tokens are the source
 * of truth and get resolved here, at build time, on the copies in dist/.
 */
const ORIGIN_TOKEN = "{{SITE_URL}}";
const GA_TOKEN = "{{GA_MEASUREMENT_ID}}";

/** Canonical origin. Override per-build with SITE_URL=https://your.domain */
const DEFAULT_SITE_URL = "https://bluebyteitinfosystem.com";

/** Google Analytics measurement ID. Empty means analytics stays off, which is
 *  what js/analytics.js expects when no valid G-XXXX id is present. */
const DEFAULT_GA_MEASUREMENT_ID = "";

/** Repo-root entries that must never be published. */
const IGNORE = new Set([
  // Output directory itself
  "dist",
  // Wrangler / deploy configuration
  "wrangler.jsonc",
  "wrangler.toml",
  "wrangler.json",
  "wrangler.json5",
  // Node / tooling
  "node_modules",
  "package.json",
  "package-lock.json",
  ".wrangler",
  // Build + SEO tooling (not part of the site)
  "scripts",
  // Worker source (deployed separately by wrangler as the Worker bundle)
  "src",
  // Server-side code that Cloudflare Workers cannot execute.
  // Publishing it would also expose the PHP source on the internet.
  "contactform.php",
  // Apache-only configuration, meaningless on Workers
  ".htaccess",
]);

/**
 * Dotfiles/dot-directories are skipped unless listed here. Fail-closed: a new
 * secret-looking file (.env.local, .dev.vars, .npmrc, ...) can never leak just
 * because it was dropped in the repo root.
 */
const DOT_ALLOW = new Set([".well-known"]);

function shouldCopy(name) {
  if (IGNORE.has(name)) return false;
  if (name.startsWith(".")) return DOT_ALLOW.has(name);
  return true;
}

/** Mirrors scripts/seo.py's validate_site_url(): origin only, no trailing slash. */
function resolveSiteUrl() {
  const raw = (process.env.SITE_URL || DEFAULT_SITE_URL).trim().replace(/\/+$/, "");
  if (/[<>"'\s]/.test(raw)) {
    throw new Error("[build-dist] SITE_URL must not contain spaces or quotes");
  }

  let parsed;
  try {
    parsed = new URL(raw);
  } catch {
    throw new Error(`[build-dist] SITE_URL is not a valid origin: "${raw}"`);
  }
  if (parsed.protocol !== "https:" && parsed.protocol !== "http:") {
    throw new Error(`[build-dist] SITE_URL must start with https:// or http:// (got "${raw}")`);
  }
  if (!parsed.hostname) {
    throw new Error(`[build-dist] SITE_URL is missing a hostname: "${raw}"`);
  }
  if (parsed.pathname && parsed.pathname !== "/") {
    throw new Error(`[build-dist] SITE_URL must be an origin with no path (got "${raw}")`);
  }
  return raw;
}

function resolveGaId() {
  const raw = (process.env.GA_MEASUREMENT_ID || DEFAULT_GA_MEASUREMENT_ID).trim();
  if (raw && !/^G-[A-Z0-9]+$/.test(raw)) {
    throw new Error(`[build-dist] GA_MEASUREMENT_ID must look like G-XXXXXXXXXX (got "${raw}")`);
  }
  return raw;
}

function* walk(dir) {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) yield* walk(full);
    else if (entry.isFile()) yield full;
  }
}

/**
 * Resolve {{SITE_URL}} / {{GA_MEASUREMENT_ID}} in every text file under dist/.
 *
 * Files are read as buffers and only decoded when they actually contain a
 * token, so images, fonts and video are never rewritten.
 */
function substituteTokens(origin, gaId) {
  const needles = [Buffer.from(ORIGIN_TOKEN), Buffer.from(GA_TOKEN)];
  let touched = 0;
  let replacements = 0;

  for (const file of walk(DIST)) {
    const buffer = readFileSync(file);
    if (!needles.some((needle) => buffer.includes(needle))) continue;

    const text = buffer.toString("utf8");
    const originHits = text.split(ORIGIN_TOKEN).length - 1;
    const gaHits = text.split(GA_TOKEN).length - 1;

    writeFileSync(
      file,
      text.split(ORIGIN_TOKEN).join(origin).split(GA_TOKEN).join(gaId)
    );

    touched += 1;
    replacements += originHits + gaHits;
  }

  return { touched, replacements };
}

/** Fail the build rather than shipping a page with an unresolved token. */
function assertNoTokensLeft() {
  const needles = [Buffer.from(ORIGIN_TOKEN), Buffer.from(GA_TOKEN)];
  const offenders = [];

  for (const file of walk(DIST)) {
    const buffer = readFileSync(file);
    if (needles.some((needle) => buffer.includes(needle))) {
      offenders.push(path.relative(DIST, file));
    }
  }

  if (offenders.length > 0) {
    throw new Error(
      `[build-dist] unresolved build tokens in ${offenders.length} file(s): ` +
        offenders.slice(0, 5).join(", ") +
        (offenders.length > 5 ? ", ..." : "")
    );
  }
}

/**
 * Cloudflare rejects/ignores _headers beyond this many rules on every plan.
 * https://developers.cloudflare.com/workers/static-assets/headers/
 */
const MAX_HEADER_RULES = 100;

/** A rule is a selector line: not blank, not a comment, not indented. */
function countHeaderRules(content) {
  return content
    .split("\n")
    .filter((line) => line.trim() && !line.trimStart().startsWith("#") && !/^\s/.test(line))
    .length;
}

/**
 * Append one Cache-Control rule per HTML page to dist/_headers.
 *
 * Cloudflare applies *every* matching _headers block and appends repeated
 * header values, so a short-lived HTML policy cannot sit on /* - it would be
 * prepended to the long-lived /css/*, /js/*, /images/* values and win. The
 * canonical page URLs are also extensionless (/about, not /about.html), so a
 * /*.html rule would never match anything. One exact rule per page solves
 * both, and regenerating it here means new pages never drift out of sync.
 *
 * The rules are budgeted against Cloudflare's 100-rule limit. Past that the
 * generation is skipped (with a loud warning) instead of breaking the deploy:
 * HTML then carries no Cache-Control, so browsers revalidate via ETag, which
 * is the same freshness guarantee max-age=0 would have given.
 */
function appendHtmlCacheRules() {
  const pages = readdirSync(ROOT, { withFileTypes: true })
    .filter((entry) => entry.isFile() && entry.name.toLowerCase().endsWith(".html"))
    .map((entry) =>
      entry.name === "index.html" ? "/" : `/${entry.name.replace(/\.html$/i, "")}`
    )
    .sort();

  const headersPath = path.join(DIST, "_headers");
  const existing = countHeaderRules(readFileSync(headersPath, "utf8"));

  if (existing + pages.length > MAX_HEADER_RULES) {
    console.warn(
      `[build-dist] WARNING: ${existing} _headers rules + ${pages.length} HTML pages ` +
        `exceeds Cloudflare's ${MAX_HEADER_RULES}-rule limit, so per-page rules were ` +
        `NOT generated. HTML will fall back to ETag revalidation (same freshness).`
    );
    return { appended: 0, total: existing };
  }

  const rules = pages
    .map((page) => `\n${page}\n  Cache-Control: public, max-age=0, must-revalidate\n`)
    .join("");

  appendFileSync(
    headersPath,
    `\n# --- generated by scripts/build-dist.mjs: HTML pages (short-lived) ---${rules}`
  );

  return { appended: pages.length, total: existing + pages.length };
}

function main() {
  // Validate first: a bad SITE_URL should fail before any copying happens.
  const origin = resolveSiteUrl();
  const gaId = resolveGaId();

  if (existsSync(DIST)) {
    rmSync(DIST, { recursive: true, force: true });
  }

  const entries = readdirSync(ROOT, { withFileTypes: true });
  const copied = [];
  const skipped = [];

  for (const entry of entries) {
    if (!shouldCopy(entry.name)) {
      skipped.push(entry.name);
      continue;
    }
    const src = path.join(ROOT, entry.name);
    cpSync(src, path.join(DIST, entry.name), {
      recursive: true,
      // Guard against nested tooling output and stray dotfiles inside the
      // directories we do copy.
      filter: (source) => {
        const rel = path.relative(ROOT, source);
        if (rel === "" || rel === ".") return true;
        const parts = rel.split(path.sep);
        if (parts.some((p) => p === "node_modules" || p === ".git")) return false;
        const base = parts[parts.length - 1];
        if (base.startsWith(".") && !DOT_ALLOW.has(base)) return false;
        return true;
      },
    });
    copied.push(entry.name);
  }

  const count = (dir) => {
    let n = 0;
    for (const e of readdirSync(dir, { withFileTypes: true })) {
      n += e.isDirectory() ? count(path.join(dir, e.name)) : 1;
    }
    return n;
  };

  const files = existsSync(DIST) ? count(DIST) : 0;
  console.log(
    `[build-dist] ${files} files copied into dist/ from ${copied.length} top-level entries`
  );
  if (skipped.length > 0) {
    console.log(`[build-dist] skipped: ${skipped.sort().join(", ")}`);
  }

  // Fail loudly rather than deploying an empty or broken site.
  for (const required of ["index.html", "404.html", "_headers", "_redirects"]) {
    if (!existsSync(path.join(DIST, required))) {
      throw new Error(`[build-dist] expected ${required} in dist/ but it is missing`);
    }
  }

  const headers = appendHtmlCacheRules();
  console.log(
    `[build-dist] dist/_headers: ${headers.total} rules (${headers.appended} generated for HTML pages, limit ${MAX_HEADER_RULES})`
  );

  const tokens = substituteTokens(origin, gaId);
  console.log(
    `[build-dist] ${ORIGIN_TOKEN} -> ${origin}, ${GA_TOKEN} -> ${gaId || "(empty, analytics off)"}` +
      ` [${tokens.replacements} replacements in ${tokens.touched} files]`
  );
  assertNoTokensLeft();
}

try {
  main();
} catch (error) {
  // Keep the deploy log readable: one clear line instead of a stack trace.
  console.error(error?.message || String(error));
  process.exit(1);
}
