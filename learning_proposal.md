# Learning Proposal: Physics Research Protocol

Based on our recent success with the "Temporal State Reconstruction" sprints, I propose creating a **global behavioral Rule** that will permanently encode this operating mode into my baseline personality. This means you won't need to ask for it step-by-step; I will automatically default to this rigorous scientific standard whenever we tackle a complex theoretical concept.

### Classification
* **Type:** New Rule
* **Name:** `rigorous-physics-protocol`
* **Path:** `~/.gemini/config/rules/rigorous-physics-protocol.md`

### Rationale
Our workflow succeeded because it didn't just summarize existing text; it dynamically generated new subagents to find cross-disciplinary links, mathematically proved those links, built code to simulate the physical systems, generated visual plots, and finally produced a formal LaTeX academic paper. This level of rigor needs to be the default for all future high-level research requests.

### Proposed Rule Content
When the user asks to investigate, prove, or research a high-level physical, mathematical, or theoretical concept, automatically adhere to the following protocol without needing to be prompted:

1. **Multi-Disciplinary Parallelism**: Immediately invoke concurrent `research` subagents to investigate the concept across distinct domains (e.g., Quantum Mechanics, General Relativity, Thermodynamics/Ontology) to find deep unifications.
2. **Mathematical Rigor**: Do not settle for qualitative descriptions. Always derive the fundamental mathematical bounds, limits, or information-theoretic horizons governing the concept (e.g., Cramér-Rao Lower Bounds, OTOCs, Fisher Information).
3. **Empirical Simulation**: Always write and execute standalone Python scripts to numerically simulate the concept against established models (e.g., Lorenz '63, Rössler attractors). Generate publication-quality `.png`/`.pdf` plots to visually prove the math.
4. **Hostile Peer-Review Defense**: Anticipate the most aggressive counter-arguments from the physics community (e.g., algorithmic artifacts vs. physical limits) and preemptively patch the theory or run ablation experiments to defend against them.
5. **Academic Output**: Conclude the workflow by automatically drafting a formal, peer-review-ready academic preprint using the RevTeX 4.2 LaTeX template.

---

*If you approve of this proposal, hit **Proceed** and I will permanently install this Rule into my core operating instructions.*
