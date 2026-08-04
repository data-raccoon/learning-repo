from pathlib import Path
import tempfile
import time
import unittest

from agent_orchestrator.contracts import ContractError, Job
from agent_orchestrator.locking import LockTimeout, TargetLock
from agent_orchestrator.scheduler import _assert_acyclic, run_graph


class StubRunner:
    def run(self, job):
        return {"job": job.id, "status": "failed" if job.id == "failure" else "passed"}


class SlowRunner:
    def run(self, job):
        time.sleep(0.15)
        return {"job": job.id, "status": "passed"}


class SchedulerLockTests(unittest.TestCase):
    def test_cycle_is_rejected(self):
        first = Job(1, "first", "x", "target", "read", "low", "low", "inference", dependencies=("second",))
        second = Job(1, "second", "x", "target", "read", "low", "low", "inference", dependencies=("first",))
        with self.assertRaises(ContractError):
            _assert_acyclic([first, second])

    def test_failed_dependency_skips_downstream(self):
        failure = Job(1, "failure", "x", "target", "read", "low", "low", "inference")
        downstream = Job(1, "downstream", "x", "target", "read", "low", "low", "inference", dependencies=("failure",))
        result = run_graph(StubRunner(), [failure, downstream], 2)
        self.assertEqual(result["jobs"][1]["status"], "skipped")

    def test_independent_jobs_execute_in_parallel(self):
        first = Job(1, "first", "x", "target", "read", "low", "low", "inference")
        second = Job(1, "second", "x", "target", "read", "low", "low", "inference")
        started = time.monotonic()
        result = run_graph(SlowRunner(), [first, second], 2)
        self.assertEqual(result["status"], "passed")
        self.assertLess(time.monotonic() - started, 0.27)

    def test_target_lock_blocks_overlap(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / "target"
            target.mkdir()
            with TargetLock(root / "locks", target):
                with self.assertRaises(LockTimeout):
                    with TargetLock(root / "locks", target, timeout=0.1):
                        pass

    def test_parent_write_blocks_child_write(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            parent = root / "target"
            child = parent / "child"
            child.mkdir(parents=True)
            with TargetLock(root / "locks", parent):
                with self.assertRaises(LockTimeout):
                    with TargetLock(root / "locks", child, timeout=0.1):
                        pass

    def test_overlapping_reads_are_allowed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / "target"
            target.mkdir()
            with TargetLock(root / "locks", target, mode="read"):
                with TargetLock(root / "locks", target, timeout=0.1, mode="read"):
                    pass


if __name__ == "__main__":
    unittest.main()
