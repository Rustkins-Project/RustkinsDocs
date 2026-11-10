---
id: DOC-0101
title: "Modèle économique de Rustkins"
type: cross-cutting
status: draft
summary: "Modèle open source auto-hébergé, abonnement premium, déploiements payants sur infrastructure cliente et développements sur devis."
topics: [business-model, strategy, open-source, premium, support]
applies_to: [all]
---

# Modèle économique de Rustkins

## 1. Objet et statut

Ce document présente le **modèle économique retenu comme orientation par l'équipe** pour Rustkins, plateforme CI/CD auto-hébergée. Il sépare les décisions annoncées des modalités opérationnelles ou juridiques qui restent à préciser.

Il décrit une stratégie produit et commerciale, **pas** une offre contractuelle, un tarif publié, une licence logicielle ni une promesse de niveau de service. Les prix, les modalités exactes de souscription, les conditions des prestations ponctuelles et la faisabilité des fonctionnalités temporairement réservées ne sont pas encore déterminés.

## 2. Positionnement et proposition de valeur

Rustkins vise à fournir un moteur CI/CD que les équipes peuvent installer et exploiter sur leur propre infrastructure. Le produit met l'accent sur la maîtrise de l'environnement d'exécution : pipelines, workers, orchestration, logs, artifacts et évolutions du moteur au fil des versions.

La proposition de valeur repose sur trois principes :

1. **Liberté d'usage :** la plateforme de base est gratuite et distribuée en open source.
2. **Maîtrise de l'hébergement :** les utilisateurs déploient Rustkins sur leurs propres machines ou infrastructures ; l'entreprise Rustkins ne fournit pas d'instances SaaS hébergées.
3. **Accompagnement facultatif :** les équipes souhaitant un traitement prioritaire de leurs besoins peuvent souscrire une offre premium, sans rendre l'abonnement obligatoire pour exploiter le logiciel gratuit.
4. **Prestations ponctuelles :** l’équipe peut proposer, contre rémunération distincte, le déploiement de Rustkins sur les infrastructures des clients et la réalisation de fonctionnalités spécifiques majeures.

Le projet peut ainsi intéresser les développeurs, équipes techniques et organisations qui préfèrent conserver la gestion de leurs données, exécutions et ressources CI/CD sur leur infrastructure.

## 3. Décisions structurantes

| Dimension | Orientation retenue |
| --- | --- |
| Nature du produit | Plateforme CI/CD open source |
| Accès au logiciel | Gratuit |
| Hébergement des instances clientes | Auto-hébergement uniquement |
| SaaS exploité par Rustkins | Aucun |
| Revenus | Abonnements premium facultatifs, déploiements payants et développements spécifiques facturables |
| Support premium | Priorisation de corrections de bugs et échanges plus réguliers avec les abonnés |
| Déploiement assisté | Prestation payante d’installation et de configuration sur l’infrastructure du client, sans hébergement par Rustkins |
| Demandes de fonctionnalités | Possibilité pour les abonnés premium de solliciter des évolutions ; réalisation des plus grosses fonctionnalités éventuellement facturée en supplément |
| Disponibilité de certaines évolutions | Mécanisme temporaire envisagé pour les abonnés, de l'ordre de **trois mois**, à définir précisément |

La durée de trois mois est une **hypothèse indicative**, pas une durée contractuelle définitivement arrêtée.

## 4. Offre gratuite

### 4.1. Accès au produit

Le logiciel est utilisable sans abonnement et installé sous la responsabilité de l'utilisateur ou de son organisation. La distribution du code source et les conditions de modification et de redistribution dépendront de la **licence open source exacte**, non encore précisée dans ce document.

### 4.2. Exploitation et responsabilités

Les clients gèrent leurs installations : infrastructure, disponibilité, mises à jour, sauvegardes, exposition réseau, gestion des accès et conditions de sécurité propres à leur environnement.

Rustkins fournit un logiciel ; il ne prend pas automatiquement en charge la maintenance des serveurs des utilisateurs ni leurs traitements de données personnelles. L’installation initiale peut toutefois être réalisée **en prestation payante sur les infrastructures du client**, sans transfert de l’hébergement à Rustkins.

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

Les demandes courantes peuvent être étudiées en priorité dans le cadre de l'abonnement premium. **Une évolution majeure ou coûteuse peut faire l'objet d'une facturation supplémentaire**, même pour un client déjà abonné, après estimation et accord sur les conditions.

**Exemple :** un client demande une intégration d'**Azure DevOps** nécessitant un développement important. Rustkins peut proposer un devis spécifique en plus de l'éventuel abonnement premium. L'abonnement ne garantit donc pas la réalisation gratuite de toutes les fonctionnalités demandées.

