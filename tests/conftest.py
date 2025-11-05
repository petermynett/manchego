"""Shared pytest fixtures for manchego tests.

This module provides common fixtures used across all test modules.
Follow Rule 706 for autouse fixture patterns for directory isolation.
"""

from pathlib import Path

import pytest


@pytest.fixture
def touch(tmp_path: Path):
    """Create a file at any path with optional content.

    Args:
        tmp_path: Pytest temporary directory fixture.

    Returns:
        Callable[[Path, bytes], Path]: Function that creates files at given path.
    """

    def _touch(p: Path, content: bytes = b"test") -> Path:
        """Create file at path with content.

        Args:
            p: Path to create file at (can be absolute or relative to tmp_path).
            content: Bytes content to write to file.

        Returns:
            Path to created file.
        """
        full_path = p if p.is_absolute() else tmp_path / p
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_bytes(content)
        return full_path

    return _touch


@pytest.fixture
def make_files(tmp_path: Path):
    """Bulk-create files under tmp_path.

    Args:
        tmp_path: Pytest temporary directory fixture.

    Returns:
        Callable[[list[str]], list[Path]]: Function that creates multiple files.
    """

    def _make_files(names: list[str]) -> list[Path]:
        """Create multiple files from list of names.

        Args:
            names: List of file names (relative paths) to create.

        Returns:
            List of Path objects for created files.
        """
        paths = []
        for name in names:
            path = tmp_path / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"test")
            paths.append(path)
        return paths

    return _make_files
