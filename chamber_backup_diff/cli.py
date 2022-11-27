"""Console script for chamber_backup_diff."""

import sys
from pathlib import Path

import click
import click.core

from .diff import ChamberDiff
from .exception_handler import ExceptionHandler
from .shell import _shell_completion
from .version import __timestamp__, __version__

header = f"{__name__.split('.')[0]} v{__version__} {__timestamp__}"


def _ehandler(ctx, option, debug):
    ctx.obj = dict(ehandler=ExceptionHandler(debug))
    ctx.obj["debug"] = debug


@click.command("cbdiff", context_settings={"auto_envvar_prefix": "CBDIFF"})
@click.version_option(message=header)
@click.option(
    "-d",
    "--debug",
    is_eager=True,
    is_flag=True,
    callback=_ehandler,
    help="debug mode",
)
@click.option(
    "--shell-completion",
    is_flag=False,
    flag_value="[auto]",
    callback=_shell_completion,
    help="configure shell completion",
)
@click.option(
    "-o", "--old-name", type=str, default="old", help="name of old tarball"
)
@click.option(
    "-O", "--old-prefix", type=str, default=None, help="old channel prefix"
)
@click.option(
    "-n", "--new-name", type=str, default="new", help="name of new tarball"
)
@click.option(
    "-N", "--new-prefix", type=str, default=None, help="new channel prefix"
)
@click.argument(
    "old-tarball",
    type=click.Path(dir_okay=False, readable=True, path_type=Path),
)
@click.argument(
    "new-tarball",
    type=click.Path(dir_okay=False, readable=True, path_type=Path),
)
@click.pass_context
def cli(
    ctx,
    debug,
    shell_completion,
    old_name,
    old_prefix,
    new_name,
    new_prefix,
    old_tarball,
    new_tarball,
):
    """diff contents of chamber backup tarballs"""
    ChamberDiff().compare(
        old_name, old_prefix, old_tarball, new_name, new_prefix, new_tarball
    )


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
