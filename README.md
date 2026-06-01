# AUDIO OUTPUT VISUALIZER
Audio Output Visualizer ‒ missing good old Windows Media Player visuals? This software takes your audio output signal and converts it to the various visualizations. The program is platform-independent: it does not matter whether you are streaming music or listening to old CDs — what matters is the audio output device.

Currently available on Linux Debian only.

![Bars](pics/bars.png)

Run:

```bash
source venv/bin/activate
python3 AOV.py
```

Keyboard:

- `1` to `9` switch visual modes.
- `f` toggles fullscreen.
- `q` or `Esc` quits.

| | |
|---|---|
| ![Tunnel](pics/tunnel.png) | ![Flower](pics/flower.png) |
| ![Ribbons](pics/ribbons.png) | ![Vortex](pics/vortex.png) |

Main files:

- `AOV.py` runs the app, audio input, FFT, smoothing and keyboard controls.
- `config.py` contains all user settings and mode-specific tuning.
- `visual_*.py` files define individual visual modes.