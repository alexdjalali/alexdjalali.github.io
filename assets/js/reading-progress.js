(function () {
  var bar = document.getElementById("reading-progress");
  var content = document.querySelector(".post-content");
  if (!bar || !content) return;

  var ticking = false;

  function updateProgress() {
    var rect = content.getBoundingClientRect();
    var contentTop = rect.top + window.scrollY;
    var contentHeight = rect.height;
    var scrolled = window.scrollY - contentTop;
    var percent = Math.min(Math.max(scrolled / (contentHeight - window.innerHeight), 0), 1) * 100;
    bar.style.width = percent + "%";
    bar.setAttribute("aria-valuenow", Math.round(percent));
    ticking = false;
  }

  window.addEventListener("scroll", function () {
    if (!ticking) {
      requestAnimationFrame(updateProgress);
      ticking = true;
    }
  });

  updateProgress();
})();
