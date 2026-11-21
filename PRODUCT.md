# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

HTML, CSS et JS sans framework, plus un script de synchronisation (Python ou Node, choisi en P2) qui produit le fichier de données affiché. Choix de Louis (P1, point 8).

## Users

Un seul utilisateur : Louis, étudiant à 42 (niveau 12,44 au 11/11/2026) et en alternance. Il ouvre le tableau de bord de temps en temps pour explorer en détail son réseau de compétences et ses cartes de domaines, sur un écran d'ordinateur.

## Product Purpose

Afficher sa progression en programmation sous une forme gamifiée, dans l'esprit des fenêtres du « Système » de *Solo Leveling* : niveaux, rangs, titres et réseau de compétences. C'est un affichage de l'état réel, pas un outil de recommandation. Il est réussi si chaque valeur affichée est fondée sur une donnée réelle et si l'exploration donne envie de progresser.

## Positioning

Les données viennent du suivi pédagogique réel de Louis (`/professor`) et de son profil 42. Rien n'est saisi à la main dans l'interface, et chaque valeur peut être observée, estimée, insuffisante ou non mesurable : elle s'affiche comme telle, sans valeur inventée.

## Operating Context

- Les données sont rafraîchies par un script lancé en local, puis publiées sur GitHub Pages (site public, non indexé, consulté par Louis seul) ; la page s'ouvre aussi en local.
- Les sources sont les fichiers `/professor` du dépôt `claude_custom_commands` (cartes, notions, relations, événements, `historique-ia.csv`) et l'API de l'intranet 42 (niveau, projets, achievements).

## Capabilities and Constraints

- Deux jauges : le niveau 42 officiel, et un niveau « Système » qui compte toutes les sources, calé pour atteindre 25 en même temps que le niveau 42.
- Rangs par domaine, lus sur les paliers de sa carte : E, D, C, B, A, S, puis Nation (détail dans `docs/plan.md`).
- Deux titres « I AM THE ANSWER » : la version 42 au niveau 42 officiel 25, et la version « Système » avec le rang S sur toutes les cartes. Les achievements de 42, obtenus et non obtenus, servent de titres quand l'API les fournit.
- Réseau de compétences fondé sur les paliers des cartes (débutant, intermédiaire, avancé, transcendée), avec leurs certifications : 16 cartes et 682 notions au 11/11/2026.
- L'XP d'un projet perso ou pro est celle d'un projet 42 comparable, et elle baisse avec la part de l'IA.
- Hors V1 : statistiques détaillées des métriques et recommandations.
- Pas encore décidé : le format exact du fichier de données (P2).

## Brand Commitments

- On s'inspire de l'ambiance et des mécaniques de *Solo Leveling* (fenêtres « Système », rangs, titres), sans reprendre de logo, d'illustration, de police, de nom de personnage ni de texte de l'œuvre.
- Les noms fixés par Louis : « I AM THE ANSWER », les rangs E à S et « Nation », le niveau « Système ».

## Evidence on Hand

- Données réelles : `~/claude_custom_commands/references/professor/suivi/` (16 cartes, 108 notions suivies, 77 relations, 730 événements au 11/11/2026).
- Table XP de 42 : `data/experience_21.json` de 42calculator (GPL-3.0), décrite dans `docs/research/42-api.md`.
- Absents, à ne pas inventer : projets perso et pro évalués, XP « Système » calculée, achievements non obtenus.

## Product Principles

1. Un libellé dit l'état réel : « insuffisant » quand des conditions existent et ne sont pas remplies, « non mesurable » quand aucune mesure ne permet de comparer. Une valeur sans preuve n'est jamais estimée en silence.
2. Le niveau (le parcours accumulé) et le rang (la maîtrise démontrée) restent visuellement distincts.
3. La gamification met en scène des données vraies : elle ne remplace pas la lisibilité.
4. Le réseau de compétences doit se parcourir : lacunes, prérequis et transferts doivent être visibles.

## Accessibility & Inclusion

Aucun besoin particulier déclaré. Socle visé : contraste WCAG AA, navigation au clavier, respect de `prefers-reduced-motion`.
