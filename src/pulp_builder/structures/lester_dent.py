"""Lester Dent-inspired story forms."""

from __future__ import annotations

from copy import deepcopy


BASE_QUARTERS: list[dict] = [
    {
        "quarter_id": "q1",
        "title": "Opening Menace",
        "description": "Open with danger, desire, and momentum.",
        "components": [
            {
                "id": "q1-hook-with-menace",
                "title": "Hook with Menace",
                "description": "Open with immediate threat or unnerving momentum.",
                "required": True,
            },
            {
                "id": "q1-hero-desire",
                "title": "Hero Desire",
                "description": "Clarify what the protagonist wants right now.",
                "required": True,
            },
            {
                "id": "q1-initial-trouble",
                "title": "Initial Trouble",
                "description": "Introduce first obstacle that blocks straightforward progress.",
                "required": True,
            },
            {
                "id": "q1-hint-of-deeper-menace",
                "title": "Hint of Deeper Menace",
                "description": "Signal that the visible threat is only surface-level.",
                "required": True,
            },
        ],
    },
    {
        "quarter_id": "q2",
        "title": "Deepening Trouble",
        "description": "Attempts backfire as stakes and danger rise.",
        "components": [
            {
                "id": "q2-first-attempt",
                "title": "First Attempt",
                "description": "Show the protagonist taking concrete action.",
                "required": True,
            },
            {
                "id": "q2-first-complication",
                "title": "First Complication",
                "description": "Complication worsens the cost of action.",
                "required": True,
            },
            {
                "id": "q2-clue-or-pattern",
                "title": "Clue or Pattern",
                "description": "Reveal evidence that reframes the threat.",
                "required": True,
            },
            {
                "id": "q2-rising-stakes",
                "title": "Rising Stakes",
                "description": "Raise personal and external consequences.",
                "required": True,
            },
        ],
    },
    {
        "quarter_id": "q3",
        "title": "Trap and Terrible Revelation",
        "description": "Plans fail, betrayal strikes, and hidden truth emerges.",
        "components": [
            {
                "id": "q3-reversal",
                "title": "Reversal",
                "description": "Turn the apparent advantage into sudden danger.",
                "required": True,
            },
            {
                "id": "q3-betrayal-or-false-safety",
                "title": "Betrayal or False Safety",
                "description": "Trust collapses or calm proves deceptive.",
                "required": True,
            },
            {
                "id": "q3-terrible-revelation",
                "title": "Terrible Revelation",
                "description": "Expose the deeper truth behind the menace.",
                "required": True,
            },
            {
                "id": "q3-deathtrap-or-contact",
                "title": "Deathtrap or Contact",
                "description": "Force direct confrontation with lethal danger.",
                "required": True,
            },
        ],
    },
    {
        "quarter_id": "q4",
        "title": "Payoff and Final Sting",
        "description": "Resolve conflict with a costly outcome and strong final note.",
        "components": [
            {
                "id": "q4-final-confrontation",
                "title": "Final Confrontation",
                "description": "Deliver decisive clash with central threat.",
                "required": True,
            },
            {
                "id": "q4-cost-of-survival",
                "title": "Cost of Survival",
                "description": "Name what is lost, scarred, or sacrificed.",
                "required": True,
            },
            {
                "id": "q4-resolution",
                "title": "Resolution",
                "description": "Show immediate aftermath and practical outcome.",
                "required": True,
            },
            {
                "id": "q4-final-sting",
                "title": "Final Sting",
                "description": "Leave an ominous or ironic final image.",
                "required": True,
            },
        ],
    },
]


