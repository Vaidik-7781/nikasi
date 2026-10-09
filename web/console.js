(function () {
  var cfg = window.NIKASI_COGNITO || {}, api = (window.NIKASI_API || "").replace(/\/spots$/, "");
  var tok = (location.hash.match(/id_token=([^&]+)/) || [])[1] || "", cur = null;
  var $ = function (i) { return document.getElementById(i); };
  function claims(t) { try { return JSON.parse(atob(t.split(".")[1].replace(/-/g, "+").replace(/_/g, "/"))); } catch (e) { return {}; } }
  var redirect = location.origin + location.pathname;
  $("login").href = cfg.domain ? "https://" + cfg.domain + "/login?client_id=" + cfg.clientId + "&response_type=token&scope=openid+email&redirect_uri=" + encodeURIComponent(redirect) : "#";
  if (!cfg.domain || !api) { $("who").textContent = "Not configured: deploy first (config.js is written by scripts/deploy.sh)."; return; }
  if (!tok) { $("who").textContent = "Signed out."; return; }
  var c = claims(tok);
  if (c.exp && c.exp * 1000 < Date.now()) { $("who").textContent = "Session expired. Sign in again."; return; }
  $("who").textContent = "Signed in as " + (c.email || c["cognito:username"] || "unknown");
  $("panel").hidden = false; $("login").hidden = true;
  function call(path, opt) { opt = opt || {}; opt.headers = {authorization: tok, "content-type": "application/json"}; return fetch(api + path, opt).then(function (r) { return r.json().then(function (j) { return {ok: r.ok, status: r.status, body: j}; }); }); }
  function load() {
    $("msg").textContent = ""; $("approve").disabled = true;
    call("/dispatch").then(function (r) {
      if (!r.ok) { $("list").textContent = "Error " + r.status; return; }
      cur = r.body;
      $("list").textContent = cur.spots.length ? cur.text : "No underpass is NO-GO right now.";
      $("approve").disabled = !cur.spots.length;
    }).catch(function () { $("list").textContent = "Cannot reach the server."; });
  }
  $("approve").addEventListener("click", function () {
    $("approve").disabled = true;
    call("/dispatch/approve", {method: "POST", body: JSON.stringify({spots: cur.spots})}).then(function (r) {
      if (r.status === 409) { $("msg").textContent = "Conditions changed. Reloaded: review again."; cur = r.body.current; $("list").textContent = cur.text; $("approve").disabled = !cur.spots.length; return; }
      $("msg").textContent = r.ok ? "Approved by " + r.body.approved_by + " at " + r.body.approved_at : "Could not approve (" + r.status + ").";
    });
  });
  $("reload").addEventListener("click", load);
  load();
})();
