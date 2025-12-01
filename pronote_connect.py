"""
Script de connexion PRONOTE avec pronotepy
"""

import pronotepy
from pronotepy.ent import ac_montpellier

def connect_pronote():
    # Configuration du lycée
    URL = "https://0110012d.index-education.net/pronote/eleve.html"
    USERNAME = "c.bennaceur34"
    PASSWORD = "Leda1312lina/"
    
    print("🔍 Tentative de connexion à PRONOTE...\n")
    
    # 1. Essai avec ENT
    print("1. Essai avec ENT ac_montpellier...")
    try:
        client = pronotepy.Client(
            URL,
            username=USERNAME,
            password=PASSWORD,
            ent=ac_montpellier
        )
        
        if client.logged_in:
            print("✅ Connecté avec succès via ENT!")
            return client
        else:
            print("❌ Échec avec ENT")
    except Exception as e:
        print(f"❌ Erreur ENT: {str(e)[:100]}...")
    
    # 2. Essai sans ENT
    print("\n2. Essai sans ENT...")
    try:
        client = pronotepy.Client(
            URL,
            username=USERNAME,
            password=PASSWORD
        )
        
        if client.logged_in:
            print("✅ Connecté avec succès sans ENT!")
            return client
        else:
            print("❌ Échec sans ENT")
    except Exception as e:
        print(f"❌ Erreur sans ENT: {str(e)[:100]}...")
    
    # 3. Essai avec QR Code (méthode recommandée)
    print("\n3. Méthode recommandée: Connexion par QR Code")
    print("Ouvrez PRONOTE sur votre téléphone et suivez ces étapes:")
    print("1. Allez dans l'application PRONOTE")
    print("2. Menu ☰ > QR Code")
    print("3. Scannez le QR Code ci-dessous\n")
    
    try:
        from pronotepy.dataClasses import QrCodeLogin
        qr = QrCodeLogin(URL)
        
        print("Scannez ce QR Code avec l'application PRONOTE:")
        print(qr.qr_code_text)
        
        print("\nEn attente de la confirmation...")
        client = qr.wait_for_connection()
        
        if client and client.logged_in:
            print("✅ Connecté avec succès via QR Code!")
            return client
        else:
            print("❌ Échec de la connexion par QR Code")
    except Exception as e:
        print(f"❌ Erreur QR Code: {str(e)[:100]}...")
    
    return None

if __name__ == "__main__":
    client = connect_pronote()
    
    if client:
        try:
            print("\n📋 Informations de connexion:")
            print(f"   Nom: {client.info.name}")
            print(f"   Classe: {client.info.class_name}")
            
            # Afficher les périodes
            print("\n📅 Périodes disponibles:")
            for period in client.periods:
                print(f"   - {period.name}")
            
            # Afficher quelques notes
            if client.current_period and client.current_period.grades:
                print("\n📊 Dernières notes:")
                for grade in client.current_period.grades[:5]:
                    print(f"   - {grade.subject.name}: {grade.grade}/{grade.out_of}")
            
            print("\n✅ Connexion réussie!")
            
        except Exception as e:
            print(f"⚠️ Erreur lors de la récupération des données: {e}")
    else:
        print("\n❌ Impossible de se connecter. Vérifiez:")
        print("  1. Vos identifiants (nom d'utilisateur/mot de passe)")
        print("  2. Que l'URL est correcte")
        print("  3. Que vous pouvez vous connecter via l'application mobile")
        print("\n💡 Conseil: Essayez d'abord de vous connecter via l'application mobile,\npuis utilisez la méthode du QR Code ci-dessus.")
    
    input("\nAppuyez sur Entrée pour quitter...")
