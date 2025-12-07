# Guide des Expérimentations

Ce guide détaille les étapes à suivre pour reproduire chaque expérimentation présentée dans le rapport et la soutenance.

## Cycle Expérimental Général

Pour chaque expérience, le cycle est le suivant :
1.  **Collecte** : Jouer au jeu pour remplir `dataset.csv`.
2.  **Entraînement** : Lancer le script Python pour entraîner le modèle.
3.  **Analyse** : Observer les courbes générées (`.png`) et tester le modèle en jeu.

---

## Expérience 1 : Régression (Échec)

**Objectif** : Apprendre à prédire la valeur exacte du stick (-1.0 à 1.0).

### Étape 1 : Collecte
1.  Lancer la scène Unity.
2.  Jouer manuellement pendant quelques minutes pour générer des données variées.
3.  Quitter le jeu (cela sauvegarde `dataset.csv`).

### Étape 2 : Entraînement
1.  Ouvrir `generate_plots.py`.
2.  Décommenter la section **"Experiment 3: Regression (MLP)"** (lignes ~233-245).
3.  S'assurer que `mode='regression'` est bien passé à `train_model`.
4.  Exécuter : `python generate_plots.py`.

### Étape 3 : Analyse
1.  Ouvrir l'image générée : `mlp_regression_learning_curve.png`.
2.  **Constat** : La courbe d'erreur (MSE) ne descend pas ou très peu. Elle stagne.
3.  **Conclusion** : L'approche régression échoue à cause du bruit dans les données humaines.

---

## Expérience 2 : Classification (Succès)

**Objectif** : Apprendre à prédire l'intention (Gauche / Droite / Rien).

### Étape 1 : Collecte
*   (On peut réutiliser le même `dataset.csv` que pour l'expérience 1).

### Étape 2 : Entraînement
1.  Ouvrir `generate_plots.py`.
2.  Décommenter la section **"Experiment 4: Classification (MLP)"** (lignes ~247-261).
3.  S'assurer que `mode='classification'` est bien passé à `train_model`.
4.  Exécuter : `python generate_plots.py`.
    *   *Note* : Cela va écraser le fichier `Assets/model.txt` avec le nouveau cerveau entraîné.

### Étape 3 : Analyse
1.  Ouvrir l'image générée : `mlp_classification_learning_curve.png`.
2.  **Constat** : La courbe d'erreur descend rapidement.
3.  **Test en Jeu** : Lancer Unity. Cocher `Use AI` sur le `PaddleController`. Observer que l'agent joue correctement (bien qu'il puisse "trembler" un peu).

---

## Expérience 3 : Agent Invincible (Expert Iteration)

**Objectif** : Apprendre d'un robot parfait pour dépasser le niveau humain.

### Étape 1 : Collecte (Automatique)
1.  Dans Unity, activer le script `AutoPilot` sur le Paddle.
2.  Laisser le jeu tourner en accéléré (TimeScale) pendant longtemps.
3.  Cela génère un fichier `perfect_dataset.csv`.

### Étape 2 : Entraînement
1.  Dans `generate_plots.py`, modifier la ligne de chargement pour utiliser `perfect_dataset.csv`.
2.  Lancer l'entraînement en mode **Classification**.

### Étape 3 : Analyse
1.  **Constat** : La précision atteint des sommets (> 87% voire 99%).
2.  **Test en Jeu** : L'agent ne rate plus aucune balle.
