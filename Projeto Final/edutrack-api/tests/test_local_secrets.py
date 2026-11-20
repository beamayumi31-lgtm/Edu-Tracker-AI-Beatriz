from edutrack.run import load_local_secrets


def test_load_local_secrets_outside_repository(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.delenv("SENDGRID_API_KEY", raising=False)
    monkeypatch.setenv("EDUTRACK_EMAIL_FROM_NAME", "Prioridade do operador")
    folder = tmp_path / "EduTrack"
    folder.mkdir()
    (folder / "backend.env").write_text(
        "SENDGRID_API_KEY=chave-falsa-apenas-teste\nEDUTRACK_EMAIL_FROM_NAME=Arquivo\n",
        encoding="utf-8",
    )
    load_local_secrets()
    import os

    assert os.environ["SENDGRID_API_KEY"] == "chave-falsa-apenas-teste"
    assert os.environ["EDUTRACK_EMAIL_FROM_NAME"] == "Prioridade do operador"
    monkeypatch.delenv("SENDGRID_API_KEY")


def test_missing_local_secrets_is_optional(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    load_local_secrets()
