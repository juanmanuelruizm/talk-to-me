# talk-to-me — AI English Tutor (CLI)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat&logo=python&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-local-black?style=flat)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

Practice English by having real conversations with an AI tutor, powered by voice recognition and a local LLM.

Hablas por micrófono, la app transcribe tu voz y un LLM local actúa como tutor de inglés: mantiene la conversación, corrige errores y te ayuda a mejorar.

> ¿Primera vez? Sigue la **[Guía rápida paso a paso (GUIA.md)](GUIA.md)** — pensada para empezar en 5 minutos aunque nunca hayas usado Ollama.

### Características

- 🎙️ **Habla o escribe** — practica con tu voz o teclea si no tienes micrófono
- 🧠 **100% local y privado** — todo corre en tu máquina (Ollama + Whisper), sin enviar tu voz a la nube
- ⚡ **Respuesta en streaming** — el tutor responde en tiempo real, palabra a palabra
- 📊 **3 niveles** — beginner, intermediate y advanced, cambiables sobre la marcha
- 🔊 **Voz opcional (TTS)** — el tutor también te puede responder hablando
- 💾 **Guarda tus sesiones** — exporta la conversación a Markdown para repasar
- 🛠️ **Configurable sin tocar código** — variables de entorno o un archivo `.env`

## Cómo funciona

```
Micrófono → faster-whisper (STT) → Prompt + historial → Ollama (LLM) → Respuesta en terminal
     ↑                                                                          |
     └──────────────────── Lees la respuesta y vuelves a hablar ←──────────────┘
```

1. **Hablas** por el micrófono (o escribes texto)
2. **faster-whisper** transcribe tu audio a texto
3. El texto se envía a **Ollama** (Llama 3.1) junto con el historial de conversación y un system prompt de tutor
4. El LLM responde como tutor: te contesta, corrige errores y sugiere mejoras
5. Repites — la conversación se mantiene con contexto

## Requisitos previos

