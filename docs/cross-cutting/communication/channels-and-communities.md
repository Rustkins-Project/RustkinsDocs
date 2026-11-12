---
id: DOC-0902
title: "Communication Rustkins — Médias et communautés"
type: cross-cutting
status: draft
summary: "Quatre supports de communication classés par priorité et guide de publication sur les sept subreddits retenus."
topics: [communication, social-media, reddit, community, outreach]
applies_to: [all]
---

# Communication Rustkins — Médias et communautés

## 1. Les quatre médias retenus, dans l'ordre

| Ordre | Média / support | Déclinaisons | Public et objectif |
| --- | --- | --- | --- |
| **1** | **Vidéos en formats courts** | **YouTube Shorts, Instagram Reels et TikTok** | Présenter Rustkins, vulgariser ou expliquer la CI/CD, montrer des démonstrations ; atteindre développeurs, DevOps, étudiants et curieux |
| **2** | **Reddit** | Communautés open source, DevOps, self-hosting, homelab, bêta-test | Trouver des testeurs, recueillir des retours techniques et installer un dialogue communautaire |
| **3** | **Site internet** | Site vitrine Rustkins en français et en anglais | Centraliser le positionnement, les fonctionnalités, la documentation, l'état du projet et les liens GitHub |
| **4** | **Salons open source** | RPLL, Open Source Experience ; veille sur les rencontres libristes, CNLL, Ploss-RA | Rencontrer utilisateurs, professionnels et contributeurs ; réaliser des démonstrations |

Le premier média désigne bien **trois plateformes de diffusion**, pas uniquement YouTube. Une production vidéo peut être déclinée et sous-titrée pour chacune.

Les salons sont une action à part entière du plan, même s'ils interviennent après les premières communications en ligne.

## 2. Formats courts : ligne éditoriale

- **Explicatif :** quel problème Rustkins résout, à quoi sert la CI/CD, pourquoi choisir l'auto-hébergement.
- **Technique :** configuration YAML, DAG, jobs Docker, logs, ressources et nouvelles fonctionnalités effectivement disponibles.
- **Grand public :** bénéfice concret de la souveraineté et du contrôle de l'infrastructure.
- **Témoignages et retours d'expérience de l'équipe :** raconter les difficultés que nous avons personnellement rencontrées avec des solutions CI/CD comme Jenkins et GitHub Actions, les frustrations qui ont motivé la création de Rustkins et les réponses que nous cherchons à apporter. S'appuyer sur des situations concrètes sans généraliser ces difficultés à tous les utilisateurs.

**Principes de diffusion :** vidéos verticales sous-titrées, versions françaises et anglaises selon les moyens, appels à l'action vers le site et le dépôt GitHub, rythme régulier mais tenable.

## 3. Reddit : communautés sélectionnées et règles à respecter

Les indications ci-dessous sont **la grille de préparation retenue par l'équipe**. Elles ne valent pas autorisation permanente de publier : relire les règles, fils épinglés et conditions de modération du subreddit le jour du post.

| Subreddit | Prérequis notés par l'équipe | Où et comment publier |
| --- | --- | --- |
| **r/alphaandbetausers** | Aucun prérequis identifié | Publication directe pour éprouver le pitch et le processus d'installation, puis demander des bêta-tests |
| **r/SideProject** | Aucun prérequis identifié | Publication directe sous la forme d'une présentation et d'une demande de retours |
| **r/devops** | **Uniquement dans le fil hebdomadaire d'autopromotion** | Présentation du projet et demande de retours dans ce fil, avec un lien clair vers le dépôt GitHub |
| **r/developpeurs** | Participation préalable ; lien vers le dépôt ; message en français et rédigé personnellement | Présentation du projet et demande de retours |
| **r/selfhosted** | En anglais ; documentation ; si le premier commit public date de moins de 3 mois, utiliser le megathread | Megathread dans ce cas ; sinon publication principale seulement avec une V0.x réellement « production ready » selon les critères du subreddit |
| **r/FOSS** | Licence libre requise | Publication directe **après les premiers retours**, en tenant compte de la modération commune évoquée avec r/opensource |
| **r/homelab** | Karma minimum ; flair « Project Showcase: Software » ; déclaration de l'usage de l'IA ; un mois de commits ; captures d'écran | Montrer le problème résolu, l'intérêt pour un homelab et pourquoi une solution FOSS existante ne répond pas au même besoin |

**Points de contrôle avant chaque publication :**

1. Vérifier que la licence publiée satisfait la définition attendue de « libre / FOSS », sans supposer qu'une licence a déjà été choisie.
2. Vérifier l'âge du dépôt / des commits publics et l'existence éventuelle d'un fil hebdomadaire ou megathread.
3. Préparer les ressources demandées : documentation d'installation testée, captures authentiques, lien du dépôt et état de maturité.
4. Écrire un message propre à la communauté, dans la langue attendue, avec déclaration d'usage de l'IA lorsque demandée.
5. Privilégier une question concrète (« L'installation fonctionne-t-elle chez vous ? ») plutôt qu'un message promotionnel générique.
6. Ne pas publier le même texte dans tous les subreddits en rafale ; respecter les règles d'autopromotion.
7. Après publication, répondre aux commentaires et orienter les anomalies reproductibles vers des issues GitHub.

## 4. Séquence de publication Reddit envisagée

1. **Valider le pitch et l'installation :** r/alphaandbetausers et r/SideProject dès qu'une version testable et documentée existe.
2. **Solliciter des avis techniques ciblés :** r/developpeurs et fil hebdomadaire r/devops, après participation conforme aux règles.
3. **Montrer une version plus mature :** r/selfhosted et r/homelab lorsque toutes les conditions de démonstration et de maturité sont réunies.
4. **Élargir la portée open source :** r/FOSS après les premiers retours et après publication d'une licence libre adaptée.

Cette séquence est **prévisionnelle**, conditionnée à la maturité du produit et aux règles des communautés.

## 5. Site vitrine et salons

**Site vitrine :** expliquer le produit, ses points forts, l'état des fonctionnalités, le modèle économique envisagé, les moyens de contribuer et les chemins de téléchargement/documentation. Prévoir deux langues ; ne pas afficher de prix ou d'offre contractuelle non arrêtés.

**Salons :** préparer un pitch oral court, une démonstration reproductible, un lien ou QR code vers le dépôt et un moyen de recueillir les retours. Les dates et les modalités de participation doivent être confirmées auprès des organisateurs.

## 6. Références

- [Positionnement et messages](positioning-and-messages.md)
- [Plan de lancement](launch-plan.md)
- [Script vidéo](promotional-video-script.md)
