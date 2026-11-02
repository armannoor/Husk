#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""
missing-symbols.py <apk> [<apk> ...] -- what an APK's arm64 libraries import that
Husk's bionic/NDK shim does not provide.

Reads the tables the loader is built from (TL_WRAP/TL_DATA/TL_DIRECT in
src/translation-layer-next/husk-tl-bionic*.c), adds what ANGLE/MoltenVK resolve
by name (gl*/egl*/vk*), and compares against the undefined symbols of every
lib/arm64-v8a/*.so in the APK. The output is grouped by category and library,
which is the list of functions to implement next.
"""
import os
import re
import struct
import sys
import zipfile
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
TL = os.path.join(ROOT, 'src', 'translation-layer-next')


def provided():
    """Every symbol name the loader binds itself."""
    names = set()
    for fn in os.listdir(TL):
        if not (fn.startswith('husk-tl-') and fn.endswith('.c')):
            continue
        text = open(os.path.join(TL, fn), errors='replace').read()
        for m in re.finditer(r'TL_(?:WRAP|DATA|DIRECT)\(\s*(?:"([^"]+)"|([A-Za-z_]\w*))', text):
            names.add(m.group(1) or m.group(2))
        # tables that use a local macro: SLID(SL_IID_PLAY) in husk-tl-opensles.c
        for m in re.finditer(r'\bSLID\(\s*([A-Za-z_]\w*)\s*\)', text):
            names.add(m.group(1))
    names.update({'__cxa_atexit', '__cxa_finalize', '__register_atfork'})
    return names


def elf_undefined(data):
    """(undefined global/weak symbol names, defined symbol names) of an ELF64 file."""
    if data[:4] != b'\x7fELF' or data[4] != 2:
        return set(), set()
    little = data[5] == 1
    e = '<' if little else '>'
    e_shoff, = struct.unpack_from(e + 'Q', data, 0x28)
    e_shentsize, e_shnum, e_shstrndx = struct.unpack_from(e + 'HHH', data, 0x3a)
    shstr = b''
    if e_shnum:
        off = e_shoff + e_shstrndx * e_shentsize
        nameoff, _, _, _, sh_offset, sh_size = struct.unpack_from(e + 'IIQQQQ', data, off)
        shstr = data[sh_offset:sh_offset + sh_size]
    undef, defined = set(), set()
    for i in range(e_shnum):
        off = e_shoff + i * e_shentsize
        nameoff, sh_type, _, _, sh_offset, sh_size, sh_link, _, _, sh_entsize = struct.unpack_from(e + 'IIQQQQIIQQ', data, off)
        nm = shstr[nameoff:shstr.find(b'\0', nameoff)].decode('utf-8', 'replace')
        if sh_type != 11 or nm not in ('.dynsym',):   # SHT_DYNSYM
            continue
        if not e_shnum or not sh_link:
            continue
        soff = e_shoff + sh_link * e_shentsize
        _, _, _, _, str_off, str_size = struct.unpack_from(e + 'IIQQQQ', data, soff)
        strs = data[str_off:str_off + str_size]
        for j in range(sh_size // (sh_entsize or 24)):
            st_name, st_info, st_other, st_shndx = struct.unpack_from(e + 'IBBH', data, sh_offset + j * sh_entsize)
            if st_name == 0:
                continue
            name = strs[st_name:strs.find(b'\0', st_name)].decode('utf-8', 'replace')
            bind = st_info >> 4
            if bind not in (1, 2):    # GLOBAL, WEAK
                continue
            if st_shndx == 0:
                undef.add(name)
            else:
                defined.add(name)
    return undef, defined


def category(name):
    if name.startswith(('_Z', '__cxa_', '_Unwind_', '__gxx_', '__dynamic_cast', '__cxa')):
        return 'C++ / unwinder'
    if name.startswith(('gl', 'egl', 'vk', 'ANativeWindow_', 'EGL_', 'GLES')):
        return 'GL / EGL / Vulkan / window'
    if name.startswith(('A', 'ASensor', 'AAudio', 'AMedia', 'AImage', 'ACamera', 'AInput', 'AKey', 'AMotion', 'AStorage', 'AThermal')):
        return 'NDK (libandroid / mediandk / camera2 / sensors)'
    if name.startswith(('pthread_', 'sem_', 'mtx_', 'cnd_', 'thrd_', '__pthread')):
        return 'pthread'
    if name.startswith('__android_log'):
        return 'log'
    if name.startswith(('SL',)):
        return 'OpenSL ES'
    if name.startswith(('dl', 'android_dl')):
        return 'dl'
    if name.startswith(('__', '_', 'str', 'mem', 'wcs', 'mb', 'iconv', 'printf', 'scanf')):
        return 'libc / libc++ ABI'
    return 'other libc / libm / libz'


def main():
    apks = [a for a in sys.argv[1:] if not a.startswith('-')]
    if not apks:
        print(__doc__)
        return 2
    known = provided()
    total = defaultdict(set)
    for apk in apks:
        try:
            z = zipfile.ZipFile(apk)
        except Exception as e:
            print('%s: %s' % (apk, e))
            continue
        libs = [n for n in z.namelist() if re.match(r'lib/arm64-v8a/.*\.so$', n)]
        if not libs:
            libs = [n for n in z.namelist() if n.endswith('.so') and '/arm64-v8a/' in n]
        print('== %s: %d arm64 libraries' % (os.path.basename(apk), len(libs)))
        # A symbol the app's other libraries define is not Husk's to provide: the
        # loader binds it in the importing library's DT_NEEDED scope first.
        undefs, app_defined = {}, set()
        for name in sorted(libs):
            u, d = elf_undefined(z.read(name))
            undefs[name] = u
            app_defined |= d
        for name in sorted(libs):
            undef = undefs[name]
            miss = {s for s in undef if s not in known and s not in app_defined and not s.startswith(('gl', 'egl', 'vk'))}
            for s in miss:
                total[category(s)].add(s)
            if miss:
                bycat = defaultdict(list)
                for s in miss:
                    bycat[category(s)].append(s)
                print('  %-40s %4d undefined, %4d missing' % (name.split('/')[-1], len(undef), len(miss)))
                for c in sorted(bycat, key=lambda k: -len(bycat[k])):
                    print('      %-45s %4d  %s' % (c, len(bycat[c]), ', '.join(sorted(bycat[c])[:8])))
    print()
    print('== what to implement, by category')
    for c in sorted(total, key=lambda k: -len(total[k])):
        print('%-45s %4d' % (c, len(total[c])))
        print('    ' + ', '.join(sorted(total[c])[:40]))
    return 0


if __name__ == '__main__':
    sys.exit(main())
