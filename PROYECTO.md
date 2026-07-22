# Proyecto JARVIS

Serás mi compañero de desarrollo durante la creación de un asistente personal llamado JARVIS.

Este proyecto es únicamente para uso personal.

No necesito arquitectura empresarial, patrones complejos ni sobreingeniería.

Prefiero avanzar muy rápido aunque el código no sea perfecto.

La prioridad es que cada nueva función sea utilizable lo antes posible.

Si una solución sencilla funciona, prefiérela sobre una solución elegante.

---

# Stack

Utilizaremos exclusivamente:

* Python
* FastAPI
* Railway
* PostgreSQL
* Maytapi
* API de Grok
* API de Oura
* Google Calendar (más adelante)
* GitHub (más adelante)

No propongas microservicios.

No propongas Kubernetes.

No propongas patrones Enterprise.

Todo puede vivir en un único proyecto mientras siga siendo fácil de entender.

---

# Objetivo

Construiremos un verdadero asistente personal.

Toda la interacción con el usuario será mediante WhatsApp.

No existirá aplicación móvil.

No existirá interfaz web.

WhatsApp será la única interfaz del sistema.

---

# Funcionamiento

Maytapi recibirá todos los mensajes.

Cada mensaje será enviado al backend.

El backend decidirá qué hacer.

Cuando sea necesario consultará a Grok.

Después responderá nuevamente por WhatsApp.

Toda la conversación deberá sentirse como hablar con un asistente personal.

---

# Filosofía

JARVIS debe ser proactivo.

No debe esperar únicamente preguntas.

Debe iniciar conversaciones cuando detecte información importante.

Ejemplos:

"Buenos días."

"Tienes una reunión en una hora."

"Detecté un compromiso importante."

"Dormiste poco."

"¿Quieres mover el entrenamiento para mañana?"

"No has avanzado la tarea principal."

---

# Memoria

JARVIS debe recordar todo lo importante.

Debe aprender:

* mis hábitos
* mis horarios
* mis proyectos
* mis objetivos
* mis rutinas
* mis preferencias

Debe utilizar esa información para responder mejor cada día.

---

# WhatsApp

Toda la interacción ocurre aquí.

El usuario podrá escribir mensajes como:

¿Qué tengo hoy?

¿Qué sigue?

Recuérdame pagar la renta.

Agenda una comida mañana.

Cancela la reunión.

Analiza este PDF.

Resume este documento.

¿Qué opinas de esta conversación?

¿Cómo dormí?

¿Qué debería hacer hoy?

Todo deberá responderse por WhatsApp.

---

# Conversaciones

JARVIS tendrá acceso a mis conversaciones de WhatsApp.

Su función será ayudarme.

Podrá detectar automáticamente:

* reuniones
* pagos
* fechas
* compromisos
* vuelos
* tareas
* cumpleaños
* entregas
* eventos

Nunca responderá mensajes en mi nombre.

Nunca escribirá a otra persona.

Siempre me hablará únicamente a mí.

Ejemplo:

"He detectado que acordaste una reunión el jueves a las 5:00 p. m. ¿Quieres agregarla al calendario?"

---

# Documentos

Todo archivo recibido por WhatsApp podrá analizarse.

Ejemplos:

PDF

Excel

Word

Imagen

Audio

JARVIS deberá identificar automáticamente:

* fechas importantes
* pagos
* tareas
* personas
* eventos
* lugares
* compromisos

Después preguntará si deseo crear recordatorios.

---

# Salud

Cada mañana consultará la API de Oura.

Obtendrá:

* sueño
* HRV
* Readiness
* recuperación
* actividad
* frecuencia cardiaca

Con esa información reorganizará mi agenda.

Nunca dará consejos médicos.

Únicamente adaptará la organización del día.

---

# Recordatorios

JARVIS podrá escribirme sin que yo lo solicite.

Ejemplos:

Buenos días.

Hoy tienes tres pendientes importantes.

Tu reunión comienza en veinte minutos.

Dormiste cinco horas.

Hoy recomiendo trabajo ligero.

Recuerda llamar al banco.

No has estudiado esta semana.

Mañana vence el seguro del automóvil.

---

# Personalidad

Debe sentirse como un verdadero asistente ejecutivo.

No como ChatGPT.

No como un chatbot.

Debe ser:

breve

natural

amigable

proactivo

inteligente

Debe evitar respuestas largas.

Cuando sea posible responderá en menos de diez líneas.

---

# Desarrollo

Quiero desarrollar este proyecto contigo.

No quiero que generes miles de líneas de código de una sola vez.

Trabajaremos función por función.

Cada vez que implementemos una característica debes:

explicar brevemente la idea

escribir únicamente el código necesario

mantener el proyecto funcionando

evitar refactorizaciones innecesarias

si descubres una forma más sencilla de hacer algo, propónla

No compliques el proyecto.

La prioridad es tener un JARVIS funcional lo antes posible.

---

# Regla principal

Siempre piensa:

"¿Cómo haría esto un desarrollador que quiere tener un prototipo funcionando hoy mismo?"

No optimices prematuramente.

Primero haz que funcione.

Después lo mejoraremos.
