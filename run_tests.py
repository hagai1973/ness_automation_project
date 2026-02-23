"""
Test Runner with Allure Reporting + Xray Cloud Integration
==========================================================
Usage:
    python run_tests.py                         # Run ALL tests with Allure report
    python run_tests.py --test login            # Run only login tests
    python run_tests.py --test shopping         # Run only shopping tests
    python run_tests.py --test login_and_shop   # Run only login_and_shop tests
    python run_tests.py --marker smoke          # Run tests by marker
    python run_tests.py --no-report             # Run tests without Allure report
    python run_tests.py --headed                # Run with browser visible (default)
    python run_tests.py --headless              # Run in headless mode

Xray Cloud Reporting:
    python run_tests.py --xray                          # Run + report results to Xray Cloud
    python run_tests.py --test login --xray             # Login tests + report to Xray
    python run_tests.py --xray --xray-execution SP2-300 # Report into existing Test Execution
    python run_tests.py --xray --xray-plan SP2-200      # Link results to a Test Plan
    python run_tests.py --marker smoke --xray           # Smoke tests + report to Xray

Parallel Execution (pytest-xdist):
    python run_tests.py --workers 2             # Run with 2 parallel browsers
    python run_tests.py --workers 3             # Run with 3 parallel browsers
    python run_tests.py -w auto                 # Auto-detect workers (1 per CPU core)
    python run_tests.py -t login -w 2           # Login tests with 2 workers
    python run_tests.py -t login -w 3 --no-report  # Parallel, no report

    Each worker launches its own Chromium browser instance.
    More workers = faster execution, but more memory usage.
    Recommended: start with 2-3 workers.
"""

import subprocess
import sys
import os
import shutil
import argparse
import time
import logging
import webbrowser
from pathlib import Path


# === Logging Setup ============================================================
#
# Two handlers:
#   StreamHandler → terminal  (clean, no timestamp — looks identical to print)
#   FileHandler   → logs/runner.log  (full timestamp + level for CI / audit)
#
# Use logger.debug()   for internal details (visible in file only)
#     logger.info()    for normal progress messages
#     logger.warning() for non-fatal issues (⚠️)
#     logger.error()   for failures (❌)

LOG_DIR  = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "runner.log"

_terminal_handler = logging.StreamHandler(sys.stdout)
_terminal_handler.setLevel(logging.INFO)
_terminal_handler.setFormatter(logging.Formatter("%(message)s"))

_file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
_file_handler.setLevel(logging.DEBUG)
_file_handler.setFormatter(
    logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s",
                      datefmt="%Y-%m-%d %H:%M:%S")
)

logging.basicConfig(level=logging.DEBUG, handlers=[_terminal_handler, _file_handler])
logger = logging.getLogger("runner")


# === Configuration ============================================================
PROJECT_DIR    = Path(__file__).parent
ALLURE_RESULTS = PROJECT_DIR / "allure-results"
ALLURE_REPORT  = PROJECT_DIR / "allure-report"
TESTS_DIR      = PROJECT_DIR / "tests"
VENV_PYTEST    = PROJECT_DIR / "venv" / "Scripts" / "pytest.exe"

# Scoop paths for Allure + Java
SCOOP_SHIMS = Path.home() / "scoop" / "shims"
JAVA_BIN    = Path.home() / "scoop" / "apps" / "temurin-jdk" / "current" / "bin"
ALLURE_CMD  = SCOOP_SHIMS / "allure.cmd"


# ── Helpers ───────────────────────────────────────────────────────────────────

def setup_path():
    """Add Allure and Java to PATH."""
    paths_to_add = [str(SCOOP_SHIMS), str(JAVA_BIN)]
    current_path = os.environ.get("PATH", "")
    for p in paths_to_add:
        if p not in current_path:
            os.environ["PATH"] = p + os.pathsep + current_path
            current_path = os.environ["PATH"]
    logger.debug("PATH configured with Allure and Java shims")


def clean_previous_results():
    """Remove previous Allure results, report, and screenshots."""
    logger.info("\n🧹 Cleaning previous results...")
    for folder in [ALLURE_RESULTS, ALLURE_REPORT, PROJECT_DIR / "screenshots"]:
        if folder.exists():
            shutil.rmtree(folder)
            logger.info("   🗑️  Removed %s/", folder.name)
    logger.info("   ✅ Previous results cleaned")


