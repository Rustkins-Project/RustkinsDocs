---
id: DOC-0910
title: "Éco-conception de Rustkins — Démarche, leviers et limites"
type: cross-cutting
status: draft
summary: "Démarche d'éco-conception de Rustkins : périmètre de responsabilité, sobriété des ressources demandées, provisionnement des workers, métriques nécessaires, compromis assumés et lacunes de la documentation actuelle."
topics: [eco-design, sobriety, scheduler, worker, provisioning, metrics]
applies_to: [all]
related_docs:
  - docs/architecture/components/scheduler/06-resource-scheduling.md
  - docs/architecture/components/worker/09-worker-architecture.md
  - docs/architecture/components/messaging/02-rabbitmq-architecture.md
  - docs/architecture/components/storage/04-artifacts.md
  - docs/architecture/components/logging/03-real-time-logs.md
  - docs/specifications/pipeline/yaml-v3.md
  - docs/cross-cutting/business-model/business-model.md
  - docs/cross-cutting/communication/positioning-and-messages.md
references:
  - https://ecoresponsable.numerique.gouv.fr/publications/referentiel-general-ecoconception/
  - https://eur-lex.europa.eu/eli/dir/2024/825/oj
---

# Éco-conception de Rustkins — Démarche, leviers et limites

## 1. Objectif

Ce document fixe la position de l'équipe sur l'éco-conception de Rustkins : ce dont Rustkins est responsable, les leviers retenus dans le produit, les métriques nécessaires pour les piloter et les compromis assumés.

**Statut :** orientation d'équipe en `draft`. Les leviers marqués « piste » ne sont ni spécifiés ni planifiés. Aucun chiffre de consommation n'est publié tant qu'il n'a pas été mesuré.

## 2. Périmètre de responsabilité

### 2.1 Ce dont Rustkins est responsable

Rustkins est responsable des **ressources qu'il demande et qu'il fait demander** :

- l'empreinte de ses propres composants (API, scheduler, workers, broker, base de données, interface) ;
- la **puissance réservée** pour les jobs et le nombre de workers tenus disponibles ;
- les volumes qu'il stocke et transfère par défaut (logs, artefacts, cache) ;
- les **valeurs par défaut** : ce qui est réglé par défaut finit par être appliqué par la majorité des installations ;
- la **visibilité** donnée aux utilisateurs sur leur propre consommation.

L'objectif produit est simple : **léger, rapide, efficace**, et une configuration sobre facile à adopter.

### 2.2 Ce qui relève de l'utilisateur

Rustkins est auto-hébergé uniquement ([modèle économique](../business-model/business-model.md)). Relèvent donc de l'entreprise utilisatrice :

- le matériel, sa durée de vie, son taux d'occupation et son refroidissement ;
- le mix électrique et le lieu d'hébergement ;
- le contenu des pipelines : images, durée des tests, taille des matrices, fréquence des déclenchements ;
- les durées de rétention choisies, dans la limite des options proposées ;
- l'usage fait des annulations, des relances et des planifications.

Rustkins **informe et recommande** ; il n'impose pas de politique d'usage. L'effet rebond (plus de runs parce que la CI est plus rapide) relève de l'usage. Il n'invalide pas les gains par run, mais il interdit de promettre une baisse de la consommation **totale** d'une organisation.

### 2.3 Conséquence sur les indicateurs

Les indicateurs de Rustkins portent sur des **ressources** (mCPU, Mo de RAM, secondes de calcul, octets stockés et transférés, workers actifs). Ils ne sont **pas convertis en énergie ni en CO₂e** : la conversion dépend du matériel et du mix électrique, que Rustkins ne connaît pas.

## 3. Leviers retenus

### 3.1 Réserver ce qui est réellement consommé (provisionnement)

