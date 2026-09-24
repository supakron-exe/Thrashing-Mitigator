"""Paging address utils — Day 2 Beam.

Contract (ห้ามเปลี่ยนชื่อ):
    logical_to_physical(p, d, f, page_size) -> f*page_size + d
    split_bits(addr, offset_bits) -> (p, d)
"""

from __future__ import annotations


def logical_to_physical(p: int, d: int, f: int, page_size: int) -> int:
    return f * page_size + d


def split_bits(addr: int, offset_bits: int) -> tuple[int, int]:
    d = addr & ((1 << offset_bits) - 1)
    p = addr >> offset_bits
    return (p, d)
