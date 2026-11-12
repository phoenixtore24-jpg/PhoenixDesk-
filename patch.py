# Phoenix Desk - personnalisation de RustDesk avant compilation
# (nom, serveur, clé, icônes). Lancé automatiquement par .github/workflows/phoenixdesk.yml
import pathlib, shutil, sys

SERVEUR = "phoenixdesk.duckdns.org"
CLE = "wUyXlGkl2hVqFVKCKD++Ue4l96DuNMbrVkI4lvynBdI="
NOM = "PhoenixDesk"            # nom interne (sans espace)
NOM_AFFICHE = "Phoenix Desk"
DESCRIPTION = "Phoenix Desk - Assistance a distance Phoenixtore"

racine = pathlib.Path(__file__).resolve().parent
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

# 4. Bandeau de présentation dans la fenêtre : nom, entreprise et téléphone
NOM_PRO = "Léo Oreiller"
ENTREPRISE = "By Phoenixtore"
TEL = "07 80 52 14 45"
bandeau = f"""      Align(
        alignment: Alignment.center,
        child: loadLogo(),
      ),
      Container(
        margin: const EdgeInsets.fromLTRB(16, 0, 16, 10),
        padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 8),
        decoration: BoxDecoration(
          color: const Color(0xFF2A1B6B),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          children: const [
            Text(
              '{NOM_PRO}',
              textAlign: TextAlign.center,
              style: TextStyle(
                  color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15),
            ),
            Text(
              '{ENTREPRISE}',
              textAlign: TextAlign.center,
              style: TextStyle(
                  color: Color(0xFF22D3EE),
                  fontWeight: FontWeight.w600,
                  fontSize: 13),
            ),
            SizedBox(height: 6),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.phone, color: Colors.white, size: 14),
                SizedBox(width: 4),
                Text(
                  '{TEL}',
                  style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 13),
                ),
              ],
            ),
          ],
        ),
      ),"""
remplacer("flutter/lib/desktop/pages/desktop_home_page.dart",
"""      Align(
        alignment: Alignment.center,
        child: loadLogo(),
      ),""", bandeau)

# 5. Fin de séance : ouvre la page Google pour laisser un avis (côté client)
AVIS = "https://g.page/r/CUogfqw2amr3ECE/review"
sm = "flutter/lib/models/server_model.dart"
remplacer(sm, "import 'model.dart';\n",
"""import 'model.dart';
import 'package:url_launcher/url_launcher.dart';

bool _avisOuvert = false;
""")
remplacer(sm, """      if (desktopType == DesktopType.cm && _clients.isEmpty) {
        hideCmWindow();
      }
      if (isAndroid) androidUpdatekeepScreenOn();
      notifyListeners();
    } catch (e) {
      debugPrint("onClientRemove failed,error:$e");""",
f"""      if (desktopType == DesktopType.cm && _clients.isEmpty) {{
        if (!_avisOuvert) {{
          _avisOuvert = true;
          launchUrl(Uri.parse('{AVIS}'),
              mode: LaunchMode.externalApplication);
        }}
        hideCmWindow();
      }}
      if (isAndroid) androidUpdatekeepScreenOn();
      notifyListeners();
    }} catch (e) {{
      debugPrint("onClientRemove failed,error:$e");""")

if erreurs:
    print("\n".join(erreurs))
    sys.exit(1)
print("Personnalisation Phoenix Desk terminée.")
