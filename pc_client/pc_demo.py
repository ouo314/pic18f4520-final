import tkinter as tk
from tkinter import messagebox
import serial

PORT = "COM3"  # macOS: ls /dev/cu.* | Windows: COM3
BAUD = 9600
SIZE = 240
BUF = 64

SAMPLES = {
    0: [0, 0, 4, 12, 5, 0, 0, 0, 0, 0, 12, 14, 15, 7, 0, 0, 0, 2, 14, 1, 2, 16, 0, 0, 0, 4, 8, 0, 0, 10, 4, 0, 0, 7, 8, 0, 0, 6, 8, 0, 0, 4, 11, 0, 0, 5, 8, 0, 0, 0, 14, 11, 3, 13, 5, 0, 0, 0, 2, 11, 16, 11, 0, 0],
    1: [0, 0, 8, 16, 15, 8, 0, 0, 0, 1, 16, 16, 16, 2, 0, 0, 0, 2, 16, 16, 10, 0, 0, 0, 0, 2, 16, 16, 12, 0, 0, 0, 0, 6, 16, 16, 13, 0, 0, 0, 0, 1, 16, 16, 11, 0, 0, 0, 0, 0, 16, 16, 10, 0, 0, 0, 0, 0, 7, 15, 15, 0, 0, 0],
    2: [0, 0, 7, 15, 13, 0, 0, 0, 0, 9, 16, 15, 16, 5, 0, 0, 0, 12, 16, 5, 15, 6, 0, 0, 0, 0, 7, 2, 13, 9, 0, 0, 0, 0, 0, 1, 16, 7, 0, 0, 0, 0, 0, 6, 16, 4, 0, 0, 0, 0, 1, 15, 16, 12, 15, 7, 0, 0, 5, 16, 14, 12, 12, 11],
    3: [0, 0, 9, 16, 16, 12, 2, 0, 0, 3, 13, 5, 4, 14, 5, 0, 0, 0, 0, 0, 7, 15, 2, 0, 0, 0, 0, 5, 16, 11, 0, 0, 0, 0, 0, 0, 8, 16, 7, 0, 0, 0, 0, 0, 0, 13, 8, 0, 0, 0, 4, 5, 5, 15, 4, 0, 0, 0, 12, 16, 15, 5, 0, 0],
    4: [0, 0, 0, 9, 15, 1, 0, 0, 0, 0, 4, 16, 12, 0, 0, 0, 0, 0, 15, 14, 2, 11, 3, 0, 0, 4, 16, 9, 4, 16, 10, 0, 0, 9, 16, 11, 13, 16, 2, 0, 0, 0, 9, 16, 16, 14, 0, 0, 0, 0, 0, 8, 16, 6, 0, 0, 0, 0, 0, 9, 16, 2, 0, 0],
    5: [0, 0, 4, 9, 12, 16, 8, 0, 0, 0, 15, 15, 8, 8, 2, 0, 0, 4, 16, 11, 4, 1, 0, 0, 0, 8, 16, 16, 16, 14, 0, 0, 0, 0, 11, 9, 8, 16, 0, 0, 0, 0, 0, 0, 7, 16, 0, 0, 0, 0, 0, 8, 16, 12, 0, 0, 0, 0, 3, 13, 9, 1, 0, 0],
    6: [0, 0, 0, 8, 12, 1, 0, 0, 0, 0, 1, 15, 12, 1, 0, 0, 0, 0, 6, 16, 3, 0, 0, 0, 0, 0, 7, 16, 1, 0, 0, 0, 0, 1, 16, 16, 14, 5, 0, 0, 0, 1, 12, 16, 6, 14, 9, 0, 0, 0, 2, 16, 6, 10, 15, 0, 0, 0, 0, 6, 16, 16, 11, 0],
    7: [0, 0, 5, 11, 16, 16, 5, 0, 0, 3, 15, 11, 10, 16, 4, 0, 0, 0, 4, 0, 10, 14, 0, 0, 0, 0, 7, 15, 16, 16, 12, 0, 0, 0, 9, 16, 14, 4, 1, 0, 0, 0, 1, 14, 7, 0, 0, 0, 0, 0, 4, 16, 4, 0, 0, 0, 0, 0, 8, 16, 0, 0, 0, 0],
    8: [0, 0, 0, 3, 14, 13, 3, 0, 0, 0, 0, 12, 9, 8, 8, 0, 0, 0, 0, 12, 8, 11, 6, 0, 0, 0, 0, 7, 14, 11, 1, 0, 0, 1, 8, 12, 15, 5, 0, 0, 0, 6, 14, 0, 4, 12, 0, 0, 0, 0, 7, 12, 1, 15, 2, 0, 0, 0, 0, 3, 13, 15, 2, 0],
    9: [0, 0, 8, 16, 13, 2, 0, 0, 0, 2, 16, 8, 11, 14, 1, 0, 0, 3, 16, 1, 12, 16, 5, 0, 0, 0, 12, 16, 16, 13, 9, 0, 0, 0, 0, 4, 2, 9, 14, 0, 0, 0, 4, 5, 0, 8, 13, 0, 0, 1, 16, 11, 1, 13, 7, 0, 0, 0, 8, 15, 16, 15, 1, 0],
}

ser = None
buf = [[0] * BUF for _ in range(BUF)]
last_xy = None
sample_idx = 0

def connect_serial():
    global ser
    try:
        ser = serial.Serial(PORT, BAUD, timeout=2)
        status_lbl.config(text=f"已連線：{PORT} ({BAUD} bps)", fg="green")
    except Exception as e:
        status_lbl.config(text=f"序列埠未連線：{e}", fg="red")

