---
id: DOC-0102
title: "Document de compréhension des attentes RGPD — Rustkins"
type: cross-cutting
status: draft
summary: "Compréhension globale des attentes RGPD : démarche interne de Rustkins, protection intégrée au logiciel, responsabilités et contextes d'utilisation."
topics: [gdpr, compliance, expectations, privacy, business-model]
applies_to: [all]
related_docs:
  - "meeting-notes/2026-11-09-rgpd-meeting.md"
  - "../business-model/business-model.md"
---

PROJET RUSTKINS • DIIAGE 3 • 13 NOVEMBRE 2026

# Document de compréhension des attentes RGPD

**Version Word du 13 novembre 2026 :** [Télécharger le document (.doc)](meeting-notes/2026-11-13-rustkins-comprehension-attentes-rgpd.doc).

**Objet :** exposer notre compréhension du RGPD et la manière dont nous prévoyons de l’aborder dans le projet Rustkins, à la suite de la réunion du 9 novembre 2026.

## 1. Notre compréhension générale

Nous comprenons que la démarche attendue consiste à relier la protection des données au fonctionnement global du projet : activité de l’entreprise, relations avec ses clients, conception du logiciel et conditions d’utilisation. Le travail devra expliquer nos choix et apporter progressivement des preuves de leur mise en œuvre. Ce document présente cette compréhension et l’orientation de notre travail ; il précède les livrables détaillés de conformité. [P1]

Le RGPD protège les personnes physiques lorsque des informations permettent de les identifier directement ou indirectement. Un traitement peut être une collecte, une consultation, une conservation, une transmission ou une suppression. Il ne se limite donc ni à une base de données clients ni à un formulaire sur un site internet. [J1]

Nous retenons les principes suivants : une finalité déterminée, une base légale adaptée, une information transparente, des données limitées au nécessaire et exactes, une conservation justifiée et une sécurité appropriée. Le consentement est une base possible parmi d’autres, à utiliser lorsqu’il est pertinent. [J3]

La démarche doit également permettre l’exercice des droits applicables, notamment l’accès, la rectification et, selon les conditions prévues, l’effacement, l’opposition ou la portabilité. Elle comprend une organisation capable de recevoir et de traiter les demandes. [J4]

## 2. La particularité de Rustkins

Rustkins est une plateforme CI/CD gratuite, open source et auto-hébergée. Les entreprises installent le logiciel sur leur infrastructure ; Rustkins ne propose pas d’hébergement SaaS de leurs instances. L’entreprise éditrice n’a donc pas vocation, dans ce modèle, à centraliser les données de leurs pipelines. [P1, P2]

Ce choix réduit les données directement gérées par l’éditeur, sans exclure la présence de données personnelles. La conception V1 prévoit des comptes et des informations de session ; les journaux d’exécution et fichiers produits peuvent aussi en contenir selon leur contenu. Il faut distinguer les données présentes chez un utilisateur de celles effectivement reçues par l’entreprise Rustkins. [P3, P4]

**Notre orientation :** traiter le RGPD selon deux dimensions complémentaires : **la conformité interne de l’entreprise Rustkins** et **la conception d’un logiciel facilitant la conformité de ses utilisateurs**. Cette approche permet de répondre aux attentes sans créer artificiellement de nouvelles collectes.

## 3. Le RGPD interne à l’entreprise Rustkins

Le premier volet portera sur les données nécessaires à la vie de l’entreprise et à ses relations avec ses clients. L’absence de SaaS ne supprime pas ces activités. Le modèle économique prévoit un abonnement premium facultatif, des déploiements payants sur l’infrastructure cliente et des développements spécifiques sur devis. [P2]

Nous prévoyons de partir de ces activités pour identifier les traitements et leurs finalités, puis de vérifier ceux qui existent effectivement. À ce stade, les activités commerciales ci-dessous sont **envisagées dans la documentation** : leur présence dans cette liste ne signifie pas qu’elles sont déjà opérationnelles.

