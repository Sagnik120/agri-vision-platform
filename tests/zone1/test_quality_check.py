import os
import cv2
import pytest
from src.zone1_edge.quality.quality_check import compute_quality, compute_blur_score, compute_exposure_score

DEMO_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "demo_data")

@pytest.fixture
def sharp_image():
    path = os.path.join(DEMO_DATA_DIR, "sharp.jpg")
    img = cv2.imread(path)
    assert img is not None, f"Missing fixture at {path}"
    return img

@pytest.fixture
def blurry_image():
    path = os.path.join(DEMO_DATA_DIR, "blurry.jpg")
    img = cv2.imread(path)
    assert img is not None, f"Missing fixture at {path}"
    return img

@pytest.fixture
def overexposed_image():
    path = os.path.join(DEMO_DATA_DIR, "overexposed.jpg")
    img = cv2.imread(path)
    assert img is not None, f"Missing fixture at {path}"
    return img

@pytest.fixture
def underexposed_image():
    path = os.path.join(DEMO_DATA_DIR, "underexposed.jpg")
    img = cv2.imread(path)
    assert img is not None, f"Missing fixture at {path}"
    return img

def test_sharp_image_ok(sharp_image):
    result = compute_quality(sharp_image)
    assert result["quality_flag"] == "ok", f"Expected ok, got {result}"
    assert result["quality_score"] > 0.6

def test_blurry_image_reject(blurry_image):
    result = compute_quality(blurry_image)
    assert result["quality_flag"] in ["warn", "reject"], f"Expected warn/reject, got {result}"
    # Specifically blur should be flagged
    assert any("blurry" in r for r in result["reasons"])

def test_overexposed_image_reject(overexposed_image):
    result = compute_quality(overexposed_image)
    assert result["quality_flag"] in ["warn", "reject"], f"Expected warn/reject, got {result}"
    assert any("exposed" in r for r in result["reasons"])

def test_underexposed_image_reject(underexposed_image):
    import numpy as np
    underexposed_image = (underexposed_image * 0.1).astype(np.uint8)
    result = compute_quality(underexposed_image)
    assert result["quality_flag"] in ["warn", "reject"], f"Expected warn/reject, got {result}"
    assert any("exposed" in r for r in result["reasons"])
