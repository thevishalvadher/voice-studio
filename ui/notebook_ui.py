"""
ui/notebook_ui.py - the "Add Voice" and "Generate" sections inside the notebook.

Built with ipywidgets (Python's version of HTML form elements). There is no
separate website, link or server: everything lives in the notebook, which is
what free Colab allows.

The notebook calls three functions from here:
    setup()            - create Drive folders and load the voice model once
    show_add_voice()   - draw the "Add Voice" form
    show_generate()    - draw the "Generate" form
"""

import ipywidgets as widgets
from IPython.display import HTML, display

import config
import engines
from core import StudioError
from core import voices

# Things the two sections share (like global variables in a small JS app).
_state = {
    "sample_path": None,     # the uploaded/recorded file waiting to be saved
    "voice_dropdown": None,  # the Generate section's voice list (refreshed after a save)
}

# Makes widget labels wide enough to read.
WIDE = {"description_width": "initial"}


# ---------------------------------------------------------------------------
# Small helpers for status messages
# ---------------------------------------------------------------------------

def _msg(text, kind="info"):
    """Return a coloured status line as HTML. kind = info / ok / error."""
    colours = {"info": "#555", "ok": "#1a7f37", "error": "#c62828"}
    return f'<div style="color:{colours[kind]};font-size:14px;margin:4px 0">{text}</div>'


# ---------------------------------------------------------------------------
# 1. Setup
# ---------------------------------------------------------------------------

def setup():
    """Create the Drive folders, then load each engine used by an enabled language (once)."""
    voices.ensure_storage()
    print("📁 Voices folder: ", config.voices_dir())
    print("📁 Outputs folder:", config.outputs_dir())
    print(f"🗣️  Saved voices: {len(voices.list_voices())}")

    engine_names = {info["engine"] for info in config.enabled_languages().values()}
    for name in sorted(engine_names):
        engine = engines.get_engine(name)
        print(f"⏳ Loading voice model '{name}' (first time: a few minutes)…")
        engine.load()
        device = getattr(engine, "device", "?")
        print(f"✅ Model '{name}' ready on {device.upper() if device else '?'}")
        if device == "cpu":
            print("⚠️  No GPU found, so this will be VERY slow. "
                  "Go to Runtime → Change runtime type → T4 GPU, then run Setup again.")
    print("✅ Setup done. Now run '2. Add Voice' or '3. Generate'.")


def run_engine_test(sample_path=""):
    """Milestone 2 check: speak a Hindi and an English test line and play them."""
    from IPython.display import Audio

    from core import generate

    try:
        paths = generate.generate_test_lines(sample_path.strip() or None)
    except StudioError as err:
        display(HTML(_msg(f"❌ {err}", "error")))
        return
    for path in paths:
        display(HTML(_msg(f"✅ {path.name} saved to {path}", "ok")))
        display(Audio(filename=str(path)))


# ---------------------------------------------------------------------------
# 2. Add Voice
# ---------------------------------------------------------------------------

