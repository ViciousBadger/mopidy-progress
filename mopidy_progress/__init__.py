import logging
import pathlib

import pkg_resources

from mopidy import config, ext

__version__ = pkg_resources.get_distribution("Mopidy-Progress").version

# TODO: If you need to log, use loggers named after the current Python module
logger = logging.getLogger(__name__)


class Extension(ext.Extension):

    dist_name = "Mopidy-Progress"
    ext_name = "progress"
    version = __version__

    def get_default_config(self):
        return config.read(pathlib.Path(__file__).parent / "ext.conf")

    def get_config_schema(self):
        schema = super().get_config_schema()
        schema["patterns"] = config.List()
        schema["min_length_minutes"] = config.Integer(minimum=0)
        return schema

    def setup(self, registry):
        from .frontend import ProgressFrontend
        registry.add("frontend", ProgressFrontend)
