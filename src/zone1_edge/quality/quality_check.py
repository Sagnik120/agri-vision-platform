"""Task A1: Quality Check Module"""

import cv2
import numpy as np

def compute_blur_score(img: np.ndarray) -> float:
    """Computes a blur score based on Laplacian variance (resized max 512px grayscale)."""
    # Resize to max 512px on the longest side for performance
    h, w = img.shape[:2]
    max_dim = max(h, w)
    if max_dim > 512:
        scale = 512.0 / max_dim
        img_resized = cv2.resize(img, (int(w * scale), int(h * scale)))
    else:
        img_resized = img.copy()
        
    # Convert to grayscale if it has 3 channels
    if len(img_resized.shape) == 3:
        gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
    else:
        gray = img_resized
        
    # Compute Laplacian variance
    var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return float(var)

def compute_exposure_score(img: np.ndarray) -> float:
    """Computes fraction of pixels in extreme luminance bins (<10 or >250)."""
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img
        
    extreme_dark = np.sum(gray < 10)
    extreme_bright = np.sum(gray > 250)
    total_pixels = gray.size
    
    return float(extreme_dark + extreme_bright) / total_pixels

def compute_quality(img: np.ndarray) -> dict:
    """
    Computes overall image quality.
    Returns: {"quality_score": float, "quality_flag": "ok"|"warn"|"reject", "reasons": [str,...]}
    """
    blur_raw = compute_blur_score(img)
    exposure_raw = compute_exposure_score(img)
    
    # Normalize blur: variance of 150+ is good (1.0), 0 is bad (0.0)
    blur_norm = min(1.0, blur_raw / 150.0)
    
    # Normalize exposure: 0% extreme is good (1.0), 50%+ extreme is bad (0.0)
    exposure_norm = max(0.0, 1.0 - (exposure_raw / 0.5))
    
    quality_score = 0.6 * blur_norm + 0.4 * exposure_norm
    
    reasons = []
    if blur_norm < 0.4:
        reasons.append("Image is too blurry.")
    if exposure_norm < 0.6:
        reasons.append("Image is poorly exposed (too dark or too bright).")
        
    if quality_score < 0.45 or blur_norm < 0.2 or exposure_norm < 0.2:
        flag = "reject"
        if not reasons:
            reasons.append("Overall quality is very low.")
    elif quality_score < 0.6 or blur_norm < 0.5 or exposure_norm < 0.4:
        flag = "warn"
    else:
        flag = "ok"
        
    return {
        "quality_score": float(quality_score),
        "quality_flag": flag,
        "reasons": reasons
    }
