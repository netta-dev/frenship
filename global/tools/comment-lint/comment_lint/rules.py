"""The two rule sets a comment is judged against, as the model's question criteria.

Comment rules come from `~/.claude/conventions.md` §Comments; prose rules from
`~/.claude/prose.md`. Each comment gets both questions in one call: which comment rule
it breaks and which prose rule, each with `none` as an option.
"""

from typesafe_sdk import Choice, Noul

COMMENT_RULES: dict[str, str] = {
    "none": "The comment is fine: it states a constraint, rationale, or trap the reader "
    "couldn't get from the code, and it describes the present code.",
    "unnecessary": "The comment doesn't save a competent engineer, working here under time "
    "pressure, from digging elsewhere or breaking something: it restates what the code "
    "shows, a rename or extraction would replace it, or it carries no constraint, rationale, "
    "or trap.",
    "section_divider": "A section-divider or banner comment that groups code instead of "
    "splitting the file or method.",
    "tombstone": "The comment describes removed code, a previous behavior, how things used "
    "to work, or narrates a change instead of describing present code.",
    "citation": "The comment cites an incident (by name or date), a design doc, a decision "
    "number, or a review round.",
    "thin_docstring": "A public method docstring that repeats the signature and omits what "
    "a caller needs: the contract, or precision the signature lacks such as units, bounds, "
    "or ownership.",
    "wrong_altitude": "A class or file comment that lists implementation details instead of "
    "the role in the system, cross-method invariants, or lifecycle.",
}

PROSE_RULES: dict[str, str] = {
    "none": "The prose breaks none of the rules below.",
    "P1_actor_first": "Cleft or fronted sentence instead of subject-verb-object, e.g. "
    "'what the guard refuses is a call'.",
    "P2_telegraphese": "Fragment or telegraphese instead of a full sentence, e.g. "
    "'ff-only merge, else abort'. A tabular block, such as aligned columns under `Usage:` "
    "or `Exit codes:`, is exempt.",
    "P3_coinage": "A one-off coinage or unusual word where a plain word exists.",
    "P4_personification": "Personifies an abstraction: the function 'wants', the alias "
    "'earns its place'.",
    "P5_worth_x": "Uses 'worth noting', 'worth x'.",
    "P6_no_negation": "'no'-negation such as 'fires no onTap', 'carries no text' instead of "
    "'doesn't fire', 'is unlabelled'.",
    "P7_intensifier": "Empty intensifier: actually, really, genuinely, simply, just, clearly, "
    "obviously, very, fundamentally, importantly, notably, or an emphatic reflexive.",
    "P8_absolute": "Overstated absolute such as 'never', 'always', 'every'. "
    "'it never re-asks' should be 'it won't re-ask'.",
    "P9_negation_emphasis": "Rejects an alternative nobody assumed, e.g. 'configuration, "
    "not re-architecture'.",
    "P10_rebuttal": "Corrects a mistake the reader hasn't made instead of asserting the fact, "
    "e.g. 'X is NOT the y site'.",
    "P11_asymmetric_pair": "Distinguishes two things by negating one instead of naming both "
    "sides symmetrically.",
    "P12_rule_of_three": "Padding lists: 'simpler, cleaner, and more maintainable'.",
    "P13_emphasis_jargon": "Emphasis jargon: 'well-defined seam', 'the key insight', "
    "'a real X'.",
    "P14_inferable": "States what the reader can infer: a justification, a restatement, or an "
    "illustrative example when the why is plain.",
    "P15_oxford_comma": "Missing Oxford comma: a list of three or more has no comma before its "
    "final 'and'/'or', e.g. 'lint, tests and types'.",
}


def questions() -> dict[str, Choice | Noul]:
    return {
        "breaks_comment_rule": Noul(
            instructions="Does this comment break any of the comment rules? Judge it against "
            "the code around it.",
            criteria={
                "true": "It breaks at least one rule: " + "; ".join(
                    f"{k}: {v}" for k, v in COMMENT_RULES.items() if k != "none"
                ),
                "false": COMMENT_RULES["none"],
            },
        ),
        "breaks_prose_rule": Noul(
            instructions="Does the comment's wording break any of the prose rules?",
            criteria={
                "true": "It breaks at least one rule: " + "; ".join(
                    f"{k}: {v}" for k, v in PROSE_RULES.items() if k != "none"
                ),
                "false": PROSE_RULES["none"],
            },
        ),
        "comment_rule": Choice(
            instructions="Which comment rule does this comment break? Judge the comment "
            "against the code around it. Pick `none` when it breaks none.",
            criteria=COMMENT_RULES,
        ),
        "prose_rule": Choice(
            instructions="Which prose rule does the comment's wording break? Pick `none` "
            "when it breaks none.",
            criteria=PROSE_RULES,
        ),
    }
