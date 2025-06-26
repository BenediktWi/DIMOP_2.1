import os

os.environ["TESTING"] = "1"

import pytest  # noqa: E402
from pydantic import ValidationError  # noqa: E402

from app.models.schemas import NodeCreate  # noqa: E402


def test_level_zero_no_parent_ok():
    NodeCreate(project_id=1, material_id=2, level=0)


def test_level_zero_with_parent_fails():
    with pytest.raises(ValidationError):
        NodeCreate(project_id=1, material_id=2, level=0, parent_id=1)


def test_level_gt_zero_missing_parent_fails():
    with pytest.raises(ValidationError):
        NodeCreate(project_id=1, material_id=2, level=1)


def test_level_gt_zero_with_parent_ok():
    NodeCreate(project_id=1, material_id=2, level=1, parent_id=1)
