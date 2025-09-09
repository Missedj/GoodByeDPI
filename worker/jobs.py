
import json, asyncio, random, time
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from telethon import TelegramClient, errors
from common.config import settings
from backend.app.db import SessionLocal
from backend.app import models

SAFE_MSG = "Operation blocked: only allowed on chats you own/admin. Use invite links and opt-in targets."

def _get_session_and_proxy(acc: models.Account):
    proxy = None  # attach proxy details here if stored
    return acc.session_path, proxy

async def _client(acc: models.Account):
    session_path, proxy = _get_session_and_proxy(acc)
    return TelegramClient(session_path, settings.telegram_api_id, settings.telegram_api_hash, proxy=proxy)

def _mark_event(db: Session, acc_id: int, level: str, code: str, meta: dict):
    ev = models.Event(account_id=acc_id, level=level, code=code, meta_json=meta)
    db.add(ev); db.commit()

def _set_job_state(db: Session, job_row: models.Job, state: str, err: str | None = None):
    job_row.state = state; job_row.updated_at = datetime.utcnow()
    if err: job_row.last_error = err
    db.add(job_row); db.commit()

def run_job(job_id: int):
    db = SessionLocal()
    job_row = db.query(models.Job).get(job_id)
    if not job_row:
        return
    acc = db.query(models.Account).get(job_row.account_id)
    if not acc:
        _set_job_state(db, job_row, "ERROR", "account_not_found"); return

    kind = job_row.kind
    try:
        if kind == "warmup":
            _job_warmup(db, acc, job_row)
        elif kind == "parser_owned":
            _job_parser_owned(db, acc, job_row)
        elif kind == "cloner_owned":
            _job_cloner_owned(db, acc, job_row)
        elif kind == "inviter_optin":
            _job_inviter_optin(db, acc, job_row)
        else:
            _set_job_state(db, job_row, "ERROR", "unsupported_kind")
            return
        _set_job_state(db, job_row, "DONE", None)
    except Exception as e:
        _set_job_state(db, job_row, "ERROR", str(e))
    finally:
        db.close()

def _job_warmup(db: Session, acc: models.Account, job_row: models.Job):
    """Low-risk actions only: fetch dialogs to keep account fresh."""
    payload = job_row.payload_json or {}
    limit = int(payload.get("dialogs_limit", 50))
    async def go():
        async with (await _client(acc)) as cli:
            async for _ in cli.iter_dialogs(limit=limit):
                pass
    asyncio.run(go())
    _mark_event(db, acc.id, "info", "warmup_ok", {"limit": limit})

def _job_parser_owned(db: Session, acc: models.Account, job_row: models.Job):
    """Export participants only if the account is admin/owner of the target chat."""
    payload = job_row.payload_json or {}
    target = payload.get("chat")  # username or id
    max_members = int(payload.get("max_members", 1000))
    if not target:
        raise ValueError("missing chat")
    members = []
    async def go():
        async with (await _client(acc)) as cli:
            chat = await cli.get_entity(target)
            # Try to check admin rights via participant permissions
            try:
                me = await cli.get_me()
                perms = await cli.get_permissions(chat, me)
                is_admin = bool(getattr(perms, "is_admin", False) or getattr(perms, "is_creator", False))
            except Exception:
                is_admin = False
            if not is_admin:
                raise RuntimeError(SAFE_MSG)
            async for u in cli.iter_participants(chat, limit=max_members):
                if getattr(u, "bot", False) or getattr(u, "deleted", False):
                    continue
                members.append({"id": u.id, "username": u.username, "first_name": u.first_name, "last_name": u.last_name})
    asyncio.run(go())
    _mark_event(db, acc.id, "info", "parser_owned_ok", {"chat": target, "count": len(members)})

def _job_cloner_owned(db: Session, acc: models.Account, job_row: models.Job):
    """Forward/copy messages only if admin in BOTH source and destination."""
    payload = job_row.payload_json or {}
    src = payload.get("source"); dst = payload.get("dest")
    limit = int(payload.get("limit", 50))
    copy_mode = bool(payload.get("copy_mode", False))  # if False -> forward
    if not src or not dst:
        raise ValueError("missing source/dest")
    async def go():
        async with (await _client(acc)) as cli:
            s = await cli.get_entity(src); d = await cli.get_entity(dst)
            me = await cli.get_me()
            try:
                sp = await cli.get_permissions(s, me)
                dp = await cli.get_permissions(d, me)
                ok_src = bool(getattr(sp, "is_admin", False) or getattr(sp, "is_creator", False))
                ok_dst = bool(getattr(dp, "is_admin", False) or getattr(dp, "is_creator", False))
            except Exception:
                ok_src = ok_dst = False
            if not (ok_src and ok_dst):
                raise RuntimeError(SAFE_MSG)
            msgs = []
            async for m in cli.iter_messages(s, limit=limit):
                msgs.append(m)
            msgs.reverse()
            for m in msgs:
                try:
                    if copy_mode:
                        if m.text:
                            await cli.send_message(d, m.text, link_preview=False)
                        elif m.media:
                            path = await cli.download_media(m, file=bytes)
                            await cli.send_file(d, path, caption=m.message or "")
                    else:
                        await cli.forward_messages(d, m)
                    time.sleep(random.uniform(1.0, 2.0))
                except errors.FloodWaitError as fw:
                    time.sleep(fw.seconds + 2)
    asyncio.run(go())
    _mark_event(db, acc.id, "info", "cloner_owned_ok", {"src": src, "dst": dst, "limit": limit})

def _job_inviter_optin(db: Session, acc: models.Account, job_row: models.Job):
    """Safe inviter: create invite link and DM ONLY opt-in contacts; no cold mass-invites."""
    payload = job_row.payload_json or {}
    chat = payload.get("chat")
    contacts = payload.get("contacts", [])
    if not chat:
        raise ValueError("missing chat")
    async def go():
        async with (await _client(acc)) as cli:
            from telethon.tl import functions
            c = await cli.get_entity(chat)
            me = await cli.get_me()
            try:
                perm = await cli.get_permissions(c, me)
                is_admin = bool(getattr(perm, "is_admin", False) or getattr(perm, "is_creator", False))
            except Exception:
                is_admin = False
            if not is_admin:
                raise RuntimeError(SAFE_MSG)
            link = await cli(functions.messages.ExportChatInviteRequest(peer=c, legacy_revoke_per_day=False))
            invite = getattr(link, "link", None) or getattr(link, "url", None) or "https://t.me/"
            sent = 0
            for u in contacts[:50]:
                try:
                    await cli.send_message(u, f"Присоединяйся: {invite}")
                    time.sleep(random.uniform(3.0, 7.0))
                    sent += 1
                except errors.FloodWaitError as fw:
                    time.sleep(fw.seconds + 2)
                except Exception:
                    continue
            return sent
    sent = asyncio.run(go())
    _mark_event(db, acc.id, "info", "inviter_optin_ok", {"chat": chat, "sent": int(sent or 0)})
