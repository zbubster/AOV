import math

import pygame


def draw_vortex(screen, waveform, bars, peaks, rms, t, ctx):
    settings = ctx.mode_settings["vortex"]

    if rms < ctx.silence_threshold:
        ctx.fade_screen(screen, settings["idle_fade"])
        ctx.draw_idle(screen)
        return

    ctx.fade_screen(screen, settings["fade"])

    width, height = screen.get_size()
    cx, cy = width // 2, height // 2

    pulse = ctx.get_pulse(waveform, rms)

    layer = pygame.Surface((width, height), pygame.SRCALPHA)

    n_streams = settings["n_streams"]
    points_per_stream = settings["points_per_stream"]
    max_radius = min(width, height) * settings["max_radius_factor"]

    for stream in range(n_streams):
        stream_phase = 2 * math.pi * stream / n_streams
        points = []

        for j in range(points_per_stream):
            u = j / (points_per_stream - 1)

            band_index = int(u * (len(bars) - 1))
            amp = float(bars[band_index])

            radius = 20 + u * max_radius
            radius += amp * 45.0
            radius += math.sin(t * 1.7 + u * 10.0 + stream) * amp * 16.0

            angle = stream_phase
            angle += u * 5.2
            angle += t * (0.22 + pulse * 0.18)
            angle += math.sin(u * 7.0 + t * 1.1) * 0.14 * amp

            x = int(cx + math.cos(angle) * radius)
            y = int(cy + math.sin(angle) * radius)

            points.append((x, y))

        hue = 200 + stream * 24 + t * 18
        color = ctx.make_color(hue, 90, 95)

        pygame.draw.lines(
            layer,
            (*color[:3], 22),
            False,
            points,
            max(2, int(5 + pulse * 4)),
        )

        pygame.draw.lines(
            layer,
            (*color[:3], 105),
            False,
            points,
            max(1, int(1 + pulse * 2)),
        )

    screen.blit(layer, (0, 0), special_flags=pygame.BLEND_ADD)

    core_radius = int(5 + pulse * 22)
    pygame.draw.circle(screen, (160, 220, 255), (cx, cy), core_radius, width=1)
