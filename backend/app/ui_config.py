from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from .routers.config_api import merge_ini, get_config, export_ini
router = APIRouter()
@router.get("/config_ui", response_class=HTMLResponse)
def ui_form(request: Request):
    return '''
    <!doctype html><html><head><meta charset="utf-8"><title>Config UI</title></head>
    <body style="font-family: system-ui, sans-serif; max-width: 900px; margin: 40px auto;">
      <h3>Config Merge (INI, skip duplicates)</h3>
      <form method="post" action="/config_ui/merge">
        <textarea name="raw" rows="16" style="width:100%"></textarea><br/>
        <button type="submit">Merge</button>
        <a href="/config/export" style="margin-left:8px">Export INI</a>
      </form>
      <hr/>
      <h4>Current (JSON)</h4>
      <pre id="cfg"></pre>
      <script>
      fetch('/config').then(r=>r.json()).then(j=>{document.getElementById('cfg').textContent = JSON.stringify(j,null,2)});
      </script>
    </body></html>
    '''
@router.post("/config_ui/merge", response_class=HTMLResponse)
async def ui_post(request: Request):
    form = await request.form()
    raw = form.get("raw","")
    res = merge_ini(raw)
    return f"<pre>{res}</pre><p><a href='/config_ui'>Back</a></p>"
