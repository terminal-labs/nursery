"""This module provides resources that need to be available to both the main nursery cli
and the cli in plugins.
"""

from functools import update_wrapper

from click import get_current_context

from nursery.pluginsystem import plugin_from_short_name
from nursery.targets import TargetPlugin


DEFAULT_CONTEXT_SETTINGS = {
    "auto_envvar_prefix": "NURSERY",
    "ignore_unknown_options": True,
    "allow_extra_args": True,
    "help_option_names": ["-h", "--help"],
}


class Context:
    def __init__(self, *args, **kwargs):
        # Allows for this context to be modified by click functions like attach_target
        self.context = self

        from nursery.environment import env
        self.env = env


def attach_target(f):
    """Decorator that finds the target and adds it to the context of the child command
    so that it can easily call its actions.
    """

    def new_func(*args, **kwargs):
        ctx = get_current_context()

        if ctx.info_name in TargetPlugin.root_actions:  # nursery cp vbox
            target = plugin_from_short_name(ctx.env, ctx.invoked_subcommand)
        else:  # nursery vbox cp
            target = plugin_from_short_name(ctx.env, ctx.info_name)

        if target:
            # This is picked up and added to ctx on the next merge.
            # This has the same effect as `ctx.obj.target = target` adding ctx.target,
            # but additionally adds target to our Context object,
            # so target is available for use there as well.
            #
            # This works because the contexts are merged by pass_context.
            ctx.context.target = target

        return f(*args, **kwargs)

    return update_wrapper(new_func, f)


# Copied from click/decorators.py, with the addition of being able to merge contexts
# See https://github.com/pallets/click/pull/1558
def merge_contexts(ctx, obj):
    """Return the given context with the attributes of another object
    merged into it. This is useful to attach a separate application
    context to a Click context.
    """
    for attr in obj.__dir__():
        if not attr.startswith("__"):
            ctx.__setattr__(attr, getattr(obj, attr))
    return ctx


def make_pass_decorator(object_type, ensure=False, merge=False):
    """Given an object type this creates a decorator that will work
    similar to :func:`pass_obj` but instead of passing the object of the
    current context, it will find the innermost context of type
    :func:`object_type`.

    This generates a decorator that works roughly like this::

        from functools import update_wrapper

        def decorator(f):
            @pass_context
            def new_func(ctx, *args, **kwargs):
                obj = ctx.find_object(object_type)
                return ctx.invoke(f, obj, *args, **kwargs)
            return update_wrapper(new_func, f)
        return decorator

    .. versionchanged:: 7.1.3
       Added the `merged` parameter.

    :param object_type: the type of the object to pass.
    :param ensure: if set to `True`, a new object will be created and
                   remembered on the context if it's not there yet.
    :param merge: if set to `True`, the object will be merged with
                   the default context object.
    """

    def decorator(f):
        def new_func(*args, **kwargs):
            ctx = get_current_context()
            if ensure:
                obj = ctx.ensure_object(object_type)
            else:
                obj = ctx.find_object(object_type)
            if obj is None:
                raise RuntimeError(
                    "Managed to invoke callback without a context"
                    f" object of type {object_type.__name__!r}"
                    " existing."
                )
            if merge:
                return f(merge_contexts(ctx, obj), *args, **kwargs)
            else:
                return ctx.invoke(f, obj, *args, **kwargs)

        return update_wrapper(new_func, f)

    return decorator


pass_context = make_pass_decorator(Context, ensure=True, merge=True)
