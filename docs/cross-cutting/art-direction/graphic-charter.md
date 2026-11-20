---
id: DOC-0106
title: "Charte graphique de Rustkins — proposition initiale"
type: cross-cutting
status: draft
summary: "Charte graphique provisoire de Rustkins : palette clair/sombre, typographies, règles du logo, composants, iconographie, accessibilité et déclinaisons de communication."
topics: [brand, graphic-charter, design-system, colors, typography, accessibility]
applies_to: [all]
---

# Charte graphique de Rustkins — proposition initiale

## 1. Objet, périmètre et niveau de validation

Cette charte propose les **règles visuelles concrètes** qui déclinent la [direction artistique de Rustkins](art-direction.md) sur l'application, le site vitrine, la documentation et les supports de communication.

Elle conserve les choix d'orientation déjà exprimés : **design minimaliste**, référence à la lisibilité de GitHub Actions et Jenkins, **tons neutres sans noir ni blanc purs**, **bleu clair comme accent** et **deux thèmes : clair et sombre**.

> **Statut : `draft`.** Les valeurs, familles typographiques et dimensions de ce document sont des **propositions de départ à valider** par l'équipe. Elles ne signifient ni qu'une identité finale est livrée, ni que les composants sont déjà implémentés. Aucun logo définitif n'est fourni à ce stade.

Cette charte ne remplace pas les spécifications produit, les règles d'accessibilité ni la [stratégie de communication](../communication/README.md).

## 2. Identité de marque

- **Nom affiché :** Rustkins (respecter cette casse).
- **Positionnement :** plateforme CI/CD open source, auto-hébergeable et indépendante des forges Git.
- **Personnalité :** sobre, technique, professionnelle, directe et accessible.
- **Valeurs :** maîtrise, indépendance, transparence, fiabilité et performance.
- **Signature :** « Rustkins — Ne subissez plus votre CI/CD, maîtrisez-la ! »

Le visuel doit aider à **comprendre et piloter la CI/CD**, pas simplement évoquer l'informatique. Éviter les effets « cyber » décoratifs, les néons omniprésents et les arrière-plans surchargés.

## 3. Palette chromatique

### 3.1. Couleurs de marque

Les trois teintes de référence de la direction artistique sont reprises comme **base de travail** :

| Usage | Nom | HEX |
| --- | --- | --- |
| Fond principal sombre | Anthracite | `#181B20` |
| Fond principal clair | Blanc cassé | `#F3F5F7` |
| Accent de marque | Bleu clair | `#75C9F1` |

**Règle :** ne pas utiliser `#000000` (noir pur) ou `#FFFFFF` (blanc pur) comme fonds ou textes dominants. Privilégier des contrastes confortables et une progression subtile des surfaces.

**Important :** le bleu clair `#75C9F1` fonctionne bien sur fond sombre, mais **pas comme texte courant sur fond clair**. Une variante plus foncée est prévue pour les liens et boutons du thème clair.

### 3.2. Tokens du thème clair (proposition)

| Token | HEX | Usage |
| --- | --- | --- |
| `background` | `#F3F5F7` | Fond global |
| `surface` | `#F8F9FB` | Cartes, panneaux |
| `surface-muted` | `#E9EDF2` | Sections secondaires, cellules sélectionnées |
| `border` | `#D4DBE3` | Traits de séparation, contours |
| `text-primary` | `#202833` | Titres, textes principaux |
| `text-secondary` | `#4D5A69` | Métadonnées, descriptions |
| `brand-accent` | `#75C9F1` | Touches graphiques et éléments non textuels |
| `interactive-primary` | `#17688C` | Boutons principaux, liens et focus visibles |

### 3.3. Tokens du thème sombre (proposition)

| Token | HEX | Usage |
| --- | --- | --- |
| `background` | `#181B20` | Fond global |
| `surface` | `#22262D` | Cartes, panneaux |
| `surface-muted` | `#2A3039` | Sections secondaires, cellules sélectionnées |
| `border` | `#343C46` | Traits de séparation, contours |
| `text-primary` | `#E8EDF3` | Titres, textes principaux |
| `text-secondary` | `#AEB9C7` | Métadonnées, descriptions |
| `brand-accent` | `#75C9F1` | Accent, liens, focus, boutons principaux |
| `interactive-primary` | `#75C9F1` | Actions principales |

Le thème clair et le thème sombre **doivent être implémentés tous les deux**. Le choix du thème doit rester possible dans l'interface et les composants doivent conserver leur organisation et leurs significations.

### 3.4. Couleurs fonctionnelles (proposition)

