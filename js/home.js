(() => {
  document.documentElement.classList.add("js-reveal");
  const reduce = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;

  const splitReveal = (el) => {
    if (el.dataset.splitDone) return;
    const text = el.textContent.trim().replace(/\s+/g, " ");
    el.dataset.splitDone = "true";
    el.textContent = "";
    text.split(" ").forEach((word, i) => {
      const wrap = document.createElement("span");
      wrap.className = "lux-word";
      wrap.style.setProperty("--lux-i", String(i));
      const inner = document.createElement("span");
      inner.textContent = word;
      wrap.appendChild(inner);
      el.appendChild(wrap);
      el.appendChild(document.createTextNode(" "));
    });
  };

  document.querySelectorAll("[data-split]").forEach(splitReveal);

  const hero = document.querySelector(".lux-hero");
  if (hero) {
    requestAnimationFrame(() => hero.classList.add("is-ready"));
  }

  const mark = (el) => el.classList.add("lux-in");

  if (reduce || !("IntersectionObserver" in window)) {
    document.querySelectorAll("[data-reveal]").forEach(mark);
    return;
  }

  const io = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          mark(entry.target);
          io.unobserve(entry.target);
        }
      }
    },
    { threshold: 0.18, rootMargin: "0px 0px -8% 0px" }
  );

  document.querySelectorAll("[data-reveal]").forEach((el) => io.observe(el));
})();
