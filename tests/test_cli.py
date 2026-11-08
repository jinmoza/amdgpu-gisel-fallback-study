import unittest

from gisel_study.cli import build_parser


class CliTest(unittest.TestCase):
    def test_collect_defaults_to_both_corpora(self):
        args = build_parser().parse_args(["collect", "--manifest", "experiment.yaml"])

        self.assertEqual(args.command, "collect")
        self.assertEqual(args.corpus, "all")
        self.assertIsNone(args.limit)

    def test_analyze_and_reduce_accept_run_directory(self):
        analyze = build_parser().parse_args(["analyze", "--run", "results/a"])
        reduce = build_parser().parse_args(["reduce", "--run", "results/a"])

        self.assertEqual(analyze.run, "results/a")
        self.assertEqual(reduce.timeout, 900)

    def test_publish_results_accepts_run_output_and_workspace(self):
        args = build_parser().parse_args(
            [
                "publish-results",
                "--run",
                "results/a",
                "--output",
                "published-results/a",
                "--workspace",
                ".",
            ]
        )

        self.assertEqual(args.command, "publish-results")
        self.assertEqual(args.output, "published-results/a")


if __name__ == "__main__":
    unittest.main()
