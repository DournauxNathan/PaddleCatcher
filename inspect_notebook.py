
import json

with open('experiment.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

for i, cell in enumerate(nb['cells']):
    print(f"Cell {i} Type: {cell['cell_type']}")
    print("Source snippet:", ''.join(cell['source'])[:100])
    print("-" * 20)