Les statuts d'exécution ne doivent **pas** dépendre exclusivement du bleu de marque. Leur sémantique reste identique dans les deux thèmes :

| État | Clair (texte / icône) | Sombre (texte / icône) |
| --- | --- | --- |
| Succès | `#216B54` | `#66C8A4` |
| Échec / erreur | `#AF3C4C` | `#F18B93` |
| Avertissement | `#895E18` | `#ECC47C` |
| En cours / information | `#17688C` | `#75C9F1` |
| En attente / ignoré | `text-secondary` | `text-secondary` |

Ces couleurs concernent en priorité les **libellés et icônes sur les fonds principaux**. Si elles sont utilisées dans des badges colorés, recalculer les contrastes avec les fonds spécifiques.

**Toujours combiner une couleur avec un texte et/ou une icône explicite** : `Running`, `Success`, `Failed`, `Skipped`, etc.

### 3.5. Exemple d'implémentation (indicatif)

```css
:root,
[data-theme="light"] {
  --rk-background: #F3F5F7;
  --rk-surface: #F8F9FB;
  --rk-surface-muted: #E9EDF2;
  --rk-border: #D4DBE3;
  --rk-text-primary: #202833;
  --rk-text-secondary: #4D5A69;
  --rk-brand-accent: #75C9F1;
  --rk-interactive-primary: #17688C;
}

[data-theme="dark"] {
  --rk-background: #181B20;
  --rk-surface: #22262D;
  --rk-surface-muted: #2A3039;
  --rk-border: #343C46;
  --rk-text-primary: #E8EDF3;
  --rk-text-secondary: #AEB9C7;
  --rk-brand-accent: #75C9F1;
  --rk-interactive-primary: #75C9F1;
}
```

Ces noms de tokens sont illustratifs : ils ne prescrivent pas encore l'architecture des styles de l'application.

## 4. Typographies

| Usage | Choix proposé | Repli |
| --- | --- | --- |
| Interface, site, documentation, présentations | **Inter** (sans empattement) | `system-ui, sans-serif` |
| Logs, commandes, chemins, YAML et extraits techniques | **JetBrains Mono** | `ui-monospace, monospace` |

**Règles de hiérarchie :**

- Corps de texte : **14–16 px**, interligne confortable (environ **1,5**).
- Titres de page : **24–32 px** ; sous-titres : **18–24 px**.
- Métadonnées : **12–14 px** lorsque la lisibilité est préservée.
- Poids : principalement **400**, **500** et **600** ; éviter les variations gratuites.
- Logs et code : police monospace ; privilégier l'alignement, le retour à la ligne contrôlé et le défilement horizontal si nécessaire.
- Éviter de multiplier les polices, les effets de contour et les capitales prolongées.

Les polices sont **proposées**, pas encore approuvées. Vérifier leurs licences et conditions de redistribution avant toute intégration ou diffusion de fichiers de police.

## 5. Logo et signature visuelle

**Le logo Rustkins reste à concevoir ou à sélectionner.** Aucune forme officielle, icône ou mascotte n'est imposée par cette version de la charte.

Orientations proposées pour sa création :

- **Lisibilité et simplicité** : reconnaissable en petit format (favicon, onglet, avatar).
- **Identité propre** : ne pas reprendre les logos, mascottes ou marques de GitHub, Jenkins ou d'autres outils.
- **Déclinaisons à prévoir** : logotype complet, pictogramme seul, versions sur fonds clairs et sombres.
- **Couleurs** : s'appuyer sur les tons neutres et l'accent bleu clair ; éviter les effets de relief ou dégradés complexes.
- **Zone de protection et taille minimale** : à fixer **après choix du logo**, sans valeurs arbitraires pour le moment.

En attendant, les supports peuvent utiliser un **wordmark textuel « Rustkins »** avec la typographie principale, sans le présenter comme un logo définitif.

## 6. Mise en page et composants

### 6.1. Grille et espacement

- Utiliser une **échelle d'espacement basée sur 4 px** : `4 / 8 / 12 / 16 / 24 / 32 / 48` px.
- Privilégier les alignements stricts, les marges régulières et les blocs bien séparés.
- Favoriser les **bordures fines** et le contraste entre surfaces plutôt que les ombres fortes.
- Arrondis proposés : **6–8 px** pour boutons, champs et cartes ; éviter les arrondis exagérés.
- Conserver une **densité d'information adaptée aux développeurs** : épurée ne signifie pas inutilement vide.

### 6.2. Boutons, liens et formulaires

