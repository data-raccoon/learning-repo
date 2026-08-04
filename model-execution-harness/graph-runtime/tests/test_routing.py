import tempfile
from dataclasses import replace
from pathlib import Path
import unittest

from agent_orchestrator.contracts import Job
from agent_orchestrator.registry import Registry
from agent_orchestrator.routing import RoutingError, route_job
from tests.helpers import write_registry


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.registry = Registry(write_registry(Path(self.temp.name)))

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def job(importance="normal", capability="summarization"):
        return Job(1, "route", "route", "target", "read", importance, "low", "inference", (capability,))

    def test_normal_job_uses_weakest_profile_that_meets_threshold(self):
        route = route_job(self.registry, self.job())
        self.assertEqual(route["selected_profile"], "weak-read")
        self.assertEqual(route["billing"], "metered-api")
        self.assertEqual(route["plan"], "test")

    def test_architecture_uses_strongest_profile(self):
        self.assertEqual(route_job(self.registry, self.job("critical", "architecture"))["selected_profile"], "strong-read")

    def test_subscription_ignores_public_api_prices_as_tiebreaker(self):
        self.registry.models["weak"] = replace(
            self.registry.models["weak"], quality=0.5, input_cost_per_million=10.0, output_cost_per_million=20.0,
        )
        self.registry.models["strong"] = replace(
            self.registry.models["strong"], quality=0.5, input_cost_per_million=0.1, output_cost_per_million=0.2,
        )
        self.assertEqual(route_job(self.registry, self.job())["selected_profile"], "strong-read")
        provider = self.registry.providers["test-provider"]
        self.registry.providers["test-provider"] = replace(provider, billing="included-subscription", plan="pro")
        self.assertEqual(route_job(self.registry, self.job())["selected_profile"], "weak-read")

    def test_only_explicit_evaluation_can_route_candidate(self):
        self.registry.profiles["weak-read"] = replace(self.registry.profiles["weak-read"], status="candidate", success_probability=0.0)
        self.registry.harnesses["fake-read"] = replace(self.registry.harnesses["fake-read"], status="candidate")
        job = replace(self.job("low"), model_profile="weak-read")
        with self.assertRaises(RoutingError):
            route_job(self.registry, job)
        self.assertEqual(route_job(self.registry, job, allow_candidate=True)["selected_profile"], "weak-read")


if __name__ == "__main__":
    unittest.main()
