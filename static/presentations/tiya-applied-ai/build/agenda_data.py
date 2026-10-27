"""Agenda content for each day, rendered by make_agendas.py into one program agenda page per day.

Each row is (start, end, kind, title, bullets, activity). ``kind`` is talk | lab | brk and also
colors that row's segment on the to-scale day strip, so the strip always matches the agenda.
"""

from typing import NamedTuple


class Row(NamedTuple):
    """One agenda row."""

    start: str
    end: str
    kind: str
    title: str
    bullets: list[str] = []
    activity: str = ""


class Session(NamedTuple):
    """A morning or afternoon session heading and its rows."""

    heading: str
    span: str
    rows: list[Row]


class Day(NamedTuple):
    """One day of the program."""

    label: str
    date: str
    short_date: str
    hours: str
    title: str
    tool: str
    desc: str
    lab_label: str
    sessions: list[Session]
    outcomes: list[str]
    prerequisite: str


DAYS: dict[str, Day] = {
    "day1": Day(
        label="Day 1",
        date="Tuesday, October 20, 2026",
        short_date="Tue, Oct 20, 2026",
        hours="8:00 AM – 5:00 PM",
        title="Generative AI for Daily Work",
        tool="Microsoft 365 Copilot",
        desc=(
            "Practical, hands-on experience with AI tools for operational and administrative roles "
            "at Ft. Benning. Participants learn to work AI into daily workflows, including facilities "
            "maintenance, contracting, and business management, while keeping strictly to internal "
            "security and data privacy policy."
        ),
        lab_label="Hands-on lab",
        sessions=[
            Session(
                "Morning · Foundations &amp; Safe Use",
                "8:00 AM – 12:00 PM",
                [
                    Row(
                        "8:00",
                        "8:30",
                        "talk",
                        "AI Overview &amp; Context",
                        [
                            "A practical understanding of AI and where it fits in TIYA workflows"
                        ],
                    ),
                    Row(
                        "8:30",
                        "9:45",
                        "lab",
                        "Generative AI Fundamentals",
                        [
                            "Using tools like ChatGPT for writing, summarization, drafting, brainstorming, organizing ideas, analyzing information, and improving communication",
                            "A simple prompting structure",
                        ],
                        "Activity: Guided exercises",
                    ),
                    Row("9:45", "10:00", "brk", "Morning break"),
                    Row(
                        "10:00",
                        "10:45",
                        "talk",
                        "Responsible Use (TIYA Policy)",
                        [
                            "PII, PHI, CUI, and pricing restrictions",
                            "Data masking and safe input techniques",
                            "Human-in-the-loop practices for validation and oversight",
                        ],
                    ),
                    Row(
                        "10:45",
                        "12:00",
                        "lab",
                        "Role-Based Application Lab",
                        [
                            "Apply AI fundamentals directly to participants' own work and responsibilities"
                        ],
                        "Activity: Lab + share-outs",
                    ),
                    Row("12:00", "1:00", "brk", "Lunch"),
                ],
            ),
            Session(
                "Afternoon · Work Product &amp; Leadership Application",
                "1:00 PM – 5:00 PM",
                [
                    Row(
                        "1:00",
                        "1:15",
                        "talk",
                        "Afternoon Framing &amp; Recap",
                        [
                            "Key takeaways from the morning session",
                            "From tool usage to workflow and leadership application",
                        ],
                    ),
                    Row(
                        "1:15",
                        "2:45",
                        "lab",
                        "SOP Lifecycle Lab",
                        [
                            "Analyze and improve SOPs: generate, update, improve, and adapt procedures, flowcharts, communications, and training materials"
                        ],
                        "Activity: Scenario-based lab &amp; discussion",
                    ),
                    Row("2:45", "3:00", "brk", "Afternoon break"),
                    Row(
                        "3:00",
                        "4:30",
                        "lab",
                        "AI for Leadership Support &amp; Responsible AI Adoption",
                        [
                            "Using AI to support leadership thinking, communication, and interpersonal effectiveness",
                            "Applying AI to planning, reflection, decision-making, and team engagement",
                            "Enabling responsible adoption within teams: guiding usage, setting expectations, and reinforcing safe and effective practice",
                        ],
                        "Activity: Scenario-based lab &amp; discussion",
                    ),
                    Row(
                        "4:30",
                        "5:00",
                        "talk",
                        "Closing &amp; Assessment",
                        ["Reflection, application, and next steps"],
                    ),
                ],
            ),
        ],
        outcomes=[
            "Apply generative AI tools to day-to-day work tasks, including drafting, summarization, and organizing information.",
            "Use a simple prompting framework to improve the quality and usefulness of AI outputs.",
            "Practice responsible AI use, including data masking and human-in-the-loop validation, in line with TIYA policy.",
            "Apply AI to real workflows to generate, update, and improve operational materials and processes.",
            "Use AI to support leadership activities, including planning, communication, reflection, and decision-making.",
        ],
        prerequisite="None.",
    ),
    "day2": Day(
        label="Day 2",
        date="Wednesday, October 21, 2026",
        short_date="Wed, Oct 21, 2026",
        hours="8:30 AM – 4:30 PM",
        title="Agentic AI with Microsoft Copilot",
        tool="Copilot agent builder",
        desc=(
            "Building practical, human-centered agentic AI capabilities with Microsoft Copilot. The "
            "workshop focuses on no-code and low-code approaches to creating AI agents. For participants "
            "who completed Day 1 in June 2026; the day opens with a short Day 1 review."
        ),
        lab_label="Hands-on build",
        sessions=[
            Session(
                "Morning",
                "8:30 AM – 12:15 PM",
                [
                    Row(
                        "8:30",
                        "10:15",
                        "talk",
                        "Agentic AI Foundations",
                        [
                            "Day 1 in review: Mask → Ask → Check",
                            "Introduction to AI agents",
                            "No-code ecosystems",
                            "The anatomy of an agent",
                        ],
                    ),
                    Row("10:15", "10:30", "brk", "Morning break"),
                    Row(
                        "10:30",
                        "12:15",
                        "lab",
                        "Building Real Agents",
                        ["Prompt engineering", "No-code agents", "Multi-tool agents"],
                        "Hands-on build",
                    ),
                    Row("12:15", "1:15", "brk", "Lunch"),
                ],
            ),
            Session(
                "Afternoon",
                "1:15 PM – 4:30 PM",
                [
                    Row(
                        "1:15",
                        "3:00",
                        "lab",
                        "Building Real Agents, Continued",
                        ["Event triggers", "Publishing agents"],
                        "Activity: Hands-on agent creation",
                    ),
                    Row("3:00", "3:15", "brk", "Afternoon break"),
                    Row(
                        "3:15",
                        "4:30",
                        "talk",
                        "Governance &amp; Security",
                        ["PII handling", "Risk assessment", "Model governance"],
                    ),
                ],
            ),
        ],
        outcomes=[
            "Understand the fundamentals of AI agent creation and common agent architectures.",
            "Design, configure, and deploy autonomous agents using no-code and low-code tools.",
            "Integrate reasoning, planning, tools, and memory into practical agent workflows.",
            "Apply security, privacy, safety, and trust principles when developing and deploying agentic AI.",
        ],
        prerequisite="Day 1, Generative AI for Daily Work.",
    ),
    "day3": Day(
        label="Day 3",
        date="[Date TBD]",
        short_date="[Date TBD]",
        hours="8:00 AM – 4:00 PM",
        title="Advanced Agents with Copilot Studio",
        tool="Microsoft Copilot Studio",
        desc=(
            "Agents that run without being asked. Participants build agents in Microsoft Copilot Studio "
            "that start on an incoming email, run on a schedule, and hand work to other agents, then "
            "learn to operate them safely: untrusted input, monitoring, cost, and a documented off "
            "switch. Every build ends with a person reviewing the agent's output. The day opens with a "
            "short review of Day 2."
        ),
        lab_label="Hands-on build",
        sessions=[
            Session(
                "Morning · Always-On Agents",
                "8:00 AM – 11:45 AM",
                [
                    Row(
                        "8:00",
                        "8:30",
                        "talk",
                        "Welcome &amp; Day 2 in Review",
                        [
                            "Copilot Studio login check",
                            "The autonomy ladder: from on-demand agents to triggered and autonomous agents",
                            "What changes when no one is watching: untrusted input, real actions, real cost",
                        ],
                    ),
                    Row(
                        "8:30",
                        "9:45",
                        "lab",
                        "From Agent Builder to Copilot Studio",
                        [
                            "A tour of Copilot Studio: knowledge, tools, agents, topics, triggers, and the activity view",
                            "Tools and connectors: how an agent acts in other systems",
                            "Build 1: the SOP Navigator, rebuilt, retested, and published for other agents to use",
                        ],
                        "Hands-on build",
                    ),
                    Row("9:45", "10:00", "brk", "Morning break"),
                    Row(
                        "10:00",
                        "11:45",
                        "lab",
                        "Event-Triggered Agents",
                        [
                            "Trigger, condition, payload, action, and human check",
                            "Agent instructions vs. payload instructions",
                            "Untrusted input: the email is data, not instructions",
                            "Build 2: a Work Order Intake agent that triages new request emails for a Facilities Lead",
                        ],
                        "Hands-on build",
                    ),
                    Row("11:45", "12:30", "brk", "Lunch"),
                ],
            ),
            Session(
                "Afternoon · Agent Teams &amp; Operations",
                "12:30 PM – 4:00 PM",
                [
                    Row(
                        "12:30",
                        "1:30",
                        "lab",
                        "Scheduled Agents",
                        [
                            "Scheduled prompts in Copilot Chat vs. recurrence triggers in Copilot Studio",
                            "Let the flow count; let the agent write",
                            "Build 3: a Monday Backlog Briefing posted to Teams for a lead to review",
                        ],
                        "Hands-on build",
                    ),
                    Row(
                        "1:30",
                        "2:45",
                        "lab",
                        "Multi-Agent Orchestration",
                        [
                            "Orchestrators and specialist agents",
                            "Child agents vs. connected agents, and when one agent is enough",
                            "Build 4: a Facilities Desk that routes questions to three specialist agents",
                        ],
                        "Hands-on build",
                    ),
                    Row("2:45", "3:00", "brk", "Afternoon break"),
                    Row(
                        "3:00",
                        "3:45",
                        "talk",
                        "Operating Autonomous Agents",
                        [
                            "Five new risks: injection, credentials, silent failure, cost, and chained errors",
                            "Red-teaming a triggered agent",
                            "Runbooks, risk tiers, and the off switch",
                        ],
                        "Activity: Red-team &amp; runbook",
                    ),
                    Row(
                        "3:45",
                        "4:00",
                        "talk",
                        "Closing &amp; Assessment",
                        ["Knowledge check, trigger shutdown check, and next steps"],
                    ),
                ],
            ),
        ],
        outcomes=[
            "Decide whether an agent should run on demand, on an event, or on a schedule, and design its trigger, conditions, actions, and human check.",
            "Build and test event-triggered and scheduled agents in Microsoft Copilot Studio that hand their output to a person for review.",
            "Design and build a multi-agent solution with an orchestrator and specialist agents, and judge when one agent is enough.",
            "Operate autonomous agents safely, including untrusted input, credentials, cost, monitoring, and a documented off switch.",
        ],
        prerequisite="Day 2, Agentic AI with Microsoft Copilot, and a Copilot Studio license.",
    ),
}