| Activité à analyser | Finalité du traitement envisagé | Données à identifier, si collectées |
| --- | --- | --- |
| Contacts et échanges commerciaux | Répondre aux demandes et préparer une éventuelle relation commerciale. | Coordonnées des interlocuteurs et contenu des échanges. |
| Abonnements premium | Suivre les souscriptions et organiser l’accompagnement prévu. | Contacts abonnés et informations de suivi de l’abonnement. |
| Support et anomalies | Comprendre les problèmes, prioriser les corrections et informer les demandeurs. | Identité ou pseudonyme, échanges et éléments de diagnostic transmis. |
| Prestations et développements sur devis | Préparer et suivre les commandes, interventions et livraisons. | Contacts, besoins exprimés, devis et comptes rendus. |
| Facturation et administration des ventes | Suivre les factures et les règlements associés aux services. | Coordonnées de facturation et références des opérations concernant des personnes. |

Les outils internes du projet devront aussi être examinés. La documentation décrit l’usage de GitHub, Azure Boards, RustkinsActivity et de rapports Discord pour la coordination et le suivi des contributions. Les identifiants et historiques associés aux membres entrent donc dans le périmètre à qualifier. [P5]

### Ce que nous devons en déduire

Pour chaque traitement confirmé, nous devrons préciser qui décide de son usage, quelles personnes sont concernées, quelles données sont nécessaires, qui peut y accéder, où elles circulent et combien de temps elles sont conservées. Nous justifierons la base légale retenue et les mesures adaptées. Les fondements et durées ne sont pas arrêtés dans les notes de réunion. [P1 ; J3, J5]

Cette analyse servira à construire le registre, la politique de confidentialité réelle de Rustkins et les procédures internes : gestion des accès, traitement des demandes relatives aux données et réaction à un incident. Les éventuels prestataires et accès à des environnements clients seront analysés selon leur rôle effectif. [J4, J5]

**Le résultat attendu** est une organisation cohérente avec l’activité de Rustkins, et non une liste de traitements imaginés pour remplir le dossier. L’identité juridique de l’organisme, les outils commerciaux et les modalités opérationnelles restent à confirmer.

## 4. Un logiciel conçu pour faciliter la conformité

Le second volet consiste à intégrer la protection des données dans la conception de Rustkins. Notre objectif est de fournir aux entreprises des mécanismes communs et documentés, afin de réduire les adaptations techniques et le travail de préparation nécessaires lors d’un déploiement.

**Nous distinguons les fonctions prévues dans les versions du produit des pistes encore à arbitrer.** Leur présence dans la documentation ne démontre pas leur réalisation ; les mesures présentées lors de l’évaluation devront être vérifiées sur une version identifiée. [P1, P3, P6]

| Fonction et statut | Contribution attendue à la protection des données |
| --- | --- |
| **Auto-hébergement**<br>Modèle du projet | Permettre à l’entreprise de choisir et maîtriser son infrastructure, ses accès et les conditions d’exploitation. |
| **Authentification et rôles par projet**<br>Prévus en V1 | Identifier les utilisateurs et limiter leurs actions selon les droits attribués. Les habilitations restent à configurer selon l’organisation. |
| **Jetons à permissions limitées et révocables**<br>Prévus en V1 | Encadrer les accès automatisés aux projets et permettre le retrait des autorisations. |
| **Protection des accès aux logs et artéfacts**<br>Prévue en V1 | Contrôler la consultation des résultats. Les liens de téléchargement signés doivent avoir une durée limitée. |
| **Politique de conservation des artéfacts**<br>Prévue en V1 | Faciliter le nettoyage des fichiers expirés. Le sort des métadonnées et des sauvegardes doit aussi être étudié. |
| **Gestion et masquage des secrets**<br>Prévus en V2 | Réduire les divulgations d’identifiants sensibles dans les exécutions et les logs. Ce mécanisme ne constitue pas une anonymisation générale. |
| **Modèle de politique de confidentialité**<br>Piste non décidée | Aider le client à rédiger sa documentation en lui fournissant une base personnalisable selon ses usages. |

