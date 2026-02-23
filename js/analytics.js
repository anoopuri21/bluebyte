(() => {
  const GA_ID = "G-7J6L90XM1Y";

  if (typeof window === "undefined") return;

  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function gtag() {
    window.dataLayer.push(arguments);
  };

  const script = document.createElement("script");
  script.src = `https://www.googletagmanager.com/gtag/js?id=${GA_ID}`;
  script.async = true;
  document.head.appendChild(script);

  window.gtag("js", new Date());
  window.gtag("config", GA_ID);
})();
