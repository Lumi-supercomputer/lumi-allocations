import pytest
from pathlib import Path
import os

import lumi_allocations.data


@pytest.fixture
def patch_set_projects(monkeypatch):
    def mock_set_projects(self, _):
        self._projects = ["project_1", "project_2", "project_3"]

    monkeypatch.setattr(
        lumi_allocations.data.ProjectInfo,
        "_set_projects",
        mock_set_projects,
    )


@pytest.fixture
def patch_set_projects_with_actual_file(monkeypatch):
    def mock_set_projects(self, _):
        self._projects = ["project_test"]

    monkeypatch.setattr(
        lumi_allocations.data.ProjectInfo,
        "_set_projects",
        mock_set_projects,
    )


@pytest.fixture
def patch_set_path(monkeypatch):
    def mock_set_path(self, _):
        self._path = Path("./lumi_allocations/tests")

    monkeypatch.setattr(
        lumi_allocations.data.ProjectInfo,
        "_set_path",
        mock_set_path,
    )


@pytest.fixture
def patch_set_data(monkeypatch):
    def gen_data():
        return {
            "billing": {
                "cpu_hours": {
                    "used": 1,
                    "alloc": 2,
                },
                "gpu_hours": {
                    "used": 1,
                    "alloc": 2,
                },
                "storage_hours": {
                    "used": 1,
                    "alloc": 2,
                },
            }
        }

    def mock_set_data(self):
        self._data = {}
        projects = {
            "project_1": gen_data(),
            "project_2": gen_data(),
            "project_3": gen_data(),
        }

        for project in self._projects:
            self._data[project] = projects[project]

    monkeypatch.setattr(
        lumi_allocations.data.ProjectInfo,
        "_set_data",
        mock_set_data,
    )
