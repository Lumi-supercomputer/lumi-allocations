from .patches import (
    patch_set_data,
    patch_groups,
    patch_set_projects_with_actual_file,
    patch_set_path,
    patch_getmtime,
    projects,
)
from lumi_allocations.data import ProjectInfo


class TestConstructor:
    def test_constructor(self, patch_groups, patch_set_data, patch_getmtime):
        info = ProjectInfo()
        assert len(info._projects) == len(projects)

    def test_with_projects(self, patch_set_data, patch_getmtime):
        info = ProjectInfo(projects=["project_1"])
        assert len(info._projects) == 1
        assert info._projects[0] == "project_1"

    def test_with_project_file_load(
        self,
        patch_set_projects_with_actual_file,
        monkeypatch,
        patch_set_path,
        patch_getmtime,
    ):
        info = ProjectInfo()
        assert info._data["project_test"]["billing"]["cpu_hours"]["used"] == 750
        assert info._data["project_test"]["billing"]["cpu_hours"]["alloc"] == 1000


class TestQuotaString:
    def test_output(self, patch_groups, patch_set_data, patch_getmtime):
        info = ProjectInfo()
        used = 1
        alloc = 3
        unit = "unit"
        quota = info._makeQuotaString({"used": used, "alloc": alloc}, unit)
        splitQuota = list(filter(lambda i: i != "", quota.split(" ")))
        assert splitQuota[-1] == unit
        assert splitQuota[0] == f"{used}/{alloc}"
        assert splitQuota[1] == f"({used/alloc*100:.1f}%)"
