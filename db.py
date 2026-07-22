"""Conexión a PostgreSQL y tabla de mensajes (la memoria cruda de JARVIS)."""
import os
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = (
    os.getenv("DATABASE_URL")
    or os.getenv("POSTGRES_URL")
    or "sqlite:///./jarvis_local.db"
)

# Limpiar saltos de línea, espacios y comillas que puedan venir al pegar la variable
DATABASE_URL = DATABASE_URL.strip().strip('"').strip("'").strip()

# Railway a veces entrega postgres:// en vez de postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    phone = Column(String(32), index=True)          # de quién es el mensaje
    role = Column(String(16))                       # "user" o "jarvis"
    text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    Base.metadata.create_all(engine)


def save_message(phone: str, role: str, text: str):
    with SessionLocal() as s:
        s.add(Message(phone=phone, role=role, text=text))
        s.commit()


def recent_history(phone: str, limit: int = 20):
    """Últimos mensajes para darle contexto a Grok."""
    with SessionLocal() as s:
        rows = (
            s.query(Message)
            .filter(Message.phone == phone)
            .order_by(Message.created_at.desc())
            .limit(limit)
            .all()
        )
    return list(reversed(rows))
