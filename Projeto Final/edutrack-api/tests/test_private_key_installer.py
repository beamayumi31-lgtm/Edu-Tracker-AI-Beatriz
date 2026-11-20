import json
import os
import stat
import subprocess
import sys
from types import SimpleNamespace

import pytest

from scripts.install_gemini_key_private import HOST, REMOTE, install_key, main


def test_dry_run_never_prompts_or_connects(monkeypatch, capsys):
    def forbidden(*args, **kwargs):
        raise AssertionError("No connection or key prompt permitted")
    monkeypatch.setattr("scripts.install_gemini_key_private.getpass.getpass", forbidden)
    main([])
    assert "DRY RUN" in capsys.readouterr().out


@pytest.mark.parametrize("key", ["synthetic-not-real-key-123456789", "AQ.synthetic_not_real.auth-key-123456789"])
def test_key_is_stdin_only_and_host_verification_enforced(key):
    def run(command, **kwargs):
        assert HOST in command and "StrictHostKeyChecking=yes" in command
        assert "-T" in command and key not in str(command)
        assert key.encode() in kwargs["input"]
        assert kwargs["capture_output"] and kwargs["timeout"] == 30
        return SimpleNamespace(returncode=0, stdout=b"KEY_INSTALLED_NO_RESTART\n")
    assert "no restart" in install_key(key, run=run)
    compile(REMOTE, "remote-installer", "exec")
    assert "docker" not in REMOTE and "EDUTRACK_GEMINI_ENABLED" in REMOTE


def test_errors_never_echo_remote_output_or_key():
    key = "synthetic-not-real-key-123456789"
    def run(*args, **kwargs):
        return SimpleNamespace(returncode=1, stdout=key.encode(), stderr=key.encode())
    with pytest.raises(RuntimeError) as error:
        install_key(key, run=run)
    assert key not in str(error.value)


def test_key_rejects_newline_without_connection():
    with pytest.raises(ValueError):
        install_key("synthetic-key\nEDUTRACK_GEMINI_ENABLED=true")


def test_noninteractive_install_does_not_prompt(monkeypatch):
    monkeypatch.setattr("scripts.install_gemini_key_private.sys.stdin", SimpleNamespace(isatty=lambda: False))
    with pytest.raises(SystemExit):
        main(["--install-authorized"])

# Execute the actual remote payload only against a disposable POSIX fixture.


@pytest.fixture
def remote_fixture(tmp_path):
    if os.name != "posix":
        pytest.skip("Real chmod/chown semantics require POSIX; run these tests on Linux")
    path = tmp_path / "backend.env"
    path.write_bytes(b"KEEP=unchanged\nEDUTRACK_GEMINI_ENABLED=false\nGEMINI_API_KEY=old-synthetic-key-12345\nTAIL=preserved\n")
    path.chmod(0o600)
    payload = REMOTE.replace("'/opt/edutrack/secrets/backend.env'", repr(str(path)))
    assert payload != REMOTE
    def run(key="synthetic-not-real-key-123456789"):
        return subprocess.run([sys.executable, "-c", payload], input=json.dumps({"key": key}).encode(), capture_output=True, timeout=5, check=False)
    return path, run


def test_remote_preserves_flags_other_bytes_owner_and_permissions(remote_fixture):
    path, run = remote_fixture
    before = path.stat()
    result = run()
    assert result.returncode == 0
    assert result.stdout == b"KEY_INSTALLED_NO_RESTART\n"
    assert not result.stderr
    assert path.read_bytes() == b"KEEP=unchanged\nEDUTRACK_GEMINI_ENABLED=false\nGEMINI_API_KEY=synthetic-not-real-key-123456789\nTAIL=preserved\n"
    after = path.stat()
    assert stat.S_IMODE(after.st_mode) == 0o600
    assert (before.st_uid, before.st_gid) == (after.st_uid, after.st_gid)
    assert not list(path.parent.glob(".gemini-key-*"))


@pytest.mark.parametrize("flag", ["", "EDUTRACK_GEMINI_ENABLED=true\n", "EDUTRACK_GEMINI_ENABLED=0\n", "EDUTRACK_GEMINI_ENABLED=false\nEDUTRACK_GEMINI_ENABLED=false\n", "EDUTRACK_GEMINI_ENABLED=false\nexport EDUTRACK_GEMINI_ENABLED=true\n"])
def test_remote_rejects_missing_enabled_or_duplicate_flags(remote_fixture, flag):
    path, run = remote_fixture
    path.write_text(flag + "KEEP=unchanged\n")
    original = path.read_bytes()
    result = run()
    assert result.returncode == 1
    assert result.stdout == b"INSTALL_FAILED_NO_DETAILS\n"
    assert path.read_bytes() == original


@pytest.mark.parametrize("extra", ["GEMINI_API_KEY=duplicate\n", " GEMINI_API_KEY=ambiguous\n", "export GEMINI_API_KEY=ambiguous\n", "GEMINI_API_KEY =ambiguous\n"])
def test_remote_rejects_duplicate_or_ambiguous_keys(remote_fixture, extra):
    path, run = remote_fixture
    path.write_bytes(path.read_bytes() + extra.encode())
    original = path.read_bytes()
    assert run().returncode == 1
    assert path.read_bytes() == original


@pytest.mark.parametrize("key", ["short", "x" * 257, "bad\nkey", None, 123])
def test_remote_rejects_invalid_key_without_write(remote_fixture, key):
    path, run = remote_fixture
    original = path.read_bytes()
    result = run(key)
    assert result.returncode == 1
    assert result.stdout == b"INSTALL_FAILED_NO_DETAILS\n"
    assert not result.stderr
    assert path.read_bytes() == original


def test_remote_rejects_unsafe_permissions(remote_fixture):
    path, run = remote_fixture
    path.chmod(0o644)
    original = path.read_bytes()
    assert run().returncode == 1
    assert path.read_bytes() == original
