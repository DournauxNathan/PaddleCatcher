import ctypes
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Setup Plotting
plt.style.use('seaborn-v0_8')
plt.rcParams['figure.figsize'] = (10, 6)

# 1. Load Rust Library (FFI)
dll_path = os.path.join("RustLib", "target", "release", "rust_machine_learning_library.dll")

if not os.path.exists(dll_path):
    print(f"Warning: {dll_path} not found.")

lib = ctypes.CDLL(dll_path)

# Define Argument and Return Types
lib.perceptron_new.argtypes = [ctypes.c_int, ctypes.c_float, ctypes.c_bool]
lib.perceptron_new.restype = ctypes.c_void_p

lib.perceptron_predict.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_float), ctypes.c_int]
lib.perceptron_predict.restype = ctypes.c_float

lib.perceptron_train.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_float), ctypes.c_int, ctypes.c_float]
lib.perceptron_train.restype = None

lib.perceptron_free.argtypes = [ctypes.c_void_p]
lib.perceptron_free.restype = None

# MLP FFI
lib.mlp_new.argtypes = [ctypes.POINTER(ctypes.c_size_t), ctypes.c_size_t]
lib.mlp_new.restype = ctypes.c_void_p

lib.mlp_predict.argtypes = [
    ctypes.c_void_p, 
    ctypes.POINTER(ctypes.c_float), ctypes.c_int, 
    ctypes.c_bool, 
    ctypes.POINTER(ctypes.c_float), ctypes.c_int
]
lib.mlp_predict.restype = None

lib.mlp_train.argtypes = [
    ctypes.c_void_p, 
    ctypes.POINTER(ctypes.c_float), ctypes.c_int, 
    ctypes.POINTER(ctypes.c_float), ctypes.c_int, 
    ctypes.c_bool, 
    ctypes.c_float
]
lib.mlp_train.restype = None

lib.mlp_free.argtypes = [ctypes.c_void_p]
lib.mlp_free.restype = None

lib.mlp_save.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
lib.mlp_save.restype = ctypes.c_bool

# 2. Load and Preprocess Data
def load_dataset(path, max_balls=3):
    df = pd.read_csv(path)
    
    X = []
    y = []
    
    for _, row in df.iterrows():
        paddle_x = row['PaddleX']
        action_x = row['ActionX']
        balls_str = row['BallsData']
        
        # Parse balls
        balls = []
        if isinstance(balls_str, str) and balls_str.strip():
            for ball_part in balls_str.split('|'):
                if ':' in ball_part:
                    bx, by = map(float, ball_part.split(':'))
                    balls.append((bx, by))
        
        # Sort balls by Y (lowest first - closest to paddle level?)
        balls.sort(key=lambda b: b[1])
        
        # Construct Input Vector
        features = [paddle_x]
        for i in range(max_balls):
            if i < len(balls):
                features.append(balls[i][0])
                features.append(balls[i][1])
            else:
                features.append(0.0) # Padding X
                features.append(10.0) # Padding Y (far away)
        
        X.append(features)
        y.append(action_x)
        
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)
    
# Use perfect dataset if available, otherwise fallback (or fail)
dataset_path = 'dataset.csv'
if not os.path.exists(dataset_path):
    print(f"Warning: {dataset_path} not found. Using dataset.csv")
    dataset_path = 'dataset.csv'

X, y = load_dataset(dataset_path)
print(f"Dataset Loaded from {dataset_path}. Shape: X={X.shape}, y={y.shape}")

# Split Train/Test
split_idx = int(len(X) * 0.8)
X_train, X_test = X[:split_idx], X[split_idx:]
y_train, y_test = y[:split_idx], y[split_idx:]

print(f"Train set: {len(X_train)}, Test set: {len(X_test)}")

# 3. Training Loop
def evaluate(model, X, y, is_classification, is_mlp=False):
    total_error = 0.0
    correct = 0
    
    for i in range(len(X)):
        inputs = X[i]
        target = y[i]
        
        c_inputs = inputs.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        c_len = len(inputs)
        
        if is_mlp:
            output = np.zeros(1, dtype=np.float32)
            c_output = output.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
            lib.mlp_predict(model, c_inputs, c_len, is_classification, c_output, 1)
            prediction = output[0]
        else:
            prediction = lib.perceptron_predict(model, c_inputs, c_len)
        
        if is_classification:
            if (prediction > 0 and target > 0) or (prediction < 0 and target < 0):
                correct += 1
        else:
            total_error += (target - prediction) ** 2
            
    if is_classification:
        return 1.0 - (correct / len(X)) # Error rate
    else:
        return total_error / len(X) # MSE

