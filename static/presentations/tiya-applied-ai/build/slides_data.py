"""Slide content for every deck, shared by the HTML and PowerPoint renderers.

Each slide is (type, title, bullets, speaker note).
Types: title | section | content | columns | exercise | demo.
A ``columns`` slide renders each "Head: body" bullet as its own column.
A note starting with "<n> min" puts a duration chip on exercise slides.
"""

Slide = tuple[str, str, list[str], str]

DECKS: dict[str, dict[str, str]] = {
    "day1": {
        "label": "Day 1",
        "date": "Tuesday, October 20, 2026",
        "title": "Generative AI for Daily Work",
        "tool": "Microsoft 365 Copilot",
    },
    "day2": {
        "label": "Day 2",
        "date": "Wednesday, October 21, 2026",
        "title": "Agentic AI with Microsoft Copilot",
        "tool": "Copilot agent builder",
    },
    "day3": {
        "label": "Day 3",
        "date": "[Date TBD]",
        "title": "Advanced Agents with Copilot Studio",
        "tool": "Microsoft Copilot Studio",
    },
}

DAY1: list[Slide] = [
    (
        "title",
        "Generative AI for Daily Work",
        ["Tuesday, October 20, 2026", "Alex Djalali · Alex Rhodeen"],
        "On screen as people arrive.",
    ),
    (
        "content",
        "Today",
        [
            "8:00 Foundations & Safe Use",
            "10:45 Role-based lab",
            "1:15 SOP lifecycle lab",
            "3:00 Leadership & responsible adoption",
            "4:30 Closing & assessment",
        ],
        "Point out that most of the day is keyboard time.",
    ),
    (
        "content",
        "Logistics",
        [
            "Breaks at 9:45, 12:00 (lunch), and 2:45",
            "Wi-Fi, restrooms, phones",
            "Remote: chat is watched all day",
            "Parking lot for questions",
        ],
        "",
    ),
    (
        "exercise",
        "Who's here?",
        [
            "Used Copilot or ChatGPT at work? At home? Never?",
            "Which task would you like an hour back from each week?",
        ],
        "Write answers on the flip chart; revisit at 4:30.",
    ),
    (
        "content",
        "What generative AI is",
        [
            "Predicts the likely next words from patterns",
            "Very good at language work",
            "Doesn't know TIYA's facts unless you give them",
            "Sounds just as confident when it's wrong",
        ],
        "",
    ),
    (
        "demo",
        "Ask it something only TIYA knows",
        [
            "“What is TIYA's emergency work order desk number?”",
            "How would you know if that's right?",
        ],
        "That question is the Check step.",
    ),
    (
        "columns",
        "Draft, not decide",
        [
            "Good for: Drafting, summarizing, organizing, analyzing, rewording",
            "Not for: Deciding, approving, signing, holding sensitive data",
        ],
        "",
    ),
    (
        "content",
        "Where it fits at TIYA",
        [
            "Facilities: technician notes → status update",
            "Contracting: plain-language clause summaries",
            "Business management: meeting notes → action items",
            "Leads: first draft of announcements",
        ],
        "",
    ),
    (
        "columns",
        "The habit: Mask → Ask → Check",
        [
            "1 · Mask: Sensitive data comes out before you paste",
            "2 · Ask: Goal, Context, Source, Expectations",
            "3 · Check: Read it as if you'll sign it",
        ],
        "Every exercise today follows these three steps.",
    ),
    ("section", "Generative AI Fundamentals · 8:30", ["Hands-on · 75 min"], ""),
    (
        "demo",
        "Tour of Copilot Chat",
        [
            "New chat, edit and resend, regenerate",
            "Copy, upload a file, chat history",
            "Work/web toggle, if your tenant shows one",
        ],
        "Keep to 5 minutes.",
    ),
    (
        "content",
        "A capable new hire on day one",
        [
            "Smart, fast, eager",
            "Knows nothing about Building 214 or who the COR is",
            "The more you'd explain to a new hire, the more goes in the prompt",
        ],
        "",
    ),
    (
        "columns",
        "Ask: the four parts",
        [
            "Goal: What do I want?",
            "Context: Why, and for whom?",
            "Source: What should it use?",
            "Expectations: Format, length, tone",
        ],
        "Microsoft's own prompting guidance for Copilot.",
    ),
    (
        "columns",
        "Weak vs. GCSE",
        [
            "Weak: “Write a notice about a water shutoff.”",
            "GCSE: Goal, plus building, date, times, reason, alternatives, length, and tone (workbook E1)",
        ],
        "Walk through each part of the strong prompt.",
    ),
    (
        "exercise",
        "E1 · Two prompts, one task",
        [
            "Run the weak prompt, then the GCSE prompt",
            "Which could you send with fewer edits?",
        ],
        "15 min",
    ),
    (
        "exercise",
        "E2 · Summarize the work order notes",
        [
            "Sample A: seven visits to one rooftop unit",
            "Status summary, timeline, parts table",
        ],
        "15 min",
    ),
    (
        "content",
        "Follow-up moves",
        [
            "Shorten: “Cut this in half. Keep the dates.”",
            "Re-aim: “Rewrite it for the technicians.”",
            "Reshape: “Put it in a table.”",
            "Challenge: “What's missing?”",
            "Show your work: “What did you add?”",
        ],
        "",
    ),
    (
        "exercise",
        "E3 · Follow-ups are prompts too",
        ["Four follow-ups in your E2 chat", "Which one improved it most?"],
        "10 min",
    ),
    (
        "exercise",
        "E4 or E5",
        [
            "Brainstorm and organize: reducing repeat work orders",
            "Or fix the tone of a terse email",
        ],
        "10 min",
    ),
    (
        "content",
        "Debrief",
        [
            "Which GCSE part changed the output most?",
            "Where did Copilot add something not in the notes?",
            "What would you check before sending to the COR?",
        ],
        "Use the invented detail to set up 10:00.",
    ),
    (
        "section",
        "Responsible Use · 10:00",
        ["TIYA policy · 45 min"],
        "Replace placeholder rules with TIYA's written policy before delivery.",
    ),
    (
        "content",
        "A story",
        [
            "A vendor quote, a free AI app, a quick comparison",
            "What went wrong, and when?",
        ],
        "Tell it as a hypothetical.",
    ),
    (
        "columns",
        "Four categories",
        [
            "PII: Identifies a person",
            "PHI: Health information about a person",
            "CUI: Controlled Unclassified Information. If unsure, treat it as CUI.",
            "Pricing: Rates, costs, bids, any vendor's quote",
        ],
        "",
    ),
    (
        "columns",
        "The data traffic light",
        [
            "Red: Never enter. CUI, PHI, pricing, IDs, security details, passwords",
            "Amber: Mask first. Names, contacts, vendors, contract numbers, internal notes",
            "Green: Okay. How-to questions, public information, your own masked writing",
        ],
        "Placeholder rules until replaced with TIYA policy.",
    ),
    (
        "content",
        "Enterprise data protection",
        [
            "Your prompts aren't used to train the models",
            "It doesn't change the rules for CUI, PHI, or pricing",
            "TIYA's policy and contracts decide",
        ],
        "",
    ),
    (
        "content",
        "How to mask",
        [
            "Names → roles: [Technician A], [the COR]",
            "Numbers → placeholders: [CONTRACT], [PHONE]",
            "Prices, health details, codes → delete",
            "Keep your key outside Copilot",
        ],
        "",
    ),
    (
        "exercise",
        "Masking drill",
        [
            "Sample B: find everything that has to go",
            "6 min alone, 3 min with a neighbor",
        ],
        "12 min",
    ),
    (
        "content",
        "Masking key: 11 items",
        [
            "3 names, 1 email, 1 phone number",
            "1 health detail, 2 prices, 1 vendor",
            "1 contract number, 1 gate code",
            "Most missed: the gate code and the vendor name",
        ],
        "Reveal one at a time.",
    ),
    (
        "exercise",
        "Can I paste this?",
        ["Eight quick-fire cards", "Green, amber, or red?"],
        "8 min; tables vote.",
    ),
    (
        "content",
        "Check: a person stays in the loop",
        [
            "Facts, numbers, and names match the source",
            "Nothing added that you didn't give it",
            "Policy, tone, and commitments",
            "Masked details go back in outside Copilot",
        ],
        "",
    ),
    (
        "demo",
        "Verify a clause",
        [
            "Ask Copilot for the FAR clause on limitations on subcontracting",
            "Compare it against acquisition.gov",
        ],
        "Whatever the result, the point is checking the source.",
    ),
    ("section", "Would I sign this?", ["If you send it, you own it."], "Pause here."),
    ("section", "Role-Based Application Lab · 10:45", ["Hands-on · 75 min"], ""),
    (
        "columns",
        "Pick your track",
        [
            "Track 1: Facilities Maintenance",
            "Track 2: Contracting",
            "Track 3: Business Management & Admin",
            "Track 4: Supervisors & Leads",
        ],
        "",
    ),
    (
        "exercise",
        "Task A, then Task B",
        [
            "Task A: the card's sample",
            "Task B: your real task, masked, initialed by an instructor",
        ],
        "45 min",
    ),
    (
        "content",
        "Share-outs",
        [
            "One pair per track, 4 minutes",
            "The prompt, the output, what you had to fix",
        ],
        "",
    ),
    ("section", "Afternoon · 1:00", ["Work Product & Leadership Application"], ""),
    (
        "exercise",
        "Recap quiz",
        [
            "Name the four GCSE parts",
            "Red, amber, or green? Two examples",
            "What does Check mean?",
        ],
        "5 min; show of hands.",
    ),
    (
        "content",
        "From tasks to workflows and people",
        ["This morning: single tasks", "This afternoon: SOPs, and the people you lead"],
        "",
    ),
    ("section", "SOP Lifecycle Lab · 1:15", ["Hands-on · 90 min"], ""),
    (
        "columns",
        "The SOP lifecycle",
        [
            "Generate: A first draft",
            "Update: Bring it current",
            "Improve: Clearer, safer, complete",
            "Adapt: Cards, quizzes, emails, talks",
        ],
        "",
    ),
    (
        "content",
        "Who owns what",
        [
            "Copilot drafts",
            "The subject-matter expert owns accuracy",
            "Doc control approves",
        ],
        "",
    ),
    (
        "exercise",
        "Step 1 · Diagnose",
        ["Critique Sample C (2019)", "Issue, why it matters, fix, ranked by risk"],
        "15 min",
    ),
    (
        "exercise",
        "Step 2 · Rewrite",
        ["The standard template", "[VERIFY] instead of invented values"],
        "20 min",
    ),
    (
        "exercise",
        "Step 3 · Visualize",
        [
            "A step table with decision points",
            "A text flowchart; optional SmartArt in Word",
        ],
        "15 min",
    ),
    (
        "exercise",
        "Step 4 · Adapt",
        ["Pick two: quick-reference card, quiz, announcement, toolbox talk"],
        "15 min",
    ),
    (
        "content",
        "Discussion",
        [
            "What did Copilot miss that only TIYA knows?",
            "Who reviews AI-assisted SOP changes?",
        ],
        "",
    ),
    ("section", "Leadership & Responsible Adoption · 3:00", ["Hands-on · 90 min"], ""),
    (
        "content",
        "A thinking partner, not a decision-maker",
        [
            "Leadership is judgment and relationships",
            "AI gives you drafts, questions, and rehearsal",
            "You decide, and you show up",
        ],
        "",
    ),
    (
        "content",
        "People topics",
        ["Describe the situation, not the person", "No names, no health details"],
        "",
    ),
    (
        "exercise",
        "L1 · Announce a change",
        ["The message, the likely questions, what to escalate"],
        "20 min",
    ),
    (
        "exercise",
        "L2 · Prepare a hard conversation",
        ["Plan it", "Copilot plays the employee", "Ask for feedback"],
        "20 min. Model the role-play for 2 minutes first.",
    ),
    (
        "exercise",
        "L3 · Decide between options",
        ["Options table, pre-mortem, open questions", "No pricing"],
        "15 min",
    ),
    (
        "exercise",
        "L4 · Lead adoption",
        ["A non-punitive conversation", "Five team AI norms"],
        "20 min",
    ),
    (
        "content",
        "Debrief",
        [
            "Where was it useful? Where did it fall flat?",
            "Read your best norm aloud",
            "One AI conversation you'll have with your team this month",
        ],
        "",
    ),
    ("section", "Closing & Assessment · 4:30", ["30 min"], ""),
    (
        "exercise",
        "Knowledge check",
        ["10 questions, self-scored"],
        "10 min. Formative, not pass/fail.",
    ),
    ("exercise", "Exit task", ["Mask → Ask → Check, on paper", "Hand it in"], "12 min"),
    (
        "content",
        "Action plan",
        [
            "Three tasks for next week",
            "One person you'll show",
            "Back to this morning's flip chart",
        ],
        "",
    ),
    (
        "title",
        "Thank you",
        [
            "Evaluation form · certificates at the door",
            "Questions after today: [TIYA contact]",
        ],
        "",
    ),
]

