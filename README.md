# Computer Vision HSLU 2026

Local dashcam pipeline that combines YOLO detection with CLIP brand recognition and VLM scene understanding.

> **Project status:** code/notebooks operational, DevOps (env pinning, repro scripts, dataset hygiene) still ongoing. Final deliverable is a **PDF presentation** built from `report.md` plus exported videos and metric figures.

## What This Project Does
- Runs YOLO on driving video and saves outputs under `runs_output/detect/predict*`.
- Stores canonical model artifacts under `weights/yolo/` and `weights/clip/linear_probe/`.
- Adds VLM captions using local Ollama (`qwen3-vl:4b`).
- Supports quick frame-based Q&A for audience/demo usage.
- Exports the captioned video for reporting. (Stage 1 also has an optional `ffmpeg` compression cell that targets ~100 MB under `runs_output/detect/predict*/converted_mp4/`; Stage 3 currently does not compress its own output.)

## Pipeline Architecture (verified)

**Stage 1 — YOLO fine-tuning** (`my_yolo_selfdriving_local.ipynb`)
- Backbone `yolo26s.pt` (COCO-pretrained), fine-tuned on `Self-Driving-Car-3` (11 classes: `biker, car, pedestrian, trafficLight, trafficLight-Green/-GreenLeft/-Red/-RedLeft/-Yellow/-YellowLeft, truck`).
- Training: `imgsz=512`, `batch=16`, `epochs=30`, `patience=10`, output to `runs_output/detect/selfdriving_v1/`.
- Eval cell runs `model.val()` for precision / recall / mAP@0.5 / mAP@0.5:0.95.
- Final cell copies `best.pt` and `results.png` into `weights/yolo/`.

**Stage 2a — CLIP linear probe training** (`clip-car-classification-with-linear-probe.ipynb`, originally trained on Kaggle)
- Backbone OpenCLIP `ViT-B-32` / `laion2b_s34b_b79k`, **frozen**; embeddings cached once.
- Probe = `nn.Linear(512, 20)`, Adam (`lr=1e-3`, `wd=1e-4`), cross-entropy, early stop `patience=7`, max `epochs=50`, 70/15/15 stratified split.
- 20 brands (European-biased): `Audi, BMW, Chevrolet, Citroen, Dacia, Fiat, Ford, Honda, Hyundai, Kia, Mercedes, Nissan, Opel, Peugeot, Renault, Seat, Skoda, Tofaş, Toyota, Volkswagen`.
- Exports `linear_probe_weights.pt`, `class_names.json`, `config.json` → `weights/clip/linear_probe/`.

**Stage 2b — YOLO + CLIP video pipeline** (`use_finetuned_yolo_and_clip_on_video.ipynb`)
- Per frame: YOLO `conf=0.4` → for every detection where `class_name.lower() == "car"` and crop ≥ 80×80 px, crop, run CLIP backbone, L2-normalize, push through linear probe → top-1 brand + softmax confidence → label `"<brand> (<conf>)"`. Truck detections are intentionally excluded from brand classification because the linear probe was trained on car-only images; truck crops are out-of-distribution.
- Output: `runs_output/detect/clip_predict/annotated_video.mp4`.

**Stage 3 — VLM caption + Q&A** (`my_yolo_vlm_step3.ipynb`)
- Local `qwen3-vl:4b` via the `ollama` Python client.
- Auto-discovery priority: `clip_predict` → highest `predictN` (Ultralytics default; `predict-N` / `predict_N` also accepted) → `predict` → other child dirs of `runs_output/detect/` containing a video. Overridable via `INPUT_VIDEO`, `PREDICT_DIR`, `INPUT_ROOT`.
- Adaptive captioning gate: gray-frame `absdiff().mean() ≥ CAPTION_DIFF_THRESHOLD (12.0)` **and** elapsed ≥ `CAPTION_MIN_SEC (5.0)`. Switch to fixed-interval mode with `CAPTION_MODE=fixed` and `CAPTION_EVERY_SEC`.
- Q&A widget seeks by frame index (`fps * sec`), sends one frame, falls back with a simpler prompt if the model returns empty, guards against duplicate clicks.

## Known Caveats / Things to Improve (DevOps + quality backlog)
- **Stage 2b** uses a hardcoded YOLO `conf=0.4`; brand confidence is **never thresholded**, so even a ~5 % top-1 brand is drawn on the box.
- **Stage 2b** runs CLIP only on `class_name == "car"`, so `truck` (and any other vehicle-like class) is excluded by design even though brand prediction would still be meaningful.
- **No tracking** in Stage 2b → labels flicker per frame for the same vehicle. ByteTrack + per-track majority/EMA on brand logits would stabilize labels significantly.
- **Domain mismatch** for the linear probe: trained on well-framed brand photos, applied to small/oblique/blurred dashcam crops — expect noisy brand outputs and use confidence thresholds + smoothing before trusting them.
- **CLIP not batched**: one crop at a time per frame; batching all car crops per frame would be a cheap speedup.
- **Stage 3 banner** renderer is hardcoded for very large frames (`font_scale=3.0`, `line_height=120`, `thickness=10`); on 720p/1080p the banner looks oversized — should scale with `frame.shape`.
- **Brand list is European-biased** (no Tesla/Subaru/Mazda/Lexus/etc.), and `Tofaş` reflects the source dataset's geography.
- **No `requirements.txt`** yet; environment is implied by per-notebook `!pip install` lines (`ultralytics`, `open_clip_torch`, `ollama`, `scikit-learn`, `tqdm`, `ipywidgets`, `Pillow`, `opencv-python`).
- **Dataset hygiene**: `Self-Driving-Car-3/` (~59k files) lives inside the repo — confirm `.gitignore` excludes it before any push.

