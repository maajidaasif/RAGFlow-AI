import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from comparison.paper_comparison import PaperComparisonEngine


comparison_engine = PaperComparisonEngine()

result = comparison_engine.compare_papers()


if result["success"]:
    print("\n========== PAPER COMPARISON RESULT ==========\n")
    print(result["comparison"])
else:
    print(result["message"])