#!/usr/bin/env python3
"""
Génère un fichier playlist.m3u8 au format JSON
Contient : nom, URL du flux (m3u8), logo, catégorie, provider, DRM
"""

import json
import sys
from pathlib import Path

# Ajouter le chemin du plugin pour les imports
sys.path.insert(0, str(Path(__file__).parent))

def generate_json_playlist():
    """
    Génère un fichier playlist.m3u8 au format JSON
    Structure : { "channels": [ { "name": "", "url": "", "logo": "", "category": "", "provider": "", "drm": false } ] }
    """
    
    json_file = Path(__file__).parent / "flux_cricfy.json"
    if not json_file.exists():
        print("❌ flux_cricfy.json introuvable")
        return
    
    with open(json_file, 'r', encoding='utf-8') as f:
        flux = json.load(f)
    
    if not flux:
        print("❌ Aucun flux trouvé")
        return
    
    # Structure de la playlist JSON
    playlist = {
        "version": "1.0",
        "generated": str(Path(__file__).parent.stat().st_mtime),
        "total": len(flux),
        "channels": []
    }
    
    # Trier par provider puis par nom
    flux_tries = sorted(flux, key=lambda x: (x.get('provider', ''), x.get('title', '')))
    
    for ch in flux_tries:
        # Nettoyer l'URL
        url = ch.get('url', '').strip()
        if not url or not url.startswith(('http', 'https')):
            continue
        
        # Nettoyer le nom
        name = ch.get('title', 'Sans titre').strip()
        if not name or name == 'Sans titre':
            # Essayer d'extraire un nom depuis l'URL
            import re
            match = re.search(r'/([^/]+)\.m3u8?', url)
            if match:
                name = match.group(1).replace('_', ' ').title()
        
        channel = {
            "name": name,
            "url": url,
            "logo": ch.get('logo', ''),
            "category": ch.get('group', '') or ch.get('provider', 'General'),
            "provider": ch.get('provider', 'Unknown'),
            "drm": ch.get('is_drm', False),
            "user_agent": ch.get('user_agent', ''),
            "referer": ch.get('referer', ''),
            "headers": ch.get('headers', {})
        }
        
        playlist["channels"].append(channel)
    
    # Sauvegarder en JSON
    output_file = Path(__file__).parent / "playlist.m3u8"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(playlist, f, indent=2, ensure_ascii=False)
    
    print(f"✅ playlist.m3u8 généré avec {len(playlist['channels'])} chaînes (format JSON)")
    
    # Générer aussi une version M3U classique pour compatibilité
    generate_classic_m3u(flux)

def generate_classic_m3u(flux):
    """Génère un fichier M3U classique en parallèle"""
    
    m3u_file = Path(__file__).parent / "playlist_classic.m3u"
    
    with open(m3u_file, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        f.write(f"# Généré automatiquement depuis Cricfy - {len(flux)} chaînes\n\n")
        
        for ch in flux:
            name = ch.get('title', 'Sans titre').strip()
            url = ch.get('url', '').strip()
            logo = ch.get('logo', '')
            group = ch.get('group', '') or ch.get('provider', 'General')
            
            if not url or not url.startswith(('http', 'https')):
                continue
            
            # Nettoyer le nom pour éviter les caractères spéciaux
            name_safe = name.replace('|', '').replace('\\', '')
            
            f.write(f'#EXTINF:-1 tvg-logo="{logo}" group-title="{group}",{name_safe}\n')
            f.write(f'{url}\n')
    
    print(f"✅ playlist_classic.m3u généré (format M3U classique)")

def generate_categories(flux):
    """Génère un résumé des catégories disponibles"""
    
    categories = {}
    for ch in flux:
        cat = ch.get('group', '') or ch.get('provider', 'General')
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += 1
    
    print("\n📊 Catégories disponibles :")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"   - {cat}: {count} chaînes")

if __name__ == "__main__":
    generate_json_playlist()