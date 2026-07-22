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
    phone = Column(String(120), index=True)         # chat: número o "Nombre <id>"
    role = Column(String(16))                       # "user", "jarvis" u "observed"
    text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class State(Base):
    __tablename__ = "state"

    key = Column(String(64), primary_key=True)
    value = Column(Text)


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)
    kind = Column(String(16))                       # "link" o "nota"
    content = Column(Text)                          # el link o texto original
    description = Column(Text)                      # cómo lo describió el usuario
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    Base.metadata.create_all(engine)
    # Ampliar phone por si la tabla ya existía con varchar(32)
    try:
        from sqlalchemy import text
        with engine.begin() as c:
            c.execute(text("ALTER TABLE messages ALTER COLUMN phone TYPE varchar(120)"))
        print("DB: columna phone ampliada a 120")
    except Exception as e:
        print(f"DB: no se pudo ampliar phone (se truncarán etiquetas): {e}")


def get_state(key: str, default: str = "") -> str:
    with SessionLocal() as s:
        row = s.get(State, key)
        return row.value if row else default


def set_state(key: str, value: str):
    with SessionLocal() as s:
        s.merge(State(key=key, value=value))
        s.commit()


def message_exists(phone: str, text: str) -> bool:
    with SessionLocal() as s:
        return (
            s.query(Message)
            .filter(Message.phone == phone, Message.text == text)
            .first()
            is not None
        )


def observed_since(last_id: int, limit: int = 50):
    """Mensajes observados con id mayor a last_id, en orden."""
    with SessionLocal() as s:
        return (
            s.query(Message)
            .filter(Message.role == "observed", Message.id > last_id)
            .order_by(Message.id.asc())
            .limit(limit)
            .all()
        )


def save_note(kind: str, content: str, description: str):
    with SessionLocal() as s:
        s.add(Note(kind=kind, content=content, description=description))
        s.commit()


def search_notes(query: str, limit: int = 10):
    """Busca notas por coincidencia simple en contenido o descripción."""
    from sqlalchemy import or_
    with SessionLocal() as s:
        q = f"%{query}%"
        return (
            s.query(Note)
            .filter(or_(Note.content.ilike(q), Note.description.ilike(q)))
            .order_by(Note.created_at.desc())
            .limit(limit)
            .all()
        )


def recent_notes(limit: int = 10):
    with SessionLocal() as s:
        return s.query(Note).order_by(Note.created_at.desc()).limit(limit).all()


def save_message(phone: str, role: str, text: str):
    if len(phone) > 120:
        phone = phone[:120]
    try:
        with SessionLocal() as s:
            s.add(Message(phone=phone, role=role, text=text))
            s.commit()
    except Exception as e:
        # Si la columna sigue en varchar(32), reintenta con etiqueta corta
        print(f"DB save retry ({e}): etiqueta truncada")
        with SessionLocal() as s:
            s.add(Message(phone=phone[:32], role=role, text=text))
            s.commit()


def recent_history(phone: str, limit: int = 40):
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


def recent_observed(limit: int = 40):
    """Últimos mensajes observados en chats de terceros (solo lectura)."""
    with SessionLocal() as s:
        rows = (
            s.query(Message)
            .filter(Message.role == "observed")
            .order_by(Message.created_at.desc())
            .limit(limit)
            .all()
        )
    return list(reversed(rows))
