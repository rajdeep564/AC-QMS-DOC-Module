"""Extract stable structural fingerprints from rendered DOCX files for golden regression."""

from __future__ import annotations

import json
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
WP_NS = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
W = f"{{{W_NS}}}"
WP = f"{{{WP_NS}}}"

WORD_XML_PREFIX = "word/"
HEADER_PREFIX = f"{WORD_XML_PREFIX}header"
FOOTER_PREFIX = f"{WORD_XML_PREFIX}footer"


def _word_xml_parts(names: list[str]) -> list[str]:
    """Return sorted word/*.xml part paths (exclude rels and media)."""
    parts = [
        n
        for n in names
        if n.startswith(WORD_XML_PREFIX)
        and n.endswith(".xml")
        and "/_rels/" not in n
        and not n.startswith(f"{WORD_XML_PREFIX}media/")
    ]
    return sorted(parts)


def _parse_xml(data: bytes) -> ET.Element:
    return ET.fromstring(data)


def _pg_mar_dict(sect_pr: ET.Element | None) -> dict[str, str] | None:
    if sect_pr is None:
        return None
    pg_mar = sect_pr.find(f"{W}pgMar")
    if pg_mar is None:
        return None
    attrs = ("top", "right", "bottom", "left", "header", "footer")
    return {k: pg_mar.get(f"{W}{k}", "") for k in attrs}


def _pg_sz_dict(sect_pr: ET.Element | None) -> dict[str, str] | None:
    if sect_pr is None:
        return None
    pg_sz = sect_pr.find(f"{W}pgSz")
    if pg_sz is None:
        return None
    return {"w": pg_sz.get(f"{W}w", ""), "h": pg_sz.get(f"{W}h", "")}


def _pg_borders_dict(sect_pr: ET.Element | None) -> dict[str, dict[str, str]] | None:
    if sect_pr is None:
        return None
    pg_brd = sect_pr.find(f"{W}pgBorders")
    if pg_brd is None:
        return None
    out: dict[str, dict[str, str]] = {}
    for side in ("top", "left", "bottom", "right"):
        el = pg_brd.find(f"{W}{side}")
        if el is not None:
            out[side] = {
                "val": el.get(f"{W}val", ""),
                "sz": el.get(f"{W}sz", ""),
                "space": el.get(f"{W}space", ""),
            }
    return out or None


def _sections_from_document(root: ET.Element) -> list[dict[str, Any]]:
    body = root.find(f"{W}body")
    if body is None:
        return []
    sections: list[dict[str, Any]] = []
    for sect_pr in body.findall(f".//{W}sectPr"):
        sections.append(
            {
                "margins": _pg_mar_dict(sect_pr),
                "paper": _pg_sz_dict(sect_pr),
                "page_borders": _pg_borders_dict(sect_pr),
            }
        )
    return sections


def _table_grids(root: ET.Element) -> list[list[int]]:
    grids: list[list[int]] = []
    for tbl in root.findall(f".//{W}tbl"):
        grid = tbl.find(f"{W}tblGrid")
        if grid is not None:
            cols = [int(c.get(f"{W}w", 0)) for c in grid.findall(f"{W}gridCol")]
            grids.append(cols)
    return grids


def _page_field_instructions(root: ET.Element) -> list[str]:
    fields: list[str] = []
    for instr in root.findall(f".//{W}instrText"):
        text = (instr.text or "").strip()
        upper = text.upper()
        if "PAGE" in upper or "NUMPAGES" in upper:
            fields.append(text)
    return fields


def _logo_extents(root: ET.Element) -> list[dict[str, str]]:
    extents: list[dict[str, str]] = []
    for extent in root.findall(f".//{WP}extent"):
        cx = extent.get("cx", "")
        cy = extent.get("cy", "")
        if cx or cy:
            extents.append({"cx": cx, "cy": cy})
    return extents


def _part_basename(part_path: str) -> str:
    return part_path.split("/")[-1]


