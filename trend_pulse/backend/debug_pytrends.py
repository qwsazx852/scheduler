from pytrends.request import TrendReq
import traceback

def test_pytrends():
    print("Initializing TrendReq...")
    pytrends = TrendReq(hl='zh-TW', tz=480, timeout=(10,25))
    
    print("\n--- Test 1: Daily Trends (Taiwan) ---")
    try:
        df = pytrends.trending_searches(pn='taiwan')
        print("Success! Head:\n", df.head())
    except Exception as e:
        print(f"FAILED: {e}")

    print("\n--- Test 2: Daily Trends (United States) ---")
    try:
        df = pytrends.trending_searches(pn='united_states')
        print("Success! Head:\n", df.head())
    except Exception as e:
        print(f"FAILED: {e}")

    print("\n--- Test 3: Realtime Trends (TW) ---")
    try:
        df = pytrends.realtime_trending_searches(pn='TW')
        print("Success! Head:\n", df.head())
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test_pytrends()