## Notebook Roles
- `my_yolo_selfdriving_local.ipynb`: trains or re-runs the YOLO self-driving detector and exports canonical YOLO weights to `weights/yolo/`.
- `clip-car-classification-with-linear-probe.ipynb`: trains/evaluates the CLIP linear probe and exports probe artifacts (`linear_probe_weights.pt`, `class_names.json`, `config.json`). This is an asset-building notebook, not the normal runtime demo notebook.
- `use_finetuned_yolo_and_clip_on_video.ipynb`: final Step 2 runtime notebook. It loads the already-trained YOLO and CLIP assets, runs one input video, and writes a CLIP-enriched output video to `runs_output/detect/clip_predict/`.
- `my_yolo_vlm_step3.ipynb`: final Step 3 runtime notebook. It adds VLM captions and Q&A on top of the Step 2 or Step 1 output video.

## Final Demo Workflow
1. If YOLO weights already exist in `weights/yolo/`, skip `my_yolo_selfdriving_local.ipynb`.
2. If CLIP probe artifacts already exist in `weights/clip/linear_probe/`, skip `clip-car-classification-with-linear-probe.ipynb`.
3. Run `use_finetuned_yolo_and_clip_on_video.ipynb` on `original_videos/dashcam.mp4` to produce `runs_output/detect/clip_predict/annotated_video.mp4`.
4. Start Ollama and ensure `qwen3-vl:4b` is available.
5. Run `my_yolo_vlm_step3.ipynb`:
	- setup/import cells,
	- caption generation cell,
	- Q&A cell.

## Important Learning Snippets

### 1) Discover the right output folder under `runs_output/detect/`
Step 3 looks for an annotated video in this priority order: `clip_predict` → highest numbered `predict*` (Ultralytics writes `predict`, `predict2`, `predict3`, …) → bare `predict` → any other sibling dir that already contains a video. Mirrors the notebook's `candidate_output_dirs`.

```python
def candidate_output_dirs(input_root):
	ordered, seen = [], set()

	clip_predict = os.path.join(input_root, "clip_predict")
	if os.path.isdir(clip_predict):
		ordered.append(clip_predict); seen.add(clip_predict)

	numbered = []
	for path in glob.glob(os.path.join(input_root, "predict*")):
		if not os.path.isdir(path):
			continue
		match = re.fullmatch(r"predict[-_]?(\d+)", os.path.basename(path))
		if match:
			numbered.append((int(match.group(1)), path))
	for _, path in sorted(numbered, key=lambda x: x[0], reverse=True):
		if path not in seen:
			ordered.append(path); seen.add(path)

	predict_dir = os.path.join(input_root, "predict")
	if os.path.isdir(predict_dir) and predict_dir not in seen:
		ordered.append(predict_dir); seen.add(predict_dir)

	for path in sorted(glob.glob(os.path.join(input_root, "*"))):
		if os.path.isdir(path) and path not in seen:
			ordered.append(path); seen.add(path)
	return ordered
```

### 2) Robust video selection for Q&A
```python
if "output_video" in globals() and os.path.isfile(output_video):
	video_path = output_video
elif "input_video" in globals() and os.path.isfile(input_video):
	video_path = input_video
else:
	video_path = resolve_input_video()
```

### 3) Safer Q&A response (fallback retry)
```python
answer = (response.message.content or "").strip()
if not answer:
	retry = chat(model=VLM_MODEL, messages=[...], stream=False)
	answer = (retry.message.content or "").strip()
```

## Outputs
- Stage 1 (optional) compressed YOLO video: `runs_output/detect/predict*/converted_mp4/*_compressed.mp4` (produced by the Stage 1 `ffmpeg` cell).
- Stage 2 video: `runs_output/detect/clip_predict/annotated_video.mp4`
- Stage 3 captioned video: `runs_output/detect/<selected_output_dir>/vlm_overlay/*_vlm.mp4`
  (`<selected_output_dir>` = `clip_predict` if it exists, else the highest-numbered `predict*`, else `predict`)

## Notes
- Q&A uses one selected frame per timestamp (single-frame reasoning).
- Model/brand identification is uncertain from many frames; prefer type/color/position unless clear.