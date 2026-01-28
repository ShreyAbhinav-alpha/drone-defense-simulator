import cv2
import numpy as np
import random
import time

# ---------------- CONFIG ----------------
W, H = 900, 600
DRONE_SPEED = 16
BULLET_SPEED = 14
ENEMY_SPEED = 3
SPAWN_RATE = 30

# ---------------- GAME STATE ----------------
drone_x, drone_y = W // 2, H - 80
bullets = []
enemies = []
enemy_bullets = []

score = 0
health = 100
frame_count = 0
paused = False

# ---------------- BOSS STATE ----------------
boss_active = False
boss_x, boss_y = W // 2, -120
boss_health = 0
boss_max_health = 200

# ---------------- CAMERA ----------------
cap = cv2.VideoCapture(0)

# ---------------- WINDOW ----------------
canvas = np.zeros((H, W, 3), dtype=np.uint8)
cv2.namedWindow("Drone Defense Simulator")

def mouse_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN and not paused:
        bullets.append([drone_x, drone_y])

cv2.setMouseCallback("Drone Defense Simulator", mouse_event)

print("""
DRONE DEFENSE SIMULATOR — BOSS MODE
W A S D : Move (Fast)
Mouse  : Shoot
P      : Pause
Q      : Quit
""")

while True:
    canvas[:] = (20, 20, 30)

    # -------- CAMERA MINI-MAP --------
    ret, cam = cap.read()
    if ret:
        cam_small = cv2.resize(cam, (180, 120))
        canvas[10:130, 10:190] = cam_small

    if paused:
        cv2.putText(canvas, "PAUSED",
                    (W//2 - 120, H//2),
                    cv2.FONT_HERSHEY_SIMPLEX, 2,
                    (255,255,255), 4)
        cv2.imshow("Drone Defense Simulator", canvas)
        if cv2.waitKey(30) & 0xFF == ord('p'):
            paused = False
        continue

    frame_count += 1

    # -------- INPUT --------
    key = cv2.waitKey(10) & 0xFF
    if key == ord('a'): drone_x -= DRONE_SPEED
    if key == ord('d'): drone_x += DRONE_SPEED
    if key == ord('w'): drone_y -= DRONE_SPEED
    if key == ord('s'): drone_y += DRONE_SPEED
    if key == ord('p'): paused = True
    if key == ord('q'): break

    drone_x = max(40, min(W - 40, drone_x))
    drone_y = max(40, min(H - 40, drone_y))

    # -------- BULLETS --------
    for b in bullets[:]:
        b[1] -= BULLET_SPEED
        if b[1] < 0:
            bullets.remove(b)

    # -------- SPAWN NORMAL ENEMIES --------
    if not boss_active:
        if frame_count % SPAWN_RATE == 0:
            enemies.append([random.randint(40, W - 40), -40])

    for e in enemies[:]:
        e[1] += ENEMY_SPEED
        if e[1] > H:
            health -= 10
            enemies.remove(e)

    # -------- BOSS SPAWN --------
    if score >= 300 and not boss_active:
        boss_active = True
        boss_x, boss_y = W // 2, -120
        boss_health = boss_max_health
        enemies.clear()

    # -------- BOSS BEHAVIOR --------
    if boss_active:
        if boss_y < 100:
            boss_y += 2
        else:
            boss_x += int(5 * np.sin(time.time()))

            if frame_count % 25 == 0:
                enemy_bullets.append([boss_x, boss_y + 40])

        for eb in enemy_bullets[:]:
            eb[1] += 8
            if eb[1] > H:
                enemy_bullets.remove(eb)
            elif abs(eb[0] - drone_x) < 20 and abs(eb[1] - drone_y) < 20:
                health -= 15
                enemy_bullets.remove(eb)

    # -------- COLLISIONS --------
    for b in bullets[:]:
        if boss_active:
            if abs(b[0] - boss_x) < 60 and abs(b[1] - boss_y) < 60:
                bullets.remove(b)
                boss_health -= 5
                if boss_health <= 0:
                    boss_active = False
                    score += 200
                    enemy_bullets.clear()
                continue

        for e in enemies[:]:
            if abs(b[0] - e[0]) < 20 and abs(b[1] - e[1]) < 20:
                bullets.remove(b)
                enemies.remove(e)
                score += 10
                break

    # -------- DRAW DRONE --------
    cv2.circle(canvas, (drone_x, drone_y), 15, (0, 200, 255), -1)
    for ox, oy in [(-25,-25),(25,-25),(-25,25),(25,25)]:
        cv2.line(canvas, (drone_x, drone_y),
                 (drone_x + ox, drone_y + oy),
                 (200,200,200), 2)

    # -------- DRAW ENEMIES --------
    for e in enemies:
        cv2.circle(canvas, (e[0], e[1]), 15, (0,0,255), -1)

    # -------- DRAW BOSS --------
    if boss_active:
        cv2.rectangle(canvas,
                      (boss_x - 60, boss_y - 40),
                      (boss_x + 60, boss_y + 40),
                      (50, 50, 200), -1)

        # Boss health bar
        bar_w = int(300 * (boss_health / boss_max_health))
        cv2.rectangle(canvas, (W//2 - 150, 20),
                      (W//2 - 150 + bar_w, 35),
                      (0,0,255), -1)
        cv2.rectangle(canvas, (W//2 - 150, 20),
                      (W//2 + 150, 35),
                      (255,255,255), 2)

    # -------- DRAW BULLETS --------
    for b in bullets:
        cv2.circle(canvas, (b[0], b[1]), 4, (255,255,0), -1)
    for eb in enemy_bullets:
        cv2.circle(canvas, (eb[0], eb[1]), 6, (0,0,255), -1)

    # -------- HUD --------
    cv2.putText(canvas, f"Health: {health}",
                (20, H - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

    cv2.putText(canvas, f"Score: {score}",
                (W - 160, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

    if health <= 0:
        cv2.putText(canvas, "GAME OVER",
                    (W//2 - 150, H//2),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 4)
        cv2.imshow("Drone Defense Simulator", canvas)
        cv2.waitKey(3000)
        break

    cv2.imshow("Drone Defense Simulator", canvas)

cap.release()
cv2.destroyAllWindows()
