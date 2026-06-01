import math

import pygame


def draw_radial(screen, waveform, bars, peaks, rms, t, ctx):
    settings = ctx.mode_settings["radial"]

    if rms < ctx.silence_threshold:
        ctx.fade_screen(screen, settings["idle_fade"])
        ctx.draw_idle(screen)
        return

    ctx.fade_screen(screen, settings["fade"])

    width, height = screen.get_size()
    cx, cy = width // 2, height // 2

    pulse = ctx.get_pulse(waveform, rms)

    n = len(bars)
    base_radius = min(width, height) * (
        settings["base_radius_factor"] + pulse * settings["base_radius_pulse"]
    )
    max_length = min(width, height) * settings["max_length_factor"]

    glow_layer = pygame.Surface((width, height), pygame.SRCALPHA)

    for i, amp in enumerate(bars):
        angle = 2 * math.pi * i / n - math.pi / 2 + t * 0.12

        r1 = base_radius
        r2 = base_radius + amp * max_length

        x1 = int(cx + math.cos(angle) * r1)
        y1 = int(cy + math.sin(angle) * r1)
        x2 = int(cx + math.cos(angle) * r2)
        y2 = int(cy + math.sin(angle) * r2)

        hue = 150 + i * 2.6 + t * 30
        color = ctx.make_color(hue, 85, 100)

        width_line = max(1, int(2 + amp * 7))

        pygame.draw.line(
            glow_layer,
            (*color[:3], 55),
            (x1, y1),
            (x2, y2),
            width_line + 6,
        )

        pygame.draw.line(
            glow_layer,
            (*color[:3], 210),
            (x1, y1),
            (x2, y2),
            width_line,
        )

    screen.blit(glow_layer, (0, 0), special_flags=pygame.BLEND_ADD)

    ring_radius = int(base_radius * 0.75)
    pygame.draw.circle(screen, (70, 170, 255), (cx, cy), ring_radius, width=1)
    pygame.draw.circle(screen, (200, 240, 255), (cx, cy), int(8 + pulse * 24), width=1)
