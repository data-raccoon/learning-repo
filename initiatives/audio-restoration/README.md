# Audio Restoration

## Purpose

This initiative provides a reproducible, offline workflow for restoring damaged
speech recordings. It currently includes two cleanup profiles for a clipped,
noisy English voice sample while preserving the speaker's accent and prosody.

Private source recordings and generated audio are intentionally excluded from
Git. The processing code, documentation, and required neural model remain
versioned.

## Layout

- `inputs/` — private source recordings; ignored by Git.
- `outputs/` — generated WAV files and measurements; ignored by Git.
- `models/sh.rnnn` — RNNoise model used by the aggressive profile.
- `clean_audio.py` — complete generation and validation pipeline.

The expected local input is:

`inputs/latin-american-sample_uncleaned.ogg`

## Processing profiles

### Version 1: balanced

Version 1 applies declipping, impulse repair, a 100 Hz–8.5 kHz speech band,
18 dB FFT noise reduction, non-local-means broadband denoising, light de-essing,
and -18 LUFS/-3 dBTP normalization. Silences of at least 600 ms are shortened
while retaining 250 ms.

Output: `outputs/latin-american-sample_cleaned_v1.wav`

### Version 2: aggressive neural

Version 2 uses lower-threshold, longer-burst impulse repair and the Somnolent
Hogwash RNNoise model through FFmpeg's `arnndn` filter. A lighter 10 dB FFT pass
removes residual stationary noise, the useful voice band is limited to
100 Hz–9 kHz, and pauses over 450 ms are shortened while retaining 180 ms.

Output: `outputs/latin-american-sample_cleaned_v2_aggressive.wav`

Both outputs are 48 kHz mono, 24-bit PCM WAV files.

## Run

From the repository root:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" initiatives\audio-restoration\clean_audio.py
```

The script requires `imageio-ffmpeg` in the workspace Python environment. It
creates `outputs/analysis.json` containing the exact ordered filter chains,
input/output hashes, model provenance, audio measurements, and automated
validation results.

## Validation

Each run checks that:

- the copied input remains unchanged during processing;
- both WAV files decode successfully;
- both outputs have peak headroom and no samples at 0 dB;
- long-pause processing reduces the duration;
- repeated runs produce deterministic WAV files.

The checks cannot replace listening. Compare both versions for speech
naturalness, consonant preservation, residual noise, and pause rhythm.

## Adding another recording

Copy the private recording into `inputs/`, update `SOURCE` and output names in
`clean_audio.py`, then run the script. Do not commit recordings or generated
outputs.

## Model provenance

`models/sh.rnnn` is the Somnolent Hogwash model from the archived
`richardpl/arnndn-models` repository:

<https://github.com/richardpl/arnndn-models/blob/master/sh.rnnn>

Its SHA-256 hash is recorded in each generated `outputs/analysis.json`.
