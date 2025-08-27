---
title: "SFT (Supervised Fine‑Tuning) for LLMs"
date: 2025-08-27
summary: "From data curation to training loops, checkpoints, and evaluation; and how SFT differs from RLHF/DPO."
tags: [sft, fine-tuning, alignment, rlhf, dpo]
---

# Supervised Fine‑Tuning (SFT)

SFT adapts a base LLM to follow instructions by training on **input → desired output** pairs (human‑written or distilled). It’s often the first step before preference‑based tuning (RLHF) or direct preference optimization (DPO).

## Pipeline (diagram)

```mermaid
flowchart LR
    D[Task & Policy Spec] --> C[Curate Dataset]
    C --> Q[Quality & Safety Filters]
    Q --> T[Tokenize & Pack]
    T --> S[Train: LoRA / Full / QLoRA]
    S --> E[Evaluate: automatic + human]
    E --> P[Promote / Rollback]
```

## Key Decisions

- **Data**: High‑quality demos; cover edge cases; remove contamination/leaks.
- **Objective**: Cross‑entropy on targets; supervise only on **answer spans** for conversational data.
- **Parameter‑Efficient Tuning**: LoRA/QLoRA for cost and memory savings.
- **Validation**: Hold‑out sets; measure helpfulness, harmlessness, and adherence to specs.
- **Overfitting**: Watch for verbatim training leakage and narrow style collapse.

## SFT vs RLHF vs DPO

- **SFT**: Learn to imitate demonstrations.
- **RLHF**: Learn a **preference model** from human rankings, then optimize a policy against it (e.g., PPO).
- **DPO**: Directly optimize the policy from ranked pairs without a separate reward model.

## Practical Tips

- Start with SFT to set behavior; add RLHF/DPO only if needed.
- Prefer PEFT (LoRA/QLoRA) unless you must update all weights.
- Evaluate with task‑specific checklists and adversarial prompts.

## Further Reading
- Ouyang et al., 2022: InstructGPT (SFT + RLHF).
