#!/usr/bin/env python3
"""Normalize an arXiv id/URL, download TeX source tarball, and unpack.

Stdlib only. Does not summarize the paper.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import tarfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional, Tuple

_ID_RE = re.compile(
    r"(?:arXiv:)?(?P<id>(?:\d{4}\.\d{4,5})(?:v\d+)?|[a-z\-]+(?:\.[A-Z]{2})?/\d{7}(?:v\d+)?)",
    re.I,
)


def extract_arxiv_id(text: str) -> str:
    text = text.strip()
    # Direct id
    m = _ID_RE.search(text.replace(" ", ""))
    if not m:
        raise SystemExit(f"Could not parse arXiv id from: {text!r}")
    return m.group("id")


def cache_key(arxiv_id: str) -> str:
    # Drop version suffix for stable cache dirs: 2601.07372v2 -> 2601.07372
    return re.sub(r"v\d+$", "", arxiv_id, flags=re.I).replace("/", "_")


def source_url(arxiv_id: str) -> str:
    return f"https://arxiv.org/src/{arxiv_id}"


def default_cache_root() -> Path:
    return Path.home() / ".cache" / "arxiv"


def legacy_nanochat_paths(key: str) -> Tuple[Path, Path]:
    root = Path.home() / ".cache" / "nanochat" / "knowledge"
    return root / f"{key}.tar.gz", root / key


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".partial")
    try:
        with urllib.request.urlopen(url, timeout=120) as resp, open(tmp, "wb") as out:
            shutil.copyfileobj(resp, out)
        tmp.replace(dest)
    except Exception:
        if tmp.exists():
            tmp.unlink(missing_ok=True)
        raise


def unpack_tarball(tarball: Path, dest_dir: Path) -> None:
    if dest_dir.exists():
        return
    dest_dir.mkdir(parents=True, exist_ok=True)
    try:
        with tarfile.open(tarball, "r:*") as tar:
            # Python 3.12+ supports filter=; use if available
            try:
                tar.extractall(dest_dir, filter=tarfile.data_filter)
            except (TypeError, AttributeError):
                tar.extractall(dest_dir)
    except Exception:
        # Clean partial unpack
        if dest_dir.exists():
            shutil.rmtree(dest_dir, ignore_errors=True)
        raise


def find_existing(
    key: str, cache_root: Path
) -> Tuple[Optional[Path], Optional[Path]]:
    tarball = cache_root / f"{key}.tar.gz"
    unpacked = cache_root / key
    if tarball.is_file():
        return tarball, unpacked if unpacked.is_dir() else None
    legacy_tar, legacy_dir = legacy_nanochat_paths(key)
    if legacy_tar.is_file():
        return legacy_tar, legacy_dir if legacy_dir.is_dir() else None
    return None, None


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fetch and unpack arXiv TeX source (not PDF)."
    )
    parser.add_argument(
        "--id-or-url",
        required=True,
        help="arXiv abs/pdf/html/src URL or bare id",
    )
    parser.add_argument(
        "--cache-root",
        default=str(default_cache_root()),
        help="Cache directory (default: ~/.cache/arxiv)",
    )
    parser.add_argument(
        "--print-only",
        action="store_true",
        help="Print id/url/paths only; do not download",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download even if tarball exists",
    )
    args = parser.parse_args(argv)

    arxiv_id = extract_arxiv_id(args.id_or_url)
    key = cache_key(arxiv_id)
    url = source_url(arxiv_id)
    cache_root = Path(args.cache_root).expanduser()
    tarball = cache_root / f"{key}.tar.gz"
    unpacked = cache_root / key

    existing_tar, existing_dir = find_existing(key, cache_root)

    print(f"arxiv_id={arxiv_id}")
    print(f"cache_key={key}")
    print(f"source_url={url}")
    print(f"tarball={tarball}")
    print(f"unpacked={unpacked}")

    if args.print_only:
        if existing_tar:
            print(f"existing_tarball={existing_tar}")
        if existing_dir:
            print(f"existing_unpacked={existing_dir}")
        return 0

    if existing_tar and not args.force:
        # Reuse legacy or current tarball path
        src_tar = existing_tar
        print(f"using_existing_tarball={src_tar}")
        if src_tar.resolve() != tarball.resolve():
            # Copy into default cache for consistency
            tarball.parent.mkdir(parents=True, exist_ok=True)
            if not tarball.exists():
                shutil.copy2(src_tar, tarball)
                print(f"copied_to={tarball}")
        else:
            tarball = src_tar
    else:
        print(f"downloading={url}")
        try:
            download(url, tarball)
        except urllib.error.HTTPError as exc:
            print(f"download_failed HTTP {exc.code}: {exc.reason}", file=sys.stderr)
            return 1
        except Exception as exc:  # noqa: BLE001
            print(f"download_failed: {exc}", file=sys.stderr)
            return 1
        print("download_ok")

    if unpacked.is_dir() and not args.force:
        print(f"already_unpacked={unpacked}")
    else:
        if args.force and unpacked.exists():
            shutil.rmtree(unpacked)
        print(f"unpacking_to={unpacked}")
        unpack_tarball(tarball, unpacked)
        print("unpack_ok")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
