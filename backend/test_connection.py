"""
Test de connexion PRONOTE pour Lycée Germaine Tillion
"""

import pronotepy

# Vos identifiants
url = "https://0110012d.index-education.net/pronote/eleve.html"
username = "c.bennaceur34"
password = "Leda1312lina/"

print("=" * 60)
print("Test de connexion PRONOTE")
print("=" * 60)
print(f"URL: {url}")
print(f"Username: {username}")
print(f"Password: {'*' * len(password)}")
print()

try:
    # Test avec ENT ac_montpellier
    print("Tentative 1: Avec ENT ac_montpellier...")
    from pronotepy.ent import ac_montpellier
    
    client = pronotepy.Client(
        url,
        username=username,
        password=password,
        ent=ac_montpellier
    )
    
    if client.logged_in:
        print("✅ CONNEXION REUSSIE avec ENT!")
        print(f"   Nom: {client.info.name}")
        print(f"   Classe: {client.info.class_name}")
        
        # Test récupération des notes
        print("\nTest récupération des notes...")
        if client.current_period:
            grades = client.current_period.grades
            print(f"✅ {len(grades)} notes trouvées!")
            if grades:
                print(f"   Exemple: {grades[0].subject.name} - {grades[0].grade}/{grades[0].out_of}")
        
        client = None
        exit(0)
    else:
        print("❌ Échec avec ENT")
        
except Exception as e:
    print(f"❌ Erreur avec ENT: {e}")

print()

try:
    # Test sans ENT
    print("Tentative 2: Sans ENT...")
    
    client = pronotepy.Client(
        url,
        username=username,
        password=password
    )
    
    if client.logged_in:
        print("✅ CONNEXION REUSSIE sans ENT!")
        print(f"   Nom: {client.info.name}")
        print(f"   Classe: {client.info.class_name}")
        
        # Test récupération des notes
        print("\nTest récupération des notes...")
        if client.current_period:
            grades = client.current_period.grades
            print(f"✅ {len(grades)} notes trouvées!")
            if grades:
                print(f"   Exemple: {grades[0].subject.name} - {grades[0].grade}/{grades[0].out_of}")
        
        exit(0)
    else:
        print("❌ Échec sans ENT")
        
except Exception as e:
    print(f"❌ Erreur sans ENT: {e}")

print()
print("=" * 60)
print("TOUTES LES TENTATIVES ONT ECHOUE")
print("Vérifiez:")
print("  1. Que l'URL est correcte")
print("  2. Que le username/password sont corrects")
print("  3. Que vous pouvez vous connecter via le site web")
print("=" * 60)
