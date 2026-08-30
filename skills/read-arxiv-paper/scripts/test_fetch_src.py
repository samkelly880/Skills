#!/usr/bin/env python3
"""Cheap unit tests for fetch_src.py (no network)."""

from __future__ import annotations

import importlib.util
import io
import tarfile
import tempfile
import unittest
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_SPEC = importlib.util.spec_from_file_location("fetch_src", _HERE / "fetch_src.py")
assert _SPEC and _SPEC.loader
fetch_src = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(fetch_src)


class TestExtractId(unittest.TestCase):
    def test_abs_url(self):
        self.assertEqual(
            fetch_src.extract_arxiv_id("https://www.arxiv.org/abs/2601.07372"),
            "2601.07372",
        )

    def test_pdf_url_with_version(self):
        self.assertEqual(
            fetch_src.extract_arxiv_id("https://arxiv.org/pdf/2601.07372v2.pdf"),
            "2601.07372v2",
        )

    def test_bare_id(self):
        self.assertEqual(fetch_src.extract_arxiv_id("2601.07372"), "2601.07372")

    def test_legacy_id(self):
        self.assertEqual(
            fetch_src.extract_arxiv_id("https://arxiv.org/abs/hep-th/9901001"),
            "hep-th/9901001",
        )

    def test_rejects_garbage(self):
        with self.assertRaises(SystemExit):
            fetch_src.extract_arxiv_id("not-a-paper")


class TestCacheKey(unittest.TestCase):
    def test_preserves_version(self):
        self.assertEqual(fetch_src.cache_key("2601.07372v2"), "2601.07372v2")
        self.assertNotEqual(
            fetch_src.cache_key("2601.07372v1"),
            fetch_src.cache_key("2601.07372v2"),
        )

    def test_maps_slash(self):
        self.assertEqual(fetch_src.cache_key("hep-th/9901001"), "hep-th_9901001")


class TestSafeUnpack(unittest.TestCase):
    def test_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            tarball = td_path / "evil.tar.gz"
            dest = td_path / "out"
            # Build a tar with a ../ escape member
            with tarfile.open(tarball, "w:gz") as tar:
                info = tarfile.TarInfo(name="../escape.txt")
                data = b"nope"
                info.size = len(data)
                tar.addfile(info, io.BytesIO(data))
            with self.assertRaises(SystemExit):
                fetch_src.unpack_tarball(tarball, dest)
            self.assertFalse((td_path / "escape.txt").exists())

    def test_unpacks_normal_member(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            tarball = td_path / "ok.tar.gz"
            dest = td_path / "out"
            with tarfile.open(tarball, "w:gz") as tar:
                info = tarfile.TarInfo(name="main.tex")
                data = b"\\documentclass{article}\\begin{document}Hi\\end{document}\n"
                info.size = len(data)
                tar.addfile(info, io.BytesIO(data))
            fetch_src.unpack_tarball(tarball, dest)
            self.assertTrue((dest / "main.tex").is_file())


if __name__ == "__main__":
    unittest.main()
