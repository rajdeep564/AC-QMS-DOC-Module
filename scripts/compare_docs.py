"""Compare generated docs against reference originals."""
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tests.docx_structure import compare_reference_subset, diff_fingerprints, extract_docx_fingerprint


def compare(label, ref, gen):
    print(f"\n{'=' * 55}")
    print(f"  {label}")
    print(f"{'=' * 55}")

    rp = extract_docx_fingerprint(ref)
    gp = extract_docx_fingerprint(gen)

    print("\n  PAGE SETUP (section 0 margins)")
    ref_m = (rp.get("sections") or [{}])[0].get("margins") or {}
    gen_m = (gp.get("sections") or [{}])[0].get("margins") or {}
    for k in ("top", "right", "bottom", "left", "header", "footer"):
        rv = ref_m.get(k, "—")
        gv = gen_m.get(k, "—")
        ok = "OK" if rv == gv else "DIFF"
        flag = "" if rv == gv else "  <- DIFF"
        print(f"    {ok}  {k:<14}  ref={rv:<8} gen={gv}{flag}")

    print(f"\n  PAPER  ref={rp.get('paper')}  gen={gp.get('paper')}")

    print(f"\n  HEADER PARTS  ref={rp.get('header_parts')}  gen={gp.get('header_parts')}")
    print(f"  FOOTER PARTS  ref={rp.get('footer_parts')}  gen={gp.get('footer_parts')}")

    rb = rp.get("body_table_grids") or []
    gb = gp.get("body_table_grids") or []
    print(f"\n  BODY TABLES  ref={len(rb)}  gen={len(gb)}")
    for i in range(max(len(rb), len(gb))):
        r = rb[i] if i < len(rb) else None
        g = gb[i] if i < len(gb) else None
        ok = "OK" if r == g else "DIFF"
        if r != g:
            print(f"    {ok}  table[{i}]  DIFF")
            if r:
                print(f"           ref={r}  sum={sum(r)}")
            if g:
                print(f"           gen={g}  sum={sum(g)}")
        else:
            print(f"    {ok}  table[{i}]  {r}  sum={sum(r)}")

    rh = (rp.get("header_table_grids") or {}).get("header2.xml", [])
    gh = (gp.get("header_table_grids") or {}).get("header2.xml", [])
    print(f"\n  REPEATING HEADER (header2.xml) TABLE GRID")
    if rh == gh:
        print(f"    OK  {rh}  sum={sum(rh[0]) if rh else 0}")
    else:
        print(f"    DIFF")
        if rh:
            print(f"           ref={rh}")
        if gh:
            print(f"           gen={gh}")

    ok, msg = compare_reference_subset(rp, gp)
    print(f"\n  REFERENCE SUBSET: {'OK' if ok else 'DIFF'}")
    if not ok:
        print(msg)

    full_diff = diff_fingerprints(rp, gp)
    if full_diff != "No differences.":
        print(f"\n  FULL FINGERPRINT DIFF (first 2000 chars):")
        print(full_diff[:2000])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Compare DOCX structural fingerprints")
    parser.add_argument("reference", type=Path, help="Reference DOCX path")
    parser.add_argument("generated", type=Path, help="Generated DOCX path")
    parser.add_argument("--label", default="COMPARE", help="Label for output")
    args = parser.parse_args()
    compare(args.label, args.reference, args.generated)
