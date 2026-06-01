import math

import pygame


def draw_lotus(screen, waveform, bars, peaks, rms, t, ctx):
    settings = ctx.mode_settings["lotus"]

    if rms < ctx.silence_threshold:
        ctx.fade_screen(screen, settings["idle_fade"])
        ctx.draw_idle(screen)
        return

    ctx.fade_screen(screen, settings["fade"])

    width, height = screen.get_size()
    cx, cy = width // 2, height // 2

    pulse = ctx.get_pulse(waveform, rms)

    layer = pygame.Surface((width, height), pygame.SRCALPHA)

    n_layers = settings["n_layers"]
    points_per_layer = settings["points_per_layer"]

    base_radius = min(width, height) * settings["base_radius_factor"]
    max_radius = min(width, height) * settings["max_radius_factor"]

    for layer_id in range(n_layers):
        points = []

        layer_u = layer_id / max(1, n_layers - 1)

        petal_count = 6 + layer_id
        rotation = t * 0.08 * (-1 if layer_id % 2 == 0 else 1)

        for j in range(points_per_layer):
            a = 2 * math.pi * j / points_per_layer

            band_index = int((j / points_per_layer) * (len(bars) - 1))
            amp = float(bars[band_index])

            petal = abs(math.sin(a * petal_count))
            breathing = math.sin(t * 1.2 + layer_id * 0.5) * 0.5 + 0.5

            radius = base_radius
            radius += layer_u * max_radius
            radius += petal * amp * 95.0
            radius += breathing * pulse * 18.0

            x = int(cx + math.cos(a + rotation) * radius)
            y = int(cy + math.sin(a + rotation) * radius)

            points.append((x, y))

        hue = 245 + layer_id * 18 + t * 12
        color = ctx.make_color(hue, 85, 100)

        pygame.draw.lines(
            layer,
            (*color[:3], 28),
            True,
            points,
            max(2, int(5 + pulse * 4)),
        )

        pygame.draw.lines(
            layer,
            (*color[:3], 135),
            True,
            points,
            max(1, int(1 + pulse * 2)),
        )

    screen.blit(layer, (0, 0), special_flags=pygame.BLEND_ADD)

    pygame.draw.circle(
        screen,
        (220, 230, 255),
        (cx, cy),
        int(7 + pulse * 18),
        width=1,
    )