La possibilité d'un développement financé fait partie du modèle économique ; aucun prix, garantie de livraison générale, exclusivité ou propriété exclusive du code n'est pour autant décidé. Périmètre, critères de livraison, délais et modalités de paiement restent à convenir pour chaque prestation.

### 5.4. Déploiement payant sur l'infrastructure du client

Rustkins peut proposer une **prestation ponctuelle d'installation et de déploiement**, facturée séparément, sur une infrastructure **fournie ou contrôlée par le client**. Le logiciel reste gratuit et auto-hébergé : le paiement rémunère le travail de l'équipe, pas une licence logicielle ni une offre SaaS.

Le périmètre de l'intervention pourra être défini par devis : vérification des prérequis, installation, configuration initiale, contrôles de bon fonctionnement et accompagnement éventuel à la prise en main. Rien de tout cela n'est inclus automatiquement tant que les modalités commerciales ne sont pas définies.

La supervision, les sauvegardes, la maintenance, les mises à jour et l'administration quotidienne demeurent de la responsabilité du client, sauf accord distinct. Les accès éventuellement nécessaires à l'installation doivent être limités dans le temps et sécurisés, notamment si des données personnelles peuvent être consultées.

## 6. Fonctionnalités temporairement disponibles pour les abonnés

L'équipe a évoqué la possibilité qu'une fonctionnalité demandée ou financée dans le cadre de l'offre premium bénéficie d'une **période d'accès privilégié**, par exemple **trois mois**, avant une disponibilité plus générale.

Pour les fonctionnalités de grande ampleur, **le client demandeur peut devoir financer spécifiquement tout ou partie du développement**, en supplément de son abonnement premium éventuel. C'est notamment le cas envisageable d'une intégration Azure DevOps nécessitant un chantier important. La tarification et la réalisation font alors l'objet d'un accord spécifique.

L'accès temporairement privilégié (au client financeur, aux abonnés premium ou aux deux) est une modalité distincte du financement ; **payer le développement ne confère pas automatiquement une exclusivité ni des droits sur le code**. La durée, le périmètre de l'accès et les conditions de publication doivent encore être arbitrés.

**Attention : les modalités exactes ne sont pas encore arbitrées.** En particulier, doivent être distinguées :
- priorité d'étude et de développement de la demande ;
- chiffrage et financement éventuel d’un développement spécifique, distincts de l’abonnement ;
- période éventuelle d’accès anticipé pour les abonnés et/ou le client financeur ;
- date et conditions de mise à disposition publique ;
- disponibilité du code source et licence applicable pendant cette période.

Il existe une tension à résoudre entre le souhait d'une plateforme **entièrement open source** et la possibilité de réserver l'utilisation ou la diffusion de certains éléments de code aux abonnés. Si du code est publié sous une licence open source permettant la redistribution, l'exclusivité commerciale de son accès ne peut pas être présumée.

