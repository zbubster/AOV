import math

import pygame


def draw_flower(screen, waveform, bars, peaks, rms, t, ctx):
    settings = ctx.mode_settings["flower"]

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
    max_deform = min(width, height) * settings["max_deform_factor"]

    for layer_id in range(n_layers):
        points = []

        layer_shift = layer_id / max(1, n_layers - 1)
        petal_count = 5 + layer_id * 2

        for j in range(points_per_layer):
            a = 2 * math.pi * j / points_per_layer

            band_pos = (j / points_per_layer) * (len(bars) - 1)
            band_index = int(band_pos)
            amp = float(bars[band_index])

            petal_wave = math.sin(a * petal_count + t * (1.5 + layer_shift))
            fine_wave = math.sin(a * (petal_count * 2 + 3) - t * 2.0)

            radius = base_radius + layer_shift * settings["layer_spacing"]
            radius += petal_wave * max_deform * amp
            radius += fine_wave * max_deform * 0.25 * amp
            radius += pulse * 35

            rotation = t * 0.15 * ((layer_id % 2) * 2 - 1)

            x = int(cx + math.cos(a + rotation) * radius)
            y = int(cy + math.sin(a + rotation) * radius)

            points.append((x, y))

        hue = 260 + layer_id * 32 + t * 30
        color = ctx.make_color(hue, 90, 100)

        pygame.draw.lines(
            layer,
            (*color[:3], 35),
            True,
            points,
            max(2, int(3 + pulse * 6)),
        )

        pygame.draw.lines(
            layer,
            (*color[:3], 155),
            True,
            points,
            max(1, int(1 + pulse * 2)),
        )

    screen.blit(layer, (0, 0), special_flags=pygame.BLEND_ADD)

    pygame.draw.circle(screen, (230, 230, 255), (cx, cy), int(6 + pulse * 22), width=1)
