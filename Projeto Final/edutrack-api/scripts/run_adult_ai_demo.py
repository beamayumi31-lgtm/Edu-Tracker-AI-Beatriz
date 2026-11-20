"""Private, adult-only, loopback demo. No real AI calls unless explicitly enabled."""
import argparse
import getpass
import importlib.util
import os
import secrets
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from edutrack.config import Settings  # noqa: E402


class DemoSettings(Settings):
    @classmethod
    def settings_customise_sources(cls, settings_cls, init_settings, env_settings,
                                   dotenv_settings, file_secret_settings):
        # Never inherit production credentials, .env, database URLs or flags.
        return (init_settings,)


def build_demo(database_path: Path, *, confirmed_private_adults=False,
               api_key=None, model="gemini-3.5-flash-lite"):
    if not confirmed_private_adults:
        raise ValueError("Confirm a private demonstration with adult participants only.")
    if api_key and any(os.environ.get(name) for name in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy", "SSL_CERT_FILE", "SSL_CERT_DIR")):
        raise ValueError("Live demo requires a clean process without inherited proxy/certificate overrides.")
    spec = importlib.util.spec_from_file_location("_adult_demo_preview", ROOT / "tests/preview_app.py")
    preview = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(preview)
    # Override only this freshly loaded fixture module, not the real app or environment.
    preview.os = SimpleNamespace(environ={"EDUTRACK_QA_PREVIEW": "1"})
    def settings(**kwargs):
        kwargs.update(jwt_secret=secrets.token_urlsafe(48), ai_audience="adults_only",
                      ai_provider="gemini", gemini_enabled=bool(api_key),
                      GEMINI_API_KEY=api_key, GEMINI_MODEL=model,
                      gemini_paid_service=False, classroom_enabled=False,
                      classroom_full_import_enabled=False,
                      frontend_url="http://127.0.0.1:3014",
                      cors_origins=["http://127.0.0.1:3014"])
        return DemoSettings(**kwargs)
    preview.Settings = settings
    return preview.build_preview(database_path)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm-private-adults", action="store_true",
                        help="Confirm this separate demo is private and only for adults.")
    parser.add_argument("--enable-live-gemini", action="store_true",
                        help="Requires prior authorization for credential use and provider calls; prompts privately.")
    parser.add_argument("--model", default="gemini-3.5-flash-lite")
    args = parser.parse_args(argv)
    if not args.confirm_private_adults:
        parser.error("--confirm-private-adults is required; public EduTrack remains unchanged.")
    key = None
    if args.enable_live_gemini:
        if not sys.stdin.isatty():
            parser.error("Live mode requires an interactive private terminal, never piped credentials.")
        key = getpass.getpass("Authorized Gemini key (not saved): ").strip()
        if not key:
            parser.error("No key supplied; nothing started.")
    import uvicorn
    with TemporaryDirectory(prefix="edutrack-adult-demo-") as directory:
        app = build_demo(Path(directory) / "demo.db", confirmed_private_adults=True,
                         api_key=key, model=args.model)
        key = None
        print("Private adult demo: http://127.0.0.1:8014; fictitious data; no Classroom.")
        print("Live Gemini enabled." if app.state.settings.ai_configured else "No-key mode: chat disabled; local planner available.")
        uvicorn.run(app, host="127.0.0.1", port=8014, access_log=False, proxy_headers=False)


if __name__ == "__main__":
    main()
