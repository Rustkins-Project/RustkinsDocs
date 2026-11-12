---
id: DOC-0901
title: "Communication Rustkins — Positionnement et messages"
type: cross-cutting
status: draft
summary: "Punchline, proposition de valeur, publics cibles, trois sujets éditoriaux et garde-fous des messages publics Rustkins."
topics: [communication, positioning, messaging, open-source, self-hosting]
applies_to: [all]
---

# Communication Rustkins — Positionnement et messages

## 1. Objectif

Définir un discours de lancement clair et cohérent pour présenter Rustkins à ses premiers utilisateurs et contributeurs, puis à un public professionnel plus large.

**Statut :** proposition de communication à valider avant diffusion externe. Ce document n'atteste ni d'une mise sur le marché ni de fonctionnalités déjà livrées.

## 2. Punchline

> **Rustkins — Ne subissez plus votre CI/CD, maîtrisez-la !**

Phrase descriptive complémentaire :

> Rustkins est un projet de plateforme CI/CD open source, complète, sécurisée et auto-hébergeable, conçue pour redonner aux équipes la maîtrise de leur infrastructure et de leurs pipelines.

La punchline exprime le bénéfice utilisateur (reprendre le contrôle), tandis que la description explicite le domaine et la proposition de valeur.

## 3. Publics cibles

| Cible | Besoin principal | Message à privilégier |
| --- | --- | --- |
| Développeurs et petites équipes | Automatiser builds et tests sans complexité excessive | Fonctionnalités natives, couverture des besoins CI/CD et facilité d'utilisation |
| Ingénieurs DevOps / administrateurs systèmes | Maîtriser la plateforme, les exécutions et son exploitation | Auto-hébergement, gestion des ressources, observabilité |
| Communautés open source et homelab | Héberger et faire évoluer des outils sur leur propre infrastructure | Transparence, contributions, contrôle de l'installation |
| Entreprises et équipes techniques | Réduire la dépendance à des services hébergés tiers | Souveraineté de l'hébergement et possibilité de prestation et de support |

**Priorité de lancement :** communautés techniques susceptibles d'installer, de tester et de contribuer ; audience plus large dans un second temps.

## 4. Trois sujets pertinents à communiquer

| Sujet | Histoire / angle de communication | Exemple de contenu |
| --- | --- | --- |
| **1. Open source, souveraineté et sécurité de l'hébergement** | Pourquoi concevoir un moteur CI/CD qui s'installe sur l'infrastructure de l'utilisateur ? Comment la maîtrise de l'hébergement facilite-t-elle la gouvernance des exécutions et des données ? | « Pourquoi auto-héberger sa CI/CD ? » |
| **2. Plateforme complète et fonctionnalités natives** | Pourquoi concevoir un moteur CI/CD riche en fonctionnalités, intégrant nativement l'orchestration et les outils du quotidien, sans devoir multiplier les plugins ? | « Et si les fonctions essentielles de votre CI/CD étaient natives ? » |
| **3. Orchestration, ressources et évolution fonctionnelle** | Montrer concrètement la définition YAML, le DAG, les jobs Docker et la progression vers les workers distribués et le cache. | « Comment Rustkins orchestre un pipeline ? » |

Ces sujets peuvent aussi prendre la forme de récits de développement : problèmes rencontrés, arbitrages techniques, démonstrations de versions et retours des bêta-testeurs.

## 5. Positionnement concurrentiel sans surpromesse

- **Face aux services CI/CD hébergés**, comme GitHub Actions : promouvoir la maîtrise de l'hébergement et du plan de contrôle. Ne pas prétendre que GitHub Actions ne propose pas de runners auto-hébergés.
- **Face à Jenkins** : présenter l'ambition d'une plateforme complète, sécurisée et dotée de fonctionnalités natives ; ne pas affirmer que Jenkins dépend de plugins pour *toute* fonctionnalité ou que Rustkins est plus performant sans mesures.
- **Indépendance des forges Git** : avantage complémentaire, mais **pas le problème principal** du discours de lancement.
- **Sécurité** : l'auto-hébergement permet une gouvernance directe, mais ne garantit pas automatiquement une installation sécurisée ; la configuration, les mises à jour et l'isolation restent indispensables.

## 6. Règles de formulation

1. Distinguer visuellement et verbalement **disponible**, **en développement** et **prévu**.
2. Se référer à la [roadmap produit](../../versions/roadmap.md) : DAG et jobs Docker visés dès la V0, déclenchements automatisés et workers multiples en V1, cache et secrets complets en V2.
3. Ne pas annoncer des gains de performance, de sécurité ou de coût sans démonstration vérifiable.
4. Ne pas présenter la conformité RGPD ou la sécurité de l'hébergement comme automatiques.
5. Ne pas annoncer des prix, une licence précise ou des conditions premium non finalisées. Voir le [modèle économique](../business-model/business-model.md).
6. Adapter le niveau technique et la langue selon le support et la communauté.

## 7. Références internes

- [Roadmap fonctionnelle](../../versions/roadmap.md)
- [Modèle économique](../business-model/business-model.md)
- [Plan de lancement](launch-plan.md)
- [Médias et communautés](channels-and-communities.md)
- [Script de la vidéo promotionnelle](promotional-video-script.md)
