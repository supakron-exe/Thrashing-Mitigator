# Beam Roadmap — Backend / OS Core (จับมือทำ Day 1-7)

> หน้าที่: Logic ทั้งหมด + ทฤษฎีสไลด์ 3.2 | เวลา: วันละ 5-6 ชม.
> ไฟล์ที่บีมเป็นเจ้าของ: `core/simulator.py`, `core/paging.py`, `core/monitor.py`, `core/detector.py`, `core/partition.py`
> ห้ามเปลี่ยนชื่อฟังก์ชัน (ทีมเรียกใช้อยู่): `simulate`, `logical_to_physical`, `split_bits`, `get_memory_stats`, `detect_thrashing`, `place_process`, `compact`

อ่าน `Main-Plan.md` ก่อนไฟล์นี้

---

## ภาพรวม 7 วันของบีม

- Day 1: FIFO (+LRU/OPT ตั้งไข่) → ต้องได้ 15
- Day 2: ครบ 5 algos + 3 ชุดเลขหนังสือ + paging ตัวเลข
- Day 3: monitor + detector + partition logic
- Day 4: paging bits + compact + สไลด์ทฤษฎี
- Day 5: ช่วยดีบัก + เทสเครื่องจริง
- Day 6: อัดคลิปพาร์ท simulator + เตรียมตอบคำถาม
- Day 7: Freeze + ซ้อม 3 นาที

---

## DAY 1 — Simulator ตั้งไข่ (3-4 ชม.)

### เป้าหมาย Day 1
รันคำสั่งเดียวแล้วได้ `faults=15`

### ขั้น 1.1: สร้างไฟล์ (30 นาที)
สร้าง `core/__init__.py` (ไฟล์เปล่า) + `core/simulator.py` โครงนี้:

```python
def simulate(ref, frames, algo="FIFO"):
    if algo == "FIFO":
        return _fifo(ref, frames)
    # Day 1 ทำแค่ FIFO ก่อน LRU/OPT เอาโครงไว้
    ...

def _fifo(ref, frames):
    mem = []          # frames ปัจจุบัน
    queue = []        # ลำดับเข้า FIFO
    steps = []        # เก็บทุกคอลัมน์
    is_fault = []
    faults = 0
    for page in ref:
        if page in mem:
            is_fault.append(False)
        else:
            faults += 1
            is_fault.append(True)
            if len(mem) < frames:
                mem.append(page)
                queue.append(page)
            else:
                victim = queue.pop(0)
                idx = mem.index(victim)
                mem[idx] = page
                queue.append(page)
        steps.append(list(mem))  # copy สำคัญ!
    return {"faults": faults, "rate": faults/len(ref), "steps": steps, "is_fault": is_fault}
```

กับดัก: `steps.append(mem)` โดยไม่ copy → ทุกคอลัมน์จะเหมือนกันหมด ต้อง `list(mem)`

### ขั้น 1.2: เทส (1 ชม.)
รันใน terminal (อยู่โฟลเดอร์โปรเจค):

```
python -c "from core.simulator import simulate; print(simulate([7,0,1,2,0,3,0,4,2,3,0,3,2,1,2,0,1,7,0,1],3,'FIFO'))"
```

**ผลที่ต้องได้ถึงเรียกว่าเสร็จ:**
- `faults=15`
- `rate=0.75` (15/20)
- `len(steps)=20`, `len(is_fault)=20`
- ถ้าได้ 14/16: เช็คว่านับ fault ตอน mem ยังไม่เต็มด้วยไหม (ต้องนับ), เช็คว่า `queue` เตะตัวแรกจริงไหม

ลอง LRU/OPT แบบหยาบต่อถ้ามีเวลา (ไม่ต้องตรงก็ได้วันนี้)

### ขั้น 1.3: ส่งงานคืนนี้
- push `core/simulator.py`
- บอกทีมในแชทว่า `steps` หน้าตาแบบ `[[7],[7,0],[7,0,1],...]` + `is_fault=[True,True,...]`

**Done Day 1 =** คำสั่งข้างบนได้ 15 + push แล้ว
ถ้าไม่เสร็จ: ห้ามขึ้น Day 2 ห้ามไปทำ paging ก่อน

---

## DAY 2 — ครบ 5 algos + 3 ชุดเลข + paging ตัวเลข (5-6 ชม.)

### เป้าหมาย Day 2
เลข 3 ชุดตรงหนังสือ 100% + ฟังก์ชันแปลง address ได้

### ขั้น 2.1: LRU (1 ชม.)
หลัก: เตะตัวที่ `last_used` เก่าสุด

