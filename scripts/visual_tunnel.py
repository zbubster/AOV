import math

import pygame


def draw_tunnel(screen, waveform, bars, peaks, rms, t, ctx):
    settings = ctx.mode_settings["tunnel"]

    if rms < ctx.silence_threshold:
        ctx.fade_screen(screen, settings["idle_fade"])
        ctx.draw_idle(screen)
        return

    ctx.fade_screen(screen, settings["fade"])

    width, height = screen.get_size()
    cx, cy = width // 2, height // 2

    pulse = ctx.get_pulse(waveform, rms)

    n_rings = settings["n_rings"]
    points_per_ring = settings["points_per_ring"]

    max_radius = min(width, height) * settings["max_radius_factor"]
    layer = pygame.Surface((width, height), pygame.SRCALPHA)

    for ring in range(n_rings):
        u_ring = ring / max(1, n_rings - 1)

        base_radius = 20 + u_ring * max_radius
        band_index = int(u_ring * (len(bars) - 1))
        amp = float(bars[band_index])

        points = []

        for j in range(points_per_ring):
            a = 2 * math.pi * j / points_per_ring

            wave = math.sin(a * 5.0 + t * 4.0 - ring * 0.55)
            fine = math.sin(a * 13.0 - t * 2.0 + ring)

            radius = base_radius
            radius += wave * amp * 70.0
            radius += fine * amp * 18.0
            radius += pulse * 12.0

            x = int(cx + math.cos(a + t * 0.08) * radius)
            y = int(cy + math.sin(a + t * 0.08) * radius)

            points.append((x, y))

        hue = 215 + u_ring * 120 + t * 25
        color = ctx.make_color(hue, 90, 100)

        alpha = int(25 + amp * 150)
        line_width = max(1, int(1 + amp * 4))

        pygame.draw.lines(
            layer,
            (*color[:3], alpha),
            True,
            points,
            line_width,
        )

    screen.blit(layer, (0, 0), special_flags=pygame.BLEND_ADD)

    pygame.draw.circle(screen, (220, 240, 255), (cx, cy), int(6 + pulse * 24), width=1)
