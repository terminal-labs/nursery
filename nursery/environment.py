from nursery.pluginsystem import initialize_plugins
from nursery.pluginsystem import PluginController


class Environment:
    def __init__(self):
        self.targets = []

        self.plugins = {}
        self.plugin_ids_by_class = {}
        self.plugin_controller = PluginController(self)

        initialize_plugins(self)


env = Environment()
