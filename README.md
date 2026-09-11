# talk-to-me — AI Language Tutor (CLI)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat&logo=python&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-local-black?style=flat)
![CI](https://github.com/juanmanuelruizm/talk-to-me/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

Practice a language by having real conversations with an AI tutor, powered by voice recognition and a local LLM.

Hablas por micrófono, la app transcribe tu voz y un LLM local actúa como tutor: mantiene la conversación, corrige errores y te ayuda a mejorar. Pensada para practicar inglés, pero también funciona con español, francés, alemán, italiano y portugués.

> ¿Primera vez? Sigue la **[Guía rápida paso a paso (GUIA.md)](GUIA.md)** — pensada para empezar en 5 minutos aunque nunca hayas usado Ollama.

### Características

- 🎙️ **Habla o escribe** — practica con tu voz o teclea si no tienes micrófono
- 🧠 **100% local y privado** — todo corre en tu máquina (Ollama + Whisper), sin enviar tu voz a la nube
- ⚡ **Respuesta en streaming** — el tutor responde en tiempo real, palabra a palabra
- 📊 **3 niveles** — beginner, intermediate y advanced, cambiables sobre la marcha
- 🌍 **Multi-idioma** — inglés, español, francés, alemán, italiano o portugués (`/language`)
- 🔊 **Voz opcional (TTS)** — el tutor también te puede responder hablando (`say` en macOS, `pyttsx3` en el resto)
- 💾 **Guarda tus sesiones** — exporta la conversación a Markdown (`/save`, o al salir)
- 🛠️ **Configurable sin tocar código** — variables de entorno o un archivo `.env`
- ✅ **Tests y CI** — suite de `pytest` sin micrófono ni red, y lint con `ruff`

## Cómo funciona

```
Micrófono → faster-whisper (STT) → Prompt + historial → Ollama (LLM) → Respuesta en terminal (+ voz)
     ↑                                                                          |
     └──────────────────── Lees/escuchas la respuesta y vuelves a hablar ←──────┘
```

1. **Hablas** por el micrófono (o escribes texto)
2. **faster-whisper** transcribe tu audio a texto
3. El texto se envía a **Ollama** junto con el historial reciente y un system prompt de tutor
4. El LLM responde como tutor: te contesta, corrige errores en una línea final `Correction:` y sigue la charla
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

Alternativa: instalar el paquete (te da el comando `talk-to-me`):

```bash
pip install -e .            # solo ejecución
pip install -e ".[tts]"     # + voz del tutor con pyttsx3 (no hace falta en macOS)
pip install -e ".[dev]"     # + pytest y ruff
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

Desde la raíz del proyecto, cualquiera de estas tres formas es equivalente:

```bash
python run.py
python -m talk_to_me
talk-to-me                  # si hiciste pip install -e .
```

Opciones de línea de comandos (todas opcionales; también se pueden fijar en `.env`):

```bash
talk-to-me --level beginner --language es --model qwen2.5:7b
talk-to-me --help
```

### Flujo de la app

1. La app verifica la conexión con Ollama (si el modelo no está, te lista los que sí tienes)
2. Muestra el prompt esperando input
3. **Pulsa ENTER** para hablar por micrófono — habla y quédate en silencio para que detecte el fin, o **pulsa ENTER otra vez** para cortar
4. La transcripción se muestra en pantalla
5. El tutor responde con correcciones y continúa la conversación

### Comandos disponibles

| Comando | Descripción |
|---|---|
| `ENTER` | Grabar audio del micrófono (ENTER de nuevo para parar) |
| `/text [mensaje]` | Escribir un mensaje manualmente |
| `/level <nivel>` | Cambiar nivel: `beginner`, `intermediate`, `advanced` |
| `/language <código>` | Cambiar idioma: `en`, `es`, `fr`, `de`, `it`, `pt` |
| `/history` | Ver la conversación hasta ahora |
| `/save` | Guardar la conversación en `sessions/` como Markdown |
| `/tts` | Activar/desactivar la voz del tutor |
| `/reset` | Reiniciar conversación (borrar historial) |
| `/help` | Mostrar ayuda |
| `/quit`, `/exit` | Salir (si hay turnos sin guardar, pregunta si quieres guardarlos) |

También puedes escribir texto directamente sin usar `/text` — cualquier input que no sea un comando se trata como mensaje. `Ctrl+C` durante una grabación o una respuesta cancela solo ese turno.

### Ejemplo de sesión

```
============================================================
  English Practice — Conversational AI Tutor
============================================================

Checking Ollama connection (llama3.1)...
Ollama connected

Level: intermediate  |  Language: English  |  Model: llama3.1  |  TTS: off
Press ENTER to start speaking, or type a message or a command.
Type /help for available commands.

[ENTER to speak | /text to type | /help] >
Listening... (speak, stay silent to finish, or press ENTER to stop)
Recorded 3.2s of audio
Transcribing...

You said: "I have went to the store yesterday"

Tutor: That sounds like a productive day! What did you buy at the store?

Correction: "I have went" -> "I went" (use simple past for completed
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
| `DEFAULT_LEVEL` | `intermediate` | Nivel por defecto del tutor |
| `TARGET_LANGUAGE` | `en` | Idioma que practicas: `en`, `es`, `fr`, `de`, `it`, `pt` |
| `MAX_HISTORY_TURNS` | `20` | Pares pregunta/respuesta enviados al LLM (0 = todo el historial) |
| `AUTO_SAVE_ON_EXIT` | `false` | Guardar automáticamente al salir (si no, pregunta) |
| `WHISPER_MODEL` | `base` | Modelo de Whisper: `tiny`, `base`, `small`, `medium`, `large-v3` |
| `WHISPER_COMPUTE_TYPE` | `int8` | `int8` para CPU, `float16` para GPU |
| `WHISPER_DEVICE` | `auto` | `auto`, `cpu`, `cuda` |
| `WHISPER_LANGUAGE` | *(vacío)* | Forzar el idioma de transcripción; vacío = sigue a `TARGET_LANGUAGE` |
| `OLLAMA_URL` | `http://localhost:11434` | URL del servidor de Ollama |
| `OLLAMA_MODEL` | `llama3.1` | Modelo de Ollama a usar |
| `OLLAMA_TIMEOUT` | `120` | Timeout (s) para la respuesta del LLM |
| `OLLAMA_NUM_CTX` | `0` | Tamaño de contexto en tokens (0 = default de Ollama) |
| `OLLAMA_TEMPERATURE` | `0.3` | Creatividad del modelo; bajo = más consistente siguiendo el formato de corrección (`-1` = default de Ollama) |
| `SILENCE_THRESHOLD` | `0.01` | Umbral RMS para detectar silencio |
| `SILENCE_DURATION` | `1.5` | Segundos de silencio para cortar grabación |
| `NO_SPEECH_TIMEOUT` | `6` | Segundos sin voz antes de cancelar la grabación |
| `MAX_RECORD_SECONDS` | `30` | Máximo de segundos por grabación |
| `TTS_ENABLED` | `false` | Que el tutor responda también con voz |
| `TTS_BACKEND` | `auto` | `auto` (`say` en macOS, `pyttsx3` en el resto), `say`, `pyttsx3` |
| `TTS_RATE` | `170` | Velocidad de la voz (palabras por minuto) |

Los valores por defecto viven en [`talk_to_me/config.py`](talk_to_me/config.py); cualquier variable de entorno o entrada en `.env` los sobreescribe.

**Whisper models**: `tiny` y `base` son más rápidos pero menos precisos; `large-v3` es el más preciso pero requiere más RAM y GPU para ser fluido.

**Historial**: Ollama trunca el contexto por el principio cuando se llena, lo que en sesiones largas hacía desaparecer el system prompt (y el tutor dejaba de corregir). Por eso solo se envían los últimos `MAX_HISTORY_TURNS` pares; el historial completo se conserva para `/history` y `/save`. Si quieres más memoria, sube `OLLAMA_NUM_CTX` (p. ej. `8192`).

### Voz del tutor (TTS opcional)

- **macOS**: no necesitas instalar nada, se usa el comando `say` del sistema.
- **Linux / Windows**: instala `pyttsx3` (`pip install pyttsx3` o `pip install -e ".[tts]"`). En Linux puede hacer falta un motor de voz como `espeak`.

Actívalo con `TTS_ENABLED=true` en tu `.env`, o en cualquier momento dentro de la app con `/tts`. La línea `Correction:` no se lee en voz alta, solo la parte conversacional.

## Desarrollo

```bash
pip install -e ".[dev]"
pytest              # tests unitarios (no necesitan micrófono, Ollama ni descargar modelos)
ruff check .        # lint
ruff format .       # formato
```

Cada módulo se puede probar por separado: `python -m talk_to_me.audio`, `python -m talk_to_me.stt`, `python -m talk_to_me.llm`, `python -m talk_to_me.tts`.

## Estructura del proyecto

```
talk-to-me/
├── talk_to_me/
│   ├── cli.py        # Loop principal CLI: comandos, turnos de voz/texto, salida
│   ├── audio.py      # Captura de micrófono + detección de silencio (SilenceDetector)
│   ├── stt.py        # Transcripción con faster-whisper
│   ├── llm.py        # Cliente de la API de Ollama (streaming, errores, comprobación de modelo)
│   ├── tts.py        # Text-to-Speech opcional (say / pyttsx3)
│   ├── prompts.py    # System prompt del tutor (por nivel e idioma)
│   ├── session.py    # Historial de la conversación, recorte y exportación a Markdown
│   ├── config.py     # Configuración (variables de entorno / .env)
│   └── __main__.py   # python -m talk_to_me
├── tests/            # pytest
├── sessions/         # Conversaciones guardadas (ignorado por git)
├── run.py            # Lanzador desde la raíz (python run.py)
├── pyproject.toml    # Paquete, extras [tts] [dev], config de ruff/pytest
├── requirements.txt
├── .env.example      # Plantilla de configuración
├── GUIA.md           # Guía rápida paso a paso
├── LICENSE
└── README.md
```

## Roadmap

- [x] **Text-to-Speech (TTS)** — Que el tutor también responda con voz
- [x] **Streaming de respuesta** — Mostrar la respuesta del LLM token a token en tiempo real
- [x] **Persistencia de sesiones** — Guardar historial de conversaciones (`/save`)
- [x] **Soporte multi-idioma** — Español, francés, alemán, italiano, portugués (`/language`)
- [ ] **Web UI** — Interfaz web con FastAPI + frontend con grabación de audio en navegador
- [ ] **Métricas de progreso** — Tracking de errores comunes, vocabulario aprendido, etc.

## Licencia

Este proyecto está bajo la licencia MIT. Úsalo, modifícalo y distribúyelo libremente.

## Autor

**Juan Manuel Ruiz Muñoz**

- LinkedIn: [Juan Manuel Ruiz Muñoz](https://www.linkedin.com/in/juan-manuel-ruiz-mu%C3%B1oz/)
- GitHub: [@juanmanuelruizm](https://github.com/juanmanuelruizm)
