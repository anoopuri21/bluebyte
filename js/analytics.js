(() => {
  if (typeof window === "undefined" || !document.head) return;

  // Injected at build time from GA_MEASUREMENT_ID; analytics stays off when unset.
  const GA_ID = document.querySelector('meta[name="google-analytics-id"]')?.content?.trim();
  if (!GA_ID || !/^G-[A-Z0-9]+$/.test(GA_ID)) return;

  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function gtag() {
    window.dataLayer.push(arguments);
  };

  const script = document.createElement("script");
  script.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(GA_ID)}`;
  script.async = true;
  document.head.appendChild(script);

  window.gtag("js", new Date());
  window.gtag("config", GA_ID);
})();
