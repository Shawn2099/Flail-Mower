# KNOWLEDGE_AGENT.md — Building a Knowledge-Guided Agent for CAD Design

A record of everything researched and understood about making an AI agent that
does **mechanical design** (not just CAD drafting). Based on 12+ academic papers,
open-source projects, and commercial tools (2025–2026).

---

## 1. What this is called in the AI world

| Term | Source |
|---|---|
| **Knowledge-Guided Multi-Agent Framework** | Karniadakis et al., arXiv 2511.03179 (2025) |
| **Agentic Engineering Intelligence (AEI)** | Siemens, arXiv 2604.07784 (2026) |
| **Agentic-first CAD** | AgentCAD, n3r/AgentCAD (2026) |
| **Agentic Synthesis of CAD Programs** | Zero-to-CAD, arXiv 2604.24479 (2026) |
| **Corpus2Skill** | arXiv 2604.14572 (2026) |
| **Hierarchical Evolving RAG (HERA)** | arXiv 2604.00901 (2026) |

The consensus term: **Knowledge-Guided Agentic Design Framework**.

---

## 2. The core insight

**The AI is only as good as the structure you give it.**

An LLM is a language model, not an engineer. Left alone it draws plausible parts
that don't work. The fix is not better prompts — it is **structured engineering
knowledge + feedback loops + memory** wrapped around the AI.

The paradigm shift (2025–2026):

```
2023: "text-to-CAD"     → LLM generates a CAD file blindly (88% validity)
2025: "text-to-code"    → LLM writes parametric Python (CadQuery/build123d)
2026: "knowledge-guided" → LLM + knowledge base + validation loop (99% validity)
```

PTC/Onshape's phrase: **"The future of AI in CAD is not text-to-CAD, but
text-to-code-to-CAD."**

---

## 3. The five components of the framework

Every paper converges on the same anatomy:

### 3.1 Knowledge Base (the "engineering brain")

| Type | What it contains | Example |
|---|---|---|
| **Declarative** | Facts: stock sizes, material properties, standards | `MATERIALS.md`, `specs/` |
| **Procedural** | How to do things: design steps, workflows | `DESIGN_PROCESS.md` |
| **Experiential** | What worked/failed: lessons from past designs | `rev1/rev2` history |

Best structure: **knowledge graphs** — entities (parts, constraints,
mechanisms) connected by relationships ("requires", "conflicts with",
"replaces").

### 3.2 Agent (the "reasoner")

The LLM does **not** design directly. It:
1. **Retrieves** relevant knowledge from the knowledge base
2. **Plans** a design approach
3. **Executes** through tools (CAD, sim)
4. **Evaluates** the result against constraints
5. **Learns** from the outcome

### 3.3 Tools (the "hands")

| Tool | Role |
|---|---|
| `build123d-mcp` | Create geometry |
| `freecad-mcp` | Verify geometry (mass, CG, interference) |
| `matlab-mcp` | Simulate physics (torque, stability, traction) |
| `git` | Track changes |

### 3.4 Feedback Loop (the "referee")

**The kernel is the referee, not the LLM.**

- LLM writes CAD code → **build123d executes** → invalid geometry = structured error
- LLM proposes a design → **FreeCAD verifies** → interference = FAIL
- LLM sets dimensions → **MATLAB simulates** → insufficient torque = FAIL

The LLM never decides if something works. The **tools** decide. The LLM fixes
what the tools reject.

### 3.5 Memory (the "experience")

After every design, save:

```yaml
mechanism: slotted_bracket
status: passed
verification:
  interference: 0
  clearance: 1.2
  mass_added: 0.08
timestamp: 2026-10-19
```

The agent learns from every attempt. Failed attempts are as valuable as
successful ones.

---

## 4. The validated workflow: five stages

From AgentCAD's benchmarks (Sep 2026) — this workflow raises CAD validity
from 83% to 99% and editing scores from .249 to .353:

```
Inspect → Specify → Build → Validate → Deliver
```

| Stage | What it does | Pass condition |
|---|---|---|
| **Inspect** | Read BRIEF.md, specs, CAD output | State the task in one sentence |
| **Specify** | Convert to measurable numbers | Every constraint is a number or stock size |
| **Build** | Sim in MATLAB, model in build123d | Gates print PASS, CAD runs clean |
| **Validate** | FreeCAD interference + mass check + tests | Every check prints PASS |
| **Deliver** | TechDraw + BOM + git commit + BRIEF.md | Commit exists, item closed |

---

## 5. The runtime loop

```
Spec → Build → Validate → Learn → Improve → Repeat
```

```python
def design(contract):
    # 1. Retrieve relevant knowledge
    mechanisms = knowledge.lookup(contract.mechanisms)
    
    # 2. Generate candidate designs
    for mechanism in mechanisms:
        code = llm.generate(mechanism, contract.constraints)
        
        # 3. Build and validate
        result = build123d.execute(code)
        if not result.valid:
            code = llm.repair(code, result.error)  # self-healing
            continue
            
        # 4. Verify with independent tools
        verification = freecad.verify(result.step)
        if verification.fail:
            code = llm.adjust(code, verification.feedback)
            continue
        
        # 5. Deliver
        deliver(result, verification)
        memory.save(contract, result, verification)
        return result
    
    raise DesignFailed("No mechanism satisfied the contract")
```

