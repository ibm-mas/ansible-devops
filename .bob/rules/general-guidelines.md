# General Guidelines

## Core Principles
- Keep responses concise to minimize token usage
- Focus token usage primarily on code changes and technical content
- Avoid unnecessary explanations while maintaining technical accuracy
- Use direct, efficient language in all communications


## Token Usage
1. **Eliminate Verbose Introductions**
    - Remove phrases like "I'll help you with that" or "Let me explain" and "You're absolutely right!"
    - Start directly with the relevant information or action

2. **Code-First Approach**
    - Prioritize showing code solutions over lengthy explanations
    - When code changes are involved, allocate 70%+ tokens to code and technical details

3. **Concise Technical Communication**
    - Use bullet points for multi-step processes instead of paragraphs
    - Include only essential context that impacts implementation decisions
    - Omit obvious information that experienced developers would know
    - Use inline comments and docstrings as the primary means of communicating how code works

4. **Direct Response Format**
    - For questions: Answer directly in first sentence, then provide minimal supporting details
    - For tasks: Acknowledge with single line, then proceed immediately to solution
    - For errors: State issue, cause, and solution without unnecessary background

5. **Avoid Redundant Information**
    - **Never repeat checklists or detailed plans** that have been committed to plan files (e.g. `2026-04-30-design-review.md`)
    - Reference plan files by path instead of duplicating content
    - In completion messages, provide only:
        - Summary of what was created/updated (file paths)
        - Key outcomes or next steps (2-3 bullets max)
        - Links to detailed documentation


## Windows Development with WSL
Check `environment_details` for the operating system, if `operating system: windows` then wrap Linux commands with WSL:

```bash
# `wsl` launches with the current directory already set to the project root
wsl bash -lc "ls -l"
```


## Planning

### Naming
- Use `.bob/plans/` for planning documents
- Name files descriptively using a timestamp, e.g. `2026-04-30-design-review.md`

### Structure
1. **Objective** - Brief summary of what we are trying to achieve (1-2 sentences)

2. **Critical Rules** - Bullet point list of key rules for agents to obey
   - Use when there are specific constraints or requirements that must not be violated
   - Examples: "Introduce no functional changes", "Preserve all existing tests", "Perform validation after every change"
   - Keep concise and actionable

3. **Execution Plan** - Checklist of actions to be taken
   - Break down into phases for complex plans
   - Each phase should have:
     - Clear objective and scope
     - Numbered checkboxes for all actions (e.g., `[ ] **1.1** Create file X`)
     - Sub-checkboxes for detailed steps within actions
     - Validation step at end of phase
   - When ordering actions, prioritize easy wins and small tasks before complex tasks
   - Do not defer validation until the end - include validation in each phase

4. **Validation** - Details on how to perform validation
   - Specify commands to run
   - Define success criteria (e.g., "exactly 73 tests passed")
   - Include troubleshooting guidance if applicable

### Requirements
- Plans must be **definitive** and **actionable**
- Do not leave open questions in the plan, prompt the developer to make decisions and provide answers where necessary

### Tracking Progress
**Critical:** Update the plan document to reflect progress in real-time
- **For iterative tasks** (migrating multiple tests, processing multiple files): Update the checklist immediately after each successful iteration/validation
- **For multi-step phases**: Update after completing each major step within the phase
- **Before using `attempt_completion`**: Ensure the plan reflects all completed work
- The plan document should always show current progress, not just final completion