def train_model(X_train, y_train, X_test, y_test, mode='regression', epochs=100, alpha=0.01, use_mlp=False, save_path=None):
    is_classification = (mode == 'classification')
    input_size = X_train.shape[1]
    
    # Create Model
    if use_mlp:
        # Architecture: Input -> 8 -> 1
        layers = np.array([input_size, 4, 1], dtype=np.uint64)
        c_layers = layers.ctypes.data_as(ctypes.POINTER(ctypes.c_size_t))
        model = lib.mlp_new(c_layers, len(layers))
    else:
        model = lib.perceptron_new(input_size, alpha, is_classification)
    
    train_errors = []
    test_errors = []
    
    for epoch in range(epochs):
        # Train
        for i in range(len(X_train)):
            inputs = X_train[i]
            target = y_train[i]
            
            c_inputs = inputs.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
            c_len = len(inputs)
            
            if use_mlp:
                # MLP expects array of outputs
                target_arr = np.array([target], dtype=np.float32)
                c_target = target_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
                lib.mlp_train(model, c_inputs, c_len, c_target, 1, is_classification, alpha)
            else:
                lib.perceptron_train(model, c_inputs, c_len, target)
            
        # Evaluate Train
        train_loss = evaluate(model, X_train, y_train, is_classification, is_mlp=use_mlp)
        train_errors.append(train_loss)
        
        # Evaluate Test
        test_loss = evaluate(model, X_test, y_test, is_classification, is_mlp=use_mlp)
        test_errors.append(test_loss)
        
        if epoch % 100 == 0:
            print(f"Epoch {epoch}: Train={train_loss:.4f}, Test={test_loss:.4f}")
            
    # Free memory
    if use_mlp:
        if save_path:
            print(f"Saving model to {save_path}...")
            c_path = save_path.encode('utf-8')
            lib.mlp_save(model, c_path)
            
        lib.mlp_free(model)
    else:
        lib.perceptron_free(model)
    
    return train_errors, test_errors

# 4. Experiment 1: Regression (Perceptron)
# print("Starting Regression Experiment (Perceptron)...")
# train_err_reg, test_err_reg = train_model(X_train, y_train, X_test, y_test, mode='regression', epochs=500, alpha=0.001)

# plt.figure()
# plt.plot(train_err_reg, label='Train MSE')
# plt.plot(test_err_reg, label='Test MSE')
# plt.title('Regression Learning Curve (Perceptron)')
# plt.xlabel('Epochs')
# plt.ylabel('MSE')
# plt.legend()
# plt.savefig('regression_learning_curve.png')
# print("Saved regression_learning_curve.png")

# 5. Experiment 2: Classification (Perceptron)
# print("Starting Classification Experiment (Perceptron)...")
# Prepare Classification Targets
y_train_class = np.where(y_train > 0, 1.0, -1.0).astype(np.float32)
y_test_class = np.where(y_test > 0, 1.0, -1.0).astype(np.float32)

# train_err_cls, test_err_cls = train_model(X_train, y_train_class, X_test, y_test_class, mode='classification', epochs=500, alpha=0.001)

# plt.figure()
# plt.plot(train_err_cls, label='Train Error Rate')
# plt.plot(test_err_cls, label='Test Error Rate')
# plt.title('Classification Learning Curve (Perceptron)')
# plt.xlabel('Epochs')
# plt.ylabel('Error Rate')
# plt.legend()
# plt.savefig('classification_learning_curve.png')
# print("Saved classification_learning_curve.png")

# 6. Experiment 3: Regression (MLP)
# print("Starting Regression Experiment (MLP)...")
# train_err_mlp, test_err_mlp = train_model(X_train, y_train, X_test, y_test, mode='regression', epochs=1000, alpha=0.001, use_mlp=True)

# plt.figure()
# plt.plot(train_err_mlp, label='Train MSE')
# plt.plot(test_err_mlp, label='Test MSE')
# plt.title('Regression Learning Curve (MLP)')
# plt.xlabel('Epochs')
# plt.ylabel('MSE')
# plt.legend()
# plt.savefig('mlp_regression_learning_curve.png')
# print("Saved mlp_regression_learning_curve.png")

# 7. Experiment 4: Classification (MLP)
print("Starting Classification Experiment (MLP)...")
# For expert bot, we might want to save to a different model file to avoid overwriting the human one immediately?
# Or just overwrite it as "model.txt" is what the game loads.
train_err_mlp_cls, test_err_mlp_cls = train_model(X_train, y_train_class, X_test, y_test_class, mode='classification', epochs=1000, alpha=0.001, use_mlp=True, save_path="Assets/model.txt")

plt.figure()
plt.plot(train_err_mlp_cls, label='Train Error Rate')
plt.plot(test_err_mlp_cls, label='Test Error Rate')
plt.title('Classification Learning Curve (MLP)')
plt.xlabel('Epochs')
plt.ylabel('Error Rate')
plt.legend()
plt.savefig('mlp_classification_learning_curve.png')
print("Saved mlp_classification_learning_curve.png")