C'est le levier principal. Aujourd'hui, le scheduler réserve les ressources **déclarées** par le job (par défaut 1000 mCPU et 1024 Mo, [ARCH-06 §4](../../architecture/components/scheduler/06-resource-scheduling.md#4-job-resource-definition)), pas celles réellement utilisées. Un job de lint qui consomme 100 mCPU bloque 1000 mCPU : le worker paraît plein alors qu'il est inactif, et l'on ajoute des machines inutiles.

Pistes :

- mesurer la consommation réelle de chaque job (CPU, pic mémoire, durée, voir §4) ;
- afficher l'écart entre ressources réservées et consommées pour chaque job ;
- **suggérer un dimensionnement** (« ce job n'a jamais dépassé 200 mCPU et 300 Mo sur les 20 derniers runs ») ;
- signaler les échecs liés aux limites (arrêt pour manque de mémoire, CPU saturé en permanence) comme tels dans l'interface, pour que l'utilisateur augmente la limite au lieu de relancer à l'aveugle.

### 3.2 Remplir les workers avant d'en solliciter d'autres

La sélection V1 retient le **premier worker compatible** ([ARCH-06 §9](../../architecture/components/scheduler/06-resource-scheduling.md#9-worker-selection)). Avec un ordre de workers stable, cela concentre la charge sur les premiers workers et laisse les derniers inactifs, qu'il devient possible d'arrêter. Cette propriété doit être **conservée volontairement** si une stratégie plus « intelligente » est introduite : répartir uniformément la charge empêche d'éteindre des machines.

### 3.3 Adapter la capacité aux heures de la journée

Rustkins ne démarre ni n'éteint de machines : en auto-hébergement, c'est le rôle de l'administrateur ou de son outillage (hyperviseur, groupe d'autoscaling, scripts). Rustkins peut fournir les **signaux** et les **états** nécessaires :

- état de worker **`draining`** : il termine ses jobs en cours sans en accepter de nouveaux, puis peut être arrêté sans perte (piste) ;
- **profils de capacité par plage horaire** : ensemble des workers acceptant des jobs selon l'heure, par exemple capacité réduite la nuit et le week-end (piste) ;
- une **API ou des webhooks** signalant « capacité insuffisante » et « worker inactif depuis N minutes », pour piloter un autoscaler externe (piste).

Les décisions s'appuient sur les bons signaux :

| Signal | Interprétation | Action |
| --- | --- | --- |
| Jobs en `waiting_resources` avec un temps d'attente qui augmente | Capacité réellement insuffisante | Ajouter un worker ou de la puissance sur la plage concernée |
| Worker réservé à 100 % mais consommation réelle faible | Ressources surdéclarées, pas un manque de capacité | Corriger le dimensionnement des jobs (§3.1), **pas** ajouter de worker |
| Worker réservé à 100 % en permanence, sans file d'attente ni erreur anormale | Utilisation efficace | Rien à faire |
| Worker souvent saturé en consommation **réelle** (CPU ou mémoire) et erreurs aléatoires (timeouts, tests instables, arrêts pour manque de mémoire) sur les jobs qu'il exécute | Contention : les jobs se gênent sur la machine | Donner plus de marge à ce worker (réduire la capacité déclarée ou ajouter de la puissance), après avoir vérifié que les mêmes jobs passent ailleurs |
| Worker inactif sur une plage récurrente | Surcapacité | Le passer en `draining` puis l'arrêter sur cette plage |

Un worker plein en permanence n'est pas un problème en soi : c'est le **temps d'attente des jobs** qui justifie d'ajouter de la capacité.

### 3.4 Lisser la charge dans la journée

Une installation est dimensionnée pour son pic. Déplacer les travaux non urgents hors des heures de pointe (nuit, pause de midi) réduit ce pic, donc le nombre de workers nécessaires.

Piste : un déclencheur planifié (`schedule`, expression cron) pour les tâches non interactives : builds nocturnes, analyses de dépendances, nettoyages. Ce déclencheur **n'existe dans aucune spécification actuelle** (YAML v3 : `push`, `pull_request`, `manual`, `api`).

### 3.5 Ne pas exécuter ce qui est inutile

- **Annulation manuelle** : indispensable, déjà prévue ([ARCH-09 §12](../../architecture/components/worker/09-worker-architecture.md#12-cancellation)). L'utilisateur reste responsable de ce qu'il annule.
- **Annulation automatique d'un run remplacé** (piste) : quand un nouveau run démarre avec la même **clé de concurrence** (par exemple la branche), annuler le run précédent devenu obsolète. Utile surtout pour les pipelines longs (compilation ou tests de plusieurs dizaines de minutes) dont seul le dernier résultat compte. Option **désactivée par défaut**, configurable par pipeline ou par job. Exemple de syntaxe à arbitrer :

  ```yaml
  concurrency:
    key: branch             # clé unique : branche, tag, environnement…
    mode: cancel-previous   # ou queue (attendre la fin du run en cours)
    scope: pipeline         # ou job : n'annuler que le même job
  ```
- **Filtres de chemins** (piste) : ne déclencher un pipeline que si certains fichiers ont changé. YAML v3 filtre les branches et les tags, pas les chemins.

### 3.6 Réutiliser plutôt que recalculer : le cache

Le cache déclaratif de YAML v3 ([§23](../../specifications/pipeline/yaml-v3.md#23-cache)) évite de retélécharger et recompiler les dépendances. Sa clé basée sur le hash des fichiers verrous règle la question de l'invalidation. La spécification du cache n'est pas terminée : elle **ne définit pas encore de durée d'expiration ni de taille maximale**, sans lesquelles le stockage du cache croît sans limite. Proposition : expiration par défaut **7 jours sans utilisation**, et quota par projet, tous deux configurables.

### 3.7 Stockage : des options, des valeurs par défaut raisonnables

- **Artefacts** : rétention de 30 jours par défaut, plafond par projet et nettoyage automatique déjà spécifiés ([ARCH-04 §9](../../architecture/components/storage/04-artifacts.md#9-retention)).
- **Logs** : aucune rétention n'est spécifiée ; elle figure seulement en évolution future ([ARCH-03 §15](../../architecture/components/logging/03-real-time-logs.md#15-future-evolution)). Il faut au minimum l'option de configuration, avec une valeur par défaut documentée. Le choix de la durée reste à l'administrateur.
- **Compression** des logs archivés (piste) : les logs texte se compressent très bien.

### 3.8 Recommandations sur les pipelines

L'objectif est de **sensibiliser** : beaucoup d'utilisateurs prennent l'image qu'ils savent fonctionner (souvent Ubuntu) parce qu'ils ne connaissent pas les alternatives. Souvent, il suffit de connaître l'information pour faire mieux. Le parcours classique est : Ubuntu → Debian `-slim` → Alpine → `distroless` ou `scratch`.

À partir des métriques (§4), l'interface peut afficher des **suggestions**, jamais des blocages :

- image lourde dont le téléchargement domine la durée du job : faire connaître les variantes plus légères (`-slim`, Alpine) ;
- `scratch` ou `distroless` pour les images finales contenant un binaire statique ;
- dépendances retéléchargées à chaque run : proposer le cache ;
- ressources déclarées très supérieures à la consommation : proposer un dimensionnement (§3.1).

Chaque suggestion indique ses limites, pour que l'utilisateur choisisse en connaissance de cause. Par exemple, Alpine utilise musl : certaines dépendances natives (paquets Python, modules Node) n'y ont pas de binaires précompilés et se recompilent à chaque build. Le job consomme alors **plus** de CPU qu'avec une image Debian `-slim`, malgré une image plus petite.

### 3.9 Interfaces web

Le portail d'administration est consulté en interne et le site vitrine aura un trafic modeste : leur poids reste secondaire face à l'exécution des jobs. Bonnes pratiques retenues sans chercher la conformité complète au RGESN : pages légères, JavaScript limité, pas de rafraîchissement automatique permanent, flux de logs en temps réel (SSE) ouvert uniquement quand la page de logs est affichée.

## 4. Métriques nécessaires

Les leviers §3.1, §3.3 et §3.8 reposent tous sur des métriques qui **ne sont spécifiées nulle part** aujourd'hui. C'est le premier manque à combler.

| Niveau | Métriques | Source possible |
| --- | --- | --- |
| Job | CPU consommé, pic mémoire, durée, temps de téléchargement de l'image, taille de l'image, motif d'arrêt (dont manque de mémoire) | Statistiques cgroups via l'API Docker, mesurées par le worker |
| Job | Ressources réservées vs consommées | Scheduler + worker |
| Worker | Taux de réservation, taux d'utilisation réel, durée d'inactivité | Scheduler + worker |
| Installation | Temps d'attente en `waiting_resources`, nombre de workers actifs par heure | Scheduler |
| Stockage | Volume de logs, d'artefacts et de cache par projet | RustFS + métadonnées |

Ces métriques servent d'abord à l'exploitation (dimensionnement, débogage) ; l'éco-conception en est un bénéfice direct. Elles doivent pouvoir être exportées vers les outils de supervision de l'utilisateur (format Prometheus par exemple), sans dépendance obligatoire.

## 5. Compromis assumés

### 5.1 RabbitMQ

L'équipe a identifié que RabbitMQ est probablement **surdimensionné** pour les besoins de la V1 : un service de plus à installer, à superviser et à faire tourner en permanence, ce qui pèse surtout sur les petites installations. Il a été retenu comme solution connue de l'équipe, et pour une raison de **sécurité** : isoler les workers de la base de données.

Constats dans la documentation :

- PostgreSQL est déjà la source de vérité et alimente RabbitMQ par une outbox transactionnelle ([ARCH-02](../../architecture/components/messaging/02-rabbitmq-architecture.md)). Une file de jobs dans PostgreSQL (`SELECT … FOR UPDATE SKIP LOCKED`) et des notifications `LISTEN/NOTIFY` couvriraient une partie des usages. Le transport des logs en temps réel vers plusieurs lecteurs est le cas où un broker apporte le plus.
- **Contradiction à arbitrer :** l'architecture actuelle fait accéder les workers **directement à PostgreSQL**. Le scheduler **décide** (placement, réservation, retries, déblocage des jobs dépendants), mais c'est le worker qui **écrit** les états d'exécution du JobRun (`running`, `success`, `warning`, `failed`, `cancelled`). Le scheduler réagit ensuite à ces écritures ([ARCH-11 §8 et §9](../../architecture/components/scheduler/11-scheduler-architecture.md#9-completion-handling), [ARCH-09 §5 et §11](../../architecture/components/worker/09-worker-architecture.md#11-status-updates)). Le worker relit aussi le JobRun en base à la réception du message, celui-ci ne contenant que des identifiants. L'isolation recherchée n'est donc pas obtenue aujourd'hui : un worker compromis par un job malveillant détiendrait des identifiants de base de données.
- Pour que le scheduler soit le seul à écrire les états, il faudrait : un message de job qui contient tout ce dont le worker a besoin (ou une API interne en lecture seule), et des comptes rendus d'état envoyés par le worker via RabbitMQ (file d'états consommée par le scheduler, idempotente). Le scheduler valide la transition puis l'écrit en base.
- L'isolation ne dépend pas du broker : elle s'obtient dès que les workers **ne détiennent aucun identifiant PostgreSQL** et passent par un intermédiaire qui valide leurs messages (RabbitMQ consommé par le scheduler, ou une API interne dédiée aux workers).

**Orientation :** conserver RabbitMQ pour sortir la V1, l'architecture étant déjà conçue autour. Isoler l'accès au broker derrière une interface (trait Rust) pour qu'un remplacement ultérieur reste localisé. Mesurer l'empreinte du broker sur l'installation de référence. Corriger l'accès direct des workers à PostgreSQL, ou le justifier, dans une ADR. Toute décision de remplacement du broker passe aussi par une ADR.

### 5.2 Autres compromis

| Choix | Gain | Contrepartie acceptée |
| --- | --- | --- |
| Limites CPU et mémoire par conteneur | Pas de job qui monopolise une machine | Échecs si sous-dimensionné, rendus visibles par les métriques (§3.1) |
| Cache | Moins de téléchargements et de calcul | Stockage, à borner par expiration et quota (§3.6) |
| Consolidation sur les premiers workers | Workers libérables | Les jobs se partagent plus souvent une même machine |
| Rétention configurable | Choix laissé à l'administrateur | Rustkins ne garantit pas une rétention courte |

## 6. Communication

- Les arguments de performance portent sur la **conception**, pas sur la vitesse brute : **provisionnement intelligent** (réservation par job, consolidation, signaux de capacité), **cache intégré**, **sobriété par défaut** (rétentions, limites, suggestions) et **métriques de consommation visibles**.
- Face à Jenkins : Jenkins sait provisionner des agents à la demande (plugins Kubernetes, EC2), mais ce n'est ni mis en avant ni le comportement par défaut, et sa configuration laisse passer des installations très gaspilleuses (agents allumés en permanence et mal répartis). L'argument juste est que **Rustkins rend la configuration sobre simple et visible par défaut**. Ne pas affirmer qu'il « consomme moins que Jenkins » sans mesure comparative publiée, conformément à la règle de [positionnement](../communication/positioning-and-messages.md).
- Rust allège l'orchestrateur lui-même (pas de machine virtuelle Java, pas de ramasse-miettes, faible empreinte mémoire). En revanche, il ne change rien à la consommation des jobs (compilations, tests), qui représente l'essentiel du total quel que soit l'orchestrateur. C'est un argument valable, pas un argument chiffré.
- Pas d'allégation générique (« CI verte », « éco-responsable ») : la directive (UE) 2024/825 interdit les allégations environnementales génériques non étayées.

## 7. Lacunes de la documentation à combler

| Manque | Document concerné | Priorité suggérée |
| --- | --- | --- |
| Collecte et exposition des métriques de consommation par job et par worker | Nouvelle spécification, ARCH-06, ARCH-09 | Haute : prérequis des autres leviers |
| Comparaison ressources réservées / consommées et suggestion de dimensionnement | ARCH-06 | Haute |
| Accès direct des workers à PostgreSQL, contraire à l'isolation recherchée (§5.1) | ARCH-01, ARCH-02, ARCH-06, ARCH-09, ADR | Haute : sécurité |
| Rétention des logs (option et valeur par défaut) | ARCH-03 | Moyenne |
| Expiration (7 jours proposés) et quota du cache | YAML v3 §23 | Moyenne |
| État `draining` des workers et profils de capacité horaires | ARCH-06, ARCH-09 | Moyenne |
| Déclencheur planifié `schedule` (cron) | Spécification YAML future | Moyenne |
| Annulation automatique des runs remplacés (`concurrency`), filtres de chemins | Spécification YAML future | Basse |
| ADR sur le maintien ou le remplacement de RabbitMQ | `decisions/` | Après la V1 |

Ces éléments sont des **propositions** : leur version cible et leur priorité s'arbitrent dans le backlog Azure Boards.

## 8. Références

- [ARCH-06 — Resource Scheduling](../../architecture/components/scheduler/06-resource-scheduling.md)
- [ARCH-09 — Worker Architecture](../../architecture/components/worker/09-worker-architecture.md)
- [ARCH-02 — RabbitMQ Architecture](../../architecture/components/messaging/02-rabbitmq-architecture.md)
- [ARCH-04 — Artifacts](../../architecture/components/storage/04-artifacts.md)
- [ARCH-03 — Real-time Logs](../../architecture/components/logging/03-real-time-logs.md)
- [Spécification YAML v3](../../specifications/pipeline/yaml-v3.md)
- [Modèle économique](../business-model/business-model.md)
- [RGESN — Référentiel général d'écoconception de services numériques](https://ecoresponsable.numerique.gouv.fr/publications/referentiel-general-ecoconception/)
- [Directive (UE) 2024/825 — allégations environnementales](https://eur-lex.europa.eu/eli/dir/2024/825/oj)