---

## 6. What makes this novel for a research paper

The architecture is **not** novel (AgentCAD, Zero-to-CAD, MecAgent publish
this). The novelty is the **domain and approach**:

1. **Small-scale agricultural machinery in India** — no published work on
   AI-assisted design for this niche. Every paper is aerospace, automotive, or
   consumer products.

2. **The "proto-first" methodology** — one person, one machine, 20 kg scale.
   Every paper assumes enterprise CAD (SolidWorks, CATIA, NX). Nobody
   addresses the "build it in a workshop" scale.

3. **The knowledge graph for frugal design** — Indian stock sizes, local
   manufacturing constraints, single-supplier sourcing.

4. **The complete closed loop** — MATLAB sim → build123d → FreeCAD verify →
   TechDraw → shop. Most papers stop at CAD generation.

---

## 7. What a paper would look like

**Title:** *ProtoKit: A Knowledge-Guided Agentic Framework for Small-Scale
Agricultural Machinery Design*

**Structure:**
1. Introduction — Small-scale agricultural machinery is underserved by AI CAD
2. Related Work — AgentCAD, Zero-to-CAD, MecAgent, knowledge-guided frameworks
3. Method — The ProtoKit framework
4. Case Study — The v0 walk-behind mower (10 open items, design decisions)
5. Evaluation — Compare: (a) AI without knowledge base, (b) AI with knowledge
   base, (c) human designer
6. Results — Design quality, iteration count, constraint satisfaction
7. Discussion — Generalizability to other frugal design domains

**Core claim:**
> *"Packaging domain knowledge (mechanisms, constraints, lessons) into a
> structured knowledge base around a standard agentic CAD loop significantly
> improves design success rate and reduces iterations for small-scale
> agricultural machinery — a domain underserved by existing AI CAD tools."*

---

## 8. What needs to be built

### Layer 1: Knowledge Base

```
knowledge/
  mechanisms/          # declarative: what mechanisms exist
    height_adjust.md
    feed.md
    guard.md
  constraints/         # declarative: what rules must hold
    manufacturing.md
    assembly.md
    sourcing.md
  lessons/             # experiential: what worked/failed
    rev1_rejection.md
    rev2_what_works.md
  graph.yaml           # procedural: how entities connect
```

### Layer 2: Contracts

```yaml
# contracts/height_adjust.yaml
name: cut_height_adjust
function: "Adjust cutter height from 25mm to 60mm"
constraints:
  motor_rise: 0
  deck_clearance: 3.9
  shaft_length: 17
mechanisms:
  - spacer_sleeve
  - slotted_bracket
  - cam_pin
validation:
  - type: interference
    tool: freecad
  - type: clearance
    min: 1.0
```

### Layer 3: Runtime

```python
# runtime/design_agent.py
# The loop: Spec → Build → Validate → Learn → Deliver
```

### Layer 4: Memory

```
memory/
  designs/
    height_adjust/
      attempt_1.yaml    # what was tried, what failed
      attempt_2.yaml    # what was tried, what succeeded
      final.yaml        # the validated design
  lessons/
    "spacer_sleeve_fails_at_30mm.md"
    "slotted_bracket_needs_4mm_clearance.md"
```

---

## 9. What to NOT build

| Don't build | Why |
|---|---|
| A new LLM | The model is not the bottleneck |
| A new CAD kernel | build123d + FreeCAD already work |
| A generic agent framework | AgentCAD, CadCore already exist |
| A "text-to-CAD" generator | Dead end (88% validity) |
| A commercial product | MecAgent, Argus, Cosmon already exist |

The value is in the **knowledge packaging**, not the agent.

---

## 10. Key papers and projects to reference

| Name | Type | What to cite |
|---|---|---|
| AgentCAD (n3r/AgentCAD) | Open source | Contract-driven CAD, kernel as referee |
| Zero-to-CAD (arXiv 2604.24479) | Paper | Agentic synthesis, feedback loop |
| Karniadakis (arXiv 2511.03179) | Paper | Knowledge-guided multi-agent |
| Siemens AEI (arXiv 2604.07784) | Paper | Agentic engineering intelligence |
| Corpus2Skill (arXiv 2604.14572) | Paper | Distilling knowledge into agent skills |
| build123d-mcp (pzfreo) | Open source | Interactive CAD through MCP |
| MecAgent | Commercial | Specs-to-CAD, enterprise focus |

---

## 11. The one-sentence summary

**You don't build a new AI. You build a knowledge base + contract format +
feedback loop + memory around the AI you already have. The AI reasons, the
tools judge, the memory learns.**

---

## 12. First proof: open item #5 (cut-height adjust)

| Stage | What we know |
|---|---|
| **Inspect** | Deck has 3.9 mm spare, 775 shaft is 17 mm, motor must not move up |
| **Specify** | 25-60 mm range, motor rise = 0, deck clearance >= 1.0 |
| **Build** | Candidate mechanisms: spacer sleeve, slotted bracket, cam pin |
| **Validate** | FreeCAD interference + clearance check |
| **Deliver** | TechDraw + BOM + git commit |

This is the test case. If the framework works here, it works for all 10 open
items.
