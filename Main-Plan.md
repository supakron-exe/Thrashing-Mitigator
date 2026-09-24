# Thrashing Mitigator — Main Plan (2 คนต้องอ่าน)

> วิชา OS บทที่ 3 Storage Management | สมาชิก: บีม + ทีม | Stack: Python + Tkinter
> ส่ง: Present 9 ต.ค. 69 เวลา 13:00 (5-10 นาที) + demo video + presentation files
> แผน: 7 วัน งานครบเท่า 14 วัน | รัน: `pip install -r requirements.txt` แล้ว `python main.py`

---

## 1. โปรเจคนี้คืออะไร (พูดให้อาจารย์ฟังใน 1 นาที)

**Thrashing Mitigator = Wise Memory Optimizer ฉบับวิชา OS + ตัวสอนทฤษฎี**

Wise Memory Optimizer ตัวจริงทำ 4 อย่าง:
1. Free up In-Use RAM
2. Empty Standby RAM
3. Defrag RAM
4. Auto Optimize (เมื่อ Available ต่ำกว่า threshold / CPU idle)

ของเราลอกทั้ง 4 อย่าง + เพิ่มสิ่งที่ Wise ไม่มีเพื่อให้ได้คะแนน OS:
- **ตรวจจับ Thrashing** ไม่ใช่แค่ดู RAM% แต่ดูสูตร OS: `RAM% สูง + Page Fault ถี่ + CPU ต่ำ + Disk สูง = Thrashing`
- **Simulator สอนทฤษฎี** ใช้ตัวเลขเดียวกับหนังสืออาจารย์เป๊ะ เพื่อพรีเซนต์

นิยาม Thrashing ที่ใช้พูดวันจริง:
> CPU ทำงานน้อยลงทั้งที่งานเยอะ เพราะ RAM เต็ม OS มัวแต่ swap page เข้า-ออกดิสก์ (page fault ถี่) ดิสก์หมุนไม่หยุดแต่ CPU ต้องรอเพจ วิธีแก้: เพิ่ม frames / ลด multiprogramming (kill/suspend โปรเซส) / ใช้ replacement ดีๆ (OPT > LRU > FIFO) / compaction รวม hole

---

## 2. Mapping เนื้อหาอาจารย์ → ฟีเจอร์ (ห้ามหลุด ตารางนี้คือคะแนน)

| หัวข้อหนังสือ | รูป/ตัวอย่าง | อยู่ใน Tab ไหน | วิธีเดโม |
|---|---|---|---|
| 3.1.5 Swapping + 3.2 Virtual Memory | รูป 3.2.A/B virtual→physical→backing store | Dashboard + Thrashing | อธิบายว่า RAM เต็มแล้ว swap out ลงดิสก์ |
| 3.2.1 Demand Paging + Valid-Invalid bit | รูป 3.2.C (V/I) + รูป 3.2.D 6 ขั้นตอน | Thrashing Monitor + สไลด์ | โชว์ 6 ขั้น: 1.reference → 2.trap → 3.page on backing store → 4.bring in free frame → 5.reset table → 6.restart |
| 3.2.2 Page Replacement + สูตร `fault rate = faults/total` | ชุดหลัก `7,0,1,2,0,3,0,4,2,3,0,3,2,1,2,0,1,7,0,1` 3 frames: FIFO15 OPT9 LRU12 LFU13 MFU15 | Simulator (หลัก) | กด Preset แล้วต้องได้เลขนี้เป๊ะ |
| Belady's Anomaly | `1,2,3,4,1,2,5,1,2,3,4,5` 3f=9 แต่ 4f=10 | Simulator | โชว์ว่าเพิ่ม frame แล้ว fault เพิ่ม (เกิดเฉพาะ FIFO) |
| ตัวอย่าง 3.2.ก | `2,3,2,1,5,2,4,5,3,2,5,2` FIFO9 LRU7 OPT6 | Simulator Preset 3 | โชว์ว่า OPT ดีสุด |
| 3.1.10 Paging Address | `logical 1502 (p=1,d=478) → physical 6622 (f=6,d=478)` สูตร `physical = f*size + d`, bit 6+10 | Paging Tab | กรอกแล้วได้ 6622 |
| 3.1.7-3.1.9 Placement + Compaction | P1-P5 (600K,1000K,300K,700K,500K ใน 2160K) + รูป 3.1.I `[P5,100K,P4,300K,P3,260K] → [P5,P4,P3,660K]` | Partition Tab + ปุ่ม Optimize | บอกว่า Optimize คือไอเดีย Compaction |

