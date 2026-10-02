import unittest
from concurrency_experiment import simulate


class SimulationChecks(unittest.TestCase):
    def test_all_jobs_finish_even_with_short_batch(self):
        result = simulate(32, jobs=3)
        self.assertEqual(result['completed'], 3)
        self.assertEqual(result['simulated_seconds'], .1)

    def test_no_contention_control_scales_with_slots(self):
        self.assertEqual(simulate(4, jobs=100, penalty_ms=0)['useful_jobs_per_second'], 40)
        self.assertEqual(simulate(8, jobs=104, penalty_ms=0)['useful_jobs_per_second'], 80)

    def test_limit_matches_same_active_worker_count(self):
        limited, baseline = simulate(32, limit=8), simulate(8)
        for key in ('completed', 'simulated_seconds', 'useful_jobs_per_second', 'p95_service_ms'):
            self.assertEqual(limited[key], baseline[key])

    def test_invalid_inputs_rejected(self):
        for kwargs in ({'workers': 0}, {'workers': 1, 'jobs': 0}, {'workers': 1, 'penalty_ms': -1}):
            with self.assertRaises(ValueError):
                simulate(**kwargs)


if __name__ == '__main__':
    unittest.main()
