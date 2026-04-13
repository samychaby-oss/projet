import pandas as pd
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import confusion_matrix, classification_report

# --- ÉTAPE 1 : DATA ---
df = pd.read_csv('ghostbot_1k_balanced.csv')
X_train, X_test, y_train, y_test = train_test_split(df['text'], df['label'], test_size=0.2)

# --- ÉTAPE 2 : DÉFINITION DES 4 MODÈLES & GRILLES ---
models = {
    'Logistic': (LogisticRegression(), {'clf__C': [1, 10]}),
    'RandomForest': (RandomForestClassifier(), {'clf__n_estimators': [50, 100]}),
    'SVM': (SVC(probability=True), {'clf__C': [1, 10], 'clf__kernel': ['linear', 'rbf']}),
    'NaiveBayes': (MultinomialNB(), {'clf__alpha': [0.1, 1]})
}

best_overall_score = 0
best_model_bundle = None

for name, (algo, params) in models.items():
    print(f"--- 🔍 Optimisation de {name} ---")
    pipe = Pipeline([('tfidf', TfidfVectorizer(ngram_range=(1,3))), ('clf', algo)])
    grid = GridSearchCV(pipe, params, cv=5)
    grid.fit(X_train, y_train)
    
    score = grid.best_score_
    if score > best_overall_score:
        best_overall_score = score
        best_model_bundle = grid.best_estimator_

# --- ÉTAPE 3 : MATRICE DE CONFUSION DU GAGNANT ---
y_pred = best_model_bundle.predict(X_test)
cm = confusion_matrix(y_test, y_pred)

print("\n📊 MATRICE DE CONFUSION DU MEILLEUR MODÈLE :")
print(cm)
print(classification_report(y_test, y_pred))

# --- ÉTAPE 4 : SAUVEGARDE ---
with open('models_bundle.pkl', 'wb') as f:
    pickle.dump(best_model_bundle, f)
print("💾 Champion sauvegardé !")