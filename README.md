# Computer Vision HSLU 2026

Local dashcam pipeline that combines YOLO detection with CLIP brand recognition and VLM scene understanding.

## What This Project Does
- Runs YOLO on driving video and saves outputs under `runs_output/detect/predict*`.
- Stores canonical model artifacts under `weights/yolo/` and `weights/clip/linear_probe/`.
- Adds VLM captions using local Ollama (`qwen3-vl:4b`).
- Supports quick frame-based Q&A for audience/demo usage.
- Exports artifacts for reporting: captioned video, optional compressed MP4, and Markdown logs.

## Key Workflow
1. Run YOLO inference/training notebook to produce `predict*` results.
2. Start Ollama server and ensure `qwen3-vl:4b` is available.
3. Run `my_yolo_vlm_step3.ipynb`:
   - setup/import cells,
   - caption generation cell,
   - optional compression,
   - Q&A cell.

## Important Learning Snippets

### 1) Pick the latest numeric `predict-N` folder
```python
def select_predict_dir(input_root):
	predict_base = os.path.join(input_root, "predict")
	predict_dirs = glob.glob(os.path.join(input_root, "predict*"))
	numbered = []
	for path in predict_dirs:
		name = os.path.basename(path)
		match = re.fullmatch(r"predict-(\d+)", name)
		if match:
			numbered.append((int(match.group(1)), path))
	if numbered:
		return max(numbered, key=lambda item: item[0])[1]
	if os.path.isdir(predict_base):
		return predict_base
	return ""
```

### 2) Robust video selection for Q&A
```python
if "compressed_video" in globals() and os.path.isfile(compressed_video):
	video_path = compressed_video
elif "output_video" in globals() and os.path.isfile(output_video):
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
- Captioned video: `runs_output/detect/predict*/vlm_overlay/*_vlm.mp4`
- Optional compressed video: `runs_output/detect/predict*/vlm_overlay/converted_mp4/*_compressed.mp4`
- Log/report file: `runs_output/detect/predict*/vlm_overlay/*_vlm_log.md`

## Notes
- Q&A uses one selected frame per timestamp (single-frame reasoning).
- Model/brand identification is uncertain from many frames; prefer type/color/position unless clear.