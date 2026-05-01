"""Deterministic parser for mapping raw text to structure components."""

from __future__ import annotations

import re
from dataclasses import dataclass

from pulp_builder.models.story_structure import ExtractedEvidence, StoryNode


PARSER_VERSION = "deterministic-v1"

SETTING_KEYWORDS = {
    "temple",
    "ruin",
    "city",
    "island",
    "cave",
    "tomb",
    "jungle",
    "tower",
    "village",
    "library",
    "archive",
    "sea",
    "ship",
    "desert",
    "mountain",
    "castle",
    "cellar",
    "laboratory",
}
EVENT_KEYWORDS = {
    "finds",
    "discovers",
    "steals",
    "escapes",
    "fights",
    "kills",
    "follows",
    "enters",
    "opens",
    "betrays",
    "reveals",
    "summons",
    "dies",
    "survives",
    "flees",
}
ENDING_KEYWORDS = {
    "dies",
    "escapes",
    "survives",
    "madness",
    "curse",
    "treasure",
    "revealed",
    "betrays",
    "vanishes",
    "returns",
    "burns",
    "loses",
}

COMPONENT_HINTS: dict[str, set[str]] = {
    "q1-hook-with-menace": {"hook", "menace", "corpse", "attack", "danger", "chase", "blood", "warning"},
    "q1-hero-desire": {"wants", "seeks", "goal", "treasure", "revenge", "rescue", "escape", "mission"},
    "q1-initial-trouble": {"trouble", "problem", "obstacle", "blocked", "threat", "hunt", "ambush"},
    "q1-hint-of-deeper-menace": {"hint", "sign", "symbol", "ancient", "curse", "cult", "shadow", "deeper"},
    "q2-first-attempt": {"attempt", "plan", "tries", "enters", "searches", "tracks", "investigates"},
    "q2-first-complication": {"complication", "fails", "worse", "injured", "trapped", "counterattack"},
    "q2-clue-or-pattern": {"clue", "pattern", "evidence", "map", "script", "mark", "record"},
    "q2-rising-stakes": {"stakes", "cost", "risk", "deadline", "spreads", "more", "rising"},
    "q3-reversal": {"reversal", "sudden", "turn", "ambushed", "collapse", "backfires"},
    "q3-betrayal-or-false-safety": {"betrayal", "betrays", "traitor", "false", "safe", "trap"},
    "q3-terrible-revelation": {"revelation", "truth", "reveals", "ancient", "real", "origin", "curse"},
    "q3-deathtrap-or-contact": {"deathtrap", "contact", "monster", "entity", "ritual", "summons", "sealed"},
    "q4-final-confrontation": {"final", "confrontation", "fight", "destroy", "battle", "last"},
    "q4-cost-of-survival": {"cost", "survival", "lost", "sacrifice", "wounded", "scarred"},
    "q4-resolution": {"resolution", "aftermath", "returns", "escapes", "buries", "ends"},
    "q4-final-sting": {"sting", "still", "again", "not", "waits", "laughs", "returns", "shadow"},
}


@dataclass(slots=True)
class ParseResult:
    """Parser output with full source and mapped structure."""

    raw_story_text: str
    root_nodes: list[StoryNode]


