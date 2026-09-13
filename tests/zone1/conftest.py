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
import random


def create_noisy_image(base_color, size=(64, 64)):
    img = Image.new("RGB", size)
    pixels = img.load()
    for i in range(size[0]):
        for j in range(size[1]):
            r = max(0, min(255, int(random.gauss(base_color[0], 30))))
            g = max(0, min(255, int(random.gauss(base_color[1], 30))))
            b = max(0, min(255, int(random.gauss(base_color[2], 30))))
            pixels[i, j] = (r, g, b)
    return img


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
