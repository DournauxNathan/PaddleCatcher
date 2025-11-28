import json
import os

notebook_path = 'experiment.ipynb'

# Define the new cells to append
new_cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 6. MLP Implementation and Experiments\n",
            "\n",
            "We will now extend our experimentation to a Multi-Layer Perceptron (MLP) to capture non-linear relationships."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Define FFI for MLP\n",
            "lib.mlp_new.argtypes = [ctypes.POINTER(ctypes.c_size_t), ctypes.c_size_t]\n",
            "lib.mlp_new.restype = ctypes.c_void_p\n",
            "\n",
            "lib.mlp_predict.argtypes = [\n",
            "    ctypes.c_void_p, \n",
            "    ctypes.POINTER(ctypes.c_float), ctypes.c_int, \n",
            "    ctypes.c_bool, \n",
            "    ctypes.POINTER(ctypes.c_float), ctypes.c_int\n",
            "]\n",
            "lib.mlp_predict.restype = None\n",
            "\n",
            "lib.mlp_train.argtypes = [\n",
            "    ctypes.c_void_p, \n",
            "    ctypes.POINTER(ctypes.c_float), ctypes.c_int, \n",
            "    ctypes.POINTER(ctypes.c_float), ctypes.c_int, \n",
            "    ctypes.c_bool, \n",
            "    ctypes.c_float\n",
            "]\n",
            "lib.mlp_train.restype = None\n",
            "\n",
            "lib.mlp_free.argtypes = [ctypes.c_void_p]\n",
            "lib.mlp_free.restype = None"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Update evaluate and train_model functions to support MLP\n",
            "def evaluate(model, X, y, is_classification, is_mlp=False):\n",
            "    total_error = 0.0\n",
            "    correct = 0\n",
            "    \n",
            "    for i in range(len(X)):\n",
            "        inputs = X[i]\n",
            "        target = y[i]\n",
            "        \n",
            "        c_inputs = inputs.ctypes.data_as(ctypes.POINTER(ctypes.c_float))\n",
            "        c_len = len(inputs)\n",
            "        \n",
            "        if is_mlp:\n",
            "            output = np.zeros(1, dtype=np.float32)\n",
            "            c_output = output.ctypes.data_as(ctypes.POINTER(ctypes.c_float))\n",
            "            lib.mlp_predict(model, c_inputs, c_len, is_classification, c_output, 1)\n",
            "            prediction = output[0]\n",
            "        else:\n",
            "            prediction = lib.perceptron_predict(model, c_inputs, c_len)\n",
            "        \n",
            "        if is_classification:\n",
            "            if (prediction > 0 and target > 0) or (prediction < 0 and target < 0):\n",
            "                correct += 1\n",
            "        else:\n",
            "            total_error += (target - prediction) ** 2\n",
            "            \n",
            "    if is_classification:\n",
            "        return 1.0 - (correct / len(X)) # Error rate\n",
            "    else:\n",
            "        return total_error / len(X) # MSE\n",
            "\n",
            "def train_model(X_train, y_train, X_test, y_test, mode='regression', epochs=100, alpha=0.01, use_mlp=False):\n",
            "    is_classification = (mode == 'classification')\n",
            "    input_size = X_train.shape[1]\n",
            "    \n",
            "    # Create Model\n",
            "    if use_mlp:\n",
            "        # Architecture: Input -> 8 -> 1\n",
            "        layers = np.array([input_size, 8, 1], dtype=np.uint64) # usize is 64-bit on 64-bit systems\n",
            "        c_layers = layers.ctypes.data_as(ctypes.POINTER(ctypes.c_size_t))\n",
            "        model = lib.mlp_new(c_layers, len(layers))\n",
            "    else:\n",
            "        model = lib.perceptron_new(input_size, alpha, is_classification)\n",
            "    \n",
            "    train_errors = []\n",
            "    test_errors = []\n",
            "    \n",
            "    for epoch in range(epochs):\n",
            "        # Train\n",
            "        for i in range(len(X_train)):\n",
            "            inputs = X_train[i]\n",
            "            target = y_train[i]\n",
            "            \n",
            "            c_inputs = inputs.ctypes.data_as(ctypes.POINTER(ctypes.c_float))\n",
            "            c_len = len(inputs)\n",
            "            \n",
            "            if use_mlp:\n",
            "                # MLP expects array of outputs\n",
            "                target_arr = np.array([target], dtype=np.float32)\n",
            "                c_target = target_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_float))\n",
            "                lib.mlp_train(model, c_inputs, c_len, c_target, 1, is_classification, alpha)\n",
            "            else:\n",
            "                lib.perceptron_train(model, c_inputs, c_len, target)\n",
            "            \n",
            "        # Evaluate Train\n",
            "        train_loss = evaluate(model, X_train, y_train, is_classification, is_mlp=use_mlp)\n",
            "        train_errors.append(train_loss)\n",
            "        \n",
            "        # Evaluate Test\n",
            "        test_loss = evaluate(model, X_test, y_test, is_classification, is_mlp=use_mlp)\n",
            "        test_errors.append(test_loss)\n",
            "        \n",
            "        if epoch % 10 == 0:\n",
            "            print(f\"Epoch {epoch}: Train={train_loss:.4f}, Test={test_loss:.4f}\")\n",
            "            \n",
            "    # Free memory\n",
            "    if use_mlp:\n",
            "        lib.mlp_free(model)\n",
            "    else:\n",
            "        lib.perceptron_free(model)\n",
            "    \n",
            "    return train_errors, test_errors"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 6.1 MLP Regression"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "print(\"Starting Regression Experiment (MLP)...\")\n",
            "train_err_mlp, test_err_mlp = train_model(X_train, y_train, X_test, y_test, mode='regression', epochs=100, alpha=0.001, use_mlp=True)\n",
            "\n",
            "plt.figure()\n",
            "plt.plot(train_err_mlp, label='Train MSE')\n",
            "plt.plot(test_err_mlp, label='Test MSE')\n",
            "plt.title('Regression Learning Curve (MLP)')\n",
            "plt.xlabel('Epochs')\n",
            "plt.ylabel('MSE')\n",
            "plt.legend()\n",
            "plt.savefig('mlp_regression_learning_curve.png')\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 6.2 MLP Classification"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "print(\"Starting Classification Experiment (MLP)...\")\n",
            "train_err_mlp_cls, test_err_mlp_cls = train_model(X_train, y_train_class, X_test, y_test_class, mode='classification', epochs=100, alpha=0.001, use_mlp=True)\n",
            "\n",
            "plt.figure()\n",
            "plt.plot(train_err_mlp_cls, label='Train Error Rate')\n",
            "plt.plot(test_err_mlp_cls, label='Test Error Rate')\n",
            "plt.title('Classification Learning Curve (MLP)')\n",
            "plt.xlabel('Epochs')\n",
            "plt.ylabel('Error Rate')\n",
            "plt.legend()\n",
            "plt.savefig('mlp_classification_learning_curve.png')\n",
            "plt.show()"
        ]
    }
]

# Read existing notebook
with open(notebook_path, 'r', encoding='utf-8') as f:
    notebook = json.load(f)

# Check if MLP cells are already present to avoid duplication
# We check if "MLP Implementation" is in any markdown cell source
mlp_present = False
for cell in notebook['cells']:
    if cell['cell_type'] == 'markdown':
        source_text = "".join(cell['source'])
        if "MLP Implementation" in source_text:
            mlp_present = True
            break

if not mlp_present:
    notebook['cells'].extend(new_cells)
    
    # Write back to file
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=4)
    print("Successfully appended MLP cells to notebook.")
else:
    print("MLP cells seem to be already present. Skipping append.")
