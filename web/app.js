(function () {
  var STALE_MIN = 45, COLORS = {GO: "#2e9e5b", CAUTION: "#e0a100", "NO-GO": "#d64545", UNKNOWN: "#7b5ea7"};
  var map = L.map("map").setView([28.6139, 77.209], 11);
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {maxZoom: 18, attribution: "&copy; OpenStreetMap contributors"}).addTo(map);
  var markers = {};

  // Fail safe on the client too: old or malformed rows become UNKNOWN, which acts as NO-GO.
  function effective(s) {
    var t = Date.parse(s.updated_at), age = (Date.now() - t) / 60000;
    if (isNaN(t) || age > STALE_MIN || age < -5) {
      return {state: "UNKNOWN", act: "NO-GO", eta: null, why: isNaN(t) ? "no timestamp" : "data is " + Math.round(age) + " min old"};
    }
    var why = (s.reasons || []).join("; ");
    return {state: s.state, act: s.act_as || (s.state === "UNKNOWN" ? "NO-GO" : s.state), eta: s.minutes_to_no_go == null ? null : Number(s.minutes_to_no_go), why: why, t: t};
  }
  function cls(e) { return e.state === "UNKNOWN" ? "UNKNOWN" : e.act.replace("-", ""); }
  function el(tag, c, text) { var n = document.createElement(tag); if (c) n.className = c; if (text != null) n.textContent = text; return n; }

  function render(spots) {
    var list = document.getElementById("cards"); list.textContent = "";
    spots.forEach(function (s) {
      var e = effective(s), li = el("li", "card " + cls(e));
      li.appendChild(el("h2", null, s.name));
      li.appendChild(el("span", "badge", e.state === "UNKNOWN" ? "UNKNOWN: treat as NO-GO" : e.act));
      if (e.act !== "NO-GO" && e.eta != null) {
        var left = Math.max(0, Math.round(e.eta - (Date.now() - e.t) / 60000));
        li.appendChild(el("p", "countdown", "NO-GO in about " + left + " min"));
      }
      li.appendChild(el("p", "why", e.why));
      list.appendChild(li);
      var shown = e.state === "UNKNOWN" ? "UNKNOWN" : e.act;
      if (s.lat != null && s.lon != null) {
        if (markers[s.spot_id]) map.removeLayer(markers[s.spot_id]);
        markers[s.spot_id] = L.circleMarker([s.lat, s.lon], {radius: 11, color: "#fff", weight: 2, fillColor: COLORS[shown], fillOpacity: 1})
          .addTo(map).bindTooltip(s.name + ": " + shown);
      }
    });
  }

  var latest = [];
  function km(a, b, c, d) { var r = Math.PI / 180, p = (c - a) * r, q = (d - b) * r, h = Math.sin(p / 2) * Math.sin(p / 2) + Math.cos(a * r) * Math.cos(c * r) * Math.sin(q / 2) * Math.sin(q / 2); return 12742 * Math.asin(Math.sqrt(h)); }
  // Location stays in the browser: it is used once to pick the nearest spot and is never sent anywhere.
  document.getElementById("near").addEventListener("click", function () {
    var out = document.getElementById("near-out");
    if (!navigator.geolocation) { out.textContent = "Location is not available on this device."; return; }
    navigator.geolocation.getCurrentPosition(function (p) {
      var best = null;
      latest.forEach(function (s) { if (s.lat != null) { var d = km(p.coords.latitude, p.coords.longitude, Number(s.lat), Number(s.lon)); if (!best || d < best.d) best = {s: s, d: d}; } });
      if (!best) { out.textContent = "No spots loaded yet."; return; }
      var e = effective(best.s);
      out.textContent = best.s.name + " (" + best.d.toFixed(1) + " km): " + (e.state === "UNKNOWN" ? "UNKNOWN, treat as NO-GO" : e.act);
      map.flyTo([Number(best.s.lat), Number(best.s.lon)], 15);
    }, function () { out.textContent = "Could not get your location."; });
  });

  var demo = !window.NIKASI_API;
  document.getElementById("banner").textContent = demo ? "DEMO DATA: set the API URL in config.js" : "";
  function load() {
    var url = demo ? "mock_state.json" : window.NIKASI_API;
    fetch(url, {cache: "no-store"}).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (d) {
        var spots = Array.isArray(d) ? d : d.spots;
        if (demo) spots.forEach(function (s) { s.updated_at = new Date(Date.now() - 3 * 60000).toISOString(); }); // demo rows look fresh, except the stale one
        if (demo) spots.forEach(function (s) { if (s.spot_id === "zakhira") s.updated_at = new Date(Date.now() - 70 * 60000).toISOString(); });
        latest = spots; render(spots);
      })
      .catch(function () {
        document.getElementById("banner").textContent = "Cannot reach the server. Treat every underpass as NO-GO.";
      });
  }
  load(); setInterval(load, 60000);
})();

if ("serviceWorker" in navigator) { navigator.serviceWorker.register("sw.js").catch(function () {}); }
