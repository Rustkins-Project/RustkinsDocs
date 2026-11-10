---
id: DOC-0100
title: "Compte rendu de la réunion RGPD du 9 novembre 2026"
type: cross-cutting
status: draft
summary: "Cadrage du dossier RGPD DIIAGE 3 pour Rustkins, entre modèle auto-hébergé, obligations internes et pistes de démonstration."
topics: [gdpr, compliance, meeting, business-model]
applies_to: [all]
---

# Réunion RGPD — 9 novembre 2026

**Participants :** équipe Rustkins et intervenant chargé de l'évaluation RGPD.  
**Contexte :** préparation du dossier collectif DIIAGE 3 (2026–2027).  
**Statut du document :** compte rendu proposé à la revue de l'équipe. Les pistes décrites ci-dessous ne sont pas des engagements de développement.

## 1. Objectif et problématique

Déterminer comment montrer l'application concrète du RGPD dans Rustkins et préparer les livrables attendus, tout en conservant le modèle économique décidé pour le projet.

Rustkins est une plateforme CI/CD **open source et gratuite**, **exclusivement auto-hébergée**, sans offre SaaS ni hébergement d'instances clientes par l'entreprise. La monétisation envisagée repose sur un abonnement premium offrant notamment la priorisation de corrections de bugs, des échanges plus réguliers avec les clients et un mécanisme temporaire autour de certaines fonctionnalités.

Ce positionnement réduit les données directement hébergées et traitées par l'éditeur dans le cadre du service logiciel. Il ne signifie pas une absence totale de RGPD : la gestion des comptes et contacts commerciaux, le support et les abonnements peuvent constituer des traitements propres à l'entreprise. Les installations des clients peuvent aussi traiter des données personnelles, même si Rustkins n'y accède pas.

**Question centrale :** comment démontrer toutes les compétences RGPD requises sans ajouter des traitements de données ou des fonctionnalités artificielles à Rustkins ?

## 2. Sujets échangés

### 2.1. Activités internes et registre des traitements

Identifier les traitements liés à la future activité de l'entreprise : contacts, clients premium, gestion des abonnements, demandes de support et opérations administratives pertinentes.

L'objectif est d'établir le **registre des activités de traitement** de Rustkins, en distinguant les traitements internes des traitements mis en œuvre par les entreprises qui auto-hébergent le logiciel.

La liste exacte, les finalités, les bases légales, les durées de conservation et les acteurs restent à qualifier dans le registre, et ne sont pas arrêtés au cours de cette réunion.

### 2.2. Support prioritaire et accès à distance

Le support premium envisagé ne signifie pas nécessairement une assistance personnalisée avec accès aux machines du client. Il s'agit principalement de **prioriser les corrections de bugs** et d'entretenir un **contact plus régulier** avec les abonnés.

Une possibilité complémentaire a été discutée : une prise en main à distance pour certaines situations de support. Un tel service pourrait donner accès à des environnements contenant des données personnelles et demanderait des précautions spécifiques : autorisations, confidentialité, traçabilité, limitation des accès, responsabilités et modalités contractuelles adaptées.

**Statut :** piste discutée et jugée pertinente pour l'analyse RGPD, **non décidée pour le produit**.

### 2.3. Analytics et télémétrie éventuelle

La collecte **éventuelle** de statistiques envoyées à Rustkins a été évoquée afin de mieux connaître les performances du produit. Exemples : caractéristiques de machines hébergeant les workers ou le scheduler, consommation de ressources et indicateurs techniques.

L'intention serait de privilégier des données véritablement anonymisées. Toutefois, les caractéristiques de machines, identifiants d'installation et autres métadonnées peuvent permettre une identification ou une ré-identification indirecte : l'absence de nom ou d'adresse e-mail ne suffit pas à garantir l'anonymat.

Aucune télémétrie remontée à l'éditeur n'avait été prévue à l'origine. Sa pertinence produit, son caractère facultatif, ses données exactes et sa conformité resteraient à étudier avant tout choix.

**Statut :** simple piste de réflexion, **non retenue pour l'instant**.

### 2.4. Modèle de politique de confidentialité pour les clients

Une fonctionnalité facultative consisterait à **inclure dans Rustkins un modèle personnalisable de politique de confidentialité**, à adapter par les entreprises utilisatrices selon leurs pratiques. Elle pourrait faciliter leur documentation de conformité et constituer un argument de différenciation ou de communication.

Il s'agirait d'un outil d'aide, non d'une garantie automatique de conformité : chaque entreprise demeure responsable du contenu adapté à ses traitements réels.

