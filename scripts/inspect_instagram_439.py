#!/usr/bin/env python3
"""Print the exact DEX shape of Instagram 439's RoundedCornerFrameLayout drawing path.

Branch-only investigation helper. It deliberately parses DEX directly (no global xref
analysis) so a 150 MB APK finishes quickly, while still exposing exact operands,
registers, try blocks, helper state, and implementations of the Canvas strategy used by
RoundedCornerFrameLayout. This is evidence collection, not a production matcher.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from androguard.core.apk import APK
from androguard.core.dex import DEX

TARGET = "Lcom/instagram/ui/widget/roundedcornerlayout/RoundedCornerFrameLayout;"
CANVAS = "Landroid/graphics/Canvas;"
METHOD_REF_RE = re.compile(r"(L[^;]+;)->([^ (]+)\(([^)]*)\)(\S+)")


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


def normalize_interfaces(cls):
    try:
        raw = cls.get_interfaces()
    except Exception:
        return []
    if raw is None:
        return []
    if isinstance(raw, str):
        # Androguard may expose a compact string such as "LX/A; LX/B;".
        return re.findall(r"L[^;]+;", raw)
    out = []
    try:
        values = list(raw)
    except Exception:
        values = []
    for value in values:
        if isinstance(value, str):
            out.extend(re.findall(r"L[^;]+;", value))
        else:
            try:
                text = value.get_name()
            except Exception:
                text = str(value)
            out.extend(re.findall(r"L[^;]+;", text))
    return out


def method_refs(method):
    refs = []
    code = method.get_code()
    if code is None:
        return refs
    for ins in code.get_bc().get_instructions():
        if not ins.get_name().startswith("invoke-"):
            continue
        text = output(ins)
        match = METHOD_REF_RE.search(text)
        if match:
            owner, name, params, ret = match.groups()
            refs.append((owner, name, f"({params}){ret}", ins.get_name(), text))
    return refs


def dump_class_summary(cls, label):
    print(f"\n=== {label} ===")
    print("class=", cls.get_name())
    print("super=", cls.get_superclassname())
    print("interfaces=", normalize_interfaces(cls))
    print("fields:")
    for field in cls.get_fields():
        print(" ", field.get_name(), field.get_descriptor())
    print("methods:")
    for method in cls.get_methods():
        print(" ", method.get_name(), method.get_descriptor(), "code=", method.get_code() is not None)


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: inspect_instagram_439.py APK")
    apk_path = Path(sys.argv[1])
    print("apk=", apk_path, "size=", apk_path.stat().st_size)
    apk = APK(str(apk_path))
    raw_dexes = list(apk.get_all_dex())
    print("dex_count=", len(raw_dexes))
    dexes = [DEX(raw) for raw in raw_dexes]

    _, target_class = find_class(dexes, TARGET)
    if target_class is None:
        raise SystemExit(f"missing {TARGET}")
    print("target superclass=", target_class.get_superclassname())
    methods = [m for m in target_class.get_methods() if m.get_name() == "dispatchDraw"]
    if len(methods) != 1:
        raise SystemExit(f"expected one dispatchDraw, found {len(methods)}")
    draw = methods[0]
    dump_method(draw, "RoundedCornerFrameLayout.dispatchDraw")

    refs = method_refs(draw)
    print("\n=== invoke operands (ordered) ===")
    for owner, name, desc, opcode, text in refs:
        print(f"{opcode:<28} {text}")

    field_types = set()
    print("\n=== target fields ===")
    for field in target_class.get_fields():
        desc = field.get_descriptor()
        field_types.add(desc)
        print(field.get_name(), desc)

    # A00 is the state holder on the real 439 class. Dump its structure so nested strategy
    # fields (for example the Canvas strategy observed from dispatchDraw) become explicit.
    nested_types = set()
    for desc in sorted(field_types):
        if not (desc.startswith("L") and desc.endswith(";")):
            continue
        _, cls = find_class(dexes, desc)
        if cls is None:
            continue
        dump_class_summary(cls, f"direct field type {desc}")
        for field in cls.get_fields():
            nested = field.get_descriptor()
            if nested.startswith("L") and nested.endswith(";"):
                nested_types.add(nested)

    # Dump every non-framework owner invoked by dispatchDraw, including interface contracts.
    invoked_owners = {owner for owner, _, _, _, _ in refs if owner.startswith("L")}
    for owner in sorted(invoked_owners):
        if owner.startswith("Landroid/") or owner == TARGET:
            continue
        _, cls = find_class(dexes, owner)
        if cls is not None:
            dump_class_summary(cls, f"invoked owner {owner}")

    # Resolve the actual implementations of interface methods used by dispatchDraw. This is
    # the key evidence for AUE/B8l/B66: identify which one clips, restores, and/or paints.
    interface_refs = {}
    for owner, name, desc, _, _ in refs:
        _, owner_cls = find_class(dexes, owner)
        if owner_cls is None:
            continue
        try:
            flags = owner_cls.get_access_flags_string()
        except Exception:
            flags = ""
        if "interface" in flags.lower() or owner in nested_types:
            interface_refs.setdefault(owner, set()).add((name, desc))

    for interface, wanted in sorted(interface_refs.items()):
        print(f"\n=== implementations of {interface} for {sorted(wanted)} ===")
        count = 0
        for dex in dexes:
            for cls in dex.get_classes():
                if interface not in normalize_interfaces(cls):
                    continue
                count += 1
                print("implementor=", cls.get_name(), "super=", cls.get_superclassname())
                for method in cls.get_methods():
                    key = (method.get_name(), method.get_descriptor())
                    if key in wanted or (CANVAS in method.get_descriptor() and method.get_name() in {n for n, _ in wanted}):
                        dump_method(method, f"implementation {cls.get_name()}->{method.get_name()}{method.get_descriptor()}")
        print("implementor_count=", count)


if __name__ == "__main__":
    main()
