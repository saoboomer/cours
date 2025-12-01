"""
Script de connexion PRONOTE ultra-simplifié
Basé sur la documentation officielle de pronotepy
"""

import pronotepy
import datetime

# Configuration
URL = "https://0110012d.index-education.net/pronote/eleve.html"
USERNAME = "c.bennaceur34"
PASSWORD = "Leda1312lina/"

print("🔍 Tentative de connexion à PRONOTE...\n")

# Méthode 1: Connexion directe (sans ENT)
try:
    print("1. Essai de connexion directe...")
    client = pronotepy.Client(
        URL,
        username=USERNAME,
        password=PASSWORD,
        # Essayer avec device_name pour les comptes sécurisés
        device_name="PRONOTE App",
        # Essayer avec un identifiant client existant si vous en avez un
        # client_identifier="VOTRE_IDENTIFIANT_CLIENT"
    )
    
    if client.logged_in:
        print("✅ Connecté avec succès!")
        print(f"👤 Élève: {client.info.name}")
        print(f"🏫 Établissement: {client.info.establishment}")
        print(f"📅 Période actuelle: {client.current_period.name if client.current_period else 'Non disponible'}")
        
        # Afficher quelques notes
        if client.current_period and hasattr(client.current_period, 'grades'):
            print("\n📊 Dernières notes:")
            for grade in client.current_period.grades[:5]:  # Affiche les 5 premières notes
                print(f"   - {grade.subject.name}: {grade.grade}/{grade.out_of}")
        
        input("\nAppuyez sur Entrée pour quitter...")
        exit(0)
    else:
        print("❌ Échec de la connexion directe")
        
except Exception as e:
    print(f"❌ Erreur lors de la connexion directe: {e}")

# Si on arrive ici, la connexion directe a échoué
print("\n⚠️ La connexion directe a échoué. Essayons avec l'ENT...")

# Méthode 2: Connexion avec ENT
try:
    print("\n2. Essai avec ENT ac_montpellier...")
    from pronotepy.ent import ac_montpellier
    
    client = pronotepy.Client(
        URL,
        username=USERNAME,
        password=PASSWORD,
        ent=ac_montpellier
    )
    
    if client.logged_in:
        print("✅ Connecté avec succès via ENT!")
        print(f"👤 Élève: {client.info.name}")
        print(f"🏫 Établissement: {client.info.establishment}")
        
        # Afficher les périodes disponibles
        print("\n📅 Périodes disponibles:")
        for period in client.periods:
            print(f"   - {period.name}")
        
        input("\nAppuyez sur Entrée pour quitter...")
        exit(0)
    else:
        print("❌ Échec de la connexion avec ENT")
        
except Exception as e:
    print(f"❌ Erreur avec ENT: {e}")

# Si on arrive ici, tout a échoué
print("\n❌ Toutes les tentatives de connexion ont échoué.")
print("\nVeuillez vérifier :")
print("1. Vos identifiants (nom d'utilisateur/mot de passe)")
print("2. Que l'URL est correcte")
print("3. Que vous pouvez vous connecter via le navigateur")
print("4. Que votre compte n'a pas de 2FA activé")
input("\nAppuyez sur Entrée pour quitter...")
