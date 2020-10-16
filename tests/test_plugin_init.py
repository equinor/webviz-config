import mock
import warnings
from webviz_config.plugins.plugin_utils import write_metadata

class DistMock:
    def __init__(self, entry_points):
        self.metadata = {
            "name": "test",
            "Project-URL": "Documentation, test.com",
            "Project-URL": "Download, test.com",
            "Project-URL": "Tracker, test.com"
        }

        self.entry_points = entry_points
        self.version = "123"


mock_entrypoint = mock.Mock()
mock_entrypoint.group = "webviz_config_plugins"
mock_entrypoint.name = "testName"

dist_mock = DistMock([mock_entrypoint])
dist_mock2 = DistMock([mock_entrypoint, mock_entrypoint, mock_entrypoint])

metadata = {}
with warnings.catch_warnings(record=True) as w:
    write_metadata([dist_mock], metadata)
    assert len(metadata) == 1, "Wrong number of items in metadata"
    assert len(w) == 0, "Too many warnings"

metadata = {}
with warnings.catch_warnings(record=True) as w:
    write_metadata([dist_mock2], metadata)
    assert len(w) == 1
    assert issubclass(w[-1].category, RuntimeWarning)

    assert len(metadata) == 1, "Wrong number of items in metadata"
    assert metadata["testName"]["dist_name"] ==  "test", "Wrong dist name"

metadata = {}
write_metadata([dist_mock2], metadata)

assert len(metadata) == 1, "Wrong number of items in metadata"
assert metadata["testName"]["dist_name"] ==  "test", "Wrong dist name"