from __future__ import annotations

import hashlib
import pathlib
import subprocess
import sys
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

from rbek_pypi import cli


class BootstrapTests(unittest.TestCase):
    def test_version_identity(self) -> None:
        self.assertEqual(cli.EXPECTED_RUNTIME_VERSION, "0.2.0")
        self.assertEqual(
            cli.EXPECTED_RUNTIME_VERSION_OUTPUT,
            "RBEK 0.2.0",
        )

    def test_existing_runtime_is_validated(self) -> None:
        with (
            mock.patch.object(
                cli,
                "_runtime_path",
                return_value="/fake/rbek-cli",
            ),
            mock.patch.object(
                cli,
                "_validate_runtime",
            ) as validate,
        ):
            result = cli.ensure_runtime()

        self.assertEqual(result, "/fake/rbek-cli")
        validate.assert_called_once_with("/fake/rbek-cli")

    def test_installer_output_is_routed_to_stderr(self) -> None:
        with (
            mock.patch.object(cli, "_download_verified", return_value=b"#!/bin/sh\nexit 0\n"),
            mock.patch.object(cli, "_runtime_path", return_value="/installed/rbek-cli"),
            mock.patch.object(cli, "_validate_runtime") as validate,
            mock.patch.object(cli.subprocess, "run") as run,
        ):
            result = cli._install_runtime()

        self.assertEqual(result, "/installed/rbek-cli")
        validate.assert_called_once_with("/installed/rbek-cli")
        args, kwargs = run.call_args
        self.assertEqual(args[0][0], "bash")
        self.assertTrue(kwargs["check"])
        self.assertIs(kwargs["stdout"], sys.stderr)
        self.assertIs(kwargs["stderr"], sys.stderr)

    def test_missing_runtime_uses_installer(self) -> None:
        with (
            mock.patch.object(
                cli,
                "_runtime_path",
                return_value=None,
            ),
            mock.patch.object(
                cli,
                "_install_runtime",
                return_value="/installed/rbek-cli",
            ) as install,
        ):
            result = cli.ensure_runtime()

        self.assertEqual(result, "/installed/rbek-cli")
        install.assert_called_once_with()

    def test_runtime_version_mismatch_fails_closed(self) -> None:
        with mock.patch.object(
            cli,
            "_runtime_version",
            return_value="RBEK 999.0.0",
        ):
            with self.assertRaises(cli.RbekBootstrapError):
                cli._validate_runtime("/fake/rbek-cli")

    def test_sha256_helper(self) -> None:
        data = b"rbek"
        self.assertEqual(
            cli._sha256(data),
            hashlib.sha256(data).hexdigest(),
        )

    def test_delegate_preserves_arguments(self) -> None:
        completed = subprocess.CompletedProcess(
            args=["rbek-cli", "run", "project"],
            returncode=7,
        )

        with mock.patch.object(
            cli.subprocess,
            "run",
            return_value=completed,
        ) as run:
            rc = cli._delegate(
                "/runtime/rbek-cli",
                ["run", "project"],
            )

        self.assertEqual(rc, 7)
        run.assert_called_once_with(
            ["/runtime/rbek-cli", "run", "project"],
            check=False,
        )


if __name__ == "__main__":
    unittest.main()
