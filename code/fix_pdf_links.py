#!/usr/bin/env python3
"""Fix broken links between local PDFs exported by VS Code's Markdown PDF extension.

The extension writes links to other local files into the PDF in the form

    file:///e%3A/GitHub/Clustering-Women-Players-Europe-2324/findings/...

(lowercase drive letter, colon written as %3A). Windows cannot open that form
("Windows cannot find ..."). This script rewrites only that drive prefix:

    file:///E:/GitHub/Clustering-Women-Players-Europe-2324/findings/...

Everything else in the PDF (text, images, in-page links, table of contents,
links to websites) is left exactly as it was.

Usage:
    python fix_pdf_links.py PATH [PATH ...] [--dry-run]

Two-folder workflow (export from findings_pdf, keep the finished PDFs in findings):
    python fix_pdf_links.py findings_pdf --map findings_pdf=findings --out findings

  --map OLD=NEW  also rewrites the folder name inside every link (/OLD/ -> /NEW/), so links in a PDF that
                 was exported from OLD point at the copies that will live in NEW.
  --out DIR      write the fixed PDFs into DIR (same sub-folders as under the single input folder)
                 instead of overwriting them in place.

PATH is a PDF file or a folder (searched recursively for *.pdf).
--dry-run only reports what would change.

Requires:  pip install pypdf

Notes:
  * Close the PDFs in your viewer first, or Windows will refuse to overwrite them.
  * The exporter bakes in the absolute path of the folder you exported from.
    If you move or rename that folder, export again and re-run this script.
"""
import argparse
import os
import re
import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, TextStringObject

# file:///e%3A/...  ->  file:///E:/...
BROKEN = re.compile(r"^file:///([A-Za-z])%3[Aa]/")


def fix_uri(uri: str, folder_map=None) -> str:
    uri = BROKEN.sub(lambda m: f"file:///{m.group(1).upper()}:/", uri)
    if folder_map and uri.lower().startswith("file:///"):
        old, new = folder_map
        uri = re.sub("/" + re.escape(old) + "/", "/" + new + "/", uri, flags=re.IGNORECASE)
    return uri


def process(path: Path, dry_run: bool, folder_map=None, dest=None) -> int:
    """Return how many links were (or would be) fixed in this PDF."""
    reader = PdfReader(str(path))
    writer = PdfWriter(clone_from=reader)

    fixed = 0
    for page in writer.pages:
        annots = page.get("/Annots")
        if annots is None:
            continue
        for ref in annots.get_object():
            annot = ref.get_object()
            action = annot.get("/A")
            if action is None:
                continue
            action = action.get_object()
            if action.get("/S") != "/URI":
                continue
            old = str(action.get("/URI", ""))
            new = fix_uri(old, folder_map)
            if new != old:
                action[NameObject("/URI")] = TextStringObject(new)
                fixed += 1

    if dest is not None and not dry_run:
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_name(dest.name + ".tmp")
        with open(tmp, "wb") as f:
            writer.write(f)
        try:
            os.replace(tmp, dest)
        except PermissionError:
            tmp.unlink(missing_ok=True)
            raise PermissionError(f"Could not overwrite {dest.name}. Close it in your PDF viewer and run again.")
    elif fixed and not dry_run:
        tmp = path.with_name(path.name + ".tmp")
        with open(tmp, "wb") as f:
            writer.write(f)
        try:
            os.replace(tmp, path)
        except PermissionError:
            tmp.unlink(missing_ok=True)
            raise PermissionError(
                f"Could not overwrite {path.name}. Close it in your PDF viewer and run again."
            )
    return fixed


def find_pdfs(paths):
    for p in map(Path, paths):
        if p.is_dir():
            yield from sorted(p.rglob("*.pdf"))
        elif p.suffix.lower() == ".pdf" and p.exists():
            yield p
        else:
            print(f"skipped (not a PDF or folder that exists): {p}", file=sys.stderr)


def main() -> int:
    ap = argparse.ArgumentParser(description="Fix file:///e%3A/... links in exported PDFs.")
    ap.add_argument("paths", nargs="+", help="PDF files or folders")
    ap.add_argument("--dry-run", action="store_true", help="report only, change nothing")
    ap.add_argument("--map", metavar="OLD=NEW", help="rename a folder inside the links, e.g. findings_pdf=findings")
    ap.add_argument("--out", metavar="DIR", help="write fixed PDFs here (needs exactly one input folder)")
    args = ap.parse_args()
    folder_map = tuple(args.map.split("=", 1)) if args.map else None
    if args.map and (folder_map is None or len(folder_map) != 2 or not all(folder_map)):
        ap.error("--map needs OLD=NEW")
    root = None
    if args.out:
        if len(args.paths) != 1 or not Path(args.paths[0]).is_dir():
            ap.error("--out needs exactly one input folder")
        root, out_root = Path(args.paths[0]).resolve(), Path(args.out).resolve()
        if root == out_root:
            ap.error("--out must be a different folder from the input")

    total_files = total_links = 0
    errors = 0
    for pdf in find_pdfs(args.paths):
        try:
            dest = out_root / pdf.resolve().relative_to(root) if root else None
            n = process(pdf, args.dry_run, folder_map, dest)
        except Exception as e:  # keep going with the other files
            print(f"ERROR  {pdf.name}: {e}", file=sys.stderr)
            errors += 1
            continue
        verb = "would fix" if args.dry_run else "fixed"
        print(f"{pdf.name:60} {verb} {n} link(s)")
        total_files += 1
        total_links += n

    print(f"\n{total_files} PDF(s) checked, {total_links} link(s) {'to fix' if args.dry_run else 'fixed'}.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())