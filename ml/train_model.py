import pandas as pd, numpy as np, json, pickle, warnings
warnings.filterwarnings("ignore")
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier

FEATURES = ["Temp", "Humidity", "Cloud Cover", "ANNUAL", "Jun-Sep"]
TARGET = "flood"

df = pd.read_excel("/mnt/user-data/uploads/flood_dataset.xlsx")
X = df[FEATURES]
y = df[TARGET]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

pos_weight = (y_train == 0).sum() / max((y_train == 1).sum(), 1)

model_defs = {
    "Decision Tree": DecisionTreeClassifier(random_state=42, max_depth=5, class_weight="balanced"),
    "Random Forest": RandomForestClassifier(random_state=42, n_estimators=200, max_depth=6, class_weight="balanced"),
    "KNN": Pipeline([("scale", StandardScaler()), ("knn", KNeighborsClassifier(n_neighbors=5))]),
    "XGBoost": XGBClassifier(random_state=42, n_estimators=150, max_depth=4, eval_metric="logloss", scale_pos_weight=pos_weight),
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
results = {}
fitted = {}
for name, model in model_defs.items():
    cv_scores = cross_val_score(model, X, y, cv=cv, scoring="accuracy")
    model.fit(X_train, y_train)
    test_acc = accuracy_score(y_test, model.predict(X_test))
    results[name] = {"cv_mean": round(cv_scores.mean() * 100, 2), "test_acc": round(test_acc * 100, 2)}
    fitted[name] = model
    print(f"{name}: cv={results[name]['cv_mean']}%  holdout={results[name]['test_acc']}%")

best_name = max(results, key=lambda n: results[n]["cv_mean"])
print("Best (by CV):", best_name)

# refit best pipeline on ALL data for deployment (tiny dataset -> use every row)
best_final = model_defs[best_name]
best_final.fit(X, y)

with open("/home/claude/floodapp/ml/best_model.pkl", "wb") as f:
    pickle.dump({"model": best_final, "features": FEATURES, "name": best_name}, f)

type_map = {"Decision Tree": "Decision Tree", "Random Forest": "Random Forest", "KNN": "K-Nearest Neighbours", "XGBoost": "XGBoost"}
meta = []
for name, r in results.items():
    meta.append({
        "ModelName": f"FloodPredictor-{name.replace(' ','')}",
        "AlgorithmType": type_map[name],
        "Accuracy": r["test_acc"],
        "CV_Accuracy": r["cv_mean"],
        "ModelFile": "best_model.pkl" if name == best_name else f"{name.lower().replace(' ','_')}.pkl",
        "IsActive": name == best_name
    })

with open("/home/claude/floodapp/ml/model_meta.json", "w") as f:
    json.dump(meta, f, indent=2)

print(json.dumps(meta, indent=2))

for name, model in fitted.items():
    fname = "best_model.pkl" if name == best_name else f"{name.lower().replace(' ','_')}.pkl"
    with open(f"/home/claude/floodapp/ml/{fname}", "wb") as f:
        pickle.dump({"model": model, "features": FEATURES, "name": name}, f)
print("saved all model files")
