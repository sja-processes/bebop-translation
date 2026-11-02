#!/usr/bin/env python3
"""Minimal headless libretro frontend (ctypes) for testing the ROM in the
same Nestopia core that RetroArch handhelds use (lr-nestopia).

    from lrnes import Core
    c = Core(rom_path)                      # default core path below
    c.run(300)                              # frames
    c.press('start', 5); c.run(100)
    c.frame_png('shot.png'); ram = c.ram()  # 2 KB internal RAM
    st = c.save(); c.load(st)

Only what's needed for testing: video capture, joypad 1 input, save
states and system RAM. Audio is discarded.
"""
import ctypes as C
import os

DEFAULT_CORE = os.path.expanduser('~/.config/retroarch/cores/nestopia_libretro.so')

# libretro constants
ENV_GET_CAN_DUPE = 3
ENV_SET_PIXEL_FORMAT = 10
ENV_GET_SYSTEM_DIRECTORY = 9
ENV_GET_VARIABLE = 15
ENV_GET_VARIABLE_UPDATE = 17
ENV_GET_SAVE_DIRECTORY = 31
PIXFMT_0RGB1555, PIXFMT_XRGB8888, PIXFMT_RGB565 = 0, 1, 2
MEMORY_SYSTEM_RAM = 2
BUTTONS = {'b': 0, 'y': 1, 'select': 2, 'start': 3, 'up': 4, 'down': 5,
           'left': 6, 'right': 7, 'a': 8}

ENV_CB = C.CFUNCTYPE(C.c_bool, C.c_uint, C.c_void_p)
VIDEO_CB = C.CFUNCTYPE(None, C.c_void_p, C.c_uint, C.c_uint, C.c_size_t)
AUDIO_CB = C.CFUNCTYPE(None, C.c_int16, C.c_int16)
AUDIO_BATCH_CB = C.CFUNCTYPE(C.c_size_t, C.c_void_p, C.c_size_t)
POLL_CB = C.CFUNCTYPE(None)
INPUT_CB = C.CFUNCTYPE(C.c_int16, C.c_uint, C.c_uint, C.c_uint, C.c_uint)


class GameInfo(C.Structure):
    _fields_ = [('path', C.c_char_p), ('data', C.c_void_p),
                ('size', C.c_size_t), ('meta', C.c_char_p)]


class Variable(C.Structure):
    _fields_ = [('key', C.c_char_p), ('value', C.c_char_p)]


