"""
Script de connexion PRONOTE via EduConnect
"""

from pronotepy import ent
import pronotepy
from getpass import getpass

# Configuration
PRONOTE_URL = "https://0110012d.index-education.net/pronote/eleve.html"
EDUCONNECT_URL = "https://educonnect.education.gouv.fr/idp/profile/SAML2/POST/SSO"

print("🔐 Connexion PRONOTE via EduConnect\n")

# Demander les identifiants
username = input("Identifiant EduConnect: ").strip()
password = getpass("Mot de passe EduConnect: ").strip()

try:
    print("\n🔗 Connexion à EduConnect en cours...")
    
    # Créer un client EduConnect
    client = pronotepy.Client(
        PRONOTE_URL,
        username=username,
        password=password,
        ent=ent.auto_ent_login(
            PRONOTE_URL,
            username,
            password,
            # Forcer l'utilisation d'EduConnect
            ent_selector=ent.find_ent("educonnect")
        )
    )
    
    if client.logged_in:
        print("\n✅ Connecté avec succès à PRONOTE via EduConnect!")
        print(f"👤 Élève: {client.info.name}")
        print(f"🏫 Établissement: {client.info.establishment}")
        
        # Afficher les périodes disponibles
        print("\n📅 Périodes disponibles:")
        for period in client.periods:
            print(f"   - {period.name}")
        
        # Afficher quelques notes
        if client.current_period and hasattr(client.current_period, 'grades'):
            print("\n📊 Dernières notes:")
            for grade in client.current_period.grades[:5]:
                print(f"   - {grade.subject.name}: {grade.grade}/{grade.out_of}")
    else:
        print("❌ Échec de la connexion. Vérifiez vos identifiants.")
    
except Exception as e:
    print(f"\n❌ Erreur lors de la connexion: {e}")
    print("\nVeuillez vérifier :")
    print("1. Vos identifiants EduConnect")
    print("2. Que vous pouvez vous connecter via le navigateur")
    print("3. Que votre compte n'est pas verrouillé")

input("\nAppuyez sur Entrée pour quitter...")
