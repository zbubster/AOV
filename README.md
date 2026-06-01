# AOV
Audio Output Visualizer ‒ missing good old Windows Media Player visuals?
Currently available on Linux Debian only.

Run:

```bash
python3 AOV.py
```

Main files:

- `AOV.py` runs the app, audio input, FFT, smoothing and keyboard controls.
- `config.py` contains all user settings and mode-specific tuning.
- `visual_*.py` files define individual visual modes.

Keyboard:

- `1` to `9` switch visual modes.
- `f` toggles fullscreen.
- `q` or `Esc` quits.