import unittest

from envdrift.core import compare_envs, parse_env_lines


class ParseEnvTests(unittest.TestCase):
    def test_parses_comments_exports_and_quotes(self):
        parsed = parse_env_lines(
            [
                "# comment",
                "export API_URL=https://example.com",
                'TOKEN="secret"',
                "PORT='8080'",
            ]
        )

        self.assertEqual(parsed.values["API_URL"], "https://example.com")
        self.assertEqual(parsed.values["TOKEN"], "secret")
        self.assertEqual(parsed.values["PORT"], "8080")
        self.assertEqual(parsed.invalid_lines, [])

    def test_detects_duplicate_and_invalid_lines(self):
        parsed = parse_env_lines(
            [
                "API_KEY=one",
                "API_KEY=two",
                "not a valid assignment",
                "9INVALID=value",
            ]
        )

        self.assertEqual(parsed.duplicates, ["API_KEY"])
        self.assertEqual(parsed.invalid_lines, [3, 4])


class CompareEnvTests(unittest.TestCase):
    def test_detects_drift_without_exposing_values(self):
        reference = parse_env_lines(
            [
                "DATABASE_URL=required",
                "REDIS_URL=required",
                "LOG_LEVEL=info",
            ]
        )
        target = parse_env_lines(
            [
                "DATABASE_URL=postgres://super-secret",
                "REDIS_URL=",
                "EXTRA_KEY=secret-value",
            ]
        )

        report = compare_envs(reference, target)

        self.assertEqual(report.missing, ["LOG_LEVEL"])
        self.assertEqual(report.empty_required, ["REDIS_URL"])
        self.assertEqual(report.unexpected, ["EXTRA_KEY"])
        self.assertFalse(report.ok)
        self.assertNotIn("super-secret", str(report.to_dict()))
        self.assertNotIn("secret-value", str(report.to_dict()))

    def test_unexpected_keys_can_be_allowed(self):
        reference = parse_env_lines(["A=required"])
        target = parse_env_lines(["A=value", "B=value"])

        report = compare_envs(reference, target, allow_unexpected=True)

        self.assertEqual(report.unexpected, [])
        self.assertTrue(report.ok)


if __name__ == "__main__":
    unittest.main()
