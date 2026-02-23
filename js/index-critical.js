(() => {
  const video = document.getElementById("heroVideo");
  if (!video) return;

  // Skip heavy autoplay for users on data saver or weak networks.
  const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
  const saveData = Boolean(connection && connection.saveData);
  const weakNetwork = Boolean(
    connection && /2g/.test(connection.effectiveType || "")
  );

  if (saveData || weakNetwork) return;

  let played = false;

  const playVideo = () => {
    if (played) return;
    played = true;
    video.preload = "metadata";
    const p = video.play();
    if (p && typeof p.catch === "function") p.catch(() => {});
  };

  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            playVideo();
            io.disconnect();
            break;
          }
        }
      },
      { rootMargin: "150px 0px" }
    );
    io.observe(video);
  } else {
    window.addEventListener("load", playVideo, { once: true });
  }
})();
