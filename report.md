
# Project Report — YOLO + CLIP + VLM Captioned Dashcam Demo

> **Final deliverable:** PDF presentation (slides exported from this report + figures + demo video stills/clips). Code/notebooks are operational; DevOps (env pinning, repro scripts, dataset hygiene) is still ongoing.

## 1. Project Summary
This project combines a fine-tuned **YOLO26s** detector, an **OpenCLIP ViT-B-32** backbone with a 20-class linear probe for car-brand recognition, and a local **Qwen3-VL** vision-language model to produce a captioned dashcam demo. The pipeline generates an annotated Stage 2 video and a captioned Stage 3 video. Stage 1 also has an optional `ffmpeg` compression cell for the YOLO-only output.

## 2. Objectives
- Detect driving-scene objects with YOLO (11 self-driving classes).
- Add per-vehicle car-brand recognition via CLIP image embeddings + a trained linear probe.
- Add VLM-based scene understanding and audience-friendly captions.
- Provide a simple Q&A interface for selected timestamps.
- Export compact outputs suitable for the final PDF presentation.

## 3. Data and Environment
- **YOLO dataset:** Self-Driving-Car-3 (Roboflow), 11 classes (`biker, car, pedestrian, trafficLight*, truck`); kept locally, not pushed to git.
- **CLIP probe dataset:** 20-class car-brand image set (European-biased: Audi, BMW, Chevrolet, Citroen, Dacia, Fiat, Ford, Honda, Hyundai, Kia, Mercedes, Nissan, Opel, Peugeot, Renault, Seat, Skoda, Tofaş, Toyota, Volkswagen). Probe trained on Kaggle.
- **Artifacts:** `weights/yolo/best.pt`, `weights/clip/linear_probe/{linear_probe_weights.pt, class_names.json, config.json}`.
- **Inference outputs:** `runs_output/detect/clip_predict/` (Stage 2 video) and `runs_output/detect/.../vlm_overlay/` (Stage 3 video + log).
- **VLM runtime:** Ollama + `qwen3-vl:4b` (local).

## 4. Implemented Pipeline

### 4.0 Stage Map
- **Stage 1 — YOLO fine-tune** (`01_yolo_finetune.ipynb`): `yolo26s.pt` → fine-tune (`imgsz=512`, `batch=16`, `epochs=30`, `patience=10`) → eval (`model.val()` for P/R/mAP@0.5/mAP@0.5:0.95) → export `weights/yolo/best.pt`.
- **Stage 2a — CLIP linear probe** (`02a_clip_probe_train.ipynb`): freeze OpenCLIP `ViT-B-32`/`laion2b_s34b_b79k`, cache image embeddings once, train `nn.Linear(512, 20)` (Adam `lr=1e-3`, `wd=1e-4`, early stop `patience=7`, 70/15/15 stratified split) → export to `weights/clip/linear_probe/`.
- **Stage 2b — YOLO+CLIP video** (`02b_yolo_clip_video.ipynb`): per frame YOLO `conf=0.2`; for each detection where `class == "car"` and crop ≥ 80×80, crop → CLIP → L2-normalize → linear probe → top-1 brand + softmax confidence → label `"<brand> (<conf>)"`. Output: `runs_output/detect/clip_predict/annotated_video.mp4`.
  - *Confidence threshold:* YOLO outputs a raw score (objectness × class probability) per box. `conf=0.2` is a post-processing filter — boxes below 20 % are discarded before reaching CLIP. Lowered from 0.4 to catch more distant/occluded cars without excessive false positives.
- **Stage 3 — VLM caption + Q&A** (`03_vlm_caption.ipynb`): local `qwen3-vl:4b` via Ollama; adaptive captioning (gray-frame `absdiff().mean() ≥ 12.0` AND ≥ `5.0 s` since last caption); banner overlay; Q&A widget seeks by frame index, single-frame reasoning, fallback retry on empty response.
- **Stage 4 — Semantic Segmentation** (`04_semantic_segmentation.ipynb`): pretrained `nvidia/segformer-b5-finetuned-cityscapes-1024-1024` via Hugging Face Transformers. Per-frame inference → nearest-neighbor upsampling → Cityscapes 19-class palette → alpha-blended overlay on original video. Output: `runs_output/segmentation/cityscapes_segmented.mp4`. Independent of Stages 1–3; reads `original_videos/dashcam.mp4` directly.

### 4.1 Detection and Input Resolution
- YOLO outputs are read from `runs_output/detect`.
- Discovery order in Step 3 (`candidate_output_dirs`): `clip_predict` → highest numbered `predict*` (Ultralytics writes `predict`, `predict2`, `predict3`, …) → bare `predict` → any other sibling dir that contains a video.
- The numbered-folder regex accepts both Ultralytics-default (`predict2`) and dashed/underscored variants:

```python
match = re.fullmatch(r"predict[-_]?(\d+)", name)
if match:
		numbered.append((int(match.group(1)), path))
```

### 4.2 VLM Caption Overlay
- Captions are generated per selected frame policy.
- Adaptive mode updates captions only when scene change exceeds threshold and minimum time gap is met.
- Captions are rendered on a high-contrast top banner for readability.

### 4.3 Q&A Mode
- User selects a timestamp.
- One frame is sampled and sent to VLM.
- Output prioritizes direct answer + evidence-oriented explanation.

