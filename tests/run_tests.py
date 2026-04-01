"""
Test runner for the comprehensive test suite.

Orchestrates all test suites (correctness, integration, format, batch) and
generates results report. Modeled after profiling/run_profiles.py.
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from tests.common import save_test_results
import tests.test_indicators as test_indicators
import tests.test_e2e as test_e2e
import tests.test_formats as test_formats
import tests.test_batch as test_batch


class TestRunner:
    """Main test orchestrator that runs all test suites."""
    
    def __init__(self, suite_filter: Optional[str] = None):
        """
        Initialize test runner.
        
        Args:
            suite_filter: Optional filter for specific test suite:
                         all, correctness, integration, formats, batch
                         If None, runs all suites.
        """
        self.suite_filter = suite_filter or "all"
        self.start_time = None
        self.end_time = None
    
    async def run_correctness_suite(self):
        """Run indicator correctness tests."""
        print("\n" + "=" * 70)
        print("RUNNING: Correctness Tests")
        print("=" * 70)
        
        try:
            results = await test_indicators.run_all_tests()
            passed = sum(1 for r in results if r.passed)
            total = len(results)
            
            for result in results:
                print(result)
            
            return {
                "suite_name": "correctness",
                "total_tests": total,
                "passed": passed,
                "failed": total - passed,
                "results": results,
            }
        except Exception as e:
            print(f"ERROR in correctness suite: {str(e)}")
            raise
    
    async def run_integration_suite(self):
        """Run end-to-end integration tests."""
        print("\n" + "=" * 70)
        print("RUNNING: Integration Tests")
        print("=" * 70)
        
        try:
            results = await test_e2e.run_all_tests()
            passed = sum(1 for r in results if r.passed)
            total = len(results)
            
            for result in results:
                print(result)
            
            return {
                "suite_name": "integration",
                "total_tests": total,
                "passed": passed,
                "failed": total - passed,
                "results": results,
            }
        except Exception as e:
            print(f"ERROR in integration suite: {str(e)}")
            raise
    
    async def run_formats_suite(self):
        """Run output format tests."""
        print("\n" + "=" * 70)
        print("RUNNING: Format Tests")
        print("=" * 70)
        
        try:
            results = await test_formats.run_all_tests()
            passed = sum(1 for r in results if r.passed)
            total = len(results)
            
            for result in results:
                print(result)
            
            return {
                "suite_name": "formats",
                "total_tests": total,
                "passed": passed,
                "failed": total - passed,
                "results": results,
            }
        except Exception as e:
            print(f"ERROR in formats suite: {str(e)}")
            raise
    
    async def run_batch_suite(self):
        """Run batch processing tests."""
        print("\n" + "=" * 70)
        print("RUNNING: Batch Processing Tests")
        print("=" * 70)
        
        try:
            results = await test_batch.run_all_tests()
            passed = sum(1 for r in results if r.passed)
            total = len(results)
            
            for result in results:
                print(result)
            
            return {
                "suite_name": "batch",
                "total_tests": total,
                "passed": passed,
                "failed": total - passed,
                "results": results,
            }
        except Exception as e:
            print(f"ERROR in batch suite: {str(e)}")
            raise
    
    def print_overall_summary(self, all_results: List[dict]):
        """Print overall summary across all suites."""
        total_tests = 0
        total_passed = 0
        total_failed = 0
        
        for suite_data in all_results:
            total_tests += suite_data.get("total_tests", 0)
            total_passed += suite_data.get("passed", 0)
            total_failed += suite_data.get("failed", 0)
        
        print("\n" + "=" * 70)
        print("OVERALL TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {total_passed}")
        print(f"Failed: {total_failed}")
        
        if total_tests > 0:
            overall_rate = (total_passed / total_tests) * 100
            print(f"Success Rate: {overall_rate:.1f}%")
        
        print("=" * 70)
        
        return total_tests, total_passed, total_failed
    
    async def run(self) -> int:
        """
        Run all test suites.
        
        Returns:
            Exit code: 0 if all tests pass, 1 if any fail/error
        """
        self.start_time = datetime.now().isoformat()
        
        all_results = []
        
        try:
            # Run selected suites
            if self.suite_filter in ["all", "correctness"]:
                results = await self.run_correctness_suite()
                all_results.append(results)
            
            if self.suite_filter in ["all", "integration"]:
                results = await self.run_integration_suite()
                all_results.append(results)
            
            if self.suite_filter in ["all", "formats"]:
                results = await self.run_formats_suite()
                all_results.append(results)
            
            if self.suite_filter in ["all", "batch"]:
                results = await self.run_batch_suite()
                all_results.append(results)
        
        except Exception as e:
            print(f"\n❌ TEST EXECUTION FAILED: {str(e)}")
            import traceback
            traceback.print_exc()
            return 1
        
        self.end_time = datetime.now().isoformat()
        
        # Print summary
        total_tests, total_passed, total_failed = (
            self.print_overall_summary(all_results)
        )
        
        # Determine exit code
        if total_failed > 0:
            print("\n❌ TESTS FAILED")
            return 1
        elif total_tests > 0:
            print("\n✅ ALL TESTS PASSED")
            return 0
        else:
            print("\n⚠️  NO TESTS RUN")
            return 1


async def main(suite_filter: Optional[str] = None) -> int:
    """
    Main entry point for test runner.
    
    Args:
        suite_filter: Optional filter for specific test suite
    
    Returns:
        Exit code
    """
    runner = TestRunner(suite_filter=suite_filter)
    return await runner.run()


if __name__ == "__main__":
    suite_filter = None
    
    if len(sys.argv) > 1:
        suite_filter = sys.argv[1]
    
    exit_code = asyncio.run(main(suite_filter))
    sys.exit(exit_code)
