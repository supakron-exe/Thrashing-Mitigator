# Team Roadmap — Frontend / Integrate / ส่งงาน (จับมือทำ Day 1-7)

> หน้าที่: GUI ทั้งหมด + ต่อของบีม + วิดีโอ/สไลด์ | เวลา: วันละ 5-6 ชม.
> ไฟล์ที่ทีมเป็นเจ้าของ: `main.py`, `requirements.txt`, `core/optimizer.py`, `ui/app.py`, `ui/dashboard_tab.py`, `ui/thrashing_tab.py`, `ui/process_tab.py`, `ui/simulator_tab.py`, `ui/paging_partition_tab.py`
> เรียกของบีมด้วยชื่อนี้เท่านั้น: `simulate`, `get_memory_stats`, `detect_thrashing`, `optimize`, `logical_to_physical`, `split_bits`, `place_process`, `compact`

อ่าน `Main-Plan.md` ก่อนไฟล์นี้

---

## ภาพรวม 7 วันของทีม

- Day 1: โครง 5 Tabs + Dashboard pie อ่านค่าจริง
- Day 2: optimizer จริง + Thrashing/Process หยาบ
- Day 3: Simulator Tab เต็ม (งานหนักสุด) + ต่อ detector
- Day 4: Paging/Partition Tab + รวมทั้งหมดให้รันไม่ error
- Day 5: เทสเครื่องจริง + screenshot
- Day 6: สไลด์ 10 หน้า + Demo.mp4
- Day 7: ซ้อม 4 นาที + เช็คโน้ตบุ๊กวันจริง

---

## DAY 1 — โครง + Dashboard (3-4 ชม.)

### เป้าหมาย Day 1
ดับเบิลคลิก `python main.py` แล้วเห็นหน้าต่าง 5 Tabs + pie ตรง Task Manager

### ขั้น 1.1: ติดตั้ง + ไฟล์ตั้งต้น (30 นาที)
1. รัน:
```
pip install psutil matplotlib
```
2. สร้าง `requirements.txt` 2 บรรทัด:
```
psutil
matplotlib
```
3. สร้าง `main.py`:
```python
from ui.app import App
if __name__ == "__main__":
    App().mainloop()
```
4. สร้าง `ui/__init__.py` (เปล่า) + `ui/app.py`:
```python
import tkinter as tk
from tkinter import ttk
from ui.dashboard_tab import DashboardTab
# Day 1 import แค่ Dashboard ก่อน Tabs อื่นใส่ Frame เปล่าไปก่อน
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Thrashing Mitigator")
        self.geometry("900x600")
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)
        nb.add(DashboardTab(nb), text="Dashboard")
        nb.add(ttk.Frame(nb), text="Thrashing")
        nb.add(ttk.Frame(nb), text="Process")
        nb.add(ttk.Frame(nb), text="Simulator")
        nb.add(ttk.Frame(nb), text="Paging+Partition")
```

### ขั้น 1.2: Dashboard pie (2 ชม.)
สร้าง `ui/dashboard_tab.py`:
- ใช้ `psutil.virtual_memory()` อ่าน `total, available, percent`
- วาด pie ด้วย `matplotlib.figure.Figure` + `FigureCanvasTkAgg`:
  - `used = total-available`, `slices=[used, available]`, labels `["In Use","Available"]`
- Label 3 อัน: `Total: X GB`, `Available: Y GB`, `In Use: Z%`
- ปุ่ม `Optimize Now` (Day 1 กดแล้วแค่ `gc.collect()` + Refresh pie พอ ยังไม่ต้องเรียก optimizer จริง)
- ปุ่ม `Refresh` + `after(2000, refresh)` ให้ pie ขยับทุก 2 วิ

กับดัก: matplotlib ใน Tk ต้อง `canvas.draw()` ทุกครั้งหลังอัปเดต ไม่งั้น pie ค้าง

### ขั้น 1.3: เทส Day 1
รัน `python main.py` **ต้องได้ถึงเรียกว่าเสร็จ:**
- [ ] หน้าต่างเปิด ไม่ error
- [ ] เห็น 5 Tabs
- [ ] pie % ตรงกับ Task Manager → Performance → Memory ±5%
- [ ] กด Optimize แล้ว pie refresh (เห็นเลขขยับ)

