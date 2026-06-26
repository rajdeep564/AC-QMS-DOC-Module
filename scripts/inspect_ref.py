import zipfile, xml.etree.ElementTree as ET
NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

def inspect_body_tables(path, label, only_range=None):
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    body = root.find(f"{NS}body")
    tables = list(body.findall(f".//{NS}tbl"))
    print(f"\n=== {label} — {len(tables)} body tables ===")
    for i, tbl in enumerate(tables):
        if only_range and i not in only_range:
            continue
        grid = tbl.find(f"{NS}tblGrid")
        cols = [int(c.get(f"{NS}w", 0)) for c in grid.findall(f"{NS}gridCol")] if grid is not None else []
        # first cell text
        first = tbl.find(f".//{NS}tc")
        text = "".join(t.text or "" for t in first.findall(f".//{NS}t"))[:70] if first is not None else ""
        print(f"  [{i}] sum={sum(cols):5d}  cols={cols}")
        print(f"       first_cell: \"{text}\"")

BASE = "C:/Users/asus/Desktop/aditya_chemicals"

inspect_body_tables(f"{BASE}/MOA Glycine IP.docx", "MOA REF (all 8)")
inspect_body_tables(f"{BASE}/Spec Glycine IP.docx", "SPEC REF (all 4)")
inspect_body_tables(f"{BASE}/GLYCINE IP.docx", "PROTOCOL REF — missing tables [22-26]", only_range=range(22, 27))
