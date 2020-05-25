"""This module provides setup for Plugins that provide Targets.
"""

from abc import ABC, abstractmethod
from importlib import import_module

from nursery.pluginsystem import Plugin


def cp_cmd():
    raise NotImplementedError


def destroy_cmd():
    raise NotImplementedError


def halt_cmd():
    raise NotImplementedError


def ssh_cmd():
    raise NotImplementedError


def up_cmd():
    raise NotImplementedError


class TargetPlugin(ABC, Plugin):
    """This needs to be subclassed for targets.

    This base class specifes that the root commands all need to be created and used,
    or at least disabled deliberately.

    This makes the assumption that the cli commands are placed in the module scope of
    the plugin. This allows for a very clean looking target plugin module at the cost
    of an unusual function lookup here.

    Everything here can be overridden by the target plugin.

    Example 1: If a target does not support `halt`, then it would set `actions`
    without that string, and omit creating a module scoped `halt_cmd` click command.

    Example 2: If a plugin developer wants to isolate its cli commands into a new a
    dedicated module, or simple use different function names, it would need to
    overwrite `cli_entry_func` and `root_command_map`.
    """

    # These are the root commands that every plugin is expected to support.
    # Overwrite this with elements removed if anything isn't supported.
    root_actions = ["cp", "destroy", "halt", "ssh", "up"]

    @property
    def cli_entry_func(self):
        """Return the `cli` function from the module scope of the plugin.
        """
        return getattr(import_module(self.__module__), "cli")

    @property
    def root_command_map(self):
        """Return the a dict mapping names of root actions to their cli command
        functions from the plugin's module scope.
        """
        return {
            action: getattr(import_module(self.__module__), f"{action}_cmd")
            for action in self.root_actions
        }

    @abstractmethod
    def cp(self):
        pass

    @abstractmethod
    def destroy(self):
        pass

    @abstractmethod
    def halt(self):
        pass

    @abstractmethod
    def ssh(self):
        pass

    @abstractmethod
    def up(self):
        pass
