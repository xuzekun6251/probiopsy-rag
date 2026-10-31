"""Renumber zh manuscript citations by first appearance (assembly order) and
rebuild the reference skeleton in 03_introduction.md.

Assembly order mirrors scripts/assemble_manuscript.py. Citation tokens look
like [4], [6-8], [9,12]. The skeleton list is a plain "N. text" block under
"## 参考文献骨架" in 03_introduction.md; its (原编号 N) annotations are
updated to record the pre-renumber number of each entry.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "outputs" / "paper"

BODY_FILES = ["00_front_zh.md", "03_introduction.md", "01_methods.md",
              "02_results.md", "04_discussion.md", "05_limitations.md", "06_conclusion.md"]
SKELETON_MARK = "## 参考文献骨架"
CIT = re.compile(r"\[(\d+(?:[,\-]\d+)*)\]")


def expand(tok: str):
    nums = []
    for part in tok.split(","):
        if "-" in part:
            a, b = map(int, part.split("-"))
            nums.extend(range(a, b + 1))
        else:
            nums.append(int(part))
    return nums


def compress(nums):
    nums = sorted(set(nums))
    parts, i = [], 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        if j == i:
            parts.append(str(nums[i]))
        elif j == i + 1:
            parts.append(f"{nums[i]},{nums[j]}")
        else:
            parts.append(f"{nums[i]}-{nums[j]}")
        i = j + 1
    return ",".join(parts)


def main(apply: bool):
    full = {name: (P / name).read_text(encoding="utf-8") for name in BODY_FILES}

    # 1. first-appearance order over body text (intro: body only, skeleton excluded)
    order = []
    for name in BODY_FILES:
        body = full[name].split(SKELETON_MARK)[0] if name == "03_introduction.md" else full[name]
        for m in CIT.finditer(body):
            for n in expand(m.group(1)):
                if n not in order:
                    order.append(n)
    n_refs = max(order)
    assert sorted(order) == list(range(1, n_refs + 1)), f"citations not a permutation of 1..{n_refs}: {order}"
    mapping = {old: i + 1 for i, old in enumerate(order)}
    print(f"{len(order)} references; first-appearance order (old numbering): {order}")
    for old, new in sorted(mapping.items()):
        if old != new:
            print(f"  {old} -> {new}")
    if not any(o != n for o, n in mapping.items()):
        print("numbering already sequential; nothing to do")
        return

    # 2. rewrite citation tokens in place
    def repl(m):
        return "[" + compress(mapping[n] for n in expand(m.group(1))) + "]"

    for name in BODY_FILES:
        new_text = CIT.sub(repl, full[name])
        if new_text != full[name]:
            if apply:
                (P / name).write_text(new_text, encoding="utf-8")
            print(f"  rewritten {name}")

    # 3. rebuild the skeleton in 03_introduction.md
    intro_path = P / "03_introduction.md"
    intro = intro_path.read_text(encoding="utf-8")
    head, sep, tail = intro.partition(SKELETON_MARK)
    assert sep, "skeleton heading not found"
    tail_lines = tail.splitlines()
    note = tail_lines[0].rstrip() if tail_lines else ""
    if "2026-10-31" not in note:
        note += "；2026-10-31 仿 Tung（JMIR 2025）版式重构后按正文首次出现次序重新编号"
    body_lines = tail_lines[1:]
    start = next(i for i, ln in enumerate(body_lines) if re.match(r"^\d+\.\s", ln.strip()))
    entries = {}
    for ln in body_lines[start:]:
        if not ln.strip():
            continue
        m = re.match(r"^(\d+)\.\s+(.*)$", ln.strip())
        assert m, f"unparsed skeleton line: {ln[:60]}"
        entries[int(m.group(1))] = m.group(2)
    assert len(entries) == n_refs, f"skeleton has {len(entries)} entries, body cites {n_refs}"

    rebuilt = {}
    for old, txt in entries.items():
        if "原编号" in txt:
            txt = re.sub(r"原编号\s*\d+", f"原编号 {old}", txt)
        elif mapping[old] != old:
            txt = f"{txt}（原编号 {old}）"
        rebuilt[mapping[old]] = txt
    skeleton = SKELETON_MARK + note + "\n\n" + "\n".join(
        f"{n}. {rebuilt[n]}" for n in sorted(rebuilt)) + "\n"
    if apply:
        intro_path.write_text(head.rstrip("\n") + "\n\n" + skeleton, encoding="utf-8")
        print("  skeleton rebuilt")

    # 4. verify
    ok = True
    seen = []
    for name in BODY_FILES:
        body = full[name].split(SKELETON_MARK)[0] if name == "03_introduction.md" else full[name]
        body = CIT.sub(repl, body)
        for m in CIT.finditer(body):
            for n in expand(m.group(1)):
                if n not in seen:
                    seen.append(n)
                if n > n_refs:
                    ok = False
                    print(f"  GHOST {n} in {name}")
    monotonic = seen == sorted(set(seen))
    complete = sorted(set(seen)) == list(range(1, n_refs + 1))
    print(f"verify: complete={complete} monotonic={monotonic} order={seen}")
    if not (ok and complete and monotonic):
        sys.exit(1)


if __name__ == "__main__":
    main(apply="--apply" in sys.argv)
