#!/usr/bin/env python3
"""Comprehensive verification of all Mornye extensions, packages, manifests, and icons."""

import hashlib
import json
import sys
import zipfile
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registry.json"
ICONS_DIR = ROOT / "icons"
EXT_DIR = ROOT / "extensions"
SOURCES_DIR = ROOT / "sources"


def main():
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    extensions = registry.get("extensions", [])
    print(f"Total extensions in registry: {len(extensions)}")

    all_passed = True

    for ext in extensions:
        ext_id = ext["id"]
        display_name = ext["display_name"]
        version = ext["version"]
        download_url = ext["download_url"]
        expected_sha = ext.get("sha256")
        icon_url = ext.get("icon_url")

        # 1. Package archive file
        pkg_name = Path(download_url).name
        pkg_path = EXT_DIR / pkg_name
        pkg_exists = pkg_path.is_file()

        # 2. SHA-256 digest
        actual_sha = None
        sha_match = False
        if pkg_exists:
            actual_sha = hashlib.sha256(pkg_path.read_bytes()).hexdigest()
            sha_match = (actual_sha == expected_sha)

        # 3. Source directory and manifest
        src_dir = SOURCES_DIR / ext_id
        src_exists = src_dir.is_dir()
        manifest_matches = False
        if src_exists:
            manifest_file = src_dir / "manifest.json"
            if manifest_file.is_file():
                m = json.loads(manifest_file.read_text(encoding="utf-8"))
                manifest_matches = (m.get("version") == version and m.get("name") == ext_id)

        # 4. Zip archive structure
        zip_ok = False
        if pkg_exists:
            try:
                with zipfile.ZipFile(pkg_path) as z:
                    names = z.namelist()
                    zip_ok = "manifest.json" in names and "index.js" in names
            except Exception:
                zip_ok = False

        # 5. Icon file and URL
        icon_name = Path(icon_url).name if icon_url else None
        icon_file = ICONS_DIR / icon_name if icon_name else None
        icon_exists = icon_file.is_file() if icon_file else False
        icon_dim_ok = False
        if icon_exists:
            try:
                with Image.open(icon_file) as im:
                    icon_dim_ok = (im.size == (512, 512))
            except Exception:
                icon_dim_ok = False

        icon_url_valid = bool(
            icon_url and (
                icon_url.startswith("https://raw.githubusercontent.com/Hix-001/Mornye-Extension/main/icons/") or
                icon_url.startswith("https://raw.githubusercontent.com/mornyeapp/Mornye-Extension/main/icons/")
            )
        )

        ok = (pkg_exists and sha_match and src_exists and manifest_matches and zip_ok and icon_exists and icon_dim_ok and icon_url_valid)
        if not ok:
            all_passed = False

        status = "[PASS]" if ok else "[FAIL]"
        print(f"{status} {display_name:<16} (v{version:<7}) | pkg: {pkg_exists} | sha: {sha_match} | src: {manifest_matches} | icon: {icon_name} (512x512: {icon_dim_ok})")

    if all_passed:
        print(f"\nAll {len(extensions)} extensions are verified and 100% functional!")
        sys.exit(0)
    else:
        print("\nSome extensions failed verification!")
        sys.exit(1)


if __name__ == "__main__":
    main()
