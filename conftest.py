import pytest
import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    passed_reports = terminalreporter.stats.get('passed', [])
    failed_reports = terminalreporter.stats.get('failed', [])
    skipped_reports = terminalreporter.stats.get('skipped', [])

    passed = len(passed_reports)
    failed = len(failed_reports)
    skipped = len(skipped_reports)

    terminalreporter.write("\n")
    terminalreporter.write_line("=" * 40, bold=True)
    terminalreporter.write_line("SMARTDROP TEST REPORT", bold=True)
    terminalreporter.write_line("=" * 40, bold=True)
    terminalreporter.write_line(f"Passed:  {passed}")
    terminalreporter.write_line(f"Failed:  {failed}")
    terminalreporter.write_line(f"Skipped: {skipped}")
    terminalreporter.write_line("=" * 40, bold=True)

    if failed > 0:
        terminalreporter.write_line("\n--- BAŞARISIZ TESTLER VE HATA SEBEPLERİ ---", red=True, bold=True)
        for rep in failed_reports:
            terminalreporter.write_line(f"• Test Adı:    {rep.nodeid}", bold=True)
            terminalreporter.write_line(f"  Hata Sebebi: {rep.longreprtext}\n")