Des solutions potentielles pourront être comparées (accès anticipé avant publication, modules distincts, mécénat de fonctionnalités, absence d'exclusivité), **sans les considérer comme choisies**. Toute option devra être validée techniquement, juridiquement et en regard des valeurs du projet.

## 7. Parcours client envisagé

Le parcours commercial cible, sans préjuger des outils techniques :

1. Une équipe découvre et installe Rustkins gratuitement sur son infrastructure.
2. Elle exploite la plateforme sans avoir besoin d'un abonnement ni d'un compte géré par l'éditeur pour l'exécution locale, sous réserve des choix d'implémentation futurs.
3. Si elle souhaite un accompagnement prioritaire, elle peut souscrire une offre premium. Si elle préfère déléguer l'installation initiale, elle peut commander **un déploiement payant sur sa propre infrastructure**, indépendamment de l'hébergement.
4. Elle communique ses anomalies ou demandes d'évolution par des canaux qui restent à choisir. Pour une fonctionnalité majeure, comme une intégration Azure DevOps, l'équipe peut proposer un **devis de développement supplémentaire**.
5. L'équipe Rustkins traite et suit les demandes conformément au niveau d'accompagnement réellement proposé.
6. Si un mécanisme d'accès anticipé aux fonctionnalités est adopté, son activation, sa durée et sa sortie devront être explicites.

Les étapes commerciales, la facturation et la vérification de l'abonnement restent à concevoir. La présente description est un **parcours cible**, pas un parcours fonctionnel déjà développé.

## 8. Sources de revenus et charges

### 8.1. Revenus envisagés

**Trois sources de revenus sont envisagées :**

1. **Abonnements premium facultatifs** : suivi renforcé, échanges plus réguliers, priorisation des corrections et étude de demandes.
2. **Déploiements payants ponctuels** : installation et configuration de Rustkins **sur l'infrastructure du client**, sans hébergement SaaS.
3. **Développements majeurs sur devis** : facturation additionnelle possible pour une fonctionnalité importante demandée par un client (ex. intégration Azure DevOps), même s'il possède un abonnement premium.

Ces prestations rémunèrent des services ou un travail de développement : elles ne rendent pas payant le logiciel de base. Aucun prix, périodicité de facturation, volume de clients, chiffre d'affaires ni objectif de rentabilité n'a été fixé. Ne pas produire de projections financières présentées comme acquises sur cette base.

### 8.2. Principaux postes de coût à prévoir

- Temps de développement du moteur, des interfaces, des correctifs et des tests.
- Temps de traitement des demandes et de communication avec les abonnés.
- Temps d'intervention sur les infrastructures clientes et de vérification des installations ponctuelles.
- Étude, estimation, développement, validation et maintenance éventuelle des fonctionnalités spécifiques financées.
- Infrastructure liée au projet lui-même : CI interne, démonstrations, documentation, distribution et outils communautaires.
- Administration de l'entreprise, facturation, gestion des abonnements, conformité et sécurité.

L'absence de SaaS client réduit certaines dépenses d'hébergement centralisé, mais ne supprime pas les coûts d'exploitation de l'entreprise et des outils de support.

## 9. Distribution, acquisition et communication

Les canaux exacts n'ont pas été arrêtés. La stratégie pourra exploiter la transparence du projet open source : dépôt de code, documentation d'installation et de contribution, démonstrations et communauté de développeurs.

Les messages commerciaux doivent séparer :
- ce qui est **actuellement livré** ;
- ce qui figure dans la **roadmap** ;
- ce qui relève de l’**offre premium prévue** ou de **prestations payantes distinctes** ;
- ce qui reste une **hypothèse**.

L'auto-hébergement peut être mis en avant comme facteur de maîtrise des infrastructures et des flux de données, sans promettre que toute installation de Rustkins serait automatiquement conforme au RGPD.

## 10. RGPD et implications du modèle

### 10.1. Pour les installations des clients

Les clients administrent leur instance. Les informations liées à l'utilisation du logiciel (comptes locaux, auteurs de commits, logs de jobs, etc.) peuvent être des données personnelles selon les cas. L'entreprise Rustkins n'en devient pas automatiquement destinataire du seul fait qu'elle édite le logiciel.

### 10.2. Pour l'activité de l'entreprise

La relation commerciale et le support peuvent entraîner des traitements propres à Rustkins : coordonnées de contacts, suivi des échanges, données relatives aux abonnements, etc. Ces activités doivent être inventoriées et documentées selon les traitements réellement réalisés.

### 10.3. Déploiements réalisés chez les clients

Une prestation ponctuelle d'installation peut nécessiter un accès temporaire aux machines ou configurations du client. Selon les conditions réelles, elle peut donner accès à des données personnelles : les mesures de confidentialité, de contrôle des accès, de traçabilité et les engagements contractuels appropriés devront être étudiés. Une telle intervention ne transforme pas automatiquement Rustkins en hébergeur ou exploitant permanent de l'instance cliente.

### 10.4. Services optionnels non décidés

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
| Déploiement payant confondu avec hébergement ou infogérance | Définir le périmètre de l'intervention et les responsabilités du client après livraison |
| Grosse fonctionnalité supposée incluse dans le premium | Prévoir un chiffrage et un accord séparés pour les développements facturables |
| Confusion entre auto-hébergement et absence de RGPD | Documenter séparément les responsabilités de l'éditeur et des exploitants |
| Fonctionnalités supplémentaires imposées par le dossier scolaire | Évaluer le bénéfice produit avant tout développement |
| Abonnement facultatif ne finançant pas durablement le support | Chiffrer charges et hypothèses après étude |
| Communication laissant entendre que tout est déjà livré | Maintenir des descriptions conformes aux versions et aux états de réalisation |

## 12. Décisions à prendre ultérieurement

1. Choisir la licence open source et la politique de publication du code.
2. Définir précisément le contenu de l'offre premium, son prix et sa facturation.
3. Définir le périmètre, les tarifs, la facturation et les responsabilités des prestations de déploiement sur infrastructure cliente.
4. Clarifier les demandes incluses dans l'abonnement et les évolutions majeures pouvant être facturées séparément sur devis.
5. Décider si un accès temporairement privilégié (environ trois mois) est pertinent et juridiquement cohérent, y compris pour les fonctionnalités financées par un client.
6. Organiser les canaux de support et les règles de priorisation sans accès distant par défaut.
7. Décider si la télémétrie, l'assistance distante ou le modèle de confidentialité intégré apportent une valeur suffisante pour être développés.

**Principe de pilotage :** ne pas faire passer une piste commerciale ou RGPD pour une fonctionnalité décidée ; documenter chaque arbitrage avant d'en déduire des contrats, tarifs ou adaptations de l'architecture.
