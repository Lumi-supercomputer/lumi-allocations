#!/usr/bin/env python

from .data import ProjectInfo
import argparse
import os


def main():
    parser = argparse.ArgumentParser(
        prog="lumi-allocations",
        description="Get data about your LUMI projects",
    )
    parser.add_argument(
        "-p",
        "--projects",
        help="Project numbers comma seperated. Default: all of your projects",
        default="",
    )
    parser.add_argument(
        "-a",
        "--all",
        help="Return information for all projects.",
        action="store_true",
    )
    parser.add_argument("--lust", action="store_true", help="Special flag for LUST")
    args = parser.parse_args()
    projdir = "/projappl"
    projects = []
    not_a_project = {"project_462000009": False, "project_465000002": False}
    if args.all is True:
        # get all projects through listing /projappl and filtering out non-existing projects
        for path in os.listdir(projdir):
            if os.path.islink(os.path.join(projdir, path)) and path not in not_a_project:
                projects.append(path)
        projects.sort()
    else:
        projects = [] if args.projects == "" else args.projects.split(",")
    info = ProjectInfo(projects, args.lust)
    info.printQuotas()
