# Computer Vision HSLU 2026

Local dashcam pipeline that combines YOLO detection with CLIP brand recognition and VLM scene understanding.

## What This Project Does
- Runs YOLO on driving video and saves outputs under `runs_output/detect/predict*`.
- Stores canonical model artifacts under `weights/yolo/` and `weights/clip/linear_probe/`.
- Adds VLM captions using local Ollama (`qwen3-vl:4b`).
- Supports quick frame-based Q&A for audience/demo usage.
- Exports artifacts for reporting: captioned video, optional compressed MP4, and Markdown logs.

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
- Step 2 video: `runs_output/detect/clip_predict/annotated_video.mp4`
- Step 3 captioned video: `runs_output/detect/<selected_output_dir>/vlm_overlay/*_vlm.mp4`
- Optional compressed video: `runs_output/detect/<selected_output_dir>/vlm_overlay/converted_mp4/*_compressed.mp4`
- Log/report file: `runs_output/detect/<selected_output_dir>/vlm_overlay/*_vlm_log.md`

## Notes
- Q&A uses one selected frame per timestamp (single-frame reasoning).
- Model/brand identification is uncertain from many frames; prefer type/color/position unless clear.