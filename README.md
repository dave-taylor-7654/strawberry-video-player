# Strawberry Video Player

A video player for the CardputerZero (Raspberry Pi CM0, Debian 13 arm64).
It plays the videos in `~/Videos` alphabetically and loops. It shows on HDMI when a
display is connected, otherwise on the built-in 320x170 LCD, and sound follows the picture.

## Keys

| Key | Action |
| --- | --- |
| Tab | switch LCD / HDMI |
| q, Space, Return | play / pause |
| z, x, Del | previous video |
| c, f | next video |
| w / e | back / forward 30 s |
| s / d | volume down / up |
| a | mute |
| l | loop one / loop all |
| 1-8 | display aspect ratio: 16:9, 16:10, 4:3, 5:4, 1:1, 2.35:1, 2.21:1, 21:9 |
| h | help (on the LCD while HDMI plays) |
| Esc | quit |

## Build and install

    dpkg-deb --build --root-owner-group . strawberry-video-player_2.3.3_all.deb
    sudo dpkg -i strawberry-video-player_2.3.3_all.deb

Run it from the launcher, or `strawberry-video-player [DIR|FILE] [--start MM:SS] [--output lcd|hdmi]`.

## Smooth 1080p on HDMI (optional)

HDMI uses VLC's DRM output, which needs the desktop stopped while playing. That needs a polkit
rule that lets the `video` group stop and start `lightdm.service`; see
`usr/share/doc/strawberry-video-player/README` for the rule and for the recommended
`/boot/firmware/config.txt` settings (`gpu_mem=64`, `dtoverlay=vc4-kms-v3d,cma-128`). Without the
rule, HDMI plays in a desktop window (software decoding), which is less smooth at 1080p.

Hardware decoding is chosen per file: 8-bit 4:2:0 H.264 up to level 4.2. Anything else is decoded
in software automatically (about 250% CPU for 1080p24 at 10 Mb/s).

## License

MIT, see `LICENSE`.
