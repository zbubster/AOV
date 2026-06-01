#!/usr/bin/env python3

import subprocess
import shutil
import sys
import queue
import threading
from dataclasses import dataclass
from typing import Callable

import numpy as np
import pygame

import config as cfg

from scripts.visual_bars import draw_bars
from scripts.visual_spiral import draw_spiral
from scripts.visual_radial import draw_radial
from scripts.visual_tunnel import draw_tunnel
from scripts.visual_vortex import draw_vortex
from scripts.visual_flower import draw_flower
from scripts.visual_ribbons import draw_ribbons
from scripts.visual_lotus import draw_lotus
from scripts.visual_mandala import draw_mandala


# - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - #
# VISUAL MODE REGISTRY
# - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - #

VISUAL_MODES = {
    "bars": draw_bars,
    "spiral": draw_spiral,
    "radial": draw_radial,
    "tunnel": draw_tunnel,
    "vortex": draw_vortex,
    "flower": draw_flower,
    "ribbons": draw_ribbons,
    "lotus": draw_lotus,
    "mandala": draw_mandala,
}
KEY_TO_MODE = {
    pygame.K_1: "bars",
    pygame.K_2: "spiral",
    pygame.K_3: "radial",
    pygame.K_4: "tunnel",
    pygame.K_5: "vortex",
    pygame.K_6: "flower",
    pygame.K_7: "ribbons",
    pygame.K_8: "lotus",
    pygame.K_9: "mandala",
}


@dataclass(frozen=True)
class DrawContext:
    silence_threshold: float
    background_fade: int
    mode_settings: dict
    fade_screen: Callable
    draw_idle: Callable
    make_color: Callable
    get_pulse: Callable
    smooth_curve: Callable


# - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - #
# PULSE / PIPEWIRE HELPERS
# - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - #

def run_cmd(cmd):
    return subprocess.check_output(cmd, text=True).strip()


def get_default_monitor_source():
    sink = run_cmd(["pactl", "get-default-sink"])
    return sink + ".monitor"


def list_sources():
    print(run_cmd(["pactl", "list", "short", "sources"]))


# - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - #
# AUDIO READING FROM OUTPUT MONITOR
# - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - #

def start_parec(monitor_source):
    cmd = [
        "parec",
        "--device", monitor_source,
        "--format", "float32le",
        "--rate", str(cfg.SAMPLERATE),
        "--channels", str(cfg.CHANNELS),
        "--raw",
    ]

    if cfg.PAREC_LATENCY_MSEC is not None:
        cmd.extend(["--latency-msec", str(cfg.PAREC_LATENCY_MSEC)])

    return subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=0,
    )


