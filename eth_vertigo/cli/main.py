import click
from os import getcwd
from pathlib import Path
from eth_vertigo.core import MutationResult
from eth_vertigo.core.network import DynamicNetworkPool, StaticNetworkPool, Ganache
from eth_vertigo.core.truffle.truffle_campaign import TruffleCampaign
from eth_vertigo.core.filters.sample_filter import SampleFilter
from eth_vertigo.core.filters.exclude_filter import ExcludeFilter
from eth_vertigo.test_runner.truffle import TruffleRunnerFactory
from eth_vertigo.test_runner.exceptions import TestRunException
from eth_vertigo.interfaces.truffle import Truffle
from eth_vertigo.mutator.universal_mutator import UniversalMutator

from eth_vertigo.incremental import IncrementalRecorder, IncrementalMutationStore, IncrementalSuggester

from tqdm import tqdm


@click.group(help="Mutation testing framework for smart contracts")
def cli():
    pass


@cli.command(help="Performs a core test campaign")
@click.option('--output', help="Output core test results to file", nargs=1, type=str)
@click.option('--network', help="Network names that vertigo can use", multiple=True)
@click.option('--ganache-path', help="Path to ganache binary", type=str, default="ganache-cli")
@click.option('--ganache-network', help="Dynamic networks that vertigo can use eg. (develop, 8485)",
              multiple=True, type=(str, int))
@click.option('--ganache-network-options', help="Options to pass to dynamic ganache networks", type=str)
@click.option('--rules', help="Universal Mutator style rules to use in mutation testing", multiple=True)
@click.option('--truffle-location', help="Location of truffle cli", nargs=1, type=str, default="truffle")
@click.option('--sample-ratio', help="If this option is set. Vertigo will apply the sample filter with the given ratio", nargs=1, type=float)
@click.option('--exclude', help="Vertigo won't mutate files in these directories", multiple=True)
@click.option('--incremental', help="File where incremental mutation state is stored",
              type=str)
def run(
        output,
        network,
        ganache_path,
        ganache_network,
        ganache_network_options,
        rules,
        truffle_location,
        sample_ratio,
        exclude,
        incremental
):
    """ Run command """
    click.echo("[*] Starting mutation testing")

    # Setup global parameters
    truffle = Truffle(truffle_location)

    working_directory = getcwd()
    project_type = _directory_type(working_directory)
    filters = []
    if exclude:
        filters.append(ExcludeFilter(exclude))

    if network and ganache_network:
        click.echo("[-] Can't use dynamic networks and regular networks simultaniously")
        exit(1)

    test_suggesters = []
    if incremental:
        incremental_store_file = Path(incremental)
        if not incremental_store_file.exists():
            pass
        elif not incremental_store_file.is_file() :
            click.echo(f"Incremental file {incremental} is not a file")
            exit(0)
        else:
            store = IncrementalMutationStore.from_file(incremental_store_file)
            test_suggesters.append(IncrementalSuggester(store))

    if project_type == "truffle":
        click.echo("[*] Starting analysis on truffle project")
        project_path = Path(working_directory)

        if not (project_path / "contracts").exists():
            click.echo("[-] No contracts directory in truffle project")
            return
        elif not (project_path / "test").exists():
            click.echo("[-] No test directory found in truffle project")
            return

        if sample_ratio:
            filters.append(SampleFilter(sample_ratio))

        mutators = []
        if rules:
            um = UniversalMutator()
            for rule_file in rules:
                um.load_rule(Path(rule_file))
            mutators.append(um)

        if network:
            network_pool = StaticNetworkPool(network)
        elif ganache_network:
            network_pool = DynamicNetworkPool(
                ganache_network,
                lambda port: Ganache(port, ganache_network_options.split(' ') if ganache_network_options else [],
                                     ganache_path)
            )
        else:
            click.echo("[-] Vertigo needs at least one network to run analyses on")
            return

        try:
            campaign = TruffleCampaign(
                project_directory=project_path,
                truffle_compiler=truffle,
                mutators=mutators,
                truffle_runner_factory=TruffleRunnerFactory(truffle),
                network_pool=network_pool,
                filters=filters,
                suggesters=test_suggesters,
            )
        except:
            click.echo("[-] Encountered an error while setting up the core campaign")
            for node in network_pool.claimed_networks.keys():
                click.echo(f"[+] Cleaning up network: {node}")
                network_pool.yield_network(node)
            raise
    else:
        click.echo("[*] Could not find supported project directory in {}".format(working_directory))
        return

    click.echo("[*] Initializing campaign run ")

    try:
        campaign.setup()
        click.echo("[*] Checking validity of project")
        if not campaign.valid():
            click.echo("[-] We couldn't get valid results by running the truffle tests.\n Aborting")
            return

        click.echo("[+] The project is valid")
        click.echo("[*] Storing compilation results")
        campaign.store_compilation_results()
        click.echo("[*] Running analysis on {} mutants".format(len(campaign.mutations)))
        with tqdm(total=len(campaign.mutations), unit="mutant") as pbar:
            report = campaign.run(lambda: pbar.update(1) and pbar.refresh(), threads=max(network_pool.size, 1))
        pbar.close()

    except TestRunException as e:
        click.echo("[-] Encountered an error while running the framework's test command:")
        click.echo(e)
        return
    except Exception as e:
        click.echo("[-] Encountered an error while running the core campaign")
        click.echo(e)
        raise

    click.echo("[*] Done with campaign run")
    click.echo("[+] Report:")
    click.echo(report.render())

    click.echo("[+] Survivors")
    for mutation in report.mutations:
        if mutation.result == MutationResult.LIVED:
            click.echo(str(mutation))

    if output:
        output_path = Path(output)
        if not output_path.exists() or click.confirm("[*] There already exists something at {}. Overwrite ".format(str(output_path))):
            click.echo("Result of core run can be found at: {}".format(output))
            output_path.write_text(report.render(with_mutations=True), "utf-8")

    if incremental:
        incremental_store_file = Path(incremental)
        if not incremental_store_file.exists() or \
            click.confirm(f"[*] There already exists an incremental at {incremental_store_file.name}. Overwrite "):
            new_incremental_store = IncrementalRecorder().record(report.mutations)
            new_incremental_store.to_file(incremental_store_file)

    click.echo("[*] Done! ")


def _directory_type(working_directory: str):
    """ Determines the current framework in the current directory """
    # jk, we only deal with truffle for now ^^'
    return "truffle"
