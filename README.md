# WITHIN × Histoires de vies — Private Newsletter

Source unique : l'artefact Claude Design (`source/Main.dc.html`). Tout le reste est généré.

```
source/Main.dc.html ──build.py──▶ index.html  (site GitHub Pages)
                                  email.html  (test / copier-coller)
                                  brevo.html  (envoi via Brevo)
```

## Nouvelle édition

1. Retravailler la newsletter dans l'artefact (Cowork).
2. Récupérer le fichier `project/Main.dc.html` de l'artefact → `source/Main.dc.html`,
   et les nouvelles images (`/_blob/<id>`) → `assets/<id>.jpg`.
3. `python3 build.py` (échoue si une image manque dans `assets/`).
4. Vérifier `email.html` dans un navigateur, puis commit + push (met le site à jour).
5. Créer le brouillon Brevo à partir de `brevo.html` (via le connecteur Brevo dans Claude,
   ou en collant le code dans Brevo > Code HTML personnalisé), envoyer un test, puis envoyer.

## Points d'attention

- `brevo.html` contient `{{ mirror }}` (version en ligne Brevo) et `{{ unsubscribe }}` (désabonnement).
- La section paiement (Wero) est sur le site (`index.html`) mais volontairement absente du mail.
- Le lien d'abonnement est encore un formulaire Jotform (`SUBSCRIBE_URL` dans `build.py`).
- Coller dans Airmail : utiliser le mode **HTML** et coller le code source, pas le rendu (sinon les liens sont réécrits).
- Le repo est public : ne rien y mettre de confidentiel.
