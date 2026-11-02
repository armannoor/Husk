"""Loaded through PYTHONPATH as sitecustomize.py while a Ren'Py APK runs under
the Java-app harness. Prints the loader state that decides whether the common
module _errorhandling can be found, before Ren'Py aborts on it.

Only methods of renpy.script.Script are replaced. Ren'Py's import_all pickles
each renpy module for its reload support, and a module-level function attribute
that is a local closure cannot be pickled -- which aborts bootstrap. A class is
pickled by reference, so patching its methods is safe.
"""

import builtins
import importlib
import sys

print("HUSK_DIAG sitecustomize loaded", file=sys.stderr, flush=True)

try:
    import os as _os

    print(
        "HUSK_DIAG startup cwd=%r private=%r apk=%r no_site=%r path0=%r"
        % (
            _os.getcwd(),
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


def _patch_script(script):
    if getattr(script, "_husk_diag", False):
        return
    script._husk_diag = True

    orig_scan = script.Script.scan_script_files

    def scan_script_files(self):
        import renpy as _r

        loader = _r.loader

        _diag(
            "scan_script_files android=%r renpy_base=%r basedir=%r gameapk=%r",
            getattr(_r, "android", None),
            getattr(_r.config, "renpy_base", None),
            getattr(_r.config, "basedir", None),
            getattr(_r.config, "renpy_base", None) == getattr(_r.config, "basedir", None),
        )
        _diag(
            "loader apks=%d prefixes=%r common=%d game=%d",
            len(loader.apks),
            [getattr(a, "prefix", None) for a in loader.apks],
            len(loader.common_files),
            len(loader.game_files),
        )

        rv = orig_scan(self)

        _diag(
            "module_files=%d has_eh=%r scripts=%d common_scripts=%d",
            len(self.module_files),
            any(n == "_errorhandling" for n, _ in self.module_files),
            len(self.script_files),
            len(self.common_script_files),
        )
        _diag("modules=%r", [n for n, _ in self.module_files][:12])
        _diag("game_scripts=%r", [n for n, _ in self.script_files][:8])
        _diag("common_files[:3]=%r", loader.common_files[:3])
        try:
            _diag("loadable eh=%r common=%r", loader.loadable("_errorhandling.rpymc"), loader.loadable("common/_errorhandling.rpymc"))
        except Exception as e:
            _diag("loadable probe failed: %r", e)
        return rv

    script.Script.scan_script_files = scan_script_files

    orig_load_module = script.Script.load_module

    def load_module(self, name):
        files = [(fn, dir) for fn, dir in self.module_files if fn == name]
        _diag("load_module(%r) files=%r", name, files[:4])
        if not files:
            _diag("module_files=%r", [n for n, _ in self.module_files][:20])
            import renpy as _r

            _diag("loader.common_files=%d apks=%d", len(_r.loader.common_files), len(_r.loader.apks))
        return orig_load_module(name)

    script.Script.load_module = load_module


def _after(name, module):
    if name == "renpy.script":
        try:
            _patch_script(module)
        except Exception as e:
            _diag("patch script failed: %r", e)


# Ren'Py imports its modules through importlib (not builtins.__import__), so the
# hook sits on importlib._bootstrap._find_and_load.
_bootstrap = importlib._bootstrap
_real_find_and_load = _bootstrap._find_and_load


def _find_and_load(name, import_):
    module = _real_find_and_load(name, import_)
    if name == "renpy.script":
        _after(name, module)
    return module


_bootstrap._find_and_load = _find_and_load

# Keep the builtins hook too, for imports that reach __import__ directly.
_real_import = builtins.__import__


def _hook(name, globals=None, locals=None, fromlist=(), level=0):
    module = _real_import(name, globals, locals, fromlist, level)

    if name == "renpy.script" or (name == "renpy" and fromlist and "script" in fromlist):
        _after("renpy.script", sys.modules["renpy.script"])

    return module


builtins.__import__ = _hook
