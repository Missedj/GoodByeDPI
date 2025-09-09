from fastapi import FastAPI
from .routers import accounts, proxies, jobs, events, flags, config_api, ui, risk, proxy_sources, proxy_ops
from .ui_config import router as ui_config_router
app = FastAPI(title="LaunchTG-lite v5", version="0.5.2")
app.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
app.include_router(proxies.router, prefix="/proxies", tags=["proxies"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(events.router, tags=["events"])
app.include_router(flags.router, tags=["flags"])
app.include_router(config_api.router, tags=["config"])
app.include_router(ui.router, tags=["ui"])
app.include_router(ui_config_router, tags=["ui"])
from .routers import risk, proxy_sources, proxy_ops  # ensure import
app.include_router(risk.router, tags=["risk"])
app.include_router(proxy_sources.router, tags=["proxy"])
app.include_router(proxy_ops.router, tags=["proxy"])
@app.get("/health")
def health(): return {"status": "ok"}
