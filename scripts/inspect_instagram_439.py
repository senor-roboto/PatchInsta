#!/usr/bin/env python3
"""Print the exact DEX shape of Instagram's RoundedCornerFrameLayout drawing path.

This is a branch-only investigation helper. It intentionally prints method/field operands,
registers, try blocks and nearby helper bodies so the production patch can match semantics
instead of guessing from opcode names.
"""
from __future__ import annotations

import sys
from pathlib import Path

from androguard.misc import AnalyzeAPK

TARGET = "Lcom/instagram/ui/widget/roundedcornerlayout/RoundedCornerFrameLayout;"


def output(ins):
    try:
        return ins.get_output()
    except TypeError:
        try:
            return ins.get_output(0)
        except Exception:
            return ""
    except Exception as exc:
        return f"<output-error {type(exc).__name__}: {exc}>"


def dump_method(method, label):
    print(f"\n=== {label} ===")
    print("class=", method.get_class_name())
    print("name=", method.get_name())
    print("descriptor=", method.get_descriptor())
    code = method.get_code()
    if code is None:
        print("NO CODE")
        return
    print(
        "registers=", code.get_registers_size(),
        "ins=", code.get_ins_size(),
        "outs=", code.get_outs_size(),
        "tries=", code.get_tries_size(),
    )
    try:
        tries = list(code.get_tries())
    except Exception:
        tries = []
    for i, tr in enumerate(tries):
        print(f"try[{i}]={tr}")
    off = 0
    for index, ins in enumerate(code.get_bc().get_instructions()):
        print(f"{index:02d} @{off:04x} {ins.get_name():<28} {output(ins)}")
        off += ins.get_length()


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: inspect_instagram_439.py APK")
    apk = Path(sys.argv[1])
    print("apk=", apk, "size=", apk.stat().st_size)
    _, dexes, _ = AnalyzeAPK(str(apk))
    target_class = None
    target_dex = None
    for dex in dexes:
        for cls in dex.get_classes():
            if cls.get_name() == TARGET:
                target_class = cls
                target_dex = dex
                break
        if target_class is not None:
            break
    if target_class is None:
        raise SystemExit(f"missing {TARGET}")
    print("target superclass=", target_class.get_superclassname())
    methods = [m for m in target_class.get_methods() if m.get_name() == "dispatchDraw"]
    if len(methods) != 1:
        raise SystemExit(f"expected one dispatchDraw, found {len(methods)}")
    draw = methods[0]
    dump_method(draw, "RoundedCornerFrameLayout.dispatchDraw")

    # Resolve every non-framework method referenced from dispatchDraw. Dumping these bodies
    # reveals which invoke actually performs the corner/stroke paint and which invokes are
    # tracing/cleanup/finally machinery that must stay intact.
    refs = []
    for ins in draw.get_code().get_bc().get_instructions():
        name = ins.get_name()
        text = output(ins)
        if name.startswith("invoke-") and "->" in text:
            refs.append(text)
    print("\n=== invoke operands (ordered) ===")
    for r in refs:
        print(r)

    # Androguard's textual operand is enough to find the exact class/name/descriptor again.
    # Dump all methods of direct object-field classes referenced by the target class that take
    # Canvas; this gives us a stable semantic painter candidate even if names are obfuscated.
    field_types = set()
    for field in target_class.get_fields():
        try:
            field_types.add(field.get_descriptor())
        except Exception:
            pass
    print("\n=== target field types ===")
    for t in sorted(field_types):
        print(t)
    for desc in sorted(field_types):
        if not (desc.startswith("L") and desc.endswith(";")):
            continue
        cls = target_dex.get_class(desc)
        if cls is None:
            # Class may live in another multidex file.
            for dex in dexes:
                cls = dex.get_class(desc)
                if cls is not None:
                    break
        if cls is None:
            continue
        for m in cls.get_methods():
            d = m.get_descriptor()
            if "Landroid/graphics/Canvas;" in d:
                dump_method(m, f"field-type Canvas method {desc}->{m.get_name()}{d}")


if __name__ == "__main__":
    main()
