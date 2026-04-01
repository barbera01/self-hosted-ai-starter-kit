# Support Scripts

## Kokoro Read Aloud Userscript

File: `support-scripts/kokoro-read-aloud.user.js`

- Install in Tampermonkey.
- Open Tampermonkey menu on any page and run `Kokoro: Settings`.
- Set your OpenAI-compatible TTS base URL (for this repo setup, `https://tts.lab.home-cloud.uk/api/v1`).
- Set API key only if you enabled `KOKORO_WEB_API_KEY`.

This script is safe to publish: it contains no hardcoded secrets.
