#!/usr/bin/env node
/**
 * Tests for src/worker.js - run with: node scripts/test-worker.mjs
 *
 * No test framework, no dependencies: plain node, plain asserts. The real
 * module is imported and its real fetch handler is called; only the outbound
 * `fetch` to the email provider is stubbed, since api.resend.com cannot be
 * reached from CI or from a sandbox.
 *
 *   node scripts/test-worker.mjs
 */

import assert from "node:assert/strict";
import worker from "../src/worker.js";

const SITE = "https://bluebyte.example";
let calls = [];

/** Replace global fetch with a recorder that returns `responder(url, init)`. */
function stubFetch(responder = () => new Response('{"ok":true}', { status: 200 })) {
  calls = [];
  globalThis.fetch = async (url, init) => {
    calls.push({ url: String(url), init });
    return responder(String(url), init);
  };
}

function postRequest(path, fields, headers = {}) {
  return new Request(SITE + path, {
    method: "POST",
    headers: {
      "content-type": "application/x-www-form-urlencoded",
      origin: SITE,
      ...headers,
    },
    body: new URLSearchParams(fields).toString(),
  });
}

const VALID = {
  firstName: "Ada",
  lastName: "Lovelace",
  email: "ada@example.com",
  phone: "+91 98000 00000",
  message: "We need a new website.",
};

const JSON_HEADERS = { accept: "application/json" };

const tests = [];
const test = (name, fn) => tests.push([name, fn]);

test("delivers via Resend when RESEND_API_KEY is set", async () => {
  stubFetch();
  const res = await worker.fetch(
    postRequest("/api/contact", VALID, JSON_HEADERS),
    { RESEND_API_KEY: "re_test", MAIL_TO: "a@x.com, b@x.com", FROM_EMAIL: "no-reply@x.com" }
  );
  assert.equal(res.status, 200);
  assert.deepEqual(await res.json(), { ok: true });
  assert.equal(calls.length, 1);
  assert.equal(calls[0].url, "https://api.resend.com/emails");
  assert.equal(calls[0].init.method, "POST");
  assert.equal(calls[0].init.headers.Authorization, "Bearer re_test");
  const body = JSON.parse(calls[0].init.body);
  assert.equal(body.from, "no-reply@x.com");
  assert.deepEqual(body.to, ["a@x.com", "b@x.com"]);
  assert.equal(body.reply_to, "ada@example.com");
  assert.match(body.subject, /Bluebyte IT Solutions/);
  assert.match(body.html, /We need a new website\./);
  assert.match(body.html, /Ada/);
});

test("delivers via Web3Forms when only WEB3FORMS_ACCESS_KEY is set", async () => {
  stubFetch();
  const res = await worker.fetch(postRequest("/api/contact", VALID, JSON_HEADERS), {
    WEB3FORMS_ACCESS_KEY: "wf_test",
  });
  assert.equal(res.status, 200);
  assert.equal(calls.length, 1);
  assert.equal(calls[0].url, "https://api.web3forms.com/submit");
  const body = JSON.parse(calls[0].init.body);
  assert.equal(body.access_key, "wf_test");
  assert.equal(body.email, "ada@example.com");
  assert.equal(body.from_name, "Ada Lovelace");
  assert.equal(body.message, "We need a new website.");
  assert.match(body.subject, /Bluebyte IT Solutions/);
});

test("Resend wins over Web3Forms when both are configured", async () => {
  stubFetch();
  await worker.fetch(postRequest("/api/contact", VALID, JSON_HEADERS), {
    RESEND_API_KEY: "re_test",
    WEB3FORMS_ACCESS_KEY: "wf_test",
  });
  assert.equal(calls.length, 1);
  assert.equal(calls[0].url, "https://api.resend.com/emails");
});

test("falls back to the default recipients when MAIL_TO is unset", async () => {
  stubFetch();
  await worker.fetch(postRequest("/api/contact", VALID, JSON_HEADERS), {
    RESEND_API_KEY: "re_test",
  });
  const body = JSON.parse(calls[0].init.body);
  assert.deepEqual(body.to, [
    "info@bluebyteitsolutions.com",
    "websitesexperts@gmail.com",
  ]);
  assert.equal(body.from, "no-reply@bluebyteitsolutions.com");
});

test("503 when no delivery method is configured", async () => {
  stubFetch();
  const res = await worker.fetch(postRequest("/api/contact", VALID, JSON_HEADERS), {});
  assert.equal(res.status, 503);
  assert.equal((await res.json()).ok, false);
  assert.equal(calls.length, 0, "must not silently drop the message");
});

test("502 when the provider rejects the request", async () => {
  stubFetch(() => new Response("unauthorized", { status: 401 }));
  const res = await worker.fetch(postRequest("/api/contact", VALID, JSON_HEADERS), {
    RESEND_API_KEY: "re_bad",
  });
  assert.equal(res.status, 502);
  assert.equal((await res.json()).ok, false);
});

test("422 on an invalid email address, nothing delivered", async () => {
  stubFetch();
  const res = await worker.fetch(
    postRequest("/api/contact", { ...VALID, email: "nope" }, JSON_HEADERS),
    { RESEND_API_KEY: "re_test" }
  );
  assert.equal(res.status, 422);
  assert.match((await res.json()).error, /valid email/);
  assert.equal(calls.length, 0);
});

