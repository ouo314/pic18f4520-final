import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier

digits = load_digits()
X = digits.data.astype(np.float32) / 16.0
y = digits.target

X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
mlp = MLPClassifier(hidden_layer_sizes=(16,), max_iter=1000, random_state=42, alpha=1e-3)
mlp.fit(X_tr, y_tr)

W1, b1 = mlp.coefs_[0].T, mlp.intercepts_[0]
W2, b2 = mlp.coefs_[1].T, mlp.intercepts_[1]
s1 = max(np.max(np.abs(W1)), 1e-8) / 127.0
s2 = max(np.max(np.abs(W2)), 1e-8) / 127.0

W1_q = np.clip(np.round(W1 / s1), -127, 127).astype(np.int8)
b1_q = np.clip(np.round(b1 / s1), -127, 127).astype(np.int8)
W2_q = np.clip(np.round(W2 / s2), -127, 127).astype(np.int8)

X_te_q = np.round(X_te * 16.0).astype(np.int32)
z1 = X_te_q @ W1_q.T.astype(np.int32) + (b1_q.astype(np.int32) * 16)
a1 = np.maximum(0, z1)
shift = max(0, int(np.ceil(np.log2(max(1, np.max(a1)) / 127.0))))
a1_q = np.clip(a1 >> shift, 0, 127).astype(np.int8)

b2_eff = np.round(b2 / s2 * (16.0 / (s1 * (2 ** shift)))).astype(np.int32)
z2 = a1_q.astype(np.int32) @ W2_q.T.astype(np.int32) + b2_eff
acc = np.mean(np.argmax(z2, axis=1) == y_te) * 100.0
print(f"FP32 Acc: {mlp.score(X_te, y_te)*100:.2f}% | INT8 Acc: {acc:.2f}% | L1_SHIFT={shift}")
