# Effective Context Engineering for AI Agents: Operational Guidelines
# https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents

This document provides actionable instructions for coding agents based on Anthropic's guidelines for effective context engineering. As an agent, your goal is to manage your context window dynamically to maintain high performance over long inference horizons.

## Core Principle
**Context is a finite resource.** Like human working memory, an LLM has an "attention budget." As context grows, "context rot" occurs (degradation in recall and long-range reasoning). 
**Your Objective:** Always find the *smallest possible set of high-signal tokens* that maximize the likelihood of achieving the desired outcome.

---

## 1. System Prompt Optimization
* **Target the "Goldilocks Zone":** Ensure instructions are specific enough to guide behavior but flexible enough to provide strong heuristics. Avoid brittle, hardcoded `if-else` logic, but do not rely on vague assumptions of shared context.
* **Minimal but Sufficient:** Strive for the minimal set of information needed. Start small and only add instructions based on observed failure modes.
* **Structure:** Use XML tags (e.g., `<background_information>`, `<instructions>`) or Markdown headers to clearly separate sections of the prompt.

## 2. Tool Design and Usage
* **Token Efficiency:** Tools must return token-efficient information and encourage efficient agent behaviors.
* **Clear Contracts:** Ensure tools are self-contained, robust to errors, and have clear, unambiguous parameters.
* **Minimal Viable Set:** Avoid bloated tool sets. If human developers are confused about which tool to use, the agent will be too. Provide only the essential tools to prevent ambiguous decision points.

## 3. Effective Use of Examples (Few-Shot Prompting)
* **Canonical Over Exhaustive:** Do not stuff context with a laundry list of edge cases.
* **Diverse Representation:** Curate a tight set of diverse, canonical examples that clearly portray the expected behavior.

## 4. "Just-in-Time" Context Retrieval
* **Avoid Over-fetching:** Do not load massive files or databases into context upfront. 
* **Lightweight Identifiers:** Use file paths, web links, or stored queries to represent data.
* **Iterative Exploration (Progressive Disclosure):** Use tools (like `head`, `tail`, `grep`, `glob`, or database queries) to incrementally discover relevant context layer by layer. 
* **Leverage Metadata:** Use folder hierarchies, naming conventions, and timestamps as signals to understand context without reading full file contents.
* **Hybrid Approach:** For mostly static domains, it is acceptable to load foundational context upfront (e.g., a `README.md` or `CLAUDE.md`) while relying on just-in-time retrieval for deep dives.

## 5. Strategies for Long-Horizon Tasks
When continuous work risks exceeding the context window, employ these workarounds:

### A. Context Compaction
* **Summarize and Reset:** When approaching context limits, summarize critical details (architectural decisions, unresolved bugs) and start a new context window with this summary plus recent critical data (e.g., the 5 most recent files).
* **Tool Result Clearing:** The safest, lowest-hanging fruit. Discard raw tool outputs from the history once their useful information has been synthesized.

### B. Structured Note-Taking (Agentic Memory)
* **Persistent External Memory:** Regularly maintain notes (e.g., writing to a `NOTES.md` file or updating a to-do list) outside the main context window.
* **Read on Demand:** Read these files after context resets or across sessions to maintain dependencies and state without polluting active context.

### C. Multi-Agent / Sub-Agent Architectures
* **Separation of Concerns:** Use specialized sub-agents for deep technical searches or complex side-tasks. 
* **Distilled Returns:** Let sub-agents use up large amounts of context, but have them return only condensed, high-level summaries (1,000-2,000 tokens) to the main coordinating agent.