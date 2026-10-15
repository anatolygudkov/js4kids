// Урок 0: раскрывает раздел про операционную систему, на которой открыта страница.
(function () {
  var ua = navigator.userAgent || "";
  var os = "";
  if (/Windows/.test(ua)) os = "windows";
  else if (/Macintosh|Mac OS X/.test(ua)) os = "mac";
  else if (/Linux/.test(ua) && !/Android/.test(ua)) os = /aarch64|armv7l|armv6l/.test(ua) ? "rpi" : "ubuntu";
  var sections = document.querySelectorAll("details.os");
  for (var i = 0; i < sections.length; i++) {
    if (sections[i].getAttribute("data-os") === os) {
      sections[i].open = true;
      sections[i].classList.add("is-mine");
    }
  }
})();
