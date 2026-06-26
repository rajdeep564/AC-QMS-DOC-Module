"""Compare generated docs against reference originals."""
import sys, zipfile, xml.etree.ElementTree as ET
from pathlib import Path

NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def page_setup(path):
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        root = ET.fromstring(z.read("word/document.xml"))
    body = root.find(f"{NS}body")
    sect = body.find(f"{NS}sectPr")
    pg_mar = sect.find(f"{NS}pgMar")
    pg_brd = sect.find(f"{NS}pgBorders")
    pg_sz  = sect.find(f"{NS}pgSz")

    r = {}
    if pg_mar is not None:
        for attr in ("top", "right", "bottom", "left", "header", "footer"):
            r[attr] = pg_mar.get(f"{NS}{attr}", "?")
    if pg_sz is not None:
        r["w"] = pg_sz.get(f"{NS}w", "?")
        r["h"] = pg_sz.get(f"{NS}h", "?")
    r["border"] = "YES" if pg_brd is not None else "NO"
    if pg_brd is not None:
        top = pg_brd.find(f"{NS}top")
        r["border_type"] = top.get(f"{NS}val", "?") if top is not None else "?"
    r["headers"] = sorted(n.split("/")[-1] for n in names if "header" in n and n.endswith(".xml"))
    r["footers"] = sorted(n.split("/")[-1] for n in names if "footer" in n and n.endswith(".xml"))
    return r


def body_table_grids(path):
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    body = root.find(f"{NS}body")
    out = []
    for tbl in body.findall(f".//{NS}tbl"):
        grid = tbl.find(f"{NS}tblGrid")
        if grid is not None:
            cols = [int(c.get(f"{NS}w", 0)) for c in grid.findall(f"{NS}gridCol")]
            out.append(cols)
    return out


def header_table_grids(path, fname):
    with zipfile.ZipFile(path) as z:
        if f"word/{fname}" not in z.namelist():
            return []
        root = ET.fromstring(z.read(f"word/{fname}"))
    out = []
    for tbl in root.findall(f".//{NS}tbl"):
        grid = tbl.find(f"{NS}tblGrid")
        if grid is not None:
            cols = [int(c.get(f"{NS}w", 0)) for c in grid.findall(f"{NS}gridCol")]
            out.append(cols)
    return out


def compare(label, ref, gen):
    print(f"\n{'='*55}")
    print(f"  {label}")
    print(f"{'='*55}")

    rp = page_setup(ref)
    gp = page_setup(gen)

    print("\n  PAGE SETUP")
    for k in ("w", "h", "top", "right", "bottom", "left", "header", "footer", "border", "border_type"):
        rv = rp.get(k, "—")
        gv = gp.get(k, "—")
        ok = "✓" if rv == gv else "✗"
        flag = "" if rv == gv else f"  ← DIFF"
        print(f"    {ok}  {k:<14}  ref={rv:<8} gen={gv}{flag}")

    print(f"\n  HEADER/FOOTER FILES")
    print(f"    ref headers: {rp['headers']}")
    print(f"    gen headers: {gp['headers']}")
    print(f"    ref footers: {rp['footers']}")
    print(f"    gen footers: {gp['footers']}")

    rb = body_table_grids(ref)
    gb = body_table_grids(gen)
    print(f"\n  BODY TABLES  ref={len(rb)}  gen={len(gb)}")
    for i in range(max(len(rb), len(gb))):
        r = rb[i] if i < len(rb) else None
        g = gb[i] if i < len(gb) else None
        ok = "✓" if r == g else "✗"
        if r is None:
            print(f"    {ok}  table[{i}]  MISSING in ref  gen={g}  sum={sum(g)}")
        elif g is None:
            print(f"    {ok}  table[{i}]  ref={r}  sum={sum(r)}  MISSING in gen")
        elif r != g:
            print(f"    {ok}  table[{i}]  DIFF")
            print(f"           ref={r}  sum={sum(r)}")
            print(f"           gen={g}  sum={sum(g)}")
        else:
            print(f"    {ok}  table[{i}]  {r}  sum={sum(r)}")

    print(f"\n  REPEATING HEADER (header2.xml) TABLE GRID")
    rh = header_table_grids(ref, "header2.xml")
    gh = header_table_grids(gen, "header2.xml")
    for i in range(max(len(rh), len(gh)) if rh or gh else 0):
        r = rh[i] if i < len(rh) else None
        g = gh[i] if i < len(gh) else None
        ok = "✓" if r == g else "✗"
        if r == g:
            print(f"    {ok}  table[{i}]  {r}  sum={sum(r)}")
        else:
            print(f"    {ok}  table[{i}]  DIFF")
            if r: print(f"           ref={r}  sum={sum(r)}")
            if g: print(f"           gen={g}  sum={sum(g)}")


BASE = Path("C:/Users/asus/Desktop/aditya_chemicals")
SOP  = Path("C:/Users/asus/Desktop/aditya_chemicals/sop/generated")

compare("MOA",      BASE / "MOA Glycine IP.docx",  SOP / "example_glycine_moa.docx")
compare("SPEC",     BASE / "Spec Glycine IP.docx", SOP / "example_glycine_spec.docx")
compare("PROTOCOL", BASE / "GLYCINE IP.docx",      SOP / "example_glycine_protocol.docx")
