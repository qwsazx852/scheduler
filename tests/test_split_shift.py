from src.scheduler_logic import SchedulerLogic

def test_parsing():
    s = SchedulerLogic(2026, 1, [], {})
    time_str = "10:00-12:00,17:00-21:30"
    segments = s._parse_shift_segments(time_str)
    print(f"Segments for {time_str}: {segments}")
    
    expected = [(600, 720), (1020, 1290)]
    assert segments == expected, f"Expected {expected}, got {segments}"
    print("Parsing OK.")

def test_overlap():
    s = SchedulerLogic(2026, 1, [], {})
    time_str = "10:00-12:00,17:00-21:30"
    segments = s._parse_shift_segments(time_str)
    
    # Need 10:00-11:00 (600-660)
    need_start, need_end = 600, 660
    is_overlap = False
    for start, end in segments:
        if start < need_end and end > need_start:
            is_overlap = True
            break
    print(f"Overlap with 10:00-11:00: {is_overlap}")
    assert is_overlap

    # Need 14:00-15:00 (840-900) - Gap
    need_start, need_end = 840, 900
    is_overlap = False
    for start, end in segments:
        if start < need_end and end > need_start:
            is_overlap = True
            break
    print(f"Overlap with 14:00-15:00: {is_overlap}")
    assert not is_overlap

    # Need 18:00-19:00 (1080-1140)
    need_start, need_end = 1080, 1140
    is_overlap = False
    for start, end in segments:
        if start < need_end and end > need_start:
            is_overlap = True
            break
    print(f"Overlap with 18:00-19:00: {is_overlap}")
    assert is_overlap
    print("Overlap Logic OK.")

if __name__ == "__main__":
    try:
        test_parsing()
        test_overlap()
        print("ALL TESTS PASSED")
    except Exception as e:
        print(f"FAILED: {e}")
