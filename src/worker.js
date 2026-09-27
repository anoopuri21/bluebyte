/**
 * Bluebyte site - contact form handler.
 *
 * The site is served as Cloudflare Workers static assets from ./dist. This
 * Worker exists to handle one thing those assets cannot: the contact form,
 * which used to POST to `contactform.php`. PHP does not run on Workers, so the
 * endpoint is implemented here.
 *
 * Routes
 *   POST /api/contact       - the endpoint the form submits to
 *   POST /contactform.php   - legacy alias, same handler
 *   GET  /api/contact       - 302 to /contact (browsers opening the URL)
 *   anything else           - forwarded to the static assets (keeps 404.html)
 *
 * wrangler.jsonc sets assets.run_worker_first for these paths. Without it,
 * Cloudflare serves assets first and a browser form POST (a navigation request)
 * never reaches this script — static assets answer 405 Method Not Allowed.
 *
 * Delivery (first one configured wins)
 *   1. RESEND_API_KEY        - email via https://resend.com
 *   2. WEB3FORMS_ACCESS_KEY  - email via https://web3forms.com (no email infra)
 *   3. CONTACT_WEBHOOK_URL   - JSON POST to any URL (Slack, Zapier, your API)
 *
 * Secrets go in `wrangler secret put <NAME>` (or `.dev.vars` locally) - never in
 * wrangler.jsonc. Non-secret defaults (MAIL_TO, FROM_EMAIL, ...) live in `vars`.
 *
 * If none of the three is configured the endpoint returns 503 and logs loudly,
 * rather than pretending the message was delivered.
 */

/** Endpoints handled by this Worker. Trailing slashes are stripped first. */
const CONTACT_PATHS = new Set(["/api/contact", "/contactform.php"]);

function normalizePath(pathname) {
  if (pathname.length > 1 && pathname.endsWith("/")) return pathname.slice(0, -1);
  return pathname;
}

/** Field length caps. Anything longer is truncated, never rejected. */
const LIMITS = {
  firstName: 100,
  lastName: 100,
  email: 254,
  phone: 50,
  message: 5000,
};

/** Reject oversized bodies before parsing them. */
const MAX_BODY_BYTES = 64 * 1024;

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

const DEFAULT_MAIL_TO = "info@bluebyteitinfosystem.com,websitesexperts@gmail.com";
const DEFAULT_FROM_EMAIL = "no-reply@bluebyteitinfosystem.com";

/** Strip control characters (CRLF injection) and clamp length. */
function clean(value, max) {
  return String(value ?? "")
    .replace(/[\u0000-\u001f\u007f]/g, " ")
    .trim()
    .slice(0, max);
}

function escapeHtml(value) {
  return String(value).replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]
  );
}

function wantsJson(request) {
  const accept = request.headers.get("accept") || "";
  const requestedWith = (request.headers.get("x-requested-with") || "").toLowerCase();
  return accept.includes("application/json") || requestedWith === "xmlhttprequest";
}

/**
 * Same-origin check. Enforced only when an Origin/Referer header is present,
 * so privacy extensions that strip them do not lock out real visitors.
 */
function originAllowed(request, env) {
  const raw = request.headers.get("origin") || request.headers.get("referer") || "";
  if (!raw) return true;

  let host;
  try {
    host = new URL(raw).host.toLowerCase();
  } catch {
    return false;
  }

  const requestHost = new URL(request.url).host.toLowerCase();
  if (host === requestHost) return true;

  return String(env.ALLOWED_ORIGINS || "")
    .split(",")
    .map((entry) =>
      entry.trim().toLowerCase().replace(/^https?:\/\//, "").replace(/\/.*$/, "")
    )
    .filter(Boolean)
    .includes(host);
}

function validate(form) {
  const data = {
    firstName: clean(form.get("firstName"), LIMITS.firstName),
    lastName: clean(form.get("lastName"), LIMITS.lastName),
    email: clean(form.get("email"), LIMITS.email),
    phone: clean(form.get("phone"), LIMITS.phone),
    message: clean(form.get("message"), LIMITS.message),
  };

  if (!data.firstName) return { error: "First name is required." };
  if (!data.lastName) return { error: "Last name is required." };
  if (!data.email) return { error: "Email address is required." };
  if (!EMAIL_RE.test(data.email)) return { error: "Please enter a valid email address." };
  if (!data.message) return { error: "Message is required." };

  return { data };
}

function emailHtml(data, request) {
  const row = (label, value) =>
    `<tr><td width="30%" style="padding:15px;background-color:#f9f2e2;">${escapeHtml(
      label
    )}</td><td width="70%" style="padding:15px;color:#555;">${escapeHtml(
      value
    )}</td></tr>`;

  return (
    `<table width="650" border="2" align="center" cellpadding="5" cellspacing="0" ` +
    `bordercolor="#ddd" bgcolor="#ffffff" style="border-collapse:collapse;font-family:sans-serif;">` +
    `<tr><td height="45" colspan="2"><center><strong style="font-size:14px;">` +
    `Bluebyte IT Solutions<br/>Contact Form</strong></center></td></tr>` +
    row("WebPage Url", request.headers.get("referer") || request.headers.get("origin") || "") +
    row("First Name", data.firstName) +
    row("Last Name", data.lastName) +
    row("Contact Number", data.phone) +
    row("E-mail", data.email) +
    row("Message", data.message) +
    `</table>`
  );
}

async function sendViaResend(data, request, env) {
  const subject = `${env.SUBJECT_PREFIX || "Contact Form - Bluebyte IT Solutions"}`;
  const response = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${env.RESEND_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      from: env.FROM_EMAIL || DEFAULT_FROM_EMAIL,
      to: String(env.MAIL_TO || DEFAULT_MAIL_TO)
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean),
      reply_to: data.email,
      subject,
      html: emailHtml(data, request),
    }),
  });

  if (!response.ok) {
    throw new Error(`Resend responded ${response.status}: ${await response.text()}`);
  }
  return "resend";
}

