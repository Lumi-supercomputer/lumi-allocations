import pytest
from pathlib import Path
import os
import grp
import time

import lumi_allocations.data


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
            "qpu_secs": {
                "used": 1,
                "alloc": 2,
            },
            "storage_hours": {
                "used": 1,
                "alloc": 2,
            },
        }
    }


projects = {
    "project_1": gen_data(),
    "project_2": gen_data(),
    "project_3": gen_data(),
}


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
def patch_groups(monkeypatch):
    def mock_os_getgroups():
        return range(1, len(projects) + 1)

    class MockGrpid:
        def __init__(self, id):
            self.gr_name = f"project_{id}"

    def mock_grp_getgrgid(id):
        return MockGrpid(id)

    monkeypatch.setattr(os, "getgroups", mock_os_getgroups)
    monkeypatch.setattr(grp, "getgrgid", mock_grp_getgrgid)


@pytest.fixture
def patch_set_data(monkeypatch):
    def mock_set_data(self):
        self._data = {}

        for project in self._projects:
            self._data[project] = projects[project]

    monkeypatch.setattr(
        lumi_allocations.data.ProjectInfo,
        "_set_data",
        mock_set_data,
    )


@pytest.fixture
def patch_getmtime(monkeypatch):
    monkeypatch.setattr(os.path, "getmtime", lambda _: time.time())
