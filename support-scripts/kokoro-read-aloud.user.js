// ==UserScript==
// @name         Kokoro Read Aloud (Self-Hosted)
// @namespace    local.kokoro.tts
// @version      1.0.0
// @description  Read selected text (or page text) using a self-hosted OpenAI-compatible TTS endpoint
// @match        *://*/*
// @grant        GM_xmlhttpRequest
// @grant        GM_getValue
// @grant        GM_setValue
// @grant        GM_registerMenuCommand
// @connect      *
// ==/UserScript==

(function () {
  "use strict";

  const DEFAULTS = {
    baseUrl: "",
    apiKey: "",
    model: "model_q8f16",
    voice: "af_heart",
    speed: 1.0,
    maxChars: 4000,
  };

  let audioEl = null;

  function cfg() {
    return {
      baseUrl: GM_getValue("baseUrl", DEFAULTS.baseUrl),
      apiKey: GM_getValue("apiKey", DEFAULTS.apiKey),
      model: GM_getValue("model", DEFAULTS.model),
      voice: GM_getValue("voice", DEFAULTS.voice),
      speed: Number(GM_getValue("speed", DEFAULTS.speed)),
      maxChars: Number(GM_getValue("maxChars", DEFAULTS.maxChars)),
    };
  }

  function save(next) {
    GM_setValue("baseUrl", next.baseUrl);
    GM_setValue("apiKey", next.apiKey);
    GM_setValue("model", next.model);
    GM_setValue("voice", next.voice);
    GM_setValue("speed", String(next.speed));
    GM_setValue("maxChars", String(next.maxChars));
  }

  function settingsDialog() {
    const current = cfg();
    const baseUrl = prompt(
      "OpenAI-compatible Base URL (example: https://your-host/api/v1)",
      current.baseUrl,
    );
    if (baseUrl === null) return;

    const apiKey = prompt(
      "API key (leave blank if your endpoint has no auth)",
      current.apiKey,
    );
    if (apiKey === null) return;

    const model = prompt("Model", current.model);
    if (model === null || !model.trim()) return;

    const voice = prompt("Voice", current.voice);
    if (voice === null || !voice.trim()) return;

    const speedRaw = prompt("Speed (0.25 to 5)", String(current.speed));
    if (speedRaw === null) return;
    const speed = Math.max(0.25, Math.min(5, Number(speedRaw) || 1));

    const maxCharsRaw = prompt(
      "Maximum characters when no text is selected",
      String(current.maxChars),
    );
    if (maxCharsRaw === null) return;
    const maxChars = Math.max(250, Number(maxCharsRaw) || DEFAULTS.maxChars);

    save({ baseUrl: baseUrl.trim(), apiKey, model: model.trim(), voice: voice.trim(), speed, maxChars });
    alert("Kokoro settings saved.");
  }

  function selectedOrPageText() {
    const selected = window.getSelection()?.toString().trim();
    if (selected) return selected;

    const article = document.querySelector("article");
    const text = (article?.innerText || document.body?.innerText || "").trim();
    return text.slice(0, cfg().maxChars);
  }

  function stop() {
    if (!audioEl) return;
    try {
      audioEl.pause();
      if (audioEl.src) URL.revokeObjectURL(audioEl.src);
      audioEl.remove();
    } finally {
      audioEl = null;
    }
  }

  function speak(text) {
    const current = cfg();
    if (!current.baseUrl) {
      alert("Set your Base URL first: Tampermonkey menu -> Kokoro: Settings");
      return;
    }

    const url = current.baseUrl.replace(/\/$/, "") + "/audio/speech";
    const headers = { "Content-Type": "application/json" };
    if (current.apiKey) headers.Authorization = "Bearer " + current.apiKey;

    const payload = JSON.stringify({
      model: current.model,
      voice: current.voice,
      input: text,
      response_format: "mp3",
      speed: current.speed,
    });

    GM_xmlhttpRequest({
      method: "POST",
      url,
      headers,
      data: payload,
      responseType: "arraybuffer",
      onload: (res) => {
        if (res.status < 200 || res.status >= 300) {
          let message = "TTS failed (HTTP " + res.status + ")";
          try {
            const body = new TextDecoder().decode(new Uint8Array(res.response));
            if (body) message += "\n\n" + body;
          } catch (_) {}
          alert(message);
          return;
        }

        stop();
        const blob = new Blob([res.response], { type: "audio/mpeg" });
        const objectUrl = URL.createObjectURL(blob);

        audioEl = new Audio(objectUrl);
        audioEl.controls = true;
        audioEl.style.position = "fixed";
        audioEl.style.right = "12px";
        audioEl.style.bottom = "12px";
        audioEl.style.zIndex = "2147483647";
        audioEl.style.background = "#fff";
        audioEl.style.border = "1px solid #ccc";
        audioEl.style.borderRadius = "8px";
        document.body.appendChild(audioEl);
        audioEl.play().catch(() => {});
      },
      onerror: () => alert("Network error calling TTS endpoint."),
    });
  }

  function readNow() {
    const text = selectedOrPageText();
    if (!text) {
      alert("No readable text found. Select text first or try another page.");
      return;
    }
    speak(text);
  }

  GM_registerMenuCommand("Kokoro: Read selected/page", readNow);
  GM_registerMenuCommand("Kokoro: Stop", stop);
  GM_registerMenuCommand("Kokoro: Settings", settingsDialog);

  window.addEventListener("keydown", (e) => {
    if (e.altKey && !e.shiftKey && e.key.toLowerCase() === "k") {
      e.preventDefault();
      readNow();
    }
    if (e.altKey && e.shiftKey && e.key.toLowerCase() === "k") {
      e.preventDefault();
      stop();
    }
  });
})();
