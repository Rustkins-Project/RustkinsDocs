---
id: DOC-0105
title: "Direction artistique de Rustkins"
type: cross-cutting
status: draft
summary: "Identité de marque, valeurs, univers visuel minimaliste, principes des thèmes clair et sombre et applications de la direction artistique Rustkins."
topics: [art-direction, brand, design, interface, communication]
applies_to: [all]
---

# Direction artistique de Rustkins

## 1. Objet et statut

Ce document définit l'**intention artistique de Rustkins** pour le produit et ses supports de communication. Il fixe une orientation commune, **sans constituer une charte graphique détaillée** : les références de couleurs, les typographies définitives, le logo et ses règles d'emploi ne sont pas arrêtés ici.

**Statut :** proposition de direction artistique à valider par l'équipe. Les références citées servent d'inspiration, pas de modèles à reproduire à l'identique.

## 2. Identité de marque et positionnement visuel

Rustkins est un **projet de plateforme CI/CD open source, auto-hébergeable et indépendante des forges Git**. Son identité doit être cohérente avec sa vocation : redonner aux équipes la maîtrise de leurs pipelines et de leur infrastructure d'exécution.

La direction artistique retenue est **moderne, technique, minimaliste et professionnelle**. Elle s'inspire de la sobriété de GitHub Actions et de l'approche fonctionnelle de Jenkins, tout en développant une identité propre à Rustkins.

Le principe directeur est de **rendre la complexité technique compréhensible, sans la faire subir à l'utilisateur**. L'esthétique doit soutenir la lecture des informations et des workflows, plutôt que détourner l'attention de leur usage.

## 3. Valeurs à transmettre

| Valeur | Traduction visuelle et éditoriale |
| --- | --- |
| **Maîtrise** | Interfaces structurées, états explicites, visualisation claire de l'exécution |
| **Indépendance** | Identité propre, sans reprendre le langage visuel d'une forge Git particulière |
| **Transparence** | Informations lisibles, vues de pipelines, logs et statuts compréhensibles |
| **Fiabilité** | Hiérarchie stable, cohérence des composants et sobriété des effets |
| **Performance** | Parcours directs et impression d'efficacité, **sans revendiquer de gains chiffrés non mesurés** |

L'identité doit inspirer confiance sans multiplier les codes visuels futuristes ou les promesses techniques non démontrées.

## 4. Univers visuel

### 4.1. Couleurs et ambiance

La palette repose principalement sur des **tons neutres** : gris anthracite, gris intermédiaires et blanc cassé. Le **noir pur et le blanc pur sont écartés** pour éviter les contrastes inutilement agressifs.

Un **bleu clair** sert d'accent visuel pour identifier les éléments importants, les actions prioritaires et les points de repère de la marque. Il doit rester mesuré pour conserver la sobriété de l'ensemble.

À titre **illustratif uniquement**, les couleurs suivantes traduisent cette intention :

| Rôle envisagé | Exemple indicatif |
| --- | --- |
| Fond sombre anthracite | `#181B20` |
| Fond clair blanc cassé | `#F3F5F7` |
| Accent bleu clair | `#75C9F1` |

Ces références **ne figent pas une charte graphique**. Leurs déclinaisons et leurs contrastes seront vérifiés dans les maquettes, notamment pour les textes et contrôles interactifs.

### 4.2. Typographie et composition

- **Typographie :** sans empattement, contemporaine et très lisible ; une police monospace pour les logs, commandes et extraits YAML.
- **Mise en page :** grilles rigoureuses, alignements cohérents, espacements réguliers et densité d'information maîtrisée.
- **Iconographie :** icônes simples et géométriques, explicites plutôt que décoratives.
- **Éléments graphiques :** pipelines, graphes de dépendances (DAG), jobs, conteneurs et flux d'exécution.
- **Effets :** animations discrètes et utiles au retour d'état ; éviter les dégradés envahissants, les illustrations génériques et les ornements superflus.

### 4.3. Thèmes clair et sombre

**Rustkins proposera un thème clair et un thème sombre.** Les deux doivent partager la même hiérarchie visuelle, les mêmes composants et le même accent bleu clair, avec des surfaces et niveaux de contraste adaptés à chacun.

Le thème sombre ne reposera pas sur un fond noir pur ; le thème clair n'utilisera pas de blanc pur comme couleur dominante. Les composants devront rester lisibles et confortables dans les deux modes.

## 5. Principes d'expérience et d'interface

L'interface doit placer au premier plan les besoins des développeurs et des équipes DevOps : **comprendre un pipeline, suivre les exécutions, retrouver un échec et consulter les logs**.

Les choix visuels privilégient :

- des listes et tableaux structurés, avec une hiérarchisation nette des informations ;
- des graphes de pipelines compréhensibles et des relations entre jobs faciles à suivre ;
- des vues de détail lisibles pour les exécutions, étapes et journaux ;
- des interactions prévisibles et une navigation sans surcharge ;
- des **statuts clairement différenciés** (en attente, en cours, succès, échec, etc.) par **libellé, icône et couleur fonctionnelle**, sans dépendre de la couleur seule.

Les couleurs de statut (par exemple réussite ou échec) ont un rôle fonctionnel distinct de l'accent bleu de la marque. Leur définition précise relève des travaux d'interface et d'accessibilité.

## 6. Applications de l'identité

La direction artistique constitue un langage visuel commun pour :

| Support | Application souhaitée |
| --- | --- |
| **Interface Rustkins** | Tableaux, détails de runs, DAG, logs et statuts lisibles en clair comme en sombre |
| **Site vitrine** | Présentation sobre des bénéfices, captures d'interface et parcours de découverte directs |
| **Documentation** | Typographie cohérente, schémas simples, exemples YAML et captures commentées |
| **Supports de communication** | Messages courts, démonstrations concrètes, visuels techniques homogènes |

La communication privilégiera les **captures d'interface, schémas et démonstrations réelles** plutôt que des images génériques. Son ton sera **direct, technique mais accessible**, centré sur les bénéfices utilisateurs.

Cette identité accompagne la punchline du projet :

> **Rustkins — Ne subissez plus votre CI/CD, maîtrisez-la !**

Le bleu clair et les représentations de pipelines pourront devenir des signes de reconnaissance récurrents, sans sacrifier la simplicité des supports.

## 7. Références internes

- [Positionnement et messages de communication](../communication/positioning-and-messages.md)
- [Plan de communication et lancement](../communication/README.md)
- [Roadmap fonctionnelle](../../versions/roadmap.md)
- [Modèle économique](../business-model/business-model.md)
