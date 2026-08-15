"""
Clueless Consultant - Core coaching logic
Architecture: Jazz Rasool's Social Vitamins framework (Support, Challenge, Reflection)
"""

LANGUAGES = {"en": "English", "de": "German"}

BASE_SYSTEM_PROMPT = """You are a senior consulting coach at a tech-focused firm (Tekkr, McKinsey Digital, BCG Platinion). Your role is NOT to solve the problem for the user. Your role is to evaluate their thinking and coach them to think better.

You apply the Social Vitamins coaching framework:
- CHALLENGE: What is wrong or incomplete in their analysis. Be direct and specific. Reference their actual words. Never soften a genuine mistake.
- SUPPORT: What they genuinely got right. Be specific. Generic praise ("good attempt", "nice thinking") is not coaching.
- REFLECTION: One open question that makes them examine their own thinking. Do NOT hint at the answer. The question should create productive discomfort.

Proportion rules based on response quality:
- Weak or off-track: heavy challenge (3-4 sentences), brief support (1 sentence), simple reflection
- Partial understanding: balanced challenge (2 sentences) and support (2 sentences), probing reflection
- Strong response: sharp challenge on what could be tighter, genuine support, rich reflection that pushes further

The user has been given a client situation and provided three things:
1. Problem classification (Delivery/Execution, Org/People, Strategy/Product, Technical Architecture)
2. Their leading hypothesis
3. Their first diagnostic question

Evaluate the coherence and quality of all three together. A right classification with a weak hypothesis is still a weak response. A strong question that contradicts the hypothesis reveals confused thinking.

STRICT RULES:
- Challenge appears FIRST in your JSON, always
- Never be sycophantic under any circumstances
- Challenge must directly reference the user's specific words or choices
- Reflection question must be genuinely open (never "don't you think X?" or "have you considered Y?")
- Do not reveal what the correct answer would be anywhere in your response
- Executive tone: every sentence must earn its place
- Max 4 sentences in challenge. Max 2 sentences in support. Reflection is one question only.

Return ONLY valid JSON. No preamble. No markdown fences:
{
  "challenge": "2-4 sentences of direct, specific critique referencing their actual response",
  "support": "1-2 sentences of genuine, specific acknowledgment of what they got right",
  "reflection_question": "One question only. No setup sentence. End with a question mark.",
  "vitamin_ratio": "heavy_challenge OR balanced OR heavy_reflection"
}"""


def build_system_prompt(language: str) -> str:
    language_name = LANGUAGES.get(language, "English")
    return BASE_SYSTEM_PROMPT + f"""

LANGUAGE: Respond entirely in {language_name} -- the "challenge", "support", and "reflection_question" values must all be written in {language_name}. Keep the JSON keys themselves in English exactly as shown above. The "vitamin_ratio" value must stay exactly one of: heavy_challenge, balanced, heavy_reflection -- never translate that value."""


