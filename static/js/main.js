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

let reportMap;
let reportMarker;

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const mapDiv =
            document.getElementById(
                "incident-map"
            );

        if (!mapDiv)
            return;

        reportMap = L.map(
            "incident-map"
        ).setView(
            [28.05,81.62],
            11
        );

        L.tileLayer(
            "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
            {
                maxZoom: 19
            }
        ).addTo(reportMap);

        reportMap.on(
            "click",
            function(e){

                setLocation(
                    e.latlng.lat,
                    e.latlng.lng
                );

            }
        );

    }
);

function setLocation(lat,lng){

    if(reportMarker){

        reportMap.removeLayer(
            reportMarker
        );

    }

    reportMarker =
        L.marker([lat,lng])
        .addTo(reportMap);

    document.getElementById(
        "id_latitude"
    ).value = lat;

    document.getElementById(
        "id_longitude"
    ).value = lng;

    document.getElementById(
        "id_location"
    ).value =

    lat.toFixed(6)
    +
    ", "
    +
    lng.toFixed(6);

}

function getCurrentLocation(){

    if(!navigator.geolocation){

        alert(
            "GPS is not supported."
        );

        return;
    }

    navigator.geolocation.getCurrentPosition(

        function(position){

            const lat =
                position.coords.latitude;

            const lng =
                position.coords.longitude;

            reportMap.setView(
                [lat,lng],
                15
            );

            setLocation(
                lat,
                lng
            );

        },

        function(){

            alert(
                "Unable to access location."
            );

        }

    );

}