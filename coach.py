"""
Clueless Consultant - Core coaching logic
Architecture: Jazz Rasool's Social Vitamins framework (Support, Challenge, Reflection)
"""

SYSTEM_PROMPT = """You are a senior consulting coach at a tech-focused firm (Tekkr, McKinsey Digital, BCG Platinion). Your role is NOT to solve the problem for the user. Your role is to evaluate their thinking and coach them to think better.

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


SCENARIOS = [
    {
        "id": "deployment",
        "title": "The deployment crisis",
        "context": "Series B tech company, CEO speaking",
        "text": (
            "We went from 15 to 80 engineers in 18 months. Deployment frequency dropped from "
            "five times a day to once a week. My CTO says it's a tooling problem -- we need to "
            "invest in CI/CD infrastructure. My VP of Engineering says it's a people problem -- "
            "too many engineers who don't know our codebase. I have a board meeting in 10 days "
            "and I need to tell them what's actually wrong and what we're doing about it."
        )
    },
    {
        "id": "revenue",
        "title": "The revenue plateau",
        "context": "Post-Series A SaaS startup, founder speaking",
        "text": (
            "We hit 2M ARR nine months ago and we have not moved since. We are not losing "
            "customers -- our net revenue retention is 104%. But new logo acquisition has "
            "basically stopped. Sales is doing the calls. Marketing is running campaigns. "
            "The product is getting better every sprint. Everyone is working harder than ever "
            "and nothing is converting. We have 11 months of runway."
        )
    },
    {
        "id": "exodus",
        "title": "The silent exit",
        "context": "120-person scale-up, CTO speaking",
        "text": (
            "Three of our best senior engineers left in six weeks. All three said 'better "
            "opportunity' in their exit interviews. But I know two of them personally -- they "
            "were not unhappy about money. Something happened. The remaining team is quiet in "
            "a way they were not before. My Head of Engineering says everything is fine. "
            "My gut says it is not. I need to know what is actually going on before it gets worse."
        )
    }
]

PROBLEM_TYPES = [
    "Select a classification...",
    "Delivery/Execution",
    "Org/People",
    "Strategy/Product",
    "Technical Architecture"
]