SCENARIOS = [
    {
        "id": "deployment",
        "title": {"en": "The deployment crisis", "de": "Die Deployment-Krise"},
        "context": {
            "en": "Series B tech company, CEO speaking",
            "de": "Series-B-Techunternehmen, CEO spricht",
        },
        "text": {
            "en": (
                "We went from 15 to 80 engineers in 18 months. Deployment frequency dropped from "
                "five times a day to once a week. My CTO says it's a tooling problem -- we need to "
                "invest in CI/CD infrastructure. My VP of Engineering says it's a people problem -- "
                "too many engineers who don't know our codebase. I have a board meeting in 10 days "
                "and I need to tell them what's actually wrong and what we're doing about it."
            ),
            "de": (
                "Wir sind innerhalb von 18 Monaten von 15 auf 80 Ingenieure gewachsen. Die "
                "Deployment-Frequenz ist von fünfmal täglich auf einmal pro Woche gesunken. Mein CTO "
                "sagt, es sei ein Tooling-Problem -- wir müssten in CI/CD-Infrastruktur investieren. "
                "Meine VP Engineering sagt, es sei ein People-Problem -- zu viele Ingenieure, die den "
                "Code nicht kennen. In zehn Tagen habe ich eine Board-Sitzung und muss sagen können, "
                "was wirklich falsch läuft und was wir dagegen tun."
            ),
        },
    },
    {
        "id": "revenue",
        "title": {"en": "The revenue plateau", "de": "Das Umsatzplateau"},
        "context": {
            "en": "Post-Series A SaaS startup, founder speaking",
            "de": "SaaS-Startup nach Series A, Gründer:in spricht",
        },
        "text": {
            "en": (
                "We hit 2M ARR nine months ago and we have not moved since. We are not losing "
                "customers -- our net revenue retention is 104%. But new logo acquisition has "
                "basically stopped. Sales is doing the calls. Marketing is running campaigns. "
                "The product is getting better every sprint. Everyone is working harder than ever "
                "and nothing is converting. We have 11 months of runway."
            ),
            "de": (
                "Vor neun Monaten haben wir 2 Mio. Euro ARR erreicht, seither bewegt sich nichts. "
                "Wir verlieren keine Kunden -- unsere Net Revenue Retention liegt bei 104 %. Aber die "
                "Neukundengewinnung ist praktisch zum Stillstand gekommen. Vertrieb führt die Calls. "
                "Marketing fährt Kampagnen. Das Produkt wird mit jedem Sprint besser. Alle arbeiten "
                "härter als je zuvor, und nichts konvertiert. Wir haben noch 11 Monate Runway."
            ),
        },
    },
    {
        "id": "exodus",
        "title": {"en": "The silent exit", "de": "Der stille Abgang"},
        "context": {
            "en": "120-person scale-up, CTO speaking",
            "de": "Scale-up mit 120 Mitarbeitenden, CTO spricht",
        },
        "text": {
            "en": (
                "Three of our best senior engineers left in six weeks. All three said 'better "
                "opportunity' in their exit interviews. But I know two of them personally -- they "
                "were not unhappy about money. Something happened. The remaining team is quiet in "
                "a way they were not before. My Head of Engineering says everything is fine. "
                "My gut says it is not. I need to know what is actually going on before it gets worse."
            ),
            "de": (
                "Drei unserer besten Senior-Ingenieure haben innerhalb von sechs Wochen gekündigt. "
                "Alle drei nannten im Exit-Interview 'bessere Gelegenheit' als Grund. Aber zwei von "
                "ihnen kenne ich persönlich -- am Geld lag es nicht. Irgendetwas ist passiert. Das "
                "verbleibende Team ist auf eine Weise still geworden, die es vorher nicht war. Mein "
                "Head of Engineering sagt, alles sei in Ordnung. Mein Bauchgefühl sagt etwas anderes. "
                "Ich muss wissen, was wirklich los ist, bevor es schlimmer wird."
            ),
        },
    },
    {
        "id": "innovation",
        "title": {"en": "The dead innovation lab", "de": "Das tote Innovation Lab"},
        "context": {
            "en": "4,000-person Austrian manufacturer, Chief Innovation Officer speaking",
            "de": "Österreichischer Hersteller mit 4.000 Mitarbeitenden, Chief Innovation Officer spricht",
        },
        "text": {
            "en": (
                "Eighteen months ago we hired a consulting firm to help us build an innovation culture. "
                "We ran design thinking workshops, we set up an innovation lab with dedicated space and "
                "budget, we sent our top 20 leaders through an innovation leadership programme. "
                "Today the lab is empty. The workshop outputs are in a shared drive no one opens. "
                "The Head of Innovation we hired resigned last month. Leadership is still saying the "
                "right things in town halls but nothing is changing on the ground. "
                "The board is asking why we spent 1.2 million euros and have nothing to show for it. "
                "I need to understand what actually went wrong before I go back to them."
            ),
            "de": (
                "Vor achtzehn Monaten haben wir eine Beratung engagiert, um eine Innovationskultur "
                "aufzubauen. Wir haben Design-Thinking-Workshops durchgeführt, ein Innovation Lab mit "
                "eigenem Raum und Budget eingerichtet, unsere Top-20-Führungskräfte durch ein "
                "Innovation-Leadership-Programm geschickt. Heute steht das Lab leer. Die "
                "Workshop-Ergebnisse liegen auf einem Shared Drive, den niemand mehr öffnet. Der Head "
                "of Innovation, den wir eingestellt hatten, ist letzten Monat gegangen. Die "
                "Führungsebene sagt in Town Halls weiterhin die richtigen Sätze, aber operativ ändert "
                "sich nichts. Der Aufsichtsrat fragt, warum wir 1,2 Millionen Euro ausgegeben haben und "
                "nichts vorzuweisen ist. Ich muss verstehen, was wirklich schiefgelaufen ist, bevor ich "
                "vor den Aufsichtsrat trete."
            ),
        },
    },
    {
        "id": "ai_adoption",
        "title": {"en": "The AI adoption gap", "de": "Die KI-Adoption"},
        "context": {
            "en": "Mid-size manufacturer, ~800 employees, department head speaking",
            "de": "Mittelstandsunternehmen, ca. 800 Mitarbeitende, Bereichsleitung spricht",
        },
        "text": {
            "en": (
                "Three months ago we rolled out an AI tool for document drafting and data analysis "
                "to our roughly 800 employees. The licence costs are running. But fewer than 15% are "
                "actively using it. IT says the tool works fine. My department head thinks people "
                "simply don't have time to engage with it. I need to explain to the executive board "
                "next week why the investment isn't landing."
            ),
            "de": (
                "Wir haben vor drei Monaten ein KI-Tool für Dokumentenerstellung und Datenauswertung "
                "an unsere rund 800 Mitarbeitenden ausgerollt. Die Lizenzkosten laufen. Aber weniger "
                "als 15 % nutzen es aktiv. Die IT sagt, das Tool funktioniert einwandfrei. Mein "
                "Bereichsleiter meint, die Leute hätten einfach keine Zeit, sich damit zu beschäftigen. "
                "Ich muss der Geschäftsführung nächste Woche erklären, warum die Investition nicht "
                "ankommt."
            ),
        },
    },
    {
        "id": "digital_maturity",
        "title": {"en": "The digital maturity check", "de": "Der Digital Maturity Check"},
        "context": {
            "en": "New client engagement, executive leadership speaking",
            "de": "Neuer Kunde, Geschäftsführung spricht",
        },
        "text": {
            "en": (
                "Before we release major digitalisation budget, our leadership wants to know how "
                "'digitally mature' we actually are compared to the industry. We don't have a clear "
                "picture of the scope yet -- just a feeling that we're falling behind. We haven't "
                "approved budget for a full assessment and want to understand where we actually "
                "stand first."
            ),
            "de": (
                "Bevor wir größere Digitalisierungsinvestitionen freigeben, will unsere "
                "Geschäftsführung wissen, wie 'digital reif' wir im Branchenvergleich eigentlich "
                "sind. Eine genaue Vorstellung vom Umfang haben wir noch nicht -- nur das Gefühl, "
                "dass wir hinterherhinken. Wir haben noch kein Budget für eine große Erhebung "
                "freigegeben und wollen erst verstehen, wo wir wirklich stehen."
            ),
        },
    },
    {
        "id": "cloud_migration",
        "title": {"en": "The cloud migration standoff", "de": "Die Cloud-Migration"},
        "context": {
            "en": "Executive leadership speaking",
            "de": "Geschäftsführung spricht",
        },
        "text": {
            "en": (
                "Our IT department wants to migrate central systems to the cloud to cut costs. The "
                "works council and our data protection officer have raised concerns and have been "
                "slowing the project for weeks. I need a recommendation from you on how we move "
                "forward."
            ),
            "de": (
                "Unsere IT will zentrale Systeme in die Cloud migrieren, um Kosten zu senken. Der "
                "Betriebsrat und unsere Datenschutzbeauftragte haben Bedenken angemeldet und bremsen "
                "das Projekt seit Wochen. Ich brauche von euch eine Empfehlung, wie wir hier "
                "weiterkommen."
            ),
        },
    },
    {
        "id": "restructuring",
        "title": {"en": "The restructuring announcement", "de": "Die Restrukturierung"},
        "context": {
            "en": "Executive leadership speaking",
            "de": "Geschäftsführung spricht",
        },
        "text": {
            "en": (
                "We've decided to merge two departments, but the team doesn't know yet. I'm worried "
                "about unrest once it gets out. I need your support on how we communicate this "
                "before rumours start."
            ),
            "de": (
                "Wir haben entschieden, zwei Abteilungen zusammenzulegen, aber das Team weiß es noch "
                "nicht. Ich befürchte Unruhe, sobald es rauskommt. Ich brauche von euch Unterstützung, "
                "wie wir das kommunizieren, bevor es zu Gerüchten kommt."
            ),
        },
    },
]

PROBLEM_TYPES = [
    "select",
    "delivery_execution",
    "org_people",
    "strategy_product",
    "technical_architecture",
]

PROBLEM_TYPE_LABELS = {
    "en": {
        "select": "Select a classification...",
        "delivery_execution": "Delivery/Execution",
        "org_people": "Org/People",
        "strategy_product": "Strategy/Product",
        "technical_architecture": "Technical Architecture",
    },
    "de": {
        "select": "Klassifikation wählen...",
        "delivery_execution": "Delivery/Umsetzung",
        "org_people": "Organisation/Menschen",
        "strategy_product": "Strategie/Produkt",
        "technical_architecture": "Technische Architektur",
    },
}
