// Offline shell. API responses are cached too, but app.js marks anything older than 45 min UNKNOWN (= NO-GO),
// so a stale offline copy can never show an old GO.
var SHELL = "nikasi-shell-v1", DATA = "nikasi-data-v1";
var FILES = ["./", "index.html", "style.css", "app.js", "config.js", "manifest.webmanifest"];
self.addEventListener("install", function (e) { e.waitUntil(caches.open(SHELL).then(function (c) { return c.addAll(FILES); })); self.skipWaiting(); });
self.addEventListener("activate", function (e) { e.waitUntil(self.clients.claim()); });
self.addEventListener("fetch", function (e) {
  var u = new URL(e.request.url);
  if (e.request.method !== "GET") return;
  var isData = /\/spots(\/|$)/.test(u.pathname) || /mock_state\.json$/.test(u.pathname);
  if (isData) {
    e.respondWith(fetch(e.request).then(function (r) { var c = r.clone(); caches.open(DATA).then(function (d) { d.put(e.request, c); }); return r; })
      .catch(function () { return caches.match(e.request); }));
  } else if (u.origin === location.origin) {
    e.respondWith(caches.match(e.request).then(function (m) { return m || fetch(e.request); }));
  }
});
