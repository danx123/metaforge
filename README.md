# MetaForge

**Professional Image Metadata Injector & AI Fingerprint Detector**

MetaForge is a desktop application for injecting accurate, camera-authentic EXIF metadata into JPEG and PNG images & AI Fingerprint Detector. Built with PySide6, it features a curated database of 33 real-world camera presets spanning Sony, Canon, Nikon, Fujifilm, Leica, Hasselblad, Phase One, DJI, and more — covering everything from smartphone sensors to 150MP medium format systems.

> **Note on this repository:**
> The source code published here is the **base reference implementation** — it reflects the architecture, core logic, and engineering decisions behind MetaForge, but may not match the feature set or UI of the current released version.
> **For the latest version, download the pre-built binary from the releases page.** No Python installation required.

---

## Screenshots

<img width="1365" height="767" alt="Screenshot 2026-04-29 184905" src="https://github.com/user-attachments/assets/52d1296c-ca35-46cc-8636-66a02ed1b247" />

<img width="1365" height="767" alt="Screenshot 2026-04-29 185047" src="https://github.com/user-attachments/assets/470ffaa5-b721-4776-80eb-1bf6cd153385" />






---

## Features

### Camera Preset Engine
- **33 built-in presets** across 14 brands and categories — Sony, Canon, Nikon, Fujifilm, Panasonic, OM System, Leica, Hasselblad, Phase One, Pentax, Sigma, DJI, smartphone, and action camera
- Each preset contains model-accurate data: sensor size, focal plane dimensions, ISO range, aperture range, shutter range, lens model, software version string, and color space
- Category filter and full-text search across model name, brand, and lens

### EXIF Injection
- Injects a complete EXIF payload: make, model, lens info, exposure triangle (focal length, aperture, shutter speed, ISO, exposure bias), date/time, color space, metering mode, and orientation
- **JPEG output at 95% quality** — lossless-friendly recompression
- **Optional PNG preservation** — PNG inputs can be saved as PNG (lossless) with EXIF embedded via `piexif.insert()`, without forced JPEG conversion
- Outputs written to a configurable destination folder; source files are never modified

### Auto-Detect Engine
- Analyzes the selected image (brightness, contrast, sharpness, dynamic range, color temperature, megapixels, aspect ratio) and scores all 33 presets against the result
- Downsamples images to ≤2MP before statistical analysis — **~30× faster** on high-resolution files while reporting original resolution accurately
- Returns ranked top-5 matches with confidence scores displayed as visual score bars
- One-click apply best match
- AI Fingerprint Detection

### Batch Processing
- Queue multiple inject jobs, each with independent preset selection and parameter overrides
- **Per-job auto-detect** option — analyzes each file individually and selects the best-matching preset automatically, with the manual preset as fallback
- `force_jpeg` flag propagated per job — batch mode fully respects the PNG preservation setting
- Separate thread pools for I/O-bound (inject) and CPU-bound (analyze) tasks prevent resource contention
- Real-time progress bar and per-file status in the activity log

### UI
- Dark theme (GitHub-inspired `#0d1117` surface palette)
- Three-panel layout: file list + preview / preset & parameter tabs / output controls
- Stat counters in the top bar (files loaded, presets available, files processed)
- Resizable splitter panels

---

## Download

Pre-built binaries for Windows are available on the **[Releases](../../releases)** page.

| Platform | Format | Notes |
|----------|--------|-------|
| Windows 10 / 11 | `.exe` (standalone) | No Python required |

