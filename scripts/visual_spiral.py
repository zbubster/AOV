import math

import pygame


def draw_spiral(screen, waveform, bars, peaks, rms, t, ctx):
    settings = ctx.mode_settings["spiral"]

    if rms < ctx.silence_threshold:
        ctx.fade_screen(screen, settings["idle_fade"])
        ctx.draw_idle(screen)
        return

    ctx.fade_screen(screen, settings["fade"])

    width, height = screen.get_size()
    cx, cy = width // 2, height // 2

    pulse = ctx.get_pulse(waveform, rms)
    intensity = min(1.0, rms * 18.0 + pulse * 0.7)

    n_arms = settings["n_arms"]
    points_per_arm = settings["points_per_arm"]

    base_radius = settings["base_radius"]
    max_radius = min(width, height) * settings["max_radius_factor"]

    glow_layer = pygame.Surface((width, height), pygame.SRCALPHA)

    for arm in range(n_arms):
        arm_phase = 2 * math.pi * arm / n_arms + t * 0.65
        points = []

        for j in range(points_per_arm):
            u = j / (points_per_arm - 1)

            band_index = int(u * (len(bars) - 1))
            amp = float(bars[band_index])

            angle = arm_phase + u * 5.3 + amp * 1.5
            radius = base_radius + u * max_radius

            wobble = math.sin(t * 3.0 + u * 12.0 + arm) * 16.0 * intensity
            radius += wobble + amp * 130.0

            x = int(cx + math.cos(angle) * radius)
            y = int(cy + math.sin(angle) * radius)

            points.append((x, y))

        hue = 195 + arm * 38 + t * 35
        color = ctx.make_color(hue, 95, 100)

        pygame.draw.lines(
            glow_layer,
            (*color[:3], 22),
            False,
            points,
            max(2, int(12 + pulse * 14)),
        )

        pygame.draw.lines(
            glow_layer,
            (*color[:3], 55),
            False,
            points,
            max(2, int(5 + pulse * 7)),
        )

        pygame.draw.lines(
            glow_layer,
            (*color[:3], 180),
            False,
            points,
            max(1, int(1 + pulse * 3)),
        )

        for j in range(10, points_per_arm, 10):
            u = j / points_per_arm
            amp = float(bars[int(u * (len(bars) - 1))])

            if amp < 0.04:
                continue

            x, y = points[j]
            dot_radius = max(1, int(1 + amp * 5))

            pygame.draw.circle(
                glow_layer,
                (*color[:3], int(80 + amp * 130)),
                (x, y),
                dot_radius,
            )

    screen.blit(glow_layer, (0, 0), special_flags=pygame.BLEND_ADD)

    core_radius = int(8 + pulse * 35)
    pygame.draw.circle(screen, (150, 220, 255), (cx, cy), core_radius, width=1)
    pygame.draw.circle(screen, (60, 160, 255), (cx, cy), max(2, core_radius // 2))
