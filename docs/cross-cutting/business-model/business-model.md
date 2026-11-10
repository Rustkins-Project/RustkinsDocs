---
id: DOC-0101
title: "Modèle économique de Rustkins"
type: cross-cutting
status: draft
summary: "Modèle économique open source auto-hébergé, gratuité du logiciel, revenus premium et arbitrages non encore définis."
topics: [business-model, strategy, open-source, premium, support]
applies_to: [all]
---

# Modèle économique de Rustkins

## 1. Objet et statut

Ce document présente le **modèle économique retenu comme orientation par l'équipe** pour Rustkins, plateforme CI/CD auto-hébergée. Il sépare les décisions annoncées des modalités opérationnelles ou juridiques qui restent à préciser.

Il décrit une stratégie produit et commerciale, **pas** une offre contractuelle, un tarif publié, une licence logicielle ni une promesse de niveau de service. Les prix, les modalités exactes de souscription et la faisabilité des fonctionnalités temporairement réservées ne sont pas encore déterminés.

## 2. Positionnement et proposition de valeur

Rustkins vise à fournir un moteur CI/CD que les équipes peuvent installer et exploiter sur leur propre infrastructure. Le produit met l'accent sur la maîtrise de l'environnement d'exécution : pipelines, workers, orchestration, logs, artifacts et évolutions du moteur au fil des versions.

La proposition de valeur repose sur trois principes :

1. **Liberté d'usage :** la plateforme de base est gratuite et distribuée en open source.
2. **Maîtrise de l'hébergement :** les utilisateurs déploient Rustkins sur leurs propres machines ou infrastructures ; l'entreprise Rustkins ne fournit pas d'instances SaaS hébergées.
3. **Accompagnement facultatif :** les équipes souhaitant un traitement prioritaire de leurs besoins peuvent souscrire une offre premium, sans rendre l'abonnement obligatoire pour exploiter le logiciel gratuit.

Le projet peut ainsi intéresser les développeurs, équipes techniques et organisations qui préfèrent conserver la gestion de leurs données, exécutions et ressources CI/CD sur leur infrastructure.

## 3. Décisions structurantes

| Dimension | Orientation retenue |
| --- | --- |
| Nature du produit | Plateforme CI/CD open source |
| Accès au logiciel | Gratuit |
| Hébergement des instances clientes | Auto-hébergement uniquement |
| SaaS exploité par Rustkins | Aucun |
| Revenus | Abonnement premium facultatif |
| Support premium | Priorisation de corrections de bugs et échanges plus réguliers avec les abonnés |
| Demandes de fonctionnalités | Possibilité pour les abonnés premium de solliciter des évolutions |
| Disponibilité de certaines évolutions | Mécanisme temporaire envisagé pour les abonnés, de l'ordre de **trois mois**, à définir précisément |

La durée de trois mois est une **hypothèse indicative**, pas une durée contractuelle définitivement arrêtée.

## 4. Offre gratuite

### 4.1. Accès au produit

Le logiciel est utilisable sans abonnement et installé sous la responsabilité de l'utilisateur ou de son organisation. La distribution du code source et les conditions de modification et de redistribution dépendront de la **licence open source exacte**, non encore précisée dans ce document.

### 4.2. Exploitation et responsabilités

Les clients gèrent leurs installations : infrastructure, disponibilité, mises à jour, sauvegardes, exposition réseau, gestion des accès et conditions de sécurité propres à leur environnement.

Rustkins fournit un logiciel ; il ne prend pas automatiquement en charge la maintenance des serveurs des utilisateurs ni leurs traitements de données personnelles.

### 4.3. Périmètre du gratuit

L'ambition est que l'utilisation de la plateforme gratuite demeure réellement viable, sans imposer un abonnement pour exécuter des pipelines. Les fonctionnalités disponibles dépendent du cycle de développement V0, V1, V2 et V3 documenté dans la [roadmap](../../versions/roadmap.md) : l'existence d'une fonctionnalité dans la roadmap ne signifie pas qu'elle est déjà livrée.

Les éventuelles restrictions temporaires d'accès à certaines nouveautés sont discutées à part (section 6), car elles doivent être conciliées avec l'engagement open source.

