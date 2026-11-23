# Strawberry Video Player

A video player, HDMI diagnostic tool and test pattern generator for AV professionals,
for the CardputerZero.

Runs on the CardputerZero (Raspberry Pi CM0, Debian 13 arm64), with no network needed.

- **Offline video player:** plays the videos in `~/Videos` alphabetically and loops (loop one, loop all). It shows
  on HDMI when a display is connected, otherwise on the built-in 320x170 LCD, and sound follows
  the picture.
- **HDMI diagnostic tool:** key `i` shows what the display reports (name, maker, active mode,
  color range, audio formats, link status, CEC address) on the LCD.
- **Test pattern generator:** key `t` shows color bars, gray steps, geometry, a convergence
  grid, and an audio and sync test on HDMI.

## Keys

| Key | Action |
| --- | --- |
| Tab | swap LCD / HDMI playback|
| q, Space, Return | play / pause |
| z, x, Del | previous video |
| c, f | next video |
| w / e | back / forward 30 s |
| s / d | volume down / up |
| a | mute |
| l | loop one / loop all |
| 0 or o | LCD off / on while playing on HDMI (saves a little power) |
| p | subtitles on HDMI: off, then each embedded track (the LCD note names the language) |
| 1-8 | display aspect ratio: 16:9, 16:10, 4:3, 5:4, 1:1, 2.35:1, 2.21:1, 21:9 |
| h | help (on the LCD while HDMI plays) |
| t | test patterns on HDMI on / off; z x c f choose the pattern: color bars, gray steps, geometry, convergence, audio + sync |
| i | HDMI diagnostics on the LCD: display name, mode, color range, audio, link, CEC address |
| Esc | quit |

## USB drives

Plug in a USB drive (FAT32, exFAT, NTFS or ext4) and its videos play: from a folder named `Videos` on the drive, or from the top level if there is no such folder. Take the drive out and the player goes back to `~/Videos`. The drive is mounted read-only, and nothing is written to it or copied to the card. With no drive and no videos in `~/Videos`, the LCD says so.

## Smooth HDMI

Nothing to set up on the stock CardputerZero image. For full-screen 1080p the player stops the desktop while it plays HDMI and starts it again afterwards, using the passwordless sudo the `pi` user already has, for those two commands only (`systemctl stop lightdm` and `systemctl start lightdm`). If a system has no sudo, HDMI plays in a desktop window (less smooth) and the LCD shows `sudo strawberry-video-player --setup`, which installs a polkit rule for the same two actions. `--unsetup` removes it.

## Build and install

    dpkg-deb --build --root-owner-group . strawberry-video-player_2.7.15_all.deb
    sudo dpkg -i strawberry-video-player_2.7.15_all.deb

Run it from the launcher, or `strawberry-video-player [DIR|FILE] [--start MM:SS] [--output lcd|hdmi]`.

## License

MIT, see `LICENSE`.
