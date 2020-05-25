"""Explanation of cli tree by way of examples:
nursery --help                                     shows basic command lists plus list of installed targets like vbox, do, vbox
nursery up --help                                  displays generic options and list of compatible targets
nursery up vbox --help / nursery vbox up --help    displays vbox specific up options
nursery vbox --help                                displays list of vbox commands
nursery vbox resize --help                         displays help menu for just this vbox command

Future work: If there is a detected target by env var or config, then it isn't needed by the cli.
`NURSERY_TARGET=vbox nursery up` would be the same as `nursery vbox up`
"""

import pkg_resources

import click

from nursery.context import DEFAULT_CONTEXT_SETTINGS
from nursery.context import attach_target
from nursery.context import pass_context
from nursery.environment import env
from nursery.targets import TargetPlugin

version = pkg_resources.get_distribution("nursery").version


@click.group(context_settings=DEFAULT_CONTEXT_SETTINGS)
@click.version_option(prog_name="Nursery", version=version)
@pass_context
def cli(ctx):
    pass


@cli.group("cp", context_settings=DEFAULT_CONTEXT_SETTINGS)
@pass_context
@attach_target
def cp_cmd(ctx):
    """Copy files.
    """
    pass


@cli.group("destroy", context_settings=DEFAULT_CONTEXT_SETTINGS)
@pass_context
@attach_target
def destroy_cmd(ctx):
    """Destroy an instance.
    """
    pass


@cli.group("halt", context_settings=DEFAULT_CONTEXT_SETTINGS)
@pass_context
@attach_target
def halt_cmd(ctx):
    """Turn off an instance, but don't destroy it. It can be restarted later.
    """
    pass


@cli.group("ssh", context_settings=DEFAULT_CONTEXT_SETTINGS)
@pass_context
@attach_target
def ssh_cmd(ctx):
    """SSH into an instance.
    """
    pass


@cli.group("up", context_settings=DEFAULT_CONTEXT_SETTINGS)
@pass_context
@attach_target
def up_cmd(ctx):
    """Create an instance, or turn on an existing instance.
    """
    pass


def register_target_commands():
    """This function takes the main cli entry point and root groups in this module and
    adds to them the plugin's groups and commands.

    Example, consider a target `vbox` that has an `up` command, and `resize` command.
    Prior to this function, `nursery` and `nursery up` exist. This function would
    register the `nursery vbox` group that gives access to all of the target's commands,
    like `nursery vbox up`. This will also register `nursery up vbox` as an alias to
    `nursery vbox up`. It will do this for each of the primary root commands listed
    by TargetPlugin.root_actions.
    """
    for plugin_cls in env.plugins.values():
        # Add target group to root commands. E.g. create `nursery vbox`
        cli.add_command(plugin_cls.cli_entry_func, plugin_cls.cli_entry_func.name)

        for cmd in TargetPlugin.root_actions:
            if cmd in plugin_cls.root_command_map:
                # Find the corresponding group in this module to add the target's
                # command group to. E.g. Find `nursery up` and add `vbox` to it.
                globals()[f"{cmd}_cmd"].add_command(
                    plugin_cls.root_command_map[cmd], plugin_cls.cli_entry_func.name
                )


register_target_commands()

main = cli
