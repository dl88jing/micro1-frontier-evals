#!/usr/bin/env python3
"""Generate Kokoro VO wavs for PyScope video."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import soundfile as sf
from kokoro_onnx import Kokoro

HERE = Path(__file__).resolve().parent
MODEL = Path("/workspace/ctrl-space/kokoro-v1.0.onnx")
VOICES = Path("/workspace/ctrl-space/voices-v1.0.bin")
OUT = HERE / "assets" / "audio"
OUT.mkdir(parents=True, exist_ok=True)

k = Kokoro(str(MODEL), str(VOICES))
durations = {}
for sid, text in json.loads((HERE / "narration.json").read_text()):
    samples, sr = k.create(text, voice="af_heart", speed=1.05, lang="en-us")
    path = OUT / f"{sid}.wav"
    sf.write(path, samples, sr)
    durations[sid] = len(samples) / sr
    print(sid, round(durations[sid], 2), flush=True)

# Concatenate narration
import numpy as np
parts = []
gap = int(0.25 * 24000)  # assume 24k; adjust after first write
# re-read first to get sr
import soundfile as sf2
first, sr = sf2.read(OUT / "vo1.wav")
gap = int(0.22 * sr)
for sid, _ in json.loads((HERE / "narration.json").read_text()):
    audio, _ = sf2.read(OUT / f"{sid}.wav")
    parts.append(audio)
    parts.append(np.zeros(gap))
full = np.concatenate(parts)
sf2.write(OUT / "narration.wav", full, sr)
durations["narration"] = len(full) / sr
(OUT / "durations.json").write_text(json.dumps(durations, indent=2) + "\n")
print("total", round(durations["narration"], 2))
