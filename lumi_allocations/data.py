import json
import os
import grp
import sys
from datetime import datetime

from operator import itemgetter


class ProjectInfo:
    def __init__(self, projects=[], lust=False, sort_spec=None):
        self._set_path(lust)
        self._set_projects(projects)
        self._set_sort_spec(sort_spec)
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

    def _set_sort_spec(self, sort_spec):
        self._sort_spec = sort_spec

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
            percentage = "(N/A)"
        else:
            percentage = f"({quota['used']/quota['alloc']*100:.1f}%)"
        return f"{quota['used']}/{quota['alloc']} {percentage:>8} {unit}"

    def _multisort(self, projects, specs):
        for item, reverse in reversed(specs):
            projects.sort(key=itemgetter(item), reverse=reverse)
        return projects

    def printQuotas(self):
        print(f"Data updated: {self._last_modified}")
        header = f"{'Project': <20}|{'CPU (used/allocated)':>40}|{'GPU (used/allocated)': >35}|{'Storage (used/allocated)':>35}"
        if self._has_qpu:
            header = header + f"|{'QPU (used/allocated)':>30}"
        print(header)
        projects = []
        if self._sort_spec is not None:
            # sort projects according to +/-
            #   n (name),
            #   C (CPU abs used), c (CPU % used)
            #   G (GPU abs used), g (GPU % used)
            #   S (storage abs used), s (storage % used)
            sort_field = {
                "n": 0,
                "C": 1,
                "c": 2,
                "G": 3,
                "g": 4,
                "S": 5,
                "s": 6,
            }
            sorted_projects = []
            for project in self._projects:
                billing_data = self._data[project]["billing"]
                storage_hours = billing_data["storage_hours"]
                cpu_hours = billing_data["cpu_hours"]
                gpu_hours = billing_data["gpu_hours"]
                # each list item's elements need to be in the order specified in sort_field
                sorted_projects.append(
                    (
                        project,
                        cpu_hours["used"],
                        0
                        if cpu_hours["alloc"] == 0
                        else cpu_hours["used"] / cpu_hours["alloc"],
                        gpu_hours["used"],
                        0
                        if gpu_hours["alloc"] == 0
                        else gpu_hours["used"] / gpu_hours["alloc"],
                        storage_hours["used"],
                        0
                        if storage_hours["alloc"] == 0
                        else storage_hours["used"] / storage_hours["alloc"],
                    )
                )
            msp = []
            for sp in self._sort_spec.split(","):
                sp_field = ""
                reverse = False
                if sp[0] == "-" or sp[0] == "+":
                    sp_field = sp[1:]
                    if sp[0] == "-":
                        reverse = True
                    else:
                        reverse = False
                else:
                    sp_field = sp[0]
                if sp_field not in sort_field:
                    print(f"ignoring unknown sort label '{sp_field}'")
                    next
                msp.append((sort_field[sp_field], reverse))
            sorted_projects = self._multisort(sorted_projects, list(msp))
            projects = [p[0] for p in sorted_projects]
        else:
            projects = self._projects

        print("-" * 164 if self._has_qpu else "-" * 134)
        for project in projects:
            billing_data = self._data[project]["billing"]
            storage_hours = billing_data["storage_hours"]
            cpu_hours = billing_data["cpu_hours"]
            gpu_hours = billing_data["gpu_hours"]
            line = f"{project: <20}|{self._makeQuotaString(cpu_hours, 'core/hours'): >40}|{self._makeQuotaString(gpu_hours, 'gpu/hours'): >35}|{self._makeQuotaString(storage_hours, 'TB/hours'): >35}"
            if self._has_qpu:
                qpu_secs = billing_data["qpu_secs"]
                line = line + f"|{self._makeQuotaString(qpu_secs, 'qpu/secs'): >30}"
            print(line)
