from fastapi import APIRouter
from fastapi.responses import HTMLResponse
router = APIRouter()
HTML = '''
<!doctype html><html><head><meta charset="utf-8"><title>LaunchTG-lite v5</title></head>
<body style="font-family: system-ui, sans-serif; max-width: 820px; margin: 40px auto;">
  <h2>LaunchTG-lite v5 (safe)</h2>
  <ul>
    <li><a href="/config_ui">Config UI</a></li>
    <li><a href="/flags">GET /flags</a></li>
    <li><a href="/accounts">GET /accounts</a></li>
    <li><a href="/jobs">GET /jobs</a></li>
  </ul>
  <p>Health: <code>/health</code></p>
</body></html>
'''
@router.get("/ui", response_class=HTMLResponse)
def ui(): return HTML