- **Action principale :** en thème clair, fond `#17688C` et texte `#F3F5F7` ; en thème sombre, fond `#75C9F1` et texte `#181B20`.
- **Action secondaire :** surface neutre, contour discret, libellé explicite.
- **Liens :** teinte interactive lisible selon le thème, soulignement au survol/focus ou autre indice non chromatique.
- **Champs :** bordure visible, libellés persistants, erreurs formulées en texte.
- **Focus clavier :** nettement identifiable sur les deux thèmes ; ne jamais le supprimer sans alternative visible.
- **États désactivés et chargements :** distinguer visuellement l'indisponibilité de l'activité en cours, sans s'appuyer sur l'opacité seule.

### 6.3. Tableaux, pipelines et logs

- **Tableaux :** en-têtes nets, séparateurs discrets, états explicites, informations critiques visibles sans survol.
- **DAG / pipelines :** priorité à la lecture des dépendances et à l'identification de la branche ou du job en échec ; éviter les animations décoratives.
- **Logs :** police monospace, horodatage et niveaux lisibles, possibilité de sélectionner/copier les lignes.
- **Badges de statut :** associer **couleur + icône ou libellé** pour permettre l'identification sans perception de la couleur.
- **Icônes :** style linéaire cohérent, tailles courantes proposées **16 ou 20 px**, sans mélange de styles.

## 7. Photographies, illustrations et communication

Sur le site vitrine, la documentation, les réseaux sociaux et les présentations :

- Privilégier les **captures d'interface authentiques**, schémas d'architecture ou de pipeline et démonstrations contextualisées.
- Utiliser des **fonds neutres**, des titres courts et des touches de bleu clair pour guider la lecture.
- Conserver la même typographie, les mêmes proportions et une hiérarchie claire des contenus.
- Éviter les visuels « hacking » génériques, les faux tableaux de bord et les promesses de vitesse non mesurées.
- Ne pas montrer une fonctionnalité prévue comme si elle était déjà disponible ; identifier les maquettes et prototypes.

La punchline officielle de travail est documentée dans le [positionnement et les messages](../communication/positioning-and-messages.md). Ses usages doivent rester cohérents entre les différents formats.

## 8. Lisibilité et accessibilité

La sobriété visuelle **ne doit pas dégrader l'accessibilité**. Viser au minimum les critères de contraste pertinents des WCAG AA : généralement **4,5:1 pour le texte normal**, **3:1 pour le texte agrandi** et **3:1 pour les éléments graphiques essentiels**.

Quelques **contrastes calculés** pour les associations de couleurs proposées :

| Association | Ratio approximatif |
| --- | ---: |
| Texte principal clair `#202833` sur fond `#F3F5F7` | **13,60:1** |
| Texte secondaire clair `#4D5A69` sur fond `#F3F5F7` | **6,44:1** |
| Texte principal sombre `#E8EDF3` sur fond `#181B20` | **14,66:1** |
| Texte secondaire sombre `#AEB9C7` sur fond `#181B20` | **8,68:1** |
| Bleu clair `#75C9F1` sur fond sombre `#181B20` | **9,36:1** |
| Bleu interactif `#17688C` sur fond clair `#F3F5F7` | **5,66:1** |
| Bleu clair `#75C9F1` sur fond clair `#F3F5F7` | **1,69:1 : insuffisant pour du texte** |

Ces calculs concernent **uniquement les combinaisons affichées**, pas l'ensemble des états, badges ou survols. Vérifier également les couleurs finales dans les maquettes, les tailles réelles, le clavier, les messages d'erreur et le rendu responsive.

## 9. À valider pour stabiliser la charte

Les éléments suivants restent **ouverts** à la validation de l'équipe :

1. **Logo officiel** et ses déclinaisons ; favicon / avatar.
2. **Validation des teintes et tokens**, notamment les variantes d'état, les survols et les bordures.
3. **Choix final des typographies** et règles de chargement.
4. **Composants de référence** (boutons, champs, tableaux, cartes, DAG, vues de logs) dans les deux thèmes.
5. **Gabarits de communication** pour le site vitrine, les présentations et les formats sociaux.

Cette charte est volontairement **évolutive** : elle fournit des valeurs suffisamment concrètes pour concevoir des premiers écrans cohérents, tout en laissant identifiables les choix à arbitrer.

## 10. Références internes

- [Direction artistique](art-direction.md)
- [Positionnement et messages](../communication/positioning-and-messages.md)
- [Communication de Rustkins](../communication/README.md)
- [Roadmap fonctionnelle](../../versions/roadmap.md)
