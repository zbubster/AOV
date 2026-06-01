import math

import numpy as np
import pygame


def draw_ribbons(screen, waveform, bars, peaks, rms, t, ctx):
    settings = ctx.mode_settings["ribbons"]

    if rms < ctx.silence_threshold:
        ctx.fade_screen(screen, settings["idle_fade"])
        ctx.draw_idle(screen)
        return

    ctx.fade_screen(screen, settings["fade"])

    width, height = screen.get_size()
    cy = height // 2

    pulse = ctx.get_pulse(waveform, rms)

    layer = pygame.Surface((width, height), pygame.SRCALPHA)

    n_ribbons = settings["n_ribbons"]
    points_per_ribbon = settings["points_per_ribbon"]

    # Each ribbon gets one smooth amplitude value, similar to how each tunnel
    # ring uses one band. The waveform is then generated from slow sine waves.
    # This avoids teeth caused by sampling a different audio band at every x.
    source_x = np.arange(len(bars), dtype=np.float32)
    ribbon_x = np.linspace(0, len(bars) - 1, n_ribbons, dtype=np.float32)

    ribbon_amps = np.interp(ribbon_x, source_x, bars)
    ribbon_amps = ctx.smooth_curve(ribbon_amps, passes=settings["smooth_passes"])
    ribbon_amps = np.clip(ribbon_amps, 0.0, 1.0)

    overall_amp = float(np.mean(ribbon_amps))

    for ribbon in range(n_ribbons):
        points = []

        ribbon_u = ribbon / max(1, n_ribbons - 1)
        ribbon_y = height * (
            settings["top_margin_factor"]
            + (settings["bottom_margin_factor"] - settings["top_margin_factor"]) * ribbon_u
        )
        phase = ribbon * 0.72
        amp = float(ribbon_amps[ribbon])

        for j in range(points_per_ribbon):
            u = j / (points_per_ribbon - 1)

            x = int(u * width)

            # Broad waves define the ribbon. Audio controls their strength,
            # not the local point-to-point shape.
            wave1 = math.sin(u * 7.0 + t * 1.45 + phase)
            wave2 = math.sin(u * 3.4 - t * 0.90 + phase * 1.5)
            wave3 = math.sin(u * 11.0 + t * 0.65 + phase * 2.0)

            y = ribbon_y
            y += wave1 * amp * settings["wave1_strength"]
            y += wave2 * amp * settings["wave2_strength"]
            y += wave3 * amp * settings["wave3_strength"]

            # A shared soft movement keeps quiet ribbons alive without
            # copying sharp spectral peaks into the line geometry.
            y += math.sin(t * 1.05 + ribbon) * pulse * 20.0
            y += math.sin(t * 0.50 + phase) * overall_amp * 28.0

            # Slight pull toward the center creates a tunnel-like feel.
            center_pull = math.sin(u * math.pi)
            y = y * (1 - center_pull * 0.15) + cy * (center_pull * 0.15)

            points.append((x, int(y)))

        hue = 170 + ribbon * 22 + t * 35
        color = ctx.make_color(hue, 90, 100)

        pygame.draw.lines(
            layer,
            (*color[:3], 26),
            False,
            points,
            max(2, int(4 + pulse * 7)),
        )

        pygame.draw.lines(
            layer,
            (*color[:3], 120),
            False,
            points,
            max(1, int(1 + pulse * 2)),
        )

        # Thin anti-aliased highlight makes the ribbon feel smoother.
        pygame.draw.aalines(
            layer,
            (*color[:3], 190),
            False,
            points,
        )

    screen.blit(layer, (0, 0), special_flags=pygame.BLEND_ADD)
