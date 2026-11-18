# v4 Four-Core Coverage Matrix
core01_conversational: all conv cats — bn/banglish still thin vs target.
core02_reasoning_decision: reasoning 23 + decision 19 + logic 17 +
  instruction 14 + multi_turn 63 + self_correction 11 — improved but thin.
core03_math_logic: math 391 (downsampled from 1274) — still largest,
  verified procedural.
core04_knowledge_uncertainty: knowledge 104 + uncertainty 44 + refusal 4
  + self_correction 11.
All cores share ONE Transformer impl — independent weights only.
