---
id: DOC-0102
title: "Présentation du projet Rustkins"
type: cross-cutting
status: draft
summary: "Problématique, proposition de valeur, fonctionnement et trajectoire produit de Rustkins pour le dossier entrepreneurial."
topics: [entrepreneurship, company, product, ci-cd, positioning]
applies_to: [all]
---

# Présentation du projet Rustkins

> **Nature du document :** volet « Présentation du projet » du dossier entrepreneurial. Il décrit la vision et le produit visé ; la roadmap ne constitue pas une preuve de fonctionnalités déjà commercialisées.

## 1. Synthèse du projet

**Rustkins est un projet de plateforme d'intégration et de déploiement continus (CI/CD), open source et auto-hébergée.** Son ambition est de permettre aux équipes de développement d'automatiser les étapes de construction, de test et, à terme, de déploiement de leurs applications, tout en conservant la maîtrise de l'infrastructure qui exécute ces opérations.

Un utilisateur décrit son pipeline dans un fichier YAML associé à son dépôt Git. Rustkins interprète cette configuration, ordonne les tâches selon leurs dépendances, les exécute dans des conteneurs et rend consultables les résultats, les statuts et les journaux d'exécution.

Le modèle prévu est **un logiciel de base gratuit, installé sur l'infrastructure de l'utilisateur**. L'équipe Rustkins envisage de se rémunérer par des services complémentaires, et non par l'hébergement d'une plateforme SaaS pour les clients. Voir [le modèle économique de référence](../business-model/business-model.md).

## 2. Problématique et opportunité

L'intégration continue consiste à automatiser des vérifications régulières du code ; le déploiement continu vise à fiabiliser sa mise en service. Ces pratiques nécessitent une chaîne outillée, une capacité de calcul et une visibilité sur les échecs.

Rustkins répond à un **besoin ciblé envisagé** : celui d'équipes qui souhaitent exploiter elles-mêmes leur moteur CI/CD et conserver la maîtrise de leurs ressources d'exécution, configurations et données associées. Le projet cherche à leur proposer un outil compréhensible, installable dans leur environnement et évolutif selon la taille de l'équipe.

Ce besoin est une **hypothèse de marché à valider** auprès de futurs utilisateurs. Les documents internes ne démontrent à ce stade ni un volume de demande ni un avantage comparatif mesuré par rapport aux solutions existantes.

## 3. Publics visés et usages

| Public cible envisagé | Situation d'usage | Valeur recherchée |
| --- | --- | --- |
| Développeurs indépendants et projets personnels | Construire et tester automatiquement un dépôt Git | Un moteur CI reproductible sur une infrastructure maîtrisée |
| Petites équipes de développement | Déclencher des pipelines à chaque modification et partager les résultats | Visibilité collective sur l'état des builds, tests et artifacts |
| Équipes techniques disposant de serveurs propres | Exploiter une chaîne CI/CD sur leurs machines, VM ou clusters | Contrôle de l'exécution, de la capacité et de l'exploitation |
| Organisations ayant des besoins d'intégration spécifiques | Ajouter des capacités ou connecter leur environnement existant | Possibilité d'accompagnement et de développements sur devis |

Il s'agit de **segments à tester**, non de clients acquis ou d'engagements commerciaux déjà signés.

Pour le lancement commercial, le [business plan](../business-model/business-plan.md) cible en priorité les PME et petites équipes techniques françaises qui auto-hébergent déjà leur CI/CD.

## 4. Proposition de valeur

Les principes qui structurent le projet sont les suivants :

1. **Maîtrise de l'hébergement :** les pipelines s'exécutent sur l'infrastructure de l'utilisateur, sans instance SaaS opérée par Rustkins.
2. **Accès gratuit au moteur :** l'ambition est de rendre la plateforme de base réellement exploitable sans abonnement.
3. **Automatisation déclarative :** configuration versionnée en YAML, jobs et dépendances décrits explicitement.
4. **Transparence d'exécution :** historique des runs, statuts, logs et, selon la version, artifacts consultables.
5. **Progressivité :** une V0 volontairement limitée précède le travail collaboratif, la distribution et les fonctions avancées.
6. **Accompagnement optionnel :** support prioritaire, aide au déploiement et développements spécifiques envisagés comme prestations payantes distinctes.

La valeur recherchée n'implique **ni promesse d'absence de coûts d'infrastructure, ni conformité de sécurité automatique, ni supériorité démontrée** sur les outils concurrents.