class DeterministicParser:
    """Simple transparent parser with keyword scoring and placeholders."""

    version = PARSER_VERSION

    def parse(self, raw_story_text: str, story_form: dict) -> ParseResult:
        """Parse raw text and map paragraphs to story components."""

        root_nodes = self._build_nodes(story_form)
        paragraphs = self._split_paragraphs(raw_story_text)
        assignments = self._assign_paragraphs(paragraphs, root_nodes)
        self._apply_assignments(assignments)
        self._insert_placeholders(root_nodes)
        return ParseResult(raw_story_text=raw_story_text, root_nodes=root_nodes)

    @staticmethod
    def _split_paragraphs(raw_story_text: str) -> list[str]:
        normalized = raw_story_text.replace("\r\n", "\n").replace("\r", "\n")
        chunks = [chunk.strip() for chunk in re.split(r"\n\s*\n", normalized) if chunk.strip()]
        if chunks:
            return chunks
        stripped = normalized.strip()
        return [stripped] if stripped else []

    def _build_nodes(self, story_form: dict) -> list[StoryNode]:
        roots: list[StoryNode] = []
        for q_index, quarter in enumerate(story_form["quarters"]):
            quarter_node = StoryNode(
                node_id=quarter["quarter_id"],
                title=quarter["title"],
                node_type="quarter",
                order_index=q_index,
                description=quarter.get("description", ""),
                required=True,
                completion_state="missing",
            )
            children: list[StoryNode] = []
            for c_index, component in enumerate(quarter["components"]):
                children.append(
                    StoryNode(
                        node_id=component["id"],
                        parent_id=quarter["quarter_id"],
                        title=component["title"],
                        node_type="component",
                        order_index=c_index,
                        description=component.get("description", ""),
                        guidance_prompt=component.get("guidance_prompt", ""),
                        required=component.get("required", True),
                        completion_state="missing",
                    )
                )
            quarter_node.children = children
            roots.append(quarter_node)
        return roots

    def _assign_paragraphs(self, paragraphs: list[str], root_nodes: list[StoryNode]) -> dict[str, list[str]]:
        component_nodes = self._component_nodes(root_nodes)
        assignments: dict[str, list[str]] = {node.node_id: [] for node in component_nodes}

        for paragraph in paragraphs:
            best_component_id = self._best_component_id(paragraph, component_nodes)
            if best_component_id is not None:
                assignments[best_component_id].append(paragraph)

        return assignments

    def _best_component_id(self, paragraph: str, component_nodes: list[StoryNode]) -> str | None:
        paragraph_tokens = self._tokens(paragraph)
        best_id: str | None = None
        best_score = 0

        for node in component_nodes:
            score = self._score_paragraph(node.node_id, paragraph_tokens)
            if score > best_score:
                best_score = score
                best_id = node.node_id

        return best_id if best_score > 0 else None

    def _score_paragraph(self, component_id: str, paragraph_tokens: set[str]) -> int:
        hints = set(COMPONENT_HINTS.get(component_id, set()))
        hints.update(self._tokens(component_id.replace("-", " ")))
        score = len(hints & paragraph_tokens)

        if paragraph_tokens & SETTING_KEYWORDS:
            score += 1
        if paragraph_tokens & EVENT_KEYWORDS:
            score += 1
        if paragraph_tokens & ENDING_KEYWORDS and component_id.startswith("q4"):
            score += 2

        return score

    def _apply_assignments(self, assignments: dict[str, list[str]]) -> None:
        for component_id, paragraphs in assignments.items():
            if not paragraphs:
                continue
            text = "\n\n".join(paragraphs)
            names = self._extract_names(text)
            settings = sorted(self._tokens(text) & SETTING_KEYWORDS)
            events = sorted(self._tokens(text) & EVENT_KEYWORDS)
            endings = sorted(self._tokens(text) & ENDING_KEYWORDS)

            evidence_bits = []
            if names:
                evidence_bits.append(f"names={', '.join(names[:6])}")
            if settings:
                evidence_bits.append(f"settings={', '.join(settings)}")
            if events:
                evidence_bits.append(f"events={', '.join(events)}")
            if endings:
                evidence_bits.append(f"ending_words={', '.join(endings)}")

            node = self._component_by_id(component_id)
            node.story_text = text
            node.extracted_evidence = [
                ExtractedEvidence(
                    source="paragraph",
                    text=paragraphs[0],
                    confidence=min(1.0, 0.4 + 0.1 * len(paragraphs)),
                    notes="; ".join(evidence_bits),
                )
            ]
            node.is_placeholder = False
            node.was_placeholder = False
            node.missing_reason = ""
            node.completion_state = "drafted"

    def _insert_placeholders(self, root_nodes: list[StoryNode]) -> None:
        for node in self._component_nodes(root_nodes):
            if node.required and not node.story_text.strip():
                node.is_placeholder = True
                node.was_placeholder = True
                node.missing_reason = (
                    "The imported story idea does not yet contain enough clear material "
                    "for this required component."
                )
                if not node.suggested_questions:
                    node.suggested_questions = self._default_questions(node)
                node.completion_state = "missing"

    @staticmethod
    def _default_questions(node: StoryNode) -> list[str]:
        return [
            f"What concrete beat should happen for '{node.title}'?",
            "Which character acts, and what do they risk here?",
            "What detail would make this section specific and pulp-toned?",
        ]

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return {token.lower() for token in re.findall(r"[A-Za-z']+", text)}

    @staticmethod
    def _extract_names(text: str) -> list[str]:
        # Simple heuristic: one- or two-word capitalized names.
        candidates = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b", text)
        deduped: list[str] = []
        for candidate in candidates:
            if candidate not in deduped:
                deduped.append(candidate)
        return deduped

    def _component_nodes(self, root_nodes: list[StoryNode]) -> list[StoryNode]:
        nodes: list[StoryNode] = []
        self._component_index: dict[str, StoryNode] = {}
        for quarter in root_nodes:
            for component in quarter.children:
                nodes.append(component)
                self._component_index[component.node_id] = component
        return nodes

    def _component_by_id(self, component_id: str) -> StoryNode:
        return self._component_index[component_id]