class Core:
    def __init__(self, rom, core=DEFAULT_CORE, sysdir=None):
        self.lib = C.CDLL(core)
        self.pixfmt = PIXFMT_0RGB1555
        self.held = set()
        self._raw = None             # last video frame, unconverted
        self.frames = 0
        self._dir = C.c_char_p((sysdir or os.path.dirname(os.path.abspath(rom))).encode())
        # keep callbacks alive
        self._cbs = [ENV_CB(self._env), VIDEO_CB(self._video), AUDIO_CB(lambda l, r: None),
                     AUDIO_BATCH_CB(lambda d, n: n), POLL_CB(lambda: None),
                     INPUT_CB(self._input)]
        L = self.lib
        L.retro_set_environment(self._cbs[0])
        L.retro_set_video_refresh(self._cbs[1])
        L.retro_set_audio_sample(self._cbs[2])
        L.retro_set_audio_sample_batch(self._cbs[3])
        L.retro_set_input_poll(self._cbs[4])
        L.retro_set_input_state(self._cbs[5])
        L.retro_init()
        data = open(rom, 'rb').read()
        self._rom = C.create_string_buffer(data, len(data))
        info = GameInfo(os.path.abspath(rom).encode(), C.cast(self._rom, C.c_void_p),
                        len(data), None)
        if not L.retro_load_game(C.byref(info)):
            raise RuntimeError('core refused the ROM')
        L.retro_serialize_size.restype = C.c_size_t
        L.retro_get_memory_data.restype = C.c_void_p
        L.retro_get_memory_size.restype = C.c_size_t

    # --- callbacks -------------------------------------------------------
    def _env(self, cmd, data):
        if cmd == ENV_SET_PIXEL_FORMAT:
            self.pixfmt = C.cast(data, C.POINTER(C.c_int))[0]
            return True
        if cmd in (ENV_GET_SYSTEM_DIRECTORY, ENV_GET_SAVE_DIRECTORY):
            C.cast(data, C.POINTER(C.c_char_p))[0] = self._dir.value
            return True
        if cmd == ENV_GET_CAN_DUPE:
            C.cast(data, C.POINTER(C.c_bool))[0] = True
            return True
        if cmd == ENV_GET_VARIABLE_UPDATE:
            C.cast(data, C.POINTER(C.c_bool))[0] = False
            return True
        return False

    def _video(self, data, w, h, pitch):
        if data:                     # keep the raw frame; convert on demand
            self._raw = (C.string_at(data, pitch * h), w, h, pitch, self.pixfmt)

    @property
    def frame(self):
        """-> (width, height, RGB bytes) of the last video frame."""
        raw, w, h, pitch, fmt = self._raw
        out = bytearray(w * h * 3)
        for y in range(h):
            row = raw[y * pitch:y * pitch + pitch]
            for x in range(w):
                if fmt == PIXFMT_XRGB8888:
                    b, g, r = row[x * 4], row[x * 4 + 1], row[x * 4 + 2]
                else:
                    v = row[x * 2] | row[x * 2 + 1] << 8
                    if fmt == PIXFMT_RGB565:
                        r, g, b = (v >> 11) << 3, ((v >> 5) & 63) << 2, (v & 31) << 3
                    else:
                        r, g, b = ((v >> 10) & 31) << 3, ((v >> 5) & 31) << 3, (v & 31) << 3
                o = (y * w + x) * 3
                out[o:o + 3] = bytes((r, g, b))
        return (w, h, bytes(out))

    def _input(self, port, device, index, ident):
        if port != 0 or device != 1:
            return 0
        return 1 if ident in self.held else 0

    # --- API ---------------------------------------------------------------
    def run(self, n=1):
        for _ in range(n):
            self.lib.retro_run()
            self.frames += 1

    def hold(self, *names):
        self.held = {BUTTONS[n] for n in names}

    def press(self, name, frames=5, after=0):
        self.hold(name)
        self.run(frames)
        self.hold()
        self.run(after)

    def save(self):
        n = self.lib.retro_serialize_size()
        buf = C.create_string_buffer(n)
        assert self.lib.retro_serialize(buf, n)
        return buf.raw

    def load(self, state):
        buf = C.create_string_buffer(state, len(state))
        assert self.lib.retro_unserialize(buf, len(state))

    def ram(self):
        p = self.lib.retro_get_memory_data(MEMORY_SYSTEM_RAM)
        n = self.lib.retro_get_memory_size(MEMORY_SYSTEM_RAM)
        return C.string_at(p, n) if p else b''

    def sram(self):
        """Battery-backed cartridge RAM ($6000-$7FFF, 8 KB)."""
        p = self.lib.retro_get_memory_data(0)
        n = self.lib.retro_get_memory_size(0)
        return C.string_at(p, n) if p else b''

    def poke(self, addr, val):
        """Write one byte of cartridge RAM by CPU address ($6000-$7FFF),
        e.g. a story flag at $7100+n."""
        assert 0x6000 <= addr < 0x8000, hex(addr)
        p = self.lib.retro_get_memory_data(0)
        C.memmove(p + addr - 0x6000, bytes([val]), 1)

    def frame_png(self, path, scale=2):
        from PIL import Image
        w, h, rgb = self.frame
        im = Image.frombytes('RGB', (w, h), rgb)
        if scale != 1:
            im = im.resize((w * scale, h * scale), Image.NEAREST)
        im.save(path)

    def close(self):
        self.lib.retro_unload_game()
        self.lib.retro_deinit()
