#!/usr/bin/env python3
"""Print the exact DEX shape of Instagram's RoundedCornerFrameLayout drawing path.

Branch-only investigation helper. It deliberately parses DEX directly (no global xref
analysis) so a 150 MB APK finishes quickly, while still exposing exact operands,
registers, try blocks, field types, and Canvas helpers.
"""
from __future__ import annotations

import sys
from pathlib import Path

from androguard.core.apk import APK
from androguard.core.dex import DEX

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


def find_class(dexes, descriptor):
    for dex in dexes:
        for cls in dex.get_classes():
            if cls.get_name() == descriptor:
                return dex, cls
    return None, None


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: inspect_instagram_439.py APK")
    apk_path = Path(sys.argv[1])
    print("apk=", apk_path, "size=", apk_path.stat().st_size)
    apk = APK(str(apk_path))
    raw_dexes = list(apk.get_all_dex())
    print("dex_count=", len(raw_dexes))
    dexes = [DEX(raw) for raw in raw_dexes]

    target_dex, target_class = find_class(dexes, TARGET)
    if target_class is None:
        raise SystemExit(f"missing {TARGET}")
    print("target superclass=", target_class.get_superclassname())
    methods = [m for m in target_class.get_methods() if m.get_name() == "dispatchDraw"]
    if len(methods) != 1:
        raise SystemExit(f"expected one dispatchDraw, found {len(methods)}")
    draw = methods[0]
    dump_method(draw, "RoundedCornerFrameLayout.dispatchDraw")

    print("\n=== invoke operands (ordered) ===")
    for ins in draw.get_code().get_bc().get_instructions():
        if ins.get_name().startswith("invoke-"):
            print(f"{ins.get_name():<28} {output(ins)}")

    field_types = set()
    print("\n=== target fields ===")
    for field in target_class.get_fields():
        desc = field.get_descriptor()
        field_types.add(desc)
        print(field.get_name(), desc)

    # Dump Canvas-taking methods on direct object-field classes. This identifies the rounded
    # painter by behavior, not by an obfuscated symbol name.
    for desc in sorted(field_types):
        if not (desc.startswith("L") and desc.endswith(";")):
            continue
        _, cls = find_class(dexes, desc)
        if cls is None:
            continue
        for m in cls.get_methods():
            descriptor = m.get_descriptor()
            if "Landroid/graphics/Canvas;" in descriptor:
                dump_method(m, f"field-type Canvas method {desc}->{m.get_name()}{descriptor}")


if __name__ == "__main__":
    main()
