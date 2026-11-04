"""
Kiểm thử tích hợp cho Streamlit App (Phase 3).
"""
import py_compile
import os
import pytest

APP_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app.py"))


def test_app_compilation():
    """Kiểm tra mã nguồn app.py compile thành công, không có lỗi cú pháp."""
    assert os.path.exists(APP_PATH)
    compiled_file = py_compile.compile(APP_PATH, doraise=True)
    assert compiled_file is not None
