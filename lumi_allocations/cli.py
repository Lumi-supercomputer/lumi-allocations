#!/usr/bin/env python

from .data import ProjectInfo
import argparse


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
    parser.add_argument("--lust", action="store_true", help="Special flag for LUST")
    args = parser.parse_args()
    projects = [] if args.projects == "" else args.projects.split(",")
    info = ProjectInfo(projects, args.lust)
    info.printQuotas()
