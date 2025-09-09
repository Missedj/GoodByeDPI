from sqlalchemy import Column, Integer, String, Boolean, Text, TIMESTAMP, JSON, BigInteger
from sqlalchemy.sql import func
from .db import Base
class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    phone = Column(String, unique=True, nullable=False)
    username = Column(String)
    premium = Column(Boolean, default=False)
    session_path = Column(Text, nullable=False)
    status = Column(String, default="NEW", nullable=False)
    next_allowed_at = Column(TIMESTAMP(timezone=True))
    proxy_id = Column(Integer)
    last_error = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
class Proxy(Base):
    __tablename__ = "proxies"
    id = Column(Integer, primary_key=True)
    kind = Column(String, nullable=False)
    host = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    login = Column(String)
    password = Column(String)
    mtproto_secret = Column(String)
    last_ok_at = Column(TIMESTAMP(timezone=True))
    fail_streak = Column(Integer, default=0)
class Job(Base):
    __tablename__ = "jobs"
    id = Column(BigInteger, primary_key=True)
    account_id = Column(Integer, nullable=False)
    kind = Column(String, nullable=False)  # inviter_optin | parser_owned | cloner_owned | warmup
    payload_json = Column(JSON, nullable=False)
    state = Column(String, default="PENDING", nullable=False)
    run_at = Column(TIMESTAMP(timezone=True))
    attempts = Column(Integer, default=0)
    last_error = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
class Event(Base):
    __tablename__ = "events"
    id = Column(BigInteger, primary_key=True)
    account_id = Column(Integer, nullable=True)
    level = Column(String, nullable=False)
    code = Column(String, nullable=False)
    meta_json = Column(JSON)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
