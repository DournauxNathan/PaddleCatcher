
import os

file_path = 'experiment.ipynb'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace incorrect variable names
new_content = content.replace('y_train_class', 'y_train_cls')
new_content = new_content.replace('y_test_class', 'y_test_cls')

if content != new_content:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Fixed variable names in experiment.ipynb")
else:
    print("No changes made. Variables might be already correct or not found.")
