from src.ai.sla_predictor import predict_sla

print("NORMAL DAY TEST")
print(predict_sla("2026-06-15", "STANDARD", 1200000, 800000, "Low", 4))

print("SNKRS DROP TEST")
print(predict_sla("2026-06-15", "SNKRS_DROP", 8500000, 900000, "High", 4))
