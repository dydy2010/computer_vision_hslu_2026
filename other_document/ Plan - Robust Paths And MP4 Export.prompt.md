## Plan: Robust Paths And MP4 Export

Make the local notebook resilient to dataset location differences and add a safe MP4 conversion cell that targets ~100MB output using ffmpeg, without changing Colab content or output management policies. Keep changes minimal and focused on the local notebook.

**Steps**
1. Update dataset path logic in the local notebook to resolve in this order: `DATASET_DIR` env var (if set) then `./Self-Driving-Car-3`, then `./self-driving-car`; raise a clear error if none exist. *Only run this when `USE_ROBOFLOW` is False.*
2. Modify the existing dataset setup cell to use the new path resolver and keep current `USE_ROBOFLOW` behavior unchanged.
3. Add a new, separate code cell after the video inference cell to convert the newest `runs_output/detect/predict*` output to MP4 using ffmpeg. The cell should:
	- verify `ffmpeg` exists (otherwise print an install hint and exit)
	- find the newest `runs_output/detect/predict*` folder and newest video inside it
	- create `converted_mp4/` inside that newest predict folder
	- compute bitrate from video duration to target ~100MB output
4. Keep output management as-is (no new artifact folders or gitignore changes).

**Verification**
1. In the local notebook, set `USE_ROBOFLOW = False` and confirm it picks `Self-Driving-Car-3` or `self-driving-car` when present; verify the printed `data.yaml` path is correct.
2. Run the video inference cell to generate an output in `runs_output/detect/predict*/`.
3. Run the new MP4 conversion cell and verify it produces an `.mp4` file in `runs_output/detect/predict*/converted_mp4/`, and logs the output path and size.

**Decisions**
- Use ffmpeg for conversion (fast, reliable) with a target ~100MB output.
- Add dataset path fallbacks for `DATASET_DIR` env var and `self-driving-car`.
- No changes to output management or reproducibility beyond path robustness.

**Further Considerations**
1. If ffmpeg is not installed on the target machine, add a short install note (no automatic install).