## 5. Offre premium et relation client

### 5.1. Objectif

L'abonnement premium finance le développement, la correction du produit et une relation plus suivie avec les organisations qui souhaitent soutenir Rustkins et faire remonter leurs besoins de façon prioritaire.

Il s'ajoute à la distribution gratuite ; il ne correspond pas à une location d'instance hébergée par Rustkins.

### 5.2. Support prioritaire

Le support premium est principalement conçu comme un **canal de communication plus direct et régulier** et une **priorisation des corrections de bugs** portés à la connaissance de l'équipe.

Ce support **n'implique pas par défaut** :
- une prise en main à distance de l'installation cliente ;
- un accès permanent aux machines, aux logs ou aux dépôts de code ;
- une administration déléguée de l'environnement ;
- une garantie contractuelle de délai de réponse ou de résolution, sauf engagement défini ultérieurement.

Pour rendre cette promesse vérifiable, l'équipe devra préciser le canal d'échange, les règles de priorisation, les niveaux de gravité et le fonctionnement en cas d'incident touchant plusieurs clients. Aucun niveau de service chiffré n'est fixé à ce stade.

### 5.3. Demandes d'évolutions

Les abonnés pourraient proposer ou demander des fonctionnalités, avec une prise en compte prioritaire par l'équipe. Il reste à distinguer clairement :
- **demande étudiée en priorité** : l'équipe analyse et planifie éventuellement la demande ;
- **fonctionnalité commandée** : engagement sur un périmètre, un délai et une livraison.

Seule la première approche est cohérente avec les décisions actuellement décrites ; aucune promesse de développement à la demande, de livraison garantie ou de propriété exclusive du code n'a été décidée.

## 6. Fonctionnalités temporairement disponibles pour les abonnés

L'équipe a évoqué la possibilité qu'une fonctionnalité demandée ou financée dans le cadre de l'offre premium bénéficie d'une **période d'accès privilégié**, par exemple **trois mois**, avant une disponibilité plus générale.

**Attention : les modalités exactes ne sont pas encore arbitrées.** En particulier, doivent être distinguées :
- priorité d'étude et de développement de la demande ;
- période éventuelle d'accès anticipé pour les abonnés ;
- date et conditions de mise à disposition publique ;
- disponibilité du code source et licence applicable pendant cette période.

Il existe une tension à résoudre entre le souhait d'une plateforme **entièrement open source** et la possibilité de réserver l'utilisation ou la diffusion de certains éléments de code aux abonnés. Si du code est publié sous une licence open source permettant la redistribution, l'exclusivité commerciale de son accès ne peut pas être présumée.

