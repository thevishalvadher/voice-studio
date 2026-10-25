# Muskaanpur ki Kahaniyan Voice Studio: Research Report and Build Plan (checked 25 Oct 2026)

**Short answer:** Build your tool on **Chatterbox Multilingual v3 by Resemble AI**. Its code and weights are MIT-licensed, it clones a voice from a short clip, and it officially supports **Hindi and English**. [clore](https://docs.clore.ai/guides/audio-and-voice/chatterbox-tts) [huggingface](https://huggingface.co/ResembleAI/chatterbox/blob/refs%2Fpr%2F48/README.md) Run it free on **Google Colab** and keep your voices in **Google Drive**, so the cost is **₹0/month**. **Gujarati is the hard part.** Every open model I found that clones Gujarati voices was trained on data whose commercial terms are unclear, so under your own rule none of them can go in the recommended stack yet. The plan therefore builds Hindi and English first, keeps a Gujarati slot ready, and gives you two clean ways to unlock it.

## TL;DR

- **Use now (commercial use is a clear YES):** Chatterbox Multilingual v3 for Hindi and English. It is MIT-licensed, it clones from about a 10-second clip with no transcript needed, and every output carries a hidden PerTh watermark. Hosting is free Google Colab with voices saved to Google Drive, so ₹0/month. Upgrade to a paid Colab tier only if the free GPU limits keep stopping you.
- **Gujarati is UNCLEAR, so it is left out for now:** Chatterbox Indic LoRA, IndicF5, Indic-Mio and svara-TTS all support Gujarati. Each was trained on data with unclear or non-commercial terms (the IIT Madras IndicTTS database, or Expresso, which is CC BY-NC). To unlock Gujarati, either get written permission from IIT Madras, or train your own Gujarati LoRA for Chatterbox using only CC-BY-4.0 data (AI4Bharat Rasa).
- **Rejected because commercial use is NO:** XTTS-v2 (non-commercial Coqui licence) and the official F5-TTS weights (CC-BY-NC). Before you publish, get written consent from every voice owner. Tick YouTube's "altered or synthetic content" box and add Meta's "AI info" label whenever a voice is realistic. Leave the watermark on.

---

## 1. Summary (plain English)

| Language | Recommended model (v1) | Status |
|---|---|---|
| Hindi | Chatterbox Multilingual v3 (base), using `language_id="hi"` | ✅ Use now |
| English | Chatterbox Multilingual v3 (base), using `language_id="en"` | ✅ Use now |
| Gujarati | None yet. The slot is reserved in the code. | ⏳ Blocked until the licence is clear (see Risks) |

- **Hosting:** Google Colab free tier with a T4 GPU and a Gradio web UI, which gives you a public link. Voices and outputs are saved in Google Drive.
- **Monthly cost:** ₹0. A paid Colab tier is an optional upgrade, not a requirement.
- **Why Chatterbox:** Resemble AI released Multilingual v3 on 10 June 2026. It says v3 "continues the Chatterbox tradition of MIT licensing" and improves speaker similarity and reduces hallucination compared with v2. Resemble rates its Hindi as "usable in production with appropriate testing", landing in the 6–8% character error rate band. [resemble](https://www.resemble.ai/resources/chatterbox-multilingual-v3-tts-with-embedded-watermarking-for-25-languages)
- **Why not one model for everything:** No model I found is both commercial-safe *and* supports Gujarati voice cloning.

---

## 2. Comparison table

All pages were checked on **25 Oct 2026**. "Commercial" means commercial use on monetized YouTube, Instagram or Facebook.

| Model | Languages (hi / gu / en) | Voice cloning | Hardware | Commercial | Licence + link | Verified |
|---|---|---|---|---|---|---|
| **Chatterbox Multilingual v3** (Resemble AI) | hi ✅ / gu ❌ / en ✅ (23 languages) | Zero-shot from a short clip (about 10 s). No transcript needed. | GPU recommended. CPU works but is slow. | **YES** | MIT (code: github.com/resemble-ai/chatterbox LICENSE; weights: huggingface.co/ResembleAI/chatterbox, `license: mit`) [github](https://github.com/resemble-ai/chatterbox/blob/master/LICENSE) [huggingface](https://huggingface.co/ResembleAI/chatterbox/blob/main/README.md) | 25 Oct 2026 | [clore](https://docs.clore.ai/guides/audio-and-voice/chatterbox-tts) [huggingface](https://huggingface.co/ResembleAI/chatterbox/blob/refs%2Fpr%2F48/README.md)
| Chatterbox Multilingual **Hindi pack** (`Chatterbox-Multilingual-hi`) | hi only | Zero-shot. Lower Hindi error rate (2.55% CER). [resemble](https://www.resemble.ai/resources/chatterbox-multilingual-v3-tts-with-embedded-watermarking-for-25-languages) | GPU | **UNCLEAR** (no licence line visible on its own card; the blog implies MIT) | huggingface.co/ResembleAI/Chatterbox-Multilingual-hi | 25 Oct 2026 | [resemble](https://www.resemble.ai/resources/chatterbox-multilingual-v3-tts-with-embedded-watermarking-for-25-languages)
| **Chatterbox Indic LoRA** (reenigne314) | hi ✅ / gu ✅ (CER 0.2377) / en ✅ | Zero-shot through Chatterbox, but trained on only 2 speakers per language | GPU (CUDA install shown) | **UNCLEAR** | LoRA: MIT; base: ResembleAI/chatterbox (MIT); training data: IndicTTS (IIT Madras custom licence) + AI4Bharat Rasa. huggingface.co/reenigne314/chatterbox-indic-lora | 25 Oct 2026 | [huggingface](https://huggingface.co/reenigne314/chatterbox-indic-lora)
| **svara-TTS v1** (Kenpath) | hi ✅ / gu ✅ / en ✅ (19 languages) | **No audio cloning.** It uses "zero-shot voice selection via speaker IDs". | GPU or CPU (GGUF) | **UNCLEAR** | Apache-2.0; base canopylabs/3b-hi-ft-research_release (Apache-2.0, built on Llama-3.2-3B); data: SYSPIN, Rasa, IndicTTS. huggingface.co/kenpath/svara-tts-v1 | 25 Oct 2026 | [huggingface](https://huggingface.co/kenpath/svara-tts-v1/blob/d4d935131e7658fefaf2a3f8b5c60c06543dba6f/README.md)
| **IndicF5** (AI4Bharat) | hi ✅ / gu ✅ / en ❌ (11 Indic languages) | Zero-shot. Needs the reference audio **and its transcript**. | GPU | **UNCLEAR** | MIT (gated); data: Rasa, IndicTTS, LIMMITS, IndicVoices-R. huggingface.co/ai4bharat/IndicF5 | 25 Oct 2026 | [huggingface](https://huggingface.co/ai4bharat/IndicF5)
| **Indic-Mio** (SPRINGLab, 2026) | hi ✅ / gu ✅ / en ✅ (22 Indic languages + English) | Zero-shot through codec speaker embeddings | GPU (RTF under 0.1) [huggingface](https://huggingface.co/SPRINGLab/Indic-Mio) | **UNCLEAR** | Apache-2.0 tag, but trained on Expresso (CC BY-NC 4.0) + IndicTTS. huggingface.co/SPRINGLab/Indic-Mio [huggingface](https://huggingface.co/SPRINGLab/Indic-Mio/blob/main/README.md) [huggingface](https://huggingface.co/datasets/ylacombe/expresso) | 25 Oct 2026 | [huggingface](https://huggingface.co/SPRINGLab/Indic-Mio/blob/main/README.md)
| **Indic-Speak** (Bodhan AI / AI4Bharat, 2026) | hi / gu / en | **No cloning.** Library voices only. [huggingface](https://huggingface.co/bodhan-ai/indic-speak) | GPU | Not applicable (no cloning) | Indic Open Model License v1.0. huggingface.co/bodhan-ai/indic-speak [huggingface](https://huggingface.co/bodhan-ai/indic-speak) | 25 Oct 2026 |
| **VoxCPM2** (OpenBMB) | hi ✅ / gu ❌ / en ✅ (30 languages) | Zero-shot. Transcript is optional. | GPU (2B parameters, RTF about 0.30 on an RTX 4090) [voxcpm](https://voxcpm.net/) | **YES** | Apache-2.0. huggingface.co/openbmb/VoxCPM2 [huggingface](https://huggingface.co/openbmb/VoxCPM2) | 25 Oct 2026 |
| **XTTS-v2** (Coqui) | hi ✅ / gu ❌ / en ✅ | About a 6 s clip [medium](https://medium.com/@emile1/xtts-v2-high-quality-generative-text-to-speech-made-easy-db6c54c9c40a) | GPU | **NO** | Coqui Public Model License 1.0.0: "allows only non-commercial use of a machine learning model and its outputs" [huggingface](https://huggingface.co/trandackhoa/viTTS/commit/cb13b948857585b2b6e55b452253c96203056c38) | 25 Oct 2026 | [pinggy](https://pinggy.io/blog/best_open_source_self_hosted_text_to_speech_models/)
| **F5-TTS** (official weights) | zh / en | Zero-shot | GPU | **NO** | Code MIT; weights CC-BY-NC because of the Emilia training data. github.com/SWivid/F5-TTS [github](https://github.com/swivid/f5-tts) | 25 Oct 2026 | [arxiv](https://arxiv.org/pdf/2609.11246)
| **OpenF5-TTS-Base** | en | Zero-shot | GPU | **YES**, but it is an alpha release and "inferior to the official NC-licensed F5-TTS model" [huggingface](https://huggingface.co/mrfakename/OpenF5-TTS-Base) | Apache-2.0. huggingface.co/mrfakename/OpenF5-TTS-Base [huggingface](https://huggingface.co/mrfakename/OpenF5-TTS-Base) | 25 Oct 2026 |
| Indic Parler-TTS, CosyVoice, Kokoro | — | Not verified in this pass | — | **Not verified, so excluded** | — | — |

**How to read this:** Under your rule, only **YES** models are allowed in the stack. For Hindi and English, Chatterbox Multilingual v3 is the best fit because it has the simplest cloning (no transcript), the clearest licence, and a single engine for both languages. VoxCPM2 is the backup YES option for Hindi and English.

---

## 3. Licensing details (first pass and second pass)

### Chatterbox Multilingual v3: **YES**
- **Code:** MIT. The GitHub LICENSE file reads "Copyright (c) 2025 Resemble AI … Permission is hereby granted, free of charge … to use, copy, modify, merge, publish, distribute, sublicense, and/or sell". [github](https://github.com/resemble-ai/chatterbox/blob/master/LICENSE)
- **Weights:** The Hugging Face card metadata says `license: mit` and lists `hi` and `en`. [huggingface](https://huggingface.co/ResembleAI/chatterbox/blob/main/README.md) [huggingface](https://huggingface.co/ResembleAI/chatterbox/blob/refs%2Fpr%2F48/README.md)
- **Training data:** Not published in detail. Resemble says v3 grew its multilingual training mix "from 25.6k hours to 36.7k hours". [resemble](https://www.resemble.ai/resources/chatterbox-multilingual-v3-tts-with-embedded-watermarking-for-25-languages) No data licence restriction is passed on to users.
- **Watermark:** v3 "ships with PerTh watermarking embedded by default on every self-hosted audio output". [resemble](https://www.resemble.ai/resources/chatterbox-multilingual-v3-tts-with-embedded-watermarking-for-25-languages) **Keep it on.**
- **Attribution:** MIT only requires keeping the licence notice if you *redistribute the software*. [oakgen](https://oakgen.ai/blog/chatterbox-tts-open-source-review) Nothing is required on your videos.

### Chatterbox Indic LoRA (Gujarati): **UNCLEAR**
- **LoRA licence:** MIT. **Base model:** ResembleAI/chatterbox (MIT). [huggingface](https://huggingface.co/reenigne314/chatterbox-indic-lora)
- **Training data:** Gujarati used "~10h (IndicTTS + ai4bharat Rasa)". [huggingface](https://huggingface.co/reenigne314/chatterbox-indic-lora) Rasa is CC-BY-4.0, which is fine. [huggingface](https://huggingface.co/sulabhkatiyar/indic-tts-mini-train) The IndicTTS database is the problem. IIT Madras keeps the notice "COPYRIGHT 2016 TTS Consortium, TDIL, Meity … ALL RIGHTS RESERVED" and requires you to agree to its "License For Use of Indic TTS" before downloading. [kaggle +2](https://www.kaggle.com/datasets/kavyamanohar/indic-tts-malayalam-speech-corpus) I could not read that licence PDF, and the secondary sources disagree about it (see the conflicts below).
- **Quality warning:** The card itself says "Naturalness (MOS), speaker similarity, and prosody have not been formally evaluated yet" and "2 speakers per language". [huggingface](https://huggingface.co/reenigne314/chatterbox-indic-lora)

### svara-TTS: **UNCLEAR**, and it does not do audio cloning
- The card says Apache-2.0 and the base model card says Apache-2.0, but that base sits on top of Llama-3.2-3B-Instruct, which brings in Meta's Llama 3.2 Community License. [huggingface](https://huggingface.co/canopylabs/3b-hi-ft-research_release) [huggingface](https://huggingface.co/kenpath/svara-tts-v1/blob/d4d935131e7658fefaf2a3f8b5c60c06543dba6f/README.md)
- Training data includes IndicTTS, and the card notes "Each dataset's license/terms apply". [huggingface](https://huggingface.co/kenpath/svara-tts-v1/blob/d4d935131e7658fefaf2a3f8b5c60c06543dba6f/README.md)

### IndicF5: **UNCLEAR**
- Licence MIT (gated). Terms of use: "By using this model, you agree to only clone voices for which you have explicit permission." [huggingface](https://huggingface.co/ai4bharat/IndicF5)
- Training data includes IndicTTS and LIMMITS. [huggingface](https://huggingface.co/ai4bharat/IndicF5) I could not verify LIMMITS terms. AI4Bharat now recommends Indic-Speak instead, [huggingface](https://huggingface.co/ai4bharat/IndicF5) and that model has no cloning.

### Indic-Mio: **UNCLEAR**
- It is tagged Apache-2.0, but its English training used Expresso, which "is distributed under the CC BY-NC 4.0 license", plus IndicTTS. [huggingface +2](https://huggingface.co/SPRINGLab/Indic-Mio)

### XTTS-v2 and F5-TTS: **NO**
- XTTS-v2 weights use the CPML, which is non-commercial, and that covers the audio outputs too. F5-TTS pretrained weights are "licensed under the CC-BY-NC license due to the training data Emilia". [promptquorum +3](https://www.promptquorum.com/power-local-llm/coqui-tts-review)

### Second-pass verification: conflicts found
1. **IndicTTS licence.** SPRINGLab's Hugging Face re-uploads are tagged CC-BY-4.0, [huggingface](https://huggingface.co/datasets/SPRINGLab/IndicTTS_Tamil/blob/6bd9a353470ac39918360ce3169da0b774c9724c/README.md) but that is the re-uploader's own label, not IIT Madras's licence. One developer's model card calls the IndicTTS licence "permissive … allows derivative works". [huggingface](https://huggingface.co/voxaura-labs/vaakya-open/blob/2f78aefb54fbbae59c84abfec4c6a63e57f417a4/README.md) A CIS India page says "Start-ups and businesses that want to use the data can sign a Memorandum Of Understanding". [cis-india](https://voice.cis-india.org/indic-tts.html) **Result: UNCLEAR.** This affects the Indic LoRA, svara, IndicF5 and Indic-Mio.
2. **Indic-Mio:** The Apache-2.0 tag conflicts with its CC BY-NC training data. **UNCLEAR.**
3. **svara:** Third-party sites claim "zero-shot speaker adaptation", but the official card only claims voice selection by speaker ID. [huggingface](https://huggingface.co/kenpath/svara-tts-v1/blob/d4d935131e7658fefaf2a3f8b5c60c06543dba6f/README.md) [dev](https://dev.co/ai/llms/svara-tts-v1) **I trust the official card.**
4. **canopylabs base:** A blog says Apache covers both code and weights. The card says Apache-2.0 but is built on Llama 3.2. [huggingface](https://huggingface.co/canopylabs/3b-hi-ft-research_release) [codersera](https://codersera.com/blog/install-and-run-orpheus-3b-tts-on-macos-a-complete-guide/) **Llama terms may also apply.**
5. **Chatterbox language count:** The model card lists 23 languages. The v3 blog says "25 total languages (including 4 dialects…)", [resemble](https://www.resemble.ai/resources/chatterbox-multilingual-v3-tts-with-embedded-watermarking-for-25-languages) [huggingface](https://huggingface.co/ResembleAI/chatterbox) and its list differs (it adds Czech and Vietnamese). [huggingface](https://huggingface.co/ResembleAI/chatterbox/blob/refs%2Fpr%2F48/README.md) [resemble](https://www.resemble.ai/resources/chatterbox-multilingual-v3-tts-with-embedded-watermarking-for-25-languages) Hindi and English appear in both lists, so this does not affect you.
6. **Hindi pack error rate:** The v3 table shows 2.55%, but the text says "2.55 - 6.72%". [resemble](https://www.resemble.ai/resources/chatterbox-multilingual-v3-tts-with-embedded-watermarking-for-25-languages) [resemble](https://www.resemble.ai/resources/chatterbox-multilingual-v3-tts-with-embedded-watermarking-for-25-languages) **Test it yourself.**
7. **VoxCPM2 Hindi quality:** The PyPI page shows one Hindi error score of 19.699 (worse than ElevenLabs at 5.827), while GitHub shows Hindi CER 0.79%. [pypi](https://pypi.org/project/voxcpm/) [github](https://github.com/OpenBMB/VoxCPM) These come from different test sets. **Test before relying on it.**
8. **Watermark:** Resemble says the watermark is on by default. [resemble](https://www.resemble.ai/resources/chatterbox-multilingual-v3-tts-with-embedded-watermarking-for-25-languages) In a Hacker News thread, one user asked whether it can be disabled by simply commenting out the `apply_watermark` call in `tts.py`, and another pointed to a `--no-watermark` flag. **The licence does not require it, but keep it on.**

---

## 4. Legal checklist (do these before publishing)

*This is not legal advice. Ask an Indian lawyer to confirm points 1–3, especially if the channel starts earning well.*

1. **Get written consent from each voice owner (DPDP Act 2023).** A voice recording of a known person is personal data. Section 6(1) of the DPDP Act 2023 says consent must be "free, specific, informed, unconditional and unambiguous with a clear affirmative action", limited to the stated purpose, and commentators add that withdrawing it must be as easy as giving it. Keep the signed form and the original recording together.
2. **Respect personality rights.** In *Arijit Singh v. Codible Ventures LLP* (ad-interim order, 26 Jul 2024), the Bombay High Court held that AI tools copying a singer's voice without consent violate his personality rights, because a voice is "a key component of their personal identity and public persona." Never clone a celebrity, and never clone anyone without signed consent, even as a joke.
3. **Know the India IT Amendment Rules 2026.** MeitY notified them on 10 Feb 2026 and they took effect on 20 Feb 2026. They cover "synthetically generated information", including voice clones. [legal500](https://www.legal500.com/intelligence/india/media-telecoms-it-entertainment/2026-it-rules-amendments-ai-content-labelling-and-intermediary-obligations) [roedl](https://www.roedl.it/en-gb/it/insights/pages/tech-data-bites/2-26/beyond-draft-indias-amended-it-rules-synthetically-generated-information.aspx) Large platforms must ask uploaders to declare AI content and then label it. [ipleaders](https://blog.ipleaders.in/it-rules-2026/) **You need to declare it honestly at upload.**
4. **YouTube:** Tick "altered or synthetic content" when a realistic AI voice could be taken for a real person. For cartoon characters voiced by clones of friends, **tick it anyway to be safe.** For monetization, YouTube's "inauthentic content" rule (renamed from "repetitious content" on 15 Jul 2025) targets mass-produced, templated videos, not AI itself. [lenspov](https://lenspov.com/articles/youtube-ai-content-demonetization-2026) [ytzolo](https://ytzolo.com/blog/youtube-repetitive-content-policy-ai-slop-2026/) Make every episode an original story.
5. **Instagram and Facebook:** Use Meta's "AI info" label when posting realistic AI audio.
6. **Watermark and attribution:** Keep Chatterbox's PerTh watermark on. No credit line is legally required, but "Voices: AI (with consent)" in the description is good practice.

### Simple consent form template

> **Voice Recording & AI Voice Consent: "Muskaanpur ki Kahaniyan"**
> I, ________ (name), age ___, give [Channel owner name] permission to:
> 1. Record my voice and use it to create an AI voice model for the character "________".
> 2. Use AI-generated speech in this voice in videos on YouTube, Instagram and Facebook, including **monetized** videos.
>
> **Limits:** My AI voice will only be used for this channel's stories. It will not be used to impersonate me, for ads endorsing products in my name, or for political, adult, hateful or misleading content. It will not be shared or sold to others.
> **Payment:** ☐ Unpaid / ☐ ₹____ per ____
> **Withdrawal:** I can withdraw consent at any time by written message. After that, no **new** content will be made with my voice, and my sample and voice files will be deleted within 30 days. Videos already published may stay online ☐ Yes ☐ No.
> **Data:** My recording is stored privately in the owner's Google Drive.
> Signature: ________ Date: ________ Phone/Email: ________
> (For a minor: parent/guardian signature ________)

---

## 5. Hosting options (no NVIDIA GPU)

| Option | Cost/month | Setup effort | Speed per line | Limits | Voice storage |
|---|---|---|---|---|---|
| **Google Colab free (recommended)** | ₹0 | Low: open notebook, Run All | Fast on a T4 GPU (a few seconds per short line) | Sessions disconnect and GPU time is not guaranteed | Google Drive (survives restarts) |
| Colab paid tier | Colab Pro is about US$9.99/month for 100 compute units, roughly ₹950/month in India once forex markup is added (secondary sources; confirm on Google's pricing page). A T4 uses about 1.19 units/hour. | Same | Faster and more reliable | Compute units | Google Drive |
| Kaggle notebooks | ₹0 | Medium (no Drive, uses Kaggle Datasets) | Similar | Weekly GPU quota | Kaggle Dataset |
| Hugging Face Spaces (ZeroGPU) | Free or Pro | Medium to high | Fast, but a queue | Daily GPU quota; storage resets unless you pay for persistent storage | HF repo |
| CPU-only on your PC | ₹0 | High (Python setup on Windows) | **Slow** (Chatterbox "can definitely run on CPU" but slowly) [ycombinator](https://news.ycombinator.com/item?id=44251411) | None | Local folder |
| GPU rental (RunPod and similar) | Pay per hour | Medium | Fastest | Your money | Network volume |

**Decision:** Use Colab free plus Google Drive. Your tool generates short lines for Shorts, so free GPU sessions are enough.

---

## 6. Development plan for Claude Code

### 6.1 Architecture and tech stack
- **Python 3.11 + Gradio** in **one Colab notebook**. It mounts Google Drive and launches the Gradio app with `share=True`, so you open it in your browser like a normal website.
- **TTS engine layer:** a small "engine" interface so new models or languages can be added later without touching the UI. v1 ships one engine, `chatterbox_mtl` (Chatterbox Multilingual v3, package `chatterbox-tts`, class `ChatterboxMultilingualTTS`).
- **Audio tools:** `soundfile`/`torchaudio` for WAV, `pydub` + `ffmpeg` for MP3, and `librosa` for trimming and loudness.
- **Consistency trick:** When a voice is added, compute its voice "conditionals" once and save them as `conds.pt`. Chatterbox supports `Conditionals.load(...)`. [huggingface](https://huggingface.co/reenigne314/chatterbox-indic-lora) Every later generation reuses the same file and a fixed seed, so the voice sounds the same every time.

### 6.2 Folder structure (in Google Drive)
```
MyDrive/MuskaanpurVoiceStudio/
├── app/                      # code (git repo)
│   ├── notebook.ipynb        # Colab launcher: install → mount Drive → run app
│   ├── app.py                # Gradio UI (2 tabs)
│   ├── config.py             # paths, defaults
│   ├── languages.json        # language → engine + language_id
│   ├── engines/
│   │   ├── base.py           # Engine interface
│   │   └── chatterbox_mtl.py # Chatterbox Multilingual engine
│   ├── core/
│   │   ├── voices.py         # add/list/load/delete voices (voices.json)
│   │   ├── audio_utils.py    # clean sample, trim, normalize, WAV→MP3
│   │   ├── text_utils.py     # split long text into sentences (।, ., ?, !)
│   │   └── generate.py       # generate(voice_id, text) → wav, mp3
│   └── tests/test_sentences.json
├── voices/
│   ├── voices.json
│   └── bhola_kaka/
│       ├── sample_original.wav
│       ├── sample_clean.wav
│       ├── conds.pt          # cached voice fingerprint
│       └── consent.pdf       # signed consent form
└── outputs/2026-10-25/bhola_kaka_0001.wav / .mp3
```

### 6.3 Voice data format (`voices.json`)
```json
{
  "version": 1,
  "voices": [
    {
      "id": "bhola_kaka",
      "name": "Bhola Kaka",
      "language": "hi",
      "engine": "chatterbox_mtl",
      "sample_file": "voices/bhola_kaka/sample_clean.wav",
      "sample_seconds": 14.2,
      "transcript": "",
      "conds_file": "voices/bhola_kaka/conds.pt",
      "consent_file": "voices/bhola_kaka/consent.pdf",
      "settings": { "exaggeration": 0.5, "cfg_weight": 0.5, "temperature": 0.8, "seed": 1234 },
      "created_at": "2026-10-25T10:00:00+05:30"
    }
  ]
}
```
`languages.json` example: `{"hi": {"label": "Hindi", "engine": "chatterbox_mtl", "language_id": "hi", "enabled": true}, "en": {...}, "gu": {"label": "Gujarati", "engine": null, "enabled": false, "note": "Blocked: licence"}}`. To add a language later, you add one line here and, if needed, one engine file.

### 6.4 UI spec (2 screens, no extra menus)
**Tab 1, "Add Voice":**
- Name (text box), Language (dropdown showing only enabled languages), and voice sample (upload **or** record with the mic, 10–30 s).
- Transcript box, shown only if the chosen engine needs it (Chatterbox does not).
- Checkbox: "I have signed consent from this person" (required) plus an optional consent file upload.
- **Save Voice** button, then a status message ("Saved ✅ 14.2 s sample"). Show errors in plain words, e.g. "Sample too short (6 s). Need at least 10 s."

**Tab 2, "Generate":**
- Voice dropdown, a text area with a character count, and a **Generate** button.
- An audio player, plus **Download WAV** and **Download MP3** buttons.
- One small "Advanced" fold with expression (exaggeration) and seed. It stays closed by default.

### 6.5 Functions and modules
- `voices.add_voice(name, language, audio_path, transcript, consent)` → validates, cleans, saves the sample, builds `conds.pt`, writes the JSON.
- `voices.list_voices()`, `voices.get_voice(id)`, `voices.delete_voice(id)`.
- `audio_utils.clean_sample(path)` → mono, trim silence, normalize loudness, check length (10–30 s).
- `audio_utils.wav_to_mp3(wav_path)` → MP3 at 192 kbps.
- `text_utils.split_text(text, lang)` → chunks of about 250 characters or less, split at sentence ends.
- `engines.base.Engine` with `load()`, `prepare_voice(sample)`, `synthesize(text, voice, settings)`.
- `engines.chatterbox_mtl.ChatterboxEngine`: loads the model once and caches it.
- `generate.generate(voice_id, text)` → sets the seed, synthesizes the chunks, joins them with 150 ms gaps, saves WAV and MP3, and returns the paths.
- (Later) `script.parse_script(text)` → list of `(speaker, line)` from `[Bhola Kaka] ...`, then one file per line.

### 6.6 Milestones and acceptance criteria
1. **M1: Colab skeleton.** The notebook installs packages, mounts Drive, creates the folders, and launches an empty 2-tab Gradio app with a public link. *Done when:* the link opens in Chrome and both tabs show.
2. **M2: Engine works.** Chatterbox loads on the T4 and speaks one hard-coded Hindi and one English line using a demo sample. *Done when:* both WAVs play and the first load takes under 5 minutes.
3. **M3: Add Voice.** Upload or record, clean, save, cache `conds.pt`, and update `voices.json`. *Done when:* after a full Colab restart, the voice still appears in the dropdown.
4. **M4: Generate + download.** Choose a voice, type text, generate, play, and download WAV and MP3. Long text gets split. *Done when:* a 600-character Hindi paragraph comes out as one clean file and the MP3 opens in CapCut.
5. **M5: Consistency.** Fixed seed plus cached conds. *Done when:* generating the same line twice gives the same-sounding audio, and five different lines sound like the same character.
6. **M6: Polish and guard rails.** Friendly errors, the consent checkbox is enforced, and Gujarati shows as "coming soon". *Done when:* the full test plan passes.
7. **M7 (later): Script mode.** Paste a script with `[Speaker]` tags and get numbered files per line plus a ZIP.

### 6.7 Test plan
**Hindi**
1. भोला काका ने खेत से लौटकर कहा, "आज बारिश ज़रूर होगी।"
2. कमला काकी, ज़रा चाय बना दो, मेहमान आने वाले हैं!
3. मुस्कानपुर गाँव में एक बहुत पुराना बरगद का पेड़ था, जिसके नीचे सब बच्चे कहानियाँ सुनते थे।

**Gujarati** (for when Gujarati is unlocked)
1. ભોલા કાકા ખેતરમાંથી પાછા આવ્યા અને બોલ્યા, "આજે વરસાદ પડશે."
2. કમળા કાકી, જરા ચા બનાવો ને, મહેમાન આવવાના છે!
3. મુસ્કાનપુર ગામમાં એક જૂનું વડનું ઝાડ હતું, જેની નીચે બાળકો વાર્તાઓ સાંભળતા.

**English**
1. Bhola Kaka smiled and said, "The rain will come today, mark my words."
2. Kamla Kaki, please make some tea, the guests are almost here!
3. Once upon a time, in the little village of Muskaanpur, there lived a very clever goat.

**How to judge (score each item 1–5; pass means an average of 4 or more):**
- **Correct words:** no missing, added or repeated words. You can also run Whisper on the output and compare the text.
- **Pronunciation:** natural Hindi, not English-accented (watch ज़, ड़, and nasal sounds).
- **Voice match:** a family member can tell which character it is without being told.
- **Consistency:** play all 3 lines in a row and check they sound like one person.
- **Clean audio:** no clicks, robotic buzz or long silences.

### 6.8 Risks and fallbacks
- **Gujarati licence (main risk).** Fallback A: email IIT Madras (the Indic TTS team) and ask in writing whether models trained on the IndicTTS database can be used commercially. If they say yes, enable the **Chatterbox Indic LoRA** as a `chatterbox_indic` engine (same code family). Fallback B: train your own Gujarati LoRA using the public `chatterbox-indic-train` scripts on **Rasa only** (CC-BY-4.0), with a few hours on a rented GPU. [github](https://github.com/rkumar1310/indic-chatter-train) [huggingface](https://huggingface.co/sulabhkatiyar/indic-tts-mini-train) Fallback C: write Gujarati episodes' dialogue in Hindi for now.
- **Hindi quality not good enough.** First try a cleaner, longer (15–20 s) sample in the same language and lower the expression setting. Then try VoxCPM2 (Apache-2.0) as a second engine. Use the Chatterbox Hindi pack only after you confirm its licence line says MIT.
- **Colab disconnects or no GPU.** Retry later, or use Kaggle. Voices are safe in Drive.
- **Voice drift between lines.** Always use cached `conds.pt` and a fixed seed, and never re-record a voice mid-series.
- **Policy changes.** Re-check model licences and platform rules every 3 months.

---

## 7. Claude Code kickoff prompt (copy and paste)

```
You are building "Muskaanpur Voice Studio", a minimal voice-cloning TTS web app.
I am a web developer (HTML/CSS/JS), NOT a Python expert: keep code simple, commented, and explain steps in short, easy English.

GOAL OF THIS SESSION: Milestone 1 + 2 only.

Tech stack (do not change):
- Python 3.11, Gradio UI, runs in a Google Colab notebook (free T4 GPU).
- Google Drive for storage: root = /content/drive/MyDrive/MuskaanpurVoiceStudio/
- TTS engine: Resemble AI Chatterbox Multilingual (MIT licence), pip package "chatterbox-tts",
  class ChatterboxMultilingualTTS from chatterbox.mtl_tts, generate(text, language_id=..., audio_prompt_path=...).
  Keep the built-in PerTh watermark ON. Do not remove it.
- Languages v1: "hi" (Hindi) and "en" (English). Gujarati "gu" must exist in languages.json but enabled=false.

Create this structure:
app/notebook.ipynb, app/app.py, app/config.py, app/languages.json,
app/engines/base.py, app/engines/chatterbox_mtl.py,
app/core/voices.py, app/core/audio_utils.py, app/core/text_utils.py, app/core/generate.py,
voices/voices.json (start as {"version":1,"voices":[]}), outputs/

Milestone 1 (acceptance: public Gradio link opens with 2 tabs "Add Voice" and "Generate"):
- notebook cells: (1) install deps incl. ffmpeg/pydub, (2) mount Drive, (3) create folders, (4) launch app.py with share=True.
- Tabs are placeholders for now.

Milestone 2 (acceptance: one Hindi and one English WAV generated and playable):
- Implement Engine interface: load(), prepare_voice(sample_path) -> saves conds.pt, synthesize(text, voice, settings) -> numpy audio + sample rate.
- ChatterboxEngine loads the model ONCE (cache it), uses cuda if available else cpu.
- Fixed seed per voice for consistency. Settings defaults: exaggeration 0.5, cfg_weight 0.5, temperature 0.8, seed 1234.
- Add a test cell that generates:
  hi: "भोला काका ने खेत से लौटकर कहा, आज बारिश ज़रूर होगी।"
  en: "Bhola Kaka smiled and said, the rain will come today, mark my words."
  and saves them to outputs/test/.

Rules:
- Engines must be pluggable via languages.json (language -> engine + language_id) so I can add languages later.
- Plain-English error messages. No extra menus or features.
- After finishing, give me: what you built, how to run it in Colab step by step, and how to verify the acceptance criteria.
```