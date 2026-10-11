"""Run Nikasi on your own machine, no AWS: python scripts/local_demo.py  ->  http://localhost:8000

Serves web/ and a /spots endpoint that plays the SYNTHETIC storm from nikasi.replay,
one 15-minute step every few seconds, so you can watch GO -> CAUTION -> NO-GO -> UNKNOWN
live. The banner says it is a simulation. This is a demo of behaviour, not of real rain.
Usage: python scripts/local_demo.py [port] [seconds_per_step]
"""
from __future__ import annotations
import json, os, sys, time
from datetime import datetime, timedelta, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from nikasi import replay

FRAMES = replay.run(replay.scripted_model())
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
SECONDS = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0
T0 = time.time()

def current() -> dict:
    i = int((time.time() - T0) / SECONDS) % len(FRAMES)
    f = FRAMES[i]
    now = datetime.now(timezone.utc)
    # stamp rows with the real clock so the browser's own 45-minute stale check behaves:
    # fresh normally, 70 minutes old during the simulated feed outage.
    stamp = (now - timedelta(minutes=70 if f["outage"] else 1)).isoformat()
    spots = [dict(s, updated_at=stamp) for s in f["spots"]]
    return {"spots": spots, "simulation": True, "sim_time": f["time"], "rain_mm_per_15min": f["rain_mm"]}

class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=os.path.join(ROOT, "web"), **k)
    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/spots":
            return self._send(json.dumps(current()), "application/json")
        if path == "/config.js":
            return self._send('window.NIKASI_API = "/spots"; window.NIKASI_SIM = true;', "application/javascript")
        if path == "/sw.js":   # no offline cache while demoing, so every refresh shows the live step
            return self._send("self.addEventListener('fetch', function(){});", "application/javascript")
        return super().do_GET()
    def _send(self, body: str, ctype: str):
        b = body.encode()
        self.send_response(200); self.send_header("content-type", ctype)
        self.send_header("cache-control", "no-store"); self.send_header("content-length", str(len(b)))
        self.end_headers(); self.wfile.write(b)
    def log_message(self, *a): pass

if __name__ == "__main__":
    print(f"Nikasi local demo: http://localhost:{PORT}  (simulated storm, {SECONDS:g}s per 15-min step)")
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