Des solutions potentielles pourront être comparées (accès anticipé avant publication, modules distincts, mécénat de fonctionnalités, absence d'exclusivité), **sans les considérer comme choisies**. Toute option devra être validée techniquement, juridiquement et en regard des valeurs du projet.

## 7. Parcours client envisagé

Le parcours commercial cible, sans préjuger des outils techniques :

1. Une équipe découvre et installe Rustkins gratuitement sur son infrastructure.
2. Elle exploite la plateforme sans avoir besoin d'un abonnement ni d'un compte géré par l'éditeur pour l'exécution locale, sous réserve des choix d'implémentation futurs.
3. Si elle souhaite un accompagnement prioritaire, elle souscrit une offre premium auprès de l'entreprise.
4. Elle communique ses anomalies ou demandes d'évolution par des canaux qui restent à choisir.
5. L'équipe Rustkins traite et suit les demandes conformément au niveau d'accompagnement réellement proposé.
6. Si un mécanisme d'accès anticipé aux fonctionnalités est adopté, son activation, sa durée et sa sortie devront être explicites.

Les étapes commerciales, la facturation et la vérification de l'abonnement restent à concevoir. La présente description est un **parcours cible**, pas un parcours fonctionnel déjà développé.

## 8. Sources de revenus et charges

### 8.1. Revenus envisagés

**Source principale identifiée :** abonnements premium facultatifs.

Aucun prix, périodicité de facturation, formule commerciale, volume de clients, chiffre d'affaires ni objectif de rentabilité n'a encore été fixé. Ne pas produire de projections financières présentées comme acquises sur cette base.

### 8.2. Principaux postes de coût à prévoir

- Temps de développement du moteur, des interfaces, des correctifs et des tests.
- Temps de traitement des demandes et de communication avec les abonnés.
- Infrastructure liée au projet lui-même : CI interne, démonstrations, documentation, distribution et outils communautaires.
- Administration de l'entreprise, facturation, gestion des abonnements, conformité et sécurité.

L'absence de SaaS client réduit certaines dépenses d'hébergement centralisé, mais ne supprime pas les coûts d'exploitation de l'entreprise et des outils de support.

## 9. Distribution, acquisition et communication

Les canaux exacts n'ont pas été arrêtés. La stratégie pourra exploiter la transparence du projet open source : dépôt de code, documentation d'installation et de contribution, démonstrations et communauté de développeurs.

Les messages commerciaux doivent séparer :
- ce qui est **actuellement livré** ;
- ce qui figure dans la **roadmap** ;
- ce qui relève de l'**offre premium prévue** ;
- ce qui reste une **hypothèse**.

L'auto-hébergement peut être mis en avant comme facteur de maîtrise des infrastructures et des flux de données, sans promettre que toute installation de Rustkins serait automatiquement conforme au RGPD.

## 10. RGPD et implications du modèle

### 10.1. Pour les installations des clients

Les clients administrent leur instance. Les informations liées à l'utilisation du logiciel (comptes locaux, auteurs de commits, logs de jobs, etc.) peuvent être des données personnelles selon les cas. L'entreprise Rustkins n'en devient pas automatiquement destinataire du seul fait qu'elle édite le logiciel.

### 10.2. Pour l'activité de l'entreprise

La relation commerciale et le support peuvent entraîner des traitements propres à Rustkins : coordonnées de contacts, suivi des échanges, données relatives aux abonnements, etc. Ces activités doivent être inventoriées et documentées selon les traitements réellement réalisés.

### 10.3. Services optionnels non décidés

Des pistes ont été abordées lors du [point RGPD du 9 novembre 2026](../gdpr/meeting-notes/2026-11-09-rgpd-meeting.md) :
- support avec prise en main à distance ;
- télémétrie ou analytics remontés à l'éditeur, idéalement anonymisés ;
- modèle personnalisable de politique de confidentialité pour les entreprises utilisatrices.

Il ne s'agit pas de fonctionnalités vendues ou promises. Si elles sont adoptées, leur utilité, la répartition des responsabilités, leurs données et les mesures nécessaires devront être analysées avant implémentation.

## 11. Risques et contraintes à maîtriser

| Risque | Conséquence ou réponse à étudier |
| --- | --- |
| Promesse open source incompatible avec une exclusivité de certaines fonctionnalités | Fixer la licence et le mécanisme réel d'accès anticipé avant commercialisation |
| Support prioritaire mal défini | Formaliser canal, périmètre et règles de priorité, sans SLA inventé |
| Confusion entre auto-hébergement et absence de RGPD | Documenter séparément les responsabilités de l'éditeur et des exploitants |
| Fonctionnalités supplémentaires imposées par le dossier scolaire | Évaluer le bénéfice produit avant tout développement |
| Abonnement facultatif ne finançant pas durablement le support | Chiffrer charges et hypothèses après étude |
| Communication laissant entendre que tout est déjà livré | Maintenir des descriptions conformes aux versions et aux états de réalisation |

## 12. Décisions à prendre ultérieurement

1. Choisir la licence open source et la politique de publication du code.
2. Définir précisément le contenu de l'offre premium, son prix et sa facturation.
3. Clarifier le traitement des demandes de fonctionnalités et les engagements éventuellement associés.
4. Décider si un accès temporairement privilégié (environ trois mois) est pertinent et juridiquement cohérent.
5. Organiser les canaux de support et les règles de priorisation sans accès distant par défaut.
6. Décider si la télémétrie, l'assistance distante ou le modèle de confidentialité intégré apportent une valeur suffisante pour être développés.

**Principe de pilotage :** ne pas faire passer une piste commerciale ou RGPD pour une fonctionnalité décidée ; documenter chaque arbitrage avant d'en déduire des contrats, tarifs ou adaptations de l'architecture.
