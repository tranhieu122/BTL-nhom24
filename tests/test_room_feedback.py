"""Unit tests for RoomFeedbackController."""
# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportUnknownLambdaType=false
from __future__ import annotations

import pytest
from typing import Any

from controllers.room_feedback_controller import RoomFeedbackController  # type: ignore[import-not-found]
from dao.room_dao import RoomDAO  # type: ignore[import-not-found]
from dao.user_dao import UserDAO  # type: ignore[import-not-found]
from models.room import Room  # type: ignore[import-not-found]
from models.user import User  # type: ignore[import-not-found]


def _setup() -> tuple[Any, Any]:
    RoomDAO().save(Room("P101", "Phong 101", 40, "Phong hoc", "", "Hoat dong"))
    user = User("U01", "fbuser", "Feedback User", "Sinh vien",
                "fb@test.com", "0901234567", "h", "Hoat dong")
    UserDAO().save(user)
    return RoomFeedbackController(), user


class TestRoomRating:
    def test_add_rating(self):
        ctrl, user = _setup()
        r = ctrl.add_rating("P101", user, 4, "Phong dep")
        assert r.stars == 4
        assert r.room_id == "P101"

    def test_add_rating_invalid_stars(self):
        ctrl, user = _setup()
        with pytest.raises(ValueError, match="1 den 5"):
            ctrl.add_rating("P101", user, 0, "")
        with pytest.raises(ValueError, match="1 den 5"):
            ctrl.add_rating("P101", user, 6, "")

    def test_get_ratings(self):
        ctrl, user = _setup()
        ctrl.add_rating("P101", user, 5, "Tuyet voi")
        ctrl.add_rating("P101", user, 3, "Binh thuong")
        ratings = ctrl.get_ratings("P101")
        assert len(ratings) == 2

    def test_average_stars(self):
        ctrl, user = _setup()
        ctrl.add_rating("P101", user, 5, "A")
        ctrl.add_rating("P101", user, 3, "B")
        avg = ctrl.average_stars("P101")
        assert avg == 4.0

    def test_add_rating_no_room(self):
        ctrl, user = _setup()
        with pytest.raises(ValueError, match="phong"):
            ctrl.add_rating("", user, 4, "Test")


class TestRoomIssue:
    def test_report_issue(self):
        ctrl, user = _setup()
        issue = ctrl.report_issue("P101", user, "Dieu hoa bi hong")
        assert issue.description == "Dieu hoa bi hong"
        assert issue.status == "Chua xu ly"

    def test_report_issue_empty_desc(self):
        ctrl, user = _setup()
        with pytest.raises(ValueError, match="Mo ta"):
            ctrl.report_issue("P101", user, "   ")

    def test_resolve_issue(self):
        ctrl, user = _setup()
        issue = ctrl.report_issue("P101", user, "Den khong sang")
        ctrl.resolve_issue(issue.issue_id)
        issues = ctrl.get_issues("P101")
        resolved = [i for i in issues if i.issue_id == issue.issue_id]
        assert resolved[0].status == "Da xu ly"

    def test_get_all_issues(self):
        ctrl, user = _setup()
        ctrl.report_issue("P101", user, "Issue 1")
        ctrl.report_issue("P101", user, "Issue 2")
        assert len(ctrl.get_issues()) >= 2
        assert len(ctrl.get_issues("P101")) >= 2
