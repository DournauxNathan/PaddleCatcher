
import json

file_path = 'experiment.ipynb'

with open(file_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# 1. Create Hyperparameters Cell
hyperparams_source = [
    "# Hyperparameters\n",
    "EPOCHS = 100\n",
    "LEARNING_RATE = 0.001\n",
    "HIDDEN_NEURONS = 8"
]

hyperparams_cell = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": hyperparams_source
}

# Insert after "Load Rust Library" (Cell 2, index 2 -> insert at 3? No, Load Rust is index 3 in my previous count? Let's check)
# Cell 0: Markdown title
# Cell 1: Imports
# Cell 2: Markdown "Load Rust"
# Cell 3: Code "Load Rust"
# So insert after Cell 3.

insert_index = 4
nb['cells'].insert(insert_index, hyperparams_cell)

# 2. Update train_model definition (Find cell with "def train_model")
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = "".join(cell['source'])
        if "def train_model" in source:
            # Replace hardcoded 8 with HIDDEN_NEURONS
            new_source = []
            for line in cell['source']:
                if "layers = np.array([input_size, 8, 1]" in line:
                    new_line = line.replace("8", "HIDDEN_NEURONS")
                    new_source.append(new_line)
                else:
                    new_source.append(line)
            cell['source'] = new_source

# 3. Update train_model calls
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = "".join(cell['source'])
        if "train_model(" in source:
            new_source = []
            for line in cell['source']:
                if "train_model(" in line:
                    # Replace epochs=100 with epochs=EPOCHS
                    line = line.replace("epochs=100", "epochs=EPOCHS")
                    # Replace alpha=0.001 or alpha=0.01 with alpha=LEARNING_RATE
                    line = line.replace("alpha=0.001", "alpha=LEARNING_RATE")
                    line = line.replace("alpha=0.01", "alpha=LEARNING_RATE")
                    new_source.append(line)
                else:
                    new_source.append(line)
            cell['source'] = new_source

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=4)

print("Hyperparameters extracted and notebook updated.")
