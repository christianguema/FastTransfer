#Script pour remplire automatiquement le fichier requirements.txt a chaque installation
import subprocess
import sys

def update_requirements(filename="requirements.txt"):
    try:
        # Exécute la commande pip freeze pour obtenir les versions exactes
        result = subprocess.run([sys.executable, "-m", "pip", "freeze"], 
                               capture_output=True, text=True, check=True)
        
        # Filtre pour ne pas inclure le paquet du script lui-même ou des paquets éditables
        packages = result.stdout
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(packages)
            
        print(f"✅ Le fichier {filename} a été mis à jour avec succès.")
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour : {e}")

if __name__ == "__main__":
    update_requirements()