ถ่ายรูปจอส่งบีมในแชท

**Done Day 1 =** 4 ข้อนี้ครบ + push `main.py, ui/app.py, ui/dashboard_tab.py, requirements.txt`

---

## DAY 2 — optimizer จริง + 2 Tabs หยาบ (5 ชม.)

### เป้าหมาย Day 2
กด Optimize แล้ว Available เพิ่มจริง (เห็นเป็น MB)

### ขั้น 2.1: optimizer.py (1.5 ชม.)
สร้าง `core/optimizer.py`:
```python
import gc
def optimize(mode="free"):
    import psutil
    before = psutil.virtual_memory().available
    try:
        import ctypes
        # Windows เท่านั้น
        ctypes.windll.psapi.EmptyWorkingSet(ctypes.windll.kernel32.GetCurrentProcess())
    except Exception:
        pass  # ไม่ใช่ Windows หรือไม่มีสิทธิ์ ให้ข้าม
    gc.collect()
    after = psutil.virtual_memory().available
    freed_mb = max(0, (after-before)/1024/1024)
    return round(freed_mb, 1)
```
- `mode` รับ `free/standby/defrag_sim` แต่ Day 2 ทำไส้เดียวกันก่อน (defrag จริงทำไม่ได้อยู่แล้ว ไปอธิบายในสไลด์ว่าเป็น simulation)
- เทส: `python -c "from core.optimizer import optimize; print(optimize('free'))"` **ต้องได้:** ตัวเลข (0 ก็ได้แต่ต้องไม่ error)

หมายเหตุ: ถ้า error `AccessDenied` → คลิกขวา terminal → Run as Administrator แล้วรันใหม่

### ขั้น 2.2: ต่อ Dashboard (1 ชม.)
- เปลี่ยนปุ่ม Optimize ให้เรียก `optimize()` จริง + Label `Freed: X MB`
- เพิ่ม Entry `threshold (เช่น 20)` หมายถึง Available% ต่ำกว่านี้ให้ auto + Check `Run when CPU idle` (Day 2 ทำแค่ UI ติ๊กได้ ยังไม่ต้อง auto จริงก็ได้)
- เทส: เปิด Chrome 5 แท็บ จำ Available → กด Optimize → **ต้องได้:** Available เพิ่ม (50MB+ ถือว่าผ่าน) ถ่าย before/after ไว้

### ขั้น 2.3: Thrashing + Process แบบหยาบ (2 ชม.)
สร้าง `ui/thrashing_tab.py`:
- Label ไฟ `status` (พื้นหลังเขียว/เหลือง/แดง) + Label `advice`
- กราฟเส้น RAM% เส้นเดียว ใช้ `ax.plot(history)` + `after(1000, update)` เก็บ `history` 60 จุดล่าสุด
- เรียก `get_memory_stats()` + `detect_thrashing()` จากของบีม (ถ้าบีมยังไม่ส่ง ให้ mock `{"percent":80}` ไปก่อน)

สร้าง `ui/process_tab.py`:
- `ttk.Treeview` columns `PID/Name/MB` โชว์ Top 10 sort by RSS จาก `psutil.process_iter(['pid','name','memory_info'])`
- ปุ่ม `Refresh` + `Kill` (`p.kill()` ใน try/except) + `Suspend` (`p.suspend()` ใน try/except ถ้าไม่ได้ให้โชว์ popup ข้าม)
- เทส: กด Refresh **ต้องได้:** เห็น chrome.exe / python.exe + กด Kill Notepad ที่เปิดเทสได้ (อย่า kill ผิดตัว)

แก้ `ui/app.py` ให้ import 2 tabs จริงแทน Frame เปล่า

**Done Day 2 =** Optimize เห็น MB + 2 tabs เปิดได้ไม่ error + push

---

## DAY 3 — Simulator Tab เต็ม (5-6 ชม. งานหนักสุด)

### เป้าหมาย Day 3
กรอก ref กด Run แล้วตารางขึ้น + Label 15/75%

