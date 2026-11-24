---
id: ADR-0004
title: "Chaque run référence une version immuable du pipeline"
status: accepted
topics: [architecture, pipeline, versioning, git, runtime]
applies_to: [all]
decided_at: 2026-11-24
approved_by: ["SNEAXIII"]
supersedes: []
related_work_items: []
references: ["https://github.com/Rustkins-Project/RustkinsDocs/pull/23", "https://github.com/Rustkins-Project/RustkinsDocs/pull/23#pullrequestreview-6040622283"]
---

# Chaque run référence une version immuable du pipeline

## Contexte

Le fichier YAML d'un dépôt change au fil des commits. Relire sa version courante pour expliquer un ancien run fausserait l'historique et pourrait modifier l'interprétation de ses jobs lors d'un retry. Les vues V0/V1 et l'architecture du versionnement décrivent un instantané `PipelineVersion` lié au SHA Git ; la spécification YAML v3 conserve ce principe.

## Décision

- La définition utilisée pour une exécution est figée dans une `PipelineVersion` liée à la révision Git et au contenu YAML validé. Elle conserve la version du contrat YAML, distincte de la version du produit Rustkins.
- Un `PipelineRun` référence exactement une `PipelineVersion`. Plusieurs runs peuvent réutiliser la même version ; une évolution du YAML produit une nouvelle version sans modifier les précédentes.
- Le Scheduler construit et évalue le DAG à partir de cette version, y compris après reprise ou retry. Les états d'exécution restent dans les entités runtime mutables.
- Cette ADR fixe l'invariant d'immuabilité, pas la représentation physique des jobs ou des steps : le modèle V0 et le modèle V1 peuvent différer.

## Alternatives

- **Relire le YAML courant au moment de chaque exécution ou retry** : l'historique et les reprises dépendraient d'un dépôt qui a pu changer ou devenir indisponible.
- **Copier toute la définition dans chaque `PipelineRun` sans version partagée** : préserverait un instantané, au prix d'une duplication et de relations moins explicites entre runs identiques.
- **Stocker seulement le SHA Git** : imposerait de retrouver le dépôt et son contenu pour interpréter chaque ancien run.

Ces alternatives expliquent le choix et ses conséquences.

## Conséquences

- Un ancien run reste interprétable avec la définition et le contrat YAML qui lui étaient associés.
- Le stockage des versions et leur politique de conservation deviennent nécessaires même lorsque le dépôt Git change.
- La validation et la normalisation doivent produire un instantané cohérent avant que le run ne soit exécuté.
- Les formats YAML v1, v2 et v3, les champs et les tables restent documentés dans les spécifications et modèles par version.

## Références

- [Architecture du versionnement](../docs/architecture/components/pipeline/08-pipeline-versioning.md) et [architecture du runtime](../docs/architecture/components/01-runtime-lifecycle.md).
- [Vue V0](../docs/versions/v0/overview.md#10-modèle-de-données-v0), [vue V1](../docs/versions/v1/overview.md#10-modèle-de-données-v1) et [modèle de données V1](../docs/architecture/data-model/10-data-model-reference.md#pipeline_version).
- [Index des contrats YAML v1 à v3](../INDEX.md#spécifications-yaml-des-pipelines).
