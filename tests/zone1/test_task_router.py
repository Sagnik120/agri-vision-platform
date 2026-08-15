import pytest
from src.zone1_edge.task_router import task_router


def test_route_crop(synthetic_crop_image):
    out = task_router.route("crop", synthetic_crop_image, mode="mock")
    assert out["domain"] == "crop"


def test_route_livestock(synthetic_livestock_image):
    out = task_router.route("livestock", synthetic_livestock_image, mode="mock")
    assert out["domain"] == "livestock"


def test_invalid_domain_raises(synthetic_crop_image):
    with pytest.raises(ValueError):
        task_router.route("fish", synthetic_crop_image, mode="mock")
