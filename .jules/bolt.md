## 2025-05-15 - [PDF Rasterization & Coordinate Parsing]
**Learning:** Directly requesting the target colorspace and disabling alpha in PyMuPDF's `get_pixmap` is more efficient than manual conversion. `json.loads` is significantly faster and safer than `eval` for parsing coordinate lists from model output.
**Action:** Always prefer `get_pixmap(..., colorspace=fitz.csRGB, alpha=False)` for RGB rendering and `json.loads` for numeric array strings.

## 2025-05-15 - [Image Handling Optimizations]
**Learning:** Pillow's `ImageOps.exif_transpose()` and `convert("RGB")` return full image copies even if no transformation is needed. On large (4000x4000) images, this adds ~0.1s per call and massive memory overhead. Delaying `image.copy()` until visualization is strictly necessary saves ~0.7s per 50 pages during OCR.
**Action:** Always check `if img.getexif()` before transposing and `if img.mode != "RGB"` before converting. Access `.size` directly from original images.