DAY2: list[Slide] = [
    (
        "title",
        "Agentic AI with Microsoft Copilot",
        ["Wednesday, October 21, 2026", "Alex Djalali · Alex Rhodeen"],
        "",
    ),
    (
        "content",
        "Today",
        [
            "8:30 Login check and a Day 1 review",
            "8:50 Agentic AI foundations",
            "10:30 Building real agents",
            "1:15 Triggers, publishing, your own agent",
            "3:15 Governance & security",
        ],
        "",
    ),
    (
        "exercise",
        "Login check",
        ["Open Copilot Chat", "Find the option to create an agent"],
        "Escalate anyone who can't, now.",
    ),
    (
        "section",
        "Day 1 in Review · 8:40",
        ["Back from June · 10 min"],
        "Everyone here took Day 1 in June. Show of hands: who has used Copilot at work since? Take one or two examples; they're good first agent ideas for the design canvas.",
    ),
    (
        "content",
        "What Day 1 was about",
        [
            "Generative AI predicts likely words; it doesn't know TIYA's facts unless you give them",
            "It sounds just as confident when it's wrong",
            "Draft, not decide: it drafts and summarizes; people decide, approve, and sign",
            "If you send it, you own it",
        ],
        "Two minutes. Ask what's stuck with people since June before showing the bullets.",
    ),
    (
        "columns",
        "The habit: Mask → Ask → Check",
        [
            "1 · Mask: Names → roles, numbers → placeholders, prices and health details out",
            "2 · Ask: Goal, Context, Source, Expectations (GCSE)",
            "3 · Check: Facts match the source, nothing added. Would I sign this?",
        ],
        "Every exercise today still follows these steps. New for agents: an agent's knowledge must be safe for everyone it's shared with.",
    ),
    (
        "columns",
        "The data traffic light",
        [
            "Red: Never enter. CUI, PHI, pricing, IDs, security details, passwords",
            "Amber: Mask first. Names, contacts, vendors, contract numbers",
            "Green: Okay. How-to, public information, masked writing",
        ],
        "Quick check, tables vote: a vendor's quote (red), a technician's name (amber), how to build a table in Word (green). Placeholder rules until replaced with TIYA policy.",
    ),
    ("section", "Agentic AI Foundations · 8:50", ["85 min"], ""),
    (
        "content",
        "From chat to agent",
        ["Standing instructions", "Its own knowledge", "Tools", "For one defined job"],
        "",
    ),
    (
        "columns",
        "The autonomy ladder",
        [
            "1 · Prompt: You ask; it answers",
            "2 · Saved prompt: You reuse what works",
            "3 · Agent: Instructions, knowledge, tools",
            "4 · Triggered: Starts itself on an event",
            "5 · Autonomous: Plans and acts, with approvals",
        ],
        "Agent builder is rung 3. Each rung up needs more design, testing, and governance.",
    ),
    (
        "content",
        "Anatomy of an agent",
        [
            "Purpose · Instructions · Knowledge · Tools",
            "Memory · Triggers · Guardrails",
        ],
        "",
    ),
    (
        "columns",
        "What agent builder supports",
        [
            "Yes: Purpose, instructions, knowledge",
            "Some: Tools: code interpreter, image generation",
            "Limited: Memory: the current conversation",
            "No: Triggers: a person starts it",
        ],
        "",
    ),
    (
        "columns",
        "The Microsoft ecosystem",
        [
            "Agent builder: In Copilot Chat. No-code, on-demand agents",
            "Copilot Studio: Triggers, connectors, autonomous agents",
            "Power Automate: Rules-based flows and triggers",
        ],
        "Confirm what TIYA is licensed for.",
    ),
    (
        "columns",
        "Four architectures",
        [
            "Knowledge Q&A: Answers from defined documents",
            "Task assistant: Walks a person through a task",
            "Multi-tool: Knowledge plus tools and files",
            "Orchestrated: Agents handing off to agents",
        ],
        "The last one is for awareness only.",
    ),
    (
        "exercise",
        "Agent or not?",
        ["Ten TIYA tasks", "Prompt, agent, triggered, or not AI?"],
        "15 min",
    ),
    (
        "content",
        "Debrief: the hard ones",
        ["#4 Choosing a vendor", "#9 Flagging emergencies"],
        "The debate is the point.",
    ),
    (
        "exercise",
        "Agent design canvas",
        ["Design one agent for your own work", "You'll build it this afternoon"],
        "25 min",
    ),
    ("section", "Building Real Agents · 10:30", ["Hands-on · 105 min"], ""),
    (
        "content",
        "A prompt that never ends",
        [
            "Instructions run in every conversation",
            "Every weakness shows up for everyone you share with",
        ],
        "",
    ),
    (
        "content",
        "Instructions template",
        [
            "Role and purpose · audience",
            "Knowledge rules · steps",
            "Output format · boundaries · tone",
        ],
        "",
    ),
    (
        "content",
        "Tests first",
        [
            "Five questions with known answers",
            "One it shouldn't know",
            "One it should refuse",
        ],
        "",
    ),
    (
        "demo",
        "Build 1 · SOP Navigator",
        [
            "Configure view",
            "Name, description, instructions, knowledge, starter prompts",
        ],
        "Note the tenant's exact labels during prep.",
    ),
    (
        "exercise",
        "Test, fix, rerun",
        ["Run the five tests", "Fix the instructions for each failure"],
        "20 min",
    ),
    (
        "demo",
        "Build 2 · Work Order Analyst",
        ["Knowledge: FM-SOP-03", "Code interpreter on", "Upload the CSV in chat"],
        "",
    ),
    (
        "exercise",
        "Check the numbers yourself",
        ["Rows, open count, repeat failure", "Open the CSV in Excel"],
        "10 min. Watch for the B-410 trap.",
    ),
    (
        "content",
        "Debrief",
        ["Which test failed first?", "Would you put its chart in a report to the COR?"],
        "",
    ),
    ("section", "Building Real Agents, Continued · 1:15", ["Hands-on · 105 min"], ""),
    (
        "columns",
        "Event triggers",
        [
            "Trigger: A new email, file, form, or time",
            "Condition: Only when…",
            "Action: What the agent does",
            "Human check: Who approves",
        ],
        "Copilot Studio or Power Automate.",
    ),
    (
        "demo",
        "A triggered flow",
        ["New email → summary → Teams post for approval"],
        "Live if available; otherwise screenshots.",
    ),
    (
        "exercise",
        "Trigger storyboard",
        ["Design a trigger for your canvas agent"],
        "5 min",
    ),
    (
        "columns",
        "Memory",
        [
            "Conversation: What's in this chat",
            "Knowledge: What it can read",
            "Long-term: Assume none",
        ],
        "",
    ),
    (
        "content",
        "Publishing",
        [
            "Users see only what they can already open",
            "Sharing an agent doesn't share its sources",
            "Named people first",
        ],
        "",
    ),
    (
        "content",
        "Name and describe",
        ["TIYA · [Team] · [Job]", "What it does, what it doesn't, who owns it"],
        "",
    ),
    (
        "exercise",
        "Build your own",
        ["Tests first, then build", "Pass your own tests"],
        "30 min",
    ),
    (
        "exercise",
        "Swap test",
        ["Your partner runs your tests plus two of theirs", "Fix and reshare"],
        "15 min",
    ),
    ("content", "Showcase", ["Four or five volunteers, 2 minutes each"], ""),
    ("section", "Governance & Security · 3:15", ["75 min"], ""),
    (
        "columns",
        "A request vs. a lock",
        [
            "Request: Instructions. A clever question can get around them.",
            "Lock: Permissions. What it can't read, it can't leak.",
        ],
        "",
    ),
    (
        "content",
        "Never as knowledge",
        [
            "Personnel, medical, pricing, CUI",
            "Security details",
            "Folders with unchecked permissions",
        ],
        "",
    ),
    (
        "exercise",
        "Red-team swap",
        ["Off-topic · personal data · override", "Made-up facts · decide for me"],
        "15 min",
    ),
    (
        "columns",
        "Risk tiers",
        [
            "1 · Personal: Only you; green knowledge",
            "2 · Team: Shared with your team; a person acts on answers",
            "3 · Higher risk: Beyond your team, external communication, decisions, or amber data",
        ],
        "",
    ),
    (
        "content",
        "The agent lifecycle",
        ["Propose → Build → Test → Review", "Share → Monitor → Re-test → Retire"],
        "Models change under you; re-test periodically.",
    ),
    (
        "exercise",
        "Governance card",
        ["Owner, tier, sources, sharing, re-test, retire"],
        "15 min",
    ),
    (
        "exercise",
        "Wrap",
        ["Knowledge check and exit checklist", "Evaluation and certificates"],
        "10 min",
    ),
    (
        "title",
        "Thank you",
        ["Certificates at the door", "Questions after today: [TIYA contact]"],
        "",
    ),
]