- **Python 3.10+**
- **Ollama** instalado y corriendo ([ollama.com](https://ollama.com))
- **Micrófono** funcional (para el modo de voz)
- **Windows**: PortAudio instalado (se instala automáticamente con `sounddevice` en la mayoría de casos; si hay problemas, instala [PortAudio](http://www.portaudio.com/) manualmente)

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/juanmanuelruizm/talk-to-me.git
cd talk-to-me
```

### 2. Crear entorno virtual e instalar dependencias

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Instalar Ollama y descargar el modelo

```bash
# Instalar Ollama desde https://ollama.com

# Descargar el modelo (una sola vez)
ollama pull llama3.1
```

### 4. Verificar que Ollama está corriendo

```bash
ollama serve   # si no está corriendo como servicio
ollama list    # verificar que llama3.1 aparece
```

## Uso

Desde la raíz del proyecto (recomendado):

```bash
python run.py
```

O entrando a `src`:

```bash
cd src
python main.py
```

### Flujo de la app

1. La app verifica la conexión con Ollama
2. Muestra el prompt esperando input
3. **Pulsa ENTER** para hablar por micrófono — habla en inglés y quédate en silencio para que detecte el fin
4. La transcripción se muestra en pantalla
5. El tutor responde con correcciones y continúa la conversación

### Comandos disponibles

| Comando | Descripción |
|---|---|
| `ENTER` | Grabar audio del micrófono |
| `/text` | Escribir un mensaje manualmente |
| `/level <nivel>` | Cambiar nivel: `beginner`, `intermediate`, `advanced` |
| `/save` | Guardar la conversación en `sessions/` como Markdown |
| `/tts` | Activar/desactivar la voz del tutor (requiere `pyttsx3`) |
| `/reset` | Reiniciar conversación (borrar historial) |
| `/help` | Mostrar ayuda |
| `/quit`, `/exit` | Salir |

También puedes escribir texto directamente sin usar `/text` — cualquier input que no sea un comando se trata como mensaje.

### Ejemplo de sesión

```
============================================================
  English Practice — Conversational AI Tutor
============================================================

Checking Ollama connection (llama3.1)...
Ollama connected

Level: intermediate  |  TTS: off
Press ENTER to start speaking, or type a command.
Type /help for available commands.

[ENTER to speak | /text to type | /help] >
Listening... (speak now)
Recorded 3.2s of audio
Transcribing...

You said: "I have went to the store yesterday"

Tutor: That sounds like a productive day! What did you buy at the store?

Correction: "I have went" → "I went" (use simple past for completed
actions with a specific time like "yesterday", not present perfect).
```

## Configuración

No necesitas tocar código. Puedes configurar todo con **variables de entorno** o, más cómodo, copiando [`.env.example`](.env.example) a `.env` y editándolo:

```bash
cp .env.example .env
# edita .env con tu editor favorito
```

| Parámetro | Default | Descripción |
|---|---|---|
| `WHISPER_MODEL` | `base` | Modelo de Whisper: `tiny`, `base`, `small`, `medium`, `large-v3` |
| `WHISPER_COMPUTE_TYPE` | `int8` | `int8` para CPU, `float16` para GPU |
| `OLLAMA_URL` | `http://localhost:11434` | URL del servidor de Ollama |
| `OLLAMA_MODEL` | `llama3.1` | Modelo de Ollama a usar |
| `OLLAMA_TIMEOUT` | `120` | Timeout (s) para la respuesta del LLM |
| `SILENCE_THRESHOLD` | `0.01` | Umbral RMS para detectar silencio |
| `SILENCE_DURATION` | `1.5` | Segundos de silencio para cortar grabación |
| `MAX_RECORD_SECONDS` | `30` | Máximo de segundos por grabación |
| `TTS_ENABLED` | `false` | Que el tutor responda también con voz (requiere `pyttsx3`) |
| `TTS_RATE` | `170` | Velocidad de la voz (palabras por minuto) |
| `DEFAULT_LEVEL` | `intermediate` | Nivel por defecto del tutor |

Los valores por defecto viven en [`src/config.py`](src/config.py); cualquier variable de entorno o entrada en `.env` los sobreescribe.

**Whisper models**: `tiny` y `base` son más rápidos pero menos precisos; `large-v3` es el más preciso pero requiere más RAM y GPU para ser fluido.

### Voz del tutor (TTS opcional)

Para que el tutor te responda hablando, instala `pyttsx3` (offline, multiplataforma) y actívalo:

```bash
pip install pyttsx3
```

Luego pon `TTS_ENABLED=true` en tu `.env`, o actívalo en cualquier momento dentro de la app con el comando `/tts`.

## Estructura del proyecto

```
talk-to-me/
├── src/
│   ├── main.py       # Loop principal CLI
│   ├── audio.py      # Captura de micrófono + detección de silencio
│   ├── stt.py        # Transcripción con faster-whisper
│   ├── llm.py        # Comunicación con Ollama API (incl. streaming)
│   ├── tts.py        # Text-to-Speech opcional (pyttsx3)
│   ├── prompts.py    # System prompts del tutor (por nivel)
│   └── config.py     # Configuración (con soporte de variables de entorno)
├── sessions/         # Conversaciones guardadas con /save (ignorado por git)
├── run.py            # Lanzador desde la raíz (python run.py)
├── .env.example      # Plantilla de configuración
├── requirements.txt
├── GUIA.md           # Guía rápida paso a paso
├── LICENSE
├── .gitignore
└── README.md
```

## Roadmap

- [x] **Text-to-Speech (TTS)** — Que el tutor también responda con voz (`pyttsx3`)
- [x] **Streaming de respuesta** — Mostrar la respuesta del LLM token a token en tiempo real
- [x] **Persistencia de sesiones** — Guardar historial de conversaciones (`/save`)
- [ ] **Soporte multi-idioma** — Francés, alemán, etc. (cambiar prompts y config de Whisper)
- [ ] **Web UI** — Interfaz web con FastAPI + frontend con grabación de audio en navegador
- [ ] **Métricas de progreso** — Tracking de errores comunes, vocabulario aprendido, etc.

## Licencia

Este proyecto está bajo la licencia MIT. Úsalo, modifícalo y distribúyelo libremente.

## Autor

**Juan Manuel Ruiz Muñoz**

- LinkedIn: [Juan Manuel Ruiz Muñoz](https://www.linkedin.com/in/juan-manuel-ruiz-mu%C3%B1oz/)
- GitHub: [@juanmanuelruizm](https://github.com/juanmanuelruizm)
