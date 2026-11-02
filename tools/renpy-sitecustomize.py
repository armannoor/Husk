"""Loaded through PYTHONPATH as sitecustomize.py while a Ren'Py APK runs under
the Java-app harness. Prints the loader state that decides whether the common
module _errorhandling can be found, before Ren'Py aborts on it.

Ren'Py imports its modules through importlib (not builtins.__import__), so the
hook sits on importlib._bootstrap._find_and_load as well."""

import builtins
import importlib
import sys

print("HUSK_DIAG sitecustomize loaded", file=sys.stderr, flush=True)

try:
    import os as _os

    print(
        "HUSK_DIAG startup cwd=%r file=%r private=%r apk=%r no_site=%r path0=%r"
        % (
            _os.getcwd(),
            globals().get("__file__"),
            _os.environ.get("ANDROID_PRIVATE"),
            _os.environ.get("ANDROID_APK"),
            sys.flags.no_site,
            sys.path[:4],
        ),
        file=sys.stderr,
        flush=True,
    )
except Exception as _e:  # noqa: BLE001
    print("HUSK_DIAG startup probe failed: %r" % (_e,), file=sys.stderr, flush=True)


def _diag(msg, *args):
    try:
        sys.stderr.write("HUSK_DIAG " + (msg % args if args else msg) + "\n")
        sys.stderr.flush()
    except Exception:
        pass


def _patch_loader(loader):
    if getattr(loader, "_husk_diag", False):
        return
    loader._husk_diag = True

    orig_find = loader.find_apks

    def find_apks():
        import os

        import renpy as _r

        _diag(
            "pre find_apks renpy_base=%r basedir=%r android=%r private=%r apk=%r",
            getattr(_r.config, "renpy_base", None),
            getattr(_r.config, "basedir", None),
            getattr(_r, "android", None),
            os.environ.get("ANDROID_PRIVATE"),
            os.environ.get("ANDROID_APK"),
        )
        rv = orig_find()
        _diag(
            "post find_apks apks=%d prefixes=%r game_apks=%d",
            len(loader.apks),
            [getattr(a, "prefix", None) for a in loader.apks],
            len(loader.game_apks),
        )
        return rv

    loader.find_apks = find_apks

    orig_scan = getattr(loader, "scandirfiles_from_apk", None)

    if orig_scan is not None:

        def scandirfiles_from_apk(add, seen):
            orig_scan(add, seen)
            _diag(
                "scan_apks common=%d game=%d has_eh=%r first=%r",
                len(loader.common_files),
                len(loader.game_files),
                any(n == "_errorhandling.rpymc" for _, n in loader.common_files),
                loader.common_files[:2],
            )

        loader.scandirfiles_callbacks = [
            scandirfiles_from_apk if c is orig_scan else c
            for c in loader.scandirfiles_callbacks
        ]

    orig_index = loader.index_files

    def index_files():
        _diag(
            "index_files callbacks=%r",
            [getattr(c, "__name__", c) for c in loader.scandirfiles_callbacks],
        )
        rv = orig_index()
        _diag(
            "index_files done common=%d game=%d apks=%d",
            len(loader.common_files),
            len(loader.game_files),
            len(loader.apks),
        )
        return rv

    loader.index_files = index_files


def _patch_script(script):
    if getattr(script, "_husk_diag", False):
        return
    script._husk_diag = True

    orig_scan = script.Script.scan_script_files

    def scan_script_files(self):
        rv = orig_scan(self)
        import renpy as _r

        _diag(
            "scan_script_files common_files=%d module_files=%d has_eh=%r scripts=%d common_scripts=%d",
            len(_r.loader.common_files),
            len(self.module_files),
            any(n == "_errorhandling" for n, _ in self.module_files),
            len(self.script_files),
            len(self.common_script_files),
        )
        _diag("modules=%r", [n for n, _ in self.module_files][:12])
        _diag("game_scripts=%r", [n for n, _ in self.script_files][:8])
        _diag("loadable eh=%r", _r.loader.loadable("_errorhandling.rpymc"))
        return rv

    script.Script.scan_script_files = scan_script_files

    orig_load_module = script.Script.load_module

    def load_module(self, name):
        files = [(fn, dir) for fn, dir in self.module_files if fn == name]
        _diag("load_module(%r) files=%r", name, files[:4])
        if not files:
            _diag("module_files=%r", [n for n, _ in self.module_files][:20])
            _diag("loader.common_files=%d", len(__import__("renpy").loader.common_files))
        return orig_load_module(name)

    script.Script.load_module = load_module


def _after(name, module):
    if name == "renpy.loader":
        _patch_loader(module)
    elif name == "renpy.script":
        _patch_script(module)


# Ren'Py's import_all and its _LibExecFinder go through importlib; wrap the
# function every import path in CPython's bootstrap ends up calling.
_bootstrap = importlib._bootstrap
_real_find_and_load = _bootstrap._find_and_load


def _find_and_load(name, import_):
    module = _real_find_and_load(name, import_)
    if name == "renpy.loader" or name == "renpy.script":
        _after(name, module)
    return module


_bootstrap._find_and_load = _find_and_load

# Keep the builtins hook too: it catches IMPORTS that reach __import__ directly.
_real_import = builtins.__import__


def _hook(name, globals=None, locals=None, fromlist=(), level=0):
    module = _real_import(name, globals, locals, fromlist, level)

    if name == "renpy.loader" or (name == "renpy" and fromlist and "loader" in fromlist):
        _patch_loader(sys.modules["renpy.loader"])
    if name == "renpy.script" or (name == "renpy" and fromlist and "script" in fromlist):
        _patch_script(sys.modules["renpy.script"])

    return module


builtins.__import__ = _hook
