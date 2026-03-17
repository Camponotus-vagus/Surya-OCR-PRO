## 2025-05-15 - [PDF Rasterization & Coordinate Parsing]
**Learning:** Directly requesting the target colorspace and disabling alpha in PyMuPDF's `get_pixmap` is more efficient than manual conversion. `json.loads` is significantly faster and safer than `eval` for parsing coordinate lists from model output.
**Action:** Always prefer `get_pixmap(..., colorspace=fitz.csRGB, alpha=False)` for RGB rendering and `json.loads` for numeric array strings.

## 2025-05-22 - [CPU Autocast and Redundant Image Copies]
**Learning:** `torch.autocast` with `bfloat16` is extremely slow on CPUs without native support (emulation overhead). Native `float32` is much faster. Also, PIL's `exif_transpose` and `convert` methods return a copy even if the image is already correct; checking `getexif()` and `mode` first avoids redundant allocations.
**Action:** Use `float32` for `autocast` on CPU. Guard PIL transformations with status checks.
