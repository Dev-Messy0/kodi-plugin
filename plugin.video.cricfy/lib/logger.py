"""
Logger adapté pour fonctionner avec ou sans Kodi
Utilise un mock de xbmc.log si Kodi n'est pas disponible
"""

import sys

# Simuler xbmc.log en environnement non-Kodi
class XbmcMock:
    @staticmethod
    def log(message, level=0):
        print(f"[LOG] {message}")

# Détecter si on est dans Kodi
try:
    import xbmc
except ImportError:
    # Environnement non-Kodi (GitHub Actions, terminal, etc.)
    xbmc = XbmcMock()
    # Simuler aussi xbmc.LOGERROR et LOGINFO
    xbmc.LOGERROR = 0
    xbmc.LOGINFO = 0

def log_error(component: str, message: str) -> None:
    xbmc.log(f"Cricfy Plugin [{component}]: {message}", xbmc.LOGERROR)

def log_info(component: str, message: str) -> None:
    xbmc.log(f"Cricfy Plugin [{component}]: {message}", xbmc.LOGINFO)