# Phoenix Desk - personnalisation de RustDesk avant compilation
# (nom, serveur, clé, icônes). Lancé automatiquement par .github/workflows/phoenixdesk.yml
import pathlib, shutil, sys

SERVEUR = "phoenixdesk.duckdns.org"
CLE = "wUyXlGkl2hVqFVKCKD++Ue4l96DuNMbrVkI4lvynBdI="
NOM = "PhoenixDesk"            # nom interne (sans espace)
NOM_AFFICHE = "Phoenix Desk"
DESCRIPTION = "Phoenix Desk - Assistance a distance Phoenixtore"

racine = pathlib.Path(__file__).resolve().parent.parent
icones = racine
erreurs = []

def remplacer(fichier, ancien, nouveau, obligatoire=True):
    p = racine / fichier
    txt = p.read_text(encoding="utf-8")
    if ancien not in txt:
        (erreurs.append if obligatoire else print)(f"Introuvable dans {fichier} : {ancien}")
        return
    p.write_text(txt.replace(ancien, nouveau), encoding="utf-8")
    print(f"OK {fichier} : {ancien[:50]}")

# 1. Serveur, clé et nom de l'application
cfg = "libs/hbb_common/src/config.rs"
remplacer(cfg, '&["rs-ny.rustdesk.com"]', f'&["{SERVEUR}"]')
remplacer(cfg, 'RS_PUB_KEY: &str = "OeVuKk5nlHiXp+APNn0Y3pC1Iwpwn44JGqrQCsWqmBw="', f'RS_PUB_KEY: &str = "{CLE}"')
remplacer(cfg, 'APP_NAME: RwLock<String> = RwLock::new("RustDesk".to_owned())', f'APP_NAME: RwLock<String> = RwLock::new("{NOM}".to_owned())')

# 2. Infos visibles dans les propriétés du .exe
remplacer("flutter/windows/runner/Runner.rc", '"RustDesk Remote Desktop"', f'"{DESCRIPTION}"')
remplacer("flutter/windows/runner/Runner.rc", 'VALUE "ProductName", "RustDesk"', f'VALUE "ProductName", "{NOM_AFFICHE}"')
remplacer("Cargo.toml", 'ProductName = "RustDesk"', f'ProductName = "{NOM_AFFICHE}"', obligatoire=False)
remplacer("Cargo.toml", 'FileDescription = "RustDesk Remote Desktop"', f'FileDescription = "{DESCRIPTION}"', obligatoire=False)

# 3. Icônes et logos
copies = {
    "icon.ico": ["res/icon.ico", "flutter/windows/runner/resources/app_icon.ico", "flutter/assets/icon.ico"],
    "tray-icon.ico": ["res/tray-icon.ico"],
    "icon.png": ["res/icon.png"],
    "mac-icon.png": ["res/mac-icon.png"],
    "32x32.png": ["res/32x32.png"],
    "64x64.png": ["res/64x64.png"],
    "128x128.png": ["res/128x128.png"],
    "128x128@2x.png": ["res/128x128@2x.png"],
    "icon-ui.png": ["flutter/assets/icon.png"],
    "icon.svg": ["flutter/assets/icon.svg"],
    "logo.png": ["flutter/assets/logo.png"],
    "logo_light.png": ["flutter/assets/logo_light.png"],
    "logo_dark.png": ["flutter/assets/logo_dark.png"],
}
for src, dests in copies.items():
    s = icones / src
    if not s.exists():
        erreurs.append(f"Icône manquante : {s}")
        continue
    for d in dests:
        shutil.copyfile(s, racine / d)
        print(f"OK icône {d}")

if erreurs:
    print("\n".join(erreurs))
    sys.exit(1)
print("Personnalisation Phoenix Desk terminée.")
