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

# Soft caps — arXiv TeX sources are typically small; refuse surprising payloads.
_MAX_DOWNLOAD_BYTES = 100 * 1024 * 1024  # 100 MiB compressed
_MAX_UNPACK_BYTES = 500 * 1024 * 1024  # 500 MiB uncompressed total
_GZIP_MAGIC = b"\x1f\x8b"


def extract_arxiv_id(text: str) -> str:
    text = text.strip()
    m = _ID_RE.search(text.replace(" ", ""))
    if not m:
        raise SystemExit(f"Could not parse arXiv id from: {text!r}")
    return m.group("id")


def cache_key(arxiv_id: str) -> str:
    """Stable filesystem key that preserves version and maps '/' → '_'.

    Examples:
      2601.07372      -> 2601.07372
      2601.07372v2    -> 2601.07372v2
      hep-th/9901001  -> hep-th_9901001
    """
    return arxiv_id.replace("/", "_")


def source_url(arxiv_id: str) -> str:
    return f"https://arxiv.org/src/{arxiv_id}"


def default_cache_root() -> Path:
    return Path.home() / ".cache" / "arxiv"


def legacy_nanochat_paths(key: str) -> Tuple[Path, Path]:
    root = Path.home() / ".cache" / "nanochat" / "knowledge"
    return root / f"{key}.tar.gz", root / key


def _safe_tar_filter(member: tarfile.TarInfo, dest_dir: Path) -> tarfile.TarInfo:
    """Fail-closed member filter for Python versions without tarfile.data_filter."""
    name = member.name
    if not name or name.startswith("/"):
        raise SystemExit(f"refusing absolute tar path: {name!r}")
    # Only regular files and directories (parity with tarfile.data_filter).
    if not (member.isfile() or member.isdir()):
        raise SystemExit(
            f"refusing special tar member type {member.type!r}: {name!r}"
        )
    target = (dest_dir / name).resolve()
    try:
        target.relative_to(dest_dir.resolve())
    except ValueError as exc:
        raise SystemExit(f"refusing tar path escape: {name!r}") from exc
    if member.issym() or member.islnk():
        # Unreachable if we only allow file/dir, but keep belt-and-braces.
        raise SystemExit(f"refusing tar link member: {name!r}")
    if member.size < 0:
        raise SystemExit(f"refusing negative-size member: {name!r}")
    return member


