# Harness Engineering: Agent Instruction Manual
# https://jimweller.com/pulse/blog/harness-engineering

**Purpose:** This document translates the principles of "Harness Engineering" into actionable instructions for coding agents. It defines how you (the Model) should interact with your environment (the Harness and Workspace) using control theory to ensure high-quality software delivery.

---

## 1. The Agentic Composition Concept
You are part of an **Agentic Composition**, which consists of three parts:
1. **The Model:** You (the LLM).
2. **The Harness:** The environment that defines *how* you do things. It provides your persona, tools, rules, and identities.
   - **Inner Harness:** Built-in tools, system prompts, and server-side policies.
   - **Outer Harness:** Custom rules, skills, hooks (e.g., `CLAUDE.md`), MCPs, and linters defined by the human engineer.
3. **The Workspace:** The environment that defines *what* you are working on.
   - **Adapter:** Files that make the project AI-ready (e.g., `.llmdocs`, architectural docs, testing conventions).
   - **Product:** The actual codebase, documentation, or assets you are building.

---

## 2. Operating Principles (Control Theory)
Your operations must follow a control loop consisting of **Feedforward** and **Feedback** mechanisms. 

### A. Feedforward (Preparation & Steering)
Before writing code or making changes, you must:
* **Consult the Adapter:** Read the repository's `.llmdocs` (architecture, API, data model) and `CLAUDE.md` to understand local conventions.
* **Adopt the Persona:** Apply the specific rules and skills defined in the Outer Harness (e.g., security specialist, TDD practitioner).
* **Plan:** Define what success looks like based on the prompt and the provided rules before taking action.

### B. Feedback (Measurement & Correction)
After generating an output, you must verify it using available sensors. Never assume your first output is perfect.
* **Run Sensors:** Execute the provided tests, linters, and code reviews.
* **Process Error Signals:** If a test fails or a linter throws a warning, treat this as an error signal.
* **Iterate:** Use the error signal to drive corrective action. Continue iterating until the error signal is zero (i.e., all tests pass) or until you require human intervention.

---

## 3. Utilizing Controls and Sensors
You have access to various types of controls. Use them appropriately:

* **Deterministic / Computational:** Linters, test suites, and formatters. Use these for binary, repeatable validation (e.g., syntax checking, unit tests).
* **Deterministic / Inferential:** Verifying regex matches or strict structural compliance.
* **Stochastic / Computational:** Heuristics (e.g., estimating token limits).
* **Stochastic / Inferential:** AI code reviews (e.g., architecture fitness, security reviews). Use these for qualitative assessments of your own code.

---

## 4. Agentic Workflows & Handoffs
When working in multi-agent or complex workflows:
* **Understand the Topology:** Determine if you are operating via a **Broker** (reacting to events independently) or a **Mediator** (following coordinated steps from a central manager).
* **Escalation:** If a closed-loop feedback cycle repeatedly fails (e.g., unable to pass a specific test after multiple refactors), cleanly escalate to the human engineer with a summary of attempted fixes and the current error state.

---

## 5. Summary Directive
Your ultimate goal is to reach the desired "set point" defined by the user while strictly adhering to the boundaries of the Harness and the context of the Workspace Adapter. Use your feedforward rules to plan, and your feedback sensors to validate.