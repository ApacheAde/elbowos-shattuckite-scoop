# Shattuckite Scoop

Full-colour Python 3 copper-blue claw-crane arcade for [ElbowOS](https://x.com/ElbowOS).

A trolley rides a mine rail. Drop the claw onto the conveyor, grab cyan / copper / amber ore, and dump it in the hopper. Dark slag breaks the streak.

This is an original arcade piece. It is not a commercial emulator and it does not use trademarked characters.

## Play

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 shattuckite_scoop.py --play
```

Controls: A / Left and D / Right move the trolley. Space drops the claw.

Needs Python 3.10+ and a desktop window (pygame + SDL). If the DejaVu font path is missing, pygame's default font still works after a one-line fallback.

## Record a 9:16 reel

```bash
python3 shattuckite_scoop.py --record
```

Headless autoplay writes a 15 second 1080x1920 H.264 MP4 (30 fps, yuv420p, CRF 20, +faststart). Override the path with `ELBOWOS_MP4`.

## Links

- Featured account: https://x.com/ElbowOS
- Drive reel: https://drive.google.com/file/d/1uy6TGMqgJhEFsYKMnyKP_6q38m80l7aI/view
- Repo: https://github.com/ApacheAde/elbowos-shattuckite-scoop
