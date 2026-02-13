"""
Test Runner with Allure Reporting
=================================
Usage:
    python run_tests.py                     # Run ALL tests with Allure report
    python run_tests.py --test login        # Run only login tests
    python run_tests.py --test shopping     # Run only shopping tests
    python run_tests.py --test login_and_shop  # Run only login_and_shop tests
    python run_tests.py --marker smoke      # Run tests by marker
    python run_tests.py --no-report         # Run tests without Allure report
    python run_tests.py --headed            # Run with browser visible (default)
    python run_tests.py --headless          # Run in headless mode
"""

import subprocess
import sys
import os
import shutil
import argparse
import time
import webbrowser
from pathlib import Path


# === Configuration ===
PROJECT_DIR = Path(__file__).parent
ALLURE_RESULTS = PROJECT_DIR / "allure-results"
ALLURE_REPORT = PROJECT_DIR / "allure-report"
TESTS_DIR = PROJECT_DIR / "tests"
VENV_PYTHON = PROJECT_DIR / "venv" / "Scripts" / "python.exe"
VENV_PYTEST = PROJECT_DIR / "venv" / "Scripts" / "pytest.exe"

# Scoop paths for Allure + Java
SCOOP_SHIMS = Path.home() / "scoop" / "shims"
JAVA_BIN = Path.home() / "scoop" / "apps" / "temurin-jdk" / "current" / "bin"
ALLURE_CMD = SCOOP_SHIMS / "allure.cmd"


def setup_path():
    """Add Allure and Java to PATH"""
    paths_to_add = [str(SCOOP_SHIMS), str(JAVA_BIN)]
    current_path = os.environ.get("PATH", "")
    for p in paths_to_add:
        if p not in current_path:
            os.environ["PATH"] = p + os.pathsep + current_path
            current_path = os.environ["PATH"]


def clean_previous_results():
    """Remove previous Allure results and report"""
    print("\n🧹 Cleaning previous Allure results...")
    if ALLURE_RESULTS.exists():
        shutil.rmtree(ALLURE_RESULTS)
    if ALLURE_REPORT.exists():
        shutil.rmtree(ALLURE_REPORT)
    print("   ✅ Previous results cleaned")


def build_pytest_command(args):
    """Build the pytest command based on arguments"""
    # Use venv pytest directly
    cmd = [str(VENV_PYTEST)]

    # Test selection
    if args.test:
        test_file = TESTS_DIR / f"test_{args.test}.py"
        if test_file.exists():
            cmd.append(str(test_file))
        else:
            print(f"   ❌ Test file not found: {test_file}")
            print(f"   Available tests:")
            for f in sorted(TESTS_DIR.glob("test_*.py")):
                print(f"      - {f.stem.replace('test_', '')}")
            sys.exit(1)
    else:
        cmd.append(str(TESTS_DIR))

    # Markers
    if args.marker:
        cmd.extend(["-m", args.marker])

    # Note: -v, --alluredir, --clean-alluredir are already in pytest.ini addopts

    return cmd


def run_tests(cmd):
    """Execute pytest and return the exit code"""
    print("\n🧪 Running tests...")
    print(f"   Command: {' '.join(cmd)}")
    print("=" * 60)

    result = subprocess.run(cmd, cwd=str(PROJECT_DIR))
    return result.returncode


def generate_report():
    """Generate Allure HTML report"""
    print("\n📊 Generating Allure HTML report...")
    result = subprocess.run(
        [str(ALLURE_CMD), "generate", str(ALLURE_RESULTS), "--clean", "-o", str(ALLURE_REPORT)],
        cwd=str(PROJECT_DIR),
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"   ❌ Failed to generate report: {result.stderr}")
        return False
    print("   ✅ Report generated successfully")
    return True


def open_report():
    """Open Allure report in browser"""
    print("\n🌐 Opening Allure report in browser...")
    time.sleep(2)
    try:
        subprocess.Popen(
            [str(ALLURE_CMD), "open", str(ALLURE_REPORT)],
            cwd=str(PROJECT_DIR),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("   ✅ Report server started - check your browser!")
    except FileNotFoundError:
        print("   ⚠️  Allure CLI not found, opening HTML directly...")
        webbrowser.open(str(ALLURE_REPORT / "index.html"))


def main():
    parser = argparse.ArgumentParser(description="🧪 Test Runner with Allure Reporting")
    parser.add_argument("--test", "-t", help="Test module to run (e.g., login, shopping, login_and_shop)")
    parser.add_argument("--marker", "-m", help="Run tests by marker (e.g., smoke, regression, e2e)")
    parser.add_argument("--no-report", action="store_true", help="Skip Allure report generation")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--headed", action="store_true", default=True, help="Run browser in headed mode (default)")
    args = parser.parse_args()

    print("=" * 60)
    print("   🧪 Test Runner with Allure Reporting")
    print("=" * 60)

    # Setup
    setup_path()

    if not args.no_report:
        clean_previous_results()

    # Build and run tests
    cmd = build_pytest_command(args)
    exit_code = run_tests(cmd)

    # Results summary
    print("\n" + "=" * 60)
    if exit_code == 0:
        print("   ✅ ALL TESTS PASSED!")
    else:
        print("   ⚠️  SOME TESTS FAILED")
    print("=" * 60)

    # Generate and open report
    if not args.no_report:
        if generate_report():
            open_report()

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
