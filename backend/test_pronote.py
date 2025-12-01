"""
Script de test de connexion PRONOTE avec différentes méthodes
"""

import pronotepy
from pronotepy.ent import ac_montpellier
import sys

def test_connection(url, username, password, ent=None):
    print("\n" + "="*60)
    print(f"Test de connexion à {url}")
    print(f"Utilisateur: {username}")
    print("="*60)
    
    # Méthode 1: Avec ENT
    if ent:
        print("\n[1/3] Tentative avec ENT...")
        try:
            client = pronotepy.Client(
                url,
                username=username,
                password=password,
                ent=ent
            )
            
            if client.logged_in:
                print("✅ Connexion réussie avec ENT!")
                show_info(client)
                return client
            else:
                print("❌ Échec de la connexion avec ENT")
        except Exception as e:
            print(f"❌ Erreur avec ENT: {e}")
    
    # Méthode 2: Sans ENT
    print("\n[2/3] Tentative sans ENT...")
    try:
        client = pronotepy.Client(
            url,
            username=username,
            password=password
        )
        
        if client.logged_in:
            print("✅ Connexion réussie sans ENT!")
            show_info(client)
            return client
        else:
            print("❌ Échec de la connexion sans ENT")
    except Exception as e:
        print(f"❌ Erreur sans ENT: {e}")
    
    # Méthode 3: Avec device_name (pour les comptes avec sécurité renforcée)
    print("\n[3/3] Tentative avec identification de l'appareil...")
    try:
        client = pronotepy.Client(
            url,
            username=username,
            password=password,
            device_name="PRONOTE Analyzer App",
            ent=ent if ent else None
        )
        
        if client.logged_in:
            print("✅ Connexion réussie avec identification d'appareil!")
            show_info(client)
            return client
        else:
            print("❌ Échec avec identification d'appareil")
    except Exception as e:
        print(f"❌ Erreur avec identification d'appareil: {e}")
    
    print("\n❌ Toutes les tentatives de connexion ont échoué")
    return None

def show_info(client):
    """Affiche les informations de l'utilisateur connecté"""
    try:
        info = client.info
        print(f"\n👤 Informations de l'élève:")
        print(f"   Nom: {info.name}")
        print(f"   Classe: {info.class_name}")
        print(f"   Établissement: {info.establishment}")
        
        # Afficher les périodes disponibles
        print("\n📅 Périodes disponibles:")
        for period in client.periods:
            print(f"   - {period.name} ({period.start.strftime('%d/%m/%Y')} - {period.end.strftime('%d/%m/%Y')})")
        
        # Afficher les notes de la période actuelle
        current = client.current_period
        if current:
            print(f"\n📊 Notes de la période {current.name}:")
            for grade in current.grades[:5]:  # Affiche les 5 premières notes
                print(f"   - {grade.subject.name}: {grade.grade}/{grade.out_of}")
            if len(current.grades) > 5:
                print(f"   ... et {len(current.grades) - 5} notes supplémentaires")
    
    except Exception as e:
        print(f"⚠️ Impossible de récupérer les informations: {e}")

if __name__ == "__main__":
    # Configuration pour le Lycée Germaine Tillion
    URL = "https://0110012d.index-education.net/pronote/eleve.html"
    USERNAME = "c.bennaceur34"
    PASSWORD = "Leda1312lina/"
    
    print("🔍 Test de connexion PRONOTE - Lycée Germaine Tillion")
    
    # Essai avec ENT ac_montpellier
    client = test_connection(URL, USERNAME, PASSWORD, ent=ac_montpellier)
    
    if not client:
        print("\n❌ Aucune méthode de connexion n'a fonctionné. Vérifiez:")
        print("  1. Vos identifiants (nom d'utilisateur/mot de passe)")
        print("  2. Que l'URL est correcte")
        print("  3. Que vous pouvez vous connecter via le navigateur")
        print("  4. Que votre compte n'a pas de 2FA activé")
    
    input("\nAppuyez sur Entrée pour quitter...")