## 5. Fonctionnement du produit

```mermaid
flowchart LR
    A["Dépôt Git et pipeline YAML"] --> B["API Rustkins"]
    B --> C["Scheduler / graphe des jobs"]
    C --> D["Workers"]
    D --> E["Conteneurs Docker"]
    E --> F["Statuts et logs"]
    F --> G["Interface Rustkins"]
```

Au niveau fonctionnel :

1. Le développeur associe son dépôt Git à un projet Rustkins.
2. Une configuration YAML décrit les jobs à réaliser et leurs dépendances.
3. Le moteur valide cette configuration et prépare un graphe d'exécution (DAG).
4. Le scheduler détermine quels jobs peuvent démarrer ; les workers lancent les conteneurs Docker correspondants.
5. Les résultats et journaux sont conservés et rendus accessibles depuis l'interface.

**Attention au périmètre :** en V0, le déclenchement est manuel et les dépôts sont publics. Les webhooks Git, les comptes d'équipe, les logs en temps réel et les artifacts font partie de la V1 ; les secrets complets, le cache, les services auxiliaires et Kubernetes sont prévus pour la V2. Le schéma résume l'architecture visée et ne certifie pas un état de livraison.

## 6. Trajectoire de développement

| Version du produit | Finalité | Capacités caractéristiques prévues |
| --- | --- | --- |
| **V0 — Moteur CI local** | Prouver une exécution de bout en bout | Dépôt public, YAML, DAG, jobs Docker, logs persistés, interface de suivi, déploiement mononœud |
| **V1 — Usage en équipe** | Rendre le moteur utilisable collectivement | Authentification et rôles, webhooks, plusieurs workers, annulation, logs temps réel, artifacts |
| **V2 — CI/CD distribuée** | Élargir les usages de production | Secrets, isolation avancée, cache, services/sidecars, matrix, reprise après incident, déploiements Swarm/Kubernetes |
| **V3 — Plateforme avancée** | Simplifier et optimiser l'expérience | Registry, templates, bibliothèque de jobs, indicateurs et optimisation, gestion avancée des ressources |

**V0 à V3 sont des versions du produit ; elles ne doivent pas être confondues avec les versions du format YAML.** Les échéances et l'avancement réel sont suivis dans les référentiels opérationnels du projet, pas déduits de ce tableau.

Le scénario commercial prévoit une bêta V1 au premier semestre 2027, une V2 commercialisable en juillet et une V3 en fin d'année. Le prévisionnel anticipe l'effet de la V3 sur les ventes à partir de 2028.

## 7. Positionnement et différenciation recherchée

Rustkins se positionne dans l'univers des outils CI/CD, où existent déjà des solutions intégrées aux forges Git et des moteurs auto-hébergés. Son axe stratégique **envisagé** est l'association d'un moteur gratuit et open source, d'un hébergement sous contrôle utilisateur et d'une offre de services facultative.

La différenciation reste à démontrer par des tests d'installation, des retours d'équipes pilotes et une comparaison documentée des coûts, de la maintenance et de l'expérience d'usage. L'auto-hébergement ne supprime pas les responsabilités de sécurité et d'administration de l'exploitant.

## 8. Critères de réussite à vérifier

Pour transformer la vision en produit démontrable, l'équipe pourra suivre :

- **Fonctionnement :** capacité à déclencher un pipeline de référence et à obtenir un résultat reproductible.
- **Fiabilité :** qualité des transitions d'état, reprise sur erreurs prévues et absence de jobs exécutés en double.
- **Expérience utilisateur :** facilité d'installation, lisibilité des logs et du diagnostic d'échec.
- **Adoption :** nombre d'installations pilotes réellement actives et retours qualitatifs des équipes utilisatrices.
- **Viabilité :** coût de maintenance et de support comparé aux revenus de services, une fois des données réelles disponibles.

Aucune valeur chiffrée ou résultat d'expérimentation n'est affirmé à ce stade.

## 9. Références internes

- [Roadmap fonctionnelle](../../versions/roadmap.md)
- [V0 — Récapitulatif détaillé](../../versions/v0/overview.md)
- [V1 — Récapitulatif détaillé](../../versions/v1/overview.md)
- [Modèle économique](../business-model/business-model.md)
- [Structure de l'équipe et de l'entreprise envisagée](company-structure.md)
