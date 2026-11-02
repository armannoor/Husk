#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""
Write the two APKs tools/renpy-prepare-test.c needs, without a Ren'Py game.

    make-fake-renpy-apk.py <renpy.apk> <plain.apk>

The first has the layout every Ren'Py Android build has: assets/private.mp3
is a gzipped tar of main.py, renpy/ and lib/python3.12; lib/arm64-v8a has
librenpython.so. The second has none of that, so it must not be detected.
"""
import io
import sys
import tarfile
import zipfile


def tar_gz(files):
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w") as t:
        for name, data in files.items():
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mode = 0o644
            t.addfile(info, io.BytesIO(data))
    import gzip
    return gzip.compress(raw.getvalue())


def main():
    if len(sys.argv) != 3:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    renpy_apk, plain_apk = sys.argv[1], sys.argv[2]

    payload = tar_gz({
        "main.py": b"# RENPY_MAIN_MARKER\nimport renpy\nrenpy.main()\n",
        "renpy/__init__.py": b"# renpy package\n",
        "lib/python3.12/os.py": b"# PYTHON_STDLIB_MARKER\n",
        "lib/python3.12/lib-dynload/README": b"# extension modules live here\n",
    })
    with zipfile.ZipFile(renpy_apk, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("AndroidManifest.xml", b"\x03\x00\x08\x00")   # binary XML is not needed by prepare
        z.writestr("assets/private.mp3", payload)
        z.writestr("lib/arm64-v8a/librenpython.so", b"\x7fELF")

    with zipfile.ZipFile(plain_apk, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("AndroidManifest.xml", b"\x03\x00\x08\x00")
        z.writestr("classes.dex", b"dex\n035\0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