Sources : modèle d’hébergement [P2], périmètre V1 et sécurité [P3, P4], artéfacts [P7], roadmap V2 [P6], modèle de confidentialité [P1 §2.4].

### Réduire les démarches, tout en clarifiant les responsabilités

L’ambition est d’éviter que chaque entreprise doive reconstruire les mêmes protections ou repartir de zéro pour sa documentation. Elle devra toutefois définir ses propres finalités, données, destinataires et durées, puis adapter les réglages et l’information fournie aux personnes. La protection dès la conception contribue à cette démarche ; elle ne remplace pas la responsabilité de l’organisme qui exploite le logiciel. [J5]

Le support à distance et la télémétrie vers Rustkins restent des pistes non décidées. Ils ne seront pas présentés comme des fonctions engagées. Le modèle de confidentialité destiné aux utilisateurs reste distinct de la politique de l’entreprise Rustkins. [P1]

## 5. Une démarche globale et adaptée aux contextes

Nous comprenons le RGPD comme un sujet transversal : il concerne le logiciel, les pratiques de l’équipe, les relations commerciales, les prestataires et la communication. L’analyse doit suivre le cycle de vie des données, de leur collecte à leur suppression, et tenir compte de leurs destinataires. Un système sécurisé ne suffit pas à justifier tous ses usages.

### Des responsabilités à distinguer

Le responsable du traitement détermine les finalités et les moyens essentiels ; un sous-traitant traite des données pour son compte. Rustkins devra qualifier son rôle pour ses propres activités et pour chaque prestation. La seule distribution d’un logiciel auto-hébergé ne signifie pas que l’éditeur reçoit les données de toutes les installations. [J2 ; P2]

### Une dimension internationale

Le RGPD s’applique notamment aux traitements dans le cadre des activités d’un établissement dans l’Union européenne. Il peut aussi concerner certains organismes hors UE lorsqu’ils proposent des biens ou services aux personnes dans l’Union ou y suivent leur comportement. Son application dépend de critères précis, pas seulement de la localisation du serveur. [J2]

Lorsqu’une activité implique des destinataires hors Espace économique européen, nous devrons examiner les transferts et leur encadrement, notamment l’adéquation ou les garanties appropriées. Les autres droits applicables seront étudiés selon les pays et secteurs effectivement retenus. Le projet ne peut donc pas revendiquer une conformité mondiale uniforme. [J6]

### Des scénarios pour mettre notre compréhension à l’épreuve

La réunion propose d’étudier différents contextes sans imposer le développement de fonctions uniquement destinées à l’évaluation. Les cas ci-dessous sont des **propositions pédagogiques**, pas des clients existants. [P1 §2.5]

| Contexte proposé | Question à examiner |
| --- | --- |
| PME utilisant Rustkins pour ses projets internes | Comment gérer les comptes, les accès et les données présentes dans les résultats ? |
| Société de services travaillant pour plusieurs clients | Comment distinguer les responsabilités et éviter les accès entre projets clients ? |
| Entreprise développant un logiciel de santé | Des données sensibles entrent-elles réellement dans la CI, et quelles règles ou analyses supplémentaires en découlent ? |
| Entreprise européenne faisant intervenir un prestataire hors EEE | Quelles données sont accessibles à distance et quel encadrement faut-il examiner ? |

Pour chaque cas, nous distinguerons **le droit applicable**, **l’organisation à mettre en place** et **les possibilités réelles du logiciel**. Cette méthode permettra de montrer notre capacité d’analyse sans présenter un cas hypothétique comme une situation rencontrée.

## 6. Traduction de cette compréhension dans le travail à mener