Ce modèle à destination des clients est **distinct** de la politique de confidentialité réelle de l'entreprise Rustkins, exigée dans le dossier pédagogique.

**Statut :** piste possible, **implémentation non décidée**.

### 2.5. Scénarios d'entreprises et réglementations

L'équipe et l'intervenant ont évoqué ensemble la création de **scénarios d'entreprises utilisatrices de Rustkins**, avec des contextes et obligations différents. L'objectif serait d'identifier les textes applicables, les acteurs et responsabilités, les données en jeu et les mesures techniques ou organisationnelles adaptées.

Les cas peuvent par exemple porter sur différents secteurs ou contextes géographiques, à déterminer et à vérifier avec les textes pertinents. L'analyse doit expliquer ce que le produit facilite déjà, quelles adaptations seraient nécessaires et quelles obligations relèvent de l'entreprise utilisatrice.

Cette approche permettrait de démontrer des compétences RGPD sans créer systématiquement de nouvelles fonctionnalités.

**Statut :** piste commune jugée intéressante, **à privilégier dans les arbitrages ultérieurs** ; scénarios précis encore à définir.

### 2.6. Plan d'actions et valorisation de la conformité

Le plan d'actions de mise en conformité servira à exposer les mesures déjà appliquées, celles restant à faire et leur priorité. L'auto-hébergement et les mesures de protection des données pourront être présentés aux entreprises intéressées par Rustkins comme éléments de confiance, à condition de justifier les affirmations.

Cette valorisation commerciale ne remplace pas le plan d'actions attendu pour l'évaluation, ni les obligations légales de l'entreprise.

## 3. Orientations de la réunion

- **Maintenir** le modèle open source, gratuit, sans SaaS et fondé sur l'auto-hébergement.
- Analyser les **traitements internes réels** de l'entreprise pour le registre.
- Chercher des **scénarios d'utilisation** permettant une démonstration réglementaire et technique crédible.
- Ne pas implémenter des fonctions supplémentaires dans le seul but d'obtenir des éléments à présenter au jury.
- Garder les analytics, l'assistance à distance et le modèle de confidentialité intégré au stade de **pistes facultatives**.

L'intervenant a validé l'intérêt de réfléchir à ces pistes, mais leur réalisation ou non appartient à l'équipe Rustkins. La validation de la réflexion ne vaut **pas** décision de les développer.

## 4. Livrables et calendrier de référence

Le document de consignes DIIAGE 3 prévoit les étapes suivantes :

| Échéance pédagogique | Livrable |
| --- | --- |
| Fin janvier 2027 | Registre des activités de traitement (modèle CNIL) |
| Fin mars 2027 | Politique de confidentialité réelle et modèle de consentement si nécessaire |
| Début mai 2027 | Plan d'actions de mise en conformité |
| Début juin 2027 | Dossier final d'analyse RGPD et annexes obligatoires |
| Mi-juin 2027 | Soutenances individuelles |

Le rapport final doit traiter les compétences évaluées de manière claire et systématique. Les annexes obligatoires comprennent le registre, le plan d'actions, la politique de confidentialité réelle et le modèle de consentement si utilisé. La soutenance inclut une démonstration des mesures effectivement mises en œuvre dans l'application.

**Important :** les échéances ci-dessus sont issues des consignes remises aux étudiants, et non de nouvelles dates fixées à cette réunion.

## 5. Travaux à engager et questions ouvertes

1. Dresser une première liste des traitements internes de Rustkins et de leurs finalités.
2. Définir des scénarios d'entreprises assez différents pour couvrir les compétences attendues ; distinguer droit applicable et mesures propres au logiciel.
3. Recenser les mesures de protection réellement présentes dans les versions de Rustkins, sans présenter les fonctionnalités futures comme réalisées.
4. Arbitrer la pertinence produit de chaque fonctionnalité supplémentaire discutée.
5. Préparer les livrables selon les échéances pédagogiques, en conservant la distinction entre conformité de l'éditeur et conformité de ses clients.

Aucun responsable nominatif ni arbitrage technique précis n'a été fixé dans les notes de cette réunion.

## 6. Conclusion

L'orientation privilégiée consiste à **prouver la maîtrise du RGPD par l'analyse et des cas d'usage réalistes**, en complément des traitements réellement effectués par Rustkins, tout en préservant son modèle économique. Les éventuelles fonctions RGPD intégrées au produit doivent apporter de la valeur aux utilisateurs et faire l'objet d'une décision indépendante.
