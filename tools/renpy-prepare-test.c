/* SPDX-License-Identifier: GPL-2.0-or-later */
/*
 * The Ren'Py half of the SDL driver, tested without a Ren'Py game.
 *
 *   renpy-prepare-test <apk> <data-dir>
 *
 * The APK only needs assets/private.mp3 (a gzipped tar, as python-for-android
 * and Ren'Py write it) and lib/arm64-v8a/librenpython.so. The test asserts
 * that tl_renpy_prepare() unpacks the archive where CPython expects it and
 * sets the environment PythonSDLActivity.preparePython() would have set.
 */
#include <errno.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

#include "husk-tl-internal.h"

bool tl_renpy_prepare(const char *apk, const char *data_dir, const char *package_name);

/* The runtime's log funnel; this test can stand alone. */
void tl_log_line(const char *fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    vfprintf(stderr, fmt, ap);
    va_end(ap);
    fputc('\n', stderr);
}

static int failures;

static void check(bool ok, const char *what)
{
    fprintf(stderr, "%s: %s\n", ok ? "ok  " : "FAIL", what);
    if (!ok) failures++;
}

static bool file_has(const char *path, const char *needle)
{
    char buf[4096];
    FILE *f = fopen(path, "rb");
    if (!f) return false;
    size_t n = fread(buf, 1, sizeof(buf) - 1, f);
    fclose(f);
    buf[n] = 0;
    return needle == NULL || strstr(buf, needle) != NULL;
}

int main(int argc, char **argv)
{
    if (argc != 3) {
        fprintf(stderr, "usage: %s <apk> <data-dir>\n", argv[0]);
        return 2;
    }
    const char *apk = argv[1], *data = argv[2];
    char files[1024], path[1200];

    check(tl_renpy_prepare(apk, data, "org.example.renpy"), "prepare returns true for a Ren'Py APK");

    snprintf(files, sizeof(files), "%s/files", data);
    snprintf(path, sizeof(path), "%s/main.py", files);
    check(file_has(path, "RENPY_MAIN_MARKER"), "main.py unpacked");
    snprintf(path, sizeof(path), "%s/renpy/__init__.py", files);
    check(file_has(path, NULL), "renpy/__init__.py unpacked");
    snprintf(path, sizeof(path), "%s/lib/python3.12/os.py", files);
    check(file_has(path, "PYTHON_STDLIB_MARKER"), "lib/python3.12/os.py unpacked");

    check(getenv("ANDROID_PRIVATE") && !strcmp(getenv("ANDROID_PRIVATE"), files), "ANDROID_PRIVATE points at files/");
    snprintf(path, sizeof(path), "%s/sdcard/Android/data/org.example.renpy/files", data);
    check(getenv("ANDROID_PUBLIC") && !strcmp(getenv("ANDROID_PUBLIC"), path), "ANDROID_PUBLIC points at the external files dir");
    snprintf(path, sizeof(path), "%s/sdcard/org.example.renpy", data);
    check(getenv("ANDROID_OLD_PUBLIC") && !strcmp(getenv("ANDROID_OLD_PUBLIC"), path), "ANDROID_OLD_PUBLIC points at the old layout");
    check(getenv("ANDROID_APK") && !strcmp(getenv("ANDROID_APK"), apk), "ANDROID_APK is the APK path");
    check(getenv("PYTHONHOME") && !strcmp(getenv("PYTHONHOME"), files), "PYTHONHOME is files/");
    check(getenv("PYTHONPATH") && strstr(getenv("PYTHONPATH"), "/lib/python3.12/lib-dynload"), "PYTHONPATH has lib-dynload");

    /* A second call must not re-unpack, but must still set the environment. */
    check(tl_renpy_prepare(apk, data, "org.example.renpy"), "prepare is idempotent");
    snprintf(path, sizeof(path), "%s/main.py", files);
    check(file_has(path, "RENPY_MAIN_MARKER"), "main.py survives the second call");

    fprintf(stderr, "%s\n", failures ? "renpy-prepare-test: FAILED" : "renpy-prepare-test: passed");
    return failures ? 1 : 0;
}