_GUIDANCE_BY_FORM: dict[str, dict[str, str]] = {
    "howard_adventure": {
        "q1-hook-with-menace": "Open with violent motion: ambush, raid, duel, storm, or bloodied discovery.",
        "q1-hero-desire": "What does the hero want now: treasure, vengeance, rescue, escape, or grim survival?",
        "q1-initial-trouble": "What immediate force blocks the hero and raises bodily risk?",
        "q1-hint-of-deeper-menace": "What sign suggests ancient sorcery or treachery behind the first conflict?",
        "q2-first-attempt": "Show a bold action through blade, stealth, or raw force.",
        "q2-first-complication": "How does the hero's move trigger worse danger or opposition?",
        "q2-clue-or-pattern": "What clue ties the conflict to cursed ruins, cults, relics, or old bloodlines?",
        "q2-rising-stakes": "What escalates from a fight to a struggle for survival and consequence?",
        "q3-reversal": "Where does apparent advantage snap into near-defeat?",
        "q3-betrayal-or-false-safety": "Who betrays the hero, or what shelter becomes a trap?",
        "q3-terrible-revelation": "What ancient truth makes the visible danger only the edge of something older and worse?",
        "q3-deathtrap-or-contact": "Place the hero in a brutal trial with monster, sorcerer, or doomed chamber.",
        "q4-final-confrontation": "How does the hero force a decisive end through risk and violence?",
        "q4-cost-of-survival": "What does survival cost in blood, allies, innocence, or future peace?",
        "q4-resolution": "Show who escapes, what is destroyed, and what immediate order is restored.",
        "q4-final-sting": "End with irony, omen, or surviving trace of menace.",
    },
    "lovecraft_weird": {
        "q1-hook-with-menace": "Begin with testimony, warning, or record of a disturbing anomaly.",
        "q1-hero-desire": "What proof, explanation, or forbidden history is the narrator seeking?",
        "q1-initial-trouble": "What first incident resists normal explanation and compels inquiry?",
        "q1-hint-of-deeper-menace": "What detail implies a larger pattern beyond human scale?",
        "q2-first-attempt": "Show the investigation: archives, interviews, sites, or experiments.",
        "q2-first-complication": "What result deepens dread instead of providing clarity?",
        "q2-clue-or-pattern": "What recurring sign, text, lineage, or geometry links the events?",
        "q2-rising-stakes": "How do stakes escalate into social ruin, sanity collapse, or existential fear?",
        "q3-reversal": "What assumption fails and leaves the narrator exposed?",
        "q3-betrayal-or-false-safety": "What trusted source, place, or method proves dangerously false?",
        "q3-terrible-revelation": "What truth proves humanity is less central, safe, or sovereign than believed?",
        "q3-deathtrap-or-contact": "Describe direct contact with the uncanny, whether physical, psychic, or visionary.",
        "q4-final-confrontation": "How does the narrator attempt to contain, flee, record, or deny the horror?",
        "q4-cost-of-survival": "What sanity, identity, bloodline, or certainty is lost?",
        "q4-resolution": "What immediate ending is reached in testimony, silence, or disappearance?",
        "q4-final-sting": "End with one final sign that the dread persists.",
    },
    "hybrid_weird_adventure": {
        "q1-hook-with-menace": "Open with a mission and immediate danger around an uncanny lead.",
        "q1-hero-desire": "What practical goal drives action: rescue, map, relic, debt, or escape?",
        "q1-initial-trouble": "What obstacle forces risky movement into hostile ground?",
        "q1-hint-of-deeper-menace": "What odd sign suggests the mission touches ancient horror?",
        "q2-first-attempt": "Show decisive action through expedition, infiltration, or pursuit.",
        "q2-first-complication": "How does human error or opposition compound the danger?",
        "q2-clue-or-pattern": "What clue links current peril to old ruins, cults, or hidden mechanisms?",
        "q2-rising-stakes": "How do stakes escalate from mission success to survival against the uncanny?",
        "q3-reversal": "Where does momentum collapse into a trap or devastating setback?",
        "q3-betrayal-or-false-safety": "Who turns traitor, or what refuge reveals itself as compromised?",
        "q3-terrible-revelation": "What hidden truth proves the mission was always part of a larger horror?",
        "q3-deathtrap-or-contact": "Force close contact with the core threat in a high-risk set piece.",
        "q4-final-confrontation": "Show a frantic showdown combining physical action and weird danger.",
        "q4-cost-of-survival": "What does victory cost in people, body, trust, or purpose?",
        "q4-resolution": "Resolve the mission outcome and immediate survival status.",
        "q4-final-sting": "End on a sign that something old still watches or waits.",
    },
}


def build_story_form(form_id: str, label: str, summary: str) -> dict:
    """Return one story form definition based on the common chassis."""

    guidance_map = _GUIDANCE_BY_FORM[form_id]
    quarters = deepcopy(BASE_QUARTERS)
    for quarter in quarters:
        for component in quarter["components"]:
            component["guidance_prompt"] = guidance_map[component["id"]]

    return {
        "id": form_id,
        "label": label,
        "summary": summary,
        "quarters": quarters,
    }


def build_all_story_forms() -> dict[str, dict]:
    """Build all supported story forms."""

    return {
        "howard_adventure": build_story_form(
            form_id="howard_adventure",
            label="Howard Adventure",
            summary="Sword-and-sorcery adventure focused on violent survival and treachery.",
        ),
        "lovecraft_weird": build_story_form(
            form_id="lovecraft_weird",
            label="Lovecraft Weird Tale",
            summary="Weird testimony-driven horror with investigation and cosmic dread.",
        ),
        "hybrid_weird_adventure": build_story_form(
            form_id="hybrid_weird_adventure",
            label="Hybrid Weird Adventure",
            summary="Fast adventure with mission pressure, betrayal, and uncanny threat.",
        ),
    }


def default_story_forms() -> list[dict]:
    """Return default story forms as a list for config serialization."""

    return list(build_all_story_forms().values())