ทริค: เปิดสไลด์รูปหนังสือเทียบกับโปรแกรมข้างๆ กัน

---

## 3. สถาปัตยกรรม + โครงไฟล์ (ล็อกแล้วห้ามเปลี่ยนชื่อกลางทาง)

```
thrashing-mitigator/
├── main.py                        # ทีม: entry point เปิด ui.app
├── requirements.txt               # psutil, matplotlib
├── core/
│   ├── simulator.py               # บีม: simulate(ref,frames,algo)
│   ├── paging.py                  # บีม: logical_to_physical + split_bits
│   ├── monitor.py                 # บีม: get_memory_stats()
│   ├── detector.py                # บีม: detect_thrashing()
│   ├── optimizer.py               # ทีม: optimize(mode)
│   └── partition.py               # บีม logic + ทีมวาด: place_process + compact
└── ui/
    ├── app.py                     # ทีม: Tk + Notebook 5 tabs
    ├── dashboard_tab.py           # ทีม
    ├── thrashing_tab.py           # ทีม
    ├── process_tab.py             # ทีม
    ├── simulator_tab.py           # ทีม (เรียกของบีม)
    └── paging_partition_tab.py    # ทีม (เรียกของบีม)
```

### 3.1 สัญญาเชื่อมงาน (Contract) — สำคัญสุด

```python
# บีมต้องส่งชื่อนี้เป๊ะ ทีมเรียกชื่อนี้เป๊ะ
def simulate(ref: list[int], frames: int, algo: str) -> dict:
    # algo = FIFO/LRU/OPT/LFU/MFU
    # return {"faults": int, "rate": float, "steps": list[list[int]], "is_fault": list[bool]}
    ...

def logical_to_physical(p:int, d:int, f:int, page_size:int) -> int:
    # return f*page_size + d

def split_bits(addr:int, offset_bits:int) -> tuple[int,int]:
    # return (p, d)

def get_memory_stats() -> dict:
    # return {"total":int, "available":int, "percent":float, "cpu":float}

def detect_thrashing(stats:dict) -> tuple[str,str]:
    # return ("Normal"|"Warning"|"Thrashing", "advice ไทย...")

def optimize(mode:str) -> float:
    # mode = free/standby/defrag_sim, return freed_mb

def place_process(holes:list[int], size:int, strategy:str) -> int:
    # strategy = First/Best/Worst, return index หรือ -1 ถ้าใส่ไม่ได้

def compact(blocks:list) -> list:
    ...
```

กฎ:
- RAM > 85 = Thrashing, > 75 = Warning, else Normal (ปรับได้วัน Day 5 ถ้าไม่แดง)
- LFU/MFU: เข้าใหม่รีเซ็ต count=1, เสมอใช้ FIFO เสริม (ตามหนังสือ)
- `steps` ต้องเป็น list ยาวเท่า ref เพื่อให้ทีมวาดตารางได้เลย

---

## 4. Timeline 7 วัน (ภาพรวม)

| วัน | บีม | ทีม | ผลรวมคืนนั้น |
|---|---|---|---|
| Day 1 | simulator FIFO/LRU/OPT ตั้งไข่ | โครง 5 Tabs + Dashboard pie | `main.py` เปิดติด + FIFO=15 ใน terminal |
| Day 2 | ครบ 5 algos + 3 ชุดเลข + paging ตัวเลข | optimizer จริง + Thrashing/Process หยาบ | กด Optimize แล้ว RAM เพิ่มจริง |
| Day 3 | monitor + detector + partition logic | Simulator Tab เต็ม + ต่อ detector | กด Run ได้ตาราง 15 + ไฟแดงขึ้น |
| Day 4 | paging bits + compact + สไลด์ทฤษฎี | Paging/Partition Tab + รวมทั้งหมด | กรอก 1502 ได้ 6622 + ได้ก้อน 660K |
| Day 5 | ช่วยดีบัก + เทสเครื่องจริง | เทส E2E + screenshot | รันเครื่องเพื่อนได้ใน 2 นาที |
| Day 6 | อัดพาร์ท simulator + เตรียมตอบคำถาม | สไลด์ 10 หน้า + Demo.mp4 | มีไฟล์ส่งครบใน Drive |
| Day 7 | Freeze + ซ้อมพาร์ท 3 นาที | ซ้อมพาร์ท 4 นาที + เช็คโน้ตบุ๊ก | พูดจบ 7-8 นาที |

