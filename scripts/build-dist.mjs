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
 * Requires Node 16.7+ (uses fs.cpSync). No dependencies.
 */

import { cpSync, existsSync, rmSync, readdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const DIST = path.join(ROOT, "dist");

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

function main() {
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
}

main();
