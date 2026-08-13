#!/usr/bin/env python3
"""
Script de test pour un provider spécifique
"""

import sys
from pathlib import Path

# Ajouter le chemin du plugin pour les imports
sys.path.insert(0, str(Path(__file__).parent))

from lib.providers import get_providers, get_channels

def list_providers():
    """Affiche la liste des providers disponibles"""
    providers = get_providers()
    print(f"\n📡 {len(providers)} providers disponibles :")
    for i, prov in enumerate(providers):
        print(f"   {i+1}. {prov.get('title', 'Unknown')}")

def test_provider(provider_name=None):
    """Test un provider spécifique"""
    providers = get_providers()
    
    for prov in providers:
        if provider_name and prov.get('title') != provider_name:
            continue
        
        print(f"\n📡 {prov.get('title')}")
        m3u_url = prov.get('catLink')
        if m3u_url:
            try:
                channels = get_channels(m3u_url)
                print(f"   ✅ {len(channels)} chaînes")
                if channels:
                    ch = channels[0]
                    print(f"   📺 Exemple : {ch.title}")
                    print(f"   🔗 URL : {ch.url[:80]}...")
            except Exception as e:
                print(f"   ❌ Erreur : {e}")

def main():
    if len(sys.argv) > 1:
        test_provider(sys.argv[1])
    else:
        list_providers()
        print("\n💡 Pour tester un provider spécifique :")
        print("   python test_flux.py 'nom_du_provider'")

if __name__ == "__main__":
    main()