def audio_reader(proc, audio_queue):
    bytes_per_sample = 4
    bytes_per_frame = cfg.CHANNELS * bytes_per_sample
    block_bytes = cfg.BLOCKSIZE * bytes_per_frame

    while True:
        raw = proc.stdout.read(block_bytes)

        if not raw:
            break

        data = np.frombuffer(raw, dtype=np.float32)

        if len(data) == 0:
            continue

        valid_length = (len(data) // cfg.CHANNELS) * cfg.CHANNELS
        data = data[:valid_length]

        if len(data) == 0:
            continue

        data = data.reshape(-1, cfg.CHANNELS)
        mono = data.mean(axis=1).astype(np.float32)

        # If the visualizer is busy, drop the oldest queued block.
        while True:
            try:
                audio_queue.put_nowait(mono)
                break
            except queue.Full:
                try:
                    audio_queue.get_nowait()
                except queue.Empty:
                    pass


# - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - #
# SPECTRUM PROCESSING
# - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - #

def make_bars(spectrum, rms, n_bars=None):
    if n_bars is None:
        n_bars = cfg.N_BARS

    if rms < cfg.SILENCE_THRESHOLD:
        return np.zeros(n_bars)

    spectrum = spectrum.copy()

    # Remove DC and very low rumble.
    spectrum[:3] = 0

    idx = np.geomspace(3, len(spectrum) - 1, n_bars + 1).astype(int)

    bars = []

    for i in range(n_bars):
        lo = idx[i]
        hi = max(idx[i + 1], lo + 1)
        band_value = np.mean(spectrum[lo:hi])
        bars.append(band_value)

    bars = np.array(bars)

    # Stable scaling, no normalization by current maximum.
    bars = np.log1p(bars * cfg.BAR_GAIN)

    loudness = min(1.0, rms * cfg.LOUDNESS_GAIN)
    bars = bars * loudness

    return np.clip(bars, 0.0, 1.0)


def get_energy(waveform):
    return float(np.mean(np.abs(waveform)))


def get_pulse(waveform, rms):
    energy = get_energy(waveform)
    return min(1.0, energy * 8.0 + rms * 3.0)


def smooth_curve(values, passes=5):
    """Smooth a 1D curve for drawing organic visual shapes."""
    values = np.asarray(values, dtype=np.float32)

    if len(values) < 5:
        return values

    kernel = np.array([1, 4, 6, 4, 1], dtype=np.float32)
    kernel = kernel / kernel.sum()

    out = values.copy()

    for _ in range(passes):
        padded = np.pad(out, (2, 2), mode="edge")
        out = np.convolve(padded, kernel, mode="valid")

    return out


# - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - #
# DRAWING HELPERS
# - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - #

def fade_screen(screen, amount):
    width, height = screen.get_size()

    fade = pygame.Surface((width, height), pygame.SRCALPHA)
    fade.fill((0, 0, 0, amount))
    screen.blit(fade, (0, 0))


def make_color(hue, saturation=90, value=100, alpha=255):
    color = pygame.Color(0)
    color.hsva = (hue % 360, saturation, value, alpha / 255 * 100)
    return color


def draw_idle(screen):
    width, height = screen.get_size()
    cx, cy = width // 2, height // 2

    pygame.draw.circle(screen, (25, 45, 70), (cx, cy), 80, width=1)
    pygame.draw.circle(screen, (45, 85, 130), (cx, cy), 34, width=1)


def make_draw_context():
    return DrawContext(
        silence_threshold=cfg.SILENCE_THRESHOLD,
        background_fade=cfg.BACKGROUND_FADE,
        mode_settings=cfg.MODE_SETTINGS,
        fade_screen=fade_screen,
        draw_idle=draw_idle,
        make_color=make_color,
        get_pulse=get_pulse,
        smooth_curve=smooth_curve,
    )


# - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - #
# MAIN
# - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - #

def main():
    if shutil.which("pactl") is None:
        print("Missing pactl. Please, install:")
        print("sudo apt install pulseaudio-utils")
        sys.exit(1)

    if shutil.which("parec") is None:
        print("Missing parec. Please, install:")
        print("sudo apt install pulseaudio-utils")
        sys.exit(1)

    monitor_source = cfg.MONITOR_SOURCE

    if monitor_source is None:
        monitor_source = get_default_monitor_source()

    print("Using output monitor source:")
    print(f"  {monitor_source}")
    print()
    print("Available audio sources:")
    list_sources()
    print()

    proc = start_parec(monitor_source)

    audio_queue = queue.Queue(maxsize=cfg.AUDIO_QUEUE_BLOCKS)

    reader_thread = threading.Thread(
        target=audio_reader,
        args=(proc, audio_queue),
        daemon=True,
    )
    reader_thread.start()

    audio_buffer = np.zeros(cfg.BUFFER_SIZE, dtype=np.float32)

    smoothed_bars = np.zeros(cfg.N_BARS, dtype=np.float32)
    peaks = np.zeros(cfg.N_BARS, dtype=np.float32)

    pygame.init()

    fullscreen = cfg.START_FULLSCREEN

    if fullscreen:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)
    else:
        screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT))
        pygame.mouse.set_visible(True)

    current_mode = cfg.VISUAL_MODE
    pygame.display.set_caption(f"Audio Output Visualizer - {current_mode}")

    clock = pygame.time.Clock()
    draw_context = make_draw_context()

    t = 0.0
    running = True

    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_q):
                        running = False

                    elif event.key == pygame.K_f:
                        fullscreen = not fullscreen

                        if fullscreen:
                            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                            pygame.mouse.set_visible(False)
                        else:
                            screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT))
                            pygame.mouse.set_visible(True)

                    elif event.key in KEY_TO_MODE:
                        current_mode = KEY_TO_MODE[event.key]

                    pygame.display.set_caption(
                        f"Audio Output Visualizer - {current_mode}"
                    )

            received_audio = False

            while not audio_queue.empty():
                block = audio_queue.get_nowait()

                audio_buffer = np.roll(audio_buffer, -len(block))
                audio_buffer[-len(block):] = block

                received_audio = True

            if not received_audio:
                audio_buffer *= 0.92

            rms = float(np.sqrt(np.mean(audio_buffer ** 2)))

            window = np.hanning(len(audio_buffer))
            spectrum = np.abs(np.fft.rfft(audio_buffer * window))

            # Keep only frequencies up to MAX_VIS_FREQ.
            freqs = np.fft.rfftfreq(len(audio_buffer), d=1.0 / cfg.SAMPLERATE)
            max_bin = np.searchsorted(freqs, cfg.MAX_VIS_FREQ, side="right")
            max_bin = max(4, max_bin)

            spectrum = spectrum[:max_bin]

            raw_bars = make_bars(spectrum, rms, n_bars=cfg.N_BARS)

            smooth_factor = np.where(
                raw_bars > smoothed_bars,
                cfg.SMOOTH_ATTACK,
                cfg.SMOOTH_RELEASE,
            )

            smoothed_bars = (
                smooth_factor * smoothed_bars
                + (1.0 - smooth_factor) * raw_bars
            )

            peaks = np.maximum(peaks - cfg.PEAK_DECAY, smoothed_bars)

            draw_function = VISUAL_MODES.get(current_mode, draw_spiral)
            draw_function(
                screen=screen,
                waveform=audio_buffer,
                bars=smoothed_bars,
                peaks=peaks,
                rms=rms,
                t=t,
                ctx=draw_context,
            )

            pygame.display.flip()

            dt = clock.tick(cfg.FPS) / 1000.0
            t += dt

    finally:
        proc.terminate()
        pygame.quit()


if __name__ == "__main__":
    main()
