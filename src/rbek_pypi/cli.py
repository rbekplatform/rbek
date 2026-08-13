from __future__ import annotations

import hashlib
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import urllib.request

EXPECTED_RUNTIME_VERSION = "0.2.0"
EXPECTED_RUNTIME_VERSION_OUTPUT = f"RBEK {EXPECTED_RUNTIME_VERSION}"

INSTALLER_URL = "https://releases.rbekplatform.com/cli/stable/install.sh"
INSTALLER_SHA256 = "0a3fabcad4c114c133b96cb71e1406d25279c2c05fa3b37f95a8e446a10b7c86"

DEMO_URL = (
    "https://raw.githubusercontent.com/"
    "rbekplatform/rbek/main/examples/real-governed-agent/demo.sh"
)
DEMO_SHA256 = "17d299b02a38aec3f722ead47153a82e0f28be2c208d6a099590984e978df2d6"

RUNTIME_COMMAND = "rbek-cli"


class RbekBootstrapError(RuntimeError):
    pass


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _download_verified(url: str, expected_sha256: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "rbek-pypi-bootstrap/0.2.0"},
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read()

    actual = _sha256(data)

    if actual != expected_sha256:
        raise RbekBootstrapError(
            "Downloaded RBEK artifact failed SHA256 validation: "
            f"expected={expected_sha256} actual={actual}"
        )

    return data


def _runtime_path() -> str | None:
    return shutil.which(RUNTIME_COMMAND)


def _runtime_version(runtime: str) -> str:
    completed = subprocess.run(
        [runtime, "--version"],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _validate_runtime(runtime: str) -> None:
    actual = _runtime_version(runtime)

    if actual != EXPECTED_RUNTIME_VERSION_OUTPUT:
        raise RbekBootstrapError(
            "RBEK runtime version mismatch: "
            f"expected={EXPECTED_RUNTIME_VERSION_OUTPUT!r} "
            f"actual={actual!r}"
        )


def _install_runtime() -> str:
    installer = _download_verified(
        INSTALLER_URL,
        INSTALLER_SHA256,
    )

    with tempfile.TemporaryDirectory(prefix="rbek-pypi-install-") as tmp:
        path = pathlib.Path(tmp) / "install.sh"
        path.write_bytes(installer)
        path.chmod(0o700)

        subprocess.run(
            ["bash", str(path)],
            check=True,
            stdout=sys.stderr,
            stderr=sys.stderr,
        )

    runtime = _runtime_path()

    if runtime is None:
        raise RbekBootstrapError(
            "RBEK installer completed but rbek-cli was not found in PATH."
        )

    _validate_runtime(runtime)
    return runtime


def ensure_runtime() -> str:
    runtime = _runtime_path()

    if runtime is None:
        runtime = _install_runtime()
    else:
        _validate_runtime(runtime)

    return runtime


def run_demo() -> int:
    demo = _download_verified(
        DEMO_URL,
        DEMO_SHA256,
    )

    with tempfile.TemporaryDirectory(prefix="rbek-pypi-demo-") as tmp:
        path = pathlib.Path(tmp) / "demo.sh"
        path.write_bytes(demo)
        path.chmod(0o700)

        completed = subprocess.run(
            ["bash", str(path)],
            check=False,
        )

    return int(completed.returncode)


def _delegate(runtime: str, args: list[str]) -> int:
    completed = subprocess.run(
        [runtime, *args],
        check=False,
    )
    return int(completed.returncode)


def main() -> None:
    args = sys.argv[1:]

    try:
        if args == ["demo"]:
            ensure_runtime()
            raise SystemExit(run_demo())

        runtime = ensure_runtime()
        raise SystemExit(_delegate(runtime, args))

    except KeyboardInterrupt:
        raise SystemExit(130)

    except RbekBootstrapError as exc:
        print(f"RBEK bootstrap error: {exc}", file=sys.stderr)
        raise SystemExit(2)

    except (OSError, subprocess.SubprocessError) as exc:
        print(f"RBEK bootstrap failure: {exc}", file=sys.stderr)
        raise SystemExit(3)
