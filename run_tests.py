import sys
import tests.test_utils as tu
import tests.test_database as td

def run_tests():
    print("🚀 Starting Careerly AI Unit Test Suite (Zero-Dependency Custom Runner)\n")

    passed = 0
    failed = 0

    # Test Utils
    utils_tests = [
        ("test_format_salary_inr", tu.test_format_salary_inr),
        ("test_format_salary_usd", tu.test_format_salary_usd),
        ("test_extract_skills", tu.test_extract_skills),
        ("test_calculate_cosine_similarity", tu.test_calculate_cosine_similarity),
        ("test_calculate_hybrid_score", tu.test_calculate_hybrid_score),
        ("test_check_notice_period_compatibility", tu.test_check_notice_period_compatibility)
    ]

    # Test Database (wrap fixture logic)
    def wrap_td_save_retrieve_job():
        generator = td.mock_db()
        mock_conn = next(generator)
        try:
            td.test_save_and_retrieve_job(mock_conn)
        finally:
            try:
                next(generator)
            except StopIteration:
                pass

    def wrap_td_save_retrieve_profile():
        generator = td.mock_db()
        mock_conn = next(generator)
        try:
            td.test_save_and_retrieve_profile(mock_conn)
        finally:
            try:
                next(generator)
            except StopIteration:
                pass

    db_tests = [
        ("test_save_and_retrieve_job", wrap_td_save_retrieve_job),
        ("test_save_and_retrieve_profile", wrap_td_save_retrieve_profile)
    ]

    all_tests = utils_tests + db_tests

    for name, func in all_tests:
        try:
            func()
            print(f"✅ {name} PASSED")
            passed += 1
        except Exception as e:
            import traceback
            print(f"❌ {name} FAILED: {e}")
            traceback.print_exc()
            failed += 1

    print(f"\n📊 Summary: {passed} passed, {failed} failed.")
    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
