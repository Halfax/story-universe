"""Migration helper to flatten repo into root `/src`, `/shared`, `/tools`, `/docs`.

Usage:
  # dry-run (default)
  python tools/migrate_to_flat.py

  # to perform changes
  python tools/migrate_to_flat.py --apply

Options:
  --remove-old    Remove original component folders after copying (destructive).

This script copies component `src` dirs into `src/<pkg>` and rewrites simple
`from src.`/`import src` occurrences into the target package name. It is
conservative and performs a dry-run unless `--apply` is supplied.
"""
from __future__ import annotations
import argparse
import shutil
from pathlib import Path
import re
import sys


COMPONENTS = [
    # (source_dir, dest_root_relative, pkg_prefixes_to_strip)
    (Path('story-universe/chronicle-keeper/src'), Path('src'), ['chronicle_keeper', 'src']),
    (Path('story-universe/narrative-engine/src'), Path('src'), ['narrative_engine', 'src']),
]


def rewrite_content(text: str, strip_prefixes: list[str]) -> str:
    # Remove package prefixes like `src.`, `chronicle_keeper.` or `narrative_engine.`
    for prefix in strip_prefixes:
        # from prefix.module -> from module
        text = re.sub(rf"\bfrom\s+{re.escape(prefix)}\.", 'from ', text)
        # import prefix.module -> import module
        text = re.sub(rf"\bimport\s+{re.escape(prefix)}\.", 'import ', text)
        # import prefix as alias -> remove prefix if importing package root
        text = re.sub(rf"\bimport\s+{re.escape(prefix)}\b", '', text)
    # Also clean up double spaces introduced
    text = re.sub(r'\s+\.', '.', text)
    text = re.sub(r'from\s+\s+', 'from ', text)
    text = re.sub(r'import\s+\s+', 'import ', text)
    return text


def copy_and_rewrite(src_root: Path, dest_root: Path, pkg_name: str, apply: bool) -> int:
    if not src_root.exists():
        print(f' - source not found: {src_root} (skipping)')
        return 0
    files_copied = 0
    for src in src_root.rglob('*.py'):
        rel = src.relative_to(src_root)
        dest = dest_root.joinpath(rel)
        dest.parent.mkdir(parents=True, exist_ok=True)
        content = src.read_text(encoding='utf-8')
        new_content = rewrite_content(content, pkg_name)
        print(f'Copy: {src} -> {dest} (pkg={pkg_name})')
        if apply:
            dest.write_text(new_content, encoding='utf-8')
        files_copied += 1
    return files_copied


def copy_tests(src_tests: Path, dest_tests: Path, pkg_name: str, apply: bool) -> int:
    if not src_tests.exists():
        return 0
    count = 0
    for src in src_tests.rglob('*.py'):
        rel = src.relative_to(src_tests)
        dest = dest_tests.joinpath(rel.name)
        dest.parent.mkdir(parents=True, exist_ok=True)
        content = src.read_text(encoding='utf-8')
        new_content = rewrite_content(content, pkg_name)
        print(f'Copy test: {src} -> {dest}')
        if apply:
            dest.write_text(new_content, encoding='utf-8')
        count += 1
    return count


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--apply', action='store_true', help='Perform copying and rewriting')
    p.add_argument('--remove-old', action='store_true', help='Remove original component dirs after copying')
    args = p.parse_args(argv)

    repo_root = Path('.').resolve()
    print('Repository root:', repo_root)

    total = 0
    for src_dir, dest_dir, prefixes in COMPONENTS:
        src_root = repo_root.joinpath(src_dir)
        dest_root = repo_root.joinpath(dest_dir)
        pkg_name = prefixes  # list of prefixes to strip
        print(f'Processing component: {src_root} -> {dest_root} (strip prefixes={pkg_name})')
        copied = copy_and_rewrite(src_root, dest_root, pkg_name, args.apply)
        total += copied

        # Copy tests if present alongside component directly into tests/
        src_tests = src_root.parent.joinpath('tests')
        dest_tests = repo_root.joinpath('tests')
        test_count = copy_tests(src_tests, dest_tests, pkg_name, args.apply)
        if test_count:
            print(f'  Copied {test_count} tests to {dest_tests}')

        if args.remove_old and args.apply:
            print(f'  Removing original {src_root.parent} (destructive)')
            shutil.rmtree(src_root.parent)

    print(f'Dry-run={not args.apply}: planned to copy {total} Python files.')
    if not args.apply:
        print('Run with --apply to perform changes. Review the printed plan first.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
