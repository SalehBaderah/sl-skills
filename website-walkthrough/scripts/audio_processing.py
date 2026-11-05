"""Build FFmpeg audio options without changing the recording's channel layout.

Input 1 is the original recording. Input 2, when present, is the synthesized
effects WAV. The caller owns video mapping, input arguments, and output timing.
"""


# Only named layouts whose channel order is defined by FFmpeg are accepted.
# In particular, a channel count alone cannot identify a multichannel layout.
_LAYOUT_CHANNELS = {
    "mono": 1,
    "stereo": 2,
    "2.1": 3,
    "3.0": 3,
    "3.0(back)": 3,
    "4.0": 4,
    "quad": 4,
    "quad(side)": 4,
    "5.0": 5,
    "5.0(side)": 5,
    "5.1": 6,
    "5.1(side)": 6,
    "6.1": 7,
    "6.1(back)": 7,
    "6.1(front)": 7,
    "7.1": 8,
    "7.1(wide)": 8,
    "7.1(wide-side)": 8,
}


def validate_audio_processing(plan):
    """Validate the public audio and optional hum-cleanup configuration.

    Cleanup is off when absent or explicitly disabled. An enabled object must
    select the local mains frequency; there is deliberately no guessed default.
    """
    if plan.get("audio", "preserve") not in ("preserve", "mute"):
        raise ValueError("audio must be preserve or mute")
    if "audio_cleanup" not in plan:
        return
    cleanup = plan["audio_cleanup"]
    if not isinstance(cleanup, dict):
        raise ValueError("audio_cleanup must be an object")
    enabled = cleanup.get("enabled", True)
    if not isinstance(enabled, bool):
        raise ValueError("audio_cleanup.enabled must be true or false")
    if enabled or "hum_hz" in cleanup:
        hum = cleanup.get("hum_hz")
        if isinstance(hum, bool) or hum not in (50, 60):
            raise ValueError("audio_cleanup.hum_hz must be 50 or 60")
    harmonics = cleanup.get("harmonics", 3)
    if isinstance(harmonics, bool) or not isinstance(harmonics, int) or not 1 <= harmonics <= 4:
        raise ValueError("audio_cleanup.harmonics must be an integer from 1 to 4")


def _source_layout(stream):
    channels = stream.get("channels")
    if isinstance(channels, bool) or not isinstance(channels, int) or channels < 1:
        raise ValueError("source audio must declare a positive channel count")
    layout = stream.get("channel_layout")
    if not layout or layout == "unknown":
        if channels in (1, 2):
            layout = "mono" if channels == 1 else "stereo"
        else:
            raise ValueError("multichannel source audio must declare a supported channel_layout")
    if layout not in _LAYOUT_CHANNELS or _LAYOUT_CHANNELS[layout] != channels:
        raise ValueError("source audio channel_layout is unsupported or does not match channels")
    return channels, layout


def _encode_options(channels, layout):
    return ["-c:a", "aac", "-b:a", "192k", "-ac", str(channels), "-channel_layout", layout]


def audio_options(plan, source_audio_stream_or_none, has_effects):
    """Return FFmpeg audio mapping/filter/encoding options for the plan.

    The source argument is its ffprobe stream object, or None. Effects are
    upmixed before mixing, so a mono effect cannot downmix stereo narration.
    Hum notches affect only the original recording. No loudness normalization
    is applied; the effects mix retains the existing peak limiter.
    """
    validate_audio_processing(plan)
    if plan.get("audio", "preserve") == "mute":
        return ["-an"]
    source = source_audio_stream_or_none
    if source is None:
        if not has_effects:
            return ["-an"]
        return ["-map", "2:a:0"] + _encode_options(1, "mono")

    channels, layout = _source_layout(source)
    cleanup = plan.get("audio_cleanup", {})
    clean = bool(cleanup) and cleanup.get("enabled", True)
    if not has_effects and not clean:
        return ["-map", "1:a:0"] + _encode_options(channels, layout)

    # first_pts=0 retains an original recording's initial audio delay as silence.
    original = (
        f"[1:a:0]aresample=48000:first_pts=0,"
        f"aformat=sample_fmts=fltp:channel_layouts={layout},asetpts=PTS-STARTPTS"
    )
    if clean:
        for harmonic in range(1, cleanup.get("harmonics", 3) + 1):
            original += f",bandreject=f={cleanup['hum_hz'] * harmonic}:t=h:w=6"
    filters = original + "[original]"
    output = "original"
    if has_effects:
        filters += (
            f";[2:a:0]aresample=48000,"
            f"aformat=sample_fmts=fltp:channel_layouts={layout},asetpts=PTS-STARTPTS[effects]"
            ";[original][effects]amix=inputs=2:duration=longest:normalize=0,"
            "alimiter=limit=0.95:level=false:latency=true"
            f",aformat=channel_layouts={layout}[mix]"
        )
        output = "mix"
    return ["-filter_complex", filters, "-map", f"[{output}]"] + _encode_options(channels, layout)