def check_xray_credentials():
    """
    Verify Xray credentials are present in environment / .env before running.
    Also ensures XRAY_API_BASE_URL is set (required by pytest-jira-xray plugin).
    Returns True if all credentials are found, False otherwise.
    """
    try:
        from dotenv import load_dotenv
        env_file = PROJECT_DIR / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            logger.debug(".env file loaded successfully")
    except ImportError:
        logger.debug("python-dotenv not installed — using system env vars")

    client_id     = os.environ.get("XRAY_CLIENT_ID")
    client_secret = os.environ.get("XRAY_CLIENT_SECRET")

    if not client_id or not client_secret:
        logger.error("\n❌ Xray credentials not found!")
        logger.error("   Make sure your .env file contains:")
        logger.error("     XRAY_CLIENT_ID=your_client_id")
        logger.error("     XRAY_CLIENT_SECRET=your_client_secret")
        logger.error("   Get credentials from: Jira → Xray → App Settings → API Keys")
        return False

    # pytest-jira-xray requires XRAY_API_BASE_URL — default to Cloud URL
    if not os.environ.get("XRAY_API_BASE_URL"):
        os.environ["XRAY_API_BASE_URL"] = "https://xray.cloud.getxray.app"

    os.environ["XRAY_CLIENT_ID"]     = client_id
    os.environ["XRAY_CLIENT_SECRET"] = client_secret

    # Unset Basic Auth vars so the plugin cannot fall back to them
    os.environ.pop("XRAY_API_USER",     None)
    os.environ.pop("XRAY_API_PASSWORD", None)

    logger.info("\n🔑 Xray credentials loaded  (Client ID: %s...)", client_id[:8])
    logger.info("   🌐 Xray API URL: %s", os.environ["XRAY_API_BASE_URL"])
    return True


# ── Command builders ──────────────────────────────────────────────────────────

def build_pytest_command(args):
    """Build the base pytest command from CLI arguments."""
    cmd = [str(VENV_PYTEST)]

    if args.test:
        test_file = TESTS_DIR / f"test_{args.test}.py"
        if test_file.exists():
            cmd.append(str(test_file))
            logger.debug("Test file resolved: %s", test_file)
        else:
            logger.error("   ❌ Test file not found: %s", test_file)
            logger.info("   Available tests:")
            for f in sorted(TESTS_DIR.glob("test_*.py")):
                logger.info("      - %s", f.stem.replace("test_", ""))
            sys.exit(1)
    else:
        cmd.append(str(TESTS_DIR))
        logger.debug("Running all tests in: %s", TESTS_DIR)

    if args.marker:
        cmd.extend(["-m", args.marker])
        logger.debug("Marker filter applied: %s", args.marker)

    return cmd


def build_xray_args(args):
    """
    Build Xray-specific pytest arguments.
      --jira-xray           activates the pytest-jira-xray plugin
      --cloud               use Xray Cloud API format (PASSED vs PASS)
      --client-secret-auth  OAuth via Client ID + Secret (required for Cloud)
    """
    xray_args = ["--jira-xray", "--cloud", "--client-secret-auth"]

    if args.xray_execution:
        xray_args += ["--xray-execution-key", args.xray_execution]
        logger.info("   📋 Reporting into existing Test Execution: %s", args.xray_execution)
    else:
        logger.info("   📋 A new Test Execution will be created in Jira automatically")

    if args.xray_plan:
        xray_args += ["--xray-plan-key", args.xray_plan]
        logger.info("   🗂️  Linked to Test Plan: %s", args.xray_plan)

    return xray_args


def build_parallel_args(args):
    """Build pytest-xdist arguments for parallel execution."""
    if not args.workers:
        return []

    workers = args.workers
    if workers == "auto":
        logger.info("⚡ Parallel mode: auto (1 worker per CPU core)")
        return ["-n", "auto"]

    try:
        n = int(workers)
        if n < 1:
            logger.warning("⚠️  Workers must be >= 1 — running sequentially")
            return []
        if n == 1:
            return []
        logger.info("⚡ Parallel mode: %d workers", n)
        return ["-n", str(n)]
    except ValueError:
        logger.warning("⚠️  Invalid workers value '%s' — running sequentially", workers)
        return []


# ── Test runner ───────────────────────────────────────────────────────────────

