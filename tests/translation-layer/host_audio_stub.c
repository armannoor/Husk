/* SPDX-License-Identifier: GPL-2.0-or-later */
/*
 * The app side of the translation layer, for the macOS host harness.
 *
 * The shipping app supplies these three from other translation units and from
 * Swift: the audio device (husk-tl-audio.c, which opens AudioToolbox), the
 * mixer hook it installs, and the JIT region reservation (husk-tl-xmem.c,
 * driven by the app's StikDebug window). The attempt harness only needs the
 * loader and the framework, so it links these no-ops instead.
 */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

void (*tl_cocos_audio_hook)(const int16_t *samples, int frames, int channels, int rate);

void tl_audio_install(void)
{
}

bool tl_jit_reserve_bottom(size_t end)
{
    (void)end;
    return true;
}