def unpack_tarball(tarball: Path, dest_dir: Path) -> None:
    """Extract ``tarball`` into ``dest_dir``.

    Caller must ensure ``dest_dir`` does not already exist (or remove it first)
    when the archive was refreshed; this function will not silently reuse a
    stale tree.
    """
    if dest_dir.exists():
        raise SystemExit(
            f"refusing unpack: destination already exists: {dest_dir} "
            "(caller must remove it before unpacking a refreshed archive)"
        )
    dest_dir.mkdir(parents=True, exist_ok=True)
    try:
        with tarfile.open(tarball, "r:*") as tar:
            members = tar.getmembers()
            total = 0
            for member in members:
                if member.isfile():
                    total += max(member.size, 0)
                    if total > _MAX_UNPACK_BYTES:
                        raise SystemExit(
                            f"refusing unpack: uncompressed size exceeds "
                            f"{_MAX_UNPACK_BYTES} bytes"
                        )
            if hasattr(tarfile, "data_filter"):
                filter_errors = (
                    getattr(tarfile, "OutsideDestinationError", ()),
                    getattr(tarfile, "FilterError", ()),
                    getattr(tarfile, "AbsolutePathError", ()),
                    getattr(tarfile, "SpecialFileError", ()),
                    getattr(tarfile, "AbsoluteLinkError", ()),
                    getattr(tarfile, "LinkOutsideDestinationError", ()),
                )
                # Filter out empty tuples from missing attrs
                filter_errors = tuple(e for e in filter_errors if e)
                try:
                    tar.extractall(dest_dir, filter=tarfile.data_filter)
                except filter_errors as exc:
                    raise SystemExit(f"refusing unsafe tar member: {exc}") from exc
            else:
                for member in members:
                    _safe_tar_filter(member, dest_dir)
                    tar.extract(member, dest_dir)
    except SystemExit:
        if dest_dir.exists():
            shutil.rmtree(dest_dir, ignore_errors=True)
        raise
    except Exception:
        if dest_dir.exists():
            shutil.rmtree(dest_dir, ignore_errors=True)
        raise


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".partial")
    try:
        with urllib.request.urlopen(url, timeout=120) as resp:
            length_hdr = resp.headers.get("Content-Length")
            if length_hdr is not None:
                try:
                    length = int(length_hdr)
                except ValueError:
                    length = None
                else:
                    if length > _MAX_DOWNLOAD_BYTES:
                        raise SystemExit(
                            f"refusing download: Content-Length {length} exceeds "
                            f"{_MAX_DOWNLOAD_BYTES} bytes"
                        )

            first = resp.read(2)
            if len(first) < 2:
                raise SystemExit("refusing download: empty response")
            buffered = first + resp.read(512)
            is_gzip = buffered.startswith(_GZIP_MAGIC)
            is_tar = b"ustar" in buffered[257:262] if len(buffered) >= 262 else False
            if not (is_gzip or is_tar):
                ctype = (resp.headers.get("Content-Type") or "").lower()
                # Refuse obvious non-archive error bodies; magic is authoritative.
                if "html" in ctype or "json" in ctype or "text/plain" in ctype:
                    raise SystemExit(
                        f"refusing download: unexpected Content-Type {ctype!r}"
                    )
                raise SystemExit(
                    "refusing download: payload is not gzip or tar (bad magic)"
                )

            written = 0
            with open(tmp, "wb") as out:
                out.write(buffered)
                written += len(buffered)
                while True:
                    chunk = resp.read(1024 * 256)
                    if not chunk:
                        break
                    written += len(chunk)
                    if written > _MAX_DOWNLOAD_BYTES:
                        raise SystemExit(
                            f"refusing download: exceeded {_MAX_DOWNLOAD_BYTES} bytes"
                        )
                    out.write(chunk)
        tmp.replace(dest)
    except BaseException:
        # Includes SystemExit policy refusals — always drop partials.
        if tmp.exists():
            tmp.unlink(missing_ok=True)
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

    refreshed = False
    if existing_tar and not args.force:
        src_tar = existing_tar
        print(f"using_existing_tarball={src_tar}")
        if src_tar.resolve() != tarball.resolve():
            tarball.parent.mkdir(parents=True, exist_ok=True)
            if not tarball.exists():
                shutil.copy2(src_tar, tarball)
                print(f"copied_to={tarball}")
                refreshed = True
        else:
            tarball = src_tar
    else:
        print(f"downloading={url}")
        try:
            download(url, tarball)
        except urllib.error.HTTPError as exc:
            print(f"download_failed HTTP {exc.code}: {exc.reason}", file=sys.stderr)
            return 1
        except SystemExit as exc:
            print(f"download_failed: {exc}", file=sys.stderr)
            return 1
        except Exception as exc:  # noqa: BLE001
            print(f"download_failed: {exc}", file=sys.stderr)
            return 1
        print("download_ok")
        refreshed = True

    if unpacked.is_dir() and not args.force and not refreshed:
        print(f"already_unpacked={unpacked}")
    else:
        if unpacked.exists() and (args.force or refreshed):
            shutil.rmtree(unpacked)
        print(f"unpacking_to={unpacked}")
        try:
            unpack_tarball(tarball, unpacked)
        except SystemExit as exc:
            print(f"unpack_failed: {exc}", file=sys.stderr)
            return 1
        except Exception as exc:  # noqa: BLE001
            print(f"unpack_failed: {exc}", file=sys.stderr)
            return 1
        print("unpack_ok")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