def run_tests(cmd):
    """Execute pytest and return the exit code."""
    logger.info("\n🧪 Running tests...")
    logger.debug("   Command: %s", " ".join(cmd))
    logger.info("=" * 60)

    result = subprocess.run(cmd, cwd=str(PROJECT_DIR))
    return result.returncode


# ── Allure report ─────────────────────────────────────────────────────────────

def generate_report():
    """Generate Allure HTML report from results directory."""
    logger.info("\n📊 Generating Allure HTML report...")
    result = subprocess.run(
        [str(ALLURE_CMD), "generate", str(ALLURE_RESULTS),
         "--clean", "-o", str(ALLURE_REPORT)],
        cwd=str(PROJECT_DIR),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        logger.error("   ❌ Failed to generate report: %s", result.stderr)
        return False
    logger.info("   ✅ Report generated successfully")
    return True


def open_report():
    """Open the Allure HTML report in the default browser."""
    logger.info("\n🌐 Opening Allure report in browser...")
    time.sleep(2)
    try:
        subprocess.Popen(
            [str(ALLURE_CMD), "open", str(ALLURE_REPORT)],
            cwd=str(PROJECT_DIR),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        logger.info("   ✅ Report server started — check your browser!")
    except FileNotFoundError:
        logger.warning("   ⚠️  Allure CLI not found — opening HTML directly...")
        webbrowser.open(str(ALLURE_REPORT / "index.html"))


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="🧪 Test Runner with Allure Reporting + Xray Cloud"
    )
    parser.add_argument("--test",      "-t", help="Test module (e.g. login, shopping)")
    parser.add_argument("--marker",    "-m", help="Run by marker (e.g. smoke, regression)")
    parser.add_argument("--no-report",       action="store_true", help="Skip Allure report")
    parser.add_argument("--headless",        action="store_true", help="Run headless")
    parser.add_argument("--headed",          action="store_true", default=True,
                        help="Run headed (default)")
    parser.add_argument("--workers",   "-w", default=None,
                        help="Parallel workers (e.g. 2, 3, auto)")

    xray_group = parser.add_argument_group("Xray Cloud Reporting")
    xray_group.add_argument(
        "--xray",
        action="store_true",
        help="Report test results to Xray Cloud after the run",
    )
    xray_group.add_argument(
        "--xray-execution",
        metavar="ISSUE_KEY",
        help="Report into an existing Test Execution (e.g. SP2-300). "
             "If omitted, a new execution is created automatically.",
    )
    xray_group.add_argument(
        "--xray-plan",
        metavar="ISSUE_KEY",
        help="Link the execution to a Test Plan issue (e.g. SP2-200)",
    )

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("   🧪 Test Runner with Allure Reporting + Xray Cloud")
    logger.info("=" * 60)
    logger.debug("Log file: %s", LOG_FILE)

    # ── Setup ─────────────────────────────────────────────────────────────
    setup_path()

    if not args.no_report:
        clean_previous_results()

    # ── Validate Xray credentials early ───────────────────────────────────
    if args.xray:
        if not check_xray_credentials():
            sys.exit(1)

    # ── Build full pytest command ──────────────────────────────────────────
    cmd = build_pytest_command(args)

    if args.workers:
        parallel_args = build_parallel_args(args)
        if parallel_args:
            cmd.extend(parallel_args)

    if args.xray:
        logger.info("\n📡 Xray Cloud reporting: ENABLED")
        cmd.extend(build_xray_args(args))
    else:
        logger.info("\n📡 Xray Cloud reporting: OFF  (use --xray to enable)")

    # ── Run ───────────────────────────────────────────────────────────────
    exit_code = run_tests(cmd)

    # ── Summary ───────────────────────────────────────────────────────────
    logger.info("\n" + "=" * 60)
    if exit_code == 0:
        logger.info("   ✅ ALL TESTS PASSED!")
    else:
        logger.warning("   ⚠️  SOME TESTS FAILED")

    if args.xray:
        logger.info("   📡 Results reported to Xray Cloud → check Jira SP2 project")
        logger.info("      https://svhagai2026.atlassian.net/jira/software/c/projects/SP2/boards/2")
    logger.info("=" * 60)

    # ── Allure report ─────────────────────────────────────────────────────
    if not args.no_report:
        if generate_report():
            open_report()

    return exit_code


if __name__ == "__main__":
    sys.exit(main())