"""Automatic hierarchical section numbering: 1.0, 1.1, 1.1.1, 2.0, etc."""


class SectionNumberingEngine:
    def __init__(self, start: int = 1) -> None:
        self._counters: list[int] = []
        self._start = start

    def reset(self) -> None:
        self._counters.clear()

    def next_section(self) -> str:
        """Top-level section: 1.0, 2.0, 3.0"""
        if not self._counters:
            self._counters = [self._start]
        else:
            self._counters = [self._counters[0] + 1]
        return f"{self._counters[0]}.0"

    def next_subsection(self) -> str:
        """Subsection: 1.1, 1.2 or 2.1, 2.2"""
        if not self._counters:
            self._counters = [self._start, 1]
        elif len(self._counters) == 1:
            self._counters.append(1)
        else:
            self._counters[-1] += 1
        return ".".join(str(c) for c in self._counters)

    def next_subsubsection(self) -> str:
        """Sub-subsection: 1.1.1, 1.1.2"""
        if len(self._counters) < 2:
            self.next_subsection()
        if len(self._counters) == 2:
            self._counters.append(1)
        else:
            self._counters[-1] += 1
        return ".".join(str(c) for c in self._counters)

    def push_level(self) -> None:
        """Enter nested level."""
        if not self._counters:
            self._counters = [self._start]
        self._counters.append(0)

    def pop_level(self) -> None:
        """Exit nested level."""
        if len(self._counters) > 1:
            self._counters.pop()


def number_tests(tests: list[dict], start: int = 1) -> list[dict]:
    """Assign section numbers to a flat or nested test list."""
    engine = SectionNumberingEngine(start=start)
    numbered: list[dict] = []

    for test in tests:
        test = dict(test)
        test["section_no"] = engine.next_section()
        test["acceptance_criteria_display"] = _criteria_display(test.get("acceptance_criteria"))

        sub_tests = test.get("sub_tests") or []
        if sub_tests:
            engine.push_level()
            numbered_subs: list[dict] = []
            for sub in sub_tests:
                sub = dict(sub)
                sub["section_no"] = engine.next_subsection()
                sub["acceptance_criteria_display"] = _criteria_display(
                    sub.get("acceptance_criteria")
                )
                numbered_subs.append(sub)
            engine.pop_level()
            test["sub_tests"] = numbered_subs

        numbered.append(test)

    return numbered


def number_sop_sections(sections: list[dict], start: int = 1) -> list[dict]:
    """Assign section numbers to SOP sections and subsections."""
    engine = SectionNumberingEngine(start=start)
    result: list[dict] = []

    for section in sections:
        section = dict(section)
        section["section_no"] = engine.next_section()
        subsections = section.get("subsections") or []
        if subsections:
            engine.push_level()
            numbered_subs: list[dict] = []
            for sub in subsections:
                sub = dict(sub)
                sub["section_no"] = engine.next_subsection()
                sub_subs = sub.get("subsections") or []
                if sub_subs:
                    engine.push_level()
                    numbered_sub_subs: list[dict] = []
                    for sub_sub in sub_subs:
                        sub_sub = dict(sub_sub)
                        sub_sub["section_no"] = engine.next_subsubsection()
                        numbered_sub_subs.append(sub_sub)
                    engine.pop_level()
                    sub["subsections"] = numbered_sub_subs
                numbered_subs.append(sub)
            engine.pop_level()
            section["subsections"] = numbered_subs
        result.append(section)

    return result


def _criteria_display(criteria: object) -> str:
    if criteria is None:
        return ""
    if isinstance(criteria, str):
        return criteria
    if isinstance(criteria, dict):
        from app.schemas.product import AcceptanceCriteria

        return AcceptanceCriteria.model_validate(criteria).to_display_string()
    return str(criteria)