# A small HTML + JavaScript box for "upload a file" or "record with the mic".
# When a sample is ready, the JavaScript sends it to Python with
# google.colab.kernel.invokeFunction(...) (Colab's built-in bridge).
RECORDER_HTML = """
<div style="font-family:sans-serif;border:1px solid #ccc;border-radius:8px;padding:10px;margin:6px 0;max-width:600px">
  <b>Voice sample</b>
  <span style="color:#666">(10–30 seconds of ONE person speaking clearly, no music)</span>
  <div style="margin-top:8px">Upload a file: <input type="file" id="mvs-file" accept="audio/*"></div>
  <div style="margin-top:8px">or record with your mic:
    <button id="mvs-rec">🎙️ Start recording</button>
    <span id="mvs-timer" style="margin-left:8px"></span>
  </div>
  <audio id="mvs-preview" controls style="display:none;margin-top:8px;width:100%"></audio>
  <div id="mvs-msg" style="margin-top:6px;color:#444"></div>
</div>
<script>
(function () {
  const MAX_SECONDS = 30;                 // recording stops by itself after this
  const MAX_UPLOAD_MB = 25;
  const fileInput = document.getElementById("mvs-file");
  const recButton = document.getElementById("mvs-rec");
  const timer = document.getElementById("mvs-timer");
  const preview = document.getElementById("mvs-preview");
  const msg = document.getElementById("mvs-msg");
  let recorder = null, chunks = [], seconds = 0, tick = null;

  // Send an audio Blob to Python (the function "mvs_receive_sample").
  async function sendToPython(blob, filename) {
    preview.src = URL.createObjectURL(blob);
    preview.style.display = "block";
    msg.textContent = "Sending sample to the notebook…";
    try {
      const dataUrl = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(blob);
      });
      const base64 = dataUrl.split(",")[1];
      await google.colab.kernel.invokeFunction("mvs_receive_sample", [base64, filename], {});
      msg.textContent = "✅ Sample ready (" + filename + "). Listen to it above, then click Save Voice below.";
    } catch (err) {
      msg.textContent = "❌ Could not send the sample. Run the Setup cell, then this cell again. (" + err + ")";
    }
  }

  // Option 1: upload a file
  fileInput.onchange = () => {
    const file = fileInput.files[0];
    if (!file) return;
    if (file.size > MAX_UPLOAD_MB * 1024 * 1024) {
      msg.textContent = "❌ File is too big. Please use a file under " + MAX_UPLOAD_MB + " MB (30 seconds is enough).";
      return;
    }
    sendToPython(file, file.name);
  };

  // Option 2: record with the microphone
  recButton.onclick = async () => {
    if (recorder && recorder.state === "recording") { recorder.stop(); return; }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      recorder = new MediaRecorder(stream);
      chunks = []; seconds = 0;
      recorder.ondataavailable = (e) => chunks.push(e.data);
      recorder.onstop = () => {
        clearInterval(tick);
        stream.getTracks().forEach((t) => t.stop());   // switch the mic off
        recButton.textContent = "🎙️ Record again";
        const type = recorder.mimeType || "audio/webm";
        const ext = type.includes("ogg") ? "ogg" : (type.includes("mp4") ? "m4a" : "webm");
        sendToPython(new Blob(chunks, { type: type }), "recording." + ext);
      };
      recorder.start();
      recButton.textContent = "⏹️ Stop";
      msg.textContent = "Recording… speak naturally for 15–20 seconds.";
      timer.textContent = "0 s";
      tick = setInterval(() => {
        seconds += 1;
        timer.textContent = seconds + " s";
        if (seconds >= MAX_SECONDS) recorder.stop();
      }, 1000);
    } catch (err) {
      msg.textContent = "❌ Could not use the microphone. Allow mic access in your browser and try again. (" + err + ")";
    }
  };
})();
</script>
"""


def _receive_sample(base64_audio, filename):
    """Called from the JavaScript above: save the sample to a temp file."""
    import base64
    from pathlib import Path

    config.TEMP_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = Path(filename).name.replace(" ", "_") or "sample.wav"
    path = config.TEMP_DIR / safe_name
    path.write_bytes(base64.b64decode(base64_audio))
    _state["sample_path"] = path


