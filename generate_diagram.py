import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_box(ax, x, y, width, height, text, color='#e0e0e0', edge_color='black'):
    rect = patches.Rectangle((x, y), width, height, linewidth=1, edgecolor=edge_color, facecolor=color)
    ax.add_patch(rect)
    ax.text(x + width/2, y + height/2, text, ha='center', va='center', fontsize=9, wrap=True)

def draw_arrow(ax, x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", lw=1.5))

def create_diagram():
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Phase 1: Collecte
    ax.text(2, 9.5, "Phase 1: Collecte (Unity)", ha='center', fontsize=12, fontweight='bold')
    draw_box(ax, 1, 8, 2, 1, "Joueur Humain", color='#d4f1f4')
    draw_arrow(ax, 2, 8, 2, 7.5)
    draw_box(ax, 1, 6.5, 2, 1, "Jeu Unity", color='#d4f1f4')
    draw_arrow(ax, 2, 6.5, 2, 6)
    draw_box(ax, 1, 5, 2, 1, "DataRecorder.cs", color='#d4f1f4')
    draw_arrow(ax, 2, 5, 2, 4.5)
    draw_box(ax, 1, 3.5, 2, 1, "dataset.csv", color='#f9f9f9')

    # Phase 2: Entrainement
    ax.text(6, 9.5, "Phase 2: Entraînement (Python/Rust)", ha='center', fontsize=12, fontweight='bold')
    draw_arrow(ax, 3, 4, 5, 4) # CSV to Python
    draw_box(ax, 5, 3.5, 2, 1, "Python / Jupyter", color='#d4e157')
    draw_arrow(ax, 6, 4.5, 6, 5)
    draw_box(ax, 5, 5, 2, 1, "Rust Lib (Train)", color='#ffcc80')
    draw_arrow(ax, 6, 6, 6, 6.5)
    draw_box(ax, 5, 6.5, 2, 1, "model.txt", color='#f9f9f9')

    # Phase 3: Inférence
    ax.text(10, 9.5, "Phase 3: Jeu (Unity/Rust)", ha='center', fontsize=12, fontweight='bold')
    draw_arrow(ax, 7, 7, 9, 7) # Model to Controller
    draw_box(ax, 9, 6.5, 2, 1, "PaddleController.cs", color='#d4f1f4')
    draw_arrow(ax, 10, 6.5, 10, 6)
    draw_box(ax, 9, 5, 2, 1, "Rust Lib (Predict)", color='#ffcc80')
    draw_arrow(ax, 10, 5, 10, 4.5)
    draw_box(ax, 9, 3.5, 2, 1, "Jeu Unity\n(Action)", color='#d4f1f4')
    
    # Feedback loop in game
    draw_arrow(ax, 9, 4, 9, 6.5) # Game back to controller (state)
    ax.text(8.8, 5.25, "État", ha='right', fontsize=8)

    plt.tight_layout()
    plt.savefig('flux_donnees.png', dpi=300)
    print("Diagram saved to flux_donnees.png")

if __name__ == "__main__":
    create_diagram()
