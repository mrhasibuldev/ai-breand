# v3 Four-Core Mapping (manifests/ generated)
core01_conversational: greeting/identity/thanks/farewell/smalltalk/qa/
  everyday_help/social/multi_turn/mixed_lang/clarification/uncertainty
core02_reasoning_decision: reasoning/decision/logic/instruction/
  multi_turn/self_correction/clarification
core03_math_logic: math/logic/reasoning (1089+52+13 records — best covered)
core04_knowledge_uncertainty: knowledge/qa/uncertainty/refusal/self_correction
NOTE: all cores share ONE Transformer impl (core01/transformer.py) —
independent configs/weights, NOT independent architectures.
