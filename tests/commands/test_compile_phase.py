import os
import json
from tests.factories.model_factories import DashboardFactory, ProjectFactory
from tests.support.utils import temp_file, temp_folder, temp_yml_file
from visivo.commands.compile_phase import compile_phase
from visivo.commands.utils import create_file_database
from visivo.parsers.core_parser import PROFILE_FILE_NAME, PROJECT_FILE_NAME


def test_filtered_dashboard():
    output_dir = temp_folder()
    project = ProjectFactory()
    additional_dashboard = DashboardFactory(name="Other Dashboard")
    additional_dashboard.rows[0].items[0].chart.name = "Additional Chart"
    additional_dashboard.rows[0].items[0].chart.traces[0].name = "Additional Trace"
    additional_dashboard.rows[0].items[0].chart.traces[0].model.name = "Additional Model"
    project.dashboards.append(additional_dashboard)
    create_file_database(url=project.targets[0].url(), output_dir=output_dir)

    tmp = temp_yml_file(dict=json.loads(project.model_dump_json()), name=PROJECT_FILE_NAME)
    working_dir = os.path.dirname(tmp)

    compile_phase(
        default_target="target",
        working_dir=working_dir,
        output_dir=output_dir,
        name_filter="dashboard",
    )
    assert "Additional Trace" not in os.listdir(output_dir)
    assert "trace" in os.listdir(output_dir)
 