def show_add_voice():
    """Draw the "Add Voice" form."""
    enabled = config.enabled_languages()
    name_box = widgets.Text(description="Voice name", placeholder="e.g. Bhola Kaka", style=WIDE)
    language_dd = widgets.Dropdown(
        description="Language",
        options=[(info["label"], code) for code, info in enabled.items()],
        style=WIDE,
    )
    # Languages that exist but are switched off (e.g. Gujarati) are shown as "coming soon".
    coming_soon = ", ".join(
        f'{info["label"]} ({info.get("note", "not ready")})'
        for info in config.disabled_languages().values()
    )
    soon_note = widgets.HTML(_msg(f"Coming soon: {coming_soon}") if coming_soon else "")

    consent_cb = widgets.Checkbox(
        description="I have signed consent from this person to clone their voice (required)",
        style=WIDE,
        layout=widgets.Layout(width="auto"),
    )
    save_btn = widgets.Button(description="Save Voice", button_style="primary", icon="save")
    status = widgets.HTML()

    def on_save(_button):
        save_btn.disabled = True
        status.value = _msg("⏳ Cleaning the sample and learning the voice (about 20 seconds)…")
        try:
            voice = voices.add_voice(
                name_box.value, language_dd.value, _state["sample_path"], consent_cb.value
            )
        except StudioError as err:
            status.value = _msg(f"❌ {err}", "error")
        except Exception as err:
            status.value = _msg(
                f"❌ Something went wrong: {err}. Try again, or run the Setup cell again.", "error"
            )
        else:
            status.value = _msg(
                f"✅ Saved '{voice['name']}' ({voice['sample_seconds']} s sample). "
                "Pick it in the Generate section below.", "ok"
            )
            _state["sample_path"] = None
            name_box.value = ""
            consent_cb.value = False
            refresh_voice_list()
        finally:
            save_btn.disabled = False

    save_btn.on_click(on_save)

    # Connect the JavaScript recorder to Python (only works inside Colab).
    try:
        from google.colab import output
        output.register_callback("mvs_receive_sample", _receive_sample)
        recorder = HTML(RECORDER_HTML)
    except ImportError:
        recorder = HTML(_msg("Upload and recording only work inside Google Colab.", "error"))

    display(widgets.VBox([name_box, language_dd, soon_note]))
    display(recorder)
    display(widgets.VBox([consent_cb, save_btn, status]))


# ---------------------------------------------------------------------------
# 3. Generate
# ---------------------------------------------------------------------------

def _voice_options():
    """Voice dropdown entries: ("Bhola Kaka (Hindi)", "bhola_kaka")."""
    languages = config.load_languages()
    options = []
    for voice in voices.list_voices():
        label = languages.get(voice["language"], {}).get("label", voice["language"])
        options.append((f'{voice["name"]} ({label})', voice["id"]))
    return options


def refresh_voice_list():
    """Reload the Generate section's voice list (called after saving a voice)."""
    dropdown = _state["voice_dropdown"]
    if dropdown is not None:
        dropdown.options = _voice_options()


def show_generate():
    """Draw the "Generate" form."""
    voice_dd = widgets.Dropdown(description="Voice", options=_voice_options(), style=WIDE)
    _state["voice_dropdown"] = voice_dd

    text_box = widgets.Textarea(
        placeholder="Type or paste Hindi or English text here…",
        layout=widgets.Layout(width="100%", max_width="700px", height="150px"),
    )
    char_count = widgets.HTML(_msg("0 characters"))

    def on_text_change(change):
        n = len(change["new"])
        if n > config.MAX_TEXT_CHARS:
            char_count.value = _msg(f"{n} characters (too long: max {config.MAX_TEXT_CHARS})", "error")
        else:
            char_count.value = _msg(f"{n} characters")

    text_box.observe(on_text_change, names="value")

    # One small "Advanced" area, closed by default.
    defaults = config.DEFAULT_SETTINGS
    exaggeration = widgets.FloatSlider(
        description="Expression", value=defaults["exaggeration"],
        min=0.25, max=2.0, step=0.05, style=WIDE,
    )
    seed = widgets.IntText(description="Seed", value=defaults["seed"], style=WIDE)
    advanced_help = widgets.HTML(_msg(
        "Expression: 0.5 = normal, higher = more dramatic. "
        "Seed: keep it the same so the voice stays consistent. "
        "Both reset to the voice's saved values when you pick a voice."
    ))
    advanced = widgets.Accordion(children=[widgets.VBox([advanced_help, exaggeration, seed])])
    advanced.set_title(0, "Advanced")
    advanced.selected_index = None  # closed

    gen_btn = widgets.Button(description="Generate", button_style="success", icon="play")
    status = widgets.HTML()
    player = widgets.Output()

    def on_generate(_button):
        status.value = _msg("Generate is not ready yet (coming in Milestone 4).")

    gen_btn.on_click(on_generate)

    if not voice_dd.options:
        status.value = _msg("No voices yet. Add one in the 'Add Voice' section above.")

    display(widgets.VBox([voice_dd, text_box, char_count, advanced, gen_btn, status, player]))
