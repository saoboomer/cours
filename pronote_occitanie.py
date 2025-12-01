"""
Script de connexion PRONOTE via EduConnect Occitanie
Utilise une approche directe avec le portail ARENA
"""

import pronotepy
from pronotepy.ent import monlyceeconnecte_occitanie
from getpass import getpass
import webbrowser
import time

print("🔐 Connexion PRONOTE - Académie de Montpellier (Occitanie)")
print("=" * 60 + "\n")

# Configuration
PRONOTE_URL = "https://0110012d.index-education.net/pronote/eleve.html"

# Demander les identifiants
print("Veuillez entrer vos identifiants EduConnect :")
username = input("Identifiant: ").strip()
password = getpass("Mot de passe: ").strip()

print("\n🔄 Tentative de connexion en cours...")

try:
    # Méthode spécifique pour l'Occitanie
    client = pronotepy.Client(
        PRONOTE_URL,
        username=username,
        password=password,
        ent=monlyceeconnecte_occitanie,
        # Paramètres supplémentaires pour le cache et la stabilité
        use_cache=True,
        timeout=30
    )
    
    if client.logged_in:
        print("\n✅ Connexion réussie !")
        print("\n📋 Informations de l'élève :")
        print(f"   👤 Nom: {client.info.name}")
        print(f"   🏫 Établissement: {client.info.establishment}")
        print(f"   📅 Période actuelle: {client.current_period.name if client.current_period else 'Non disponible'}")
        
        # Afficher quelques notes
        if client.current_period and hasattr(client.current_period, 'grades'):
            print("\n📊 Dernières notes :")
            for grade in client.current_period.grades[:5]:
                print(f"   - {grade.subject.name}: {grade.grade}/{grade.out_of}")
        
        # Ouvrir le navigateur pour vérifier la connexion
        if input("\n🌐 Ouvrir PRONOTE dans le navigateur ? (o/n): ").lower() == 'o':
            webbrowser.open(PRONOTE_URL)
            
    else:
        print("\n❌ Échec de la connexion. Vérifiez vos identifiants.")
        print("   Essayez d'abord de vous connecter via le navigateur :")
        print("   https://educonnect.education.gouv.fr")

except Exception as e:
    print(f"\n❌ Une erreur est survenue : {str(e)}")
    print("\nConseils de dépannage :")
    print("1. Vérifiez votre connexion Internet")
    print("2. Essayez d'abord de vous connecter via le navigateur")
    print("3. Vérifiez que vos identifiants sont corrects")
    print("4. Votre compte est peut-être verrouillé (trop de tentatives)")

input("\nAppuyez sur Entrée pour quitter...")
