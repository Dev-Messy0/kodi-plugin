#!/usr/bin/env python3
"""
Extracteur de flux Cricfy
Utilise les fonctions du plugin Kodi pour récupérer les URLs des streams
"""

import json
import sys
from pathlib import Path

# Ajouter le chemin du plugin pour les imports
sys.path.insert(0, str(Path(__file__).parent))

from lib.remote_config import get_provider_api_url
from lib.req import fetch_url
from lib.crypto_utils import decrypt_data, decrypt_content
from lib.m3u_parser import parse_m3u
from lib.logger import log_info, log_error

def get_all_flux():
    """Récupère tous les flux vidéo de tous les providers"""
    
    print("🔍 Récupération de l'URL de l'API...")
    api_url = get_provider_api_url()
    if not api_url:
        print("❌ Impossible de récupérer l'URL de l'API")
        return []
    print(f"✅ API URL : {api_url}")
    
    print("🔍 Récupération de cats.txt...")
    try:
        encrypted = fetch_url(f"{api_url}/cats.txt")
        if not encrypted:
            print("❌ cats.txt vide ou inaccessible")
            return []
    except Exception as e:
        print(f"❌ Erreur fetch cats.txt : {e}")
        return []
    
    print("🔍 Déchiffrement de cats.txt...")
    providers_json = decrypt_data(encrypted)
    if not providers_json:
        print("❌ Échec du déchiffrement (vérifie secret1.txt et secret2.txt)")
        return []
    
    try:
        providers = json.loads(providers_json)
        print(f"✅ {len(providers)} providers trouvés")
    except json.JSONDecodeError as e:
        print(f"❌ Erreur JSON : {e}")
        return []
    
    all_channels = []
    
    for idx, provider in enumerate(providers):
        title = provider.get('title', 'Unknown')
        m3u_url = provider.get('catLink')
        print(f"\n📡 [{idx+1}/{len(providers)}] Provider : {title}")
        
        if not m3u_url:
            print("   ⚠️ Pas d'URL M3U")
            continue
        
        try:
            print(f"   🔗 Récupération du M3U...")
            content = fetch_url(m3u_url)
            if not content:
                print("   ❌ Contenu M3U vide")
                continue
            
            print("   🔓 Déchiffrement du M3U...")
            m3u_content = decrypt_content(content)
            
            print("   📊 Parsing du M3U...")
            channels = parse_m3u(m3u_content)
            print(f"   ✅ {len(channels)} chaînes trouvées")
            
            for ch in channels:
                all_channels.append({
                    'provider': title,
                    'title': ch.title,
                    'url': ch.url,
                    'logo': ch.tvg_logo,
                    'group': ch.group_title,
                    'user_agent': ch.user_agent,
                    'cookie': ch.cookie,
                    'referer': ch.referer,
                    'headers': ch.headers,
                    'is_drm': ch.is_drm,
                    'license_string': ch.license_string
                })
                
        except Exception as e:
            print(f"   ❌ Erreur : {e}")
    
    return all_channels

def save_flux(flux, output_file="flux_cricfy.json"):
    """Sauvegarde les flux dans un fichier JSON"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(flux, f, indent=2, ensure_ascii=False)
    print(f"\n💾 {len(flux)} flux sauvegardés dans {output_file}")

def save_flux_csv(flux, output_file="flux_cricfy.csv"):
    """Sauvegarde les flux en CSV (version simplifiée)"""
    import csv
    if not flux:
        return
    
    keys = ['title', 'provider', 'url', 'group', 'logo']
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for ch in flux:
            writer.writerow({k: ch.get(k, '') for k in keys})
    print(f"💾 CSV sauvegardé dans {output_file}")

def main():
    print("=" * 60)
    print("🚀 EXTRACTEUR DE FLUX CRICFY")
    print("=" * 60)
    
    flux = get_all_flux()
    
    if not flux:
        print("\n❌ Aucun flux récupéré")
        return
    
    print(f"\n✅ {len(flux)} flux récupérés au total")
    
    # Sauvegarde en JSON
    save_flux(flux)
    
    # Sauvegarde en CSV
    try:
        save_flux_csv(flux)
    except Exception as e:
        print(f"⚠️ Erreur export CSV : {e}")
    
    # Afficher un aperçu
    print("\n📺 Aperçu des 5 premiers flux :")
    for i, ch in enumerate(flux[:5]):
        print(f"\n{i+1}. {ch['title']}")
        print(f"   Provider: {ch['provider']}")
        print(f"   URL: {ch['url'][:100]}...")
        if ch.get('user_agent'):
            print(f"   User-Agent: {ch['user_agent'][:50]}...")
        if ch.get('referer'):
            print(f"   Referer: {ch['referer']}")
        if ch.get('is_drm'):
            print("   🔒 DRM protégé")

if __name__ == "__main__":
    main()