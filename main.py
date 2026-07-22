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


async def send_whatsapp(to: str, text: str):
    url = f"https://api.maytapi.com/api/{MAYTAPI_PRODUCT_ID}/{MAYTAPI_PHONE_ID}/sendMessage"
    RECENT_REPLIES.add(text)
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(
            url,
            headers={"x-maytapi-key": MAYTAPI_TOKEN},
            json={"to_number": to, "type": "text", "message": text},
        )
        print(f"ENVIO a {to}: HTTP {r.status_code} {r.text[:300]}")


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
    # Si MY_PHONE no está configurado o el mensaje viene de cualquier
    # otro número, se ignora por completo. NUNCA se responde a terceros.
    if not MY_PHONE:
        print("BLOQUEADO: MY_PHONE no configurado, nadie recibe respuestas")
        return {"ok": True}
    if sender != MY_PHONE:
        print(f"BLOQUEADO: mensaje de {sender}, no es mi número. Ignorado.")
        return {"ok": True}
    if not text:
        return {"ok": True}

    db.save_message(sender, "user", text)

    try:
        reply = await ask_grok(sender, text)
    except Exception as e:
        print(f"ERROR Grok: {e}")
        reply = "Tuve un problema para pensar la respuesta. Intenta de nuevo en un momento."

    db.save_message(sender, "jarvis", reply)
    await send_whatsapp(sender, reply)
    return {"ok": True}