def stamp_circle(bx, by, r=4):
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                nx, ny = bx + dx, by + dy
                if 0 <= nx < BUF and 0 <= ny < BUF:
                    buf[ny][nx] = 1

def draw_line_buf(x0, y0, x1, y1):
    steps = max(1, abs(x1 - x0), abs(y1 - y0))
    for s in range(steps + 1):
        bx = int(round(x0 + (x1 - x0) * s / steps))
        by = int(round(y0 + (y1 - y0) * s / steps))
        stamp_circle(bx, by, r=4)

def on_press(event):
    global last_xy
    last_xy = (event.x, event.y)
    paint(event)

def on_release(event):
    global last_xy
    last_xy = None

def paint(event):
    global last_xy
    x, y = event.x, event.y
    if 0 <= x < SIZE and 0 <= y < SIZE:
        bx, by = x * BUF // SIZE, y * BUF // SIZE
        if last_xy is not None:
            lx, ly = last_xy
            canvas.create_line(lx, ly, x, y, fill="white", width=22, capstyle=tk.ROUND, smooth=True)
            draw_line_buf(lx * BUF // SIZE, ly * BUF // SIZE, bx, by)
        else:
            r = 11
            canvas.create_oval(x - r, y - r, x + r, y + r, fill="white", outline="white")
            stamp_circle(bx, by, r=4)
        last_xy = (x, y)

def clear():
    global buf, last_xy
    buf = [[0] * BUF for _ in range(BUF)]
    last_xy = None
    canvas.delete("all")
    preview.delete("all")
    res_lbl.config(text="辨識結果：--")

def buf_to_8x8_gray():
    xs, ys = [], []
    for y in range(BUF):
        for x in range(BUF):
            if buf[y][x]:
                xs.append(x)
                ys.append(y)
    if not xs:
        return [0] * 64

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    w, h = max_x - min_x + 1, max_y - min_y + 1
    side = max(w, h)
    pad = max(2, side // 8)
    box = side + 2 * pad
    ox = min_x - (box - w) // 2
    oy = min_y - (box - h) // 2

    grid = [0] * 64
    for gy in range(8):
        y0, y1 = oy + (gy * box) // 8, oy + ((gy + 1) * box) // 8
        for gx in range(8):
            x0, x1 = ox + (gx * box) // 8, ox + ((gx + 1) * box) // 8
            total, count = 0, 0
            for y in range(y0, max(y0 + 1, y1)):
                for x in range(x0, max(x0 + 1, x1)):
                    count += 1
                    if 0 <= x < BUF and 0 <= y < BUF:
                        total += buf[y][x]
            val = int(round(16.0 * total / max(1, count)))
            grid[gy * 8 + gx] = min(16, max(0, val))
    return grid

def draw_preview(grid):
    preview.delete("all")
    cell = 15
    for r in range(8):
        for c in range(8):
            v = min(255, grid[r * 8 + c] * 16)
            color = f"#{v:02x}{v:02x}{v:02x}"
            preview.create_rectangle(c * cell, r * cell, (c + 1) * cell, (r + 1) * cell, fill=color, outline="#333333")

def send_grid(grid, label_prefix="PIC18 辨識結果"):
    draw_preview(grid)
    if ser is None or not ser.is_open:
        messagebox.showwarning("未連線", f"無法開啟 {PORT}，請確認序列埠設定與接線。")
        return
    ser.reset_input_buffer()
    ser.write(bytes([0xAA] + grid))
    res = ser.read(1)
    if res:
        res_lbl.config(text=f"{label_prefix}：{res.decode('ascii', errors='replace')}")
    else:
        res_lbl.config(text="逾時：未收到 PIC18 回應")

def send_and_predict():
    send_grid(buf_to_8x8_gray())

def test_official_sample():
    global sample_idx
    d = sample_idx % 10
    sample_idx += 1
    send_grid(SAMPLES[d], label_prefix=f"官方測試樣本({d}) → PIC18 辨識")

root = tk.Tk()
root.title("PIC18F4520 手寫數字辨識 (UART DEMO)")

top = tk.Frame(root)
top.pack(padx=10, pady=10)
canvas = tk.Canvas(top, width=SIZE, height=SIZE, bg="black")
canvas.pack(side=tk.LEFT, padx=10)
canvas.bind("<ButtonPress-1>", on_press)
canvas.bind("<B1-Motion>", paint)
canvas.bind("<ButtonRelease-1>", on_release)

right = tk.Frame(top)
right.pack(side=tk.LEFT, padx=10)
tk.Label(right, text="8x8 灰階傳送預覽").pack()
preview = tk.Canvas(right, width=120, height=120, bg="black")
preview.pack(pady=5)

btn_frame = tk.Frame(root)
btn_frame.pack(pady=5)
tk.Button(btn_frame, text="送出辨識", width=11, command=send_and_predict).pack(side=tk.LEFT, padx=4)
tk.Button(btn_frame, text="清除畫布", width=11, command=clear).pack(side=tk.LEFT, padx=4)
tk.Button(btn_frame, text="測官方樣本", width=11, command=test_official_sample).pack(side=tk.LEFT, padx=4)

res_lbl = tk.Label(root, text="辨識結果：--", font=("Arial", 16, "bold"))
res_lbl.pack(pady=5)
status_lbl = tk.Label(root, text="", font=("Arial", 10))
status_lbl.pack(pady=5)

connect_serial()
root.mainloop()
