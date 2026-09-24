"""Paging address translation — Day 2 Beam.

Contract (ห้ามเปลี่ยนชื่อ ทีมเรียกใช้อยู่):
    logical_to_physical(p, d, f, page_size) -> int  # f*page_size + d
    split_bits(addr, offset_bits) -> (p, d)

อ้างอิงหนังสือ 3.1.10:
    logical 1502 (p=1, d=478) -> physical 6622 (f=6, d=478)
    เพราะ page_size = 1024 (offset 10 bits): 6*1024+478 = 6622
    และ 1502 = 1*1024+478
"""

from __future__ import annotations


def logical_to_physical(p: int, d: int, f: int, page_size: int) -> int:
    return f * page_size + d


def split_bits(addr: int, offset_bits: int) -> tuple[int, int]:
    d = addr & ((1 << offset_bits) - 1)
    p = addr >> offset_bits
    return (p, d)


if __name__ == "__main__":
    assert logical_to_physical(1, 478, 6, 1024) == 6622
    assert split_bits(1502, 10) == (1, 478)
    print("PASS paging 6622")
