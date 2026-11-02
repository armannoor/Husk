#!/bin/bash
# build.sh <out.dex> -- Husk's Java framework (android.* for apps run on Husk's Dalvik runtime): javac, then d8.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
JDK="${HUSK_JDK:-/Volumes/GTAV/husk2/tools-dl/jdk/Contents/Home}"
D8="${HUSK_D8:-/Volumes/GTAV/husk2/tools-dl/r8.jar}"   # R8 8.5+: the d8 in build-tools 34 crashes on these classes
OUT="${1:-$HERE/../../build/husk-framework.dex}"
TMP="$(mktemp -d)"
python3 "$HERE/gen/gles20.py" "$HERE/src/android/opengl" "$HERE/../translation-layer-next/husk-tl-dvm-gles20.c" >/dev/null
# libcore's own classes that javac's JDK does not have (org.xmlpull): compiled to build against, not put in the dex
"$JDK/bin/javac" -nowarn --release 8 -encoding UTF-8 -d "$TMP/stubs" $(find "$HERE/stubs" -name '*.java')
# An argument file: the 3,000-odd sources exceed the Windows command line limit.
# cygpath (MSYS/Git Bash) turns the paths into the ones the Windows javac reads.
find "$HERE/src" "$HERE/gen-src" -name '*.java' > "$TMP/sources.txt"
ARGS="$TMP/sources.txt"
if command -v cygpath >/dev/null 2>&1; then
    while IFS= read -r f; do cygpath -w "$f"; done < "$TMP/sources.txt" > "$TMP/sources-win.txt"
    ARGS="$(cygpath -w "$TMP/sources-win.txt")"
fi
if ! "$JDK/bin/javac" -nowarn --release 8 -encoding UTF-8 -Xmaxerrs 100000 -cp "$TMP/stubs" -d "$TMP/classes" "@$ARGS" 2> "$TMP/javac.log"; then
    grep -v "^Note:" "$TMP/javac.log" > "${JAVAC_LOG:-/dev/stderr}"; echo "javac failed" >&2; exit 1
fi
(cd "$TMP/classes" && "$JDK/bin/jar" cf "$TMP/classes.jar" .)
"$JDK/bin/java" -cp "$D8" com.android.tools.r8.D8 --min-api 26 --output "$TMP" "$TMP/classes.jar"
mkdir -p "$(dirname "$OUT")"
mv "$TMP/classes.dex" "$OUT"

# Core dex: handwritten src/ only (and nested types of those classes). Generated
# gen-src stubs stay out so AOSP framework.jar can define them when it is on the
# boot path. Nested stubs of a handwritten outer class stay here so Activity$Foo
# still matches Husk's Activity.
CORE="${OUT%.dex}-core.dex"
python3 - "$HERE/src" "$TMP/classes" "$TMP/core-classes" <<'PY'
import os, shutil, sys
src, classes, dest = sys.argv[1:4]
os.makedirs(dest, exist_ok=True)
kept = 0
for dirpath, _, files in os.walk(classes):
    for name in files:
        if not name.endswith(".class"):
            continue
        rel = os.path.relpath(os.path.join(dirpath, name), classes)
        outer = rel[:-6].split("$", 1)[0]
        if os.path.isfile(os.path.join(src, outer + ".java")):
            out = os.path.join(dest, rel)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            shutil.copy2(os.path.join(dirpath, name), out)
            kept += 1
print(kept)
PY
(cd "$TMP/core-classes" && "$JDK/bin/jar" cf "$TMP/core.jar" .)
mkdir -p "$TMP/core-out"
"$JDK/bin/java" -cp "$D8" com.android.tools.r8.D8 --min-api 26 --output "$TMP/core-out" "$TMP/core.jar"
mv "$TMP/core-out/classes.dex" "$CORE"
rm -rf "$TMP"
echo "built $OUT"
echo "built $CORE"