```python
target_idx = int(round(max(0.0, float(sec)) * fps))
cap.set(cv2.CAP_PROP_POS_FRAMES, target_idx)
ret, frame = cap.read()
```

### 4.4 Robustness Improvements
- Deterministic video selection priority:
	`output_video` -> `input_video` -> resolved predict video.
- Empty-response fallback retry for Q&A prompt.
- Widget/session guards to reduce duplicated callback behavior during reruns.

## 5. Outputs
- Stage 2 video: `runs_output/detect/clip_predict/annotated_video.mp4`
- Stage 3 captioned video: `runs_output/detect/<selected_output_dir>/vlm_overlay/*_vlm.mp4`
  (`<selected_output_dir>` = `clip_predict` if it exists, else the highest-numbered `predict*`, else `predict`)
- Stage 4 segmentation video: `runs_output/segmentation/cityscapes_segmented.mp4` (pretrained SegFormer-B5 on Cityscapes, independent of Stages 1–3).
- Stage 1 (optional) compressed YOLO video: `runs_output/detect/predict*/converted_mp4/*_compressed.mp4` (produced by the Stage 1 `ffmpeg` cell, not by Stage 3).

## 6. Current Results
- End-to-end demo is operational.
- Prompting behavior improved from rigid template to smarter, question-first style.
- Response speed and stability improved with bounded generation and fallback handling.

### 6.1 YOLOv10n Baseline (before upgrade)

These numbers were copied directly from the `model.val()` cell output in `01_yolo_finetune.ipynb`.

- **Model**: `yolov10n.pt` (COCO-pretrained, fine-tuned on Self-Driving-Car-3)
- **Training**: `epochs=30`, `imgsz=512`, `batch=16`, `patience=10`

| Metric | Value |
|---|---|
| Precision | 0.801 |
| Recall | 0.598 |
| mAP@0.5 | 0.675 |
| mAP@0.5:0.95 | 0.388 |

Per-class validation metrics (from cell output):

| Class | Images | Instances | Precision | Recall | mAP@0.5 | mAP@0.5:0.95 |
|---|---|---|---|---|---|---|
| all | 2980 | 19514 | 0.801 | 0.598 | 0.675 | 0.388 |
| biker | 257 | 405 | 0.697 | 0.608 | 0.676 | 0.373 |
| car | 2579 | 12667 | 0.826 | 0.799 | 0.856 | 0.579 |

*(Remaining per-class rows omitted for brevity — full table is in the notebook output.)*

### 6.2 YOLO26 Comparison (after retraining — to be filled)

| Metric | YOLOv10n (baseline) | YOLO26 (new) | Δ |
|---|---|---|---|
| Precision | 0.801 | — | — |
| Recall | 0.598 | — | — |
| mAP@0.5 | 0.675 | — | — |
| mAP@0.5:0.95 | 0.388 | — | — |

## 7. Known Limits
- **Stage 2b labeling**: brand confidence is not thresholded — even a ~5 % top-1 brand is drawn on the box.
- **Stage 2b coverage**: only `class == "car"` triggers CLIP brand classification. Trucks are intentionally excluded because the linear probe was trained on car-only images; truck crops are out-of-distribution and would yield miscalibrated brand confidence.
- **No tracking**: no per-vehicle ID across frames → brand labels flicker even when YOLO is stable.
- **Domain mismatch**: linear probe was trained on well-framed brand photos and is applied to small / oblique / motion-blurred dashcam crops → noisy outputs.
- **CLIP not batched**: one crop at a time per frame.
- **Stage 3 banner**: hardcoded font/thickness sized for very large frames; oversized on 720p/1080p.
- **Brand list**: 20 European-leaning brands only (no Tesla, Subaru, Mazda, Lexus, …).
- **Single-frame Q&A**: misses temporal context (motion, intent, signal transitions).
- **Exact model identification** from dashcam distance/resolution is often not visually verifiable.

## 8. DevOps Backlog (in progress)
- Add a pinned `requirements.txt` (Ultralytics, open_clip_torch, ollama, scikit-learn, opencv-python, ipywidgets, Pillow, tqdm).
- Confirm `.gitignore` excludes `Self-Driving-Car-3/`, `runs_output/`, `original_videos/`, `.venv/` and large weights as appropriate.
- Add a thin `make demo` / shell script wrapping Stage 2b → Stage 3 for one-command reruns.
- Optional: package the Q&A widget as a small Gradio app for the live demo.

## 9. Next Sections (planned)
- Add tracking (`model.track(..., tracker="bytetrack.yaml")`) and per-track brand smoothing (majority vote / EMA on logits).
- Apply a brand-confidence threshold (e.g., ≥ 0.5) before drawing the brand label; fall back to `"car"`.
- Extend CLIP-trigger to `truck` and other vehicle classes; consider a "vehicle vs not" gate.
- Auto-scale banner font from `frame.shape` so the overlay looks consistent across resolutions.
- Add a YOLO-vs-VLM object-consistency check (do detected classes appear in the VLM caption?) as a sanity metric.
- Final evaluation tables + figures for the PDF presentation: training curves, confusion matrix, per-class F1, qualitative frames.
- Side-by-side YOLO boxes vs. segmentation mask figure for the final PDF presentation.

