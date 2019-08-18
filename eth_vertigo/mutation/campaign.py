from typing import Callable, List
from eth_vertigo.mutation.filter import MutationFilter

from eth_vertigo.mutation import Mutation, MutationResult
from jinja2 import PackageLoader, Environment
from concurrent.futures import ThreadPoolExecutor

environment = Environment(
        loader=PackageLoader("eth_vertigo.mutation"), trim_blocks=True
    )


class CampaignReport:
    def __init__(self, mutations):
        """
        Constructs a campaign report object
        :param mutations: Mutations for this campaign
        """
        self.mutations = mutations

    @property
    def mutation_count(self):
        """ Amount of mutations in this report """
        return len(self.mutations)

    @property
    def nr_killed(self):
        """ Amount of killed mutations in this report"""
        return len([e for e in self.mutations if e.result == MutationResult.KILLED])

    @property
    def nr_alive(self):
        """ Amount of alive mutations in this report"""
        return len([e for e in self.mutations if e.result == MutationResult.LIVED])

    def render(self, with_mutations=False):
        template = environment.get_template("report_template.jinja2")
        return template.render(
            nr_mutations=len(self.mutations),
            nr_killed=self.nr_killed,
            mutations=self.mutations,
            with_mutations=with_mutations
        )


class Campaign:
    """
    A mutation campaign class orchestrates and manages a mutation testing run
    """

    def __init__(self, filters: List[MutationFilter] = None):
        self.sources = []
        self.project_directory = None
        self.mutations = []
        self.is_set_up = False
        self.filters = filters or []

    def setup(self):
        """ Sets up the campaign for execution"""
        raise NotImplementedError

    def run(self, progress_callback: Callable, threads=1):
        """ Starts a mutation testing campaign"""
        if not self.is_set_up:
            raise ValueError("This campaign is not setup yet")

        report = CampaignReport(self.mutations)
        with ThreadPoolExecutor(max_workers=threads) as e:
            for mutation in self.mutations:
                e.submit(self.test_mutation, mutation, progress_callback)
            e.shutdown()
        return report

    def test_mutation(self, mutation: Mutation, done_callback: Callable):
        """ Run the test suite using a mutation and check for murders """
        raise NotImplementedError

    def valid(self):
        """ Checks whether the current project is valid """
        raise NotImplementedError