### ขั้น 3.1: วาง Layout (1 ชม.)
`ui/simulator_tab.py` มี:
- Entry `ref` (default ใส่ `7,0,1,2,0,3,0,4,2,3,0,3,2,1,2,0,1,7,0,1` ไว้เลย)
- Spinbox `frames` 1-7 (default 3)
- Radio `FIFO/LRU/OPT/LFU/MFU` (default FIFO)
- ปุ่ม `Run` + ปุ่ม Preset 3 ปุ่ม: `Main` / `Belady` / `3.2ก`
  - Main: ref ชุดหลัก frames 3
  - Belady: ref `1,2,3,4,1,2,5,1,2,3,4,5` frames 3 (มีปุ่มย่อย 3f/4f)
  - 3.2ก: ref `2,3,2,1,5,2,4,5,3,2,5,2` frames 3
- `Treeview` สำหรับตาราง steps + Label `faults + rate` + กราฟแท่งเทียบ

### ขั้น 3.2: ต่อ simulate (2 ชม.)
```python
from core.simulator import simulate
ref = list(map(int, entry.get().split(",")))
res = simulate(ref, frames, algo)
# res = {"faults","rate","steps","is_fault"}
```
- ล้าง Treeview เก่า → ใส่ `steps` ทีละคอลัมน์ (column = ครั้งที่, row = frame ที่) + แถวสุดท้าย `F` ตรงที่ fault
- Label: `Faults: 15  Rate: 15/20=75%`
- กราฟแท่ง: เรียก `simulate` 3 รอบ FIFO/LRU/OPT กับ ref เดียวกันแล้ว `ax.bar(["FIFO","LRU","OPT"],[15,12,9])`

กับดัก: `ref.split(",")` มีช่องว่าง → ต้อง `.strip()` ทุกตัว ไม่งั้น `int(" 0")` error บางเครื่อง

### ขั้น 3.3: เทส 3 ปุ่ม (1 ชม.)
- กด Main + Run **ต้องได้:** ตาราง 20 คอลัมน์ + `15, 75%`
- เปลี่ยน Radio OPT + Run **ต้องได้:** `9`
- กด Belady 4f + Run **ต้องได้:** `10`
- ถ้าเลขไม่ตรง → แคปจอส่งบีมทันที อย่าแก้ logic เอง

### ขั้น 3.4: ต่อ detector เข้า Thrashing Tab (1 ชม.)
- เอา `history` มาอัปเดตสีไฟทุกวินาที + โชว์ `advice` จากบีม
- **ต้องได้:** เปิด Chrome เยอะๆ แล้วไฟแดง (ถ้าไม่แดงให้ลด threshold ในโค้ดเป็น 70 ชั่วคราว)

**Done Day 3 =** 3 ปุ่มได้เลขถูก + ไฟแดงขึ้นได้ + push `simulator_tab.py`

---

## DAY 4 — Paging/Partition Tab + รวมทั้งหมด (4-5 ชม.)

### เป้าหมาย Day 4
กรอก 1502 ได้ 6622 + ได้ก้อน 660K + `main.py` ไม่ error

### ขั้น 4.1: ครึ่งบน Paging (2 ชม.)
`ui/paging_partition_tab.py` แบ่ง `top/bottom`:
- แถว 1: Entry `p,d,f,size` (default 1,478,6,4) + ปุ่ม `=` + Label physical → เรียก `logical_to_physical` **ต้องได้ 6622**
- แถว 2: Entry `addr,offset_bits` (default 1502,10) + ปุ่ม Split + Label `p,d` → เรียก `split_bits` **ต้องได้ p1,d478**

### ขั้น 4.2: ครึ่งล่าง Partition (2 ชม.)
- Entry `holes (เช่น 600,1000,300)` + Entry `size (500)` + Radio First/Best/Worst + ปุ่ม Place → Label `ลงช่อง index X` (เรียก `place_process`)
- Canvas วาดแท่งหน่วยความจำ (ใช้ `tk.Canvas` วาดสี่เหลี่ยมง่ายๆ ไม่ต้องสวย) + ปุ่ม `Compaction` → เรียก `compact` → วาดใหม่ + Label `hole รวม 660K`
- เทส: ใส่ holes ตามตัวอย่าง **ต้องได้:** First=0, Worst=1, compact=660

