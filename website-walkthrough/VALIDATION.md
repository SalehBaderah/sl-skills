# Validation

Validated in the development workspace on November 5, 2026.

All **10 tests passed**, including the optional browser integration test:

- Seven locally synthesized effects have finite, distinct waveforms and short fades.
- Independent cues respect silence, gain, timestamps, and the end of the clip.
- Disabled/muted effects and invalid plans behave as documented.
- Silent video gains an audio stream only when effects are enabled.
- Original source audio remains in mixed and effects-disabled renders.
- Full mute removes all audio; older plans preserve their previous behavior.
- A real Chromium session opened a menu and changed the local test site's theme. Saved video frames confirmed both changes at the recorded event times.
- That capture's edit plan produced a final MP4, and the exported video fully decoded.
- Existing capture directories were protected from overwrite.

The browser test used an isolated local demo, system Chromium, and system FFmpeg. The workspace's network policy blocked Playwright's encoder-download hosts, so the already installed system FFmpeg was exposed through a temporary Playwright encoder-cache path for this test. No TLS or checksum verification was disabled. The standard Playwright browser/encoder installation command is documented but was not validated successfully through this workspace's restricted network.

This is functional and signal-level validation, not a listening review of sound design or verification of an arbitrary user's website. Login, iframe/popup interactions, custom site cursors, and third-party site access still need per-site review. Browser capture does not record system/site audio. The opening mode question is an instruction for the host agent; standalone Python scripts do not prompt for it.
