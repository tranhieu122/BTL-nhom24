"""Unit tests for AuthController."""
from __future__ import annotations

import pytest
from controllers.auth_controller import AuthController


class TestAuthController:
    def test_register_and_login(self):
        ctrl = AuthController()
        ctrl.register("Nguyen Van A", "nguyenvana",
                      "a@test.com", "0901234560", "password1")
        user = ctrl.authenticate("nguyenvana", "password1")
        assert user is not None
        assert user.username == "nguyenvana"
        assert user.role == "Sinh vien"

    def test_login_wrong_password(self):
        ctrl = AuthController()
        ctrl.register("Tran Thi B", "tranthib",
                      "b@test.com", "0901234561", "password2")
        assert ctrl.authenticate("tranthib", "wrongpass") is None

    def test_login_nonexistent_user(self):
        ctrl = AuthController()
        assert ctrl.authenticate("nobody", "pass") is None

    def test_register_duplicate_username(self):
        ctrl = AuthController()
        ctrl.register("User One", "dupuser", "dup1@test.com",
                      "0901234562", "pass123")
        with pytest.raises(ValueError, match="da duoc su dung"):
            ctrl.register("User Two", "dupuser", "dup2@test.com",
                          "0901234563", "pass456")

    def test_register_duplicate_email(self):
        ctrl = AuthController()
        ctrl.register("User One", "user1dup", "same@test.com",
                      "0901234564", "pass123")
        with pytest.raises(ValueError, match="da duoc dang ky"):
            ctrl.register("User Two", "user2dup", "same@test.com",
                          "0901234565", "pass456")

    def test_register_invalid_email(self):
        ctrl = AuthController()
        with pytest.raises(ValueError, match="Email khong hop le"):
            ctrl.register("Test", "testinv", "not-an-email",
                          "0901234566", "pass123")

    def test_register_short_password(self):
        ctrl = AuthController()
        with pytest.raises(ValueError, match="6 ky tu"):
            ctrl.register("Test", "testshort", "short@test.com",
                          "0901234567", "abc")

    def test_register_with_role(self):
        ctrl = AuthController()
        ctrl.register("Giang Vien A", "gva", "gva@test.com",
                      "0901234568", "pass123", role="Giang vien")
        user = ctrl.authenticate("gva", "pass123")
        assert user.role == "Giang vien"

    def test_reset_password(self):
        ctrl = AuthController()
        ctrl.register("Reset User", "resetuser", "reset@test.com",
                      "0901234569", "oldpass")
        ctrl.reset_password("resetuser", "reset@test.com", "newpass1")
        assert ctrl.authenticate("resetuser", "newpass1") is not None
        assert ctrl.authenticate("resetuser", "oldpass") is None

    def test_reset_password_wrong_email(self):
        ctrl = AuthController()
        ctrl.register("Reset User2", "resetuser2", "reset2@test.com",
                      "0901234570", "oldpass")
        with pytest.raises(ValueError):
            ctrl.reset_password("resetuser2", "wrong@test.com", "newpass1")

    def test_locked_account_cannot_login(self):
        ctrl = AuthController()
        ctrl.register("Locked", "lockeduser", "locked@test.com",
                      "0901234571", "pass123")
        user = ctrl.user_dao.find_by_username("lockeduser")
        user.status = "Bi khoa"
        ctrl.user_dao.save(user)
        assert ctrl.authenticate("lockeduser", "pass123") is None