test("422 when required fields are empty", async () => {
  stubFetch();
  const res = await worker.fetch(
    postRequest("/api/contact", { firstName: "", lastName: "", email: "", message: "" }, JSON_HEADERS),
    { RESEND_API_KEY: "re_test" }
  );
  assert.equal(res.status, 422);
  assert.equal(calls.length, 0);
});

test("honeypot: reports success, delivers nothing", async () => {
  stubFetch();
  const res = await worker.fetch(
    postRequest("/api/contact", { ...VALID, website: "http://spam.example" }, JSON_HEADERS),
    { RESEND_API_KEY: "re_test" }
  );
  assert.equal(res.status, 200);
  assert.deepEqual(await res.json(), { ok: true });
  assert.equal(calls.length, 0);
});

test("rejects a foreign Origin, allows an allow-listed one", async () => {
  stubFetch();
  const bad = await worker.fetch(
    postRequest("/api/contact", VALID, { ...JSON_HEADERS, origin: "https://evil.example" }),
    { RESEND_API_KEY: "re_test" }
  );
  assert.equal(bad.status, 403);
  assert.equal(calls.length, 0);

  const good = await worker.fetch(
    postRequest("/api/contact", VALID, { ...JSON_HEADERS, origin: "https://www.bluebyte.example" }),
    { RESEND_API_KEY: "re_test", ALLOWED_ORIGINS: "www.bluebyte.example" }
  );
  assert.equal(good.status, 200);
  assert.equal(calls.length, 1);
});

test("browser POST gets a 303 back to /contact?sent=1", async () => {
  stubFetch();
  const res = await worker.fetch(postRequest("/api/contact", VALID), {
    RESEND_API_KEY: "re_test",
  });
  assert.equal(res.status, 303);
  assert.equal(res.headers.get("location"), `${SITE}/contact?sent=1`);
});

test("failed browser POST redirects to /contact?error=1", async () => {
  stubFetch();
  const res = await worker.fetch(postRequest("/api/contact", { ...VALID, email: "bad" }), {
    RESEND_API_KEY: "re_test",
  });
  assert.equal(res.status, 303);
  assert.equal(res.headers.get("location"), `${SITE}/contact?error=1`);
});

test("legacy contactform.php path is handled identically", async () => {
  stubFetch();
  const res = await worker.fetch(postRequest("/contactform.php", VALID), {
    RESEND_API_KEY: "re_test",
  });
  assert.equal(res.status, 303);
  assert.equal(calls.length, 1);
});

test("POST /api/contact/ (trailing slash) is handled identically", async () => {
  stubFetch();
  const res = await worker.fetch(postRequest("/api/contact/", VALID), {
    RESEND_API_KEY: "re_test",
  });
  assert.equal(res.status, 303);
  assert.equal(res.headers.get("location"), `${SITE}/contact?sent=1`);
  assert.equal(calls.length, 1);
});

test("GET on the contact endpoint redirects to /contact", async () => {
  stubFetch();
  const res = await worker.fetch(new Request(`${SITE}/api/contact`), {});
  assert.equal(res.status, 302);
  assert.equal(res.headers.get("location"), `${SITE}/contact`);
  assert.equal(calls.length, 0);
});

test("GET /api/contact/ (trailing slash) also redirects to /contact", async () => {
  stubFetch();
  const res = await worker.fetch(new Request(`${SITE}/api/contact/`), {});
  assert.equal(res.status, 302);
  assert.equal(res.headers.get("location"), `${SITE}/contact`);
});

test("PUT on the contact endpoint is 405", async () => {
  stubFetch();
  const res = await worker.fetch(new Request(`${SITE}/api/contact`, { method: "PUT" }), {});
  assert.equal(res.status, 405);
  assert.equal(res.headers.get("allow"), "GET, HEAD, POST");
});

test("everything else is forwarded to the ASSETS binding", async () => {
  stubFetch();
  let forwarded = null;
  const env = {
    ASSETS: {
      fetch: (request) => {
        forwarded = new URL(request.url).pathname;
        return new Response("asset", { status: 200 });
      },
    },
  };
  const res = await worker.fetch(new Request(`${SITE}/about`), env);
  assert.equal(res.status, 200);
  assert.equal(forwarded, "/about");
});

test("404 when there is no ASSETS binding and no route match", async () => {
  stubFetch();
  const res = await worker.fetch(new Request(`${SITE}/about`), {});
  assert.equal(res.status, 404);
});

test("strips CRLF and clamps oversized fields", async () => {
  stubFetch();
  await worker.fetch(
    postRequest(
      "/api/contact",
      { ...VALID, message: `line1\r\nBcc: attacker@evil.example\r\n${"x".repeat(9000)}` },
      JSON_HEADERS
    ),
    { RESEND_API_KEY: "re_test" }
  );
  const body = JSON.parse(calls[0].init.body);
  assert.ok(!body.html.includes("Bcc: attacker@evil.example\r\n"), "CRLF must be stripped");
  const message = /Contact Number[\s\S]*?E-mail[\s\S]*?Message<\/td><td[^>]*>([\s\S]*?)<\/td>/.exec(
    body.html
  );
  assert.ok(message, "message row should be present");
  assert.ok(message[1].length <= 5200, "message must be truncated");
});

let failed = 0;
for (const [name, fn] of tests) {
  try {
    await fn();
    console.log(`  ok   ${name}`);
  } catch (error) {
    failed += 1;
    console.log(`  FAIL ${name}\n       ${error.message}`);
  }
}

console.log(
  `\n${tests.length - failed}/${tests.length} passed${failed ? ` - ${failed} FAILED` : ""}`
);
process.exit(failed ? 1 : 0);
