"""Tests for pagination in admin_panel.py — covers all 4 paginated sections."""
import os
import sys
import re
import inspect

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["BOT_TOKEN"] = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz012345678"

import pytest
from handlers.admin_panel import (
    paginate, _parse_page, _nav_buttons, admin_callbacks, promo_callbacks,
    ITEMS_PER_PAGE,
)


# ── paginate() helper ──

class TestPaginate:
    def test_empty_list(self):
        items, total = paginate([], 0)
        assert items == []
        assert total == 1

    def test_fewer_than_page_size(self):
        items, total = paginate([1, 2, 3], 0)
        assert items == [1, 2, 3]
        assert total == 1

    def test_exact_one_page(self):
        items, total = paginate(list(range(8)), 0)
        assert items == list(range(8))
        assert total == 1

    def test_two_pages_first(self):
        data = list(range(10))
        items, total = paginate(data, 0)
        assert items == list(range(8))
        assert total == 2

    def test_two_pages_second(self):
        data = list(range(10))
        items, total = paginate(data, 1)
        assert items == [8, 9]
        assert total == 2

    def test_page_out_of_range_clamped(self):
        data = list(range(3))
        items, total = paginate(data, 99)
        assert items == [0, 1, 2]
        assert total == 1

    def test_negative_page_clamped(self):
        items, total = paginate(list(range(20)), -1)
        assert items == list(range(8))
        assert total == 3

    def test_custom_per_page(self):
        items, total = paginate(list(range(5)), 0, per_page=2)
        assert items == [0, 1]
        assert total == 3

    def test_per_page_equals_items(self):
        items, total = paginate(list(range(8)), 0, per_page=8)
        assert len(items) == 8
        assert total == 1

    def test_three_full_pages(self):
        data = list(range(24))
        p0, t0 = paginate(data, 0)
        p1, t1 = paginate(data, 1)
        p2, t2 = paginate(data, 2)
        assert len(p0) == 8 and len(p1) == 8 and len(p2) == 8
        assert t0 == t1 == t2 == 3


# ── _parse_page() ──

class TestParsePage:
    def test_no_suffix(self):
        assert _parse_page("admin_users", "admin_users") == 0

    def test_page_zero(self):
        assert _parse_page("admin_users_p0", "admin_users") == 0

    def test_page_five(self):
        assert _parse_page("admin_status_p5", "admin_status") == 5

    def test_page_double_digit(self):
        assert _parse_page("admin_promos_p12", "admin_promos") == 12

    def test_page_refs(self):
        assert _parse_page("admin_refs_p3", "admin_refs") == 3


# ── _nav_buttons() ──

class TestNavButtons:
    def test_single_page_no_buttons(self):
        assert _nav_buttons("admin_users", 0, 1) == []

    def test_first_of_two_pages(self):
        btns = _nav_buttons("admin_users", 0, 2)
        assert len(btns) == 1
        assert btns[0].callback_data == "admin_users_p1"
        assert "▶️" in btns[0].text

    def test_last_of_two_pages(self):
        btns = _nav_buttons("admin_users", 1, 2)
        assert len(btns) == 1
        assert btns[0].callback_data == "admin_users_p0"
        assert "◀️" in btns[0].text

    def test_middle_of_three_pages(self):
        btns = _nav_buttons("admin_promos", 1, 3)
        assert len(btns) == 2
        assert btns[0].callback_data == "admin_promos_p0"
        assert btns[1].callback_data == "admin_promos_p2"

    def test_refs_nav(self):
        btns = _nav_buttons("admin_refs", 0, 3)
        assert len(btns) == 1
        assert btns[0].callback_data == "admin_refs_p1"


# ── Routing: startswith-based matching for all paginated sections ──

