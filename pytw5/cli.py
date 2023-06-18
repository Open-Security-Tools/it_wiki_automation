import logging
import click
from .aliased_group import AliasedGroup
import datetime

log = logging.getLogger(__name__)


# noinspection PyUnusedLocal
def _setup_logging(ctx, obj, verbose):
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO
    )

    if log.isEnabledFor(logging.DEBUG):
        log.debug("Verbose logging enabled")

    return verbose


# noinspection PyUnusedLocal
def _setup_path(ctx, obj, path):
    from .config import singleton
    singleton.initialise(path)
    return singleton.path


@click.group("contexts", cls=AliasedGroup, invoke_without_command=True)
@click.option(
    "--verbose",
    is_flag=True,
    callback=_setup_logging,
    expose_value=False,
    is_eager=True,
    help="Enable DEBUG logging level")
@click.option(
    "-p", "--path",
    callback=_setup_path,
    default=".",
    expose_value=False,
    is_eager=True,
    help="Override working path, default=\".\"")
@click.version_option("0.1")
@click.pass_context
def root_cmd(ctx):

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help(), color=ctx.color)
        ctx.exit()


@root_cmd.command("update")
def update():
    from . import integrator
    updater = integrator.Integrator()
    updater.process_network_interfaces()
    updater.process_ip_addresses()
    updater.process_networks()
    updater.process_dns_lookups()
