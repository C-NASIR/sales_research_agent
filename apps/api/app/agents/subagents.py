from app.agents import prompts


SUBAGENTS = [
    {
        "name": "icp_strategist",
        "description": "Creates the ideal customer profile and scoring rubric.",
        "prompt": prompts.ICP_STRATEGIST_PROMPT,
    },
    {
        "name": "account_researcher",
        "description": "Builds structured company research summaries.",
        "prompt": prompts.ACCOUNT_RESEARCHER_PROMPT,
    },
    {
        "name": "signal_detector",
        "description": "Creates timing signals and why-now summaries.",
        "prompt": prompts.SIGNAL_DETECTOR_PROMPT,
    },
    {
        "name": "scoring_analyst",
        "description": "Produces deterministic fit and timing scores.",
        "prompt": prompts.SCORING_ANALYST_PROMPT,
    },
    {
        "name": "outreach_writer",
        "description": "Writes the initial outbound draft.",
        "prompt": prompts.OUTREACH_WRITER_PROMPT,
    },
    {
        "name": "compliance_reviewer",
        "description": "Checks the draft for unsupported familiarity and quality issues.",
        "prompt": prompts.COMPLIANCE_REVIEWER_PROMPT,
    },
]
