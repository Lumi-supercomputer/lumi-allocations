from .patches import (
    patch_set_data,
    patch_groups,
    patch_set_projects_with_actual_file,
    patch_set_path,
    patch_getmtime,
    projects,
)
from lumi_allocations.cli import main


class TestMain:
    def test_run_main(self, patch_groups, patch_set_data, patch_getmtime, capsys):
        main()
        captured = capsys.readouterr()
        for key in projects.keys():
            assert key in captured.out
