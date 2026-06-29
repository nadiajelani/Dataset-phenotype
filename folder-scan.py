#!/usr/bin/env python3
"""
Fast folder structure and file count scanner.

Run this BEFORE video_inventory.py if you're looking at a large, possibly
mixed-content directory. It does not open or probe any video files --
it only lists folder structure and counts files by extension and by
subfolder, so it finishes in seconds rather than hours.

This does not transmit anything anywhere; it only reads local file names
and writes a local text summary.

Usage:
    python3 folder_scan.py /path/to/owncloud/directory

Output:
    Prints a folder tree with file counts directly to the terminal, and
    also writes folder_scan_summary.txt in the current directory.
"""

import sys
import os
from pathlib import Path
from collections import defaultdict

VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".m4v", ".wmv", ".mts", ".mxf"}


def scan(root_path):
    root = Path(root_path)

    ext_counts = defaultdict(int)
    folder_counts = defaultdict(lambda: defaultdict(int))  # folder -> ext -> count
    folder_total = defaultdict(int)
    total_files = 0
    total_size_bytes = 0

    print(f"Scanning {root} ...")
    for path in root.rglob("*"):
        if path.is_file():
            total_files += 1
            ext = path.suffix.lower()
            ext_counts[ext] += 1
            try:
                total_size_bytes += path.stat().st_size
            except OSError:
                pass

            # Track at the top-level subfolder relative to root, so we get
            # a manageable summary even if the tree is deeply nested.
            try:
                rel = path.relative_to(root)
                top_level = rel.parts[0] if len(rel.parts) > 1 else "(root)"
            except ValueError:
                top_level = "(root)"

            folder_counts[top_level][ext] += 1
            folder_total[top_level] += 1

    return {
        "total_files": total_files,
        "total_size_bytes": total_size_bytes,
        "ext_counts": ext_counts,
        "folder_counts": folder_counts,
        "folder_total": folder_total,
    }


def human_size(num_bytes):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} PB"


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 folder_scan.py /path/to/owncloud/directory")
        sys.exit(1)

    root_path = sys.argv[1]
    if not os.path.isdir(root_path):
        print(f"ERROR: {root_path} is not a valid directory")
        sys.exit(1)

    result = scan(root_path)

    lines = []
    lines.append("=" * 70)
    lines.append("FOLDER SCAN SUMMARY")
    lines.append("=" * 70)
    lines.append(f"Root path: {root_path}")
    lines.append(f"Total files (all types): {result['total_files']}")
    lines.append(f"Total size: {human_size(result['total_size_bytes'])}")
    lines.append("")

    lines.append("-" * 70)
    lines.append("FILE COUNTS BY EXTENSION (all files, not just video)")
    lines.append("-" * 70)
    for ext, count in sorted(result["ext_counts"].items(), key=lambda x: -x[1]):
        is_video = " <- VIDEO" if ext in VIDEO_EXTENSIONS else ""
        lines.append(f"  {ext or '(no extension)':15s} {count:>8d}{is_video}")
    lines.append("")

    video_total = sum(c for e, c in result["ext_counts"].items() if e in VIDEO_EXTENSIONS)
    lines.append(f"TOTAL VIDEO FILES (across all subfolders): {video_total}")
    lines.append("")

    lines.append("-" * 70)
    lines.append("TOP-LEVEL SUBFOLDER BREAKDOWN")
    lines.append("-" * 70)
    lines.append("(This is the most useful section -- look here first to see if")
    lines.append(" the data is organised into folders you recognise, e.g. a")
    lines.append(" specific 'locomotion' or 'RHTSI' or project-named folder,")
    lines.append(" versus one large undifferentiated pile.)")
    lines.append("")

    sorted_folders = sorted(result["folder_total"].items(), key=lambda x: -x[1])
    for folder, total in sorted_folders:
        video_count = sum(c for e, c in result["folder_counts"][folder].items() if e in VIDEO_EXTENSIONS)
        lines.append(f"  {folder:40s} {total:>7d} files total  ({video_count} video)")

    lines.append("")
    lines.append("-" * 70)
    lines.append("NEXT STEP")
    lines.append("-" * 70)
    lines.append("If one or two subfolders clearly correspond to the locomotion")
    lines.append("project (e.g. matching what Zhi or Muhammad described), re-run")
    lines.append("video_inventory.py pointed at just that subfolder, rather than")
    lines.append("the whole directory. This avoids spending hours probing footage")
    lines.append("that turns out to be unrelated to this project.")

    output = "\n".join(lines)
    print(output)

    with open("folder_scan_summary.txt", "w") as f:
        f.write(output)
    print(f"\n(Also saved to folder_scan_summary.txt)")


if __name__ == "__main__":
    main()