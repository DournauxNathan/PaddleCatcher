# Questions / Réponses pour la Soutenance

Ce document résume nos échanges techniques pour vous aider à répondre aux questions du jury.

---

## 1. Architecture et Rôle de la `lib.rs`

**Q : À quoi sert exactement le fichier `lib.rs` ?**
**R :** C'est le **cerveau** de l'IA. Il a 3 rôles clés :
1.  **Moteur Mathématique** : Il contient le code des réseaux de neurones (Perceptron, MLP) et les algorithmes d'apprentissage (rétropropagation).
2.  **Performance** : Écrit en **Rust** pour garantir une exécution ultra-rapide (indispensable pour les calculs matriciels à 50Hz).
3.  **Interopérabilité** : Compilé en DLL, il sert de pont commun. Le *même* code est utilisé par **Python** (pour l'entraînement) et par **Unity** (pour le jeu), garantissant une cohérence parfaite.

---

## 2. Flux de Données (Data Flow)

**Q : Comment les données circulent-elles entre Unity, Python et Rust ?**
**R :** Le processus se fait en 3 phases :
1.  **Collecte (Unity)** : Le jeu enregistre les positions (Paddle + Balles) dans un fichier `dataset.csv`.
2.  **Entraînement (Python + Rust)** : Python lit ce CSV et envoie les données à la DLL Rust. Rust entraîne le modèle et sauvegarde le "cerveau" dans `model.txt`.
3.  **Inférence (Unity + Rust)** : Au lancement du jeu, Unity charge `model.txt`. À chaque image, il envoie l'état du jeu à la DLL Rust qui renvoie instantanément l'action à effectuer.

---

## 3. Méthodologie : Choix des Entrées (Features)

**Q : Pourquoi ne pas utiliser la vitesse du paddle en entrée ?**
**R :** C'est une simplification volontaire (Rasoir d'Occam).
*   Dans notre moteur physique "arcade", le mouvement est **instantané** (pas d'inertie, pas d'accélération).
*   La position seule suffit donc à définir l'état complet. Si nous avions une physique réaliste (glissade), la vitesse aurait été indispensable.

**Q : Comment lire le fichier `dataset.csv` ?**
**R :** Le format est `PaddleX, ActionX, BallsData`.
*   L'entrée (Input) est composée de `PaddleX` ET `BallsData`.
*   La sortie (Target) est `ActionX` (au milieu).
*   L'IA doit apprendre à prédire `ActionX` à partir des deux autres.

---

## 4. Méthodologie : Régression vs Classification

**Q : Pourquoi avoir choisi la Classification plutôt que la Régression ?**
**R :**
*   **Régression** (Prédire une valeur continue, ex: 0.84) : Échec. Le comportement humain est trop "bruité" et inconstant pour qu'un modèle mathématique trouve une logique précise.
*   **Classification** (Prédire Gauche/Droite/Rien) : **Succès**. En discrétisant l'intention, on élimine le bruit. C'est plus robuste.

**Q : Pourquoi le paddle "tremble" (jittering) ?**
**R :** C'est un effet secondaire de la Classification.
*   Le modèle n'a que des commandes fortes ("Tout à gauche" ou "Tout à droite").
*   Pour rester immobile à une position précise, il est obligé d'osciller très vite autour de cette position (Gauche-Droite-Gauche-Droite...).

---

## 5. Choix du Modèle : Perceptron vs MLP

**Q : Pourquoi un modèle simple (Perceptron Linéaire) ne suffit pas ?**
**R :** Le Perceptron ne peut tracer qu'une ligne droite pour séparer les décisions.
*   Il échoue dans les cas complexes, par exemple devoir choisir entre deux balles (arbitrage).
*   Le **MLP** (Multi-Layer Perceptron), grâce à ses couches cachées et ses fonctions d'activation non-linéaires (`Tanh`), peut apprendre des règles conditionnelles complexes et gérer ces conflits.
