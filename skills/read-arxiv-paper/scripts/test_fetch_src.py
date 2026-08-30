#!/usr/bin/env python3
"""Cheap unit tests for fetch_src.py (no network)."""

from __future__ import annotations

import importlib.util
import io
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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


class TestSafeTarFilter(unittest.TestCase):
    def test_rejects_fifo(self):
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out"
            dest.mkdir()
            info = tarfile.TarInfo(name="pipe")
            info.type = tarfile.FIFOTYPE
            with self.assertRaises(SystemExit) as cm:
                fetch_src._safe_tar_filter(info, dest)
            self.assertIn("special tar member", str(cm.exception))

    def test_rejects_escape(self):
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out"
            dest.mkdir()
            info = tarfile.TarInfo(name="../escape.txt")
            info.type = tarfile.REGTYPE
            info.size = 1
            with self.assertRaises(SystemExit):
                fetch_src._safe_tar_filter(info, dest)

    def test_allows_regular_file(self):
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out"
            dest.mkdir()
            info = tarfile.TarInfo(name="main.tex")
            info.type = tarfile.REGTYPE
            info.size = 10
            out = fetch_src._safe_tar_filter(info, dest)
            self.assertIs(out, info)


class TestSafeUnpack(unittest.TestCase):
    def test_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            tarball = td_path / "evil.tar.gz"
            dest = td_path / "out"
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

    def test_rejects_oversized_uncompressed(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            tarball = td_path / "big.tar.gz"
            dest = td_path / "out"
            with tarfile.open(tarball, "w:gz") as tar:
                info = tarfile.TarInfo(name="huge.bin")
                info.size = 101
                tar.addfile(info, io.BytesIO(b"x" * 101))
            with mock.patch.object(fetch_src, "_MAX_UNPACK_BYTES", 100):
                with self.assertRaises(SystemExit) as cm:
                    fetch_src.unpack_tarball(tarball, dest)
            self.assertIn("uncompressed size exceeds", str(cm.exception))


class TestDownloadGuards(unittest.TestCase):
    def test_systemexit_cleans_partial(self):
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "x.tar.gz"
            partial = dest.with_suffix(dest.suffix + ".partial")

            class FakeResp:
                headers = {"Content-Length": str(fetch_src._MAX_DOWNLOAD_BYTES + 1)}

                def read(self, n: int = -1):
                    return b""

                def __enter__(self):
                    return self

                def __exit__(self, *args):
                    return False

            with mock.patch("urllib.request.urlopen", return_value=FakeResp()):
                with self.assertRaises(SystemExit):
                    fetch_src.download("https://arxiv.org/src/2601.07372", dest)
            self.assertFalse(partial.exists())
            self.assertFalse(dest.exists())


if __name__ == "__main__":
    unittest.main()
