
import json

with open('experiment.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Print source of cells that likely contain train_model or experiment calls
# Based on previous output, it seems to be around cell 4 and later
for i in range(4, len(nb['cells'])):
    cell = nb['cells'][i]
    if cell['cell_type'] == 'code':
        print(f"Cell {i} Source:")
        print(''.join(cell['source']))
        print("-" * 20)
