"""Page replacement simulator — Day 1-2 Beam.

Contract (ห้ามเปลี่ยนชื่อ):
    simulate(ref, frames, algo) -> {"faults", "rate", "steps", "is_fault"}
    algo = FIFO / LRU / OPT / LFU / MFU
    steps = list ยาวเท่า ref, แต่ละช่องคือสำเนา frames ขณะนั้น
    is_fault = list[bool] ยาวเท่า ref
"""

from __future__ import annotations


def simulate(ref: list[int], frames: int, algo: str = "FIFO") -> dict:
    algo = algo.upper()
    if algo == "FIFO":
        return _fifo(ref, frames)
    if algo == "LRU":
        return _lru(ref, frames)
    if algo == "OPT":
        return _opt(ref, frames)
    if algo == "LFU":
        return _counting(ref, frames, most=False)
    if algo == "MFU":
        return _counting(ref, frames, most=True)
    raise ValueError(f"unknown algo: {algo} (use FIFO/LRU/OPT/LFU/MFU)")


def _finalize(faults: int, total: int, steps: list, is_fault: list) -> dict:
    return {
        "faults": faults,
        "rate": (faults / total) if total else 0.0,
        "steps": steps,
        "is_fault": is_fault,
    }


def _fifo(ref: list[int], frames: int) -> dict:
    mem: list[int] = []
    queue: list[int] = []
    steps: list[list[int]] = []
    is_fault: list[bool] = []
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
                mem[mem.index(victim)] = page
                queue.append(page)
        steps.append(list(mem))
    return _finalize(faults, len(ref), steps, is_fault)


def _lru(ref: list[int], frames: int) -> dict:
    mem: list[int] = []
    last: dict[int, int] = {}
    insert: dict[int, int] = {}
    steps: list[list[int]] = []
    is_fault: list[bool] = []
    faults = 0
    clock = 0
    for page in ref:
        clock += 1
        if page in mem:
            is_fault.append(False)
            last[page] = clock
        else:
            faults += 1
            is_fault.append(True)
            if len(mem) < frames:
                mem.append(page)
            else:
                victim = min(mem, key=lambda x: (last.get(x, -1), insert.get(x, 0)))
                mem[mem.index(victim)] = page
            last[page] = clock
            insert[page] = clock
        steps.append(list(mem))
    return _finalize(faults, len(ref), steps, is_fault)


def _opt(ref: list[int], frames: int) -> dict:
    mem: list[int] = []
    insert: dict[int, int] = {}
    steps: list[list[int]] = []
    is_fault: list[bool] = []
    faults = 0
    clock = 0
    n = len(ref)
    for i, page in enumerate(ref):
        clock += 1
        if page in mem:
            is_fault.append(False)
        else:
            faults += 1
            is_fault.append(True)
            if len(mem) < frames:
                mem.append(page)
                insert[page] = clock
            else:
                future = ref[i + 1 :]

                def next_use(x: int) -> float:
                    try:
                        return future.index(x)
                    except ValueError:
                        return float("inf")

                # ตัวที่ใช้อีกทีช้าสุด (inf = ไม่ใช้อีกเลย) ถูกเตะก่อน
                # เสมอใช้ FIFO เสริม: next_use เท่ากันเอา insert เก่าสุด
                victim = max(mem, key=lambda x: (next_use(x), -insert.get(x, 0)))
                # max + (-insert) => insert น้อยสุดชนะเมื่อ next_use เท่ากัน
                # แต่ max กับ tuple: ตัวที่สองใหญ่สุดชนะ ดังนั้นใช้ -insert ถูกแล้ว
                # ตรวจซ้ำ: ถ้า next_use เท่ากัน (เช่น inf,inf) ตัวที่ -insert ใหญ่กว่า
                # = insert น้อยกว่า = เข้าก่อน = FIFO ถูกต้อง
                mem[mem.index(victim)] = page
                insert[page] = clock
        steps.append(list(mem))
    return _finalize(faults, n, steps, is_fault)


def _counting(ref: list[int], frames: int, most: bool = False) -> dict:
    """LFU (most=False) / MFU (most=True). เข้าใหม่ count=1, เสมอใช้ FIFO เสริม."""
    mem: list[int] = []
    count: dict[int, int] = {}
    insert: dict[int, int] = {}
    steps: list[list[int]] = []
    is_fault: list[bool] = []
    faults = 0
    clock = 0
    for page in ref:
        clock += 1
        if page in mem:
            is_fault.append(False)
            count[page] = count.get(page, 0) + 1
        else:
            faults += 1
            is_fault.append(True)
            if len(mem) < frames:
                mem.append(page)
                count[page] = 1
                insert[page] = clock
            else:
                if most:
                    # MFU: count มากสุดออกก่อน, เสมอเอาเข้าก่อนออกก่อน
                    victim = max(mem, key=lambda x: (count.get(x, 0), -insert.get(x, 0)))
                else:
                    # LFU: count น้อยสุดออกก่อน, เสมอเอาเข้าก่อนออกก่อน
                    victim = min(mem, key=lambda x: (count.get(x, 0), insert.get(x, 0)))
                mem[mem.index(victim)] = page
                count[page] = 1
                insert[page] = clock
        steps.append(list(mem))
    return _finalize(faults, len(ref), steps, is_fault)


if __name__ == "__main__":
    main_ref = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
    for a in ["FIFO", "OPT", "LRU", "LFU", "MFU"]:
        r = simulate(main_ref, 3, a)
        print(f"{a}: faults={r['faults']} rate={r['rate']:.2%}")
