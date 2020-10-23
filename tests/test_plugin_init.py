import mock
import warnings
from webviz_config.plugins.plugin_utils import write_metadata

class DistMock:
    def __init__(self, entry_points, name):
        self.metadata = {
            "name": name,
            "Project-URL": "Documentation, test.com",
            "Project-URL": "Download, test.com",
            "Project-URL": "Tracker, test.com"
        }

        self.entry_points = entry_points
        self.version = "123"


mock_entrypoint = mock.Mock()
mock_entrypoint.group = "webviz_config_plugins"
mock_entrypoint.name = "testName"

dist_mock = DistMock([mock_entrypoint], 'dist_mock_1')
dist_mock2 = DistMock([mock_entrypoint, mock_entrypoint, mock_entrypoint], 'dist_mock_2')

metadata = {}
with warnings.catch_warnings(record=True) as w:
    write_metadata([dist_mock], metadata)
    assert len(metadata) == 1, "Wrong number of items in metadata"
    assert len(w) == 0, "Too many warnings"

metadata = {}
with warnings.catch_warnings(record=True) as w:
    write_metadata([dist_mock, dist_mock2], metadata)   
    assert len(w) == 1
    assert issubclass(w[-1].category, RuntimeWarning)
    assert str(w[-1].message) == "Plugin testName already exists. Previously loaded from package: 'dist_mock_1'. Overwriting using package : 'dist_mock_2'"

    assert len(metadata) == 1, "Wrong number of items in metadata"
    assert metadata["testName"]["dist_name"] ==  "dist_mock_2", "Wrong dist name"

metadata = {}
write_metadata([dist_mock2], metadata)

assert len(metadata) == 1, "Wrong number of items in metadata"
assert metadata["testName"]["dist_name"] ==  "dist_mock_2", "Wrong dist name"