async function sendViaWeb3Forms(data, request, env) {
  const response = await fetch("https://api.web3forms.com/submit", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({
      access_key: env.WEB3FORMS_ACCESS_KEY,
      subject: env.SUBJECT_PREFIX || "Contact Form - Bluebyte IT Solutions",
      from_name: `${data.firstName} ${data.lastName}`.trim(),
      email: data.email,
      firstName: data.firstName,
      lastName: data.lastName,
      phone: data.phone,
      message: data.message,
      referer: request.headers.get("referer") || "",
      botcheck: "",
    }),
  });

  const body = await response.text();
  if (!response.ok) {
    throw new Error(`Web3Forms responded ${response.status}: ${body}`);
  }
  try {
    if (JSON.parse(body).success === false) {
      throw new Error(`Web3Forms rejected the submission: ${body}`);
    }
  } catch (e) {
    if (e instanceof SyntaxError) {
      /* non-JSON success body - treat as delivered */
    } else {
      throw e;
    }
  }
  return "web3forms";
}

async function sendViaWebhook(data, request, env) {
  const response = await fetch(env.CONTACT_WEBHOOK_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      type: "contact-form",
      receivedAt: new Date().toISOString(),
      ...data,
      referer: request.headers.get("referer") || "",
      userAgent: request.headers.get("user-agent") || "",
    }),
  });

  if (!response.ok) {
    throw new Error(`Webhook responded ${response.status}: ${await response.text()}`);
  }
  return "webhook";
}

async function deliver(data, request, env) {
  if (env.RESEND_API_KEY) return sendViaResend(data, request, env);
  if (env.WEB3FORMS_ACCESS_KEY) return sendViaWeb3Forms(data, request, env);
  if (env.CONTACT_WEBHOOK_URL) return sendViaWebhook(data, request, env);
  return null;
}

function redirect(request, query) {
  const url = new URL("/contact", request.url);
  url.searchParams.set(query, "1");
  return Response.redirect(url.toString(), 303);
}

async function handleContact(request, env) {
  const json = wantsJson(request);

  if (request.method === "GET" || request.method === "HEAD") {
    // Opening /api/contact in a browser is not a form submit. Send visitors
    // to the contact page instead of a raw 405.
    return Response.redirect(new URL("/contact", request.url).toString(), 302);
  }

  if (request.method !== "POST") {
    return new Response("Method Not Allowed", {
      status: 405,
      headers: { Allow: "GET, HEAD, POST" },
    });
  }

  const length = Number(request.headers.get("content-length") || 0);
  if (length > MAX_BODY_BYTES) {
    return json
      ? Response.json({ ok: false, error: "Submission is too large." }, { status: 413 })
      : redirect(request, "error");
  }

  let form;
  try {
    form = await request.formData();
  } catch {
    return json
      ? Response.json({ ok: false, error: "Malformed form submission." }, { status: 400 })
      : redirect(request, "error");
  }

  // Honeypot: a real visitor never sees this field, a bot fills in everything.
  // Answer with success but deliver nothing, so bots do not learn they were caught.
  if (clean(form.get("website"), 200)) {
    return json ? Response.json({ ok: true }) : redirect(request, "sent");
  }

  if (!originAllowed(request, env)) {
    return json
      ? Response.json({ ok: false, error: "Origin not allowed." }, { status: 403 })
      : redirect(request, "error");
  }

  const result = validate(form);
  if (result.error) {
    return json
      ? Response.json({ ok: false, error: result.error }, { status: 422 })
      : redirect(request, "error");
  }

  let provider;
  try {
    provider = await deliver(result.data, request, env);
  } catch (error) {
    console.error("contact form delivery failed:", error?.message || error);
    return json
      ? Response.json({ ok: false, error: "Could not send your message." }, { status: 502 })
      : redirect(request, "error");
  }

  if (!provider) {
    console.error(
      "contact form is not configured: set RESEND_API_KEY, WEB3FORMS_ACCESS_KEY " +
        "or CONTACT_WEBHOOK_URL (wrangler secret put <NAME>)"
    );
    return json
      ? Response.json(
          { ok: false, error: "Contact form is not configured on the server." },
          { status: 503 }
        )
      : redirect(request, "error");
  }

  console.log(`contact form submission delivered via ${provider}`);
  return json ? Response.json({ ok: true }) : redirect(request, "sent");
}

export default {
  async fetch(request, env) {
    const { pathname } = new URL(request.url);

    if (CONTACT_PATHS.has(normalizePath(pathname))) {
      return handleContact(request, env);
    }

    // Everything else is a static asset. Forwarding through the binding keeps
    // `html_handling` and `not_found_handling` (the custom 404 page) working.
    if (env.ASSETS) return env.ASSETS.fetch(request);

    return new Response("Not Found", { status: 404 });
  },
};
