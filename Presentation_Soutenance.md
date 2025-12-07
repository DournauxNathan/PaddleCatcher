# Squelette de Présentation - Soutenance Finale PaddleCatcher

## Slide 1 : Titre
**Titre** : Développement d'un Agent Artificiel par Apprentissage Supervisé
**Sous-titre** : Projet PaddleCatcher
**Présenté par** : [Votre Nom]
**Date** : [Date de la soutenance]

---

## Slide 2 : Sommaire
1.  **Contexte et Définition du Problème**
    *   *Vers une IA qui imite l'humain*
2.  **Architecture Technique**
    *   *L'alliance de la performance et de la flexibilité*
3.  **Méthodologie**
    *   *De la capture de données à la prédiction*
4.  **Conclusion**
    *   *Résultats et futures améliorations*

---

## Slide 3 : 1. Contexte et Définition du Problème
**Sous-titre** : *Vers une IA qui imite l'humain*

*   **Objectif** : Créer un agent IA capable d'imiter un joueur humain sur *PaddleCatcher*.
*   **Le Jeu** : Intercepter des balles tombantes avec un paddle (mouvement horizontal).
*   **Problème (Apprentissage Supervisé)** :
    *   **Entrées ($X$)** : État du jeu (Position Paddle + Positions Balles).
    *   **Sortie ($Y$)** : Action humaine (Gauche / Droite / Rien).
*   **But** : Apprendre la fonction de décision $f(X) \approx Y_{humain}$.

---

## Slide 4 : 2. Architecture Technique
**Sous-titre** : *L'alliance de la performance et de la flexibilité*

*   **Approche Hybride** pour la performance et la flexibilité :
    *   **Unity (C#)** : Simulation du jeu, Interface, Collecte de données (50Hz).
    *   **Rust (`RustLib`)** : Cœur de l'IA (Réseaux de neurones MLP), calcul haute performance.
    *   **Python (Jupyter)** : Orchestration des expériences, analyse des données.
*   **Flux de données** :
    *   Unity $\rightarrow$ CSV (Dataset).
    *   Python $\rightarrow$ Rust DLL (Entraînement).
    *   Unity $\leftrightarrow$ Rust DLL (Inférence temps réel).

---

## Slide 5 : 3. Expérimentations
**Sous-titre** : *Une démarche scientifique itérative*

*   **Le Cycle Expérimental (3 étapes)** :
    1.  **Collecte** : Enregistrement des parties (Humain ou Bot).
    2.  **Entraînement** : Apprentissage du réseau (Python/Rust).
    3.  **Analyse** : Validation via les courbes d'erreur.

*   **Expérience 1 : Régression (Échec)**
    *   *Hypothèse* : Prédire la valeur exacte du stick.
    *   *Résultat* : L'erreur ne descend pas.
    *   *Cause* : Jouer au **Clavier** donne des valeurs discrètes (-1, 0, 1) incompatibles avec une régression continue (qui cherche une courbe lisse). Le modèle est perdu.

*   **Expérience 2 : Classification (Succès)**
    *   *Hypothèse* : Prédire l'intention (Gauche / Droite).
    *   *Résultat* : Précision > 84%. Le modèle converge rapidement.

    <!-- TODO POUR PLUS TARD : Insérer ici les graphiques comparatifs -->
    <!-- Pour générer ces graphiques : -->
    <!-- 1. Ouvrir le fichier `generate_plots.py` -->
    <!-- 2. Décommenter les sections "Experiment 3: Regression (MLP)" et "Experiment 4: Classification (MLP)" -->
    <!-- 3. Exécuter la commande : `python generate_plots.py` -->
    <!-- 4. Insérer les images `mlp_regression_learning_curve.png` et `mlp_classification_learning_curve.png` ici. -->

---

## Slide 6 : 4. Conclusion
**Sous-titre** : *Ce que nous avons appris*

*   **Bilan Technique** :
    *   L'architecture hybride **Unity (C#) + Rust** est performante et fonctionnelle.
    *   Le **MLP (8 neurones)** est l'architecture optimale pour ce problème.

*   **Leçon Principale : "Garbage In, Garbage Out"** :
    *   La qualité de l'IA dépend directement de la qualité des données.
    *   Notre dataset humain (court et biaisé) limite la performance de l'IA (biais vers la gauche).
    *   L'IA imite parfaitement les imperfections du joueur.

*   **Perspectives** :
    *   **Data Augmentation** : Doubler le dataset par symétrie (miroir) pour éliminer le biais "Gauche" et le manque de données.
    *   **Enrichissement des Entrées** : Ajouter la vitesse du paddle et des balles pour permettre à l'IA d'anticiper les trajectoires (physique).
    *   **Analyse Critique (Quantité vs Qualité)** : Bien que le volume de données soit suffisant (94x plus d'exemples que de paramètres), c'est la distribution inégale des actions (biais humain) qui limite la performance, nécessitant un rééquilibrage statistique.

---

## Slide 7 : Questions / Réponses
*   Merci de votre attention.
