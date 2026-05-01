"""LLM-assisted first-pass parser that guides deterministic mapping."""

from __future__ import annotations

from dataclasses import dataclass

from pulp_builder.services.llm_connection import LLMConnectionService
from pulp_builder.services.parser import DeterministicParser, ParseResult, StoryParser


@dataclass(slots=True)
class LLMParseArtifacts:
    """Debug artifacts from LLM first-pass import."""

    first_pass_text: str
    parser_version: str
    used_fallback: bool
    warning: str = ""


class LLMFirstPassParser(StoryParser):
    """Generate a Lester Dent recommendation, then parse deterministically."""

    version = "llm-first-pass+deterministic-v1"

    def __init__(
        self,
        llm_connection: LLMConnectionService | None = None,
        deterministic_parser: DeterministicParser | None = None,
    ) -> None:
        self._llm = llm_connection or LLMConnectionService()
        self._deterministic = deterministic_parser or DeterministicParser()
        self.last_artifacts: LLMParseArtifacts | None = None

    def parse_with_llm(
        self,
        raw_story_text: str,
        story_form: dict,
        provider_id: str,
        model: str,
    ) -> ParseResult:
        """Run LLM first pass and feed output into deterministic parser."""

        prompt = self._build_first_pass_prompt(raw_story_text=raw_story_text, story_form=story_form)
        generated = ""
        warning = ""
        used_fallback = False

        try:
            generated = self._llm.generate_text(
                provider_id=provider_id,
                model=model,
                user_prompt=prompt,
                system_prompt=(
                    "You are a pulp fiction structure analyst. "
                    "Return concise plain text following the requested structure exactly."
                ),
            ).strip()
        except Exception as exc:
            used_fallback = True
            warning = f"LLM first pass failed: {exc}"

        if not generated:
            used_fallback = True
            warning = warning or "LLM first pass returned empty output; deterministic parser fallback used."
            generated = self._minimal_fallback_breakdown(story_form)

        guided_text = self._build_guided_input(raw_story_text=raw_story_text, llm_first_pass_text=generated)
        result = self._deterministic.parse(raw_story_text=guided_text, story_form=story_form)
        result.raw_story_text = raw_story_text

        self.last_artifacts = LLMParseArtifacts(
            first_pass_text=generated,
            parser_version=self.version,
            used_fallback=used_fallback,
            warning=warning,
        )
        return result

    def generate_first_pass_text(
        self,
        raw_story_text: str,
        story_form: dict,
        provider_id: str,
        model: str,
    ) -> LLMParseArtifacts:
        """Generate only the first-pass outline text without parsing nodes."""

        prompt = self._build_first_pass_prompt(raw_story_text=raw_story_text, story_form=story_form)
        generated = ""
        warning = ""
        used_fallback = False

        try:
            generated = self._llm.generate_text(
                provider_id=provider_id,
                model=model,
                user_prompt=prompt,
                system_prompt=(
                    "You are a pulp fiction structure analyst. "
                    "Return concise plain text following the requested structure exactly."
                ),
            ).strip()
        except Exception as exc:
            used_fallback = True
            warning = f"LLM first pass failed: {exc}"

        if not generated:
            used_fallback = True
            warning = warning or "LLM first pass returned empty output."
            generated = self._minimal_fallback_breakdown(story_form)

        artifacts = LLMParseArtifacts(
            first_pass_text=generated,
            parser_version=self.version,
            used_fallback=used_fallback,
            warning=warning,
        )
        self.last_artifacts = artifacts
        return artifacts

    def parse(self, raw_story_text: str, story_form: dict) -> ParseResult:
        """Protocol-compatible parse that defaults to deterministic-only behavior."""

        return self._deterministic.parse(raw_story_text=raw_story_text, story_form=story_form)

    @staticmethod
    def _build_guided_input(raw_story_text: str, llm_first_pass_text: str) -> str:
        return (
            f"{raw_story_text.strip()}\n\n"
            "=== LLM RECOMMENDED LESTER DENT BREAKDOWN ===\n"
            f"{llm_first_pass_text.strip()}\n"
        )

    @staticmethod
    def _build_first_pass_prompt(raw_story_text: str, story_form: dict) -> str:
        quarter_blocks = []
        for quarter in story_form.get("quarters", []):
            component_titles = [component["title"] for component in quarter.get("components", [])]
            quarter_blocks.append(f"- {quarter['title']}: {', '.join(component_titles)}")
        quarter_text = "\n".join(quarter_blocks)

        return (
            "Take the raw story idea and produce a first-pass Lester Dent-style breakdown.\n"
            "Keep it transparent and compact. Use this exact format:\n\n"
            "# Recommended Lester Dent Breakdown\n"
            "## Opening Menace\n"
            "- Hook with Menace: ...\n"
            "... continue every required component through Final Sting ...\n"
            "## Notes\n"
            "- Key names: ...\n"
            "- Key settings: ...\n"
            "- Core events: ...\n"
            "- Ending/cost signals: ...\n\n"
            "Story form components:\n"
            f"{quarter_text}\n\n"
            "Raw story idea:\n"
            f"{raw_story_text}\n"
        )

    @staticmethod
    def _minimal_fallback_breakdown(story_form: dict) -> str:
        lines = ["# Recommended Lester Dent Breakdown"]
        for quarter in story_form.get("quarters", []):
            lines.append(f"## {quarter['title']}")
            for component in quarter.get("components", []):
                lines.append(f"- {component['title']}: [needs detail]")
        lines.extend([
            "## Notes",
            "- Key names: [unknown]",
            "- Key settings: [unknown]",
            "- Core events: [unknown]",
            "- Ending/cost signals: [unknown]",
        ])
        return "\n".join(lines)
