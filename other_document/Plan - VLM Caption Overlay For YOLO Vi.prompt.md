## Plan: VLM Caption Overlay For YOLO Video

Goal: Add a local VLM captioning step that fuses scene-level descriptions with YOLO detections and overlays text onto the video output (Option 1), using well-known, easy-to-run packages.

**Scope**
- Local notebook only (no Colab changes).
- Use existing YOLO video output in runs_output/detect/predict*/.
- Add new cells for VLM install, captioning, and video overlay.

**Steps**
1. Pick a local image-to-text model that is widely used and easy to run on GPU.
   - Primary: LLaVA 1.5 (7B) via Hugging Face Transformers.
   - Alternate (lighter): BLIP-2 (Flan-T5 XL).
2. Add a setup cell to install required packages: transformers, accelerate, sentencepiece, bitsandbytes (optional), and opencv-python if not present.
3. Add a captioning cell that:
   - Samples frames every N seconds.
   - Runs VLM on each sampled frame to produce a short scene caption.
4. Add an overlay cell that:
   - Loads the YOLO-annotated video from runs_output/detect/predict*/.
   - Draws the latest caption at the top (banner text).
   - Writes a new annotated MP4 output.
5. Keep output files under runs_output/detect/predict*/vlm_overlay/.

**Outputs**
- Annotated MP4 with YOLO boxes + VLM scene captions.
- Optional CSV with timestamp -> caption for the report.

**Verification**
1. Run the captioning cell on a short video segment (10-30 seconds) to confirm speed and quality.
2. Run the overlay cell and check that captions appear and the MP4 plays.

**Decisions Needed**
- Final model choice: LLaVA 1.5 (7B) vs BLIP-2 (Flan-T5 XL).
- Caption frequency (every 1s, 2s, or N frames).
- Whether to add per-box labels from VLM (optional, heavier).
