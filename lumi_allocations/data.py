import json
import os
import grp


class ProjectInfo:
    def __init__(self, projects=[], lust=False):
        self._set_path(lust)
        self._set_projects(projects)
        self._set_data()

    def _set_path(self, lust):
        self._path = f"/var/lib/project_info/{'lust' if lust else 'users'}"

    def _set_projects(self, projects):
        if projects is not []:
            self._projects = projects
        else:
            self._projects = [
                grp.getgrgid(a).gr_name
                for a in os.getgroups()
                if grp.getgrgid(a).gr_name.startswith("project_")
            ]

    def _set_data(self):
        self._data = {}
        for project in self._projects:
            with open(f"{self._path}/{project}/{project}.json") as f:
                self._data[project] = json.load(f)

    def _makeQuotaString(self, quota, unit):
        if quota["alloc"] == 0:
            return "N/A"
        percentage = f"({quota['used']/quota['alloc']*100:.1f}%)"
        return f"{quota['used']}/{quota['alloc']} {percentage:>8} {unit}"

    def printQuotas(self):
        print(
            f"{'Project': <20}|{'CPU (used/allocated)':>40}|{'GPU (used/allocated)': >35}|{'Storage (used/allocated)':>30}"
        )
        print("-" * 128)
        for project in self._projects:
            billing_data = self._data[project]["billing"]
            storage_hours = billing_data["storage_hours"]
            cpu_hours = billing_data["cpu_hours"]
            gpu_hours = billing_data["gpu_hours"]
            print(
                f"{project: <20}|{self._makeQuotaString(cpu_hours, 'core/hours'): >40}|{self._makeQuotaString(gpu_hours, 'gpu/hours'): >35}|{self._makeQuotaString(storage_hours, 'TB/hours'): >30}"
            )