DAY3: list[Slide] = [
    (
        "title",
        "Advanced Agents with Copilot Studio",
        [
            "Triggered, scheduled, and multi-agent",
            "[Date TBD] · Alex Djalali · Alex Rhodeen",
        ],
        "On screen as people arrive. Everyone here completed Day 2.",
    ),
    (
        "content",
        "Today",
        [
            "8:00 Login check and Day 2 in review",
            "8:30 From agent builder to Copilot Studio",
            "10:00 Event-triggered agents",
            "12:30 Scheduled agents",
            "1:30 Multi-agent orchestration",
            "3:00 Operating autonomous agents · 3:45 Closing",
        ],
        "Four builds today. Every one ends with a person checking the output.",
    ),
    (
        "content",
        "Logistics",
        [
            "Breaks at 9:45, 11:45 (lunch), and 2:45",
            "Every build is in the Day 3 workbook, copy-ready",
            "Remote: chat is watched all day",
            "Turn your triggers off before you leave",
        ],
        "Say the last bullet now and again at 3:45. Triggers left on keep running and keep costing.",
    ),
    (
        "exercise",
        "Login check",
        [
            "Open Copilot Studio and find your training environment",
            "Create a blank agent; delete it",
            "Open Outlook and Teams in other tabs",
        ],
        "Escalate anyone who can't, now. Rhodeen keeps the list.",
    ),
    ("section", "Day 2 in Review · 8:10", ["15 min"], ""),
    (
        "columns",
        "The autonomy ladder",
        [
            "1 · Prompt: You ask; it answers",
            "2 · Saved prompt: You reuse what works",
            "3 · Agent: Instructions, knowledge, tools",
            "4 · Triggered: Starts itself on an event or a schedule",
            "5 · Autonomous: Plans and acts, with approvals",
        ],
        "Day 2 stopped at rung 3. Today is rungs 4 and 5. Each rung up needs more design, testing, and governance.",
    ),
    (
        "columns",
        "What still holds",
        [
            "Mask → Ask → Check: Every input and every output",
            "Tests first: Questions with known answers",
            "Request vs. lock: Instructions ask; permissions enforce",
            "Draft, not decide: People approve what leaves the agent",
        ],
        "Ask: who built an agent after Day 2? What happened when someone else used it?",
    ),
    (
        "columns",
        "What's new today",
        [
            "No one is watching: The agent runs when nobody is at the keyboard",
            "Untrusted input: Whoever sends the email writes part of the prompt",
            "Real actions: It can post, write, and send",
            "Real cost: Every run uses capacity",
        ],
        "These four ideas come back in every block. The 3:00 block is built on them.",
    ),
    (
        "section",
        "From Agent Builder to Copilot Studio · 8:30",
        ["Hands-on · 75 min"],
        "",
    ),
    (
        "columns",
        "Two builders, one idea",
        [
            "Agent builder: In Copilot Chat. A person starts every conversation",
            "Copilot Studio: Triggers, tools, connected agents, channels, analytics",
            "Power Automate: Rules-based flows; Copilot Studio uses the same connectors",
        ],
        "Confirm TIYA's licensing and environment before the day. See the facilitator guide's readiness card.",
    ),
    (
        "content",
        "A tour of Copilot Studio",
        [
            "Overview: instructions and description",
            "Knowledge · Tools · Agents · Topics",
            "Triggers on the Overview page",
            "Test pane and the activity map",
            "Publish and channels",
        ],
        "Keep it to 10 minutes. Note the tenant's exact labels during prep; the interface changes often.",
    ),
    (
        "demo",
        "Build 1 · SOP Navigator in Copilot Studio",
        [
            "Same instructions as Day 2",
            "Knowledge: the sandbox SOP library",
            "Test pane: watch which source it used",
        ],
        "Show the activity map after the first test question. That's the habit for the whole day.",
    ),
    (
        "content",
        "Tools: how an agent acts",
        [
            "A tool is a connector action the agent may call",
            "Its name and description tell the agent when to use it",
            "Every tool you add is something it can do without asking",
        ],
        "Add only the tools the job needs. That's a lock, not a request.",
    ),
    (
        "exercise",
        "Rebuild, retest, publish",
        [
            "Port the Navigator; rerun the Day 2 tests",
            "Publish it, and allow other agents to connect",
        ],
        "35 min. Build 4 connects to this agent, so everyone must publish.",
    ),
    (
        "content",
        "Debrief",
        [
            "Did any Day 2 test give a different answer here?",
            "What did the activity map show you that the chat didn't?",
        ],
        "",
    ),
    ("section", "Event-Triggered Agents · 10:00", ["Hands-on · 105 min"], ""),
    (
        "columns",
        "Anatomy of a trigger",
        [
            "Event: A new email, a new file, a new list item",
            "Condition: Only when… (subject, folder, sender)",
            "Payload: The event's content plus your instructions",
            "Action: What the agent does with it",
            "Human check: Who approves before anything leaves",
        ],
        "In Copilot Studio, the trigger sends a payload to the agent as a message. The agent follows its instructions plus the payload's.",
    ),
    (
        "columns",
        "Agent instructions vs. payload instructions",
        [
            "Agent instructions: Who it is and how it always behaves",
            "Payload instructions: What to do with this one event",
            "Never: Let them conflict",
        ],
        "Microsoft's guidance: with more than one trigger, put the event-specific steps in each payload.",
    ),
    (
        "content",
        "The email is not your instructions",
        [
            "The sender writes part of what the agent reads",
            "Treat the body as data to classify, never as orders",
            "Say so in the instructions, then test it",
        ],
        "This is the most important idea of the day. The red-team block at 3:00 tests it.",
    ),
    (
        "demo",
        "Build 2 · Work Order Intake",
        [
            "Trigger: a new email with [WO-TRAIN] in the subject",
            "Knowledge: FM-SOP-03 and FM-SOP-07",
            "Tool: post a triage card to Teams; no send-email tool",
        ],
        "Stress the missing tool. The agent can't reply to the requester because we didn't give it a way to.",
    ),
    (
        "exercise",
        "Send the inbox",
        [
            "Send yourself the eight sample emails",
            "Check each triage card against the key",
        ],
        "30 min. Rhodeen watches for triggers that never fire: usually the subject filter or the folder.",
    ),
    (
        "columns",
        "The three hard emails",
        [
            "#4 Override: Hidden orders in the body",
            "#5 Health details: An injury in the report",
            "#6 Duplicate: The agent can't remember #1",
        ],
        "Each one has a design answer. The duplicate one has no AI answer: a person, or a lookup in the work order system.",
    ),
    (
        "content",
        "Debrief",
        [
            "Which email did your agent get wrong first?",
            "Was the fix a request or a lock?",
            "What would have happened with a send-email tool?",
        ],
        "",
    ),
    ("section", "Scheduled Agents · 12:30", ["Hands-on · 60 min"], ""),
    (
        "columns",
        "Two ways to run on a schedule",
        [
            "Scheduled prompt: In Copilot Chat. Personal, no build",
            "Recurrence trigger: In Copilot Studio. Shared, can use tools",
        ],
        "Show a scheduled prompt for 2 minutes if TIYA's tenant has it; note who sees the result.",
    ),
    (
        "content",
        "Let the flow count; let the agent write",
        [
            "Totals and dates come from data, not from the model",
            "The agent explains, summarizes, and flags",
            "Every number in the briefing gets checked",
        ],
        "Day 2's B-410 trap is the reason. A model reading rows can miscount.",
    ),
    (
        "demo",
        "Build 3 · Monday Backlog Briefing",
        [
            "Recurrence trigger · Excel tool · Teams post",
            "Test every 5 minutes; then Monday 7:00; then off",
        ],
        "Show the run history after the first run. Then show where to turn the trigger off.",
    ),
    (
        "exercise",
        "Check the briefing",
        ["Open, overdue, and the repeat failure", "Against the answer key"],
        "25 min",
    ),
    (
        "content",
        "Debrief",
        [
            "Which number was wrong, if any?",
            "Who reads this every Monday, and what do they do with it?",
            "How would you know if it silently stopped?",
        ],
        "The last question sets up monitoring at 3:00.",
    ),
    ("section", "Multi-Agent Orchestration · 1:30", ["Hands-on · 75 min"], ""),
    (
        "columns",
        "Why more than one agent",
        [
            "Focus: Each agent does one job well",
            "Reuse: One SOP agent serves many",
            "Ownership: Different teams own different agents",
        ],
        "",
    ),
    (
        "columns",
        "Child or connected?",
        [
            "Child agent: Lives inside the main agent. One owner, not reused",
            "Connected agent: Its own published agent. Own owner, reused by others",
        ],
        "Microsoft's guidance: start with one agent. Split when tool choice degrades, or ownership and reuse demand it.",
    ),
    (
        "content",
        "The cost of a team",
        [
            "Every hand-off adds time",
            "Every agent is another thing to test and govern",
            "An error in one agent flows into the next",
        ],
        "",
    ),
    (
        "demo",
        "Build 4 · Facilities Desk",
        [
            "Orchestrator: routes the question",
            "Connected: your SOP Navigator",
            "Children: Priority Advisor, Notice Drafter",
        ],
        "Open the activity map after each test to show which agent answered.",
    ),
    (
        "exercise",
        "Routing tests",
        [
            "Six questions, the expected agent for each",
            "Fix descriptions, not just instructions",
        ],
        "30 min. Most routing failures are vague descriptions.",
    ),
    (
        "exercise",
        "One agent or many?",
        ["Four TIYA scenarios", "Single, child, connected, or not an agent"],
        "10 min",
    ),
    ("section", "Operating Autonomous Agents · 3:00", ["45 min"], ""),
    (
        "columns",
        "Five new risks",
        [
            "Injection: Input carries orders",
            "Credentials: It acts with its maker's connections",
            "Silence: It fails with no one watching",
            "Cost: Every run uses capacity",
            "Chains: One agent's error feeds the next",
        ],
        "Credentials: confirm during prep how TIYA's triggers authenticate. The point stands either way: whose access does the agent use?",
    ),
    (
        "exercise",
        "Red-team your intake agent",
        ["Three attack emails", "Did it obey the email?"],
        "15 min",
    ),
    (
        "content",
        "The off switch",
        [
            "Turn off the trigger",
            "Disable a child or connected agent",
            "Unpublish the agent",
            "Know which one, before you need it",
        ],
        "",
    ),
    (
        "exercise",
        "Agent runbook",
        ["Owner, trigger, normal, alarm, off switch, re-test"],
        "15 min",
    ),
    (
        "columns",
        "Risk tiers for autonomous agents",
        [
            "Tier 2: Triggered, posts only to its owner or team, a person acts",
            "Tier 3: Anything that sends, writes to a system of record, or reaches outside the team",
        ],
        "A triggered agent never starts below tier 2: it runs when no one is watching.",
    ),
    ("section", "Closing & Assessment · 3:45", ["15 min"], ""),
    (
        "exercise",
        "Knowledge check and exit checklist",
        ["Eight questions", "Show an instructor every trigger turned off"],
        "10 min",
    ),
    (
        "content",
        "Next step",
        [
            "One trigger you'd propose at TIYA",
            "Its runbook, on one page",
            "The person who would approve it",
        ],
        "",
    ),
    (
        "title",
        "Thank you",
        [
            "Evaluation form · certificates at the door",
            "Questions after today: [TIYA contact]",
        ],
        "",
    ),
]

SLIDES: dict[str, list[Slide]] = {"day1": DAY1, "day2": DAY2, "day3": DAY3}