```python
last = {}  # page -> เวลาล่าสุดที่ใช้
time = 0
for page in ref:
    time += 1
    if page in mem:
        last[page] = time
    else:
        faults += 1
        if len(mem) < frames:
            mem.append(page)
        else:
            victim = min(mem, key=lambda x: last.get(x, -1))
            # เสมอใช้ FIFO เสริม: ถ้า last เท่ากัน min จะเอาตัวแรกใน mem = FIFO โดยธรรมชาติ
            mem[mem.index(victim)] = page
        last[page] = time
    ...
```

เทส: ชุดหลัก 3f LRU **ต้องได้ 12**

### ขั้น 2.2: OPT (1 ชม.)
หลัก: มองไปข้างหน้า เตะตัวที่ใช้อีกทีช้าสุด / ไม่ใช้อีกเลย

```python
for i, page in enumerate(ref):
    if page not in mem:
        faults += 1
        if len(mem) < frames:
            mem.append(page)
        else:
            future = ref[i+1:]
            # หา next use ของแต่ละตัวใน mem
            def next_use(x):
                return future.index(x) if x in future else float('inf')
            victim = max(mem, key=next_use)
            mem[mem.index(victim)] = page
```

เทส: ชุดหลัก 3f OPT **ต้องได้ 9**

### ขั้น 2.3: LFU/MFU (1 ชม.)
หลัก: นับ `count`, เข้าใหม่รีเซ็ต 1, เสมอใช้ FIFO เสริม (ต้องเก็บ `insert_time` ด้วย)

```python
count = {}
insert = {}
# hit: count[page]+=1
# miss + เต็ม: LFU -> min(count), MFU -> max(count), ถ้าเท่ากันเอา insert เก่าสุด
```

เทส: ชุดหลัก 3f **LFU=13, MFU=15**

### ขั้น 2.4: เทส 3 ชุดบังคับ (30 นาที)
สร้าง `test_day2.py` ชั่วคราวแล้วรัน:

```python
from core.simulator import simulate
# ชุดหลัก
assert simulate([7,0,1,2,0,3,0,4,2,3,0,3,2,1,2,0,1,7,0,1],3,'FIFO')['faults']==15
assert simulate([7,0,1,2,0,3,0,4,2,3,0,3,2,1,2,0,1,7,0,1],3,'OPT')['faults']==9
assert simulate([7,0,1,2,0,3,0,4,2,3,0,3,2,1,2,0,1,7,0,1],3,'LRU')['faults']==12
# Belady
assert simulate([1,2,3,4,1,2,5,1,2,3,4,5],3,'FIFO')['faults']==9
assert simulate([1,2,3,4,1,2,5,1,2,3,4,5],4,'FIFO')['faults']==10
# ตัวอย่าง 3.2.ก
ref3=[2,3,2,1,5,2,4,5,3,2,5,2]
assert simulate(ref3,3,'FIFO')['faults']==9
assert simulate(ref3,3,'LRU')['faults']==7
assert simulate(ref3,3,'OPT')['faults']==6
print("PASS Day2")
```

**ต้องได้:** `PASS Day2` ถ้า fail ตัวเดียวให้แก้ก่อนนอน ห้ามข้าม

### ขั้น 2.5: paging ตัวเลข (1 ชม.)
สร้าง `core/paging.py`:

```python
def logical_to_physical(p,d,f,page_size):
    return f*page_size + d

def split_bits(addr, offset_bits):
    d = addr & ((1<<offset_bits)-1)
    p = addr >> offset_bits
    return (p, d)
```

เทส:
- `logical_to_physical(1,478,6,1024) == 6622` (6*1024+478)
- `split_bits(1502,10) == (1,478)` (เพราะ 1502 = 1*1024+478)

**Done Day 2 =** `PASS Day2` + 6622 ถูก + push 2 ไฟล์

---

## DAY 3 — monitor + detector + partition logic (4-5 ชม.)

### เป้าหมาย Day 3
ทีมเอาของบีมขึ้นกราฟได้คืนนี้

### ขั้น 3.1: monitor.py (1.5 ชม.)
```python
import psutil
def get_memory_stats():
    vm = psutil.virtual_memory()
    return {
      "total": vm.total,
      "available": vm.available,
      "percent": vm.percent,
      "cpu": psutil.cpu_percent(interval=0.5),
    }
```
เทส: `python -c "from core.monitor import get_memory_stats; print(get_memory_stats())"` **ต้องได้:** percent ตรง Task Manager ±5%

หมายเหตุ: page fault จริงบน Windows อ่านยาก ให้ทีมใช้ `percent` เป็นหลักก่อน ไม่ต้องหา fault counter วันนี้

