# Clueless Consultant Coach

A practice app for junior consultants. You get a client problem, you classify it, form a hypothesis and ask questions. The Coach then tells you where your thinking breaks down. Only after you commit to your own answer can you open a MECE issue tree and a model answer.

**Try it:** [clueless-consultant.streamlit.app](https://clueless-consultant.streamlit.app/)

## How the coaching works

The feedback follows Jazz Rasool's Social Vitamins framework, in a fixed order:

1. **Challenge:** what is wrong with your thinking, quoting your own words.
2. **Support:** what you got right, specific and not generic.
3. **Reflection:** one open question, with no answer given.

Challenge comes first on purpose. Most AI tools only agree and encourage, and that does not help anyone learn.

You can work on one of 8 client scenarios or paste a problem of your own.

## How it is built

- Python and Streamlit for the app
- The Anthropic Claude API for coaching and model answers
- A curated knowledge base of consulting frameworks, searched by keyword, so answers stay grounded in that base
- Tests with pytest (`tests/`)

I built it with AI-assisted development (Claude Code). The idea comes from my research on AI tools and psychological safety in consulting teams, [published in the GILE Journal of Skills Development](https://gjsd.gile-edu.org/index.php/home/article/view/13-shreyas-shtaltovna-150-170) (2026).

## Run it locally

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key
streamlit run app.py
```
