"""Imported as sitecustomize while a Ren'Py APK runs under the Java-app
harness. Prints the loader state that decides whether the common module
_errorhandling can be found, before Ren'Py aborts on it."""

import builtins
import sys

print("HUSK_DIAG sitecustomize loaded", file=sys.stderr, flush=True)

_real_import = builtins.__import__
_patched = set()


def _patch_loader(loader):
    if "loader" in _patched:
        return
    _patched.add("loader")

    orig_find = loader.find_apks

    def find_apks():
        import renpy as _r

        print(
            "HUSK_DIAG pre find_apks renpy_base=%r basedir=%r android=%r private=%r apk=%r"
            % (
                getattr(_r.config, "renpy_base", None),
                getattr(_r.config, "basedir", None),
                getattr(_r, "android", None),
                __import__("os").environ.get("ANDROID_PRIVATE"),
                __import__("os").environ.get("ANDROID_APK"),
            ),
            file=sys.stderr,
            flush=True,
        )
        orig_find()
        print(
            "HUSK_DIAG find_apks apks=%d prefixes=%r"
            % (len(loader.apks), [getattr(a, "prefix", None) for a in loader.apks]),
            file=sys.stderr,
            flush=True,
        )

    loader.find_apks = find_apks

    orig_scan = loader.scandirfiles_from_apk

    def scan(add, seen):
        orig_scan(add, seen)
        print(
            "HUSK_DIAG scan_apk common=%d game=%d errorhandling=%r first_common=%r"
            % (
                len(loader.common_files),
                len(loader.game_files),
                any(n == "_errorhandling.rpymc" for _, n in loader.common_files),
                loader.common_files[:3],
            ),
            file=sys.stderr,
            flush=True,
        )

    loader.scandirfiles_callbacks = [scan if c is orig_scan else c for c in loader.scandirfiles_callbacks]


def _patch_script(script):
    if "script" in _patched:
        return
    _patched.add("script")

    orig_scan = script.Script.scan_script_files

    def scan_script_files(self):
        orig_scan(self)
        print(
            "HUSK_DIAG scan_script module_files=%d errorhandling=%r common_scripts=%d scripts=%d"
            % (
                len(self.module_files),
                any(n == "_errorhandling" for n, _ in self.module_files),
                len(self.common_script_files),
                len(self.script_files),
            ),
            file=sys.stderr,
            flush=True,
        )

    script.Script.scan_script_files = scan_script_files


def _hook(name, globals=None, locals=None, fromlist=(), level=0):
    module = _real_import(name, globals, locals, fromlist, level)

    if name == "renpy.loader" or (name == "renpy" and fromlist and "loader" in fromlist):
        loader = sys.modules.get("renpy.loader")
        if loader is not None:
            _patch_loader(loader)

    if name == "renpy.script" or (name == "renpy" and fromlist and "script" in fromlist):
        script = sys.modules.get("renpy.script")
        if script is not None:
            _patch_script(script)

    return module


builtins.__import__ = _hook