### ขั้น 3.2: detector.py (1 ชม.)
```python
def detect_thrashing(stats):
    p = stats["percent"]
    if p >= 85:
        return ("Thrashing", "RAM เต็ม + เสี่ยง thrashing: ปิดโปรเซส / กด Optimize / ลดงาน")
    elif p >= 75:
        return ("Warning", "เริ่มแน่น: เตรียม Optimize")
    else:
        return ("Normal", "ปกติ")
```
เทส: ใส่ `{"percent":90}` ต้องได้ Thrashing, `80` ได้ Warning, `50` ได้ Normal

### ขั้น 3.3: partition.py logic (1.5 ชม.)
```python
def place_process(holes, size, strategy):
    # holes เช่น [600,1000,300], size=500
    # First: ตัวแรกที่พอ, Best: เล็กสุดที่พอ, Worst: ใหญ่สุดที่พอ
    # return index หรือ -1
```
เทส:
- First([600,1000,300],500) == 0
- Best([600,1000,300],500) == 0 (600 เล็กสุดที่พอ)
- Worst([600,1000,300],500) == 1 (1000 ใหญ่สุด)

**Done Day 3 =** 3 ไฟล์นี้ push + ทีม import ได้ไม่ error

---

## DAY 4 — paging bits + compact + สไลด์ (4 ชม.)

### ขั้น 4.1: split_bits + compact (2 ชม.)
- `split_bits` เทสซ้ำให้ผ่าน (ดู Day 2)
- เพิ่มใน `partition.py`:
```python
def compact(blocks):
    # blocks = [("P5",500),("hole",100),("P4",700),("hole",300),("P3",300),("hole",260)]
    # return [("P5",500),("P4",700),("P3",300),("hole",660)]
```
เทส: hole รวมต้องได้ 660 (100+300+260)

### ขั้น 4.2: สไลด์ทฤษฎี 4 หน้า (2 ชม.)
ทำใน PowerPoint/Google Slides ส่งให้ทีม:
1. Demand paging 6 ขั้น (ลอกชื่อจาก Main-Plan)
2. Valid-Invalid bit (รูป 3.2.C)
3. ตาราง FIFO15 vs OPT9 vs LRU12
4. Belady 9 vs 10 + อธิบายว่าเกิดเฉพาะ FIFO

**Done Day 4 =** compact ได้ 660 + สไลด์ 4 หน้าส่งทีม

---

## DAY 5 — ช่วยดีบัก + เทสเครื่องจริง (2-3 ชม. ทำพร้อมทีม)

1. เปิด `main.py` กับทีม กด Preset ทุกปุ่มดูเลขตรงไหม
2. เปิด Chrome 10 แท็บ + Notepad 10 อัน ดู `percent` ขึ้น 80+ ไหม ถ้าไม่ถึงให้บอกทีมลด threshold ชั่วคราวเป็น 70 เพื่อถ่ายคลิป
3. รัน `test_day2.py` อีกรอบต้อง PASS
4. **Done Day 5 =** ไม่มีเลขผิด + percent อ่านตรง

---

## DAY 6 — คลิป + เตรียมตอบ (2 ชม.)

1. อัดหน้าจอตัวเอง 3 นาที: กด Preset หลัก → ชี้ FIFO15 vs OPT9 → กด Belady → ชี้ 9vs10 → พูดสูตร rate
2. เตรียมคำตอบ 4 ข้อ (เขียนใส่กระดาษ):
   - ทำไม OPT ดีสุดแต่ใช้จริงไม่ได้? (ตอบ: ต้องรู้อนาคต)
   - Belady เกิดกับ LRU ไหม? (ตอบ: ไม่ เกิดเฉพาะ FIFO)
   - valid bit ดูตรงไหน? (ตอบ: page table บอกว่าเพจอยู่ใน RAM หรือ backing store)
   - 6 ขั้น page fault มีอะไร? (ท่องจาก Main-Plan)
3. ส่งคลิปดิบให้ทีมตัดต่อ

**Done Day 6 =** มีคลิปดิบ + ตอบ 4 ข้อได้โดยไม่อ่านโพย

---

## DAY 7 — Freeze + ซ้อม (1-2 ชม.)

- เช้า: รัน test ทั้งหมดอีกรอบ ห้ามแก้ logic ถ้าไม่พัง
- บ่าย: ซ้อมพูดพาร์ทตัวเอง 3 นาทีจับเวลา (ดูสคริปต์ใน Main-Plan) อัดมือถือ 1 รอบ
- **Done Day 7 =** พูดจบใน 3 นาที ไม่เกิน 3:30

---

## เช็คลิสต์ส่งท้ายทุกคืน (copy ไปติ๊กในแชท)

- [ ] ไฟล์ push แล้วชื่อถูก?
- [ ] เทสตัวเลขผ่าน?
- [ ] ทีม import แล้วไม่ error?
- [ ] พรุ่งนี้ทำอะไรต่อรู้แล้ว?

ถ้าติดให้ถามทีมก่อน 22:00 อย่าดองข้ามวัน
