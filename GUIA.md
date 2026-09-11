# Guía rápida — talk-to-me

Esta guía te lleva de cero a estar conversando con tu tutor de inglés en unos
**5 minutos**, aunque nunca hayas usado Ollama ni Python. Sigue los pasos en orden.

---

## ✅ Antes de empezar necesitas

1. **Python 3.10 o superior** → comprueba con: `python --version`
2. **Ollama** (el "motor" del tutor) → lo instalamos en el Paso 2
3. **Un micrófono** (opcional: también puedes escribir en vez de hablar)

---

## Paso 1 — Descargar el proyecto

```bash
git clone https://github.com/juanmanuelruizm/talk-to-me.git
cd talk-to-me
```

---

## Paso 2 — Instalar Ollama y el modelo

Ollama es lo que ejecuta el "cerebro" (el LLM) en tu propio ordenador, sin internet.

1. Descárgalo e instálalo desde **[ollama.com](https://ollama.com)**.
2. Descarga el modelo (solo la primera vez, pesa unos GB):

```bash
ollama pull llama3.1
```

3. Comprueba que está listo:

```bash
ollama list      # debe aparecer "llama3.1"
```

> 💡 Ollama normalmente queda corriendo en segundo plano tras instalarlo. Si la
> app te dice que no se puede conectar, abre otra terminal y ejecuta `ollama serve`.

---

## Paso 3 — Instalar las dependencias de Python

Creamos un "entorno virtual" (una caja aislada para las librerías del proyecto):

```bash
python -m venv venv
```

Actívalo:

```bash
# Windows
venv\Scripts\activate

# Linux / Mac
source venv/bin/activate
```

Instala lo necesario:

```bash
pip install -r requirements.txt
```

> ⏳ La primera vez que pulses ENTER para hablar se descargará el modelo de Whisper
> (reconocimiento de voz) automáticamente, antes de empezar a grabar. Es normal que tarde un poco.

---

## Paso 4 — Arrancar la app

```bash
python run.py
```

Si todo va bien verás:

```
============================================================
  English Practice — Conversational AI Tutor
============================================================

Checking Ollama connection (llama3.1)...
Ollama connected

Level: intermediate  |  TTS: off
Press ENTER to start speaking, or type a command.
```

---

## Paso 5 — ¡A practicar!

| Quiero... | Hago... |
|---|---|
| **Hablar por el micrófono** | Pulso `ENTER`, hablo y me quedo en silencio ~1,5 s (o pulso `ENTER` otra vez para cortar) |
| **Escribir en vez de hablar** | Escribo `/text` y pulso Enter |
| **Cambiar de nivel** | `/level beginner`, `/level intermediate` o `/level advanced` |
| **Practicar otro idioma** | `/language es` (también `fr`, `de`, `it`, `pt`, `en`) |
| **Ver lo que llevamos hablado** | `/history` |
| **Que el tutor me hable** | `/tts` (en macOS funciona sin instalar nada; en Linux/Windows: `pip install pyttsx3`) |
| **Guardar la conversación** | `/save` (se guarda en la carpeta `sessions/`; al salir también te lo pregunta) |
| **Empezar de cero** | `/reset` |
| **Ver la ayuda** | `/help` |
| **Salir** | `/quit` |

> ℹ️ También puedes escribir una frase directamente (sin `/text`) y se enviará como mensaje.

### Cómo funciona una ronda

1. Hablas (o escribes) en inglés.
2. La app transcribe tu voz y te muestra: `You said: "..."`.
3. El tutor responde **en tiempo real** corrigiéndote y siguiendo la charla:

```
You said: "I have went to the store yesterday"

Tutor: That sounds productive! What did you buy?

Correction: "I have went" -> "I went" (usa pasado simple con "yesterday").
```

> ⌨️ `Ctrl+C` mientras grabas o mientras el tutor responde cancela solo ese turno; en el
> prompt principal, sale de la app.

---

## ⚙️ Personalizar (opcional)

¿Quieres otro modelo, otra voz o que no te corte tan rápido al hablar? No hace
falta tocar código: copia la plantilla y edita lo que quieras.

```bash
cp .env.example .env
```

Abre `.env` y descomenta lo que necesites, por ejemplo:

```env
WHISPER_MODEL=small      # más preciso que "base" (pero más lento)
OLLAMA_MODEL=llama3.1
TARGET_LANGUAGE=en       # o es, fr, de, it, pt
TTS_ENABLED=true         # el tutor te responde con voz
SILENCE_DURATION=2.0     # te da más tiempo de silencio antes de cortar
```

También puedes pasar opciones al arrancar: `python run.py --level beginner --language fr`.

---

## 🆘 Solución de problemas

**"Could not connect to Ollama..."**
→ Ollama no está corriendo. Abre una terminal y ejecuta `ollama serve`.

**"model 'llama3.1' is not available in Ollama"**
→ Falta descargarlo: `ollama pull llama3.1`. La app te lista los modelos que sí tienes;
puedes usar uno de ellos con `--model <nombre>` o `OLLAMA_MODEL=<nombre>` en `.env`.

**"(no speech detected)"**
→ No se detectó voz en los primeros ~6 s. Comprueba el micro o baja `SILENCE_THRESHOLD`
(p. ej. `0.005`) en tu `.env`. Puedes subir el margen con `NO_SPEECH_TIMEOUT=10`.

**"Audio error" o no detecta el micrófono**
→ Revisa que tu micro funcione y tenga permisos. Mientras lo arreglas, usa `/text`
para escribir. En Windows, si falla, instala [PortAudio](http://www.portaudio.com/).

**Me corta antes de terminar de hablar**
→ Sube `SILENCE_DURATION` (p. ej. `2.0`) en tu `.env`. Si hay ruido de fondo,
sube también `SILENCE_THRESHOLD` (p. ej. `0.02`).

**La transcripción no es buena**
→ Usa un modelo de Whisper más grande: `WHISPER_MODEL=small` o `medium` en `.env`.

**Va lento**
→ Usa un modelo de Whisper más pequeño (`tiny`/`base`) y/o un modelo de Ollama más
ligero. Con GPU, pon `WHISPER_COMPUTE_TYPE=float16`.

**El tutor no habla con `/tts`**
→ En macOS debería funcionar sin instalar nada (usa `say`). En Linux/Windows instala la
librería: `pip install pyttsx3`; en Linux puede que necesites además un motor de voz
del sistema (p. ej. `espeak`).

**El tutor deja de corregir en conversaciones largas**
→ Ya no debería pasar: solo se envían los últimos 20 turnos al modelo (`MAX_HISTORY_TURNS`).
Si quieres que recuerde más, sube `OLLAMA_NUM_CTX=8192` en tu `.env`.

---

¿Listo? Ejecuta `python run.py` y empieza a hablar. 🚀
