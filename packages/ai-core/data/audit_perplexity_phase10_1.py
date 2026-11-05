"""
Phase 10.1 - Loss and Perplexity Verification

Independently verifies the perplexity calculation from test loss.
"""

import math

print("="*60)
print("Phase 10.1 - Loss and Perplexity Verification")
print("="*60)

# Reported values from evaluation results
reported_test_loss = 6.162087641821968
reported_perplexity = 474.417455460409

# Calculate perplexity from test loss
calculated_perplexity = math.exp(reported_test_loss)

print(f"\nReported test loss: {reported_test_loss}")
print(f"Reported perplexity: {reported_perplexity}")
print(f"Calculated perplexity: {calculated_perplexity}")
print(f"Match: {abs(calculated_perplexity - reported_perplexity) < 0.01}")

# Mathematical verification
print(f"\nMathematical relationship:")
print(f"  Perplexity = exp(test_loss)")
print(f"  exp({reported_test_loss}) = {calculated_perplexity}")

# Check if the value is reasonable
print(f"\nReasonableness check:")
print(f"  Perplexity < 1000: {calculated_perplexity < 1000}")
print(f"  Perplexity > 1: {calculated_perplexity > 1}")
print(f"  Perplexity is finite: {math.isfinite(calculated_perplexity)}")

# Interpretation
print(f"\nInterpretation:")
if calculated_perplexity < 10:
    print("  Excellent model")
elif calculated_perplexity < 100:
    print("  Good model")
elif calculated_perplexity < 500:
    print("  Fair model (current state)")
elif calculated_perplexity < 1000:
    print("  Poor model")
else:
    print("  Very poor model")

print("\n" + "="*60)
print("PERPLEXITY VERIFICATION COMPLETE")
print("="*60)
