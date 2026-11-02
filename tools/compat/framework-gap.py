#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""
Report the android.* (and javax.microedition.khronos.*, dalvik.system.*) classes
and members an APK references that a boot class path does not define.

    framework-gap.py --boot java-runtime --framework husk-framework.dex app.apk...

The boot directory is searched recursively for .jar files (the same jars ART's
boot class path uses: core-oj, core-libart, core-icu4j, conscrypt, ...). The
framework dex is built from src/java-framework. Exit status is 0 even when gaps
are found: this is a report, and CI prints it into the log.
"""
import argparse
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_source = open(os.path.join(HERE, "javagap.py"), encoding="utf-8").read().split("def main")[0]
_g = {}
exec(_source, _g)
dexes = _g["dexes"]
OBJECT_METHODS = _g["OBJECT_METHODS"]
OBJECT_FIELDS = _g["OBJECT_FIELDS"]

FW = ("Landroid/", "Ljavax/microedition/khronos/", "Ldalvik/system/")


def has(boot, cls, member, field):
    seen = set()
    todo = [cls]
    while todo:
        c = todo.pop()
        if c in seen or c is None:
            continue
        seen.add(c)
        info = boot.get(c)
        if not info:
            if c == "Ljava/lang/Object;":
                return ((member in OBJECT_FIELDS) if field else (member in OBJECT_METHODS))
            if c.startswith("Ljava/") or (c.startswith("Ljavax/") and not c.startswith("Ljavax/microedition/")):
                return True
            continue
        sup, ifs, meths, fields = info
        if ((member in fields) if field else (member in meths)):
            return True
        todo.append(sup)
        todo.extend(ifs)
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", required=True, help="directory with the boot jars")
    ap.add_argument("--framework", required=True, help="husk-framework.dex built from src/java-framework")
    ap.add_argument("apks", nargs="+")
    args = ap.parse_args()

    jars = sorted(glob.glob(os.path.join(args.boot, "**", "*.jar"), recursive=True))
    boot = {}
    for p in jars + [args.framework]:
        for d in dexes(p):
            boot.update(d.classes())
    print("boot: %d jars + the framework dex = %d classes" % (len(jars), len(boot)))

    total_gaps = 0
    for apk in args.apks:
        own = {}
        app_dex = dexes(apk)
        for d in app_dex:
            own.update(d.classes())
        missing_cls, missing = set(), {}
        for d in app_dex:
            for i in range(d.nmeth):
                c, n, sig = d.method(i)
                if not c.startswith(FW) or c in own:
                    continue
                if c not in boot:
                    missing_cls.add(c)
                    continue
                if not has(boot, c, n + sig, False):
                    missing.setdefault(c, set()).add(n + sig)
            for i in range(d.nfield):
                c, n, ty = d.field(i)
                if not c.startswith(FW) or c in own:
                    continue
                if c not in boot:
                    missing_cls.add(c)
                    continue
                if not has(boot, c, n, True):
                    missing.setdefault(c, set()).add(n + ":" + ty)
            for i in range(d.ntype):
                c = d.t(i)
                if c.startswith(FW) and c not in own and c not in boot:
                    missing_cls.add(c)
        members = sum(len(v) for v in missing.values())
        total_gaps += len(missing_cls) + members
        print("%s: %d classes missing, %d present classes lacking members"
              % (os.path.basename(apk), len(missing_cls), len(missing)))
        for c in sorted(missing_cls):
            print("  class  ", c)
        for c in sorted(missing):
            for m in sorted(missing[c]):
                print("  member ", c, m)
    print("total gaps:", total_gaps)
    return 0


if __name__ == "__main__":
    sys.exit(main())
