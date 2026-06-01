# - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - #
# USER CONFIGURATION
# - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - #

# Audio input settings
SAMPLERATE = 48_000
CHANNELS = 2
BLOCKSIZE = 256

# Window settings
WIDTH = 1000
HEIGHT = 520
FPS = 90
START_FULLSCREEN = False

# Main spectrum object
N_BARS = 64

# Upper frequency limiter. This only affects visuals; music stays unchanged.
MAX_VIS_FREQ = 8_000

# Visual amplification
SILENCE_THRESHOLD = 0.0015
BAR_GAIN = 2.0
LOUDNESS_GAIN = 1.0

# Spectrum smoothing
# Lower attack = faster reaction when audio gets louder.
# Higher release = slower falloff when audio gets quieter.
SMOOTH_ATTACK = 0.20
SMOOTH_RELEASE = 0.65
PEAK_DECAY = 0.004

# General background fade for the classic bars mode
BACKGROUND_FADE = 75

# Music loading options
BUFFER_SECONDS = 0.025
BUFFER_SIZE = max(BLOCKSIZE * 4, int(SAMPLERATE * BUFFER_SECONDS))
AUDIO_QUEUE_BLOCKS = 3

# parec / PulseAudio / PipeWire latency
PAREC_LATENCY_MSEC = 15

# Starting visual mode
VISUAL_MODE = "bars"

# Audio source. Leave None to use the default output monitor.
MONITOR_SOURCE = None
# MONITOR_SOURCE = "alsa_output.usb-0c76_USB_PnP_Audio_Device-00.analog-stereo.monitor"


# - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - #
# VISUAL MODE SETTINGS
# - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - #

# All mode-specific tuning is centralized here.
# The visual_*.py files should mostly contain only drawing logic.
MODE_SETTINGS = {
    "bars": {
        "gap": 3,
        "top_margin": 28,
        "bottom_margin": 28,
        "min_bar_width": 3,
        "bar_radius": 2,
    },
    "spiral": {
        "fade": 70,
        "idle_fade": 95,
        "n_arms": 8,
        "points_per_arm": 200,
        "base_radius": 8,
        "max_radius_factor": 1.0,
    },
    "radial": {
        "fade": 40,
        "idle_fade": 95,
        "base_radius_factor": 0.20,
        "base_radius_pulse": 0.04,
        "max_length_factor": 0.34,
    },
    "tunnel": {
        "fade": 34,
        "idle_fade": 95,
        "n_rings": 25,
        "points_per_ring": 160,
        "max_radius_factor": 0.62,
    },
    "vortex": {
        "fade": 90,
        "idle_fade": 95,
        "n_streams": 7,
        "points_per_stream": 130,
        "max_radius_factor": 0.55,
    },
    "flower": {
        "fade": 70,
        "idle_fade": 95,
        "n_layers": 7,
        "points_per_layer": 260,
        "base_radius_factor": 0.16,
        "max_deform_factor": 0.28,
        "layer_spacing": 150,
    },
    "ribbons": {
        "fade": 70,
        "idle_fade": 95,
        "n_ribbons": 18,
        "points_per_ribbon": 260,
        "top_margin_factor": 0.05,
        "bottom_margin_factor": 0.95,
        "smooth_passes": 4,
        "wave1_strength": 82.0,
        "wave2_strength": 48.0,
        "wave3_strength": 12.0,
    },
    "lotus": {
        "fade": 35,
        "idle_fade": 95,
        "n_layers": 7,
        "points_per_layer": 300,
        "base_radius_factor": 0.12,
        "max_radius_factor": 0.33,
    },
    "mandala": {
        "fade": 45,
        "idle_fade": 95,
        "n_rings": 9,
        "points_per_ring": 240,
        "max_radius_factor": 0.43,
    },
}
