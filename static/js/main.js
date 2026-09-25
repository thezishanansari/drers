// DRERS — front-end helpers
(function () {
  "use strict";

  // 1. Duplicate the ticker items so the marquee loops seamlessly.
  var track = document.getElementById("drers-ticker");
  if (track && track.children.length && !track.dataset.cloned) {
    track.innerHTML += track.innerHTML;
    track.dataset.cloned = "1";

    // Pause on hover
    var view = track.parentElement;
    view.addEventListener("mouseenter", function () {
      track.style.animationPlayState = "paused";
    });
    view.addEventListener("mouseleave", function () {
      track.style.animationPlayState = "running";
    });
  }

  // 2. Auto-dismiss flash messages after 6 seconds.
  document.querySelectorAll(".flash").forEach(function (el) {
    setTimeout(function () {
      el.style.transition = "opacity .4s";
      el.style.opacity = "0";
      setTimeout(function () { el.remove(); }, 400);
    }, 6000);
  });

  // 3. Focus the first empty input on auth pages.
  var first = document.querySelector(".auth-right input");
  if (first && !first.value) first.focus();
})();