เจอกันทุกคืน 21:00 30 นาที เปิด `main.py` ด้วยกัน ไม่ติดห้ามนอน

Milestone บังคับ:
- คืน Day 3: ตารางขึ้นจอได้
- คืน Day 5: Optimize เห็นผลจริง
- Day 6: Freeze ห้ามเพิ่มฟีเจอร์

---

## 5. เกณฑ์ผ่าน (Definition of Done รวม)

1. ตัวเลข 3 ชุดตรงหนังสือ 100% (15/9/12/13/15, 9vs10, 9/7/6)
2. `logical 1502 → 6622` ถูก
3. เปิด Chrome เยอะๆ แล้วไฟแดงขึ้นได้ (ยอมลด threshold เป็น 70 เพื่อเดโมได้)
4. กด Optimize แล้ว Available เพิ่ม (50MB ขึ้นไปถือว่าผ่าน)
5. `pip install -r requirements.txt` + `python main.py` รันได้ใน 2 นาทีบนเครื่องอื่น
6. มี `Demo.mp4` สำรอง + สไลด์ 10 หน้าใน Drive

---

## 6. ความเสี่ยง + แผนสำรอง

| เสี่ยง | แผนสำรอง (ใช้วัน Day 5 ถ้าติด) |
|---|---|
| `EmptyWorkingSet` ต้อง Admin / error | ใช้ `gc.collect()` อย่างเดียว + mock freed_mb อย่าฝืน |
| `suspend()` โปรเซสไม่ได้ (AccessDenied) | ตัดเหลือแค่ Kill อย่างเดียว |
| Matplotlib หน่วง | refresh ทุก 1s พอ ไม่ต้อง real-time |
| ตัวเลข Simulator ผิด | หยุดทุกอย่าง แก้ logic ก่อน ห้ามต่อ GUI |
| เน็ต/เครื่องวันจริงพัง | เปิดวิดีโอสำรองในมือถือแทนเดโมสด |

---

## 7. สคริปต์พรีเซนต์ 7 นาที (แบ่งกันพูด)

- 0:00-1:00 (ทีม): Wise vs เรา + เปิด Dashboard pie
- 1:00-3:00 (ทีม): เปิด Chrome เยอะๆ → ไฟแดง Thrashing → อธิบาย 6 ขั้น page fault → กด Optimize → ไฟเขียว
- 3:00-6:00 (บีม): กด Preset หลักโชว์ FIFO15 vs OPT9 + กราฟ Belady 9vs10 + ตัวอย่าง 3.2.ก 9/7/6 + สูตร rate + กรอก 1502 ได้ 6622
- 6:00-7:00 (ทีม): สรุปวิธีแก้ thrashing 4 ข้อ + Compaction 660K

คำถามอาจารย์ที่ต้องเตรียม: 6 ขั้นมีอะไร? valid bit ดูตรงไหน? ทำไม OPT ใช้จริงไม่ได้? Belady เกิดกับ LRU ไหม? (ตอบ: ไม่ เกิดเฉพาะ FIFO)

---

## 8. Git + ส่งงาน

- Branch: `main` อย่างเดียวพอ (เวลาน้อย) commit ทุกคืน `Day1-beam-sim-fifo` ฯลฯ
- ไฟล์ส่ง: `ThrashingMitigator_Demo.mp4` + `ThrashingMitigator_Slides.pptx/pdf` + ลิงก์ repo
- เช็คก่อนส่ง: ชื่อไฟล์ไม่มีภาษาไทยกันเพี้ยน, วิดีโอเปิดในมือถือได้

อ่านจบแล้วแยกไปอ่านไฟล์ของตัวเอง: `Beam-Roadmap.md` / `Team-Roadmap.md`