### ขั้น 4.3: รวม + ล้าง error (1 ชม.)
- แก้ `app.py` ให้ครบ 5 tabs จริง
- รัน `python main.py` ไล่กดทุกปุ่ม **ต้องได้:** ไม่มี popup error แดง
- push ทั้งหมด

**Done Day 4 =** 6622 + 660K โชว์บนจอได้ + รันรวมไม่พัง = ฟีเจอร์ครบ 100%

---

## DAY 5 — เทสเครื่องจริง + screenshot (2-3 ชม. ทำพร้อมบีม)

1. เปิด Chrome/Edge 10 แท็บ + Notepad 10 อัน → ดูไฟ Thrashing (ถ่ายคลิปสั้น 20 วิ)
2. กด Optimize ถ่าย before/after (ต้องเห็น Freed MB)
3. กด Simulator 3 preset ถ่ายรูปเลข 15/9/10
4. กรอก Paging ถ่ายรูป 6622
5. เอาโปรเจคไปรันเครื่องเพื่อน/เครื่องบีม: `pip install -r requirements.txt` → `python main.py` **ต้องได้:** ติดใน 2 นาที
6. ลิสต์บั๊ก 5 อันดับแรกเท่านั้น ห้ามเพิ่มจอใหม่

**Done Day 5 =** มีรูปครบ 5 ชุด + รันเครื่องอื่นได้

---

## DAY 6 — สไลด์ 10 หน้า + Demo.mp4 (4-5 ชม.)

### สไลด์ (บีมส่งทฤษฎี 4 หน้ามาให้แล้ว เอามาประกอบ)
1. ปก: Thrashing Mitigator + บีม ทีม + วิชา OS
2. Wise vs เรา (ตาราง 4 ข้อ + ที่เพิ่ม)
3. Swapping/Virtual (รูป 3.2.A/B)
4. Page Fault 6 ขั้น + valid bit (รูป 3.2.C/D)
5. ผล Simulator ชุดหลัก (ตาราง FIFO15 OPT9 LRU12)
6. Belady 9vs10 + ตัวอย่าง 3.2.ก 9/7/6 + สูตร rate
7. Paging 1502→6622 + Compaction 660K
8. Demo จริง (แปะรูป Day 5)
9. วิธีแก้ thrashing 4 ข้อ
10. สรุป + Q&A + ลิงก์ repo

### วิดีโอ
- เอาคลิปดิบบีม + คลิปตัวเองมาตัด (ใช้ Clipchamp/CapCut) ยาว 5 นาที พูดตามสคริปต์ Main-Plan
- Export `ThrashingMitigator_Demo.mp4` 720p พอ (ไฟล์เล็กส่งง่าย) + อัป Drive + backup ในมือถือ
- ตั้งชื่อไฟล์ส่งไม่มีภาษาไทยกันเพี้ยน

**Done Day 6 =** มีไฟล์ 2 อย่างใน Drive เปิดได้ + Freeze โค้ดห้ามแตะ

---

## DAY 7 — ซ้อม + เช็คของ (1-2 ชม.)

- เช้า: เปิด `main.py` รอบสุดท้าย กดทุกปุ่มเร็วๆ 1 รอบ
- บ่าย: ซ้อมพูดพาร์ทตัวเอง 4 นาทีจับเวลา (1 monitor + 2 optimize + 1 สรุป) อัดมือถือดูเอง
- เช็คลิสต์วันจริง: โน้ตบุ๊ก + สายชาร์จ + เมาส์ + portable Python + วิดีโอในมือถือ + สไลด์ PDF สำรอง (กันฟอนต์เพี้ยน)
- **Done Day 7 =** พูดจบ 4 นาที ไม่เกิน 4:30 + ของครบใส่กระเป๋า

---

## เช็คลิสต์ส่งท้ายทุกคืน

- [ ] `python main.py` เปิดติด?
- [ ] ปุ่มใหม่กดแล้วไม่ error?
- [ ] เลขตรงกับของบีม?
- [ ] push + แคปจอส่งบีมแล้ว?
- [ ] พรุ่งนี้ทำอะไรต่อรู้แล้ว?

ติดให้ถามบีมก่อน 22:00 อย่าดองข้ามวัน
