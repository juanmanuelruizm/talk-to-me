# talk-to-me — AI English Tutor (CLI)

Practice English by having real conversations with an AI tutor, powered by voice recognition and a local LLM.

Hablas por micrófono, la app transcribe tu voz y un LLM local actúa como tutor de inglés: mantiene la conversación, corrige errores y te ayuda a mejorar.

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
| `/text` | Escribir mensaje manualmente |
| `/level <nivel>` | Cambiar nivel: `beginner`, `intermediate`, `advanced` |
| `/reset` | Reiniciar conversación (borrar historial) |
| `/help` | Mostrar ayuda |
| `/quit` | Salir |

También puedes escribir texto directamente sin usar `/text` — cualquier input que no sea un comando se trata como mensaje.

### Ejemplo de sesión

```
============================================================
  English Practice — Conversational AI Tutor
============================================================

Checking Ollama connection (llama3.1)...
Ollama connected

Level: intermediate
Press ENTER to start speaking, or type a command.
Type /help for available commands.

[ENTER to speak | /text to type | /help] >
Listening... (speak now)
Recorded 3.2s of audio
Transcribing...

You said: "I have went to the store yesterday"

Thinking...

Tutor: That sounds like a productive day! What did you buy at the store?

Correction: "I have went" → "I went" (use simple past for completed
actions with a specific time like "yesterday", not present perfect).
```

## Configuración

Todos los parámetros se configuran en [`src/config.py`](src/config.py):

| Parámetro | Default | Descripción |
|---|---|---|
| `WHISPER_MODEL` | `base` | Modelo de Whisper: `tiny`, `base`, `small`, `medium`, `large-v3` |
| `WHISPER_COMPUTE_TYPE` | `int8` | `int8` para CPU, `float16` para GPU |
| `OLLAMA_MODEL` | `llama3.1` | Modelo de Ollama a usar |
| `SILENCE_THRESHOLD` | `0.01` | Umbral RMS para detectar silencio |
| `SILENCE_DURATION` | `1.5` | Segundos de silencio para cortar grabación |
| `DEFAULT_LEVEL` | `intermediate` | Nivel por defecto del tutor |

## Estructura del proyecto

```
talk-to-me/
├── src/
│   ├── main.py       # Loop principal CLI
│   ├── audio.py      # Captura de micrófono + detección de silencio
│   ├── stt.py        # Transcripción con faster-whisper
│   ├── llm.py        # Comunicación con Ollama API
│   ├── prompts.py    # System prompts del tutor (por nivel)
│   └── config.py     # Configuración general
├── requirements.txt
├── .gitignore
└── README.md
```

## Roadmap

- [ ] **Text-to-Speech (TTS)** — Que el tutor también responda con voz (`piper-tts` o `edge-tts`)
- [ ] **Streaming de respuesta** — Mostrar la respuesta del LLM token a token en tiempo real
- [ ] **Soporte multi-idioma** — Francés, alemán, etc. (cambiar prompts y config de Whisper)
- [ ] **Persistencia de sesiones** — Guardar historial de conversaciones
- [ ] **Web UI** — Interfaz web con FastAPI + frontend con grabación de audio en navegador
- [ ] **Métricas de progreso** — Tracking de errores comunes, vocabulario aprendido, etc.

## Licencia

MIT