Le travail devra partir de la réalité du projet et aboutir à des éléments vérifiables. Les notes du 9 novembre identifient les livrables ci-dessous ; ce document explique comment nous comprenons leur articulation. [P1 §4]

| Livrable attendu | Application envisagée à Rustkins |
| --- | --- |
| Registre des activités de traitement | Décrire les traitements internes confirmés et distinguer, si nécessaire, les opérations effectuées pour le compte de clients. |
| Politique de confidentialité réelle | Informer sur les pratiques de l’entreprise Rustkins à partir du registre, sans la confondre avec un modèle fourni aux utilisateurs du logiciel. |
| Modèle de consentement, si pertinent | Le préparer uniquement si un traitement retenu repose sur ce fondement. |
| Plan d’actions de mise en conformité | Distinguer les mesures vérifiées, les écarts et les actions restant à réaliser, avec une priorité adaptée. |
| Rapport d’analyse et démonstration | Expliquer les choix, analyser les scénarios et démontrer les protections effectivement mises en œuvre. |

### Notre méthode proposée

Nous commencerons par confirmer les activités et les flux de données, puis préciserons les responsabilités et les règles à appliquer. Nous confronterons ensuite les besoins aux fonctions documentées et à leur état réel. Les démonstrations utiliseront des données fictives et identifieront la version testée. Les décisions de développement resteront fondées sur l’utilité du produit. [P1]

Les points encore ouverts portent notamment sur les traitements commerciaux effectivement actifs, les outils retenus, les durées, les bases légales et la mise en œuvre réelle des protections. Les fonctionnalités optionnelles évoquées en réunion devront faire l’objet d’un choix explicite avant de devenir des engagements.

**Compréhension retenue pour Rustkins :** construire la conformité interne de l’entreprise et concevoir un produit qui facilite celle de ses utilisateurs. La valeur attendue repose sur des pratiques et des protections explicables et vérifiables, adaptées à chaque contexte d’utilisation.

### Sources du projet

Références dans RustkinsDocs, consultées pour ce document. Les sources décrivent des orientations et des cibles ; elles ne prouvent pas à elles seules l’implémentation du produit.

**P1.** Réunion du 9 novembre 2026 — [docs/cross-cutting/gdpr/meeting-notes/2026-11-09-rgpd-meeting.md](meeting-notes/2026-11-09-rgpd-meeting.md).

**P2.** Modèle économique — [docs/cross-cutting/business-model/business-model.md](../business-model/business-model.md).

**P3.** Périmètre V1 — [docs/versions/v1/overview.md](../../versions/v1/overview.md).

**P4.** Sécurité — [docs/architecture/components/security/05-security.md](../../architecture/components/security/05-security.md).

**P5.** Organisation actuelle — [docs/project-management/activity-journal-integration.md](../../project-management/activity-journal-integration.md).

**P6.** Roadmap — [docs/versions/roadmap.md](../../versions/roadmap.md).

**P7.** Artéfacts — [docs/architecture/components/storage/04-artifacts.md](../../architecture/components/storage/04-artifacts.md).

### Références officielles

CNIL, consultée le 13 novembre 2026 : **J1.** [RGPD : de quoi parle-t-on ?](https://www.cnil.fr/fr/rgpd-de-quoi-parle-t-on) ; **J2.** [chapitre I, champ d’application et définitions](https://www.cnil.fr/fr/reglement-europeen-protection-donnees/chapitre1) ; **J3.** [chapitre II, principes et licéité](https://www.cnil.fr/fr/reglement-europeen-protection-donnees/chapitre2) ; **J4.** [chapitre III, droits des personnes](https://www.cnil.fr/fr/reglement-europeen-protection-donnees/chapitre3) ; **J5.** [chapitre IV, responsabilités et mesures de protection](https://www.cnil.fr/fr/reglement-europeen-protection-donnees/chapitre4) ; **J6.** [chapitre V, transferts internationaux](https://www.cnil.fr/fr/reglement-europeen-protection-donnees/chapitre5).
