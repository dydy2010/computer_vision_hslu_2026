
# Project Report — YOLO + VLM Captioned Dashcam Demo

## 1. Project Summary
This project combines YOLO detection with a local Vision Language Model (VLM) to create a captioned dashcam demo. The pipeline is designed for reproducibility and presentation use: it generates an annotated video, optional compressed export, and text logs.

## 2. Objectives
- Detect driving-scene objects with YOLO.
- Add VLM-based scene understanding and audience-friendly captions.
- Provide a simple Q&A interface for selected timestamps.
- Export compact outputs suitable for reports and slides.

## 3. Data and Environment
- Dataset: Self-Driving-Car-3 (kept locally; not intended for git upload).
- Inference outputs: `runs_output/detect/predict*`.
- VLM runtime: Ollama + `qwen3-vl:4b` (local).

## 4. Implemented Pipeline
### 4.1 Detection and Input Resolution
- YOLO outputs are read from `runs_output/detect`.
- The system prefers the highest numeric folder (`predict-N`) for deterministic behavior.

```python
match = re.fullmatch(r"predict-(\d+)", name)
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
	`compressed_video` -> `output_video` -> `input_video` -> resolved predict video.
- Empty-response fallback retry for Q&A prompt.
- Widget/session guards to reduce duplicated callback behavior during reruns.

## 5. Outputs
- Captioned video: `runs_output/detect/predict*/vlm_overlay/*_vlm.mp4`
- Optional compressed video: `runs_output/detect/predict*/vlm_overlay/converted_mp4/*_compressed.mp4`
- Caption log: `runs_output/detect/predict*/vlm_overlay/*_vlm_log.md`

## 6. Current Results
- End-to-end demo is operational.
- Prompting behavior improved from rigid template to smarter, question-first style.
- Response speed and stability improved with bounded generation and fallback handling.

## 7. Known Limits and Next Sections
- Single-frame Q&A can miss temporal context.
- Exact vehicle brand/model is often uncertain from dashcam distance and resolution.
- Future sections planned: temporal reasoning, YOLO-vs-VLM object consistency scoring, and final evaluation metrics.

