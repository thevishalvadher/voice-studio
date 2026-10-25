# 🎙️ Voice Studio

A small voice-cloning text-to-speech tool for **Hindi** and **English**.
Give it a 10–30 second voice sample, type a line, and get a WAV + MP3 in that voice.

- Runs **inside a free Google Colab notebook** (T4 GPU). There is no separate website, link or tunnel, which is what Colab's free tier allows.
- Voices and audio are saved in **your Google Drive**, so they survive restarts.
- Engine: **Resemble AI Chatterbox Multilingual** (MIT licence, OK for commercial use).
  Every output keeps Resemble's invisible **PerTh watermark**, which we never turn off.
- Gujarati is listed but **switched off** until its licence is clear (see `research-plan.md`).

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/thevishalvadher/muskaanpur-voice-studio/blob/main/notebook.ipynb)

---

## 1. Run it in Colab (step by step)

1. Click the **Open in Colab** badge above (or go to <https://colab.research.google.com>, choose **File → Open notebook → GitHub**, paste `thevishalvadher/muskaanpur-voice-studio` and pick `notebook.ipynb`).
2. Menu **Runtime → Change runtime type → Hardware accelerator: T4 GPU → Save**.
3. Run **1. Setup** (click the ▶ button on the cell).
   - The first time it installs packages (about 3 minutes). The runtime may then **restart by itself once**, and Colab may say "session crashed". That is expected.
   - When it says *Connected* again, **run 1. Setup again**.
   - Allow Google Drive access in the pop-up.
   - Wait for `✅ Model 'chatterbox_mtl' ready on CUDA` and `✅ Setup done`.
4. Run **2. Add Voice** and **3. Generate** (below).
5. (Optional) Run **Engine test** at the bottom to hear the Hindi + English test lines in the built-in demo voice.

Next time you open the notebook, just run **1. Setup** again. Your voices are still in Drive.

## 2. Add your first voice

In the **2. Add Voice** section:

1. **Voice name**: for example `Bhola Kaka`.
2. **Language**: Hindi or English (the language the person will speak).
3. **Voice sample**: **upload** a file (WAV/MP3/M4A/OGG/WEBM) **or** click **🎙️ Start recording**, speak for 15–20 seconds, then click **⏹️ Stop**. Recording stops by itself at 30 s. Listen to the preview.
4. Tick **"I have signed consent from this person…"** (required).
5. Click **Save Voice**. After about 20 seconds you will see `✅ Saved 'Bhola Kaka' (14.2 s sample)`.

Tips for a good sample: one person, quiet room, no music, normal speaking style,
and the same language you will generate in. Silence at the start and end is cut automatically.

## 3. Generate audio

In the **3. Generate** section:

1. Pick the **Voice**.
2. Type or paste your text. The character count updates as you type (max 3,000).
3. Click **Generate**. Long text is split into ~250-character parts at `।` `.` `?` `!` and joined with 150 ms pauses.
4. Listen in the player, then click **⬇️ Download WAV** or **⬇️ Download MP3** (192 kbps).
   The files are also saved in Drive at `outputs/<date>/<voice>_0001.wav` and `.mp3`.
5. **Advanced** (closed by default): **Expression** (0.5 = normal, higher = more dramatic) and **Seed**.
   Keep the seed the same so the character always sounds the same.

## 4. Where things are saved (Google Drive)

```
MyDrive/VoiceStudio/
├── voices/
│   ├── voices.json              ← list of all your voices
│   └── bhola_kaka/
│       ├── sample_original.wav  ← what you uploaded/recorded
│       ├── sample_clean.wav     ← mono, trimmed, normalized
│       └── conds.pt             ← cached voice "fingerprint"
└── outputs/
    └── 2026-10-25/
        ├── bhola_kaka_0001.wav
        └── bhola_kaka_0001.mp3
```

Voice samples, audio and personal data are **never** committed to this GitHub repo (see `.gitignore`).

---

## 5. How to test in Colab (checklist)

### Milestone checks

- [ ] **M1 Skeleton**: *1. Setup* finishes with `✅ Setup done`. In Drive, `VoiceStudio/voices/voices.json` and `outputs/` exist. *2. Add Voice* and *3. Generate* both show their fields.
- [ ] **M2 Engine**: run **Engine test**. `hi_test.wav` and `en_test.wav` play, and are saved in `outputs/test/`. The Setup log says `CUDA` (GPU), not `CPU`.
- [ ] **M3 Add Voice**: save a voice. It appears in the Generate voice list. Then **Runtime → Disconnect and delete runtime**, reopen, run *1. Setup* and *3. Generate*: the voice is still in the list.
- [ ] **M4 Generate + download**: paste a ~600-character Hindi paragraph (e.g. all 3 Hindi lines below, twice). You get **one** file, the status says it used several parts, and both download links work. The MP3 opens in CapCut.
- [ ] **M5 Consistency**: generate the same line twice and the two files sound the same. Generate the 3 lines of one language one by one and they sound like one person.
- [ ] **M6 Polish**: try a 6-second sample and see `Sample too short (6 s). Need at least 10 s.` Try saving without ticking consent and you get a polite refusal. Gujarati shows `🔒 Gujarati: coming soon (Blocked: licence)`.

### Listening test

Use the lines in [`tests/test_sentences.json`](tests/test_sentences.json) (3 Hindi + 3 English).
For each voice, generate each line in the matching language and score it **1–5** on:

| What to check | 1 = bad | 5 = great |
|---|---|---|
| **Correct words** | words missing, added or repeated | every word exactly as written |
| **Pronunciation** | sounds English-accented / wrong (watch ज़, ड़, nasal sounds) | natural Hindi / natural English |
| **Voice match** | doesn't sound like the person | family can tell who it is without being told |
| **Consistency** | lines sound like different people | all 3 lines in a row sound like one person |
| **Clean audio** | clicks, robotic buzz, long silences | clean and smooth |

**Pass = an average of 4 or more.** If a voice scores low, first try a cleaner 15–20 s
sample in the same language, and lower **Expression** a little.

### Unit tests (no GPU needed)

The `tests/` folder checks the logic with a **fake engine**, so it runs anywhere in a few seconds.
In Colab (after Setup), run this in a new cell:

```
!cd /content/voice-studio && python -m unittest discover -s tests -t . -v
```

On your own computer: `pip install numpy soundfile pydub ipywidgets` (plus `audioop-lts` on
Python 3.13+), have `ffmpeg` installed, then run the same `python -m unittest …` command in the repo folder.

---

## 6. How the code is organised

| File | What it does |
|---|---|
| `notebook.ipynb` | The Colab notebook: Setup → Add Voice → Generate (+ optional Engine test) |
| `config.py` | All settings in one place (Drive path, 10–30 s limits, 250-char chunks, 150 ms gap, 192 kbps…) |
| `languages.json` | Which languages exist, which engine speaks them, and whether they are enabled |
| `engines/base.py` | The "shape" every engine must have: `load()`, `prepare_voice()`, `synthesize()` |
| `engines/chatterbox_mtl.py` | The Chatterbox Multilingual engine |
| `engines/__init__.py` | Turns an engine name from `languages.json` into a loaded engine (loads each model once) |
| `core/voices.py` | Add / list / load voices in `voices.json` |
| `core/audio_utils.py` | Clean samples (mono, trim, normalize, length check), join parts, make MP3 |
| `core/text_utils.py` | Split long text at sentence ends |
| `core/generate.py` | Text → audio → WAV + MP3 files |
| `ui/notebook_ui.py` | The widgets (form fields and buttons) shown in the notebook |
| `tests/` | Unit tests with a fake engine + `test_sentences.json` |

### Adding a language or engine later

- **Same engine, new language** (Chatterbox supports 23): add an entry to `languages.json`, e.g.
  `"mr": {"label": "Marathi", "engine": "chatterbox_mtl", "language_id": "mr", "enabled": true}`
  (only if Chatterbox lists it). No UI changes needed.
- **New engine** (e.g. a Gujarati model once its licence is clear): create `engines/my_engine.py`
  following `engines/base.py`, add one line to `ENGINE_CLASSES` in `engines/__init__.py`,
  and point the language at it in `languages.json` with `"enabled": true`.

---

## 7. Things to know (limitations)

- **Free Colab is not guaranteed.** Sometimes no GPU is available, and sessions disconnect after
  inactivity or a few hours. Your voices and outputs are safe in Drive; just run Setup again.
- **First Setup is slow** (~5 min: packages + ~3 GB model download) and restarts the runtime once.
  This happens again in every new Colab session.
- **CPU mode works but is very slow.** Always pick the T4 GPU.
- **Hindi quality varies.** Test with the listening checklist before publishing. A clean, same-language sample helps most.
- **Consistency is "same sound", not "identical forever".** The same text + voice + seed gives the
  same audio on the same setup. A new package version or a different GPU may change it slightly.
- **Chatterbox mainly listens to the first ~10 s** of a sample. A longer sample does not hurt, but make sure the start is clean speech.
- **Download buttons** put the file into the page itself. For very long audio, if a button does nothing, get the file from Drive (`outputs/<date>/`).
- **Gujarati is blocked** for licence reasons (see `research-plan.md` §6.8 for ways to unlock it).
- The pip package `chatterbox-tts` is pinned to `0.1.7`. Check Resemble AI's notes before upgrading.
- **Legal:** get signed consent from every voice owner, never clone celebrities, keep the watermark on,
  and declare AI/synthetic audio on YouTube and Meta. This is not legal advice (see `research-plan.md` §4).
