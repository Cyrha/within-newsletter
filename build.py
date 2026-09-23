#!/usr/bin/env python3
"""Build the newsletter outputs from the Claude Design artifact source.

  source/Main.dc.html  ->  index.html  (site GitHub Pages)
                           email.html  (copier-coller / test navigateur)
                           brevo.html  (a coller / envoyer a Brevo)

Usage:  python3 build.py [chemin/vers/Main.dc.html]
Les images sont lues dans assets/<id>.<ext> (id = identifiant _blob de l'artefact).
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_HTML = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "source", "Main.dc.html")
ASSETS_DIR = os.path.join(ROOT, "assets")


def _clean(s):
    return re.sub(r"\s+", " ", s).strip() if s else None


def extract_articles(path):
    """Parse the 3 rubriques (visuel / technique / plugins) of the artifact page."""
    with open(path, encoding="utf-8") as f:
        html = f.read()
    out = {}
    for sec in ("visuel", "technique", "plugins"):
        s = re.search(r'<section id="%s".*?</section>' % sec, html, re.S).group(0)
        items = []
        for a in re.findall(r"<article.*?</article>", s, re.S):
            title = re.search(r"<h3(?:\s[^>]*)?>(.*?)</h3>", a, re.S)
            desc = re.search(r"<p(?:\s[^>]*)?>(.*?)</p>", a, re.S)
            cta = re.search(r'<a href="(https?://[^"]+)"[^>]*>([^<]*?↗)</a>', a)
            items.append({
                "title": _clean(title.group(1)) if title else None,
                "desc": _clean(desc.group(1)) if desc else None,
                "diamant": "Diamant" in a,
                "meta": re.findall(r'color: #5A5970;">([^<]+)</span>', a),
                "imgs": re.findall(r'src="/_blob/([0-9a-f]{32})"', a),
                "cta_href": cta.group(1) if cta else None,
                "cta_label": _clean(cta.group(2)) if cta else None,
            })
        out[sec] = items
    return out


DATA = extract_articles(SRC_HTML)
EXT = {os.path.splitext(fn)[0]: os.path.splitext(fn)[1] for fn in os.listdir(ASSETS_DIR)}
missing = sorted({i for sec in DATA.values() for it in sec for i in it["imgs"] if i not in EXT})
if missing:
    sys.exit("Images manquantes dans assets/ : " + ", ".join(missing))
BASE = "https://cyrha.github.io/within-newsletter"

def img(bid, w=None):
    return f"{BASE}/assets/{bid}{EXT.get(bid, '.jpg')}"

SUBSCRIBE_URL = "https://form.jotform.com/262652969645069"
ONLINE_URL = "https://cyrha.github.io/within-newsletter/"
WERO_EMAIL = "cyril.hamel@within.fr"

DARK = "#17162E"
ACCENT = "#E94E1B"
PURPLE = "#433F80"
TEXT = "#3C3B55"
MUTED = "#5A5970"
BG = "#F2F1F6"
BORDER = "#E3E2EA"
CREAM = "#F5F5F8"

RUBRIQUE_COLORS = {"visuel": "#433F80", "technique": "#3F6FA0", "plugins": "#2E9DAA"}
RUBRIQUE_TITLES = {
    "visuel": ("01", "Possibilités visuelles", "Transformer du vrai tournage, générer des plans premium."),
    "technique": ("02", "Possibilités techniques", "Nos logiciels se pilotent en langage naturel."),
    "plugins": ("03", "Plugins &amp; scripts", "Les nouveautés à installer dans nos suites."),
}

def esc(s):
    return s or ""

def badge_html(label="Diamant"):
    return (f'<span style="display:inline-block;font-family:Oswald,Arial,sans-serif;font-weight:500;'
            f'letter-spacing:0.08em;text-transform:uppercase;font-size:11px;padding:4px 9px;'
            f'border-radius:999px;background:{ACCENT};color:#ffffff;">{label}</span>')

def meta_html(meta_list):
    if not meta_list:
        return ""
    return f'<span style="font-size:13px;color:{MUTED};font-family:Outfit,Arial,sans-serif;">{esc(meta_list[0])}</span>'

def cta_html(href, label):
    if not href:
        return ""
    return (f'<a href="{href}" style="display:inline-block;margin-top:10px;font-size:13px;font-weight:600;'
            f'color:{DARK};text-decoration:none;background:{CREAM};padding:7px 13px;border-radius:999px;'
            f'font-family:Outfit,Arial,sans-serif;">{esc(label)}</a>')

def featured_article(item, sec):
    img_url = img(item['imgs'][0]) if item['imgs'] else None
    badge = badge_html() if item['diamant'] else ""
    meta = meta_html(item['meta'])
    sep = '<span style="display:inline-block;width:1px;height:12px;background:#cfcfe0;margin:0 8px;"></span>' if (badge and meta) else ""
    img_cell = (
        f'<td width="240" valign="top" style="padding:0 20px 0 0;">'
        f'<a href="{img_url}" style="text-decoration:none;"><img src="{img_url}" width="240" alt="" '
        f'style="display:block;width:240px;max-width:240px;height:auto;border-radius:14px;border:0;"></a></td>'
        if img_url else ''
    )
    return f'''
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#ffffff;border:2px solid {ACCENT};border-radius:18px;margin-bottom:16px;">
<tr><td style="padding:18px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
{img_cell}
<td valign="top" style="font-family:Outfit,Arial,sans-serif;">
<div style="margin-bottom:8px;">{badge}{sep}{meta}</div>
<div style="font-family:Outfit,Arial,sans-serif;font-weight:800;font-size:24px;line-height:1.15;color:{DARK};margin-bottom:6px;">{esc(item['title'])}</div>
<div style="font-size:15px;line-height:1.5;color:{TEXT};">{esc(item['desc'])}</div>
{cta_html(item['cta_href'], item['cta_label'])}
</td>
</tr></table>
</td></tr>
</table>
'''

def secondary_article(item):
    img_url = img(item['imgs'][0]) if item['imgs'] else None
    badge = badge_html() if item['diamant'] else ""
    meta = meta_html(item['meta'])
    sep = '<span style="display:inline-block;width:1px;height:12px;background:#cfcfe0;margin:0 8px;"></span>' if (badge and meta) else ""
    img_html = (f'<img src="{img_url}" width="100%" alt="" style="display:block;width:100%;height:auto;'
                f'border-radius:12px;border:0;margin-bottom:12px;">') if img_url else ""
    return f'''
<td valign="top" width="50%" style="padding:0 8px 16px 0;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#ffffff;border:1px solid {BORDER};border-radius:16px;">
<tr><td style="padding:14px;font-family:Outfit,Arial,sans-serif;">
{img_html}
<div style="margin-bottom:6px;">{badge}{sep}{meta}</div>
<div style="font-family:Outfit,Arial,sans-serif;font-weight:800;font-size:18px;line-height:1.2;color:{DARK};margin-bottom:6px;">{esc(item['title'])}</div>
<div style="font-size:14px;line-height:1.5;color:{TEXT};">{esc(item['desc'])}</div>
{cta_html(item['cta_href'], item['cta_label'])}
</td></tr>
</table>
</td>'''

def ai_act_block(item):
    return f'''
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#ffffff;border:1px solid #F3C9C4;border-radius:16px;margin-bottom:16px;">
<tr><td style="padding:20px;font-family:Outfit,Arial,sans-serif;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
<td><span style="display:inline-block;font-family:Oswald,Arial,sans-serif;font-weight:500;letter-spacing:0.08em;text-transform:uppercase;font-size:11px;padding:4px 9px;border-radius:999px;background:#FDECEC;color:#B42318;">Attention</span></td>
<td align="right"><a href="{item['cta_href']}" style="font-size:13px;font-weight:500;color:{DARK};text-decoration:none;">{esc(item['cta_label'])}</a></td>
</tr></table>
<div style="font-family:Outfit,Arial,sans-serif;font-weight:700;font-size:20px;color:{DARK};margin:14px 0 8px;">{esc(item['title'])}</div>
<div style="font-size:15px;line-height:1.5;color:{TEXT};margin-bottom:14px;">{esc(item['desc'])}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
<td width="33%" style="background:{CREAM};border-radius:12px;padding:12px;"><div style="font-weight:700;font-size:13px;color:#B42318;">2 août 2026</div><div style="font-weight:600;font-size:14px;color:{DARK};">Applicable</div></td>
<td width="2%"></td>
<td width="33%" style="background:{ACCENT};border-radius:12px;padding:12px;"><div style="font-weight:700;font-size:13px;color:#ffffff;">9 oct. 2026</div><div style="font-weight:600;font-size:14px;color:#ffffff;">Aujourd'hui</div></td>
<td width="2%"></td>
<td width="30%" style="background:{CREAM};border-radius:12px;padding:12px;"><div style="font-weight:700;font-size:13px;color:#B42318;">2 déc. 2026</div><div style="font-weight:600;font-size:14px;color:{DARK};">Marquage</div></td>
</tr></table>
</td></tr>
</table>
'''

def rubrique_section(sec_id):
    num, title, blurb = RUBRIQUE_TITLES[sec_id]
    color = RUBRIQUE_COLORS[sec_id]
    items = DATA[sec_id]
    featured = items[0]
    rest = items[1:]
    ai_act = None
    if sec_id == 'technique':
        ai_act = rest[-1]
        rest = rest[:-1]

    secondary_rows = ""
    for i in range(0, len(rest), 2):
        pair = rest[i:i+2]
        cells = "".join(secondary_article(it) for it in pair)
        if len(pair) == 1:
            cells += '<td width="50%"></td>'
        secondary_rows += f'<tr>{cells}</tr>'

    ai_act_html = ai_act_block(ai_act) if ai_act else ""

    return f'''
<tr><td style="padding:56px 24px 0;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="border-bottom:3px solid {color};padding-bottom:14px;margin-bottom:22px;">
<tr>
<td width="70" valign="bottom"><span style="font-family:Outfit,Arial,sans-serif;font-weight:800;font-size:56px;color:{color};line-height:0.8;">{num}</span></td>
<td valign="bottom">
<div style="font-family:Oswald,Arial,sans-serif;font-weight:500;letter-spacing:0.08em;text-transform:uppercase;font-size:12px;color:{MUTED};margin-bottom:4px;">Rubrique {num}</div>
<div style="font-family:Outfit,Arial,sans-serif;font-weight:800;font-size:28px;color:{DARK};">{title}</div>
</td>
</tr>
</table>
{featured_article(featured, sec_id)}
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">{secondary_rows}</table>
{ai_act_html}
</td></tr>
'''

SOMMAIRE_CARDS = [
    ("01", "Possibilités visuelles", "5 outils →", "#2E2160", "#5A47A6"),
    ("02", "Possibilités techniques", "3 outils + AI Act →", "#22406F", "#4583B8"),
    ("03", "Plugins &amp; scripts", "5 outils →", "#16606B", "#3BB8C4"),
]
sommaire_cells = ""
for num, title, sub, c1, c2 in SOMMAIRE_CARDS:
    sommaire_cells += f'''
<td width="33%" valign="top" style="padding:0 6px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{c1}" style="background:{c1};border-radius:16px;">
<tr><td style="padding:18px;font-family:Outfit,Arial,sans-serif;">
<div style="font-weight:800;font-size:34px;color:#ffffff;line-height:0.9;">{num}</div>
<div style="font-weight:700;font-size:16px;color:#ffffff;margin-top:6px;">{title}</div>
<div style="font-family:Oswald,Arial,sans-serif;font-weight:500;letter-spacing:0.08em;text-transform:uppercase;font-size:10px;color:#ffffff;opacity:0.9;margin-top:4px;">{sub}</div>
</td></tr>
</table>
</td>'''

hero_thumbs = [DATA['visuel'][0]['imgs'][0], DATA['technique'][0]['imgs'][0], DATA['plugins'][0]['imgs'][0], DATA['visuel'][1]['imgs'][0]]
hero_grid = ""
for i in range(0, 4, 2):
    hero_grid += '<tr>'
    for j in (i, i+1):
        hero_grid += f'<td width="50%" style="padding:0 0 8px {"8px" if j%2 else "0"};"><img src="{img(hero_thumbs[j])}" width="100%" alt="" style="display:block;width:100%;height:auto;border-radius:12px;border:0;"></td>'
    hero_grid += '</tr>'

EMAIL = f'''<!doctype html>
<html lang="fr" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<title>Private Newsletter N°01 · WITHIN × Histoires de vies</title>
<!--[if mso]>
<noscript><xml><o:OfficeDocumentSettings><o:PixelsPerInch>96</o:PixelsPerInch></o:OfficeDocumentSettings></xml></noscript>
<style>table {{border-collapse:collapse;}} .fallback-font {{font-family: Arial, sans-serif !important;}}</style>
<![endif]-->
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&family=Oswald:wght@500&display=swap" rel="stylesheet" type="text/css">
<style>
  body, table, td {{ -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; }}
  img {{ -ms-interpolation-mode:bicubic; }}
  a {{ color:{ACCENT}; }}
  @media screen and (max-width:640px) {{
    .container {{ width:100% !important; }}
    .stack {{ display:block !important; width:100% !important; padding-right:0 !important; padding-bottom:16px !important; }}
    .px {{ padding-left:18px !important; padding-right:18px !important; }}
    .h1 {{ font-size:46px !important; }}
  }}
</style>
</head>
<body style="margin:0;padding:0;background:{BG};">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;">Spécial IA · vidéo, image &amp; marketing — 14 outils, veille juillet → septembre 2026.&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{BG}" style="background:{BG};">
<tr><td align="center" style="padding:0;">

<table role="presentation" class="container" width="640" cellpadding="0" cellspacing="0" border="0" style="width:640px;max-width:640px;">

<tr><td bgcolor="{DARK}" style="background:{DARK};padding:10px 24px;font-family:Oswald,Arial,sans-serif;font-weight:500;letter-spacing:0.08em;text-transform:uppercase;font-size:11px;color:#ffffff;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
<td>Confidentiel · équipes WITHIN &amp; Histoires de vies</td>
<td align="right" style="color:#FFB08F;">N°01 · 9 oct. 2026</td>
</tr></table>
</td></tr>

<tr><td align="center" bgcolor="{DARK}" style="background:{DARK};padding:8px 24px 14px;font-family:Outfit,Arial,sans-serif;font-size:12px;">
<a href="{ONLINE_URL}" style="color:#B9B8CC;text-decoration:underline;">Voir la version en ligne ↗</a>
</td></tr>

<tr><td bgcolor="#ffffff" class="px" style="background:#ffffff;border-bottom:1px solid {BORDER};padding:26px 24px 30px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
<td>
<span style="font-family:Outfit,Arial,sans-serif;font-weight:900;font-size:20px;color:{ACCENT};">WITHIN</span>
<span style="display:inline-block;width:1px;height:16px;background:{BORDER};margin:0 10px;"></span>
<span style="font-family:Outfit,Arial,sans-serif;font-weight:700;font-size:16px;color:{DARK};">Histoires de vies</span>
</td>
</tr></table>
<div class="h1" style="font-family:Outfit,Arial,sans-serif;font-weight:900;font-size:60px;line-height:0.95;letter-spacing:-0.02em;color:{DARK};margin-top:18px;border-top:3px solid {DARK};padding-top:18px;">
Private <span style="color:{ACCENT};">Newsletter</span>
</div>
<div style="font-family:Oswald,Arial,sans-serif;font-weight:500;letter-spacing:0.08em;text-transform:uppercase;font-size:13px;color:{ACCENT};margin-top:12px;">Spécial IA · Vidéo, image &amp; marketing</div>
<div style="font-family:Outfit,Arial,sans-serif;font-size:15px;color:{MUTED};margin-top:4px;">Veille juillet → septembre 2026</div>
</td></tr>

<tr><td class="px" style="padding:32px 24px 0;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#3A2A70" style="background:#3A2A70;border-radius:20px;">
<tr><td style="padding:32px;font-family:Outfit,Arial,sans-serif;">
<div style="font-family:Oswald,Arial,sans-serif;font-weight:500;letter-spacing:0.08em;text-transform:uppercase;font-size:12px;color:#D7F3F6;">À la une</div>
<div style="font-weight:800;font-size:28px;line-height:1.15;color:#ffffff;margin:10px 0 10px;">L'IA ne génère plus seulement des images : elle transforme nos rushes.</div>
<div style="font-size:15px;line-height:1.5;color:#E4F4F7;margin-bottom:16px;">14 outils, 2 exemples vidéo chacun. Cliquez sur une vignette pour voir la démo.</div>
<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr><td bgcolor="{ACCENT}" style="background:{ACCENT};border-radius:999px;">
<a href="{ONLINE_URL}" style="display:inline-block;padding:12px 22px;font-family:Outfit,Arial,sans-serif;font-weight:700;font-size:15px;color:#ffffff;text-decoration:none;">Découvrir en ligne ↗</a>
</td></tr></table>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:18px;">
{hero_grid}
</table>
</td></tr>
</table>
</td></tr>

<tr><td class="px" style="padding:36px 24px 0;">
<div style="font-family:Outfit,Arial,sans-serif;font-weight:800;font-size:22px;color:{DARK};margin-bottom:14px;">Au sommaire</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>{sommaire_cells}</tr></table>
</td></tr>

<tr><td class="px" style="padding:0;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
{rubrique_section('visuel')}
{rubrique_section('technique')}
{rubrique_section('plugins')}
</table>
</td></tr>

<tr><td class="px" style="padding:56px 24px 0;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="border-bottom:3px solid {ACCENT};padding-bottom:14px;margin-bottom:22px;">
<tr>
<td width="70" valign="bottom"><span style="font-family:Outfit,Arial,sans-serif;font-weight:800;font-size:56px;color:{ACCENT};line-height:0.8;">04</span></td>
<td valign="bottom">
<div style="font-family:Oswald,Arial,sans-serif;font-weight:500;letter-spacing:0.08em;text-transform:uppercase;font-size:12px;color:{MUTED};margin-bottom:4px;">Rubrique 04 · Le club</div>
<div style="font-family:Outfit,Arial,sans-serif;font-weight:800;font-size:26px;color:{DARK};">Vous avez aimé ? Rejoignez le club.</div>
</td>
</tr>
</table>

<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#2A1E5C" style="background:#2A1E5C;border-radius:20px;margin-bottom:16px;">
<tr><td style="padding:30px;font-family:Outfit,Arial,sans-serif;">
<div style="font-family:Oswald,Arial,sans-serif;font-weight:500;letter-spacing:0.08em;text-transform:uppercase;font-size:12px;color:#D7F3F6;">Abonnement · gratuit</div>
<div style="font-weight:800;font-size:26px;line-height:1.1;color:#ffffff;margin:10px 0;">Recevez le N°02 avant tout le monde.</div>
<div style="font-size:15px;line-height:1.5;color:#E4F4F7;margin-bottom:16px;">Enfin, avant les autres collègues. C'est gratuit, contrairement aux crédits Higgsfield.</div>
<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr><td bgcolor="#ffffff" style="background:#ffffff;border-radius:999px;">
<a href="{SUBSCRIBE_URL}" style="display:inline-block;padding:15px 26px;text-decoration:none;"><span style="font-family:Outfit,Arial,sans-serif;font-weight:800;font-size:17px;color:{DARK};">Je m'abonne au N°02 →</span></a>
</td></tr></table>
<div style="font-family:Outfit,Arial,sans-serif;font-size:12px;line-height:1.4;color:#D7F3F6;margin-top:14px;">Le bouton ne marche pas ? Copiez ce lien : <a href="{SUBSCRIBE_URL}" style="color:#ffffff;">{SUBSCRIBE_URL}</a></div>
</td></tr>
</table>

</td></tr>

<tr><td bgcolor="{DARK}" style="background:{DARK};padding:36px 24px;margin-top:40px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
<td>
<div style="font-family:Outfit,Arial,sans-serif;font-weight:900;font-size:22px;color:#ffffff;">Private <span style="color:#3BB8C4;">Newsletter</span> <span style="color:{ACCENT};">N°01</span></div>
<div style="font-family:Outfit,Arial,sans-serif;font-size:13px;color:#B9B8CC;margin-top:6px;">Cyril Hamel · Présentation du 9 octobre 2026 · Veille arrêtée au 23 septembre 2026</div>
<div style="font-family:Outfit,Arial,sans-serif;font-size:12px;color:#8886A3;margin-top:14px;">Vous recevez cet e-mail car vous êtes abonné·e à la Private Newsletter WITHIN × Histoires de vies.<br>
<a href="{ONLINE_URL}" style="color:#B9B8CC;">Voir en ligne</a> · <a href="mailto:{WERO_EMAIL}" style="color:#B9B8CC;">Se désabonner</a></div>
</td>
</tr></table>
</td></tr>

</table>
</td></tr>
</table>
</body>
</html>
'''



# ---------------------------------------------------------------- post-traitement
_CTA = re.compile(r'<a href="(https?://[^"]+)" style="display:inline-block;margin-top:10px;')
_IMG = re.compile(r'<img src="(https://cyrha\.github\.io/within-newsletter/assets/([a-f0-9]+)\.jpg)"[^>]*>')


def link_images(h):
    """Every image links to the same URL as the button of its own card."""
    mapping = {}
    for m in _IMG.finditer(h):            # later (card) occurrence overrides the hero mosaic
        c = _CTA.search(h, m.end())
        if c:
            mapping[m.group(2)] = c.group(1)
    h = re.sub(r'<a href="(https://cyrha\.github\.io/within-newsletter/assets/[a-f0-9]+\.jpg)" style="text-decoration:none;">',
               lambda m: '<a href="%s" style="text-decoration:none;">' % mapping[re.search(r'assets/([a-f0-9]+)\.jpg', m.group(1)).group(1)], h)
    out, pos = [], 0
    for m in _IMG.finditer(h):
        already = h[max(0, m.start() - 200):m.start()].rstrip().endswith('style="text-decoration:none;">')
        out.append(h[pos:m.start()])
        out.append(m.group(0) if already else '<a href="%s" style="text-decoration:none;">%s</a>' % (mapping[m.group(2)], m.group(0)))
        pos = m.end()
    out.append(h[pos:])
    return "".join(out)


def write(name, text):
    with open(os.path.join(ROOT, name), "w", encoding="utf-8") as f:
        f.write(text)
    print("ecrit %-11s %7d octets" % (name, len(text.encode("utf-8"))))


email = link_images(EMAIL)
write("email.html", email)

brevo = email.replace('href="%s"' % ONLINE_URL, 'href="{{ mirror }}"')
unsub = '<a href="mailto:%s" style="color:#B9B8CC;">Se désabonner</a>' % WERO_EMAIL
assert brevo.count(unsub) == 1, "lien de desabonnement introuvable"
brevo = brevo.replace(unsub, '<a href="{{ unsubscribe }}" style="color:#B9B8CC;">Se désabonner</a>')
write("brevo.html", brevo)


# ---------------------------------------------------------------- site (GitHub Pages)
def build_site():
    with open(SRC_HTML, encoding="utf-8") as f:
        html = f.read()
    html = re.sub(r"/_blob/([0-9a-f]{32})", lambda m: "assets/%s%s" % (m.group(1), EXT.get(m.group(1), ".jpg")), html)
    html = html.replace('<script src="./support.js"></script>\n', "")
    m = re.search(r"<helmet>(.*?)</helmet>", html, re.S)
    html = html.replace(m.group(0), "").replace("</head>", m.group(1) + "</head>")
    html = html.replace("<x-dc>\n", "").replace("</x-dc>", "")
    html = re.sub(r'<script type="text/x-dc".*?</script>\n?', "", html, flags=re.S)

    pill = ('style="text-decoration: none; color: #17162E; background: transparent; border: 1px solid #E3E2EA; '
            'border-radius: 999px; padding: 8px 16px; font-weight: 600; font-size: 15px;"')
    for i, (anchor, label) in enumerate((("visuel", "01 Visuel"), ("technique", "02 Technique"), ("plugins", "03 Plugins")), 1):
        old = ('<a href="#%s" style="text-decoration: none; color: {{ navColor%d }}; background: {{ navBg%d }}; '
               'border: 1px solid {{ navBorder%d }}; border-radius: 999px; padding: 8px 16px; font-weight: 600; '
               'font-size: 15px;">%s</a>') % (anchor, i, i, i, label)
        assert old in html, "nav " + anchor
        html = html.replace(old, '<a href="#%s" id="nav-%s" class="nav-pill" %s>%s</a>' % (anchor, anchor, pill, label))

    for key, i, bg, col, border in (("1", 1, "#F5F5F8", "#17162E", "#E3E2EA"), ("3", 3, "#F5F5F8", "#17162E", "#E3E2EA"),
                                    ("10", 10, "#F5F5F8", "#17162E", "#E3E2EA"), ("libre", "Libre", "#17162E", "#FFFFFF", "#17162E")):
        fn = "selectAmount" + str(i)
        old = ('<button type="button" onClick="{{ %s }}" style="cursor: pointer; font-family: inherit; background: {{ %s }}; '
               'color: %s; border: 2px solid {{ %s }}; border-radius: 16px; padding: 16px 12px; display: flex; '
               'flex-direction: column; gap: 4px; text-align: center; align-items: center; min-height: 44px;">') % (
                   fn, ("bg%s" % i), col, ("border%s" % i))
        assert old in html, "amount " + key
        html = html.replace(old, ('<button type="button" id="amt-%s" class="amt-btn" onclick="selectAmount(\'%s\')" '
                                  'style="cursor: pointer; font-family: inherit; background: %s; color: %s; border: 2px solid %s; '
                                  'border-radius: 16px; padding: 16px 12px; display: flex; flex-direction: column; gap: 4px; '
                                  'text-align: center; align-items: center; min-height: 44px;">') % (key, key, bg, col, border))

    old = 'onClick="{{ copyWero }}"'
    assert old in html
    html = html.replace(old, 'onclick="copyWero()"')
    old = ('style="border: 0; cursor: pointer; background: #E94E1B; color: #FFFFFF; font-family: inherit; font-weight: 700; '
           'font-size: 15px; padding: 10px 16px; border-radius: 999px; min-height: 44px;">{{ copyLabel }}<')
    assert old in html
    html = html.replace(old, old.replace("{{ copyLabel }}<", "Copier l’adresse<").replace('style="border: 0;', 'id="copyBtn" style="border: 0;', 1))
    old = '<span style="font-size: 13px; line-height: 1.4; color: #B9B8CC;">{{ stepHint }}</span>'
    assert old in html
    html = html.replace(old, '<span id="stepHint" style="font-size: 13px; line-height: 1.4; color: #B9B8CC;">'
                             'Choisissez un montant ci-dessus, puis Wero → envoyer → coller l’adresse ci-dessus.</span>')

    html = html.replace("</body>", SITE_JS + "</body>")
    assert "{{" not in html and "_blob" not in html, "placeholders restants"
    return html


SITE_JS = """<style>
.nav-pill.active{color:#FFFFFF !important;background:#17162E !important;border-color:#17162E !important}
.amt-btn.selected{background:#E94E1B !important;border-color:#E94E1B !important;color:#FFFFFF !important}
.amt-btn.selected span{color:#FFFFFF !important}
#amt-libre.selected{background:#E94E1B !important;border-color:#E94E1B !important}
</style>
<script>
function copyWero() {
  var btn = document.getElementById('copyBtn');
  var done = function () { btn.textContent = 'Copié !'; setTimeout(function(){ btn.textContent = 'Copier l\\u2019adresse'; }, 2000); };
  try { navigator.clipboard.writeText('cyril.hamel@within.fr').then(done, done); } catch (e) { done(); }
}
var AMOUNT_LABELS = { '1': '1 €', '3': '3 €', '10': '10 €', 'libre': 'du montant de votre choix' };
function selectAmount(key) {
  document.querySelectorAll('.amt-btn').forEach(function (b) { b.classList.remove('selected'); });
  document.getElementById('amt-' + key).classList.add('selected');
  document.getElementById('stepHint').textContent = 'Wero → envoyer ' + AMOUNT_LABELS[key] + " → coller l'adresse ci-dessus. C'est tout.";
}
(function () {
  var ids = ['visuel', 'technique', 'plugins'];
  var els = ids.map(function (id) { return document.getElementById(id); }).filter(Boolean);
  if (!els.length || !window.IntersectionObserver) return;
  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        document.querySelectorAll('.nav-pill').forEach(function (p) { p.classList.remove('active'); });
        var el = document.getElementById('nav-' + entry.target.id);
        if (el) el.classList.add('active');
      }
    });
  }, { rootMargin: '-20% 0px -70% 0px', threshold: 0 });
  els.forEach(function (el) { observer.observe(el); });
})();
</script>
"""

write("index.html", build_site())
