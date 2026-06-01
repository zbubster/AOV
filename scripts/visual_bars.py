import pygame


def draw_bars(screen, waveform, bars, peaks, rms, t, ctx):
    settings = ctx.mode_settings["bars"]

    ctx.fade_screen(screen, ctx.background_fade)

    width, height = screen.get_size()

    if rms < ctx.silence_threshold:
        ctx.draw_idle(screen)
        return

    bottom = height - settings["bottom_margin"]
    top_margin = settings["top_margin"]
    usable_height = bottom - top_margin

    gap = settings["gap"]
    bar_width = max(
        settings["min_bar_width"],
        (width - gap * (len(bars) + 1)) // len(bars),
    )

    for i, value in enumerate(bars):
        x = gap + i * (bar_width + gap)
        bar_height = int(value * usable_height)
        y = bottom - bar_height

        hue = 95 + (i / max(1, len(bars) - 1)) * 80
        color = ctx.make_color(hue, 75, 95)

        if bar_height > 0:
            pygame.draw.rect(
                screen,
                color,
                pygame.Rect(x, y, bar_width, bar_height),
                border_radius=settings["bar_radius"],
            )

            pygame.draw.rect(
                screen,
                (220, 255, 180),
                pygame.Rect(x, y, bar_width, 2),
            )

        peak_y = bottom - int(peaks[i] * usable_height)

        if peaks[i] > 0.02:
            pygame.draw.rect(
                screen,
                (230, 230, 230),
                pygame.Rect(x, peak_y - 2, bar_width, 3),
            )