def extract_docx_fingerprint(path: Path | str) -> dict[str, Any]:
    """Return a stable structural fingerprint for a DOCX file."""
    path = Path(path)
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        word_parts = _word_xml_parts(names)

        doc_root = _parse_xml(zf.read("word/document.xml"))
        sections = _sections_from_document(doc_root)

        header_parts = sorted(
            _part_basename(n) for n in names if n.startswith(HEADER_PREFIX) and n.endswith(".xml")
        )
        footer_parts = sorted(
            _part_basename(n) for n in names if n.startswith(FOOTER_PREFIX) and n.endswith(".xml")
        )

        header_table_grids: dict[str, list[list[int]]] = {}
        footer_table_grids: dict[str, list[list[int]]] = {}
        page_fields: list[str] = []
        logo_extents: list[dict[str, str]] = []

        for part in word_parts:
            root = _parse_xml(zf.read(part))
            basename = _part_basename(part)
            if basename.startswith("header") and basename.endswith(".xml"):
                header_table_grids[basename] = _table_grids(root)
            elif basename.startswith("footer") and basename.endswith(".xml"):
                footer_table_grids[basename] = _table_grids(root)
            page_fields.extend(_page_field_instructions(root))
            logo_extents.extend(_logo_extents(root))

    paper = sections[0]["paper"] if sections else None

    return {
        "paper": paper,
        "sections": sections,
        "header_parts": header_parts,
        "footer_parts": footer_parts,
        "body_table_grids": _table_grids(doc_root),
        "header_table_grids": header_table_grids,
        "footer_table_grids": footer_table_grids,
        "page_fields": page_fields,
        "logo_extents": logo_extents,
    }


def fingerprint_to_json(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def fingerprint_from_json(text: str) -> dict[str, Any]:
    return json.loads(text)


def diff_fingerprints(expected: dict[str, Any], actual: dict[str, Any]) -> str:
    """Human-readable diff between two fingerprints."""
    lines: list[str] = []

    def _walk(path: str, exp: Any, act: Any) -> None:
        if exp == act:
            return
        if isinstance(exp, dict) and isinstance(act, dict):
            all_keys = sorted(set(exp) | set(act))
            for key in all_keys:
                _walk(f"{path}.{key}" if path else key, exp.get(key), act.get(key))
            return
        if isinstance(exp, list) and isinstance(act, list):
            max_len = max(len(exp), len(act))
            for i in range(max_len):
                e = exp[i] if i < len(exp) else "<missing>"
                a = act[i] if i < len(act) else "<missing>"
                _walk(f"{path}[{i}]", e, a)
            return
        lines.append(f"  {path}")
        lines.append(f"    expected: {exp!r}")
        lines.append(f"    actual:   {act!r}")

    _walk("", expected, actual)
    if not lines:
        return "No differences."
    return "Structural fingerprint diff:\n" + "\n".join(lines)


def compare_reference_subset(
    reference: dict[str, Any], generated: dict[str, Any]
) -> tuple[bool, str]:
    """Compare margins, page borders, and header2 table grids (client reference check)."""
    diffs: list[str] = []

    ref_secs = reference.get("sections") or []
    gen_secs = generated.get("sections") or []
    if ref_secs and gen_secs:
        ref_m = ref_secs[0].get("margins") or {}
        gen_m = gen_secs[0].get("margins") or {}
        for key in ("top", "right", "bottom", "left", "header", "footer"):
            if ref_m.get(key) != gen_m.get(key):
                diffs.append(
                    f"margins.{key}: ref={ref_m.get(key)!r} gen={gen_m.get(key)!r}"
                )
        ref_b = ref_secs[0].get("page_borders")
        gen_b = gen_secs[0].get("page_borders")
        if ref_b != gen_b:
            diffs.append(f"page_borders: ref={ref_b!r} gen={gen_b!r}")

    ref_h2 = (reference.get("header_table_grids") or {}).get("header2.xml")
    gen_h2 = (generated.get("header_table_grids") or {}).get("header2.xml")
    if ref_h2 is not None and gen_h2 is not None and ref_h2 != gen_h2:
        diffs.append(f"header2.xml grids: ref={ref_h2!r} gen={gen_h2!r}")

    if diffs:
        return False, "\n".join(diffs)
    return True, "Reference subset matches."
