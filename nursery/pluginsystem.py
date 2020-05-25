import pkg_resources
from pkg_resources import get_distribution

import click


class Plugin(object):
    """This needs to be subclassed for custom plugins."""

    name = "Your Plugin Name"
    description = "Description goes here"

    def __init__(self, env, plugin_id=None):
        self.env = env
        if plugin_id:
            self.plugin_id = plugin_id

    @property
    def version(self):
        return get_distribution("nursery-" + self.plugin_id).version


def plugin_from_short_name(env, name):
    for plugin in env.plugin_ids_by_class:
        if name == plugin.short_name:
            return env.plugins[env.plugin_ids_by_class[plugin]]
    return None


def load_plugins():
    """Loads all available plugins and returns them."""
    plugins = {}
    # Find (pip) installed plugins by name and load them.
    for ep in pkg_resources.iter_entry_points("nursery.plugins"):
        match_name = ep.name.lower()
        if match_name != ep.dist.project_name.lower():
            raise RuntimeError(
                f"Mismatching entry point name.  Found {ep.name} but expected "
                f"{ep.dist.project_name[8:]} for package {ep.dist.project_name}."
            )
        plugins[ep.name] = ep.load()  # Import the remaining plugins
    return plugins


def initialize_plugins(env):
    """Loads and initializes the plugins for the environment."""
    # Plugins imported in load_plugins are pre-initialized by viture of their import
    plugins = load_plugins()
    for plugin_id, plugin_cls in plugins.items():
        env.plugin_controller.instanciate_plugin(plugin_id, plugin_cls)
    env.plugin_controller.emit("setup_env")


class PluginController(object):
    """Helper management class that is used to control plugins through the environment.
    """

    def __init__(self, env):
        self.env = env

    def emit(self, event):
        rv = {}
        funcname = f"on_{event}"
        for plugin_cls in self.env.plugins.values():
            handler = getattr(plugin_cls, funcname, None)
            if handler:
                rv[plugin_cls.plugin_id] = handler()
        return rv

    def instanciate_plugin(self, plugin_id, plugin_cls):
        env = self.env
        if plugin_id in env.plugins:
            raise RuntimeError('Plugin "%s" is already registered' % plugin_id)

        try:
            # Iinstanciates the plugin
            env.plugins[plugin_id] = plugin_cls(env, plugin_id)
        except TypeError:
            # This plugin class probably doesn't have the required methods
            click.secho(
                f"{plugin_id} can't be used. Talk to its maintainer.",
                fg="red",
                err=True,
            )
            pass
        env.plugin_ids_by_class[plugin_cls] = plugin_id
        pass

    def sort_plugins(self):
        """Sort the plugins giving various preferences like local > included > external
        """
        self.plugins.sort()
