import math

import pygame


def draw_mandala(screen, waveform, bars, peaks, rms, t, ctx):
    settings = ctx.mode_settings["mandala"]

    if rms < ctx.silence_threshold:
        ctx.fade_screen(screen, settings["idle_fade"])
        ctx.draw_idle(screen)
        return

    ctx.fade_screen(screen, settings["fade"])

    width, height = screen.get_size()
    cx, cy = width // 2, height // 2

    pulse = ctx.get_pulse(waveform, rms)

    layer = pygame.Surface((width, height), pygame.SRCALPHA)

    n_rings = settings["n_rings"]
    points_per_ring = settings["points_per_ring"]

    for ring in range(n_rings):
        ring_u = ring / max(1, n_rings - 1)

        base_radius = 35 + ring_u * min(width, height) * settings["max_radius_factor"]
        symmetry = 5 + ring

        points = []

        for j in range(points_per_ring):
            a = 2 * math.pi * j / points_per_ring

            band_index = int((j / points_per_ring) * (len(bars) - 1))
            amp = float(bars[band_index])

            wave = math.sin(a * symmetry + t * 0.9)
            fine = math.sin(a * symmetry * 2 - t * 1.3)

            radius = base_radius
            radius += wave * amp * 42.0
            radius += fine * amp * 14.0
            radius += pulse * 8.0

            rotation = t * 0.04 * (-1 if ring % 2 == 0 else 1)

            x = int(cx + math.cos(a + rotation) * radius)
            y = int(cy + math.sin(a + rotation) * radius)

            points.append((x, y))

        hue = 180 + ring * 19 + t * 10
        color = ctx.make_color(hue, 85, 100)

        alpha = int(35 + ring_u * 80)

        pygame.draw.lines(
            layer,
            (*color[:3], alpha),
            True,
            points,
            max(1, int(1 + pulse * 2)),
        )

    screen.blit(layer, (0, 0), special_flags=pygame.BLEND_ADD)

    pygame.draw.circle(
        screen,
        (190, 230, 255),
        (cx, cy),
        int(5 + pulse * 20),
        width=1,
    )
