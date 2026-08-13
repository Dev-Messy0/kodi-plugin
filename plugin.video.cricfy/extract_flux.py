#!/usr/bin/env python3
"""
Extracteur de flux Cricfy - Version améliorée
Récupère tous les flux, y compris beIN, Canal+, RMC Sport
"""

import json
import sys
import time
import re
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
        print("❌ Échec du déchiffrement")
        return []
    
    try:
        providers = json.loads(providers_json)
        print(f"✅ {len(providers)} providers trouvés")
    except json.JSONDecodeError as e:
        print(f"❌ Erreur JSON : {e}")
        return []
    
    all_channels = []
    failed_providers = []
    
    for idx, provider in enumerate(providers):
        title = provider.get('title', 'Unknown')
        m3u_url = provider.get('catLink')
        print(f"\n📡 [{idx+1}/{len(providers)}] Provider : {title}")
        
        if not m3u_url or m3u_url == "null" or m3u_url == "N":
            print("   ⚠️ URL invalide, ignoré")
            continue
        
        try:
            print(f"   🔗 Récupération du M3U...")
            content = fetch_url(m3u_url, timeout=20)
            
            if not content:
                print("   ❌ Contenu vide")
                failed_providers.append(title)
                continue
            
            # Vérifier si c'est du HTML (erreur)
            if content.strip().startswith("<!DOCTYPE") or content.strip().startswith("<html"):
                print("   ⚠️ Réponse HTML (probablement bloqué), tentative de récupération alternative...")
                # Essayer avec un User-Agent différent
                content = fetch_url(m3u_url, timeout=20, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
                if content and content.strip().startswith("#EXTM3U"):
                    print("   ✅ Récupéré avec User-Agent alternatif")
                else:
                    failed_providers.append(title)
                    continue
            
            print("   🔓 Déchiffrement du M3U...")
            m3u_content = decrypt_content(content)
            
            # Si le contenu est encore chiffré, essayer de le déchiffrer différemment
            if not m3u_content.startswith("#EXTM3U") and len(m3u_content) > 100:
                print("   🔄 Tentative de déchiffrement alternatif...")
                try:
                    # Essayer de décoder comme base64
                    import base64
                    decoded = base64.b64decode(m3u_content).decode('utf-8', errors='ignore')
                    if decoded.startswith("#EXTM3U"):
                        m3u_content = decoded
                        print("   ✅ Déchiffré via base64")
                except:
                    pass
            
            print("   📊 Parsing du M3U...")
            channels = parse_m3u(m3u_content)
            
            # Filtrer les chaînes sans URL valide
            valid_channels = [ch for ch in channels if ch.url and ch.url.startswith(('http', 'https'))]
            
            print(f"   ✅ {len(valid_channels)} chaînes valides trouvées")
            
            for ch in valid_channels:
                # Nettoyer l'URL
                url = ch.url.strip()
                if not url.startswith(('http', 'https')):
                    continue
                
                all_channels.append({
                    'provider': title,
                    'title': ch.title.strip() if ch.title else 'Sans titre',
                    'url': url,
                    'logo': ch.tvg_logo or '',
                    'group': ch.group_title or '',
                    'user_agent': ch.user_agent or '',
                    'cookie': ch.cookie or '',
                    'referer': ch.referer or '',
                    'headers': ch.headers or {},
                    'is_drm': ch.is_drm or False,
                    'license_string': ch.license_string or ''
                })
            
            # Pause pour éviter le blocage
            time.sleep(1)
                
        except Exception as e:
            print(f"   ❌ Erreur : {str(e)[:100]}")
            failed_providers.append(title)
            # Essayer de récupérer le contenu brut
            try:
                content = fetch_url(m3u_url, timeout=15)
                if content and content.startswith("#EXTM3U"):
                    channels = parse_m3u(content)
                    print(f"   ✅ {len(channels)} chaînes récupérées en brut")
                    for ch in channels:
                        if ch.url and ch.url.startswith('http'):
                            all_channels.append({
                                'provider': title,
                                'title': ch.title or 'Sans titre',
                                'url': ch.url,
                                'logo': ch.tvg_logo or '',
                                'group': ch.group_title or '',
                                'user_agent': '',
                                'cookie': '',
                                'referer': '',
                                'headers': {},
                                'is_drm': False,
                                'license_string': ''
                            })
            except:
                pass
    
    # Afficher les providers qui ont échoué
    if failed_providers:
        print(f"\n⚠️ {len(failed_providers)} providers ont échoué :")
        for p in failed_providers[:10]:
            print(f"   - {p}")
    
    return all_channels

def save_flux(flux, output_file="flux_cricfy.json"):
    """Sauvegarde les flux dans un fichier JSON"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(flux, f, indent=2, ensure_ascii=False)
    print(f"\n💾 {len(flux)} flux sauvegardés dans {output_file}")

def save_flux_csv(flux, output_file="flux_cricfy.csv"):
    """Sauvegarde les flux en CSV"""
    import csv
    if not flux:
        return
    
    keys = ['title', 'provider', 'url', 'group', 'logo', 'is_drm']
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for ch in flux:
            row = {k: ch.get(k, '') for k in keys}
            row['is_drm'] = 'Oui' if ch.get('is_drm') else 'Non'
            writer.writerow(row)
    print(f"💾 CSV sauvegardé dans {output_file}")

def search_keywords(flux, keywords):
    """Recherche des mots-clés dans les titres des flux"""
    results = []
    for ch in flux:
        title = ch.get('title', '').lower()
        for kw in keywords:
            if kw.lower() in title:
                results.append(ch)
                break
    return results

def main():
    print("=" * 60)
    print("🚀 EXTRACTEUR DE FLUX CRICFY - VERSION AMÉLIORÉE")
    print("=" * 60)
    
    flux = get_all_flux()
    
    if not flux:
        print("\n❌ Aucun flux récupéré")
        return
    
    print(f"\n✅ {len(flux)} flux récupérés au total")
    
    save_flux(flux)
    
    try:
        save_flux_csv(flux)
    except Exception as e:
        print(f"⚠️ Erreur export CSV : {e}")
    
    # Rechercher beIN, Canal+, RMC, etc.
    keywords = ['bein', 'canal', 'rmc', 'sport', 'foot', 'football', 'l1', 'ligue 1', 
                'premier league', 'champions league', 'euro', 'coupe du monde']
    sports_flux = search_keywords(flux, keywords)
    
    if sports_flux:
        print(f"\n⚽ {len(sports_flux)} flux sportifs trouvés (beIN, Canal+, RMC, ...)")
        print("\n📺 Aperçu des flux sportifs :")
        for i, ch in enumerate(sports_flux[:10]):
            print(f"\n{i+1}. {ch['title']}")
            print(f"   Provider: {ch['provider']}")
            print(f"   URL: {ch['url'][:80]}...")
    else:
        print("\n⚠️ Aucun flux avec beIN/Canal/RMC trouvé dans les titres")
        print("   Vérifie le fichier flux_cricfy.json pour explorer manuellement")
    
    # Aperçu général
    print("\n📺 Aperçu des 5 premiers flux :")
    for i, ch in enumerate(flux[:5]):
        if ch.get('title'):
            print(f"\n{i+1}. {ch['title']}")
            print(f"   Provider: {ch['provider']}")
            print(f"   URL: {ch['url'][:80]}...")

if __name__ == "__main__":
    main()