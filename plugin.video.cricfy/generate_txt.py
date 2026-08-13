#!/usr/bin/env python3
"""
Génère un fichier cricfy.txt avec les flux et leurs images
Format : Nom de la chaîne | URL du flux | URL du logo | Provider
"""

import json
import sys
from pathlib import Path

# Ajouter le chemin du plugin pour les imports
sys.path.insert(0, str(Path(__file__).parent))

def generate_txt():
    """Génère cricfy.txt à partir de flux_cricfy.json"""
    
    # Charger le fichier JSON
    json_file = Path(__file__).parent / "flux_cricfy.json"
    if not json_file.exists():
        print("❌ flux_cricfy.json introuvable")
        return
    
    with open(json_file, 'r', encoding='utf-8') as f:
        flux = json.load(f)
    
    if not flux:
        print("❌ Aucun flux trouvé")
        return
    
    # Générer le fichier TXT
    txt_file = Path(__file__).parent / "cricfy.txt"
    
    with open(txt_file, 'w', encoding='utf-8') as f:
        # En-tête
        f.write("#" + "=" * 78 + "\n")
        f.write("# LISTE DES FLUX CRICFY\n")
        f.write(f"# {len(flux)} chaînes récupérées\n")
        f.write("#" + "=" * 78 + "\n")
        f.write("# Format: Nom | URL du flux | URL du logo | Provider | DRM\n")
        f.write("#" + "=" * 78 + "\n\n")
        
        # Trier par provider puis par nom
        flux_tries = sorted(flux, key=lambda x: (x.get('provider', ''), x.get('title', '')))
        
        # Compter par provider
        providers = {}
        for ch in flux_tries:
            prov = ch.get('provider', 'Unknown')
            providers[prov] = providers.get(prov, 0) + 1
        
        for prov, count in providers.items():
            f.write(f"\n# 📡 {prov} ({count} chaînes)\n")
            f.write("#" + "-" * 78 + "\n")
            
            for ch in flux_tries:
                if ch.get('provider') != prov:
                    continue
                
                title = ch.get('title', 'Unknown')
                url = ch.get('url', '')
                logo = ch.get('logo', '')
                drm = '🔒' if ch.get('is_drm') else ''
                
                # Écrire la ligne
                f.write(f"{title} | {url} | {logo} | {prov} | {drm}\n")

    print(f"✅ cricfy.txt généré avec {len(flux)} chaînes")

def generate_m3u():
    """Génère un fichier M3U utilisable dans Kodi/VLC"""
    
    json_file = Path(__file__).parent / "flux_cricfy.json"
    if not json_file.exists():
        print("❌ flux_cricfy.json introuvable")
        return
    
    with open(json_file, 'r', encoding='utf-8') as f:
        flux = json.load(f)
    
    if not flux:
        return
    
    m3u_file = Path(__file__).parent / "cricfy.m3u"
    
    with open(m3u_file, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        f.write("# Généré automatiquement depuis Cricfy\n\n")
        
        for ch in flux:
            title = ch.get('title', 'Unknown')
            url = ch.get('url', '')
            logo = ch.get('logo', '')
            group = ch.get('group', '')
            
            if not url:
                continue
            
            f.write(f'#EXTINF:-1 tvg-logo="{logo}" group-title="{group}",{title}\n')
            f.write(f'{url}\n')
    
    print(f"✅ cricfy.m3u généré avec {len(flux)} chaînes")

if __name__ == "__main__":
    generate_txt()
    generate_m3u()