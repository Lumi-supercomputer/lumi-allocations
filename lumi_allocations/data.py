import json
import os
import grp
import sys
from datetime import datetime


class ProjectInfo:
    def __init__(self, projects=[], lust=False):
        self._set_path(lust)
        self._set_projects(projects)
        self._set_data()
        self._has_qpu = any(
            self._data[p]["billing"]["qpu_secs"]["alloc"] > 0 for p in self._data
        )
        if len(self._projects) == 0:
            print("Error: No projects were found")
            sys.exit(0)
        try:
            self._last_modified = datetime.fromtimestamp(
                os.path.getmtime(
                    f"{self._path}/{self._projects[0]}/{self._projects[0]}.json"
                )
            )
        except OSError:
            print(
                "ERROR: Could not access file data",
                file=sys.stderr,
            )
            sys.exit(0)

    def _set_path(self, lust):
        self._path = f"/var/lib/project_info/{'lust' if lust else 'users'}"

    def _set_projects(self, projects):
        if projects != []:
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
            try:
                with open(f"{self._path}/{project}/{project}.json") as f:
                    self._data[project] = json.load(f)
            except OSError:
                print(
                    f"Error: You do not have permissions to access {project}",
                    file=sys.stderr,
                )
                sys.exit(0)

    def _makeQuotaString(self, quota, unit):
        if quota["alloc"] == 0:
            return "N/A"
        percentage = f"({quota['used']/quota['alloc']*100:.1f}%)"
        return f"{quota['used']}/{quota['alloc']} {percentage:>8} {unit}"

    def printQuotas(self):
        print(f"Data updated: {self._last_modified}")
        header = f"{'Project': <20}|{'CPU (used/allocated)':>40}|{'GPU (used/allocated)': >35}|{'Storage (used/allocated)':>35}"
        if self._has_qpu:
            header = header + f"|{'QPU (used/allocated)':>30}"
        print(header)

        print("-" * 164 if self._has_qpu else "-" * 134)
        for project in self._projects:
            billing_data = self._data[project]["billing"]
            storage_hours = billing_data["storage_hours"]
            cpu_hours = billing_data["cpu_hours"]
            gpu_hours = billing_data["gpu_hours"]
            line = f"{project: <20}|{self._makeQuotaString(cpu_hours, 'core/hours'): >40}|{self._makeQuotaString(gpu_hours, 'gpu/hours'): >35}|{self._makeQuotaString(storage_hours, 'TB/hours'): >35}"
            if self._has_qpu:
                qpu_secs = billing_data["qpu_secs"]
                line = line + f"|{self._makeQuotaString(qpu_secs, 'qpu/secs'): >30}"
            print(line)
