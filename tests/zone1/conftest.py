"""
conftest.py — shared pytest fixtures for Zone 1 (Person A) tests.

Forces AGRIVISION_EXPERT_MODE=mock for the whole test session so tests run
fast, deterministic, and WITHOUT internet / downloaded HF models. This is
what proves the pipeline logic (fusion, gate, advisory, router) is correct
independent of which real model gets swapped in later.
"""

import os

os.environ["AGRIVISION_EXPERT_MODE"] = "mock"

import pytest
from PIL import Image
import numpy as np


def create_noisy_image(base_color, size=(64, 64)):
    arr = np.random.normal(loc=base_color, scale=30, size=(size[0], size[1], 3))
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


@pytest.fixture(scope="session")
def synthetic_crop_image(tmp_path_factory):
    path = tmp_path_factory.mktemp("imgs") / "crop.jpg"
    create_noisy_image((100, 180, 90)).save(path)
    return str(path)


@pytest.fixture(scope="session")
def synthetic_livestock_image(tmp_path_factory):
    path = tmp_path_factory.mktemp("imgs") / "livestock.jpg"
    create_noisy_image((180, 140, 100)).save(path)
    return str(path)