> macOS and Linux builds are not officially distributed at this time. Users on those platforms can run from source — see [Running from Source](#running-from-source) below.

---

## Running from Source

### Requirements

- Python 3.10 or later
- pip

### Install dependencies

```bash
pip install PySide6 Pillow piexif
```

### Run

```bash
python metaforge.py
```

### Run unit tests

```bash
python metaforge.py --test
```

The test suite covers `ImageAnalyzer.score_preset()`, `MetadataInjector.build_exif()`, downsample accuracy, `BatchJob` flag propagation, and the presence of explicit `megapixels` fields across all presets — no Qt runtime required.

---

## Architecture

```
metaforge.py
│
├── CAMERA_PRESETS          dict[str, dict]  — 33 preset definitions
│
├── ImageAnalyzer
│   ├── analyze()           Downsample → stat → return analysis dict
│   └── score_preset()      Score one preset against analysis result
│
├── MetadataInjector
│   ├── build_exif()        Assemble piexif-compatible IFD dicts
│   └── inject()            Open image → embed EXIF → write output
│
├── BatchJob                Data model for one queued inject job
│
├── Workers (QRunnable)
│   ├── InjectWorker        Single-job inject — uses io_pool
│   ├── BatchWorker         Multi-job queue  — uses io_pool
│   └── AnalyzeWorker       Image analysis   — uses cpu_pool
│
└── MetaForgeWindow (QMainWindow)
    ├── _build_topbar()
    ├── _build_left_panel()
    ├── _build_center_panel()
    │   ├── _build_preset_tab()
    │   ├── _build_params_tab()
    │   ├── _build_auto_detect_tab()
    │   └── _build_batch_tab()
    └── _build_right_panel()
```

Thread pools are separated by workload type:

| Pool | Max threads | Used for |
|------|-------------|----------|
| `io_pool` | 4 | Inject (I/O-bound) |
| `cpu_pool` | 2 | Analysis (CPU-bound) |

---

## Supported Camera Presets

| Brand | Models |
|-------|--------|
| **Sony** | A7R V, A7 IV, ZV-E1, RX100 VII, A6700 |
| **Canon** | EOS R5, EOS R6 Mark II, EOS 5D Mark IV, EOS 90D, PowerShot G7X Mark III |
| **Nikon** | Z9, Z8, Z6 III, D850, D7500 |
| **Fujifilm** | X-T5, X100VI, GFX 100S II |
| **Panasonic** | Lumix S5 II, Lumix G9 II |
| **OM System** | OM-1 Mark II |
| **Leica** | Q3, M11 |
| **Hasselblad** | X2D 100C |
| **Phase One** | IQ4 150MP |
| **Pentax** | K-3 Mark III |
| **Sigma** | fp L |
| **DJI** | Mavic 3 Pro, Mini 4 Pro |
| **Smartphone** | Apple iPhone 15 Pro Max, Samsung Galaxy S24 Ultra, Google Pixel 9 Pro |
| **Action Camera** | GoPro HERO13 Black |

---

## Notes on the Source Code

This repository contains the **base reference source** — the version that established MetaForge's core architecture and was used as the foundation for continued development. It is published for transparency and as a reference for anyone interested in how the metadata engine, auto-detect scoring, and batch pipeline work under the hood.

The binary releases may include UI refinements, additional presets, and features not reflected here. If you find a bug or have a feature request, please open an [Issue](../../issues).

---

## License

This project is source-available for reference purposes. Please do not redistribute modified versions or repackage the binaries without permission.

---

## Acknowledgements

- [piexif](https://github.com/hMatoba/Piexif) — EXIF read/write library
- [Pillow](https://python-pillow.org/) — Image processing
- [PySide6](https://doc.qt.io/qtforpython/) — Qt bindings for Python

---

## Disclaimer

MetaForge Disclaimer

MetaForge is a software tool designed for educational, research, and workflow simulation purposes. It provides functionality for metadata editing, EXIF simulation, and image processing to support developers, researchers, and content creators in testing and enhancing their workflows.

The use of MetaForge for deceptive, fraudulent, or misleading activities—such as falsifying the origin or authenticity of images—is strictly discouraged and may violate applicable laws and regulations.

By using this software, you agree to take full responsibility for how it is utilized. The developer shall not be held liable for any misuse, damages, legal consequences, or claims arising from the improper or unlawful use of this application.

MetaForge is provided “as is”, without warranty of any kind, express or implied, including but not limited to fitness for a particular purpose or non-infringement.

Use responsibly.
