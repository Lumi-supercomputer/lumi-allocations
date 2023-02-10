#!/usr/bin/env python

from .data import ProjectInfo
import argparse
import os
import grp


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
    parser.add_argument("-a", "--all", help=argparse.SUPPRESS, action="store_true")
    parser.add_argument("--lust", help=argparse.SUPPRESS, action="store_true")
    args = parser.parse_args()
    if args.lust and "project_462000008" not in [
        grp.getgrgid(a).gr_name for a in os.getgroups()
    ]:
        parser.error("Error: You are not a LUST member")
    if args.all and not args.lust:
        parser.error("-a or --all can only be used with --lust")
    projdir = "/projappl"
    projects = []
    not_a_project = {"project_462000009": False, "project_465000002": False}
    if args.all is True:
        # get all projects through listing /projappl and filtering out non-existing projects
        for path in os.listdir(projdir):
            if (
                os.path.islink(os.path.join(projdir, path))
                and path not in not_a_project
            ):
                projects.append(path)
        projects.sort()
    else:
        projects = [] if args.projects == "" else args.projects.split(",")
    info = ProjectInfo(projects, args.lust)
    info.printQuotas()
