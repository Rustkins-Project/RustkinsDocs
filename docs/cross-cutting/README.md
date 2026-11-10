# Domaines transversaux de Rustkins

Ce répertoire rassemble la documentation relative à l'entreprise et aux enjeux qui traversent plusieurs composants ou versions du produit. Il complète les dossiers techniques et le référentiel de gestion de projet.

| Domaine | Contenu |
| --- | --- |
| [RGPD et protection des données](gdpr/README.md) | Gouvernance des données, analyses, livrables RGPD, comptes rendus |
| [Modèle économique](business-model/README.md) | Offre gratuite, financement, services premium, stratégie commerciale |
| [Direction artistique](art-direction/README.md) | Identité visuelle, marque, charte, supports graphiques |
| [Veille](technology-watch/README.md) | Veille technologique, réglementaire, concurrentielle et synthèses |
| [Éco-conception](eco-design/README.md) | Empreinte du service, bonnes pratiques et indicateurs |
| [Communication](communication/README.md) | Messages publics, canaux, campagne et supports de communication |

## Règles de classement

- La documentation technique de référence demeure dans `docs/architecture/`, `docs/specifications/` et `docs/operations/`.
- Les règles Agile et le suivi de projet demeurent dans `docs/project-management/` et Azure Boards.
- Les arbitrages d'architecture sont consignés dans les ADR de `decisions/`.
- Les comparaisons exploratoires et POC non validés demeurent dans `research/` ; les synthèses de veille suivies dans le temps relèvent de `technology-watch/`.
- Éviter la duplication : les documents transversaux pointent vers les référentiels techniques ou organisationnels lorsqu'ils s'y réfèrent.
- Les propositions et pistes ouvertes doivent être explicitement distinguées des décisions prises. Les modèles légaux ou commerciaux non finalisés ne doivent pas être présentés comme déjà applicables.
- Les documents de référence Markdown suivent le schéma `schemas/document.schema.json`. Chaque `README.md` est un index sans métadonnées.

Les sous-dossiers et fichiers supplémentaires sont créés à mesure que des contenus réels existent.