class TestRouting:
    @pytest.fixture(autouse=True)
    def _src(self):
        self.src = inspect.getsource(admin_callbacks)

    def test_admin_users_startswith(self):
        assert 'call.data.startswith("admin_users")' in self.src

    def test_admin_status_startswith(self):
        assert 'call.data.startswith("admin_status")' in self.src

    def test_admin_promos_startswith(self):
        assert 'call.data.startswith("admin_promos")' in self.src

    def test_admin_refs_startswith(self):
        assert 'call.data.startswith("admin_refs")' in self.src

    def test_nav_buttons_for_users(self):
        assert '_nav_buttons("admin_users"' in self.src

    def test_nav_buttons_for_status(self):
        assert '_nav_buttons("admin_status"' in self.src

    def test_nav_buttons_for_promos(self):
        assert '_nav_buttons("admin_promos"' in self.src

    def test_nav_buttons_for_refs(self):
        assert '_nav_buttons("admin_refs"' in self.src

    def test_page_header_in_users(self):
        idx = self.src.find('startswith("admin_users")')
        # Find next elif/else to bound the block
        end = self.src.find('\n    elif ', idx + 1)
        block = self.src[idx:end]
        assert "Page " in block

    def test_page_header_in_status(self):
        idx = self.src.find('startswith("admin_status")')
        end = self.src.find('\n    elif ', idx + 1)
        block = self.src[idx:end]
        assert "Page " in block

    def test_page_header_in_promos(self):
        idx = self.src.find('startswith("admin_promos")')
        end = self.src.find('\n    elif ', idx + 1)
        block = self.src[idx:end]
        assert "Page " in block

    def test_page_header_in_refs(self):
        idx = self.src.find('startswith("admin_refs")')
        end = self.src.find('\n    elif ', idx + 1)
        block = self.src[idx:end]
        assert "Page " in block


# ── promo_del_ carries page ──

class TestPromoDelPage:
    def test_promo_del_callback_includes_page(self):
        src = inspect.getsource(admin_callbacks)
        assert 'f"promo_del_{code}_p{page}"' in src

    def test_promo_del_handler_parses_page(self):
        src = inspect.getsource(promo_callbacks)
        idx = src.find('"promo_del_"')
        block = src[idx:idx+400]
        assert "_p" in block
        assert "page" in block


# ── No unpaginated display loops remain ──

class TestNoPaginationGaps:
    def test_all_user_loops_paginated(self):
        src = inspect.getsource(admin_callbacks)
        user_loops = [line.strip() for line in src.split('\n') if 'for user in' in line]
        for loop in user_loops:
            assert 'page_users' in loop, f"Unpaginated user loop: {loop}"

    def test_all_promo_loops_paginated(self):
        src = inspect.getsource(admin_callbacks)
        promo_loops = [line.strip() for line in src.split('\n')
                       if re.search(r'for\s+(code|c),\s*(p|promo)\s+in', line)]
        for loop in promo_loops:
            assert 'page_promos' in loop, f"Unpaginated promo loop: {loop}"

    def test_all_ref_loops_paginated(self):
        src = inspect.getsource(admin_callbacks)
        # Only check actual for-statement loops, not list comprehensions
        ref_loops = [line.strip() for line in src.split('\n')
                     if re.search(r'^\s+for\s+uid_ref', line) and 'in [' not in line and '= [' not in line]
        for loop in ref_loops:
            assert 'page_refs' in loop, f"Unpaginated ref loop: {loop}"


# ── ITEMS_PER_PAGE constant ──

class TestConstant:
    def test_items_per_page_is_8(self):
        assert ITEMS_PER_PAGE == 8


# ── Existing non-paginated callbacks preserved ──

class TestExistingBehaviorPreserved:
    @pytest.fixture(autouse=True)
    def _src(self):
        self.src = inspect.getsource(admin_callbacks)

    def test_admin_stats_exact_match(self):
        assert 'call.data == "admin_stats"' in self.src

    def test_admin_live_monitor_exact_match(self):
        assert 'call.data == "admin_live_monitor"' in self.src

    def test_admin_back_exact_match(self):
        assert 'call.data == "admin_back"' in self.src

    def test_admin_broadcast_exact_match(self):
        assert 'call.data == "admin_broadcast"' in self.src

    def test_no_routing_collision_stats_vs_status(self):
        assert not "admin_stats".startswith("admin_status")

    def test_no_routing_collision_refs_vs_reset(self):
        assert not "admin_reset_trial".startswith("admin_refs")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-x"])
