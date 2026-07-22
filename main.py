"""JARVIS - backend mínimo: Maytapi webhook -> Grok -> respuesta por WhatsApp."""
import os

import httpx
from fastapi import FastAPI, Request
from dotenv import load_dotenv

import db

load_dotenv()

MAYTAPI_PRODUCT_ID = os.getenv("MAYTAPI_PRODUCT_ID")
MAYTAPI_PHONE_ID = os.getenv("MAYTAPI_PHONE_ID")
MAYTAPI_TOKEN = os.getenv("MAYTAPI_TOKEN") or os.getenv("MAYTAPI_API_TOKEN")
GROK_API_KEY = os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY")
MY_PHONE = os.getenv("MY_PHONE", "")

SYSTEM_PROMPT = (
    "Eres JARVIS, el asistente personal ejecutivo del usuario. "
    "Hablas por WhatsApp: respuestas breves, naturales, amigables, máximo 10 líneas. "
    "Eres proactivo e inteligente, nunca suenas a chatbot genérico. "
    "Respondes siempre en español."
)

app = FastAPI()

# Memoria corta de respuestas enviadas, para no reaccionar a nuestro propio eco
RECENT_REPLIES = set()


@app.on_event("startup")
def startup():
    try:
        db.init_db()
    except Exception as e:
        print(f"WARN: no se pudo inicializar la BD al arrancar: {e}")


@app.get("/")
def health():
    return {"status": "JARVIS vivo"}


async def ask_grok(phone: str, user_text: str) -> str:
    history = db.recent_history(phone)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in history:
        messages.append({"role": "user" if m.role == "user" else "assistant", "content": m.text})
    messages.append({"role": "user", "content": user_text})

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROK_API_KEY}"},
            json={"model": "grok-3-mini", "messages": messages},
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()


def _digits(phone: str) -> str:
    return "".join(c for c in str(phone) if c.isdigit())


async def send_whatsapp(text: str):
    """Envía ÚNICAMENTE a MY_PHONE. No acepta destinatario: es imposible
    enviar a otro número desde ninguna parte del código."""
    if not MY_PHONE:
        print("ENVIO ABORTADO: MY_PHONE no configurado")
        return
    url = f"https://api.maytapi.com/api/{MAYTAPI_PRODUCT_ID}/{MAYTAPI_PHONE_ID}/sendMessage"
    RECENT_REPLIES.add(text)
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(
            url,
            headers={"x-maytapi-key": MAYTAPI_TOKEN},
            json={"to_number": MY_PHONE, "type": "text", "message": text},
        )
        print(f"ENVIO a MI NUMERO: HTTP {r.status_code} {r.text[:300]}")


def _is_me(sender: str) -> bool:
    """Compara por sufijo de dígitos para tolerar prefijos/sufijos del payload."""
    if not MY_PHONE:
        return False
    a, b = _digits(sender), _digits(MY_PHONE)
    if not a or not b:
        return False
    return a.endswith(b[-10:]) or b.endswith(a[-10:])


@app.post("/webhook/maytapi")
async def webhook(request: Request):
    data = await request.json()
    print(f"WEBHOOK payload: {data}")

    msg = data.get("message", {})
    if data.get("type") != "message" or msg.get("type") != "text":
        return {"ok": True}

    text = msg.get("text", "").strip()
    sender = str(data.get("user", {}).get("phone", ""))
    from_me = bool(data.get("user", {}).get("fromMe") or data.get("fromMe"))

    # Guard anti-bucle: si el mensaje saliente lo envió JARVIS, ignorarlo
    if from_me and text in RECENT_REPLIES:
        print("BLOQUEADO: eco de mi propia respuesta. Ignorado.")
        return {"ok": True}

    # REGLA DE SEGURIDAD ABSOLUTA: JARVIS solo habla conmigo.
    # 1) Interruptor maestro. 2) Solo mi número dispara respuesta.
    # 3) El envío siempre va a MY_PHONE, jamás al remitente.
    if os.getenv("JARVIS_DISABLED", "").lower() in ("1", "true", "si"):
        print("BLOQUEADO: interruptor JARVIS_DISABLED activo")
        return {"ok": True}
    if not _is_me(sender):
        print(f"BLOQUEADO: remitente={sender!r} no coincide con MY_PHONE. Ignorado.")
        return {"ok": True}
    if not text:
        return {"ok": True}

    db.save_message(MY_PHONE, "user", text)

    try:
        reply = await ask_grok(MY_PHONE, text)
    except Exception as e:
        print(f"ERROR Grok: {e}")
        reply = "Tuve un problema para pensar la respuesta. Intenta de nuevo en un momento."

    db.save_message(MY_PHONE, "jarvis", reply)
    await send_whatsapp(reply)
    return {"ok": True}
