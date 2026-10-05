"""Shattuckite Scoop — copper-blue claw crane over a mine conveyor.

Python 3 + pygame. Featured: https://x.com/ElbowOS
  python3 shattuckite_scoop.py --play     # interactive window
  python3 shattuckite_scoop.py --record   # 15s 9:16 MP4 autoplay
"""
import math
import os
import random
import subprocess
import sys

RECORD = "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1"
PLAY = "--play" in sys.argv
if RECORD or not PLAY:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get("ELBOWOS_MP4", "/workspace/artifacts/SHATTUCKITE_SCOOP_ElbowOS.mp4")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
NIGHT = (7, 14, 28)
CYAN = (64, 224, 214)
TEAL = (16, 120, 138)
COPPER = (214, 118, 58)
AMBER = (255, 186, 70)
SLAG = (54, 46, 50)
CREAM = (236, 244, 250)
RUST = (110, 48, 28)
BELT = (48, 36, 28)
INK = (8, 10, 16)


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        flags = 0 if PLAY else pygame.HIDDEN
        try:
            self.screen = pygame.display.set_mode((W, H), flags)
        except pygame.error:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            pygame.display.quit()
            pygame.display.init()
            self.screen = pygame.display.set_mode((W, H), pygame.HIDDEN)
        pygame.display.set_caption("Shattuckite Scoop")
        self.font = pygame.font.Font(FONT, 64)
        self.mid = pygame.font.Font(FONT, 42)
        self.small = pygame.font.Font(FONT, 32)
        self.reset()

    def reset(self):
        self.tx = 540.0
        self.cable = 0.12
        self.phase = "idle"  # idle drop bite rise carry dump
        self.held = None
        self.jaw = 1.0
        self.score = 0
        self.streak = 0
        self.ores = []
        self.sparks = []
        self.flash = 0
        self.t = 0
        self.spawn = 0
        random.seed(7)
        for i in range(6):
            self.ores.append(self._ore(180 + i * 150))

    def _ore(self, x):
        kind = random.choices(["cyan", "copper", "amber", "slag"], [5, 3, 2, 2])[0]
        return {"x": float(x), "kind": kind, "r": random.randint(40, 54), "spin": random.random() * 6.28, "alive": True}

    def step(self, left, right, drop):
        self.t += 1
        self.flash = max(0, self.flash - 1)
        speed = 9.5
        if left:
            self.tx -= speed
        if right:
            self.tx += speed
        self.tx = max(120, min(960, self.tx))
        self.spawn += 1
        if self.spawn > 38:
            self.spawn = 0
            self.ores.append(self._ore(-40))
        for o in self.ores:
            o["x"] += 6.4
            o["spin"] += 0.04
        self.ores = [o for o in self.ores if o["alive"] and o["x"] < 1180]
        tip = self.tip_y()
        if self.phase == "idle":
            self.cable += (0.12 - self.cable) * 0.18
            self.jaw = 1.0
            if drop:
                self.phase = "drop"
        elif self.phase == "drop":
            self.cable = min(1.0, self.cable + 0.085)
            self.jaw = 1.0
            if self.cable >= 0.98:
                self.phase = "bite"
        elif self.phase == "bite":
            self.jaw = max(0.15, self.jaw - 0.18)
            if self.jaw <= 0.2:
                self._try_grab()
                self.phase = "rise"
        elif self.phase == "rise":
            self.cable = max(0.12, self.cable - 0.07)
            if self.cable <= 0.14:
                self.phase = "carry" if self.held else "idle"
        elif self.phase == "carry":
            self.cable += (0.12 - self.cable) * 0.2
            if abs(self.tx - 180) < 36:
                self._dump()
        elif self.phase == "dump":
            self.phase = "idle"
        for s in self.sparks:
            s["x"] += s["vx"]
            s["y"] += s["vy"]
            s["vy"] += 0.35
            s["life"] -= 1
        self.sparks = [s for s in self.sparks if s["life"] > 0]
        return tip

    def tip_y(self):
        return 300 + self.cable * 980

    def _try_grab(self):
        tip = self.tip_y()
        best = None
        for o in self.ores:
            if not o["alive"]:
                continue
            if abs(o["x"] - self.tx) < o["r"] + 18 and abs(tip - 1360) < 90:
                best = o
                break
        if not best:
            self.streak = 0
            self._burst(self.tx, tip, CREAM, 8)
            return
        best["alive"] = False
        if best["kind"] == "slag":
            self.score = max(0, self.score - 40)
            self.streak = 0
            self.flash = 8
            self.held = None
            self._burst(best["x"], 1360, (180, 80, 60), 16)
        else:
            self.held = best["kind"]
            self.streak += 1
            self.score += 50 + self.streak * 10
            self._burst(best["x"], 1360, self.col(best["kind"]), 18)

    def _dump(self):
        self._burst(180, 420, self.col(self.held or "cyan"), 14)
        self.score += 25
        self.held = None
        self.phase = "idle"

    def _burst(self, x, y, col, n):
        for _ in range(n):
            a = random.random() * 6.28
            sp = random.uniform(2, 8)
            self.sparks.append({"x": x, "y": y, "vx": math.cos(a) * sp, "vy": math.sin(a) * sp - 2, "life": random.randint(12, 26), "c": col})

    def col(self, kind):
        return {"cyan": CYAN, "copper": COPPER, "amber": AMBER, "slag": SLAG}.get(kind, CYAN)

    def ai(self):
        left = right = drop = False
        if self.phase in ("idle", "carry"):
            if self.phase == "carry":
                goal = 180
            else:
                gems = [o for o in self.ores if o["alive"] and o["kind"] != "slag" and 40 < o["x"] < 1000]
                goal = min(gems, key=lambda o: abs(o["x"] - self.tx))["x"] if gems else 540 + math.sin(self.t * 0.05) * 200
            if self.tx < goal - 14:
                right = True
            elif self.tx > goal + 14:
                left = True
            if self.phase == "idle" and gems:
                near = [o for o in gems if abs(o["x"] - self.tx) < 34 and 160 < o["x"] < 940]
                if near and self.cable < 0.25:
                    drop = True
        return left, right, drop

    def draw(self, surf):
        surf.fill(NIGHT)
        for i in range(18):
            c = 10 + i * 2
            pygame.draw.rect(surf, (c, 18 + i, 36 + i), (0, i * 90, W, 90))
        for x in (70, 1010):
            pygame.draw.rect(surf, (22, 36, 52), (x, 180, 28, 1500))
            for y in range(220, 1600, 90):
                pygame.draw.rect(surf, (40, 70, 88), (x - 8, y, 44, 10))
        for i, lx in enumerate((220, 540, 860)):
            flicker = 8 if (self.t + i * 3) % 17 == 0 else 0
            pygame.draw.line(surf, (80, 70, 40), (lx, 160), (lx, 250), 3)
            pygame.draw.circle(surf, (255, 200 - flicker, 90), (lx, 268), 16)
            pygame.draw.circle(surf, (255, 170, 60), (lx, 268), 28, 2)
        pygame.draw.rect(surf, (70, 86, 98), (90, 168, 900, 22), border_radius=4)
        pygame.draw.rect(surf, (160, 170, 180), (90, 176, 900, 4))
        pygame.draw.rect(surf, (40, 52, 64), (self.tx - 54, 150, 108, 36), border_radius=6)
        pygame.draw.circle(surf, AMBER, (int(self.tx - 30), 188), 8)
        pygame.draw.circle(surf, AMBER, (int(self.tx + 30), 188), 8)
        tip = int(self.tip_y())
        pygame.draw.line(surf, (190, 196, 204), (self.tx, 186), (self.tx, tip - 30), 5)
        for sign in (-1, 1):
            jx = self.tx + sign * (18 + self.jaw * 28)
            pygame.draw.line(surf, COPPER, (self.tx, tip - 30), (jx, tip + 8), 8)
            pygame.draw.circle(surf, AMBER, (int(jx), tip + 10), 8)
        if self.held:
            pygame.draw.circle(surf, self.col(self.held), (int(self.tx), tip - 8), 22)
            pygame.draw.circle(surf, CREAM, (int(self.tx) - 6, tip - 14), 6)
        pygame.draw.polygon(surf, (30, 70, 84), [(80, 360), (280, 360), (250, 520), (110, 520)])
        pygame.draw.polygon(surf, CYAN, [(80, 360), (280, 360), (250, 520), (110, 520)], 4)
        hop = self.small.render("HOPPER", True, CREAM)
        surf.blit(hop, hop.get_rect(center=(180, 430)))
        pygame.draw.rect(surf, RUST, (40, 1320, 1000, 150), border_radius=12)
        pygame.draw.rect(surf, BELT, (60, 1340, 960, 78), border_radius=8)
        for i in range(12):
            rx = 90 + i * 80 + (self.t * 6) % 80
            if 70 < rx < 1000:
                pygame.draw.circle(surf, (70, 54, 40), (int(rx), 1455), 16)
                pygame.draw.circle(surf, (120, 90, 60), (int(rx), 1455), 16, 2)
        for o in self.ores:
            if not o["alive"]:
                continue
            self._gem(surf, int(o["x"]), 1368, o["r"], o["kind"], o["spin"])
        for s in self.sparks:
            pygame.draw.circle(surf, s["c"], (int(s["x"]), int(s["y"])), 4)
        if self.flash:
            veil = pygame.Surface((W, H), pygame.SRCALPHA)
            veil.fill((180, 40, 40, 70))
            surf.blit(veil, (0, 0))
        banner = pygame.Surface((W, 130), pygame.SRCALPHA)
        banner.fill((4, 10, 20, 170))
        surf.blit(banner, (0, 0))
        title = self.font.render("SHATTUCKITE SCOOP", True, CYAN)
        surf.blit(title, title.get_rect(center=(W // 2, 52)))
        sub = self.small.render("claw the ore  \u00b7  dump the hopper", True, AMBER)
        surf.blit(sub, sub.get_rect(center=(W // 2, 104)))
        score = self.mid.render(f"SCORE  {self.score}", True, CREAM)
        surf.blit(score, score.get_rect(center=(W // 2, 1560)))
        streak = self.small.render(f"STREAK  {self.streak}", True, COPPER)
        surf.blit(streak, streak.get_rect(center=(W // 2, 1612)))
        foot = pygame.Surface((W, 80), pygame.SRCALPHA)
        foot.fill((4, 10, 20, 180))
        surf.blit(foot, (0, H - 80))
        url = self.mid.render("x.com/ElbowOS", True, CYAN)
        surf.blit(url, url.get_rect(center=(W // 2, H - 40)))

    def _gem(self, surf, x, y, r, kind, spin):
        col = self.col(kind)
        if kind == "slag":
            pts = []
            for i in range(7):
                a = spin + i * 6.28 / 7
                rr = r * (0.7 + 0.3 * ((i * 3) % 2))
                pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr * 0.7))
            pygame.draw.polygon(surf, (40, 34, 36), pts)
            pygame.draw.polygon(surf, (160, 70, 40), pts, 3)
            return
        pts = []
        for i in range(6):
            a = spin + i * 3.1416 / 3
            pts.append((x + math.cos(a) * r, y + math.sin(a) * r * 0.72))
        pygame.draw.polygon(surf, col, pts)
        pygame.draw.polygon(surf, CREAM, pts, 3)
        pygame.draw.circle(surf, (255, 255, 255), (x - r // 4, y - r // 5), max(4, r // 7))

    def play_interactive(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            left = right = drop = False
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
                    drop = True
            keys = pygame.key.get_pressed()
            left = keys[pygame.K_LEFT] or keys[pygame.K_a]
            right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
            if keys[pygame.K_SPACE]:
                drop = True
            self.step(left, right, drop)
            self.draw(self.screen)
            pygame.display.flip()
            clock.tick(FPS)
        pygame.quit()

    def record(self):
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
            "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-crf", "20", "-preset", "veryfast", "-movflags", "+faststart", OUT,
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        frames = FPS * SECS
        try:
            for _ in range(frames):
                left, right, drop = self.ai()
                self.step(left, right, drop)
                self.draw(self.screen)
                proc.stdin.write(pygame.image.tobytes(self.screen, "RGB"))
        finally:
            proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", "ignore")
        rc = proc.wait()
        if rc != 0:
            raise SystemExit(f"ffmpeg failed ({rc}):\n{err[-1500:]}")
        print("wrote", OUT)
        pygame.quit()


def main():
    g = Game()
    if PLAY and not RECORD:
        g.play_interactive()
    else:
        g.record()


if __name__ == "__main__":
    main()
