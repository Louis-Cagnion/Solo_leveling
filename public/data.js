window.SYSTEME = {
 "meta": {
  "schema": "maquette-constellation-1",
  "generatedAt": "2026-11-21T23:38+01:00"
 },
 "counts": {
  "cards": 19,
  "cardNotions": 812,
  "tracked": 179,
  "trackedOnCards": 119,
  "trackedOffCards": 60,
  "relationsRead": 95,
  "relationsRejected": 0,
  "relationsKept": 95
 },
 "sources": [
  {
   "label": "cartes/*.md",
   "status": "ok",
   "read": 19,
   "rejected": 10
  },
  {
   "label": "notions.md",
   "status": "ok",
   "read": 179,
   "rejected": 0
  },
  {
   "label": "relations.csv",
   "status": "ok",
   "read": 95,
   "rejected": 0
  },
  {
   "label": "API de l'intranet 42",
   "status": "unavailable",
   "read": null
  }
 ],
 "states": [
  {
   "label": "découverte",
   "code": "discovered"
  },
  {
   "label": "en cours",
   "code": "in-progress"
  },
  {
   "label": "comprise",
   "code": "understood"
  },
  {
   "label": "appliquée",
   "code": "applied"
  },
  {
   "label": "retenue",
   "code": "retained"
  },
  {
   "label": "transférée",
   "code": "transferred"
  },
  {
   "label": "transcendée",
   "code": "transcended"
  },
  {
   "label": "déclarée",
   "code": "declared"
  },
  {
   "label": "non rencontrée",
   "code": "unmet"
  }
 ],
 "proofOrder": [
  "découverte",
  "en cours",
  "comprise",
  "appliquée",
  "retenue",
  "transférée",
  "transcendée"
 ],
 "rankDThreshold": "comprise",
 "certThreshold": "retenue",
 "linkStatuses": [
  {
   "code": "demonstrated",
   "label": "démontrée"
  },
  {
   "code": "recognized",
   "label": "reconnue"
  },
  {
   "code": "theoretical",
   "label": "théorique"
  }
 ],
 "linkKinds": {
  "prerequis": {
   "label": "prérequis",
   "outgoing": "prérequis de",
   "incoming": "a pour prérequis"
  },
  "transfert": {
   "label": "transfert",
   "outgoing": "se transfère vers",
   "incoming": "reçoit un transfert de"
  },
  "complementaire": {
   "label": "complémentaire",
   "outgoing": "complémentaire de",
   "incoming": "complémentaire de"
  },
  "instance_de": {
   "label": "instance de",
   "outgoing": "instance de",
   "incoming": "a pour instance"
  },
  "analogue": {
   "label": "analogue",
   "outgoing": "analogue à",
   "incoming": "analogue à"
  }
 },
 "levels": {
  "level42": {
   "value": 12.44,
   "status": "observed",
   "reason": "déclaré par Louis le 11/11/2026, API 42 non branchée"
  },
  "xp42": {
   "value": 133834,
   "status": "estimated",
   "reason": "interpolation linéaire dans la table data/experience_21.json de 42calculator, entre le niveau 12 (124446 XP) et le niveau 13 (145782 XP)"
  },
  "systemLevel": {
   "value": 12.44,
   "status": "estimated",
   "reason": "aucun projet perso ou pro enregistré"
  },
  "levelTarget": 25,
  "xpTarget": 777756
 },
 "cards": [
  {
   "id": "algorithmique",
   "name": "Algorithmique",
   "tiers": [
    {
     "code": "beginner",
     "label": "Débutant",
     "notions": [
      "algorithmique-logique-booleenne",
      "algorithmique-lois-de-morgan",
      "algorithmique-complexite",
      "algorithmique-recherches",
      "algorithmique-tris-simples",
      "algorithmique-recursivite",
      "algorithmique-structures-lineaires",
      "algorithmique-invariant-boucle"
     ]
    },
    {
     "code": "intermediate",
     "label": "Intermédiaire",
     "notions": [
      "algorithmique-tris-efficaces",
      "algorithmique-table-hachage",
      "algorithmique-arbres-binaires",
      "algorithmique-graphes-parcours",
      "algorithmique-retour-sur-trace",
      "algorithmique-diviser-regner",
      "algorithmique-glouton",
      "algorithmique-file-priorite",
      "algorithmique-sat-clause-litteral",
      "algorithmique-masques-bits"
     ]
    },
    {
     "code": "advanced",
     "label": "Avancé",
     "notions": [
      "algorithmique-programmation-dynamique",
      "algorithmique-plus-courts-chemins",
      "algorithmique-arbres-equilibres",
      "algorithmique-contraintes",
      "algorithmique-automates",
      "algorithmique-minimax",
      "algorithmique-union-find",
      "algorithmique-analyse-amortie",
      "algorithmique-reduction-sat"
     ]
    },
    {
     "code": "transcended",
     "label": "Transcendée",
     "notions": [
      "algorithmique-np-completude",
      "algorithmique-solveurs-sat",
      "algorithmique-flots",
      "algorithmique-chaines",
      "algorithmique-probabilistes",
      "algorithmique-approximation",
      "algorithmique-structures-cache",
      "algorithmique-calculabilite"
     ]
    }
   ],
   "certifications": [],
   "certificationNote": "(vérifiées le 11/11/2026) : aucune certification reconnue ; preuve publique : classement sur une plateforme de programmation compétitive (Codewars, où Louis a déjà un historique).",
   "rank": {
    "value": "E",
    "status": "observed",
    "reason": "2 notions de la carte suivies (« déclarée » exclue)"
   },
   "nextRank": {
    "rank": "D",
    "condition": "notions débutantes au moins « comprise », aucun fait « niveau validé » enregistré dans /professor",
    "progress": {
     "value": 0,
     "status": "estimated",
     "reason": null
    },
    "total": 8,
    "missing": [
     "algorithmique-logique-booleenne",
     "algorithmique-lois-de-morgan",
     "algorithmique-complexite",
     "algorithmique-recherches",
     "algorithmique-tris-simples",
     "algorithmique-recursivite",
     "algorithmique-structures-lineaires",
     "algorithmique-invariant-boucle"
    ]
   },
   "trackedCount": 2,
   "offCard": [
    "algorithmique-sat-au-plus-un",
    "algorithmique-encodage-sat"
   ]
  },
  {
   "id": "apprentissage-automatique",
   "name": "Apprentissage automatique",
   "tiers": [
    {
     "code": "beginner",
     "label": "Débutant",
     "notions": [
      "ml-numpy-vectorisation",
      "ml-pandas-nettoyage",
      "ml-statistiques-descriptives",
      "ml-visualisation",
      "ml-probabilites",
      "ml-supervise-principe",
      "ml-regression-lineaire",
      "ml-fonction-cout",
      "ml-descente-gradient",
      "ml-normalisation",
      "ml-entrainement-test",
      "ml-surapprentissage"
     ]
    },
    {
     "code": "intermediate",
     "label": "Intermédiaire",
     "notions": [
      "ml-regression-logistique",
      "ml-metriques-classification",
      "ml-validation-croisee",
      "ml-ingenierie-caracteristiques",
      "ml-arbres-forets",
      "ml-clustering",
      "ml-reduction-dimension",
      "ml-perceptron-multicouche",
      "ml-retropropagation",
      "ml-regularisation",
      "ml-optimiseurs",
      "ml-scikit-learn",
      "ml-cnn-images",
      "ml-ia-responsable"
     ]
    },
    {
     "code": "advanced",
     "label": "Avancé",
     "notions": [
      "ml-apprentissage-renforcement",
      "ml-traitement-signal",
      "ml-reseaux-recurrents",
      "ml-pytorch",
      "ml-entrainement-gpu",
      "ml-hyperparametres",
      "ml-desequilibre-classes",
      "ml-pipelines-mlops",
      "ml-service-modeles",
      "ml-surveillance-derive",
      "ml-suivi-experiences",
      "ml-feature-store",
      "ml-solutions-low-code"
     ]
    },
    {
     "code": "transcended",
     "label": "Transcendée",
     "notions": [
      "ml-biais-variance",
      "ml-optimisation-convexe",
      "ml-entrainement-distribue",
      "ml-interpretabilite",
      "ml-modeles-generatifs",
      "ml-inference-bayesienne",
      "ml-auto-supervise",
      "ml-robustesse-adversariale"
     ]
    }
   ],
   "certifications": [
    {
     "label": "Google Cloud Professional Machine Learning Engineer",
     "detail": "Google Cloud Professional Machine Learning Engineer, 50 à 60 questions en 2 h : six compétences évaluées relues le 11/11/2026 sur cloud.google.com/learn/certification/machine-learning-engineer ; guide détaillé (version 3.1, PDF) non lu, à relire.",
     "obtained": {
      "value": null,
      "status": "insufficient",
      "reason": "aucun fait « certification » dans /professor"
     }
    },
    {
     "label": "Partie apprentissage automatique de NCA-GENL (NVIDIA)",
     "detail": "Partie apprentissage automatique de NCA-GENL (NVIDIA) : sources sur la carte LLM.",
     "obtained": {
      "value": null,
      "status": "insufficient",
      "reason": "aucun fait « certification » dans /professor"
     }
    },
    {
     "label": "Non retenues en propre (vérification du 13/11/2026 sur les pages officielles)",
     "detail": "Non retenues en propre (vérification du 13/11/2026 sur les pages officielles) : AWS Machine Learning Engineer, même métier sur une autre plateforme (MLA-C01 retirée en anglais le 28/09/2026, MLA-C02 en bêta à 75 $ depuis le 29/09/2026, docs.aws.amazon.com/aws-certification) ; AWS Certified AI Practitioner AIF-C01 (100 $, en ligne surveillé ou en centre ; IA, IA générative, modèles de fondation, IA responsable, gouvernance) et Microsoft AI-901 (remplace AI-900, retirée le 30/06/2026 ; learn.microsoft.com/credentials/certifications/exams/ai-901), niveau fondamentaux, possibles premières preuves avant la Google ; AI-103 (remplace AI-102, retirée le 30/06/2026), centrée sur Azure.",
     "obtained": {
      "value": null,
      "status": "insufficient",
      "reason": "aucun fait « certification » dans /professor"
     }
    }
   ],
   "certificationNote": "couvertes par cette carte et les cartes LLM (IA générative), Python et SQL",
   "rank": {
    "value": null,
    "status": "observed",
    "reason": "aucune notion de la carte suivie (« déclarée » exclue)"
   },
   "nextRank": {
    "rank": "E",
    "condition": "au moins une notion de la carte suivie (« déclarée » exclue)",
    "progress": {
     "value": 0,
     "status": "observed",
     "reason": null
    },
    "total": null,
    "missing": []
   },
   "trackedCount": 0,
   "offCard": []
  },
  {
   "id": "c",
   "name": "C",
   "tiers": [
    {
     "code": "beginner",
     "label": "Débutant",
     "notions": [
      "c-lexique-identifiants",
      "c-types-variables",
      "c-operateurs-expressions",
      "c-conditions-boucles",
      "c-fonctions-prototypes",
      "c-tableaux-chaines",
      "c-pointeurs",
      "c-preprocesseur-entetes",
      "cpp-compilation-edition-liens"
     ]
    },
    {
     "code": "intermediate",
     "label": "Intermédiaire",
     "notions": [
      "c-allocation-dynamique",
      "c-gestion-memoire-echec",
      "c-structures-unions-enum",
      "c-pointeurs-fonction",
      "c-arithmetique-pointeurs",
      "c-entrees-sorties",
      "c-parseur-fichiers",
      "c-classes-stockage",
      "c-makefile",
      "c-makefile-cibles-factices",
      "c-debogage-outils",
      "linux-bibliotheque-partagee",
      "c-debordements-tampon",
      "c-tri-recherche-stdlib",
      "c-versions-norme"
     ]
    },
    {
     "code": "advanced",
     "label": "Avancé",
     "notions": [
      "c-comportement-indefini",
      "c-alignement-remplissage",
      "c-qualificateurs",
      "c-operations-bits",
      "c-macros-avancees",
      "c-fonctions-variadiques",
      "linux-chargeur-dynamique",
      "c-symboles-sections",
      "c-memoire-processus",
      "c-controle-descripteurs",
      "c-caracteres-larges",
      "c-processus-threads",
      "c-flottants-ieee754",
      "c-sauts-non-locaux",
      "c-declarations-complexes"
     ]
    },
    {
     "code": "transcended",
     "label": "Transcendée",
     "notions": [
      "c-aliasing-strict",
      "c-atomiques-modele-memoire",
      "c-promotions-entieres",
      "c-points-sequence",
      "c-optimiseur",
      "c-allocateur-maison",
      "c-performance-cache",
      "c-durcissement",
      "c-assembleur-en-ligne",
      "c-precision-arbitraire"
     ]
    }
   ],
   "certifications": [
    {
     "label": "CLA",
     "detail": "CLA, C++ Institute / OpenEDG, version CLA-11-03 : programme relu le 11/11/2026 puis le 14/11/2026 (texte brut de cppinstitute.org/cla) ; examen : 40 questions, 65 min, réussite 70%, examen à partir de 325 USD, QCM à choix unique ou multiple, en anglais ; cours gratuits associés : C Essentials 2 (Cisco Networking Academy, OpenEDG Edube).",
     "obtained": {
      "value": null,
      "status": "insufficient",
      "reason": "aucun fait « certification » dans /professor"
     }
    },
    {
     "label": "CLP",
     "detail": "CLP, C++ Institute / OpenEDG, version CLP-12-01, CLA recommandée avant : programme relu le 11/11/2026 puis le 14/11/2026 (texte brut de cppinstitute.org/clp) ; examen : 55 questions, 65 min, réussite 70%, examen à partir de 325 USD.",
     "obtained": {
      "value": null,
      "status": "insufficient",
      "reason": "aucun fait « certification » dans /professor"
     }
    }
   ],
   "certificationNote": "couvertes par cette carte, la carte Réseau (sockets) et la carte Noyau et assembleur (boutisme)",
   "rank": {
    "value": "E",
    "status": "observed",
    "reason": "23 notions de la carte suivies (« déclarée » exclue)"
   },
   "nextRank": {
    "rank": "D",
    "condition": "notions débutantes au moins « comprise », aucun fait « niveau validé » enregistré dans /professor",
    "progress": {
     "value": 4,
     "status": "estimated",
     "reason": null
    },
    "total": 9,
    "missing": [
     "c-lexique-identifiants",
     "c-types-variables",
     "c-operateurs-expressions",
     "c-conditions-boucles",
     "cpp-compilation-edition-liens"
    ]
   },
   "trackedCount": 23,
   "offCard": [
    "linux-compilateur-variable-cc"
   ]
  },
  {
   "id": "cpp",
   "name": "C++",
   "tiers": [
    {
     "code": "beginner",
     "label": "Débutant",
     "notions": [
      "cpp-types-litteraux",
      "cpp-classes-objets",
      "cpp-constructeurs-destructeur",
      "cpp-references",
      "cpp-surcharge",
      "cpp-flux-iostream",
      "cpp-constexpr-portee",
      "cpp-new-delete",
      "cpp-string",
      "cpp-membres-const-amis"
     ]
    },
    {
     "code": "intermediate",
     "label": "Intermédiaire",
     "notions": [
      "cpp-forme-canonique",
      "cpp-heritage-polymorphisme",
      "cpp-classes-abstraites",
      "cpp-heritage-multiple",
      "cpp-exceptions-try-catch",
      "cpp-conversion-stricte-stoi",
      "cpp-templates",
      "cpp-casts",
      "cpp-raii",
      "cpp-conteneurs-sequence",
      "cpp-conteneurs-associatifs",
      "cpp-iterateurs",
      "cpp-algorithmes-non-modifiants",
      "cpp-algorithmes-modifiants"
     ]
    },
    {
     "code": "advanced",
     "label": "Avancé",
     "notions": [
      "cpp-algorithmes-tri-recherche",
      "cpp-algorithmes-fusion-tas",
      "cpp-foncteurs-adaptateurs",
      "cpp-flux-formatage",
      "cpp-pointeurs-intelligents",
      "cpp-semantique-deplacement",
      "cpp-lambdas",
      "cpp-auto-inference",
      "cpp-specialisation-templates",
      "cpp-garanties-exceptions",
      "cpp-complexite-invalidation",
      "cpp-threads",
      "cpp-calcul-compilation"
     ]
    },
    {
     "code": "transcended",
     "label": "Transcendée",
     "notions": [
      "cpp-sfinae-concepts",
      "cpp-templates-variadiques",
      "cpp-categories-valeurs",
      "cpp-modele-objet",
      "cpp-atomiques",
      "cpp-allocateurs",
      "cpp-odr-liaison",
      "cpp-ranges-coroutines"
     ]
    }
   ],
   "certifications": [
    {
     "label": "CPA",
     "detail": "CPA, C++ Institute / OpenEDG, version CPA-21-02 : programme relu le 11/11/2026 puis le 14/11/2026 (texte brut de cppinstitute.org/cpa ; CPA-21-02 active, CPA-21-01 retirée) ; examen : 40 questions, 65 min, réussite 70%, examen à partir de 325 USD, QCM à choix unique ou multiple.",
     "obtained": {
      "value": null,
      "status": "insufficient",
      "reason": "aucun fait « certification » dans /professor"
     }
    },
    {
     "label": "CPP",
     "detail": "CPP, C++ Institute / OpenEDG, version CPP-22-02, CPA prérequis : programme relu le 11/11/2026 puis le 14/11/2026 (texte brut de cppinstitute.org/cpp) ; examen : 40 questions, 65 min, réussite 70%, examen à partir de 325 USD.",
     "obtained": {
      "value": null,
      "status": "insufficient",
      "reason": "aucun fait « certification » dans /professor"
     }
    }
   ],
   "certificationNote": "couvertes par cette carte et la carte C (types, contrôle, pointeurs, préprocesseur)",
   "rank": {
    "value": "E",
    "status": "observed",
    "reason": "18 notions de la carte suivies (« déclarée » exclue)"
   },
   "nextRank": {
    "rank": "D",
    "condition": "notions débutantes au moins « comprise », aucun fait « niveau validé » enregistré dans /professor",
    "progress": {
     "value": 4,
     "status": "estimated",
     "reason": null
    },
    "total": 10,
    "missing": [
     "cpp-types-litteraux",
     "cpp-references",
     "cpp-flux-iostream",
     "cpp-new-delete",
     "cpp-string",
     "cpp-membres-const-amis"
    ]
   },
   "trackedCount": 18,
   "offCard": []
  },
  {
   "id": "developpement-web",
   "name": "Développement web (serveur)",
   "tiers": [
    {
     "code": "beginner",
     "label": "Débutant",
     "notions": [
      "web-client-serveur",
      "web-routage",
      "web-mvc",
      "web-structure-framework",
      "web-gabarits",
      "web-formulaires-validation",
      "web-configuration",
      "web-json-api",
      "web-gestion-erreurs",
      "web-fichiers-statiques"
     ]
    },
    {
     "code": "intermediate",
     "label": "Intermédiaire",
     "notions": [
      "web-orm",
      "web-migrations",
      "web-sessions-authentification",
      "web-mots-de-passe",
      "web-autorisation",
      "web-api-rest",
      "web-intergiciels",
      "web-securite-owasp",
      "web-cors",
      "web-televersement",
      "web-courriels",
      "web-tests-integration",
      "web-commandes-console"
     ]
    },
    {
     "code": "advanced",
     "label": "Avancé",
     "notions": [
      "web-oauth-oidc",
      "web-jwt",
      "web-temps-reel",
      "web-taches-fond",
      "web-cache",
      "web-streaming-media",
      "web-limitation-debit",
      "web-graphql",
      "web-rendu-serveur-spa",
      "web-deploiement",
      "web-observabilite",
      "web-tests-bout-en-bout"
     ]
    },
    {
     "code": "transcended",
     "label": "Transcendée",
     "notions": [
      "web-architecture-distribuee",
      "web-idempotence-sagas",
      "web-montee-charge",
      "web-securite-avancee",
      "web-performance-serveur",
      "web-cqrs-evenements",
      "web-pubsub-distribue",
      "web-evolution-api"
     ]
    }
   ],
   "certifications": [
    {
     "label": "SYMF",
     "detail": "SYMF, Symfony Certification (SensioLabs), Symfony 6.0 à 8.0, 250 €, en ligne surveillée par webcam, 75 questions en 90 min : 14 thèmes relus le 13/11/2026 sur certification.symfony.com/exams/symfony.html.",
     "obtained": {
      "value": null,
      "status": "insufficient",
      "reason": "aucun fait « certification » dans /professor"
     }
    },
    {
     "label": "FCC-BE",
     "detail": "FCC-BE, freeCodeCamp « Back-End Development and APIs » v9, gratuite : chapitres relus le 13/11/2026 (Node.js, npm, HTTP, Express, intergiciels, API REST, gestion d'erreurs, WebSockets, sécurité, authentification).",
     "obtained": {
      "value": null,
      "status": "insufficient",
      "reason": "aucun fait « certification » dans /professor"
     }
    }
   ],
   "certificationNote": "couvertes par cette carte et les cartes PHP (Symfony), Réseau (HTTP) et JavaScript et TypeScript (Node.js de freeCodeCamp)",
   "rank": {
    "value": null,
    "status": "observed",
    "reason": "aucune notion de la carte suivie (« déclarée » exclue)"
   },
   "nextRank": {
    "rank": "E",
    "condition": "au moins une notion de la carte suivie (« déclarée » exclue)",
    "progress": {
     "value": 0,
     "status": "observed",
     "reason": null
    },
    "total": null,
    "missing": []
   },
   "trackedCount": 0,
   "offCard": []
  },
  {
   "id": "docker",
   "name": "Docker",
   "tiers": [
    {
     "code": "beginner",
     "label": "Débutant",
     "notions": [
      "docker-image-conteneur",
      "docker-conteneur-processus-isole",
      "docker-dockerfile",
      "docker-cycle-vie",
      "docker-publication-ports",
      "docker-bind-mount",
      "docker-volume-nomme-vs-bind",
      "docker-variables-environnement"
     ]
    },
    {
     "code": "intermediate",
     "label": "Intermédiaire",
     "notions": [
      "docker-reseau-isole",
      "docker-service-reseau-volume",
      "docker-compose-dependances",
      "docker-pid1-init",
      "docker-idempotence-demarrage",
      "docker-couches-cache",
      "docker-conteneur-root-defaut",
      "docker-secrets",
      "docker-healthcheck",
      "docker-registre-etiquettes",
      "docker-installation-demon"
     ]
    },
    {
     "code": "advanced",
     "label": "Avancé",
     "notions": [
      "docker-multi-etapes",
      "docker-image-minimale",
      "docker-pilotes-reseau",
      "docker-pilotes-stockage",
      "docker-limites-ressources",
      "docker-rootless-capacites",
      "docker-journalisation",
      "docker-construction-reproductible",
      "docker-swarm",
      "docker-kubernetes-bases"
     ]
    },
    {
     "code": "transcended",
     "label": "Transcendée",
     "notions": [
      "docker-oci-runtime",
      "docker-plateforme-entreprise",
      "docker-seccomp-apparmor",
      "docker-chaine-approvisionnement",
      "docker-reseau-internes",
      "docker-demon-socket",
      "docker-multi-architecture",
      "docker-debogage"
     ]
    }
   ],
   "certifications": [
    {
     "label": "Docker Certified Associate (DCA)",
     "detail": "Docker Certified Associate (DCA), Mirantis, valable 2 ans : page d'examen relue le 11/11/2026 (training.mirantis.com/certification/dca-certification-exam, inscription ouverte) ; six domaines (orchestration 25 %, images et registre 20 %, installation et configuration 15 %, réseau 15 %, sécurité 15 %, stockage 10 %) pris du guide d'étude officiel v1.4 tel que repris par des guides tiers, guide non lu : à relire à la prochaine vérification.",
     "obtained": {
      "value": null,
      "status": "insufficient",
      "reason": "aucun fait « certification » dans /professor"
     }
    }
   ],
   "certificationNote": "",
   "rank": {
    "value": "E",
    "status": "observed",
    "reason": "9 notions de la carte suivies (« déclarée » exclue)"
   },
   "nextRank": {
    "rank": "D",
    "condition": "notions débutantes au moins « comprise », aucun fait « niveau validé » enregistré dans /professor",
    "progress": {
     "value": 4,
     "status": "estimated",
     "reason": null
    },
    "total": 8,
    "missing": [
     "docker-dockerfile",
     "docker-cycle-vie",
     "docker-publication-ports",
     "docker-variables-environnement"
    ]
   },
   "trackedCount": 9,
   "offCard": [
    "docker-compose-v1-v2",
    "docker-monit-configuration",
    "docker-modele-envsubst"
   ]
  },
  {
   "id": "infographie-3d",
   "name": "Infographie 3D",
   "tiers": [
    {
     "code": "beginner",
     "label": "Débutant",
     "notions": [
      "infographie-pixels-couleurs",
      "infographie-vecteurs",
      "infographie-reperes",
      "infographie-maillage",
      "cpp-boucle-de-jeu",
      "cpp-double-tampon",
      "cpp-vitesse-deltatime-diagonale",
      "c-entrees-clavier-souris"
     ]
    },
    {
     "code": "intermediate",
     "label": "Intermédiaire",
     "notions": [
      "c-matrices-transformation",
      "c-pipeline-opengl",
      "infographie-glsl",
      "c-eclairage-textures",
      "infographie-tampon-profondeur",
      "c-triangulation-ear-clipping",
      "infographie-modele-hierarchique",
      "infographie-images-cles",
      "infographie-collisions"
     ]
    },
    {
     "code": "advanced",
     "label": "Avancé",
     "notions": [
      "infographie-quaternions",
      "infographie-phong",
      "infographie-matrice-normales",
      "infographie-filtrage-textures",
      "infographie-graphe-scene",
      "infographie-squelette",
      "infographie-instanciation",
      "infographie-transparence",
      "infographie-ombres"
     ]
    },
    {
     "code": "transcended",
     "label": "Transcendée",
     "notions": [
      "infographie-pbr",
      "infographie-rendu-differe",
      "infographie-gpu-internes",
      "infographie-precision-profondeur",
      "infographie-gamma",
      "infographie-elimination-lod",
      "infographie-api-bas-niveau",
      "infographie-pas-fixe"
     ]
    }
   ],
   "certifications": [],
   "certificationNote": "(vérifiées le 11/11/2026) : aucune certification reconnue pour le rendu 3D ; preuve publique : `scop`, `humangl` et `bomberman` au Portfolio, avec démonstration jouable.",
   "rank": {
    "value": "E",
    "status": "observed",
    "reason": "7 notions de la carte suivies (« déclarée » exclue)"
   },
   "nextRank": {
    "rank": "D",
    "condition": "notions débutantes au moins « comprise », aucun fait « niveau validé » enregistré dans /professor",
    "progress": {
     "value": 1,
     "status": "estimated",
     "reason": null
    },
    "total": 8,
    "missing": [
     "infographie-pixels-couleurs",
     "infographie-vecteurs",
     "infographie-reperes",
     "infographie-maillage",
     "cpp-double-tampon",
     "cpp-vitesse-deltatime-diagonale",
     "c-entrees-clavier-souris"
    ]
   },
   "trackedCount": 8,
   "offCard": []
  },
  {
   "id": "javascript",
   "name": "JavaScript et TypeScript",
   "tiers": [
    {
     "code": "beginner",
     "label": "Débutant",
     "notions": [
      "js-types-valeurs",
      "js-portee-declarations",
      "js-coercition-egalite",
      "js-operateurs-interaction",
      "js-conditions-boucles",
      "js-fonctions",
      "js-tableaux",
      "js-objets-litteraux",
      "js-chaines-gabarits",
      "js-exceptions-debogage",
      "js-dom-evenements",
      "js-modules-es"
     ]
    },
    {
     "code": "intermediate",
     "label": "Intermédiaire",
     "notions": [
      "js-fermetures",
      "js-this-liaison",
      "js-prototypes",
      "js-classes",
      "js-destructuration",
      "js-objets-natifs",
      "js-iterateurs-generateurs",
      "js-promesses",
      "js-async-await",
      "js-boucle-evenements",
      "js-fetch",
      "js-node-npm",
      "ts-types-interfaces",
      "ts-generiques"
     ]
    },
    {
     "code": "advanced",
     "label": "Avancé",
     "notions": [
      "js-fonctionnel",
      "js-composants-interface",
      "js-etat-application",
      "js-tests",
      "js-outils-construction",
      "ts-types-avances",
      "ts-configuration",
      "js-securite-navigateur",
      "js-canvas-animation",
      "js-erreurs-asynchrones",
      "js-mobile-multiplateforme",
      "js-proxy-reflect"
     ]
    },
    {
     "code": "transcended",
     "label": "Transcendée",
     "notions": [
      "js-moteur-jit",
      "js-specification",
      "js-node-libuv",
      "js-workers-memoire-partagee",
      "js-ramasse-miettes",
      "js-interop-modules",
      "ts-compilateur",
      "js-webassembly"
     ]
    }
   ],
   "certifications": [
    {
     "label": "JSE",
     "detail": "JSE, JS Institute / OpenEDG, version JSE-40-01 (programme du 22/09/2025), à partir de 69 $, OpenEDG Testing Service (TestNow) : sections relues le 13/11/2026 sur jsinstitute.org/jse-exam-syllabus.",
     "obtained": {
      "value": null,
      "status": "insufficient",
      "reason": "aucun fait « certification » dans /professor"
     }
    },
    {
     "label": "JSA",
     "detail": "JSA, version JSA-41-01 (mise à jour du 22/09/2025), à partir de 295 $, en ligne surveillé (OnVUE) ou en centre (Pearson VUE), 40 questions, seuil 70 % : sections relues le 13/11/2026 sur jsinstitute.org/jsa-exam-syllabus.",
     "obtained": {
      "value": null,
      "status": "insufficient",
      "reason": "aucun fait « certification » dans /professor"
     }
    }
   ],
   "certificationNote": "couvertes par cette carte",
   "rank": {
    "value": null,
    "status": "observed",
    "reason": "aucune notion de la carte suivie (« déclarée » exclue)"
   },
   "nextRank": {
    "rank": "E",
    "condition": "au moins une notion de la carte suivie (« déclarée » exclue)",
    "progress": {
     "value": 0,
     "status": "observed",
     "reason": null
    },
    "total": null,
    "missing": []
   },
   "trackedCount": 0,
   "offCard": []
  },
  {
   "id": "linux-systeme",
   "name": "Linux (système)",
   "tiers": [
    {
     "code": "beginner",
     "label": "Débutant",
     "notions": [
      "linux-noyau-distribution",
      "linux-hierarchie-fichiers",
      "linux-utilisateur-droits",
      "linux-processus",
      "linux-variable-environnement",
      "linux-path",
      "linux-liens-physiques-symboliques",
      "linux-partition",
      "linux-gestion-paquets",
      "linux-somme-de-controle",
      "linux-archives-compression",
      "linux-editeur-texte",
      "linux-peripheriques-detection"
     ]
    },
    {
     "code": "intermediate",
     "label": "Intermédiaire",
     "notions": [
      "linux-montage-ordre-visibilite",
      "linux-fstab",
      "linux-systemes-fichiers",
      "linux-systemes-fichiers-virtuels",
      "linux-udev-devtmpfs",
      "linux-signaux-processus",
      "linux-demarrage",
      "linux-grub-amorcage",
      "linux-init-systemd",
      "linux-journaux-systeme",
      "linux-planification-taches",
      "linux-utilisateurs-groupes",
      "linux-swap",
      "linux-tables-partitions",
      "linux-umask-bits-speciaux"
     ]
    },
    {
     "code": "advanced",
     "label": "Avancé",
     "notions": [
      "linux-configure-script",
      "linux-chroot",
      "linux-lvm-raid",
      "linux-namespaces-cgroups",
      "linux-setuid-capacites",
      "linux-diagnostic-performance",
      "linux-virtualisation-hote-invite",
      "linux-recuperation-demarrage",
      "linux-selinux-administration",
      "linux-limites-ressources",
      "linux-acl",
      "linux-git-administration",
      "linux-affichage-x11",
      "linux-localisation",
      "linux-gpg-chiffrement"
     ]
    },
    {
     "code": "transcended",
     "label": "Transcendée",
     "notions": [
      "linux-securite-mac",
      "linux-ordonnanceur-priorites",
      "linux-memoire-virtuelle-admin",
      "linux-tracage-ebpf",
      "linux-sysctl-reglages"
     ]
    }
   ],
   "certifications": [
    {
     "label": "RHCSA",
     "detail": "RHCSA, Red Hat, examen pratique EX200 sur RHEL 10 : objectifs relus le 11/11/2026 sur redhat.com/en/services/training/ex200-red-hat-certified-system-administrator-rhcsa-exam.",
     "obtained": {
      "value": null,
      "status": "insufficient",
      "reason": "aucun fait « certification » dans /professor"
     }
    },
    {
     "label": "LFCS",
     "detail": "LFCS, Linux Foundation, examen pratique indépendant de la distribution (aucun numéro de version publié) : domaines relus le 11/11/2026 sur training.linuxfoundation.org/certification/linux-foundation-certified-sysadmin-lfcs.",
     "obtained": {
      "value": null,
      "status": "insufficient",
      "reason": "aucun fait « certification » dans /professor"
     }
    },
    {
     "label": "LPIC-1",
     "detail": "LPIC-1, LPI, version 5.0 (examens 101-500 et 102-500) : objectifs relus le 11/11/2026 sur lpi.org (101) et wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0 (102).",
     "obtained": {
      "value": null,
      "status": "insufficient",
      "reason": "aucun fait « certification » dans /professor"
     }
    }
   ],
   "certificationNote": "couvertes par cette carte et les cartes Shell, Réseau, C (bibliothèques partagées) et Docker (moteurs de conteneurs)",
   "rank": {
    "value": "E",
    "status": "observed",
    "reason": "19 notions de la carte suivies (« déclarée » exclue)"
   },
   "nextRank": {
    "rank": "D",
    "condition": "notions débutantes au moins « comprise », aucun fait « niveau validé » enregistré dans /professor",
    "progress": {
     "value": 1,
     "status": "estimated",
     "reason": null
    },
    "total": 13,
    "missing": [
     "linux-noyau-distribution",
     "linux-hierarchie-fichiers",
     "linux-utilisateur-droits",
     "linux-processus",
     "linux-path",
     "linux-liens-physiques-symboliques",
     "linux-partition",
     "linux-gestion-paquets",
     "linux-somme-de-controle",
     "linux-archives-compression",
     "linux-editeur-texte",
     "linux-peripheriques-detection"
    ]
   },
   "trackedCount": 19,
   "offCard": [
    "linux-compilation-croisee",
    "linux-build-host",
    "linux-destdir",
    "linux-alignement-partition",
    "linux-qcow2-snapshot",
    "linux-boot-separee",
    "linux-hierarchie-liens-usr",
    "linux-lib64-interpreteur",
    "linux-hierarchie-limitee-tools",
    "linux-utilisateur-non-privilegie",
    "linux-environnement-construction",
    "linux-chaine-croisee-binutils",
    "linux-prerequis-hote",
    "linux-mesure-sbu-parallelisme",
    "linux-gcc-passe1",
    "linux-api-headers",
    "linux-glibc-contenu",
    "linux-libstdcpp",
    "linux-tic-natif",
    "linux-fichiers-la-libtool",
    "linux-fichiers-essentiels",
    "linux-suite-tests-resultats",
    "linux-tests-chronometres-parallelisme",
    "linux-comparer-journaux-reference",
    "linux-sysv-init",
    "linux-telechargement-sans-client",
    "linux-qemu-captures",
    "linux-demarche-echec-compilation",
    "linux-noyau-secours",
    "linux-qemu-port-serie",
    "linux-certificats-https",
    "linux-sudo-wheel",
    "linux-tty-terminaux",
    "linux-bus-usb-hote"
   ]
  },
  {
   "id": "llm",
   "name": "LLM",
   "tiers": [
    {
     "code": "beginner",
     "label": "Débutant",
     "notions": [
      "llm-prediction-jeton",
      "llm-tokenisation",
      "llm-prompt-bases",
      "llm-api-parametres",
      "llm-fenetre-contexte",
      "llm-hallucinations",
      "llm-embeddings",
      "llm-few-shot",
      "llm-sorties-structurees",
      "llm-cas-usage"
     ]
    },
    {
     "code": "intermediate",
     "label": "Intermédiaire",
     "notions": [
      "llm-chaine-pensee",
      "llm-rag",
      "llm-bases-vectorielles",
      "llm-decoupage-curation",
      "llm-appel-outils",
      "llm-agents",
      "llm-evaluation",
      "llm-transformeur",
      "llm-attention",
      "llm-preparation-donnees",
      "llm-garde-fous",
      "llm-bibliotheques-nlp",
      "llm-cout-latence"
     ]
    },
    {
     "code": "advanced",
     "label": "Avancé",
     "notions": [
      "llm-pre-entrainement",
      "llm-fine-tuning",
      "llm-peft-lora",
      "llm-alignement-rlhf",
      "llm-adaptation-domaine",
      "llm-echantillonnage",
      "llm-quantification",
      "llm-service-inference",
      "llm-batching-cache-kv",
      "llm-surveillance-production",
      "llm-cadre-evaluation",
      "llm-securite-adversariale",
      "llm-audit-biais",
      "llm-multimodal"
     ]
    },
    {
     "code": "transcended",
     "label": "Transcendée",
     "notions": [
      "llm-parallelisme-distribue",
      "llm-optimisation-gpu",
      "llm-lois-echelle",
      "llm-melange-experts",
      "llm-contextes-longs",
      "llm-decodage-speculatif",
      "llm-distillation",
      "llm-interpretabilite-mecaniste",
      "llm-compilation-inference",
      "llm-modeles-raisonnement"
     ]
    }
   ],
   "certifications": [
    {
     "label": "NVIDIA-Certified Associate: Generative AI LLMs (NCA-GENL)",
     "detail": "NVIDIA-Certified Associate: Generative AI LLMs (NCA-GENL), 50 à 60 questions en 1 h, valable 2 ans : programme relu le 11/11/2026 sur nvidia.com/en-us/learn/certification/generative-ai-llm-associate.",
     "obtained": {
      "value": null,
      "status": "insufficient",
      "reason": "aucun fait « certification » dans /professor"
     }
    },
    {
     "label": "NVIDIA-Certified Professional: Generative AI LLMs (NCP-GENL)",
     "detail": "NVIDIA-Certified Professional: Generative AI LLMs (NCP-GENL), 60 à 70 questions en 2 h, valable 2 ans, 2 à 3 ans de pratique recommandés : programme relu le 11/11/2026 sur nvidia.com/en-us/learn/certification/generative-ai-llm-professional ; la ligne « Fine-Tuning » (13 %) de la page affiche un texte sans rapport (erreur de la page), objectifs pris des prérequis (fine-tuning à paramètres efficaces), à relire.",
     "obtained": {
      "value": null,
      "status": "insufficient",
      "reason": "aucun fait « certification » dans /professor"
     }
    }
   ],
   "certificationNote": "couvertes par cette carte et les cartes Apprentissage automatique (bases, analyse de données), Python et Docker (conteneurs)",
   "rank": {
    "value": null,
    "status": "observed",
    "reason": "aucune notion de la carte suivie (« déclarée » exclue)"
   },
   "nextRank": {
    "rank": "E",
    "condition": "au moins une notion de la carte suivie (« déclarée » exclue)",
    "progress": {
     "value": 0,
     "status": "observed",
     "reason": null
    },
    "total": null,
    "missing": []
   },
   "trackedCount": 0,
   "offCard": []
  },
  {
   "id": "mathematiques-ia",
   "name": "Mathématiques pour l'IA",
   "tiers": [
    {
     "code": "beginner",
     "label": "Débutant",
     "notions": [
      "maths-notations",
      "maths-vecteurs",
      "maths-matrices",
      "maths-produit-scalaire",
      "maths-fonctions-usuelles",
      "maths-derivee",
      "maths-pourcentages-erreurs",
      "maths-esperance-variance",
      "maths-logique-booleenne",
      "maths-ensembles"
     ]
    },
    {
     "code": "intermediate",
     "label": "Intermédiaire",
     "notions": [
      "maths-produit-matriciel",
      "maths-systemes-lineaires",
      "maths-determinant-inverse",
      "maths-derivees-partielles",
      "maths-regle-chaine",
      "maths-lois-probabilite",
      "maths-probabilites-conditionnelles",
      "maths-covariance-correlation",
      "maths-vraisemblance",
      "maths-sigmoide-softmax",
      "maths-entropie-croisee",
      "maths-projections"
     ]
    },
    {
     "code": "advanced",
     "label": "Avancé",
     "notions": [
      "maths-espaces-vectoriels",
      "maths-valeurs-propres",
      "maths-svd",
      "maths-jacobienne-hessienne",
      "maths-convexite",
      "maths-series-fourier",
      "maths-tests-statistiques",
      "maths-nombres-complexes",
      "maths-interpolation-lineaire",
      "maths-normes-matricielles",
      "maths-algebre-ensembles"
     ]
    },
    {
     "code": "transcended",
     "label": "Transcendée",
     "notions": [
      "maths-calcul-tensoriel",
      "maths-theorie-information",
      "maths-chaines-markov",
      "maths-optimisation-contrainte",
      "maths-stabilite-numerique",
      "maths-convergence",
      "maths-noyaux",
      "maths-geometrie-grande-dimension",
      "maths-differentiation-automatique",
      "maths-transformee-discrete",
      "maths-matrices-aleatoires"
     ]
    }
   ],
   "certifications": [],
   "certificationNote": "aucune certification reconnue propre aux mathématiques pour l'IA (vérification du 13/11/2026, ci-dessous) ; preuve publique : `matrix`, `ready-set-boole` et la chaîne ML du RNCP7 au Portfolio.",
   "rank": {
    "value": null,
    "status": "observed",
    "reason": "aucune notion de la carte suivie (« déclarée » exclue)"
   },
   "nextRank": {
    "rank": "E",
    "condition": "au moins une notion de la carte suivie (« déclarée » exclue)",
    "progress": {
     "value": 0,
     "status": "observed",
     "reason": null
    },
    "total": null,
    "missing": []
   },
   "trackedCount": 0,
   "offCard": []
  },
  {
   "id": "noyau-assembleur",
   "name": "Noyau et assembleur",
   "tiers": [
    {
     "code": "beginner",
     "label": "Débutant",
     "notions": [
      "linux-materiel-composants",
      "linux-chaine-disque-reseau",
      "noyau-binaire-hexadecimal",
      "noyau-registres-pile-x86",
      "noyau-instructions-base",
      "noyau-espace-noyau-utilisateur",
      "linux-modules-noyau",
      "linux-noyau-configuration",
      "noyau-module-premier",
      "noyau-module-kbuild",
      "noyau-version-noyau"
     ]
    },
    {
     "code": "intermediate",
     "label": "Intermédiaire",
     "notions": [
      "noyau-convention-appel",
      "noyau-multiboot-grub",
      "noyau-script-edition-liens",
      "noyau-compilation-autonome",
      "noyau-memoire-video-texte",
      "noyau-ports-entree-sortie",
      "noyau-gdt-segmentation",
      "noyau-interruptions-idt",
      "noyau-pagination",
      "noyau-allocateur-memoire",
      "noyau-appels-systeme",
      "noyau-pilote-caractere",
      "noyau-interfaces-utilisateur",
      "noyau-style-code",
      "noyau-patch"
     ]
    },
    {
     "code": "advanced",
     "label": "Avancé",
     "notions": [
      "noyau-processus-structure",
      "noyau-ordonnancement-contexte",
      "noyau-fork-exec-wait",
      "noyau-signaux",
      "noyau-ata-ide",
      "noyau-ext2",
      "noyau-vfs",
      "noyau-ipc-sockets",
      "noyau-elf-chargeur",
      "noyau-api-modules",
      "noyau-chargement-automatique",
      "noyau-concurrence"
     ]
    },
    {
     "code": "transcended",
     "label": "Transcendée",
     "notions": [
      "noyau-copie-sur-ecriture",
      "noyau-tlb-caches",
      "noyau-mode-long",
      "noyau-smp-apic",
      "noyau-rcu-barrieres",
      "noyau-dma-pilotes-bloc",
      "noyau-debogage",
      "noyau-protections"
     ]
    }
   ],
   "certifications": [],
   "certificationNote": "(vérifiées le 11/11/2026) : aucune certification reconnue pour le développement du noyau ; preuve publique : un patch accepté dans le noyau Linux (historique Git public), et les projets `kfs` au Portfolio.",
   "rank": {
    "value": "E",
    "status": "observed",
    "reason": "9 notions de la carte suivies (« déclarée » exclue)"
   },
   "nextRank": {
    "rank": "D",
    "condition": "notions débutantes au moins « comprise », aucun fait « niveau validé » enregistré dans /professor",
    "progress": {
     "value": 5,
     "status": "estimated",
     "reason": null
    },
    "total": 11,
    "missing": [
     "noyau-binaire-hexadecimal",
     "noyau-registres-pile-x86",
     "noyau-instructions-base",
     "noyau-espace-noyau-utilisateur",
     "linux-modules-noyau",
     "linux-noyau-configuration"
    ]
   },
   "trackedCount": 9,
   "offCard": [
    "linux-32-64-bits",
    "linux-arbre-noyau-stable",
    "linux-localversion-auto",
    "linux-bzimage-vmlinux"
   ]
  },
  {
   "id": "php",
   "name": "PHP",
   "tiers": [
    {
     "code": "beginner",
     "label": "Débutant",
     "notions": [
      "php-variables-types",
      "php-tableaux",
      "php-fonctions",
      "php-conditions-boucles",
      "php-chaines",
      "php-requete-reponse",
      "php-inclusion",
      "php-erreurs"
     ]
    },
    {
     "code": "intermediate",
     "label": "Intermédiaire",
     "notions": [
      "php-classes-objets",
      "php-espaces-noms-autoload",
      "php-composer",
      "php-pdo-requetes-preparees",
      "php-sessions-cookies",
      "php-exceptions",
      "php-xss-csrf",
      "php-typage-strict",
      "php-framework-cms",
      "php-tests-phpunit",
      "php-formats-donnees",
      "php-formulaires-en-tetes",
      "php-expressions-regulieres",
      "php-mots-de-passe"
     ]
    },
    {
     "code": "advanced",
     "label": "Avancé",
     "notions": [
      "php-interfaces-traits",
      "php-injection-dependances",
      "php-generateurs",
      "php-psr",
      "php-opcache",
      "php-closures",
      "php-nouveautes-8",
      "php-api-rest",
      "php-flux-fichiers",
      "php-spl"
     ]
    },
    {
     "code": "transcended",
     "label": "Transcendée",
     "notions": [
      "php-moteur-zend",
      "php-fpm",
      "php-profilage",
      "php-reflexion-attributs",
      "php-analyse-statique",
      "php-asynchrone",
      "php-deserialisation",
      "php-jit"
     ]
    }
   ],
   "certifications": [
    {
     "label": "Zend Certified PHP Engineer",
     "detail": "Zend Certified PHP Engineer, Zend / Perforce, réintroduite en 2025, programme jusqu'à PHP 8.4 : thèmes relus le 11/11/2026 sur zend.com/training/php-certification-exam (sans sous-thèmes publiés).",
     "obtained": {
      "value": null,
      "status": "insufficient",
      "reason": "aucun fait « certification » dans /professor"
     }
    }
   ],
   "certificationNote": "",
   "rank": {
    "value": null,
    "status": "observed",
    "reason": "aucune notion de la carte suivie (« déclarée » exclue)"
   },
   "nextRank": {
    "rank": "E",
    "condition": "au moins une notion de la carte suivie (« déclarée » exclue)",
    "progress": {
     "value": 0,
     "status": "observed",
     "reason": null
    },
    "total": null,
    "missing": []
   },
   "trackedCount": 0,
   "offCard": [
    "drupal-multisite",
    "drupal-module",
    "drupal-drush"
   ]
  },
  {
   "id": "programmation-fonctionnelle",
   "name": "Programmation fonctionnelle",
   "tiers": [
    {
     "code": "beginner",
     "label": "Débutant",
     "notions": [
      "fonctionnel-expressions-liaisons",
      "fonctionnel-types-inference",
      "fonctionnel-fonctions-valeurs",
      "fonctionnel-recursivite-terminale",
      "fonctionnel-listes",
      "fonctionnel-filtrage-motif",
      "fonctionnel-variants-records",
      "fonctionnel-option-result",
      "fonctionnel-compilation-dune"
     ]
    },
    {
     "code": "intermediate",
     "label": "Intermédiaire",
     "notions": [
      "fonctionnel-ordre-superieur",
      "fonctionnel-polymorphisme",
      "fonctionnel-modules-signatures",
      "fonctionnel-exceptions",
      "fonctionnel-references-mutables",
      "fonctionnel-purete-transparence",
      "fonctionnel-json-parsing",
      "fonctionnel-collections-stdlib",
      "fonctionnel-types-recursifs",
      "fonctionnel-opam-bibliotheques",
      "fonctionnel-sequences-paresse"
     ]
    },
    {
     "code": "advanced",
     "label": "Avancé",
     "notions": [
      "fonctionnel-foncteurs",
      "fonctionnel-concurrence-lwt",
      "fonctionnel-eliom-client-serveur",
      "fonctionnel-js-of-ocaml",
      "fonctionnel-variants-polymorphes",
      "fonctionnel-objets",
      "fonctionnel-monades",
      "fonctionnel-modules-premiere-classe",
      "fonctionnel-continuations",
      "fonctionnel-types-fantomes"
     ]
    },
    {
     "code": "transcended",
     "label": "Transcendée",
     "notions": [
      "fonctionnel-gadt",
      "fonctionnel-hindley-milner",
      "fonctionnel-effets-ocaml5",
      "fonctionnel-representation-gc",
      "fonctionnel-ppx",
      "fonctionnel-lambda-calcul",
      "fonctionnel-optimisation-flambda",
      "fonctionnel-structures-persistantes"
     ]
    }
   ],
   "certifications": [],
   "certificationNote": "aucune certification OCaml reconnue (recherche du 11/11/2026) ; preuve publique : un paquet publié sur opam, `ft_turing` et `h42n42` au Portfolio.",
   "rank": {
    "value": null,
    "status": "observed",
    "reason": "aucune notion de la carte suivie (« déclarée » exclue)"
   },
   "nextRank": {
    "rank": "E",
    "condition": "au moins une notion de la carte suivie (« déclarée » exclue)",
    "progress": {
     "value": 0,
     "status": "observed",
     "reason": null
    },
    "total": null,
    "missing": []
   },
   "trackedCount": 0,
   "offCard": []
  },
  {
   "id": "python",
   "name": "Python",
   "tiers": [
    {
     "code": "beginner",
     "label": "Débutant",
     "notions": [
      "python-types-variables",
      "python-operateurs-entrees-sorties",
      "python-conditions-boucles",
      "python-fonctions",
      "python-listes-tuples",
      "python-dictionnaires-ensembles",
      "python-chaines",
      "python-fichiers-flux",
      "python-modules-paquets",
      "python-exceptions",
      "python-comprehensions",
      "python-environnements-virtuels",
      "python-tests-debogage",
      "python-developpement-collaboratif"
     ]
    },
    {
     "code": "intermediate",
     "label": "Intermédiaire",
     "notions": [
      "python-classes-objets",
      "python-heritage-mro",
      "python-lambda-fermetures",
      "python-methodes-speciales",
      "python-decorateurs",
      "python-methodes-classe",
      "python-gestionnaires-contexte",
      "python-dataclasses-annotations",
      "python-serialisation",
      "python-expressions-regulieres",
      "python-formatage",
      "python-conventions-qualite",
      "python-http-rest",
      "python-sqlite",
      "python-journalisation"
     ]
    },
    {
     "code": "advanced",
     "label": "Avancé",
     "notions": [
      "python-descripteurs",
      "python-abc-metaclasses",
      "python-groupes-exceptions",
      "python-protocoles-variance",
      "python-generateurs-pipelines",
      "python-memoisation",
      "python-packaging",
      "python-profilage",
      "python-slots-modele-donnees",
      "python-architecture-modules",
      "python-threads-processus",
      "python-asyncio",
      "python-securite",
      "python-fastapi-pydantic",
      "python-observabilite"
     ]
    },
    {
     "code": "transcended",
     "label": "Transcendée",
     "notions": [
      "python-cpython-internes",
      "python-sans-gil",
      "python-memoire-gc",
      "python-extensions-c",
      "python-machinerie-import",
      "python-ast-metaprogrammation",
      "python-typage-avance",
      "python-strategies-livraison"
     ]
    }
   ],
   "certifications": [
    {
     "label": "PCEP",
     "detail": "PCEP, Python Institute / OpenEDG, version PCEP-30-03 (35 questions, 50 minutes, seuil 70 %, valable 5 ans ; cinq sections : bases du langage et de Python, contrôle de flux, collections, fonctions et exceptions, fichiers et import de modules) : page et programme détaillé (35 objectifs) relus le 17/11/2026 sur pythoninstitute.org/pcep et pythoninstitute.org/pcep-exam-syllabus ; prix non indiqué sur ces pages (boutique OpenEDG), à relire à l'inscription.",
     "obtained": {
      "value": null,
      "status": "insufficient",
      "reason": "aucun fait « certification » dans /professor"
     }
    },
    {
     "label": "PCAP",
     "detail": "PCAP, Python Institute / OpenEDG, version PCAP-31-04 (42 questions, 65 minutes, seuil 72 %) : programme détaillé (42 objectifs) relu le 17/11/2026 sur pythoninstitute.org/pcap et pythoninstitute.org/pcap-exam-syllabus ; prix non indiqué.",
     "obtained": {
      "value": null,
      "status": "insufficient",
      "reason": "aucun fait « certification » dans /professor"
     }
    },
    {
     "label": "PCPP1",
     "detail": "PCPP1, version PCPP1-32-102 (45 questions, seuil 72 %, durée à confirmer) : page relue le 17/11/2026 sur pythoninstitute.org/pcpp1 ; elle ne détaille que 21 des 33 objectifs annoncés, le programme complet est à lire sur son syllabus avant de proposer la certification.",
     "obtained": {
      "value": null,
      "status": "insufficient",
      "reason": "aucun fait « certification » dans /professor"
     }
    },
    {
     "label": "PCPP2",
     "detail": "PCPP2, version PCPP2-32-202, en essai sur marché restreint, programme formel « à venir », bons d'examen attendus mi-novembre 2026 : périmètre relu le 17/11/2026 sur pythoninstitute.org/pcpp2 (50 questions, 90 minutes, seuil 72 %).",
     "obtained": {
      "value": null,
      "status": "insufficient",
      "reason": "aucun fait « certification » dans /professor"
     }
    }
   ],
   "certificationNote": "couvertes par cette carte et la carte SQL (requêtes de PCPP1)",
   "rank": {
    "value": "E",
    "status": "observed",
    "reason": "17 notions de la carte suivies (« déclarée » exclue)"
   },
   "nextRank": {
    "rank": "D",
    "condition": "notions débutantes au moins « comprise », aucun fait « niveau validé » enregistré dans /professor",
    "progress": {
     "value": 3,
     "status": "estimated",
     "reason": null
    },
    "total": 14,
    "missing": [
     "python-types-variables",
     "python-operateurs-entrees-sorties",
     "python-fonctions",
     "python-listes-tuples",
     "python-chaines",
     "python-fichiers-flux",
     "python-modules-paquets",
     "python-exceptions",
     "python-comprehensions",
     "python-environnements-virtuels",
     "python-tests-debogage"
    ]
   },
   "trackedCount": 17,
   "offCard": []
  },
  {
   "id": "reseau",
   "name": "Réseau",
   "tiers": [
    {
     "code": "beginner",
     "label": "Débutant",
     "notions": [
      "reseau-modele-couches",
      "reseau-adresses-ip",
      "reseau-tcp-udp-ports",
      "reseau-dns-resolution",
      "reseau-configuration-ip",
      "reseau-http-bases",
      "reseau-outils-diagnostic",
      "reseau-client-serveur"
     ]
    },
    {
     "code": "intermediate",
     "label": "Intermédiaire",
     "notions": [
      "linux-ssh-serveur",
      "reseau-pare-feu",
      "reseau-nat-redirection",
      "reseau-routage-statique",
      "reseau-synchronisation-heure",
      "reseau-tls-certificats",
      "reseau-dhcp",
      "reseau-serveur-web",
      "reseau-sockets",
      "reseau-capture-paquets"
     ]
    },
    {
     "code": "advanced",
     "label": "Avancé",
     "notions": [
      "reseau-proxy-inverse",
      "reseau-pont-agregation",
      "reseau-partages-nfs-autofs",
      "reseau-mta-courrier",
      "reseau-vpn-tunnels",
      "reseau-annuaire-ldap",
      "reseau-http-securise",
      "reseau-vlan",
      "reseau-espaces-noms"
     ]
    },
    {
     "code": "transcended",
     "label": "Transcendée",
     "notions": [
      "reseau-congestion-tcp",
      "reseau-ipv6-avance",
      "reseau-routage-dynamique",
      "reseau-performance-pile",
      "reseau-dns-internes",
      "reseau-quic-http3",
      "reseau-ebpf-xdp",
      "reseau-attaques"
     ]
    }
   ],
   "certifications": [],
   "certificationNote": "aucune retenue en propre. CompTIA Network+ et Cisco CCNA visent l'administration d'équipements réseau, hors des objectifs de Louis ; les objectifs réseau de RHCSA, LFCS et LPIC-1 sont couverts ici.",
   "rank": {
    "value": "E",
    "status": "observed",
    "reason": "3 notions de la carte suivies (« déclarée » exclue)"
   },
   "nextRank": {
    "rank": "D",
    "condition": "notions débutantes au moins « comprise », aucun fait « niveau validé » enregistré dans /professor",
    "progress": {
     "value": 0,
     "status": "estimated",
     "reason": null
    },
    "total": 8,
    "missing": [
     "reseau-modele-couches",
     "reseau-adresses-ip",
     "reseau-tcp-udp-ports",
     "reseau-dns-resolution",
     "reseau-configuration-ip",
     "reseau-http-bases",
     "reseau-outils-diagnostic",
     "reseau-client-serveur"
    ]
   },
   "trackedCount": 3,
   "offCard": []
  },
  {
   "id": "securite-binaire",
   "name": "Sécurité binaire",
   "tiers": [
    {
     "code": "beginner",
     "label": "Débutant",
     "notions": [
      "secu-outils-inspection",
      "secu-desassemblage-lecture",
      "secu-debogueur-analyse",
      "secu-pile-appels-exploitation",
      "secu-debordement-pile",
      "secu-memoire-shellcode-bases",
      "secu-escalade-suid",
      "secu-injection-commande",
      "secu-encodages-hachage",
      "secu-conditions-course"
     ]
    },
    {
     "code": "intermediate",
     "label": "Intermédiaire",
     "notions": [
      "secu-controle-flot",
      "secu-shellcode-ecriture",
      "secu-format-string",
      "secu-debordement-entier",
      "secu-off-by-one",
      "secu-ret2libc",
      "secu-rop-chaines",
      "secu-nx-dep",
      "secu-canari",
      "secu-aslr-pie",
      "secu-plt-got",
      "secu-scripts-offensifs",
      "secu-reverse-desassembleur",
      "secu-recherche-bugs"
     ]
    },
    {
     "code": "advanced",
     "label": "Avancé",
     "notions": [
      "secu-fuite-adresse",
      "secu-stack-pivot",
      "secu-tas-agencement",
      "secu-use-after-free",
      "secu-tcache-fastbin",
      "secu-exploitation-distance",
      "secu-ret2dlresolve",
      "secu-one-gadget-relro",
      "secu-windows-execution-memoire",
      "secu-seh",
      "secu-egghunter",
      "secu-windows-dep-aslr",
      "secu-fuzzing",
      "secu-environnements-restreints"
     ]
    },
    {
     "code": "transcended",
     "label": "Transcendée",
     "notions": [
      "secu-house-of",
      "secu-fsop",
      "secu-srop",
      "secu-exploitation-noyau",
      "secu-protections-modernes",
      "secu-execution-symbolique",
      "secu-attaques-crypto",
      "secu-evasion-poste",
      "secu-acces-reseau",
      "secu-allocateurs-durcis"
     ]
    }
   ],
   "certifications": [
    {
     "label": "OSED (OffSec Exploit Developer)",
     "detail": "OSED (OffSec Exploit Developer), cours EXP-301 « Windows User Mode Exploit Development », examen pratique surveillé, sans expiration : programme relu le 11/11/2026 (syllabus de 03/2026 sur manage.offsec.com, lien depuis offsec.com/courses/exp-301).",
     "obtained": {
      "value": null,
      "status": "insufficient",
      "reason": "aucun fait « certification » dans /professor"
     }
    },
    {
     "label": "GXPN (GIAC Exploit Researcher and Advanced Penetration Tester)",
     "detail": "GXPN (GIAC Exploit Researcher and Advanced Penetration Tester), 60 questions en 3 h, 67 % pour réussir : 14 objectifs relus le 11/11/2026 sur giac.org/certifications/exploit-researcher-advanced-penetration-tester-gxpn.",
     "obtained": {
      "value": null,
      "status": "insufficient",
      "reason": "aucun fait « certification » dans /professor"
     }
    }
   ],
   "certificationNote": "couvertes par cette carte, la carte Réseau (interception et manipulation de trafic) et la carte Noyau et assembleur (assembleur, conventions d'appel)",
   "rank": {
    "value": null,
    "status": "observed",
    "reason": "aucune notion de la carte suivie (« déclarée » exclue)"
   },
   "nextRank": {
    "rank": "E",
    "condition": "au moins une notion de la carte suivie (« déclarée » exclue)",
    "progress": {
     "value": 0,
     "status": "observed",
     "reason": null
    },
    "total": null,
    "missing": []
   },
   "trackedCount": 0,
   "offCard": []
  },
  {
   "id": "shell",
   "name": "Shell",
   "tiers": [
    {
     "code": "beginner",
     "label": "Débutant",
     "notions": [
      "shell-commandes-base",
      "shell-commande-options",
      "linux-redirections-shell",
      "shell-tubes-filtres",
      "shell-code-retour",
      "shell-variables-guillemets",
      "shell-jokers",
      "linux-script-shell"
     ]
    },
    {
     "code": "intermediate",
     "label": "Intermédiaire",
     "notions": [
      "linux-shell-test-substitution",
      "linux-shell-case",
      "shell-boucles",
      "shell-fonctions",
      "shell-substitution-commande",
      "linux-shell-set-eu",
      "linux-sed-adresses",
      "shell-expressions-regulieres",
      "shell-find-xargs",
      "shell-awk",
      "shell-controle-taches",
      "shell-environnement-alias"
     ]
    },
    {
     "code": "advanced",
     "label": "Avancé",
     "notions": [
      "shell-expansions-parametres",
      "shell-tableaux-bash",
      "shell-trap",
      "shell-here-doc-sous-shell",
      "shell-getopts",
      "shell-portabilite-posix",
      "shell-sed-avance",
      "shell-decoupage-mots"
     ]
    },
    {
     "code": "transcended",
     "label": "Transcendée",
     "notions": [
      "shell-ordre-expansions",
      "shell-descripteurs-avances",
      "shell-fifo-coproc",
      "shell-cout-processus",
      "shell-debogage",
      "shell-awk-programmes",
      "shell-groupes-sessions",
      "shell-securite-scripts"
     ]
    }
   ],
   "certifications": [],
   "certificationNote": "pas de certification propre au shell ; les objectifs shell de RHCSA, LFCS et LPIC-1 (sources et versions : carte Linux (système)) sont couverts ici.",
   "rank": {
    "value": "E",
    "status": "observed",
    "reason": "6 notions de la carte suivies (« déclarée » exclue)"
   },
   "nextRank": {
    "rank": "D",
    "condition": "notions débutantes au moins « comprise », aucun fait « niveau validé » enregistré dans /professor",
    "progress": {
     "value": 0,
     "status": "estimated",
     "reason": null
    },
    "total": 8,
    "missing": [
     "shell-commandes-base",
     "shell-commande-options",
     "linux-redirections-shell",
     "shell-tubes-filtres",
     "shell-code-retour",
     "shell-variables-guillemets",
     "shell-jokers",
     "linux-script-shell"
    ]
   },
   "trackedCount": 6,
   "offCard": [
    "linux-lien-sh-bash",
    "linux-shell-pushd-popd",
    "linux-fichiers-caches"
   ]
  },
  {
   "id": "sql",
   "name": "SQL",
   "tiers": [
    {
     "code": "beginner",
     "label": "Débutant",
     "notions": [
      "sql-tables-cle-primaire",
      "sql-select-from-where",
      "sql-order-by-top",
      "sql-filtres-courants",
      "sql-valeurs-absentes",
      "sql-types-valeurs",
      "sql-agregation-group-by",
      "sql-insert-update-delete"
     ]
    },
    {
     "code": "intermediate",
     "label": "Intermédiaire",
     "notions": [
      "sql-jointures",
      "sql-having",
      "sql-sous-requetes",
      "sql-contraintes",
      "sql-normalisation",
      "sql-transactions-acid",
      "sql-index",
      "sql-vues",
      "sql-case-fonctions",
      "sql-ensembles",
      "sql-requetes-parametrees",
      "sql-definition-tables",
      "sql-privileges"
     ]
    },
    {
     "code": "advanced",
     "label": "Avancé",
     "notions": [
      "sql-fenetrage",
      "sql-cte-recursives",
      "sql-plans-execution",
      "sql-niveaux-isolation",
      "sql-procedures-declencheurs",
      "sql-modelisation",
      "sql-optimisation-requetes",
      "sql-verrous-interblocages",
      "sql-sequences-synonymes",
      "sql-dictionnaire-donnees",
      "sql-fuseaux-horaires",
      "sql-merge-insertion-multiple",
      "sql-flashback"
     ]
    },
    {
     "code": "transcended",
     "label": "Transcendée",
     "notions": [
      "sql-stockage-interne",
      "sql-optimiseur-statistiques",
      "sql-mvcc",
      "sql-journal-recuperation",
      "sql-partitionnement-replication",
      "sql-algebre-relationnelle",
      "sql-analytique-colonnes",
      "sql-anomalies-concurrence"
     ]
    }
   ],
   "certifications": [
    {
     "label": "Oracle Database SQL Certified Associate",
     "detail": "Oracle Database SQL Certified Associate, examen 1Z0-071, validé de la base 11g R2 à 19c, sans date d'expiration. Page officielle (education.oracle.com, examen 1Z0-071) non lue le 11/11/2026 (délai dépassé, puis accès refusé) : thèmes pris de guides tiers concordants, à relire sur la page officielle à la prochaine vérification.",
     "obtained": {
      "value": null,
      "status": "insufficient",
      "reason": "aucun fait « certification » dans /professor"
     }
    }
   ],
   "certificationNote": "",
   "rank": {
    "value": "E",
    "status": "observed",
    "reason": "5 notions de la carte suivies (« déclarée » exclue)"
   },
   "nextRank": {
    "rank": "D",
    "condition": "notions débutantes au moins « comprise », aucun fait « niveau validé » enregistré dans /professor",
    "progress": {
     "value": 5,
     "status": "estimated",
     "reason": null
    },
    "total": 8,
    "missing": [
     "sql-tables-cle-primaire",
     "sql-filtres-courants",
     "sql-insert-update-delete"
    ]
   },
   "trackedCount": 5,
   "offCard": [
    "sql-variable-de-table"
   ]
  }
 ],
 "notions": {
  "algorithmique-logique-booleenne": {
   "label": "Logique booléenne (et, ou, non, tables de vérité)",
   "card": "algorithmique",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "algorithmique-lois-de-morgan": {
   "label": "Lois de De Morgan",
   "card": "algorithmique",
   "tier": "beginner",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "07/11/2026",
   "section": "Algorithmique"
  },
  "algorithmique-complexite": {
   "label": "Complexité (notation O, meilleur et pire cas)",
   "card": "algorithmique",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "algorithmique-recherches": {
   "label": "Recherche linéaire et dichotomique",
   "card": "algorithmique",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "algorithmique-tris-simples": {
   "label": "Tris simples (sélection, insertion)",
   "card": "algorithmique",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "algorithmique-recursivite": {
   "label": "Récursivité (cas de base, pile d'appels)",
   "card": "algorithmique",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "algorithmique-structures-lineaires": {
   "label": "Tableau, liste chaînée, pile, file",
   "card": "algorithmique",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "algorithmique-invariant-boucle": {
   "label": "Invariant de boucle",
   "card": "algorithmique",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "algorithmique-tris-efficaces": {
   "label": "Tris efficaces (fusion, rapide, par tas)",
   "card": "algorithmique",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "algorithmique-table-hachage": {
   "label": "Table de hachage (collisions, facteur de charge)",
   "card": "algorithmique",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "algorithmique-arbres-binaires": {
   "label": "Arbres binaires et arbres de recherche",
   "card": "algorithmique",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "algorithmique-graphes-parcours": {
   "label": "Graphes et parcours (largeur, profondeur)",
   "card": "algorithmique",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "algorithmique-retour-sur-trace": {
   "label": "Retour sur trace et élagage",
   "card": "algorithmique",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "algorithmique-diviser-regner": {
   "label": "Diviser pour régner",
   "card": "algorithmique",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "algorithmique-glouton": {
   "label": "Algorithmes gloutons",
   "card": "algorithmique",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "algorithmique-file-priorite": {
   "label": "Tas et file de priorité",
   "card": "algorithmique",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "algorithmique-sat-clause-litteral": {
   "label": "Variable, littéral, clause et satisfaction (SAT)",
   "card": "algorithmique",
   "tier": "intermediate",
   "state": "appliquée",
   "objective": "socle",
   "lastPractice": "08/11/2026",
   "section": "Algorithmique"
  },
  "algorithmique-masques-bits": {
   "label": "Masques de bits",
   "card": "algorithmique",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "algorithmique-programmation-dynamique": {
   "label": "Programmation dynamique",
   "card": "algorithmique",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "algorithmique-plus-courts-chemins": {
   "label": "Plus courts chemins (Dijkstra, A*)",
   "card": "algorithmique",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "algorithmique-arbres-equilibres": {
   "label": "Arbres équilibrés",
   "card": "algorithmique",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "algorithmique-contraintes": {
   "label": "Satisfaction de contraintes (propagation, heuristique MRV)",
   "card": "algorithmique",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "algorithmique-automates": {
   "label": "Automates finis et machine de Turing",
   "card": "algorithmique",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "algorithmique-minimax": {
   "label": "Minimax et élagage alpha-bêta",
   "card": "algorithmique",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "algorithmique-union-find": {
   "label": "Union-find et arbre couvrant minimal",
   "card": "algorithmique",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "algorithmique-analyse-amortie": {
   "label": "Analyse amortie",
   "card": "algorithmique",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "algorithmique-reduction-sat": {
   "label": "Réduire un problème à SAT",
   "card": "algorithmique",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "algorithmique-np-completude": {
   "label": "NP-complétude et réductions",
   "card": "algorithmique",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "algorithmique-solveurs-sat": {
   "label": "Solveurs SAT (DPLL, CDCL)",
   "card": "algorithmique",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "algorithmique-flots": {
   "label": "Flots dans un réseau",
   "card": "algorithmique",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "algorithmique-chaines": {
   "label": "Algorithmes de chaînes (KMP, tableaux de suffixes)",
   "card": "algorithmique",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "algorithmique-probabilistes": {
   "label": "Algorithmes probabilistes",
   "card": "algorithmique",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "algorithmique-approximation": {
   "label": "Algorithmes d'approximation",
   "card": "algorithmique",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "algorithmique-structures-cache": {
   "label": "Structures adaptées au cache",
   "card": "algorithmique",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "algorithmique-calculabilite": {
   "label": "Calculabilité et problème de l'arrêt",
   "card": "algorithmique",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-numpy-vectorisation": {
   "label": "Tableaux NumPy et calcul vectorisé",
   "card": "apprentissage-automatique",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-pandas-nettoyage": {
   "label": "Données tabulaires (pandas, nettoyage, valeurs manquantes)",
   "card": "apprentissage-automatique",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-statistiques-descriptives": {
   "label": "Statistiques descriptives (moyenne, écart-type, quartiles)",
   "card": "apprentissage-automatique",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-visualisation": {
   "label": "Visualisation (Matplotlib : histogramme, nuage de points)",
   "card": "apprentissage-automatique",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-probabilites": {
   "label": "Probabilités de base",
   "card": "apprentissage-automatique",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-supervise-principe": {
   "label": "Apprentissage supervisé (caractéristiques, étiquettes, entraînement, prédiction)",
   "card": "apprentissage-automatique",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-regression-lineaire": {
   "label": "Régression linéaire",
   "card": "apprentissage-automatique",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-fonction-cout": {
   "label": "Fonction de coût",
   "card": "apprentissage-automatique",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-descente-gradient": {
   "label": "Descente de gradient",
   "card": "apprentissage-automatique",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-normalisation": {
   "label": "Normalisation et standardisation",
   "card": "apprentissage-automatique",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-entrainement-test": {
   "label": "Jeux d'entraînement, de validation et de test",
   "card": "apprentissage-automatique",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-surapprentissage": {
   "label": "Surapprentissage et sous-apprentissage",
   "card": "apprentissage-automatique",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-regression-logistique": {
   "label": "Régression logistique et classification multiclasse",
   "card": "apprentissage-automatique",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-metriques-classification": {
   "label": "Métriques (précision, rappel, F1, matrice de confusion, ROC ; variance expliquée)",
   "card": "apprentissage-automatique",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-validation-croisee": {
   "label": "Validation croisée et comparaison de modèles",
   "card": "apprentissage-automatique",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-ingenierie-caracteristiques": {
   "label": "Ingénierie des caractéristiques",
   "card": "apprentissage-automatique",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-arbres-forets": {
   "label": "Arbres de décision, forêts et boosting (XGBoost)",
   "card": "apprentissage-automatique",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-clustering": {
   "label": "Partitionnement (k-moyennes)",
   "card": "apprentissage-automatique",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-reduction-dimension": {
   "label": "Réduction de dimension (ACP)",
   "card": "apprentissage-automatique",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-perceptron-multicouche": {
   "label": "Perceptron multicouche (couches, activations)",
   "card": "apprentissage-automatique",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-retropropagation": {
   "label": "Rétropropagation",
   "card": "apprentissage-automatique",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-regularisation": {
   "label": "Régularisation (L1, L2, dropout, arrêt précoce)",
   "card": "apprentissage-automatique",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-optimiseurs": {
   "label": "Optimiseurs (SGD, momentum, Adam)",
   "card": "apprentissage-automatique",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-scikit-learn": {
   "label": "scikit-learn",
   "card": "apprentissage-automatique",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-cnn-images": {
   "label": "Réseaux convolutifs et augmentation d'images",
   "card": "apprentissage-automatique",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-ia-responsable": {
   "label": "IA responsable (biais, équité, confidentialité et consentement)",
   "card": "apprentissage-automatique",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-apprentissage-renforcement": {
   "label": "Apprentissage par renforcement (récompense, exploration, Q-learning)",
   "card": "apprentissage-automatique",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-traitement-signal": {
   "label": "Traitement du signal (filtres, transformée de Fourier, EEG)",
   "card": "apprentissage-automatique",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-reseaux-recurrents": {
   "label": "Réseaux récurrents (RNN, LSTM)",
   "card": "apprentissage-automatique",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-pytorch": {
   "label": "Frameworks d'apprentissage profond (PyTorch)",
   "card": "apprentissage-automatique",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-entrainement-gpu": {
   "label": "Entraînement sur GPU (lots, précision mixte)",
   "card": "apprentissage-automatique",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-hyperparametres": {
   "label": "Recherche d'hyperparamètres",
   "card": "apprentissage-automatique",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-desequilibre-classes": {
   "label": "Classes déséquilibrées",
   "card": "apprentissage-automatique",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-pipelines-mlops": {
   "label": "Pipelines automatisés et entraînement continu (Kubeflow, Vertex AI Pipelines)",
   "card": "apprentissage-automatique",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-service-modeles": {
   "label": "Servir un modèle (en ligne, par lots, mise à l'échelle)",
   "card": "apprentissage-automatique",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-surveillance-derive": {
   "label": "Surveillance en production et dérive des données",
   "card": "apprentissage-automatique",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-suivi-experiences": {
   "label": "Suivi des expériences, registre de modèles, versions des données",
   "card": "apprentissage-automatique",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-feature-store": {
   "label": "Magasin de caractéristiques",
   "card": "apprentissage-automatique",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-solutions-low-code": {
   "label": "Solutions à peu de code sur le cloud (BigQuery ML, AutoML, Vertex AI)",
   "card": "apprentissage-automatique",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-biais-variance": {
   "label": "Compromis biais-variance et théorie de l'apprentissage",
   "card": "apprentissage-automatique",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-optimisation-convexe": {
   "label": "Optimisation convexe",
   "card": "apprentissage-automatique",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-entrainement-distribue": {
   "label": "Entraînement distribué (parallélisme de données et de modèle)",
   "card": "apprentissage-automatique",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-interpretabilite": {
   "label": "Interprétabilité (SHAP, attributions)",
   "card": "apprentissage-automatique",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-modeles-generatifs": {
   "label": "Modèles génératifs (VAE, GAN, diffusion)",
   "card": "apprentissage-automatique",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-inference-bayesienne": {
   "label": "Inférence bayésienne",
   "card": "apprentissage-automatique",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-auto-supervise": {
   "label": "Apprentissage auto-supervisé",
   "card": "apprentissage-automatique",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ml-robustesse-adversariale": {
   "label": "Robustesse face aux exemples adverses",
   "card": "apprentissage-automatique",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "c-lexique-identifiants": {
   "label": "Lexique (jetons et séparateurs, identifiants et règles de nommage, mots-clés, constantes)",
   "card": "c",
   "tier": "beginner",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "19/11/2026",
   "section": "C"
  },
  "c-types-variables": {
   "label": "Types de base, déclaration et définition, conversions implicites",
   "card": "c",
   "tier": "beginner",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "14/11/2026",
   "section": "C"
  },
  "c-operateurs-expressions": {
   "label": "Opérateurs, priorité et associativité",
   "card": "c",
   "tier": "beginner",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "19/11/2026",
   "section": "C"
  },
  "c-conditions-boucles": {
   "label": "Conditions et boucles (`if`, `switch`, `while`, `do`, `for`, `break`, `continue`, `goto`)",
   "card": "c",
   "tier": "beginner",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "19/11/2026",
   "section": "C"
  },
  "c-fonctions-prototypes": {
   "label": "Fonctions et prototypes (passage par valeur, par adresse ; `main`, `argc`/`argv`, code de retour)",
   "card": "c",
   "tier": "beginner",
   "state": "comprise",
   "objective": "socle",
   "lastPractice": "19/11/2026",
   "section": "C"
  },
  "c-tableaux-chaines": {
   "label": "Tableaux et chaînes terminées par `'\\0'`",
   "card": "c",
   "tier": "beginner",
   "state": "comprise",
   "objective": "socle",
   "lastPractice": "19/11/2026",
   "section": "C"
  },
  "c-pointeurs": {
   "label": "Pointeurs (adresse, déréférencement)",
   "card": "c",
   "tier": "beginner",
   "state": "comprise",
   "objective": "socle",
   "lastPractice": "19/11/2026",
   "section": "C"
  },
  "c-preprocesseur-entetes": {
   "label": "Préprocesseur et en-têtes (`#include`, `#define`, `#ifdef`, gardes)",
   "card": "c",
   "tier": "beginner",
   "state": "comprise",
   "objective": "socle",
   "lastPractice": "19/11/2026",
   "section": "C"
  },
  "cpp-compilation-edition-liens": {
   "label": "Compilation et édition de liens (source, objet, exécutable)",
   "card": "c",
   "tier": "beginner",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "10/11/2026",
   "section": "C"
  },
  "c-allocation-dynamique": {
   "label": "Allocation dynamique (`malloc`, `calloc`, `realloc`, `free`, fuite)",
   "card": "c",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "c-gestion-memoire-echec": {
   "label": "Libération sur chaque chemin d'échec",
   "card": "c",
   "tier": "intermediate",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "18/11/2026",
   "section": "C"
  },
  "c-structures-unions-enum": {
   "label": "Structures, unions et énumérations (initialisation)",
   "card": "c",
   "tier": "intermediate",
   "state": "comprise",
   "objective": "socle",
   "lastPractice": "19/11/2026",
   "section": "C"
  },
  "c-pointeurs-fonction": {
   "label": "Pointeurs de fonction",
   "card": "c",
   "tier": "intermediate",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "21/11/2026",
   "section": "C"
  },
  "c-arithmetique-pointeurs": {
   "label": "Arithmétique des pointeurs, tableau contre pointeur, tableaux 2D",
   "card": "c",
   "tier": "intermediate",
   "state": "comprise",
   "objective": "socle",
   "lastPractice": "19/11/2026",
   "section": "C"
  },
  "c-entrees-sorties": {
   "label": "Entrées-sorties (`stdio` : `printf` et ses formats, `fopen`, `fprintf`, `fscanf` ; appels `open`, `read`, `write` ; interfaces POSIX, API, ABI et WINAPI)",
   "card": "c",
   "tier": "intermediate",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "19/11/2026",
   "section": "C"
  },
  "c-parseur-fichiers": {
   "label": "Parseur de fichiers et rejet des entrées mal formées",
   "card": "c",
   "tier": "intermediate",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "19/11/2026",
   "section": "C"
  },
  "c-classes-stockage": {
   "label": "Classes de stockage, portée, liaison et durée de vie",
   "card": "c",
   "tier": "intermediate",
   "state": "comprise",
   "objective": "socle",
   "lastPractice": "19/11/2026",
   "section": "C"
  },
  "c-makefile": {
   "label": "Makefile (règles, dépendances, variables, éviter de relier pour rien)",
   "card": "c",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "c-makefile-cibles-factices": {
   "label": "Cibles factices (`.PHONY`)",
   "card": "c",
   "tier": "intermediate",
   "state": "appliquée",
   "objective": "socle",
   "lastPractice": "20/11/2026",
   "section": "C"
  },
  "c-debogage-outils": {
   "label": "Outils de débogage (`gdb`, Valgrind, sanitizers)",
   "card": "c",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-bibliotheque-partagee": {
   "label": "Bibliothèque partagée contre statique",
   "card": "c",
   "tier": "intermediate",
   "state": "découverte",
   "objective": "socle",
   "lastPractice": "19/11/2026",
   "section": "C"
  },
  "c-debordements-tampon": {
   "label": "Débordements de tampon et fonctions bornées",
   "card": "c",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "c-tri-recherche-stdlib": {
   "label": "Fonctions de chaînes et de mémoire, `qsort` et `bsearch`",
   "card": "c",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "c-versions-norme": {
   "label": "Versions de la norme (C89 à C23, constructions obsolètes, trigraphes, mots-clés de C11)",
   "card": "c",
   "tier": "intermediate",
   "state": "découverte",
   "objective": "socle",
   "lastPractice": "12/11/2026",
   "section": "C"
  },
  "c-comportement-indefini": {
   "label": "Comportement indéfini, non spécifié, défini par l'implémentation",
   "card": "c",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "c-alignement-remplissage": {
   "label": "Alignement et remplissage des structures (`sizeof`)",
   "card": "c",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "c-qualificateurs": {
   "label": "Qualificateurs `const`, `volatile`, `restrict`",
   "card": "c",
   "tier": "advanced",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "21/11/2026",
   "section": "C"
  },
  "c-operations-bits": {
   "label": "Opérations bit à bit et masques",
   "card": "c",
   "tier": "advanced",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "19/11/2026",
   "section": "C"
  },
  "c-macros-avancees": {
   "label": "Macros avancées (`#`, `##`, variadiques, double évaluation)",
   "card": "c",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "c-fonctions-variadiques": {
   "label": "Fonctions variadiques (`stdarg.h`, famille `vprintf`)",
   "card": "c",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-chargeur-dynamique": {
   "label": "Chargeur dynamique (`ld.so`, résolution au lancement)",
   "card": "c",
   "tier": "advanced",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "19/11/2026",
   "section": "C"
  },
  "c-symboles-sections": {
   "label": "Symboles, visibilité et sections (`.text`, `.data`, `.bss`)",
   "card": "c",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "c-memoire-processus": {
   "label": "Organisation mémoire d'un processus (pile, tas, segments)",
   "card": "c",
   "tier": "advanced",
   "state": "comprise",
   "objective": "socle",
   "lastPractice": "19/11/2026",
   "section": "C"
  },
  "c-controle-descripteurs": {
   "label": "Contrôle des descripteurs (`fcntl`, `dup`, modes non bloquants)",
   "card": "c",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "c-caracteres-larges": {
   "label": "Caractères larges et Unicode (`wchar_t`, UTF-8)",
   "card": "c",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "c-processus-threads": {
   "label": "Processus et threads (modèles Unix et Windows, `threads.h` de C11, sûreté des fonctions)",
   "card": "c",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "c-flottants-ieee754": {
   "label": "Nombres flottants IEEE 754 (représentation, précision, comparaisons)",
   "card": "c",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "c-sauts-non-locaux": {
   "label": "Sauts non locaux (`setjmp`, `longjmp`)",
   "card": "c",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "c-declarations-complexes": {
   "label": "Déclarations complexes (pointeur de fonction qui renvoie un tableau...)",
   "card": "c",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "c-aliasing-strict": {
   "label": "Règle d'aliasing strict",
   "card": "c",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "c-atomiques-modele-memoire": {
   "label": "Atomiques et modèle mémoire de C11",
   "card": "c",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "c-promotions-entieres": {
   "label": "Promotions entières, conversions arithmétiques, dépassement signé",
   "card": "c",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "c-points-sequence": {
   "label": "Points de séquence et ordre d'évaluation",
   "card": "c",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "c-optimiseur": {
   "label": "Ce que l'optimiseur suppose (comportement indéfini exploité, inlining, LTO)",
   "card": "c",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "c-allocateur-maison": {
   "label": "Écrire un allocateur (listes libres, fragmentation)",
   "card": "c",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "c-performance-cache": {
   "label": "Performance et cache (localité, mesure)",
   "card": "c",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "c-durcissement": {
   "label": "Durcissement (`_FORTIFY_SOURCE`, canaris, PIE, RELRO)",
   "card": "c",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "c-assembleur-en-ligne": {
   "label": "Assembleur en ligne (contraintes, registres modifiés)",
   "card": "c",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "c-precision-arbitraire": {
   "label": "Arithmétique en précision arbitraire",
   "card": "c",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "cpp-types-litteraux": {
   "label": "Types prédéfinis, plages, littéraux (décimal, octal, hexadécimal, binaire, `char`, `bool`) et `sizeof`",
   "card": "cpp",
   "tier": "beginner",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "21/11/2026",
   "section": "C++"
  },
  "cpp-classes-objets": {
   "label": "Classes et objets (membres, `public`, `private`)",
   "card": "cpp",
   "tier": "beginner",
   "state": "comprise",
   "objective": "socle",
   "lastPractice": "21/11/2026",
   "section": "C++"
  },
  "cpp-constructeurs-destructeur": {
   "label": "Constructeurs, liste d'initialisation, destructeur",
   "card": "cpp",
   "tier": "beginner",
   "state": "comprise",
   "objective": "socle",
   "lastPractice": "21/11/2026",
   "section": "C++"
  },
  "cpp-references": {
   "label": "Références contre pointeurs",
   "card": "cpp",
   "tier": "beginner",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "21/11/2026",
   "section": "C++"
  },
  "cpp-surcharge": {
   "label": "Surcharge de fonctions et d'opérateurs, arguments par défaut",
   "card": "cpp",
   "tier": "beginner",
   "state": "comprise",
   "objective": "socle",
   "lastPractice": "21/11/2026",
   "section": "C++"
  },
  "cpp-flux-iostream": {
   "label": "Flux (`std::cout`, `std::cin`, `std::fstream`)",
   "card": "cpp",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "cpp-constexpr-portee": {
   "label": "`constexpr`, portée, espaces de noms et `::`",
   "card": "cpp",
   "tier": "beginner",
   "state": "transférée",
   "objective": "socle",
   "lastPractice": "10/11/2026",
   "section": "C++"
  },
  "cpp-new-delete": {
   "label": "`new` et `delete` (tableaux compris)",
   "card": "cpp",
   "tier": "beginner",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "21/11/2026",
   "section": "C++"
  },
  "cpp-string": {
   "label": "`std::string`",
   "card": "cpp",
   "tier": "beginner",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "21/11/2026",
   "section": "C++"
  },
  "cpp-membres-const-amis": {
   "label": "Membres `const` et `static`, fonctions et classes amies",
   "card": "cpp",
   "tier": "beginner",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "21/11/2026",
   "section": "C++"
  },
  "cpp-forme-canonique": {
   "label": "Forme canonique (copie, affectation, règle de trois et de cinq)",
   "card": "cpp",
   "tier": "intermediate",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "21/11/2026",
   "section": "C++"
  },
  "cpp-heritage-polymorphisme": {
   "label": "Héritage et polymorphisme (`virtual`, liaison dynamique)",
   "card": "cpp",
   "tier": "intermediate",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "21/11/2026",
   "section": "C++"
  },
  "cpp-classes-abstraites": {
   "label": "Classes abstraites et interfaces",
   "card": "cpp",
   "tier": "intermediate",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "21/11/2026",
   "section": "C++"
  },
  "cpp-heritage-multiple": {
   "label": "Héritage multiple et virtuel (diamant)",
   "card": "cpp",
   "tier": "intermediate",
   "state": "découverte",
   "objective": "socle",
   "lastPractice": "21/11/2026",
   "section": "C++"
  },
  "cpp-exceptions-try-catch": {
   "label": "Exceptions (`throw`, `catch` ordonnés par type)",
   "card": "cpp",
   "tier": "intermediate",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "10/11/2026",
   "section": "C++"
  },
  "cpp-conversion-stricte-stoi": {
   "label": "Conversion stricte d'un texte en nombre",
   "card": "cpp",
   "tier": "intermediate",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "11/11/2026",
   "section": "C++"
  },
  "cpp-templates": {
   "label": "Templates de fonctions et de classes, templates imbriqués",
   "card": "cpp",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "cpp-casts": {
   "label": "Conversions nommées (`static_cast`, `dynamic_cast`, `reinterpret_cast`, `const_cast`)",
   "card": "cpp",
   "tier": "intermediate",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "21/11/2026",
   "section": "C++"
  },
  "cpp-raii": {
   "label": "RAII (ressource liée à la durée de vie d'un objet)",
   "card": "cpp",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "cpp-conteneurs-sequence": {
   "label": "Conteneurs séquentiels (`vector`, `deque`, `list`) et adaptateurs (`stack`, `queue`, `priority_queue`)",
   "card": "cpp",
   "tier": "intermediate",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "21/11/2026",
   "section": "C++"
  },
  "cpp-conteneurs-associatifs": {
   "label": "Conteneurs associatifs (`set`, `multiset`, `map`, `multimap`)",
   "card": "cpp",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "cpp-iterateurs": {
   "label": "Itérateurs (catégories, intervalles)",
   "card": "cpp",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "cpp-algorithmes-non-modifiants": {
   "label": "Algorithmes sans modification (parcourir, chercher, compter, comparer)",
   "card": "cpp",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "cpp-algorithmes-modifiants": {
   "label": "Algorithmes de modification (copier, transformer, remplacer, supprimer, réordonner)",
   "card": "cpp",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "cpp-algorithmes-tri-recherche": {
   "label": "Tri et recherche dichotomique de la STL",
   "card": "cpp",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "cpp-algorithmes-fusion-tas": {
   "label": "Fusion, opérations d'ensemble, tas, minimum et maximum de la STL",
   "card": "cpp",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "cpp-foncteurs-adaptateurs": {
   "label": "Objets fonctions et adaptateurs de fonctions",
   "card": "cpp",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "cpp-flux-formatage": {
   "label": "Flux avancés (drapeaux de format, manipulateurs)",
   "card": "cpp",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "cpp-pointeurs-intelligents": {
   "label": "Pointeurs intelligents (`unique_ptr`, `shared_ptr`, `weak_ptr`)",
   "card": "cpp",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "cpp-semantique-deplacement": {
   "label": "Sémantique de déplacement",
   "card": "cpp",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "cpp-lambdas": {
   "label": "Lambdas et captures",
   "card": "cpp",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "cpp-auto-inference": {
   "label": "`auto` et inférence de type",
   "card": "cpp",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "cpp-specialisation-templates": {
   "label": "Spécialisation de templates",
   "card": "cpp",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "cpp-garanties-exceptions": {
   "label": "Garanties d'exception et `noexcept`",
   "card": "cpp",
   "tier": "advanced",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "21/11/2026",
   "section": "C++"
  },
  "cpp-complexite-invalidation": {
   "label": "Complexité des conteneurs et invalidation des itérateurs",
   "card": "cpp",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "cpp-threads": {
   "label": "Concurrence standard (`std::thread`, `std::mutex`)",
   "card": "cpp",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "cpp-calcul-compilation": {
   "label": "Calcul à la compilation (`constexpr`, `consteval`)",
   "card": "cpp",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "cpp-sfinae-concepts": {
   "label": "SFINAE et concepts",
   "card": "cpp",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "cpp-templates-variadiques": {
   "label": "Templates variadiques et métaprogrammation",
   "card": "cpp",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "cpp-categories-valeurs": {
   "label": "Catégories de valeurs et transfert parfait",
   "card": "cpp",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "cpp-modele-objet": {
   "label": "Modèle objet (vtable, disposition mémoire, coût du virtuel)",
   "card": "cpp",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "cpp-atomiques": {
   "label": "Atomiques et modèle mémoire",
   "card": "cpp",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "cpp-allocateurs": {
   "label": "Allocateurs",
   "card": "cpp",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "cpp-odr-liaison": {
   "label": "Règle de définition unique et liaison des templates",
   "card": "cpp",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "cpp-ranges-coroutines": {
   "label": "Ranges et coroutines (C++20)",
   "card": "cpp",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-client-serveur": {
   "label": "Application web : cycle requête, traitement, réponse côté serveur",
   "card": "developpement-web",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-routage": {
   "label": "Routage (adresse vers contrôleur, paramètres de route)",
   "card": "developpement-web",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-mvc": {
   "label": "Modèle, vue, contrôleur",
   "card": "developpement-web",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-structure-framework": {
   "label": "Anatomie d'un projet de framework (Django, Rails, Symfony)",
   "card": "developpement-web",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-gabarits": {
   "label": "Gabarits et échappement automatique",
   "card": "developpement-web",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-formulaires-validation": {
   "label": "Formulaires et validation côté serveur",
   "card": "developpement-web",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-configuration": {
   "label": "Configuration et environnements (variables d'environnement, développement contre production)",
   "card": "developpement-web",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-json-api": {
   "label": "Réponses JSON et premières API",
   "card": "developpement-web",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-gestion-erreurs": {
   "label": "Gestion des erreurs et pages d'erreur de l'application",
   "card": "developpement-web",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-fichiers-statiques": {
   "label": "Fichiers statiques et ressources",
   "card": "developpement-web",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-orm": {
   "label": "ORM (modèles, relations, requêtes, problème N+1)",
   "card": "developpement-web",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-migrations": {
   "label": "Migrations de schéma",
   "card": "developpement-web",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-sessions-authentification": {
   "label": "Authentification par session ou par jeton",
   "card": "developpement-web",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-mots-de-passe": {
   "label": "Stockage des mots de passe (hachage lent, sel)",
   "card": "developpement-web",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-autorisation": {
   "label": "Autorisation (rôles, permissions, contrôle d'accès)",
   "card": "developpement-web",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-api-rest": {
   "label": "Conception d'API REST (ressources, verbes, codes, pagination, versions)",
   "card": "developpement-web",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-intergiciels": {
   "label": "Intergiciels et cycle de traitement d'une requête",
   "card": "developpement-web",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-securite-owasp": {
   "label": "Sécurité applicative (injection, XSS, CSRF : le top 10 d'OWASP)",
   "card": "developpement-web",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-cors": {
   "label": "Partage entre origines (CORS)",
   "card": "developpement-web",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-televersement": {
   "label": "Téléversement et stockage de fichiers",
   "card": "developpement-web",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-courriels": {
   "label": "Envoi de courriels et vérification d'adresse",
   "card": "developpement-web",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-tests-integration": {
   "label": "Tests fonctionnels et d'intégration",
   "card": "developpement-web",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-commandes-console": {
   "label": "Commandes en console du framework",
   "card": "developpement-web",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-oauth-oidc": {
   "label": "Connexion par un fournisseur tiers (OAuth 2.0, OpenID Connect)",
   "card": "developpement-web",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-jwt": {
   "label": "Jetons JWT (signature, expiration, révocation)",
   "card": "developpement-web",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-temps-reel": {
   "label": "Temps réel (WebSockets, événements envoyés par le serveur)",
   "card": "developpement-web",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-taches-fond": {
   "label": "Tâches de fond et files de messages",
   "card": "developpement-web",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-cache": {
   "label": "Cache (HTTP, application, Redis)",
   "card": "developpement-web",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-streaming-media": {
   "label": "Diffusion de médias (requêtes par plages, flux vidéo)",
   "card": "developpement-web",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-limitation-debit": {
   "label": "Limitation de débit et protection contre les abus",
   "card": "developpement-web",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-graphql": {
   "label": "GraphQL",
   "card": "developpement-web",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-rendu-serveur-spa": {
   "label": "Rendu serveur contre application monopage",
   "card": "developpement-web",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-deploiement": {
   "label": "Déploiement (application à douze facteurs, proxy inverse, conteneurs)",
   "card": "developpement-web",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-observabilite": {
   "label": "Journaux et métriques de l'application",
   "card": "developpement-web",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-tests-bout-en-bout": {
   "label": "Tests de bout en bout",
   "card": "developpement-web",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-architecture-distribuee": {
   "label": "Architecture distribuée (services, files de messages)",
   "card": "developpement-web",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-idempotence-sagas": {
   "label": "Idempotence et transactions distribuées (sagas)",
   "card": "developpement-web",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-montee-charge": {
   "label": "Montée en charge horizontale (sessions partagées, répartition de charge)",
   "card": "developpement-web",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-securite-avancee": {
   "label": "Sécurité avancée (SSRF, désérialisation, chaîne d'approvisionnement)",
   "card": "developpement-web",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-performance-serveur": {
   "label": "Performance du serveur (profilage, réservoirs de connexions)",
   "card": "developpement-web",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-cqrs-evenements": {
   "label": "CQRS et sourçage d'événements",
   "card": "developpement-web",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-pubsub-distribue": {
   "label": "Publication et abonnement distribués pour le temps réel",
   "card": "developpement-web",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "web-evolution-api": {
   "label": "Évolution d'une API (compatibilité, dépréciation)",
   "card": "developpement-web",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "docker-image-conteneur": {
   "label": "Image et conteneur",
   "card": "docker",
   "tier": "beginner",
   "state": "appliquée",
   "objective": "socle",
   "lastPractice": "17/11/2026",
   "section": "Docker"
  },
  "docker-conteneur-processus-isole": {
   "label": "Conteneur = processus isolé sur le noyau de l'hôte",
   "card": "docker",
   "tier": "beginner",
   "state": "transférée",
   "objective": "socle",
   "lastPractice": "19/11/2026",
   "section": "Docker"
  },
  "docker-dockerfile": {
   "label": "Dockerfile (`FROM`, `RUN`, `COPY`, `CMD`, `ENTRYPOINT`)",
   "card": "docker",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "docker-cycle-vie": {
   "label": "Cycle de vie d'un conteneur (`run`, `ps`, `stop`, `rm`, `logs`, `exec`)",
   "card": "docker",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "docker-publication-ports": {
   "label": "Publication de ports",
   "card": "docker",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "docker-bind-mount": {
   "label": "Bind mount",
   "card": "docker",
   "tier": "beginner",
   "state": "comprise",
   "objective": "socle",
   "lastPractice": "16/11/2026",
   "section": "Docker"
  },
  "docker-volume-nomme-vs-bind": {
   "label": "Volume nommé et bind mount",
   "card": "docker",
   "tier": "beginner",
   "state": "transférée",
   "objective": "socle",
   "lastPractice": "16/11/2026",
   "section": "Docker"
  },
  "docker-variables-environnement": {
   "label": "Variables d'environnement (`ENV`, `.env`)",
   "card": "docker",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "docker-reseau-isole": {
   "label": "Réseau Docker (annuaire par nom, réseaux isolés)",
   "card": "docker",
   "tier": "intermediate",
   "state": "transférée",
   "objective": "socle",
   "lastPractice": "16/11/2026",
   "section": "Docker"
  },
  "docker-service-reseau-volume": {
   "label": "Ajouter un service au compose",
   "card": "docker",
   "tier": "intermediate",
   "state": "transférée",
   "objective": "socle",
   "lastPractice": "19/11/2026",
   "section": "Docker"
  },
  "docker-compose-dependances": {
   "label": "Dépendances et redémarrage dans le compose (`depends_on`, `restart`)",
   "card": "docker",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "docker-pid1-init": {
   "label": "PID 1 et signaux d'arrêt",
   "card": "docker",
   "tier": "intermediate",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "04/11/2026",
   "section": "Docker"
  },
  "docker-idempotence-demarrage": {
   "label": "Script de démarrage relançable",
   "card": "docker",
   "tier": "intermediate",
   "state": "découverte",
   "objective": "socle",
   "lastPractice": "02/11/2026",
   "section": "Docker"
  },
  "docker-couches-cache": {
   "label": "Couches d'image et cache de construction",
   "card": "docker",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "docker-conteneur-root-defaut": {
   "label": "Conteneur lancé en root par défaut",
   "card": "docker",
   "tier": "intermediate",
   "state": "découverte",
   "objective": "socle",
   "lastPractice": "02/11/2026",
   "section": "Docker"
  },
  "docker-secrets": {
   "label": "Secrets (jamais dans l'image)",
   "card": "docker",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "docker-healthcheck": {
   "label": "Vérification de santé (`HEALTHCHECK`)",
   "card": "docker",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "docker-registre-etiquettes": {
   "label": "Registre et étiquettes (`login`, `push`, `pull`, `tag`, suppression)",
   "card": "docker",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "docker-installation-demon": {
   "label": "Installer et configurer le moteur (`daemon.json`, pilotes de journalisation, sauvegarde)",
   "card": "docker",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "docker-multi-etapes": {
   "label": "Construction en plusieurs étapes",
   "card": "docker",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "docker-image-minimale": {
   "label": "Image minimale (Alpine, distroless, surface d'attaque)",
   "card": "docker",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "docker-pilotes-reseau": {
   "label": "Pilotes réseau (bridge, host, overlay, répartition d'entrée)",
   "card": "docker",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "docker-pilotes-stockage": {
   "label": "Pilotes de stockage (overlayfs, couche d'écriture)",
   "card": "docker",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "docker-limites-ressources": {
   "label": "Limites de ressources (processeur, mémoire)",
   "card": "docker",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "docker-rootless-capacites": {
   "label": "Mode rootless, capacités et espaces de noms utilisateur",
   "card": "docker",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "docker-journalisation": {
   "label": "Journalisation et supervision",
   "card": "docker",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "docker-construction-reproductible": {
   "label": "Construction reproductible (versions épinglées, BuildKit)",
   "card": "docker",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "docker-swarm": {
   "label": "Swarm (services, piles, nœuds, mise à l'échelle)",
   "card": "docker",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "docker-kubernetes-bases": {
   "label": "Bases de Kubernetes (pods, déploiements, services, volumes persistants, ConfigMap)",
   "card": "docker",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "docker-oci-runtime": {
   "label": "Norme OCI et environnement d'exécution (runc, containerd)",
   "card": "docker",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "docker-plateforme-entreprise": {
   "label": "Plateforme d'entreprise (MKE, MSR, contrôle d'accès par rôles, TLS mutuel)",
   "card": "docker",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "docker-seccomp-apparmor": {
   "label": "Profils seccomp et AppArmor",
   "card": "docker",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "docker-chaine-approvisionnement": {
   "label": "Chaîne d'approvisionnement (signature et Content Trust, SBOM, analyse)",
   "card": "docker",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "docker-reseau-internes": {
   "label": "Réseau interne de Docker (NAT, iptables, DNS embarqué)",
   "card": "docker",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "docker-demon-socket": {
   "label": "API du démon et risques de `docker.sock`",
   "card": "docker",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "docker-multi-architecture": {
   "label": "Images multi-architectures",
   "card": "docker",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "docker-debogage": {
   "label": "Débogage de conteneurs (`nsenter`, images sans shell)",
   "card": "docker",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "infographie-pixels-couleurs": {
   "label": "Pixel, image, couleur RGBA et tampon d'image",
   "card": "infographie-3d",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "infographie-vecteurs": {
   "label": "Vecteurs (somme, produit scalaire, norme)",
   "card": "infographie-3d",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "infographie-reperes": {
   "label": "Repères et coordonnées 2D et 3D",
   "card": "infographie-3d",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "infographie-maillage": {
   "label": "Maillage (sommets, faces, triangles)",
   "card": "infographie-3d",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "cpp-boucle-de-jeu": {
   "label": "Boucle de jeu (événements, mise à jour, dessin)",
   "card": "infographie-3d",
   "tier": "beginner",
   "state": "comprise",
   "objective": "socle",
   "lastPractice": "10/11/2026",
   "section": "Infographie 3D"
  },
  "cpp-double-tampon": {
   "label": "Double tampon",
   "card": "infographie-3d",
   "tier": "beginner",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "09/11/2026",
   "section": "Infographie 3D"
  },
  "cpp-vitesse-deltatime-diagonale": {
   "label": "Vitesse indépendante de la fréquence d'images et normalisation",
   "card": "infographie-3d",
   "tier": "beginner",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "09/11/2026",
   "section": "Infographie 3D"
  },
  "c-entrees-clavier-souris": {
   "label": "Entrées clavier et souris",
   "card": "infographie-3d",
   "tier": "beginner",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "19/11/2026",
   "section": "Infographie 3D"
  },
  "c-matrices-transformation": {
   "label": "Matrices de transformation (translation, rotation, échelle, caméra, perspective)",
   "card": "infographie-3d",
   "tier": "intermediate",
   "state": "en cours",
   "objective": "déclarée",
   "lastPractice": "21/11/2026",
   "section": "Infographie 3D"
  },
  "c-pipeline-opengl": {
   "label": "Pipeline OpenGL (shaders, VBO, EBO, VAO, boucle de rendu)",
   "card": "infographie-3d",
   "tier": "intermediate",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "19/11/2026",
   "section": "Infographie 3D"
  },
  "infographie-glsl": {
   "label": "GLSL (shaders de sommets et de fragments, uniformes, attributs)",
   "card": "infographie-3d",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "c-eclairage-textures": {
   "label": "Éclairage par face et textures (coordonnées UV)",
   "card": "infographie-3d",
   "tier": "intermediate",
   "state": "déclarée",
   "objective": "déclarée",
   "lastPractice": "30/09/2026",
   "section": "Infographie 3D"
  },
  "infographie-tampon-profondeur": {
   "label": "Tampon de profondeur et élimination des faces arrière",
   "card": "infographie-3d",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "c-triangulation-ear-clipping": {
   "label": "Triangulation par ear clipping",
   "card": "infographie-3d",
   "tier": "intermediate",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "18/11/2026",
   "section": "Infographie 3D"
  },
  "infographie-modele-hierarchique": {
   "label": "Modèle hiérarchique (pile de matrices)",
   "card": "infographie-3d",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "infographie-images-cles": {
   "label": "Animation par images clés et interpolation",
   "card": "infographie-3d",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "infographie-collisions": {
   "label": "Collisions (boîtes alignées, réponse)",
   "card": "infographie-3d",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "infographie-quaternions": {
   "label": "Quaternions",
   "card": "infographie-3d",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "infographie-phong": {
   "label": "Éclairage de Phong et Blinn (ambiant, diffus, spéculaire)",
   "card": "infographie-3d",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "infographie-matrice-normales": {
   "label": "Matrice des normales",
   "card": "infographie-3d",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "infographie-filtrage-textures": {
   "label": "Filtrage des textures et mipmaps",
   "card": "infographie-3d",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "infographie-graphe-scene": {
   "label": "Graphe de scène et entités-composants",
   "card": "infographie-3d",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "infographie-squelette": {
   "label": "Animation squelettale",
   "card": "infographie-3d",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "infographie-instanciation": {
   "label": "Instanciation et réduction des appels de dessin",
   "card": "infographie-3d",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "infographie-transparence": {
   "label": "Transparence et mélange",
   "card": "infographie-3d",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "infographie-ombres": {
   "label": "Ombres par carte de profondeur",
   "card": "infographie-3d",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "infographie-pbr": {
   "label": "Rendu physiquement réaliste (PBR)",
   "card": "infographie-3d",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "infographie-rendu-differe": {
   "label": "Rendu différé",
   "card": "infographie-3d",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "infographie-gpu-internes": {
   "label": "Fonctionnement du GPU et synchronisation CPU-GPU",
   "card": "infographie-3d",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "infographie-precision-profondeur": {
   "label": "Précision flottante (z-fighting, profondeur inversée)",
   "card": "infographie-3d",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "infographie-gamma": {
   "label": "Espaces de couleur et correction gamma",
   "card": "infographie-3d",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "infographie-elimination-lod": {
   "label": "Élimination hors champ et niveaux de détail",
   "card": "infographie-3d",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "infographie-api-bas-niveau": {
   "label": "API bas niveau (Vulkan : commandes, synchronisation explicite)",
   "card": "infographie-3d",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "infographie-pas-fixe": {
   "label": "Pas de simulation fixe et interpolation du rendu",
   "card": "infographie-3d",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-types-valeurs": {
   "label": "Types primitifs, objets et valeurs (`typeof`, `null`, `undefined`)",
   "card": "javascript",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-portee-declarations": {
   "label": "`let`, `const`, `var`, portée de bloc et remontée",
   "card": "javascript",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-coercition-egalite": {
   "label": "Conversions implicites et égalités `==` contre `===`",
   "card": "javascript",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-operateurs-interaction": {
   "label": "Opérateurs et interaction avec l'utilisateur (`console`, `prompt`, `alert`)",
   "card": "javascript",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-conditions-boucles": {
   "label": "Conditions et boucles (`for…of`, `for…in`, `switch`)",
   "card": "javascript",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-fonctions": {
   "label": "Fonctions (déclaration, expression, fléchée, paramètres par défaut et reste)",
   "card": "javascript",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-tableaux": {
   "label": "Tableaux et leurs méthodes (`map`, `filter`, `reduce`, `sort`)",
   "card": "javascript",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-objets-litteraux": {
   "label": "Objets littéraux (propriétés, méthodes, parcours)",
   "card": "javascript",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-chaines-gabarits": {
   "label": "Chaînes et gabarits de chaînes",
   "card": "javascript",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-exceptions-debogage": {
   "label": "Exceptions (`try`, `catch`, `finally`, `throw`) et débogage",
   "card": "javascript",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-dom-evenements": {
   "label": "DOM et événements du navigateur",
   "card": "javascript",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-modules-es": {
   "label": "Modules ES (`import`, `export`)",
   "card": "javascript",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-fermetures": {
   "label": "Fermetures et fabriques de fonctions",
   "card": "javascript",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-this-liaison": {
   "label": "`this` et sa liaison (`call`, `apply`, `bind`, fonctions fléchées)",
   "card": "javascript",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-prototypes": {
   "label": "Prototypes, chaîne de prototypes et `Object.create`",
   "card": "javascript",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-classes": {
   "label": "Classes (constructeur, héritage, accesseurs, champs privés, membres statiques)",
   "card": "javascript",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-destructuration": {
   "label": "Déstructuration, décomposition et propriétés calculées",
   "card": "javascript",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-objets-natifs": {
   "label": "Objets natifs (`Date`, `Math`, `Map`, `Set`, `RegExp`, `JSON`)",
   "card": "javascript",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-iterateurs-generateurs": {
   "label": "Itérateurs et générateurs",
   "card": "javascript",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-promesses": {
   "label": "Promesses",
   "card": "javascript",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-async-await": {
   "label": "`async` et `await`",
   "card": "javascript",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-boucle-evenements": {
   "label": "Boucle d'événements (pile, file de tâches, microtâches)",
   "card": "javascript",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-fetch": {
   "label": "`fetch` et requêtes HTTP depuis le navigateur",
   "card": "javascript",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-node-npm": {
   "label": "Node.js, npm et `package.json`",
   "card": "javascript",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ts-types-interfaces": {
   "label": "TypeScript : annotations, interfaces, unions et rétrécissement",
   "card": "javascript",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ts-generiques": {
   "label": "TypeScript : génériques",
   "card": "javascript",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-fonctionnel": {
   "label": "Style fonctionnel (fonctions pures, immutabilité, composition)",
   "card": "javascript",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-composants-interface": {
   "label": "Interface à composants (React : composants, propriétés, état, hooks)",
   "card": "javascript",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-etat-application": {
   "label": "État d'application (Redux : magasin, actions, réducteurs purs)",
   "card": "javascript",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-tests": {
   "label": "Tests (Jest ou Vitest, simulations, couverture)",
   "card": "javascript",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-outils-construction": {
   "label": "Construction (Vite ou webpack, transpilation, cartes de source)",
   "card": "javascript",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ts-types-avances": {
   "label": "TypeScript : types conditionnels et mappés, inférence, gardes de type",
   "card": "javascript",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ts-configuration": {
   "label": "TypeScript : `tsconfig` et mode strict",
   "card": "javascript",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-securite-navigateur": {
   "label": "Sécurité dans le navigateur (XSS par le DOM, CSP, stockage des jetons)",
   "card": "javascript",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-canvas-animation": {
   "label": "Canvas 2D et animation (`requestAnimationFrame`)",
   "card": "javascript",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-erreurs-asynchrones": {
   "label": "Erreurs asynchrones (rejets non gérés, annulation par `AbortController`)",
   "card": "javascript",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-mobile-multiplateforme": {
   "label": "Application mobile multiplateforme (React Native)",
   "card": "javascript",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-proxy-reflect": {
   "label": "`Proxy`, `Reflect` et métaprogrammation",
   "card": "javascript",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-moteur-jit": {
   "label": "Moteur et compilation à la volée (V8 : classes cachées, caches en ligne)",
   "card": "javascript",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-specification": {
   "label": "Spécification ECMAScript (opérations abstraites)",
   "card": "javascript",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-node-libuv": {
   "label": "Boucle d'événements de Node.js (libuv, phases)",
   "card": "javascript",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-workers-memoire-partagee": {
   "label": "Workers, `SharedArrayBuffer` et `Atomics`",
   "card": "javascript",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-ramasse-miettes": {
   "label": "Ramasse-miettes et fuites mémoire",
   "card": "javascript",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-interop-modules": {
   "label": "Interopérabilité CommonJS et modules ES",
   "card": "javascript",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "ts-compilateur": {
   "label": "TypeScript : API du compilateur et transformations",
   "card": "javascript",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "js-webassembly": {
   "label": "WebAssembly depuis JavaScript",
   "card": "javascript",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-noyau-distribution": {
   "label": "Noyau et distribution (rôle de chacun, appel système)",
   "card": "linux-systeme",
   "tier": "beginner",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "09/11/2026",
   "section": "Linux (système)"
  },
  "linux-hierarchie-fichiers": {
   "label": "Arborescence standard (FHS) et recherche de fichiers (`find`, `locate`, `which`)",
   "card": "linux-systeme",
   "tier": "beginner",
   "state": "découverte",
   "objective": "socle",
   "lastPractice": "11/11/2026",
   "section": "Linux (système)"
  },
  "linux-utilisateur-droits": {
   "label": "Utilisateur et droits (propriétaire, groupe, r/w/x, root)",
   "card": "linux-systeme",
   "tier": "beginner",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "16/11/2026",
   "section": "Linux (système)"
  },
  "linux-processus": {
   "label": "Processus (programme en cours d'exécution, PID, mémoire propre)",
   "card": "linux-systeme",
   "tier": "beginner",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "16/11/2026",
   "section": "Linux (système)"
  },
  "linux-variable-environnement": {
   "label": "Variable d'environnement (`export`, héritage par les processus enfants)",
   "card": "linux-systeme",
   "tier": "beginner",
   "state": "appliquée",
   "objective": "socle",
   "lastPractice": "16/11/2026",
   "section": "Linux (système)"
  },
  "linux-path": {
   "label": "`PATH` (dossiers où le shell cherche un programme, premier trouvé)",
   "card": "linux-systeme",
   "tier": "beginner",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "16/11/2026",
   "section": "Linux (système)"
  },
  "linux-liens-physiques-symboliques": {
   "label": "Liens physiques et symboliques (même inode contre chemin)",
   "card": "linux-systeme",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-partition": {
   "label": "Partition et montage (point de montage)",
   "card": "linux-systeme",
   "tier": "beginner",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "12/11/2026",
   "section": "Linux (système)"
  },
  "linux-gestion-paquets": {
   "label": "Gestion de paquets (dépôts, dépendances ; `apt` et `dpkg`, `dnf` et `rpm`, Flatpak)",
   "card": "linux-systeme",
   "tier": "beginner",
   "state": "découverte",
   "objective": "socle",
   "lastPractice": "09/11/2026",
   "section": "Linux (système)"
  },
  "linux-somme-de-controle": {
   "label": "Somme de contrôle (empreinte comparée à une référence de confiance)",
   "card": "linux-systeme",
   "tier": "beginner",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "12/11/2026",
   "section": "Linux (système)"
  },
  "linux-archives-compression": {
   "label": "Archives et compression (`tar`, `gzip`, `bzip2`, `xz`)",
   "card": "linux-systeme",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-editeur-texte": {
   "label": "Éditer un fichier en console (`vi`)",
   "card": "linux-systeme",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-peripheriques-detection": {
   "label": "Matériel détecté (`lspci`, `lsusb`, `lsmod`, `/proc`, `/sys`)",
   "card": "linux-systeme",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-montage-ordre-visibilite": {
   "label": "Ordre des montages (parent avant enfant, contenu masqué par un montage)",
   "card": "linux-systeme",
   "tier": "intermediate",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "11/11/2026",
   "section": "Linux (système)"
  },
  "linux-fstab": {
   "label": "`fstab` (six champs, montage par UUID ou étiquette au démarrage)",
   "card": "linux-systeme",
   "tier": "intermediate",
   "state": "appliquée",
   "objective": "socle",
   "lastPractice": "20/11/2026",
   "section": "Linux (système)"
  },
  "linux-systemes-fichiers": {
   "label": "Systèmes de fichiers (ext4, XFS, vfat ; inode, bloc, journal ; `mkfs`, `fsck`, `df`, `du`)",
   "card": "linux-systeme",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-systemes-fichiers-virtuels": {
   "label": "Systèmes de fichiers virtuels du noyau (`proc`, `sysfs`, `devpts`, `tmpfs`)",
   "card": "linux-systeme",
   "tier": "intermediate",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "12/11/2026",
   "section": "Linux (système)"
  },
  "linux-udev-devtmpfs": {
   "label": "`devtmpfs` et `udev` (fichiers de périphériques créés à la détection)",
   "card": "linux-systeme",
   "tier": "intermediate",
   "state": "découverte",
   "objective": "socle",
   "lastPractice": "11/11/2026",
   "section": "Linux (système)"
  },
  "linux-signaux-processus": {
   "label": "Signaux et contrôle des processus (`kill`, `top`, priorité `nice` et `renice`)",
   "card": "linux-systeme",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-demarrage": {
   "label": "Démarrage de la machine (BIOS ou UEFI, chargeur, noyau, init)",
   "card": "linux-systeme",
   "tier": "intermediate",
   "state": "appliquée",
   "objective": "socle",
   "lastPractice": "12/11/2026",
   "section": "Linux (système)"
  },
  "linux-grub-amorcage": {
   "label": "GRUB (installation du chargeur, `grub.cfg`, options du noyau)",
   "card": "linux-systeme",
   "tier": "intermediate",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "20/11/2026",
   "section": "Linux (système)"
  },
  "linux-init-systemd": {
   "label": "Gestion centrale du démarrage : systemd (unités, cibles, cible par défaut, activation au démarrage) et System V (`/etc/inittab`, niveaux d'exécution, scripts `rc`)",
   "card": "linux-systeme",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-journaux-systeme": {
   "label": "Journaux du système (`journalctl`, journal persistant, syslog, `dmesg`)",
   "card": "linux-systeme",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-planification-taches": {
   "label": "Tâches planifiées (`at`, cron, minuteries systemd)",
   "card": "linux-systeme",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-utilisateurs-groupes": {
   "label": "Comptes et groupes (`/etc/passwd`, `/etc/shadow`, vieillissement des mots de passe, `sudo`)",
   "card": "linux-systeme",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-swap": {
   "label": "Espace d'échange (partition ou fichier, `mkswap`, `swapon`)",
   "card": "linux-systeme",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-tables-partitions": {
   "label": "Tables de partitions MBR et GPT (`fdisk`, `gdisk`, `parted`)",
   "card": "linux-systeme",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-umask-bits-speciaux": {
   "label": "Droits par défaut (`umask`) et bits spéciaux (setgid sur dossier, sticky bit)",
   "card": "linux-systeme",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-configure-script": {
   "label": "Script `configure` (détection de l'hôte, `Makefile` généré)",
   "card": "linux-systeme",
   "tier": "advanced",
   "state": "découverte",
   "objective": "socle",
   "lastPractice": "12/11/2026",
   "section": "Linux (système)"
  },
  "linux-chroot": {
   "label": "Chroot (changer la racine d'un processus, isolement partiel)",
   "card": "linux-systeme",
   "tier": "advanced",
   "state": "découverte",
   "objective": "socle",
   "lastPractice": "09/11/2026",
   "section": "Linux (système)"
  },
  "linux-lvm-raid": {
   "label": "Volumes logiques (LVM : volumes physiques, groupes, extension) et RAID logiciel",
   "card": "linux-systeme",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-namespaces-cgroups": {
   "label": "Espaces de noms et cgroups (base des conteneurs)",
   "card": "linux-systeme",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-setuid-capacites": {
   "label": "`setuid` et capacités POSIX (privilège partiel d'un programme)",
   "card": "linux-systeme",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-diagnostic-performance": {
   "label": "Diagnostic (charge, `vmstat`, `iostat`, `strace`, `lsof`, profils `tuned`)",
   "card": "linux-systeme",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-virtualisation-hote-invite": {
   "label": "Virtualisation (hôte, invité, QEMU/KVM, libvirt et `virsh`)",
   "card": "linux-systeme",
   "tier": "advanced",
   "state": "découverte",
   "objective": "socle",
   "lastPractice": "22/10/2026",
   "section": "Linux (système)"
  },
  "linux-recuperation-demarrage": {
   "label": "Reprendre la main au démarrage (mode secours, mot de passe root oublié, réparation)",
   "card": "linux-systeme",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-selinux-administration": {
   "label": "SELinux en pratique (modes, contextes, restauration, étiquettes de ports, booléens)",
   "card": "linux-systeme",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-limites-ressources": {
   "label": "Limites de ressources (`ulimit`, `limits.conf`)",
   "card": "linux-systeme",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-acl": {
   "label": "Listes de contrôle d'accès (`getfacl`, `setfacl`)",
   "card": "linux-systeme",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-git-administration": {
   "label": "Git pour l'administration (dépôt, commit, branche, configuration versionnée)",
   "card": "linux-systeme",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-affichage-x11": {
   "label": "Serveur X, gestionnaire de fenêtres, environnement de bureau, accessibilité",
   "card": "linux-systeme",
   "tier": "advanced",
   "state": "découverte",
   "objective": "socle",
   "lastPractice": "10/11/2026",
   "section": "Linux (système)"
  },
  "linux-localisation": {
   "label": "Localisation (locale, fuseau horaire, encodage)",
   "card": "linux-systeme",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-gpg-chiffrement": {
   "label": "Chiffrer et signer des données (GPG)",
   "card": "linux-systeme",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-securite-mac": {
   "label": "Politiques MAC sur mesure (module SELinux, profil AppArmor)",
   "card": "linux-systeme",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-ordonnanceur-priorites": {
   "label": "Ordonnanceur vu de l'administrateur (CFS, temps réel, affinité processeur)",
   "card": "linux-systeme",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-memoire-virtuelle-admin": {
   "label": "Mémoire sous charge (cache de pages, surallocation, OOM killer)",
   "card": "linux-systeme",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-tracage-ebpf": {
   "label": "Traçage du noyau en production (`perf`, eBPF)",
   "card": "linux-systeme",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-sysctl-reglages": {
   "label": "Paramètres du noyau, persistants ou non (`sysctl`, `/proc/sys`)",
   "card": "linux-systeme",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-prediction-jeton": {
   "label": "Modèle de langage : prédire le jeton suivant",
   "card": "llm",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-tokenisation": {
   "label": "Tokenisation et vocabulaire",
   "card": "llm",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-prompt-bases": {
   "label": "Prompt (rôle, instructions, contexte)",
   "card": "llm",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-api-parametres": {
   "label": "Appeler un modèle par API (température, top-p, longueur maximale)",
   "card": "llm",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-fenetre-contexte": {
   "label": "Fenêtre de contexte",
   "card": "llm",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-hallucinations": {
   "label": "Hallucinations et limites",
   "card": "llm",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-embeddings": {
   "label": "Plongements de texte et similarité",
   "card": "llm",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-few-shot": {
   "label": "Apprentissage zéro, un ou quelques exemples",
   "card": "llm",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-sorties-structurees": {
   "label": "Contrôler la sortie (format, JSON)",
   "card": "llm",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-cas-usage": {
   "label": "Cas d'usage (assistant conversationnel, résumé, extraction)",
   "card": "llm",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-chaine-pensee": {
   "label": "Chaîne de pensée",
   "card": "llm",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-rag": {
   "label": "Génération augmentée par récupération (RAG)",
   "card": "llm",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-bases-vectorielles": {
   "label": "Bases vectorielles",
   "card": "llm",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-decoupage-curation": {
   "label": "Préparer un corpus pour le RAG (curation, découpage, indexation)",
   "card": "llm",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-appel-outils": {
   "label": "Appel d'outils",
   "card": "llm",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-agents": {
   "label": "Agents (boucle, planification, mémoire)",
   "card": "llm",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-evaluation": {
   "label": "Évaluation (métriques quantitatives et qualitatives, benchmarks, modèle juge)",
   "card": "llm",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-transformeur": {
   "label": "Architecture du transformeur (encodeur, décodeur)",
   "card": "llm",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-attention": {
   "label": "Mécanisme d'attention (auto-attention, têtes, positions)",
   "card": "llm",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-preparation-donnees": {
   "label": "Préparer des données d'entraînement (nettoyage, déduplication, collecte)",
   "card": "llm",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-garde-fous": {
   "label": "Garde-fous et injection de prompt",
   "card": "llm",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-bibliotheques-nlp": {
   "label": "Bibliothèques NLP en Python (Hugging Face `transformers`, `tokenizers`, spaCy)",
   "card": "llm",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-cout-latence": {
   "label": "Coût par jeton, latence et cache de prompt",
   "card": "llm",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-pre-entrainement": {
   "label": "Pré-entraînement",
   "card": "llm",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-fine-tuning": {
   "label": "Affinage supervisé",
   "card": "llm",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-peft-lora": {
   "label": "Affinage à paramètres efficaces (LoRA)",
   "card": "llm",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-alignement-rlhf": {
   "label": "Alignement (RLHF, DPO, collecte de préférences humaines)",
   "card": "llm",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-adaptation-domaine": {
   "label": "Adaptation à un domaine ou à une nouvelle distribution",
   "card": "llm",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-echantillonnage": {
   "label": "Échantillonnage avancé (top-k, faisceau, décodage contraint)",
   "card": "llm",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-quantification": {
   "label": "Quantification",
   "card": "llm",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-service-inference": {
   "label": "Servir un modèle (serveur d'inférence, Triton, vLLM, conteneurs, Kubernetes)",
   "card": "llm",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-batching-cache-kv": {
   "label": "Débit et latence (lots continus, cache KV)",
   "card": "llm",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-surveillance-production": {
   "label": "Surveillance en production (tableaux de bord, anomalies, versions, réentraînement)",
   "card": "llm",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-cadre-evaluation": {
   "label": "Concevoir un cadre d'évaluation (analyse d'erreurs, échelle, comparaison d'agents)",
   "card": "llm",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-securite-adversariale": {
   "label": "Attaques adverses (contournement, injection indirecte, exfiltration)",
   "card": "llm",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-audit-biais": {
   "label": "Audit de biais et d'équité",
   "card": "llm",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-multimodal": {
   "label": "Modèles multimodaux",
   "card": "llm",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-parallelisme-distribue": {
   "label": "Parallélisme distribué (données, tenseurs, pipeline, ZeRO)",
   "card": "llm",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-optimisation-gpu": {
   "label": "Optimisation GPU (profilage, mémoire, noyaux d'attention optimisés)",
   "card": "llm",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-lois-echelle": {
   "label": "Lois d'échelle",
   "card": "llm",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-melange-experts": {
   "label": "Mélange d'experts",
   "card": "llm",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-contextes-longs": {
   "label": "Positions et contextes longs (RoPE, extension)",
   "card": "llm",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-decodage-speculatif": {
   "label": "Décodage spéculatif",
   "card": "llm",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-distillation": {
   "label": "Distillation",
   "card": "llm",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-interpretabilite-mecaniste": {
   "label": "Interprétabilité mécaniste",
   "card": "llm",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-compilation-inference": {
   "label": "Compilation pour l'inférence (TensorRT-LLM)",
   "card": "llm",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "llm-modeles-raisonnement": {
   "label": "Modèles de raisonnement (apprentissage par renforcement, calcul au moment du test)",
   "card": "llm",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-notations": {
   "label": "Notations Σ, Π, indices et fonctions",
   "card": "mathematiques-ia",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-vecteurs": {
   "label": "Vecteurs (composantes, addition, multiplication par un scalaire)",
   "card": "mathematiques-ia",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-matrices": {
   "label": "Matrices (dimensions, addition, transposée)",
   "card": "mathematiques-ia",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-produit-scalaire": {
   "label": "Produit scalaire, norme et angle",
   "card": "mathematiques-ia",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-fonctions-usuelles": {
   "label": "Fonctions usuelles (affine, polynôme, exponentielle, logarithme)",
   "card": "mathematiques-ia",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-derivee": {
   "label": "Dérivée d'une fonction d'une variable (pente, règles de calcul)",
   "card": "mathematiques-ia",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-pourcentages-erreurs": {
   "label": "Erreurs et écarts (absolu, relatif, carré, moyenne)",
   "card": "mathematiques-ia",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-esperance-variance": {
   "label": "Espérance, variance et écart-type d'une variable aléatoire",
   "card": "mathematiques-ia",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-logique-booleenne": {
   "label": "Logique booléenne (tables de vérité, lois de De Morgan, formes normales)",
   "card": "mathematiques-ia",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-ensembles": {
   "label": "Ensembles (union, intersection, complémentaire, produit cartésien)",
   "card": "mathematiques-ia",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-produit-matriciel": {
   "label": "Produit matriciel et composition d'applications linéaires",
   "card": "mathematiques-ia",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-systemes-lineaires": {
   "label": "Systèmes linéaires et élimination de Gauss",
   "card": "mathematiques-ia",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-determinant-inverse": {
   "label": "Déterminant, rang et inverse d'une matrice",
   "card": "mathematiques-ia",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-derivees-partielles": {
   "label": "Dérivées partielles et gradient d'une fonction de plusieurs variables",
   "card": "mathematiques-ia",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-regle-chaine": {
   "label": "Règle de dérivation en chaîne (fonctions composées)",
   "card": "mathematiques-ia",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-lois-probabilite": {
   "label": "Lois de probabilité (Bernoulli, binomiale, uniforme, normale)",
   "card": "mathematiques-ia",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-probabilites-conditionnelles": {
   "label": "Probabilités conditionnelles et théorème de Bayes",
   "card": "mathematiques-ia",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-covariance-correlation": {
   "label": "Covariance et corrélation",
   "card": "mathematiques-ia",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-vraisemblance": {
   "label": "Vraisemblance et estimation par maximum de vraisemblance",
   "card": "mathematiques-ia",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-sigmoide-softmax": {
   "label": "Sigmoïde, softmax et leurs dérivées",
   "card": "mathematiques-ia",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-entropie-croisee": {
   "label": "Entropie et entropie croisée (perte logarithmique)",
   "card": "mathematiques-ia",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-projections": {
   "label": "Projections et matrices de projection (perspective comprise)",
   "card": "mathematiques-ia",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-espaces-vectoriels": {
   "label": "Espaces vectoriels, bases et changement de base",
   "card": "mathematiques-ia",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-valeurs-propres": {
   "label": "Valeurs et vecteurs propres, diagonalisation",
   "card": "mathematiques-ia",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-svd": {
   "label": "Décomposition en valeurs singulières",
   "card": "mathematiques-ia",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-jacobienne-hessienne": {
   "label": "Matrice jacobienne et matrice hessienne",
   "card": "mathematiques-ia",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-convexite": {
   "label": "Fonctions convexes, minimums locaux et globaux",
   "card": "mathematiques-ia",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-series-fourier": {
   "label": "Séries et transformée de Fourier (fréquences d'un signal)",
   "card": "mathematiques-ia",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-tests-statistiques": {
   "label": "Tests d'hypothèse, p-valeur et intervalles de confiance",
   "card": "mathematiques-ia",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-nombres-complexes": {
   "label": "Nombres complexes (forme algébrique et exponentielle)",
   "card": "mathematiques-ia",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-interpolation-lineaire": {
   "label": "Interpolation et combinaison linéaires",
   "card": "mathematiques-ia",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-normes-matricielles": {
   "label": "Normes de matrices et conditionnement",
   "card": "mathematiques-ia",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-algebre-ensembles": {
   "label": "Algèbre de Boole, ensembles et leur correspondance (courbe remplissant l'espace comprise)",
   "card": "mathematiques-ia",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-calcul-tensoriel": {
   "label": "Tenseurs et dérivation de fonctions à valeurs tensorielles",
   "card": "mathematiques-ia",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-theorie-information": {
   "label": "Théorie de l'information (divergence de Kullback-Leibler, information mutuelle)",
   "card": "mathematiques-ia",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-chaines-markov": {
   "label": "Chaînes de Markov et processus de décision markoviens",
   "card": "mathematiques-ia",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-optimisation-contrainte": {
   "label": "Optimisation sous contrainte (multiplicateurs de Lagrange, dualité)",
   "card": "mathematiques-ia",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-stabilite-numerique": {
   "label": "Stabilité numérique (flottants, annulation, log-somme-exp)",
   "card": "mathematiques-ia",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-convergence": {
   "label": "Vitesse de convergence des méthodes itératives",
   "card": "mathematiques-ia",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-noyaux": {
   "label": "Noyaux et espaces de caractéristiques (astuce du noyau)",
   "card": "mathematiques-ia",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-geometrie-grande-dimension": {
   "label": "Géométrie en grande dimension (malédiction de la dimension, concentration de la mesure)",
   "card": "mathematiques-ia",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-differentiation-automatique": {
   "label": "Différentiation automatique (modes direct et inverse, graphe de calcul)",
   "card": "mathematiques-ia",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-transformee-discrete": {
   "label": "Transformée de Fourier discrète et rapide (FFT), complexité",
   "card": "mathematiques-ia",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "maths-matrices-aleatoires": {
   "label": "Matrices aléatoires et initialisation des poids (variance conservée d'une couche à l'autre)",
   "card": "mathematiques-ia",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-materiel-composants": {
   "label": "Composants d'un ordinateur (carte mère, processeur, RAM, stockage, BIOS)",
   "card": "noyau-assembleur",
   "tier": "beginner",
   "state": "comprise",
   "objective": "socle",
   "lastPractice": "08/11/2026",
   "section": "Noyau et assembleur"
  },
  "linux-chaine-disque-reseau": {
   "label": "Du disque au réseau (bits, octets, RAM, carte réseau)",
   "card": "noyau-assembleur",
   "tier": "beginner",
   "state": "comprise",
   "objective": "socle",
   "lastPractice": "17/11/2026",
   "section": "Noyau et assembleur"
  },
  "noyau-binaire-hexadecimal": {
   "label": "Binaire, hexadécimal, octets et boutisme",
   "card": "noyau-assembleur",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "noyau-registres-pile-x86": {
   "label": "Registres x86 et pile (`eip`, `esp`, `ebp`, `push`, `pop`)",
   "card": "noyau-assembleur",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "noyau-instructions-base": {
   "label": "Instructions de base (`mov`, `add`, `cmp`, sauts conditionnels, `call`, `ret`)",
   "card": "noyau-assembleur",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "noyau-espace-noyau-utilisateur": {
   "label": "Espace noyau et espace utilisateur (anneaux de protection)",
   "card": "noyau-assembleur",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-modules-noyau": {
   "label": "Module intégré ou chargeable (`y`, `m`, fichier `.ko`)",
   "card": "noyau-assembleur",
   "tier": "beginner",
   "state": "découverte",
   "objective": "socle",
   "lastPractice": "10/11/2026",
   "section": "Noyau et assembleur"
  },
  "linux-noyau-configuration": {
   "label": "Configurer, compiler et installer un noyau",
   "card": "noyau-assembleur",
   "tier": "beginner",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "17/11/2026",
   "section": "Noyau et assembleur"
  },
  "noyau-module-premier": {
   "label": "Écrire un module (`init` et `exit`, `printk`, Kbuild, `insmod`, `rmmod`)",
   "card": "noyau-assembleur",
   "tier": "beginner",
   "state": "appliquée",
   "objective": "socle",
   "lastPractice": "17/11/2026",
   "section": "Noyau et assembleur"
  },
  "noyau-module-kbuild": {
   "label": "Makefile d'un module hors de l'arbre (`obj-m`, `make -C … M=`, version du noyau lue, `vermagic`)",
   "card": "noyau-assembleur",
   "tier": "beginner",
   "state": "appliquée",
   "objective": "socle",
   "lastPractice": "21/11/2026",
   "section": "Noyau et assembleur"
  },
  "noyau-version-noyau": {
   "label": "Version du noyau (`VERSION`, `EXTRAVERSION`, `LOCALVERSION`, suffixe du dépôt)",
   "card": "noyau-assembleur",
   "tier": "beginner",
   "state": "appliquée",
   "objective": "socle",
   "lastPractice": "20/11/2026",
   "section": "Noyau et assembleur"
  },
  "noyau-convention-appel": {
   "label": "Conventions d'appel et cadre de pile (arguments, registres sauvegardés, ABI)",
   "card": "noyau-assembleur",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "noyau-multiboot-grub": {
   "label": "Amorçage multiboot (en-tête, GRUB charge le noyau, point d'entrée en assembleur)",
   "card": "noyau-assembleur",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "noyau-script-edition-liens": {
   "label": "Script de l'éditeur de liens (sections, adresse de chargement)",
   "card": "noyau-assembleur",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "noyau-compilation-autonome": {
   "label": "Compilation autonome (`-ffreestanding`, `-nostdlib`, compilateur croisé i386)",
   "card": "noyau-assembleur",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "noyau-memoire-video-texte": {
   "label": "Écran en mode texte (mémoire `0xB8000`, caractère et attribut)",
   "card": "noyau-assembleur",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "noyau-ports-entree-sortie": {
   "label": "Ports d'entrée-sortie (`in`, `out`) et clavier PS/2 (codes de touche)",
   "card": "noyau-assembleur",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "noyau-gdt-segmentation": {
   "label": "Segmentation et GDT (descripteurs, sélecteurs, `lgdt`)",
   "card": "noyau-assembleur",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "noyau-interruptions-idt": {
   "label": "Interruptions et IDT (exceptions, IRQ, PIC, `iret`)",
   "card": "noyau-assembleur",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "noyau-pagination": {
   "label": "Pagination (répertoire et tables de pages, `cr3`, adresse virtuelle et physique)",
   "card": "noyau-assembleur",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "noyau-allocateur-memoire": {
   "label": "Allocation physique et virtuelle (cadres de pages, `kmalloc`, `kfree`)",
   "card": "noyau-assembleur",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "noyau-appels-systeme": {
   "label": "Appels système (interruption ou `syscall`, numéro, arguments en registres, table)",
   "card": "noyau-assembleur",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "noyau-pilote-caractere": {
   "label": "Pilote de périphérique caractère (misc device, `file_operations`, `copy_to_user`)",
   "card": "noyau-assembleur",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "noyau-interfaces-utilisateur": {
   "label": "Interfaces noyau-utilisateur (debugfs, sysfs, procfs, `ioctl`)",
   "card": "noyau-assembleur",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "noyau-style-code": {
   "label": "Style de code du noyau (`coding-style.rst`, `checkpatch`)",
   "card": "noyau-assembleur",
   "tier": "intermediate",
   "state": "appliquée",
   "objective": "socle",
   "lastPractice": "17/11/2026",
   "section": "Noyau et assembleur"
  },
  "noyau-patch": {
   "label": "Patch et message de commit du noyau (format, signature, `git format-patch`)",
   "card": "noyau-assembleur",
   "tier": "intermediate",
   "state": "appliquée",
   "objective": "socle",
   "lastPractice": "19/11/2026",
   "section": "Noyau et assembleur"
  },
  "noyau-processus-structure": {
   "label": "Structure d'un processus côté noyau (PID, état, parent et enfants, pile, tas)",
   "card": "noyau-assembleur",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "noyau-ordonnancement-contexte": {
   "label": "Ordonnancement et changement de contexte (tic d'horloge, registres sauvegardés)",
   "card": "noyau-assembleur",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "noyau-fork-exec-wait": {
   "label": "`fork`, `exec`, `wait`, `exit` côté noyau (copie d'espace d'adresses)",
   "card": "noyau-assembleur",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "noyau-signaux": {
   "label": "Signaux côté noyau (file d'attente, livraison au tic suivant)",
   "card": "noyau-assembleur",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "noyau-ata-ide": {
   "label": "Lecture et écriture d'un disque ATA en mode PIO",
   "card": "noyau-assembleur",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "noyau-ext2": {
   "label": "ext2 (superbloc, groupes, inodes, blocs)",
   "card": "noyau-assembleur",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "noyau-vfs": {
   "label": "Couche VFS (inode générique, montages, dossier courant par processus)",
   "card": "noyau-assembleur",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "noyau-ipc-sockets": {
   "label": "Communication entre processus (sockets, descripteurs partagés)",
   "card": "noyau-assembleur",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "noyau-elf-chargeur": {
   "label": "Format ELF et chargeur (en-têtes, segments, `execve`)",
   "card": "noyau-assembleur",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "noyau-api-modules": {
   "label": "API de modules d'un noyau (enregistrement, rappels, symboles exportés)",
   "card": "noyau-assembleur",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "noyau-chargement-automatique": {
   "label": "Chargement automatique d'un module (`MODULE_DEVICE_TABLE`, hotplug)",
   "card": "noyau-assembleur",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "noyau-concurrence": {
   "label": "Concurrence dans le noyau (spinlock, mutex, contexte d'interruption)",
   "card": "noyau-assembleur",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "noyau-copie-sur-ecriture": {
   "label": "Copie sur écriture et défaut de page",
   "card": "noyau-assembleur",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "noyau-tlb-caches": {
   "label": "TLB, caches et leur invalidation",
   "card": "noyau-assembleur",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "noyau-mode-long": {
   "label": "Passage en mode protégé puis long (x86-64, pagination à 4 niveaux)",
   "card": "noyau-assembleur",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "noyau-smp-apic": {
   "label": "Multiprocesseur (APIC, interruptions entre processeurs)",
   "card": "noyau-assembleur",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "noyau-rcu-barrieres": {
   "label": "RCU et barrières mémoire",
   "card": "noyau-assembleur",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "noyau-dma-pilotes-bloc": {
   "label": "DMA, pilotes bloc et ordonnanceur d'entrées-sorties",
   "card": "noyau-assembleur",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "noyau-debogage": {
   "label": "Débogage du noyau (oops, panique, QEMU et `gdb`)",
   "card": "noyau-assembleur",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "noyau-protections": {
   "label": "Protections du noyau (KASLR, SMEP, SMAP)",
   "card": "noyau-assembleur",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-variables-types": {
   "label": "Syntaxe, variables et types",
   "card": "php",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-tableaux": {
   "label": "Tableaux indexés et associatifs, fonctions de tableaux",
   "card": "php",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-fonctions": {
   "label": "Fonctions",
   "card": "php",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-conditions-boucles": {
   "label": "Conditions et boucles",
   "card": "php",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-chaines": {
   "label": "Chaînes, interpolation et formatage",
   "card": "php",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-requete-reponse": {
   "label": "Cycle requête-réponse et superglobales (`$_GET`, `$_POST`)",
   "card": "php",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-inclusion": {
   "label": "Inclusion de fichiers (`include`, `require`)",
   "card": "php",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-erreurs": {
   "label": "Erreurs, avertissements et journaux",
   "card": "php",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-classes-objets": {
   "label": "Classes et objets",
   "card": "php",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-espaces-noms-autoload": {
   "label": "Espaces de noms et chargement automatique (PSR-4)",
   "card": "php",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-composer": {
   "label": "Composer et dépendances",
   "card": "php",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-pdo-requetes-preparees": {
   "label": "PDO, requêtes préparées et transactions",
   "card": "php",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-sessions-cookies": {
   "label": "Sessions et cookies",
   "card": "php",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-exceptions": {
   "label": "Exceptions",
   "card": "php",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-xss-csrf": {
   "label": "Échappement des sorties, protection CSRF, injection SQL",
   "card": "php",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-typage-strict": {
   "label": "Déclarations de types et `strict_types`",
   "card": "php",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-framework-cms": {
   "label": "Framework et CMS (routage, modules, hooks)",
   "card": "php",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-tests-phpunit": {
   "label": "Tests avec PHPUnit",
   "card": "php",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-formats-donnees": {
   "label": "Formats de données (JSON, XML, dates avec `DateTime`)",
   "card": "php",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-formulaires-en-tetes": {
   "label": "Formulaires, en-têtes HTTP et téléversement de fichiers",
   "card": "php",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-expressions-regulieres": {
   "label": "Expressions régulières (PCRE)",
   "card": "php",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-mots-de-passe": {
   "label": "Hachage des mots de passe (`password_hash`, `password_verify`)",
   "card": "php",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-interfaces-traits": {
   "label": "Interfaces, classes abstraites et traits",
   "card": "php",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-injection-dependances": {
   "label": "Injection de dépendances",
   "card": "php",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-generateurs": {
   "label": "Générateurs et itérateurs",
   "card": "php",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-psr": {
   "label": "Recommandations PSR (HTTP, journaux, style)",
   "card": "php",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-opcache": {
   "label": "OPcache et cache d'application",
   "card": "php",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-closures": {
   "label": "Fermetures et appelables",
   "card": "php",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-nouveautes-8": {
   "label": "Apports de PHP 8 (`enum`, `readonly`, `match`, arguments nommés)",
   "card": "php",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-api-rest": {
   "label": "API REST en PHP",
   "card": "php",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-flux-fichiers": {
   "label": "Fichiers, flux et contextes de flux",
   "card": "php",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-spl": {
   "label": "Bibliothèque standard (SPL : structures, itérateurs, exceptions)",
   "card": "php",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-moteur-zend": {
   "label": "Moteur Zend (zval, comptage de références, ramasse-miettes)",
   "card": "php",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-fpm": {
   "label": "PHP-FPM et modèle de processus",
   "card": "php",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-profilage": {
   "label": "Profilage (Xdebug, Blackfire)",
   "card": "php",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-reflexion-attributs": {
   "label": "Réflexion et attributs",
   "card": "php",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-analyse-statique": {
   "label": "Analyse statique (PHPStan, Psalm)",
   "card": "php",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-asynchrone": {
   "label": "Asynchrone (Fibers, boucle d'événements)",
   "card": "php",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-deserialisation": {
   "label": "Désérialisation non sûre et injection d'objets",
   "card": "php",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "php-jit": {
   "label": "Compilateur JIT",
   "card": "php",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-expressions-liaisons": {
   "label": "Tout est expression ; liaison `let` et immuabilité",
   "card": "programmation-fonctionnelle",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-types-inference": {
   "label": "Types de base et inférence de type",
   "card": "programmation-fonctionnelle",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-fonctions-valeurs": {
   "label": "Fonctions comme valeurs, curryfication, application partielle",
   "card": "programmation-fonctionnelle",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-recursivite-terminale": {
   "label": "Récursivité et appel terminal",
   "card": "programmation-fonctionnelle",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-listes": {
   "label": "Listes (construction, tête et queue)",
   "card": "programmation-fonctionnelle",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-filtrage-motif": {
   "label": "Filtrage par motif (`match`, exhaustivité)",
   "card": "programmation-fonctionnelle",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-variants-records": {
   "label": "Types somme (variants) et produit (enregistrements)",
   "card": "programmation-fonctionnelle",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-option-result": {
   "label": "Absence et erreur comme valeurs (`option`, `result`)",
   "card": "programmation-fonctionnelle",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-compilation-dune": {
   "label": "Compiler (`ocamlc`, `ocamlopt`, `dune`, toplevel)",
   "card": "programmation-fonctionnelle",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-ordre-superieur": {
   "label": "Fonctions d'ordre supérieur (`map`, `filter`, `fold`)",
   "card": "programmation-fonctionnelle",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-polymorphisme": {
   "label": "Polymorphisme paramétrique (`'a`)",
   "card": "programmation-fonctionnelle",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-modules-signatures": {
   "label": "Modules et signatures (interface `.mli`, type abstrait)",
   "card": "programmation-fonctionnelle",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-exceptions": {
   "label": "Exceptions",
   "card": "programmation-fonctionnelle",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-references-mutables": {
   "label": "Effets de bord et mutabilité (`ref`, tableaux, champs `mutable`)",
   "card": "programmation-fonctionnelle",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-purete-transparence": {
   "label": "Fonction pure et transparence référentielle",
   "card": "programmation-fonctionnelle",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-json-parsing": {
   "label": "Lire un JSON vers ses propres types",
   "card": "programmation-fonctionnelle",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-collections-stdlib": {
   "label": "Collections de la bibliothèque standard (`Map`, `Set`, `Hashtbl`)",
   "card": "programmation-fonctionnelle",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-types-recursifs": {
   "label": "Types récursifs et arbres",
   "card": "programmation-fonctionnelle",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-opam-bibliotheques": {
   "label": "Paquets et bibliothèques (opam)",
   "card": "programmation-fonctionnelle",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-sequences-paresse": {
   "label": "Séquences et évaluation paresseuse (`Seq`, `lazy`)",
   "card": "programmation-fonctionnelle",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-foncteurs": {
   "label": "Foncteurs (modules paramétrés)",
   "card": "programmation-fonctionnelle",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-concurrence-lwt": {
   "label": "Concurrence coopérative (promesses et threads de Lwt)",
   "card": "programmation-fonctionnelle",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-eliom-client-serveur": {
   "label": "Application client-serveur avec Ocsigen et Eliom",
   "card": "programmation-fonctionnelle",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-js-of-ocaml": {
   "label": "Compilation vers JavaScript et DOM typé (js_of_ocaml, TyXML)",
   "card": "programmation-fonctionnelle",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-variants-polymorphes": {
   "label": "Variants polymorphes",
   "card": "programmation-fonctionnelle",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-objets": {
   "label": "Objets et classes d'OCaml",
   "card": "programmation-fonctionnelle",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-monades": {
   "label": "Monades et opérateurs `let*`",
   "card": "programmation-fonctionnelle",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-modules-premiere-classe": {
   "label": "Modules de première classe",
   "card": "programmation-fonctionnelle",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-continuations": {
   "label": "Style par passage de continuations",
   "card": "programmation-fonctionnelle",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-types-fantomes": {
   "label": "Types fantômes et types abstraits pour imposer des invariants",
   "card": "programmation-fonctionnelle",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-gadt": {
   "label": "Types algébriques généralisés (GADT)",
   "card": "programmation-fonctionnelle",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-hindley-milner": {
   "label": "Algorithme d'inférence Hindley-Milner",
   "card": "programmation-fonctionnelle",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-effets-ocaml5": {
   "label": "Gestionnaires d'effets et domaines d'OCaml 5",
   "card": "programmation-fonctionnelle",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-representation-gc": {
   "label": "Représentation des valeurs et ramasse-miettes générationnel",
   "card": "programmation-fonctionnelle",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-ppx": {
   "label": "Métaprogrammation par PPX",
   "card": "programmation-fonctionnelle",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-lambda-calcul": {
   "label": "Lambda-calcul",
   "card": "programmation-fonctionnelle",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-optimisation-flambda": {
   "label": "Optimisation du compilateur (flambda, inlining)",
   "card": "programmation-fonctionnelle",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "fonctionnel-structures-persistantes": {
   "label": "Structures de données persistantes et partage",
   "card": "programmation-fonctionnelle",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "python-types-variables": {
   "label": "Types, variables et références",
   "card": "python",
   "tier": "beginner",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "17/11/2026",
   "section": "Python"
  },
  "python-operateurs-entrees-sorties": {
   "label": "Structure d'un programme, opérateurs et expressions, entrées-sorties console (`print`, `input`) et conversions de types",
   "card": "python",
   "tier": "beginner",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "17/11/2026",
   "section": "Python"
  },
  "python-conditions-boucles": {
   "label": "Conditions et boucles (`else` de boucle, `match`)",
   "card": "python",
   "tier": "beginner",
   "state": "comprise",
   "objective": "socle",
   "lastPractice": "17/11/2026",
   "section": "Python"
  },
  "python-fonctions": {
   "label": "Fonctions (arguments par défaut, `*args`, `**kwargs`, portée)",
   "card": "python",
   "tier": "beginner",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "17/11/2026",
   "section": "Python"
  },
  "python-listes-tuples": {
   "label": "Listes et tuples",
   "card": "python",
   "tier": "beginner",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "17/11/2026",
   "section": "Python"
  },
  "python-dictionnaires-ensembles": {
   "label": "Dictionnaires et ensembles",
   "card": "python",
   "tier": "beginner",
   "state": "comprise",
   "objective": "socle",
   "lastPractice": "17/11/2026",
   "section": "Python"
  },
  "python-chaines": {
   "label": "Chaînes (Unicode, UTF-8, immuabilité, méthodes, `f-strings`)",
   "card": "python",
   "tier": "beginner",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "17/11/2026",
   "section": "Python"
  },
  "python-fichiers-flux": {
   "label": "Fichiers et flux texte ou binaires (`pathlib`, `bytearray`, module `csv`)",
   "card": "python",
   "tier": "beginner",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "17/11/2026",
   "section": "Python"
  },
  "python-modules-paquets": {
   "label": "Modules et paquets (import, chemins de recherche, `pip`, modules `math` et `random`)",
   "card": "python",
   "tier": "beginner",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "17/11/2026",
   "section": "Python"
  },
  "python-exceptions": {
   "label": "Exceptions (ordre des `except`, `else`, `finally`, exceptions personnalisées)",
   "card": "python",
   "tier": "beginner",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "17/11/2026",
   "section": "Python"
  },
  "python-comprehensions": {
   "label": "Compréhensions",
   "card": "python",
   "tier": "beginner",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "17/11/2026",
   "section": "Python"
  },
  "python-environnements-virtuels": {
   "label": "Environnements virtuels (`venv`)",
   "card": "python",
   "tier": "beginner",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "17/11/2026",
   "section": "Python"
  },
  "python-tests-debogage": {
   "label": "Tests et débogage (`unittest`, `assert`, trace d'appels)",
   "card": "python",
   "tier": "beginner",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "17/11/2026",
   "section": "Python"
  },
  "python-developpement-collaboratif": {
   "label": "Développement collaboratif (dépôt, branche, revue, intégration continue, code assisté par IA validé à part)",
   "card": "python",
   "tier": "beginner",
   "state": "comprise",
   "objective": "socle",
   "lastPractice": "17/11/2026",
   "section": "Python"
  },
  "python-classes-objets": {
   "label": "Classes et objets (attributs, `__init__`, introspection, noms brouillés)",
   "card": "python",
   "tier": "intermediate",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "21/11/2026",
   "section": "Python"
  },
  "python-heritage-mro": {
   "label": "Héritage multiple, ordre de résolution (MRO) et polymorphisme",
   "card": "python",
   "tier": "intermediate",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "21/11/2026",
   "section": "Python"
  },
  "python-lambda-fermetures": {
   "label": "`lambda`, `map`, `filter` et fermetures",
   "card": "python",
   "tier": "intermediate",
   "state": "comprise",
   "objective": "socle",
   "lastPractice": "21/11/2026",
   "section": "Python"
  },
  "python-methodes-speciales": {
   "label": "Méthodes spéciales et extension des types natifs",
   "card": "python",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "python-decorateurs": {
   "label": "Décorateurs",
   "card": "python",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "python-methodes-classe": {
   "label": "Méthodes de classe et statiques, objets appelables",
   "card": "python",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "python-gestionnaires-contexte": {
   "label": "Gestionnaires de contexte (`with`)",
   "card": "python",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "python-dataclasses-annotations": {
   "label": "Annotations de type et `dataclasses`",
   "card": "python",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "python-serialisation": {
   "label": "Identité, copie et sérialisation (JSON, CSV, XML, `pickle`)",
   "card": "python",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "python-expressions-regulieres": {
   "label": "Expressions régulières",
   "card": "python",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "python-formatage": {
   "label": "Formatage des chaînes et risques d'interpolation",
   "card": "python",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "python-conventions-qualite": {
   "label": "Conventions et qualité (PEP 8, 20, 257 ; Ruff, Pylint, Black ; couverture)",
   "card": "python",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "python-http-rest": {
   "label": "HTTP et API REST",
   "card": "python",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "python-sqlite": {
   "label": "SQLite depuis Python",
   "card": "python",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "python-journalisation": {
   "label": "Journalisation (`logging`, gestionnaires, propagation, JSON)",
   "card": "python",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "python-descripteurs": {
   "label": "Descripteurs et règles de recherche d'attribut",
   "card": "python",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "python-abc-metaclasses": {
   "label": "Classes abstraites, métaclasses, `__init_subclass__`, registres",
   "card": "python",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "python-groupes-exceptions": {
   "label": "Exceptions chaînées, notes, `ExceptionGroup` et `except*`",
   "card": "python",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "python-protocoles-variance": {
   "label": "Protocoles, typage structurel et variance",
   "card": "python",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "python-generateurs-pipelines": {
   "label": "Générateurs et chaînes de traitement (`yield from`, `itertools`, `functools`)",
   "card": "python",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "python-memoisation": {
   "label": "Mémoïsation et politiques de cache",
   "card": "python",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "python-packaging": {
   "label": "Construire et distribuer (wheels, `pyproject.toml`, Poetry, `uv`, verrous, Conda)",
   "card": "python",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "python-profilage": {
   "label": "Débogage et profilage (`pdb`, post-mortem, `cProfile`, `tracemalloc`)",
   "card": "python",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "python-slots-modele-donnees": {
   "label": "`__slots__`, `__format__`, `__bytes__` et disposition mémoire",
   "card": "python",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "python-architecture-modules": {
   "label": "Architecture de modules (imports paresseux, API publique explicite)",
   "card": "python",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "python-threads-processus": {
   "label": "Threads, processus, files et réservoirs de travailleurs (GIL, calcul contre entrées-sorties)",
   "card": "python",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "python-asyncio": {
   "label": "`asyncio` (boucle d'événements, tâches)",
   "card": "python",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "python-securite": {
   "label": "Sécurité (désérialisation, injection SQL, comparaison à temps constant, mots de passe, Bandit)",
   "card": "python",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "python-fastapi-pydantic": {
   "label": "Services web (WSGI, ASGI, intergiciels, FastAPI, Pydantic)",
   "card": "python",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "python-observabilite": {
   "label": "Observabilité (OpenTelemetry, contexte de requête)",
   "card": "python",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "python-cpython-internes": {
   "label": "Fonctionnement de CPython (bytecode, boucle d'évaluation)",
   "card": "python",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "python-sans-gil": {
   "label": "Exécution sans GIL (CPython 3.13 et suivants)",
   "card": "python",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "python-memoire-gc": {
   "label": "Comptage de références et ramasse-miettes",
   "card": "python",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "python-extensions-c": {
   "label": "Extensions en C (API C, ctypes, Cython)",
   "card": "python",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "python-machinerie-import": {
   "label": "Machinerie d'import (`importlib`, chercheurs, chargeurs)",
   "card": "python",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "python-ast-metaprogrammation": {
   "label": "Métaprogrammation par l'AST et `inspect`",
   "card": "python",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "python-typage-avance": {
   "label": "Typage avancé (génériques, `TypeVar`, `ParamSpec`, mypy)",
   "card": "python",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "python-strategies-livraison": {
   "label": "Stratégies de livraison (rebase, cherry-pick, versions, drapeaux de fonctionnalité, suivi des décisions)",
   "card": "python",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "reseau-modele-couches": {
   "label": "Modèle en couches (liaison, réseau, transport, application)",
   "card": "reseau",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "reseau-adresses-ip": {
   "label": "Adresses IPv4 et IPv6, masques et sous-réseaux",
   "card": "reseau",
   "tier": "beginner",
   "state": "découverte",
   "objective": "socle",
   "lastPractice": "12/11/2026",
   "section": "Réseau"
  },
  "reseau-tcp-udp-ports": {
   "label": "TCP, UDP et ports",
   "card": "reseau",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "reseau-dns-resolution": {
   "label": "Résolution de noms (DNS, `/etc/hosts`, `nsswitch.conf`)",
   "card": "reseau",
   "tier": "beginner",
   "state": "découverte",
   "objective": "socle",
   "lastPractice": "12/11/2026",
   "section": "Réseau"
  },
  "reseau-configuration-ip": {
   "label": "Configuration réseau (interface, adresse, passerelle, route ; persistante)",
   "card": "reseau",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "reseau-http-bases": {
   "label": "HTTP (requête, réponse, méthodes, codes d'état, en-têtes)",
   "card": "reseau",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "reseau-outils-diagnostic": {
   "label": "Outils de diagnostic (`ping`, `ip`, `ss`, `traceroute`, `dig`)",
   "card": "reseau",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "reseau-client-serveur": {
   "label": "Modèle client-serveur (service qui écoute, client qui se connecte)",
   "card": "reseau",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-ssh-serveur": {
   "label": "SSH (serveur et client, clés, transfert `scp` et `sftp`, redirection de port)",
   "card": "reseau",
   "tier": "intermediate",
   "state": "appliquée",
   "objective": "socle",
   "lastPractice": "13/11/2026",
   "section": "Réseau"
  },
  "reseau-pare-feu": {
   "label": "Pare-feu (nftables, iptables, firewalld : filtrage, politique par défaut)",
   "card": "reseau",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "reseau-nat-redirection": {
   "label": "Traduction d'adresses (NAT) et redirection de port",
   "card": "reseau",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "reseau-routage-statique": {
   "label": "Routage statique",
   "card": "reseau",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "reseau-synchronisation-heure": {
   "label": "Synchronisation de l'heure (NTP, chrony)",
   "card": "reseau",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "reseau-tls-certificats": {
   "label": "TLS et certificats (autorité, chaîne, `openssl`)",
   "card": "reseau",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "reseau-dhcp": {
   "label": "Attribution automatique d'adresse (DHCP)",
   "card": "reseau",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "reseau-serveur-web": {
   "label": "Serveur web (nginx ou Apache, hôtes virtuels)",
   "card": "reseau",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "reseau-sockets": {
   "label": "Programmation par sockets (`socket`, `bind`, `listen`, `accept`, `poll`, boutisme réseau)",
   "card": "reseau",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "reseau-capture-paquets": {
   "label": "Capture de paquets (`tcpdump`, Wireshark)",
   "card": "reseau",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "reseau-proxy-inverse": {
   "label": "Proxy inverse et équilibrage de charge",
   "card": "reseau",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "reseau-pont-agregation": {
   "label": "Pont et agrégation de liens (bridge, bonding)",
   "card": "reseau",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "reseau-partages-nfs-autofs": {
   "label": "Systèmes de fichiers distants et montage automatique (NFS, autofs, périphériques bloc réseau)",
   "card": "reseau",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "reseau-mta-courrier": {
   "label": "Courrier (agent de transfert, SMTP)",
   "card": "reseau",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "reseau-vpn-tunnels": {
   "label": "VPN et tunnels (WireGuard, tunnels SSH)",
   "card": "reseau",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "reseau-annuaire-ldap": {
   "label": "Comptes depuis un annuaire LDAP",
   "card": "reseau",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "reseau-http-securise": {
   "label": "HTTPS, HTTP/2, cookies et en-têtes de sécurité",
   "card": "reseau",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "reseau-vlan": {
   "label": "VLAN",
   "card": "reseau",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "reseau-espaces-noms": {
   "label": "Espaces de noms réseau (`veth`, `netns`)",
   "card": "reseau",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "reseau-congestion-tcp": {
   "label": "Contrôle de congestion TCP",
   "card": "reseau",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "reseau-ipv6-avance": {
   "label": "IPv6 avancé (autoconfiguration, découverte de voisins)",
   "card": "reseau",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "reseau-routage-dynamique": {
   "label": "Routage dynamique (BGP, OSPF)",
   "card": "reseau",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "reseau-performance-pile": {
   "label": "Performance de la pile réseau (réglages, déchargement matériel)",
   "card": "reseau",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "reseau-dns-internes": {
   "label": "DNS en profondeur (récursif, autorité, DNSSEC)",
   "card": "reseau",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "reseau-quic-http3": {
   "label": "QUIC et HTTP/3",
   "card": "reseau",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "reseau-ebpf-xdp": {
   "label": "Traitement de paquets par eBPF et XDP",
   "card": "reseau",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "reseau-attaques": {
   "label": "Attaques réseau (homme du milieu, usurpation ARP, inondation SYN)",
   "card": "reseau",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-outils-inspection": {
   "label": "Inspecter un binaire (`file`, `strings`, `readelf`, `ltrace`, `strace`)",
   "card": "securite-binaire",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-desassemblage-lecture": {
   "label": "Lire un désassemblage (`objdump`, fonctions, sauts, appels)",
   "card": "securite-binaire",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-debogueur-analyse": {
   "label": "Analyse dynamique au débogueur (`gdb`, WinDbg : points d'arrêt, mémoire, plantage)",
   "card": "securite-binaire",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-pile-appels-exploitation": {
   "label": "Pile d'un appel vue par l'attaquant (variables locales, cadre sauvegardé, adresse de retour)",
   "card": "securite-binaire",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-debordement-pile": {
   "label": "Débordement de tampon sur la pile",
   "card": "securite-binaire",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-memoire-shellcode-bases": {
   "label": "Mémoire d'exécution et principe du shellcode (code injecté exécuté par le processus)",
   "card": "securite-binaire",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-escalade-suid": {
   "label": "Escalade de privilèges par un programme SUID",
   "card": "securite-binaire",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-injection-commande": {
   "label": "Injection de commande (entrée non validée passée à un shell, `PATH` détourné)",
   "card": "securite-binaire",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-encodages-hachage": {
   "label": "Encodages, hachage et chiffrement faible (les reconnaître et les inverser)",
   "card": "securite-binaire",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-conditions-course": {
   "label": "Situation de compétition entre vérification et usage (TOCTOU)",
   "card": "securite-binaire",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-controle-flot": {
   "label": "Détourner le flot d'exécution (adresse de retour, fonction cachée)",
   "card": "securite-binaire",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-shellcode-ecriture": {
   "label": "Écrire un shellcode de zéro (appels système, octets interdits)",
   "card": "securite-binaire",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-format-string": {
   "label": "Chaîne de format (lecture et écriture arbitraires)",
   "card": "securite-binaire",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-debordement-entier": {
   "label": "Débordement et troncature d'entiers",
   "card": "securite-binaire",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-off-by-one": {
   "label": "Débordement d'un octet",
   "card": "securite-binaire",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-ret2libc": {
   "label": "Retour dans la libc",
   "card": "securite-binaire",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-rop-chaines": {
   "label": "Programmation orientée retour (gadgets, chaînes, décodeurs de charge)",
   "card": "securite-binaire",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-nx-dep": {
   "label": "Pile non exécutable (NX, DEP)",
   "card": "securite-binaire",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-canari": {
   "label": "Canari de pile et son contournement",
   "card": "securite-binaire",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-aslr-pie": {
   "label": "Adresses aléatoires (ASLR, PIE)",
   "card": "securite-binaire",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-plt-got": {
   "label": "PLT et GOT (résolution dynamique, réécriture de la GOT)",
   "card": "securite-binaire",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-scripts-offensifs": {
   "label": "Scripts d'exploitation (pwntools, Python)",
   "card": "securite-binaire",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-reverse-desassembleur": {
   "label": "Rétro-ingénierie au désassembleur (Ghidra, IDA, binaire sans symboles)",
   "card": "securite-binaire",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-recherche-bugs": {
   "label": "Trouver une faille en lisant un binaire",
   "card": "securite-binaire",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-fuite-adresse": {
   "label": "Fuite d'adresse et calcul des bases",
   "card": "securite-binaire",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-stack-pivot": {
   "label": "Déplacer la pile (stack pivot)",
   "card": "securite-binaire",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-tas-agencement": {
   "label": "Agencement du tas (blocs, listes libres de glibc)",
   "card": "securite-binaire",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-use-after-free": {
   "label": "Utilisation après libération",
   "card": "securite-binaire",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-tcache-fastbin": {
   "label": "Attaques du tcache et des fastbins",
   "card": "securite-binaire",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-exploitation-distance": {
   "label": "Exploiter un service distant, à l'aveugle",
   "card": "securite-binaire",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-ret2dlresolve": {
   "label": "Détourner le résolveur dynamique (ret2dlresolve)",
   "card": "securite-binaire",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-one-gadget-relro": {
   "label": "One-gadget et RELRO",
   "card": "securite-binaire",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-windows-execution-memoire": {
   "label": "Exécution et mémoire sous Windows (format PE, processus, modules)",
   "card": "securite-binaire",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-seh": {
   "label": "Débordement du gestionnaire d'exceptions de Windows (SEH)",
   "card": "securite-binaire",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-egghunter": {
   "label": "Charge trop grande pour la place : egghunter",
   "card": "securite-binaire",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-windows-dep-aslr": {
   "label": "Contourner DEP et ASLR sous Windows",
   "card": "securite-binaire",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-fuzzing": {
   "label": "Fuzzing, avec et sans code source",
   "card": "securite-binaire",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-environnements-restreints": {
   "label": "Sortir d'un environnement restreint (shell restreint, kiosque)",
   "card": "securite-binaire",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-house-of": {
   "label": "Techniques House-of (corruption des métadonnées du tas)",
   "card": "securite-binaire",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-fsop": {
   "label": "Détournement des structures `FILE` (FSOP)",
   "card": "securite-binaire",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-srop": {
   "label": "Retour par `sigreturn` (SROP)",
   "card": "securite-binaire",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-exploitation-noyau": {
   "label": "Escalade de privilèges par une faille du noyau",
   "card": "securite-binaire",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-protections-modernes": {
   "label": "Protections modernes du flot (CFI, pile fantôme, CET)",
   "card": "securite-binaire",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-execution-symbolique": {
   "label": "Analyse binaire automatisée (exécution symbolique)",
   "card": "securite-binaire",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-attaques-crypto": {
   "label": "Attaques de cryptographie appliquée (oracle de remplissage, réutilisation de flux)",
   "card": "securite-binaire",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-evasion-poste": {
   "label": "Contourner les contrôles d'un poste et s'y élever",
   "card": "securite-binaire",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-acces-reseau": {
   "label": "Obtenir un accès réseau et manipuler l'infrastructure (contrôle d'accès réseau, routage)",
   "card": "securite-binaire",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "secu-allocateurs-durcis": {
   "label": "Allocateurs durcis et leurs limites",
   "card": "securite-binaire",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "shell-commandes-base": {
   "label": "Fichiers en ligne de commande (`cd`, `ls`, `cp`, `mv`, `rm`, `mkdir`, `cat`)",
   "card": "shell",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "shell-commande-options": {
   "label": "Commande, options et arguments ; aide (`man`, `--help`)",
   "card": "shell",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-redirections-shell": {
   "label": "Redirections `<`, `>`, `>>`, `2>` (fichier de `>` vidé avant la commande)",
   "card": "shell",
   "tier": "beginner",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "12/11/2026",
   "section": "Shell"
  },
  "shell-tubes-filtres": {
   "label": "Tubes et filtres (`grep`, `sort`, `uniq`, `wc`, `head`, `cut`, `tr`, `tee`)",
   "card": "shell",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "shell-code-retour": {
   "label": "Code de retour, `&&`, `||`, `$?`",
   "card": "shell",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "shell-variables-guillemets": {
   "label": "Variables du shell et guillemets (simples, doubles)",
   "card": "shell",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "shell-jokers": {
   "label": "Motifs de noms de fichiers (`*`, `?`, `[...]`)",
   "card": "shell",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-script-shell": {
   "label": "Script exécutable (shebang, droit x, `./` contre `PATH`)",
   "card": "shell",
   "tier": "beginner",
   "state": "découverte",
   "objective": "socle",
   "lastPractice": "22/10/2026",
   "section": "Shell"
  },
  "linux-shell-test-substitution": {
   "label": "Test `[ ... ]` (commande `[`, espaces, guillemets)",
   "card": "shell",
   "tier": "intermediate",
   "state": "découverte",
   "objective": "socle",
   "lastPractice": "08/11/2026",
   "section": "Shell"
  },
  "linux-shell-case": {
   "label": "`case ... in` (motifs, `;;`, `esac`)",
   "card": "shell",
   "tier": "intermediate",
   "state": "découverte",
   "objective": "socle",
   "lastPractice": "08/11/2026",
   "section": "Shell"
  },
  "shell-boucles": {
   "label": "Boucles `for`, `while` et `read`",
   "card": "shell",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "shell-fonctions": {
   "label": "Fonctions (`$1`, `$@`, `local`, `return`)",
   "card": "shell",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "shell-substitution-commande": {
   "label": "Substitution de commande `$(...)` et arithmétique `$(( ))`",
   "card": "shell",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-shell-set-eu": {
   "label": "Options `set -e` et `set -u`",
   "card": "shell",
   "tier": "intermediate",
   "state": "découverte",
   "objective": "socle",
   "lastPractice": "08/11/2026",
   "section": "Shell"
  },
  "linux-sed-adresses": {
   "label": "`sed` : substitution et adresses par numéro ou par motif",
   "card": "shell",
   "tier": "intermediate",
   "state": "découverte",
   "objective": "socle",
   "lastPractice": "09/11/2026",
   "section": "Shell"
  },
  "shell-expressions-regulieres": {
   "label": "Expressions régulières (BRE et ERE, `grep -E`)",
   "card": "shell",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "shell-find-xargs": {
   "label": "`find` et `xargs`",
   "card": "shell",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "shell-awk": {
   "label": "`awk` (champs, motifs, actions)",
   "card": "shell",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "shell-controle-taches": {
   "label": "Contrôle des tâches (`&`, `jobs`, `fg`, `bg`, `nohup`)",
   "card": "shell",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "shell-environnement-alias": {
   "label": "Environnement du shell (alias, `~/.bashrc`, `/etc/profile`)",
   "card": "shell",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "shell-expansions-parametres": {
   "label": "Expansions de paramètres (`${v:-x}`, `${v#motif}`, `${#v}`)",
   "card": "shell",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "shell-tableaux-bash": {
   "label": "Tableaux de Bash (indexés et associatifs)",
   "card": "shell",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "shell-trap": {
   "label": "`trap` (nettoyage à la sortie, signaux)",
   "card": "shell",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "shell-here-doc-sous-shell": {
   "label": "Here-doc, sous-shell `( )` contre groupe `{ }`",
   "card": "shell",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "shell-getopts": {
   "label": "Lecture des options d'un script (`getopts`)",
   "card": "shell",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "shell-portabilite-posix": {
   "label": "POSIX sh contre Bash (bashismes, `dash`)",
   "card": "shell",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "shell-sed-avance": {
   "label": "`sed` avancé (espace de maintien, plusieurs lignes, `-i`)",
   "card": "shell",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "shell-decoupage-mots": {
   "label": "Découpage des mots et pièges de citation (`IFS`, `\"$@\"`)",
   "card": "shell",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "shell-ordre-expansions": {
   "label": "Ordre des expansions (accolades, tilde, paramètres, commande, découpage, jokers)",
   "card": "shell",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "shell-descripteurs-avances": {
   "label": "Descripteurs avancés (`exec 3>`, ordre de `2>&1`, `<( )`)",
   "card": "shell",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "shell-fifo-coproc": {
   "label": "FIFO nommés et `coproc`",
   "card": "shell",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "shell-cout-processus": {
   "label": "Coût des processus lancés (commandes internes contre externes)",
   "card": "shell",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "shell-debogage": {
   "label": "Débogage de scripts (`set -x`, `PS4`, `shellcheck`)",
   "card": "shell",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "shell-awk-programmes": {
   "label": "Programmes `awk` (tableaux associatifs, fonctions)",
   "card": "shell",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "shell-groupes-sessions": {
   "label": "Groupes de processus, sessions et terminal de contrôle",
   "card": "shell",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "shell-securite-scripts": {
   "label": "Sécurité des scripts (`eval`, entrées non fiables, `mktemp`)",
   "card": "shell",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-tables-cle-primaire": {
   "label": "Table, ligne, colonne, clé primaire ; lien avec un schéma entité-association",
   "card": "sql",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-select-from-where": {
   "label": "Lire des lignes (`SELECT`, `FROM`, `WHERE`)",
   "card": "sql",
   "tier": "beginner",
   "state": "transférée",
   "objective": "socle",
   "lastPractice": "12/11/2026",
   "section": "SQL"
  },
  "sql-order-by-top": {
   "label": "Trier et limiter le résultat (`ORDER BY`, `TOP`, `FETCH FIRST`)",
   "card": "sql",
   "tier": "beginner",
   "state": "transférée",
   "objective": "socle",
   "lastPractice": "13/11/2026",
   "section": "SQL"
  },
  "sql-filtres-courants": {
   "label": "Filtres courants (`LIKE`, `IN`, `BETWEEN`, `DISTINCT`, alias)",
   "card": "sql",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-valeurs-absentes": {
   "label": "Valeurs absentes (`NULL`, `IS NULL`, fonctions de remplacement)",
   "card": "sql",
   "tier": "beginner",
   "state": "transférée",
   "objective": "socle",
   "lastPractice": "20/11/2026",
   "section": "SQL"
  },
  "sql-types-valeurs": {
   "label": "Types de colonne et valeurs cohérentes",
   "card": "sql",
   "tier": "beginner",
   "state": "appliquée",
   "objective": "socle",
   "lastPractice": "13/11/2026",
   "section": "SQL"
  },
  "sql-agregation-group-by": {
   "label": "Agréger et regrouper (`GROUP BY`)",
   "card": "sql",
   "tier": "beginner",
   "state": "transférée",
   "objective": "socle",
   "lastPractice": "17/11/2026",
   "section": "SQL"
  },
  "sql-insert-update-delete": {
   "label": "Écrire (`INSERT`, `UPDATE`, `DELETE`)",
   "card": "sql",
   "tier": "beginner",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-jointures": {
   "label": "Jointures (interne, externes, croisée, auto-jointure)",
   "card": "sql",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-having": {
   "label": "Filtrer les groupes (`HAVING`)",
   "card": "sql",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-sous-requetes": {
   "label": "Sous-requêtes (corrélées ou non, `EXISTS`)",
   "card": "sql",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-contraintes": {
   "label": "Contraintes (clé étrangère, `UNIQUE`, `CHECK`)",
   "card": "sql",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-normalisation": {
   "label": "Normalisation (première à troisième forme normale)",
   "card": "sql",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-transactions-acid": {
   "label": "Transactions et ACID (`COMMIT`, `ROLLBACK`, `SAVEPOINT`)",
   "card": "sql",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-index": {
   "label": "Index (principe, coût en écriture)",
   "card": "sql",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-vues": {
   "label": "Vues",
   "card": "sql",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-case-fonctions": {
   "label": "`CASE`, fonctions de texte, de nombre et de date, conversions de type",
   "card": "sql",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-ensembles": {
   "label": "Opérations d'ensemble (`UNION`, `INTERSECT`, `EXCEPT`)",
   "card": "sql",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-requetes-parametrees": {
   "label": "Requêtes paramétrées contre injection SQL",
   "card": "sql",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-definition-tables": {
   "label": "Définir les tables (`CREATE`, `ALTER`, `DROP`, `TRUNCATE`)",
   "card": "sql",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-privileges": {
   "label": "Droits d'accès (`GRANT`, `REVOKE`, rôles)",
   "card": "sql",
   "tier": "intermediate",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-fenetrage": {
   "label": "Fonctions de fenêtrage (`OVER`, `PARTITION BY`)",
   "card": "sql",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-cte-recursives": {
   "label": "Expressions de table communes, récursives comprises",
   "card": "sql",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-plans-execution": {
   "label": "Plans d'exécution",
   "card": "sql",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-niveaux-isolation": {
   "label": "Niveaux d'isolation",
   "card": "sql",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-procedures-declencheurs": {
   "label": "Procédures stockées, fonctions et déclencheurs",
   "card": "sql",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-modelisation": {
   "label": "Modélisation (cardinalités, dénormalisation volontaire)",
   "card": "sql",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-optimisation-requetes": {
   "label": "Optimisation des requêtes (sargabilité, index couvrants)",
   "card": "sql",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-verrous-interblocages": {
   "label": "Verrous et interblocages",
   "card": "sql",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-sequences-synonymes": {
   "label": "Séquences et synonymes",
   "card": "sql",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-dictionnaire-donnees": {
   "label": "Dictionnaire de données (vues du catalogue)",
   "card": "sql",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-fuseaux-horaires": {
   "label": "Dates et fuseaux horaires",
   "card": "sql",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-merge-insertion-multiple": {
   "label": "`MERGE` et insertion dans plusieurs tables",
   "card": "sql",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-flashback": {
   "label": "Requêtes sur un état passé (`FLASHBACK`, tables temporelles)",
   "card": "sql",
   "tier": "advanced",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-stockage-interne": {
   "label": "Stockage interne (pages, arbres B, tas)",
   "card": "sql",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-optimiseur-statistiques": {
   "label": "Optimiseur et statistiques (estimation de cardinalité)",
   "card": "sql",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-mvcc": {
   "label": "Contrôle de concurrence multiversion",
   "card": "sql",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-journal-recuperation": {
   "label": "Journal d'écriture anticipée et récupération",
   "card": "sql",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-partitionnement-replication": {
   "label": "Partitionnement et réplication",
   "card": "sql",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-algebre-relationnelle": {
   "label": "Algèbre relationnelle",
   "card": "sql",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-analytique-colonnes": {
   "label": "Bases analytiques et stockage en colonnes",
   "card": "sql",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "sql-anomalies-concurrence": {
   "label": "Anomalies de concurrence (lecture fantôme, write skew)",
   "card": "sql",
   "tier": "transcended",
   "state": "non rencontrée",
   "objective": null,
   "lastPractice": null,
   "section": null
  },
  "linux-compilation-croisee": {
   "label": "Compilation croisée : pourquoi la chaîne de l'hôte ne suffit pas (programmes reliés à la libc de l'hôte, absente de la distro)",
   "state": "appliquée",
   "objective": "socle",
   "lastPractice": "14/11/2026",
   "section": "Linux (système)",
   "card": null,
   "tier": null
  },
  "linux-build-host": {
   "label": "Machines d'une compilation croisée (`--build` : où l'on compile, `--host` : où le résultat tourne, `config.guess` donne la valeur par défaut ; chapitre 6 : build = VM Ubuntu, host = distro `lfs`)",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "19/11/2026",
   "section": "Linux (système)",
   "card": null,
   "tier": null
  },
  "linux-destdir": {
   "label": "Installation dans une racine alternative (`make DESTDIR=$LFS install` : tout chemin d'installation est préfixé, `/usr/lib` devient `$LFS/usr/lib` ; `--prefix=/usr` est le chemin vu dans la distro)",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "19/11/2026",
   "section": "Linux (système)",
   "card": null,
   "tier": null
  },
  "linux-alignement-partition": {
   "label": "Alignement des partitions (début multiple de 2048 secteurs, superbloc relatif au début)",
   "state": "appliquée",
   "objective": "socle",
   "lastPractice": "09/11/2026",
   "section": "Linux (système)",
   "card": null,
   "tier": null
  },
  "linux-qcow2-snapshot": {
   "label": "Disque virtuel qcow2 et snapshot (disque seul contre disque + RAM)",
   "state": "transférée",
   "objective": "socle",
   "lastPractice": "08/11/2026",
   "section": "Linux (système)",
   "card": null,
   "tier": null
  },
  "linux-boot-separee": {
   "label": "Partition `/boot` séparée (contenu, chargeur à mini-pilotes de lecture, taille fixe)",
   "state": "en cours",
   "objective": "projet (ft_linux)",
   "lastPractice": "12/11/2026",
   "section": "Linux (système)",
   "card": null,
   "tier": null
  },
  "linux-hierarchie-liens-usr": {
   "label": "Pourquoi `bin`, `lib`, `sbin` sont des liens vers `usr/` (convention des distributions modernes, visible sur l'Ubuntu de l'hôte)",
   "state": "en cours",
   "objective": "projet (ft_linux)",
   "lastPractice": "09/11/2026",
   "section": "Linux (système)",
   "card": null,
   "tier": null
  },
  "linux-lib64-interpreteur": {
   "label": "Pourquoi `lib64` : le chemin du chargeur dynamique est écrit dans chaque programme x86_64",
   "state": "en cours",
   "objective": "projet (ft_linux)",
   "lastPractice": "07/11/2026",
   "section": "Linux (système)",
   "card": null,
   "tier": null
  },
  "linux-hierarchie-limitee-tools": {
   "label": "Hiérarchie limitée sous `$LFS` et dossier `tools` (pourquoi maintenant : emplacement final des outils temporaires, réécrits au chapitre 8)",
   "state": "appliquée",
   "objective": "projet (ft_linux)",
   "lastPractice": "02/11/2026",
   "section": "Linux (système)",
   "card": null,
   "tier": null
  },
  "linux-utilisateur-non-privilegie": {
   "label": "Construire avec un utilisateur ordinaire (`lfs`) : protège l'hôte d'une erreur de chemin, `chown` des seuls dossiers utiles, moindre privilège",
   "state": "appliquée",
   "objective": "projet (ft_linux)",
   "lastPractice": "09/11/2026",
   "section": "Linux (système)",
   "card": null,
   "tier": null
  },
  "linux-environnement-construction": {
   "label": "Environnement de construction du shell de `lfs` (`exec env -i`, `.bash_profile`, `.bashrc`, `export`, fichier de l'hôte écarté, `MAKEFLAGS`)",
   "state": "transférée",
   "objective": "projet (ft_linux)",
   "lastPractice": "03/11/2026",
   "section": "Linux (système)",
   "card": null,
   "tier": null
  },
  "linux-chaine-croisee-binutils": {
   "label": "Chaîne d'outils croisée et rôle de Binutils passe 1 (outils qui tournent sur l'hôte et produisent pour la distro, préfixe de la machine cible, `--prefix`, `--target`, `--with-sysroot`, Binutils en premier, tests inutiles aux chapitres 5 et 6 ; ordre de construction du chapitre 5 : Binutils, GCC passe 1, en-têtes de l'API Linux, Glibc, Libstdc++)",
   "state": "comprise",
   "objective": "projet (ft_linux)",
   "lastPractice": "07/11/2026",
   "section": "Linux (système)",
   "card": null,
   "tier": null
  },
  "linux-prerequis-hote": {
   "label": "Prérequis de l'hôte de construction (script de vérification du livre, paquets installés avec `apt`, `sh` relié à `bash`, nom de programme contre nom de paquet)",
   "state": "découverte",
   "objective": "projet (ft_linux)",
   "lastPractice": "01/11/2026",
   "section": "Linux (système)",
   "card": null,
   "tier": null
  },
  "linux-mesure-sbu-parallelisme": {
   "label": "Mesurer une construction : SBU sur un cœur, `time { ... }`, `make -j`, gain inférieur au nombre de cœurs (étapes en série)",
   "state": "découverte",
   "objective": "hors objectif",
   "lastPractice": "01/11/2026",
   "section": "Linux (système)",
   "card": null,
   "tier": null
  },
  "linux-gcc-passe1": {
   "label": "GCC passe 1 : compilateur croisé réduit (sans libc cible : `--disable-shared`, `--with-newlib`, `--without-headers`), qui construit la Glibc ; portée : `stdio.h` introuvable, `-c` seul réussit, édition de liens en échec sans fichiers de démarrage ni `-lc` ; `gcc` de l'hôte contre `$LFS_TGT-gcc`",
   "state": "en cours",
   "objective": "projet (ft_linux)",
   "lastPractice": "07/11/2026",
   "section": "Linux (système)",
   "card": null,
   "tier": null
  },
  "linux-api-headers": {
   "label": "En-têtes de l'API Linux (fichiers `.h` tirés des sources du noyau qui décrivent à la Glibc ce que le noyau accepte ; sans eux elle ne peut pas être compilée ; installés dans `$LFS/usr/include`)",
   "state": "découverte",
   "objective": "projet (ft_linux)",
   "lastPractice": "07/11/2026",
   "section": "Linux (système)",
   "card": null,
   "tier": null
  },
  "linux-glibc-contenu": {
   "label": "Glibc : ce qu'elle fournit (fichiers de démarrage `Scrt1.o`, `crti.o`, `crtn.o`, `libc`, chargeur), compilée par la passe 1, installée avec `DESTDIR`, vérifiée avec un programme vide compilé en mode bavard et `readelf -l`",
   "state": "découverte",
   "objective": "projet (ft_linux)",
   "lastPractice": "07/11/2026",
   "section": "Linux (système)",
   "card": null,
   "tier": null
  },
  "linux-libstdcpp": {
   "label": "Libstdc++ : bibliothèque standard du C++, nécessaire pour compiler du C++, installée après la Glibc dont elle dépend",
   "state": "découverte",
   "objective": "projet (ft_linux)",
   "lastPractice": "07/11/2026",
   "section": "Linux (système)",
   "card": null,
   "tier": null
  },
  "linux-tic-natif": {
   "label": "`tic` natif de Ncurses (`make install` s'exécute sur la VM Ubuntu et lance `tic` ; celui du Ncurses croisé est conçu pour la distro ; le livre construit d'abord un `tic` avec les outils de l'hôte, installé dans `$LFS/tools/bin`, trouvé par `PATH`)",
   "state": "en cours",
   "objective": "hors objectif",
   "lastPractice": "08/11/2026",
   "section": "Linux (système)",
   "card": null,
   "tier": null
  },
  "linux-fichiers-la-libtool": {
   "label": "Fichiers `.la` de libtool (petit fichier texte décrivant une bibliothèque, `libdir` en dur ; inutiles sur Linux ; nuisibles en compilation croisée, cause exacte non sourcée ; supprimés après File, Xz, Binutils passe 2, puis tous au nettoyage 7.13)",
   "state": "découverte",
   "objective": "projet (ft_linux)",
   "lastPractice": "09/11/2026",
   "section": "Linux (système)",
   "card": null,
   "tier": null
  },
  "linux-fichiers-essentiels": {
   "label": "Fichiers essentiels du chroot (7.6) : `/etc/passwd` (champs), `/etc/group`, `/etc/hosts`, lien `/etc/mtab`, here-document `<< EOF` avec ou sans guillemets, `>>` qui ajoute, `exec bash --login`, journaux `btmp`, `lastlog`, `faillog`, `wtmp`",
   "state": "découverte",
   "objective": "projet (ft_linux)",
   "lastPractice": "09/11/2026",
   "section": "Linux (système)",
   "card": null,
   "tier": null
  },
  "linux-suite-tests-resultats": {
   "label": "Lire les résultats d'une suite de tests (PASS, FAIL, XFAIL, XPASS, UNSUPPORTED ; seuls les FAIL font échouer la commande ; liste dans `tests.sum` et `<test>.out` ; délai par défaut de 20 s multiplié par `TIMEOUTFACTOR` ; relancer un test seul)",
   "state": "découverte",
   "objective": "projet (ft_linux)",
   "lastPractice": "09/11/2026",
   "section": "Linux (système)",
   "card": null,
   "tier": null
  },
  "linux-tests-chronometres-parallelisme": {
   "label": "Tests chronométrés et parallélisme (un test qui dépend du temps échoue par dépassement de délai quand la machine est chargée par `make -j6` ; relancé en `-j1` il réussit ; lire le journal pour trouver le vrai test en échec, hors sous-tests voulus)",
   "state": "découverte",
   "objective": "projet (ft_linux)",
   "lastPractice": "09/11/2026",
   "section": "Linux (système)",
   "card": null,
   "tier": null
  },
  "linux-comparer-journaux-reference": {
   "label": "Comparer les résultats d'une suite de tests à des journaux de référence (`FAIL` : test lancé et échoué, `ERROR` : test que le banc n'a pas su lire ou lancer ; comparer les listes de tests, pas les totaux ; écart de cause matérielle plausible, non vérifié)",
   "state": "découverte",
   "objective": "projet (ft_linux)",
   "lastPractice": "09/11/2026",
   "section": "Linux (système)",
   "card": null,
   "tier": null
  },
  "linux-sysv-init": {
   "label": "System V : `init` (PID 1) lit `/etc/inittab`, niveaux d'exécution (0, 1, 3, 5, 6), scripts de `/etc/rc.d/init.d`, liens `S10…` et `K80…` dans `rcN.d`",
   "state": "en cours",
   "objective": "socle (carte Linux (système), fusionnée avec systemd : exigée par LPIC-1)",
   "lastPractice": "21/11/2026",
   "section": "Linux (système)",
   "card": null,
   "tier": null
  },
  "linux-telechargement-sans-client": {
   "label": "Télécharger sans `curl` ni `wget` : Python `urllib` (HTTPS non vérifié sans certificats), somme MD5",
   "state": "en cours",
   "objective": "projet (ft_linux)",
   "lastPractice": "12/11/2026",
   "section": "Linux (système)",
   "card": null,
   "tier": null
  },
  "linux-qemu-captures": {
   "label": "Captures QEMU : `savevm`/`loadvm`/`delvm` avec mémoire contre `qemu-img snapshot -c/-d/-a` disque seul ; `cont` après un `loadvm` échoué ; un fichier qcow2 ne rétrécit pas",
   "state": "découverte",
   "objective": "socle",
   "lastPractice": "10/11/2026",
   "section": "Linux (système)",
   "card": null,
   "tier": null
  },
  "linux-demarche-echec-compilation": {
   "label": "Démarche en cas d'échec de compilation (lire la première erreur : fichier et ligne ; comparer avec une commande qui a déjà fonctionné ; repartir d'une archive propre ; cas vécus : `c99` introuvable, puis `falseUL` undeclared)",
   "state": "en cours",
   "objective": "projet (ft_linux)",
   "lastPractice": "12/11/2026",
   "section": "Linux (système)",
   "card": null,
   "tier": null
  },
  "linux-noyau-secours": {
   "label": "Noyau de secours (seconde entrée du menu de GRUB, copie de celle qui marche sous un titre différent ; protège d'un noyau qui ne démarre pas ; inutile si l'ancien fichier est écrasé ou si GRUB ou `/boot` sont abîmés)",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "18/11/2026",
   "section": "Linux (système)",
   "card": null,
   "tier": null
  },
  "linux-qemu-port-serie": {
   "label": "Port série d'une VM (`-serial file:NOM`, fichier vidé à chaque lancement, `stdio` en direct, `console=ttyS0` côté noyau)",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "20/11/2026",
   "section": "Linux (système)",
   "card": null,
   "tier": null
  },
  "linux-certificats-https": {
   "label": "Certificats et HTTPS (autorités de certification, `make-ca`, `p11-kit`, cURL puis Git en https)",
   "state": "découverte",
   "objective": "socle",
   "lastPractice": "12/11/2026",
   "section": "Linux (système)",
   "card": null,
   "tier": null
  },
  "linux-sudo-wheel": {
   "label": "`sudo` (lance une commande en root, groupe `wheel`, fichiers de `sudoers.d` en `0440`, `visudo -c`)",
   "state": "découverte",
   "objective": "socle",
   "lastPractice": "12/11/2026",
   "section": "Linux (système)",
   "card": null,
   "tier": null
  },
  "linux-tty-terminaux": {
   "label": "Terminaux (`tty` : *teletype*, `/dev/tty0` console de l'écran et du clavier, `/dev/ttyS0` premier port série, `/dev/pts/N` terminal d'une fenêtre ; port série : bits envoyés l'un derrière l'autre sur un fil, simulé par QEMU, trame asynchrone (ligne au repos à `1`, start à `0` seul front garanti, 8 bits lus au milieu de chaque temps à la cadence convenue, stop à `1` vérifié) ; `console=ttyS0` : le noyau écrit ses messages sur ce port)",
   "state": "découverte",
   "objective": "socle",
   "lastPractice": "20/11/2026",
   "section": "Linux (système)",
   "card": null,
   "tier": null
  },
  "linux-bus-usb-hote": {
   "label": "Bus et USB (un bus est un chemin partagé avec règles et adresses, pas un fil ; `lsusb` ; l'hôte commande, le périphérique répond ; paquets et confirmations, comme sur internet (analogie trouvée par Louis) ; USB 2.0 une paire de fils à tour de rôle, 3.0 deux paires de plus ; paire en miroir contre le bruit ; une clé est lue par le noyau et son pilote de système de fichiers)",
   "state": "découverte",
   "objective": "hors objectif",
   "lastPractice": "20/11/2026",
   "section": "Linux (système)",
   "card": null,
   "tier": null
  },
  "linux-32-64-bits": {
   "label": "32 ou 64 bits (taille des nombres que le noyau manipule, plafond d'adressage de 4 Gio en 32 bits, `uname -m`, `getconf LONG_BIT`, `file`)",
   "state": "découverte",
   "objective": "projet (ft_linux)",
   "lastPractice": "12/11/2026",
   "section": "Noyau et assembleur",
   "card": null,
   "tier": null
  },
  "linux-arbre-noyau-stable": {
   "label": "Arbre de Linus contre version stable (l'arbre de Linus, `torvalds/linux`, reçoit le développement et les versions candidates `-rc` ; une stable est une version finale seulement corrigée, dans un autre dépôt `linux-X.Y.y` ; risque de ne pas démarrer, d'où une entrée de secours)",
   "state": "comprise",
   "objective": "socle",
   "lastPractice": "21/11/2026",
   "section": "Noyau et assembleur",
   "card": null,
   "tier": null
  },
  "linux-localversion-auto": {
   "label": "`CONFIG_LOCALVERSION_AUTO` (suffixe ajouté à la version : nombre de commits depuis la dernière étiquette, puis `-g` et 12 caractères du commit, lus dans le dépôt git à la compilation par `scripts/setlocalversion` ; `olddefconfig` complète seulement le `.config` ; `6.16.1-[masqué]` de `ft_linux` sans suffixe : déduit sans dépôt git, à confirmer)",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "19/11/2026",
   "section": "Noyau et assembleur",
   "card": null,
   "tier": null
  },
  "linux-bzimage-vmlinux": {
   "label": "`bzImage` contre `vmlinux` (deux formes du même noyau : `vmlinux` brut, ELF avec symboles, pour déboguer ; `bzImage` compressé avec le code de démarrage x86, chargé par GRUB ; copie dans `/boot` sous un nom libre avec `cp`)",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "20/11/2026",
   "section": "Noyau et assembleur",
   "card": null,
   "tier": null
  },
  "linux-lien-sh-bash": {
   "label": "Lien `sh` vers Bash dans `$LFS` (`#!/bin/sh` cherche `/bin/sh`, absent de la distro vide ; lien relatif : `bash` est lu depuis `$LFS/bin`, qui mène à `usr/bin`)",
   "state": "découverte",
   "objective": "hors objectif",
   "lastPractice": "08/11/2026",
   "section": "Shell",
   "card": null,
   "tier": null
  },
  "linux-shell-pushd-popd": {
   "label": "`pushd` et `popd` (pile de dossiers de Bash : `pushd D` mémorise le dossier courant et y entre, `popd` revient au dernier mémorisé ; erreur si le dossier est absent ou la pile vide ; absents de `sh`/dash)",
   "state": "découverte",
   "objective": "hors objectif",
   "lastPractice": "09/11/2026",
   "section": "Shell",
   "card": null,
   "tier": null
  },
  "linux-fichiers-caches": {
   "label": "Fichiers cachés (nom commençant par un point, fichier ordinaire dont seul l'affichage est omis : `ls -a`, `ls -A` sans `.` ni `..`, désigné par son nom ; le joker `*` les saute, `.*` les désigne ; pas une protection)",
   "state": "appliquée",
   "objective": "socle",
   "lastPractice": "21/11/2026",
   "section": "Shell",
   "card": null,
   "tier": null
  },
  "linux-compilateur-variable-cc": {
   "label": "Compilateur et variable `CC` (`cc` nom générique, `gcc` et `clang` deux compilateurs ; `CC=gcc ./configure` fixe la variable pour une commande ; sans elle `configure` de `bc` prend `c99`, absent de la VM)",
   "state": "en cours",
   "objective": "projet (ft_linux)",
   "lastPractice": "12/11/2026",
   "section": "C",
   "card": null,
   "tier": null
  },
  "algorithmique-sat-au-plus-un": {
   "label": "Interdire une combinaison par une clause (« au plus un »)",
   "state": "en cours",
   "objective": "projet (rush01)",
   "lastPractice": "27/10/2026",
   "section": "Algorithmique",
   "card": null,
   "tier": null
  },
  "algorithmique-encodage-sat": {
   "label": "Encoder un problème en SAT (brique 1 du rush01)",
   "state": "découverte",
   "objective": "projet (rush01)",
   "lastPractice": "15/10/2026",
   "section": "Algorithmique",
   "card": null,
   "tier": null
  },
  "sql-variable-de-table": {
   "label": "Variable de table (`DECLARE @t TABLE`, vit le temps d'une exécution, `@` dans `FROM`)",
   "state": "découverte",
   "objective": "hors objectif",
   "lastPractice": "29/10/2026",
   "section": "SQL",
   "card": null,
   "tier": null
  },
  "docker-compose-v1-v2": {
   "label": "`docker-compose` (v1, programme à part) contre `docker compose` (v2, plugin de `docker`), installé par `docker-compose-v2`",
   "state": "découverte",
   "objective": "hors objectif",
   "lastPractice": "02/11/2026",
   "section": "Docker",
   "card": null,
   "tier": null
  },
  "docker-monit-configuration": {
   "label": "Configuration de Monit (`set daemon`, `set httpd` + `allow`, `check host … with address`, `if failed port … then alert` ; Monit lit son propre langage, n'exécute pas de shell et ne remplace aucune variable d'environnement ; `-I` premier plan, `-c` fichier)",
   "state": "découverte",
   "objective": "projet (inception)",
   "lastPractice": "08/11/2026",
   "section": "Docker",
   "card": null,
   "tier": null
  },
  "docker-modele-envsubst": {
   "label": "Modèle de configuration rempli au démarrage (`envsubst` avec liste de variables entre quotes, fichier écrit dans `conf.d`, `exec` en dernier, `HTTP_HOST` sans le port avec `$host`)",
   "state": "en cours",
   "objective": "projet (inception)",
   "lastPractice": "02/11/2026",
   "section": "Docker",
   "card": null,
   "tier": null
  },
  "drupal-multisite": {
   "label": "Multisite de Drupal, site web en PHP (un code, plusieurs sites et bases)",
   "state": "découverte",
   "objective": "socle",
   "lastPractice": "12/10/2026",
   "section": "PHP",
   "card": null,
   "tier": null
  },
  "drupal-module": {
   "label": "Module de Drupal (extension qui ajoute une fonctionnalité)",
   "state": "découverte",
   "objective": "socle",
   "lastPractice": "12/10/2026",
   "section": "PHP",
   "card": null,
   "tier": null
  },
  "drupal-drush": {
   "label": "Drush (ligne de commande de Drupal)",
   "state": "découverte",
   "objective": "socle",
   "lastPractice": "12/10/2026",
   "section": "PHP",
   "card": null,
   "tier": null
  },
  "principes-cycle-jusqu-a-arret": {
   "label": "Répéter un cycle jusqu'à une condition d'arrêt (boucle principale, récursion)",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "21/11/2026",
   "section": "Principes",
   "card": null,
   "tier": null
  },
  "principes-ordre-non-garanti": {
   "label": "Un ordre n'existe pas tant qu'on ne l'a pas demandé ou construit explicitement (compter sur l'ordre d'arrivée est une hypothèse non garantie)",
   "state": "découverte",
   "objective": "socle",
   "lastPractice": "29/10/2026",
   "section": "Principes",
   "card": null,
   "tier": null
  },
  "principes-verification-integrite": {
   "label": "Vérifier l'intégrité d'un contenu par une empreinte comparée à une référence de confiance",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "16/11/2026",
   "section": "Principes",
   "card": null,
   "tier": null
  },
  "principes-moindre-privilege": {
   "label": "Moindre privilège (donner à un acteur seulement les droits dont sa tâche a besoin, ni plus ni moins)",
   "state": "en cours",
   "objective": "socle",
   "lastPractice": "31/10/2026",
   "section": "Principes",
   "card": null,
   "tier": null
  },
  "principes-isolation-environnement": {
   "label": "Isoler pour rendre le résultat indépendant du contexte (partir d'un état vide, n'y mettre que ce qu'on déclare : `env -i`, conteneur, `venv`)",
   "state": "découverte",
   "objective": "socle",
   "lastPractice": "31/10/2026",
   "section": "Principes",
   "card": null,
   "tier": null
  },
  "principes-surface-exposition": {
   "label": "Réduire la surface d'exposition (ne laisser joignable que le strict nécessaire, le reste derrière un réseau fermé)",
   "state": "découverte",
   "objective": "socle",
   "lastPractice": "02/11/2026",
   "section": "Principes",
   "card": null,
   "tier": null
  },
  "principes-separer-etat-processus": {
   "label": "Séparer l'état des processus (le programme est jetable, les données ont un stockage durable à part)",
   "state": "découverte",
   "objective": "socle",
   "lastPractice": "02/11/2026",
   "section": "Principes",
   "card": null,
   "tier": null
  },
  "principes-idempotence": {
   "label": "Idempotence (relancer une opération donne le même résultat final qu'une seule exécution)",
   "state": "découverte",
   "objective": "socle",
   "lastPractice": "02/11/2026",
   "section": "Principes",
   "card": null,
   "tier": null
  },
  "principes-outil-construction-sur-build": {
   "label": "Un outil lancé pendant la construction tourne sur la machine qui construit (`build`), pas sur celle de destination (`host`) : un programme compilé pour le `host` n'y est pas fait pour tourner, d'où une version native construite d'abord (exemple : `tic` de Ncurses)",
   "state": "découverte",
   "objective": "socle",
   "lastPractice": "09/11/2026",
   "section": "Principes",
   "card": null,
   "tier": null
  }
 },
 "relations": [
  {
   "source": "algorithmique-sat-clause-litteral",
   "target": "algorithmique-sat-au-plus-un",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "15/10/2026",
   "limit": null,
   "proof": null,
   "line": 2
  },
  {
   "source": "algorithmique-lois-de-morgan",
   "target": "algorithmique-sat-au-plus-un",
   "kind": "prerequis",
   "status": "demonstrated",
   "date": "15/10/2026",
   "limit": null,
   "proof": "S2/algorithmique-sat-au-plus-un/M2",
   "line": 3
  },
  {
   "source": "algorithmique-sat-au-plus-un",
   "target": "algorithmique-encodage-sat",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "15/10/2026",
   "limit": null,
   "proof": null,
   "line": 4
  },
  {
   "source": "algorithmique-sat-clause-litteral",
   "target": "algorithmique-encodage-sat",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "15/10/2026",
   "limit": null,
   "proof": null,
   "line": 5
  },
  {
   "source": "linux-partition",
   "target": "linux-alignement-partition",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "23/10/2026",
   "limit": null,
   "proof": null,
   "line": 6
  },
  {
   "source": "cpp-compilation-edition-liens",
   "target": "cpp-boucle-de-jeu",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "25/10/2026",
   "limit": null,
   "proof": null,
   "line": 7
  },
  {
   "source": "cpp-boucle-de-jeu",
   "target": "cpp-double-tampon",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "25/10/2026",
   "limit": null,
   "proof": null,
   "line": 8
  },
  {
   "source": "cpp-boucle-de-jeu",
   "target": "cpp-vitesse-deltatime-diagonale",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "25/10/2026",
   "limit": null,
   "proof": null,
   "line": 9
  },
  {
   "source": "cpp-boucle-de-jeu",
   "target": "principes-cycle-jusqu-a-arret",
   "kind": "instance_de",
   "status": "recognized",
   "date": "28/10/2026",
   "limit": "la récursion d'un solveur ne dépend que de son état; la boucle de jeu dépend aussi des entrées et du temps",
   "proof": "S12/cpp-boucle-de-jeu/principe",
   "line": 10
  },
  {
   "source": "cpp-exceptions-try-catch",
   "target": "cpp-conversion-stricte-stoi",
   "kind": "complementaire",
   "status": "theoretical",
   "date": "28/10/2026",
   "limit": null,
   "proof": null,
   "line": 11
  },
  {
   "source": "linux-demarrage",
   "target": "linux-boot-separee",
   "kind": "complementaire",
   "status": "theoretical",
   "date": "28/10/2026",
   "limit": null,
   "proof": null,
   "line": 12
  },
  {
   "source": "linux-partition",
   "target": "linux-montage-ordre-visibilite",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "28/10/2026",
   "limit": null,
   "proof": null,
   "line": 13
  },
  {
   "source": "linux-materiel-composants",
   "target": "linux-montage-ordre-visibilite",
   "kind": "transfert",
   "status": "recognized",
   "date": "28/10/2026",
   "limit": "la RAM garde l'état de montage seulement tant que la VM tourne; un snapshot avec RAM le garde",
   "proof": "S13/linux-montage-ordre-visibilite/Q5",
   "line": 14
  },
  {
   "source": "linux-somme-de-controle",
   "target": "principes-verification-integrite",
   "kind": "instance_de",
   "status": "recognized",
   "date": "28/10/2026",
   "limit": "l'ISO d'Ubuntu se vérifie avec une empreinte comme les archives; la référence doit venir d'ailleurs que du fichier",
   "proof": "S13/linux-somme-de-controle/M1",
   "line": 15
  },
  {
   "source": "linux-hierarchie-limitee-tools",
   "target": "linux-compilation-croisee",
   "kind": "complementaire",
   "status": "theoretical",
   "date": "28/10/2026",
   "limit": null,
   "proof": null,
   "line": 16
  },
  {
   "source": "linux-variable-environnement",
   "target": "linux-hierarchie-limitee-tools",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "28/10/2026",
   "limit": null,
   "proof": null,
   "line": 17
  },
  {
   "source": "sql-select-from-where",
   "target": "sql-order-by-top",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "29/10/2026",
   "limit": null,
   "proof": null,
   "line": 18
  },
  {
   "source": "sql-order-by-top",
   "target": "principes-ordre-non-garanti",
   "kind": "instance_de",
   "status": "theoretical",
   "date": "29/10/2026",
   "limit": "SQL: on demande l ordre et le serveur choisit comment; push_swap: Louis construit lui-même l algorithme et son coût compte",
   "proof": null,
   "line": 19
  },
  {
   "source": "sql-select-from-where",
   "target": "sql-agregation-group-by",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "29/10/2026",
   "limit": null,
   "proof": null,
   "line": 20
  },
  {
   "source": "sql-order-by-top",
   "target": "sql-agregation-group-by",
   "kind": "complementaire",
   "status": "theoretical",
   "date": "29/10/2026",
   "limit": "ORDER BY trie le résultat du calcul après le regroupement; GROUP BY ne trie pas",
   "proof": "S15/sql-agregation-group-by/M2",
   "line": 21
  },
  {
   "source": "sql-agregation-group-by",
   "target": "principes-ordre-non-garanti",
   "kind": "instance_de",
   "status": "theoretical",
   "date": "29/10/2026",
   "limit": "GROUP BY ne règle aucun ordre: l ordre vu est incident",
   "proof": "S15/sql-agregation-group-by/M2",
   "line": 22
  },
  {
   "source": "sql-types-valeurs",
   "target": "sql-valeurs-absentes",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "29/10/2026",
   "limit": null,
   "proof": null,
   "line": 23
  },
  {
   "source": "sql-valeurs-absentes",
   "target": "sql-agregation-group-by",
   "kind": "complementaire",
   "status": "theoretical",
   "date": "29/10/2026",
   "limit": "COUNT(colonne) ignore les valeurs absentes alors que COUNT(*) compte les lignes",
   "proof": "S15/sql-valeurs-absentes/M2",
   "line": 24
  },
  {
   "source": "linux-hierarchie-liens-usr",
   "target": "linux-variable-environnement",
   "kind": "analogue",
   "status": "recognized",
   "date": "31/10/2026",
   "limit": "la variable vit dans la mémoire d'un shell (perdue avec lui, propre à un terminal) ; le lien est une entrée stockée dans le système de fichiers, qui survit et que tous les programmes voient",
   "proof": "S17/linux-hierarchie-liens-usr/analogie trouvée par Louis ; limite trouvée avec le rappel de DEST",
   "line": 25
  },
  {
   "source": "linux-utilisateur-droits",
   "target": "linux-utilisateur-non-privilegie",
   "kind": "prerequis",
   "status": "demonstrated",
   "date": "31/10/2026",
   "limit": null,
   "proof": "S18/linux-utilisateur-droits/M1",
   "line": 26
  },
  {
   "source": "linux-utilisateur-non-privilegie",
   "target": "principes-moindre-privilege",
   "kind": "instance_de",
   "status": "recognized",
   "date": "31/10/2026",
   "limit": null,
   "proof": "S18/linux-utilisateur-non-privilegie/M3",
   "line": 27
  },
  {
   "source": "linux-variable-environnement",
   "target": "linux-utilisateur-non-privilegie",
   "kind": "complementaire",
   "status": "theoretical",
   "date": "31/10/2026",
   "limit": "une variable vide fait viser le mauvais chemin; l'utilisateur ordinaire borne les dégâts mais ne remplace pas la vérification de la variable",
   "proof": null,
   "line": 28
  },
  {
   "source": "linux-path",
   "target": "linux-environnement-construction",
   "kind": "prerequis",
   "status": "demonstrated",
   "date": "31/10/2026",
   "limit": null,
   "proof": "S19/linux-environnement-construction/M3",
   "line": 29
  },
  {
   "source": "linux-variable-environnement",
   "target": "linux-environnement-construction",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "31/10/2026",
   "limit": null,
   "proof": null,
   "line": 30
  },
  {
   "source": "linux-environnement-construction",
   "target": "principes-isolation-environnement",
   "kind": "instance_de",
   "status": "theoretical",
   "date": "31/10/2026",
   "limit": null,
   "proof": null,
   "line": 31
  },
  {
   "source": "linux-environnement-construction",
   "target": "minishell-environnement",
   "kind": "analogue",
   "status": "recognized",
   "date": "31/10/2026",
   "limit": "Louis : son Minishell gérait déjà la liste des variables d'un shell ; ici elle est vidée puis reconstruite par fichiers, alors que Minishell copiait un comportement de bash (limite : à vérifier si sa liste était transmise aux programmes lancés)",
   "proof": null,
   "line": 32
  },
  {
   "source": "linux-utilisateur-non-privilegie",
   "target": "linux-environnement-construction",
   "kind": "complementaire",
   "status": "theoretical",
   "date": "31/10/2026",
   "limit": "l'utilisateur lfs protège l'hôte de la construction ; l'environnement vide protège la construction de l'hôte",
   "proof": null,
   "line": 33
  },
  {
   "source": "linux-compilation-croisee",
   "target": "linux-chaine-croisee-binutils",
   "kind": "prerequis",
   "status": "demonstrated",
   "date": "01/11/2026",
   "limit": null,
   "proof": "S21/linux-compilation-croisee/M1 (prérequis diagnostiqué)",
   "line": 34
  },
  {
   "source": "linux-chargeur-dynamique",
   "target": "linux-chaine-croisee-binutils",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "01/11/2026",
   "limit": null,
   "proof": null,
   "line": 35
  },
  {
   "source": "linux-prerequis-hote",
   "target": "linux-chaine-croisee-binutils",
   "kind": "prerequis",
   "status": "demonstrated",
   "date": "01/11/2026",
   "limit": null,
   "proof": "S21 (configure échoue sans compilateur sur l'hôte)",
   "line": 36
  },
  {
   "source": "linux-chaine-croisee-binutils",
   "target": "principes-isolation-environnement",
   "kind": "instance_de",
   "status": "theoretical",
   "date": "01/11/2026",
   "limit": "résultat indépendant de l'hôte, comme l'environnement vide de lfs",
   "proof": null,
   "line": 37
  },
  {
   "source": "linux-lib64-interpreteur",
   "target": "linux-chargeur-dynamique",
   "kind": "complementaire",
   "status": "theoretical",
   "date": "01/11/2026",
   "limit": "lib64 : le chemin du chargeur est écrit dans chaque programme; le chargeur lui-même est la notion découverte le 01/11",
   "proof": null,
   "line": 38
  },
  {
   "source": "linux-processus",
   "target": "docker-conteneur-processus-isole",
   "kind": "prerequis",
   "status": "demonstrated",
   "date": "02/11/2026",
   "limit": null,
   "proof": "S22 (le sleep du conteneur est un processus de l'hôte dans ps)",
   "line": 39
  },
  {
   "source": "linux-noyau-distribution",
   "target": "docker-conteneur-processus-isole",
   "kind": "prerequis",
   "status": "demonstrated",
   "date": "02/11/2026",
   "limit": null,
   "proof": "S22 (noyau partagé contre noyau distinct d'une VM, donné par Louis)",
   "line": 40
  },
  {
   "source": "docker-image-conteneur",
   "target": "docker-conteneur-processus-isole",
   "kind": "prerequis",
   "status": "demonstrated",
   "date": "02/11/2026",
   "limit": null,
   "proof": "S22 (restitution du conteneur)",
   "line": 41
  },
  {
   "source": "docker-conteneur-processus-isole",
   "target": "docker-volume-nomme-vs-bind",
   "kind": "prerequis",
   "status": "demonstrated",
   "date": "02/11/2026",
   "limit": null,
   "proof": "S22 (couche d'écriture du conteneur perdue à la création)",
   "line": 42
  },
  {
   "source": "docker-conteneur-processus-isole",
   "target": "docker-reseau-isole",
   "kind": "prerequis",
   "status": "demonstrated",
   "date": "02/11/2026",
   "limit": null,
   "proof": "S22 (annuaire et isolation entre réseaux)",
   "line": 43
  },
  {
   "source": "linux-demarrage",
   "target": "docker-conteneur-processus-isole",
   "kind": "transfert",
   "status": "recognized",
   "date": "02/11/2026",
   "limit": "init = PID 1 du démarrage, PID 1 d'un conteneur = commande placée après le nom de l'image; le conteneur ne démarre pas de machine",
   "proof": "S22 (Louis a relié PID 1 et init)",
   "line": 44
  },
  {
   "source": "docker-conteneur-processus-isole",
   "target": "principes-moindre-privilege",
   "kind": "instance_de",
   "status": "recognized",
   "date": "02/11/2026",
   "limit": "le moindre privilège limite les droits d'un acteur, le conteneur limite sa vue",
   "proof": "S22 (moindre privilège cité par Louis pour le conteneur en root)",
   "line": 45
  },
  {
   "source": "docker-conteneur-processus-isole",
   "target": "principes-isolation-environnement",
   "kind": "instance_de",
   "status": "theoretical",
   "date": "02/11/2026",
   "limit": "un conteneur isole la vue, il ne garantit pas l'indépendance totale (noyau partagé)",
   "proof": null,
   "line": 46
  },
  {
   "source": "docker-volume-nomme-vs-bind",
   "target": "principes-separer-etat-processus",
   "kind": "instance_de",
   "status": "recognized",
   "date": "02/11/2026",
   "limit": null,
   "proof": "S22 (principe donné par Louis: volume pour garder son avancée)",
   "line": 47
  },
  {
   "source": "docker-volume-nomme-vs-bind",
   "target": "linux-qcow2-snapshot",
   "kind": "analogue",
   "status": "recognized",
   "date": "02/11/2026",
   "limit": "un volume garde l'état en cours, un snapshot une copie figée à un instant avec retour en arrière possible",
   "proof": "S22 (analogie donnée par Louis)",
   "line": 48
  },
  {
   "source": "docker-reseau-isole",
   "target": "principes-surface-exposition",
   "kind": "instance_de",
   "status": "theoretical",
   "date": "02/11/2026",
   "limit": null,
   "proof": null,
   "line": 49
  },
  {
   "source": "principes-surface-exposition",
   "target": "principes-moindre-privilege",
   "kind": "complementaire",
   "status": "theoretical",
   "date": "02/11/2026",
   "limit": "surface d'exposition: ce qui est joignable; moindre privilège: ce qu'un acteur peut faire",
   "proof": null,
   "line": 50
  },
  {
   "source": "docker-conteneur-root-defaut",
   "target": "docker-volume-nomme-vs-bind",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "02/11/2026",
   "limit": null,
   "proof": null,
   "line": 51
  },
  {
   "source": "linux-utilisateur-droits",
   "target": "docker-conteneur-root-defaut",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "02/11/2026",
   "limit": null,
   "proof": null,
   "line": 52
  },
  {
   "source": "docker-idempotence-demarrage",
   "target": "principes-idempotence",
   "kind": "instance_de",
   "status": "theoretical",
   "date": "02/11/2026",
   "limit": null,
   "proof": null,
   "line": 53
  },
  {
   "source": "linux-redirections-shell",
   "target": "docker-modele-envsubst",
   "kind": "prerequis",
   "status": "demonstrated",
   "date": "02/11/2026",
   "limit": null,
   "proof": "S22 (redirections < et > de load_model.sh)",
   "line": 54
  },
  {
   "source": "docker-conteneur-processus-isole",
   "target": "docker-idempotence-demarrage",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "02/11/2026",
   "limit": "restart relance le même conteneur, donc le script de démarrage se rejoue sur l'état déjà créé",
   "proof": null,
   "line": 55
  },
  {
   "source": "linux-chaine-croisee-binutils",
   "target": "linux-gcc-passe1",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "07/11/2026",
   "limit": null,
   "proof": null,
   "line": 56
  },
  {
   "source": "linux-gcc-passe1",
   "target": "linux-glibc-contenu",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "07/11/2026",
   "limit": "la passe 1 compile la Glibc",
   "proof": null,
   "line": 57
  },
  {
   "source": "linux-api-headers",
   "target": "linux-glibc-contenu",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "07/11/2026",
   "limit": "la Glibc ne peut pas être compilée sans eux",
   "proof": null,
   "line": 58
  },
  {
   "source": "linux-glibc-contenu",
   "target": "linux-libstdcpp",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "07/11/2026",
   "limit": "Libstdc++ dépend de la Glibc",
   "proof": null,
   "line": 59
  },
  {
   "source": "linux-chargeur-dynamique",
   "target": "linux-glibc-contenu",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "07/11/2026",
   "limit": "la Glibc installe le chargeur",
   "proof": null,
   "line": 60
  },
  {
   "source": "linux-tic-natif",
   "target": "principes-outil-construction-sur-build",
   "kind": "instance_de",
   "status": "theoretical",
   "date": "08/11/2026",
   "limit": null,
   "proof": null,
   "line": 61
  },
  {
   "source": "linux-build-host",
   "target": "principes-outil-construction-sur-build",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "08/11/2026",
   "limit": "le principe oppose la machine qui construit (`build`) à celle de destination (`host`)",
   "proof": null,
   "line": 62
  },
  {
   "source": "linux-compilation-croisee",
   "target": "linux-build-host",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "08/11/2026",
   "limit": "pourquoi une chaîne croisée précède la notion des deux machines",
   "proof": null,
   "line": 63
  },
  {
   "source": "linux-destdir",
   "target": "linux-build-host",
   "kind": "complementaire",
   "status": "theoretical",
   "date": "08/11/2026",
   "limit": "DESTDIR place les fichiers dans la racine de destination, `--host` dit où ils tourneront",
   "proof": null,
   "line": 64
  },
  {
   "source": "linux-configure-script",
   "target": "linux-build-host",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "09/11/2026",
   "limit": "configure porte les options --host et --build",
   "proof": null,
   "line": 65
  },
  {
   "source": "linux-chroot",
   "target": "principes-isolation-environnement",
   "kind": "analogue",
   "status": "theoretical",
   "date": "09/11/2026",
   "limit": "le chroot change la racine mais partage le noyau de l'hôte",
   "proof": null,
   "line": 66
  },
  {
   "source": "linux-suite-tests-resultats",
   "target": "linux-tests-chronometres-parallelisme",
   "kind": "complementaire",
   "status": "theoretical",
   "date": "09/11/2026",
   "limit": "lire les résultats d'une suite : un échec « Test timeout expired » peut venir de la charge, pas d'un défaut",
   "proof": null,
   "line": 67
  },
  {
   "source": "principes-cycle-jusqu-a-arret",
   "target": "linux-processus",
   "kind": "complementaire",
   "status": "theoretical",
   "date": "09/11/2026",
   "limit": "chaque appel récursif en attente occupe la pile du processus",
   "proof": null,
   "line": 68
  },
  {
   "source": "linux-comparer-journaux-reference",
   "target": "linux-suite-tests-resultats",
   "kind": "complementaire",
   "status": "theoretical",
   "date": "09/11/2026",
   "limit": "un écart de cause matérielle n'est pas un défaut du logiciel : la liste des échecs dit lesquels ont échoué et la référence dit s'ils sont attendus",
   "proof": null,
   "line": 69
  },
  {
   "source": "linux-noyau-distribution",
   "target": "linux-modules-noyau",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "10/11/2026",
   "limit": null,
   "proof": null,
   "line": 70
  },
  {
   "source": "linux-modules-noyau",
   "target": "linux-udev-devtmpfs",
   "kind": "complementaire",
   "status": "theoretical",
   "date": "10/11/2026",
   "limit": "udev charge les pilotes par MODALIAS ; un module ne peut pas servir au montage de la racine sans initramfs",
   "proof": null,
   "line": 71
  },
  {
   "source": "linux-demarrage",
   "target": "linux-sysv-init",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "10/11/2026",
   "limit": null,
   "proof": null,
   "line": 72
  },
  {
   "source": "linux-demarrage",
   "target": "linux-grub-amorcage",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "10/11/2026",
   "limit": null,
   "proof": null,
   "line": 73
  },
  {
   "source": "linux-partition",
   "target": "linux-fstab",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "10/11/2026",
   "limit": null,
   "proof": null,
   "line": 74
  },
  {
   "source": "linux-modules-noyau",
   "target": "linux-noyau-configuration",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "10/11/2026",
   "limit": null,
   "proof": null,
   "line": 75
  },
  {
   "source": "linux-noyau-configuration",
   "target": "linux-grub-amorcage",
   "kind": "complementaire",
   "status": "theoretical",
   "date": "10/11/2026",
   "limit": "la ligne linux de grub.cfg désigne le noyau installé et son root=",
   "proof": null,
   "line": 76
  },
  {
   "source": "linux-affichage-x11",
   "target": "linux-noyau-configuration",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "10/11/2026",
   "limit": "le serveur X exige DRM et un pilote d'entrée dans le noyau",
   "proof": null,
   "line": 77
  },
  {
   "source": "linux-somme-de-controle",
   "target": "linux-telechargement-sans-client",
   "kind": "transfert",
   "status": "demonstrated",
   "date": "10/11/2026",
   "limit": "vérifier une archive téléchargée sans outil de confiance",
   "proof": "S33/linux-telechargement-sans-client/M1",
   "line": 78
  },
  {
   "source": "linux-configure-script",
   "target": "linux-compilateur-variable-cc",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "12/11/2026",
   "limit": "configure choisit le compilateur par la variable CC",
   "proof": null,
   "line": 79
  },
  {
   "source": "linux-redirections-shell",
   "target": "linux-somme-de-controle",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "12/11/2026",
   "limit": "sha1sum -c lit l'entrée standard désignée par le nom -",
   "proof": null,
   "line": 80
  },
  {
   "source": "reseau-dns-resolution",
   "target": "linux-telechargement-sans-client",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "12/11/2026",
   "limit": "télécharger par un nom exige de le traduire en adresse",
   "proof": null,
   "line": 81
  },
  {
   "source": "linux-partition",
   "target": "linux-grub-amorcage",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "12/11/2026",
   "limit": "root=/dev/sda3 désigne la partition à brancher sur /",
   "proof": null,
   "line": 82
  },
  {
   "source": "linux-noyau-secours",
   "target": "linux-grub-amorcage",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "12/11/2026",
   "limit": "la seconde entrée se lit et s'écrit dans le menu de GRUB",
   "proof": null,
   "line": 83
  },
  {
   "source": "linux-fstab",
   "target": "linux-systemes-fichiers-virtuels",
   "kind": "complementaire",
   "status": "demonstrated",
   "date": "12/11/2026",
   "limit": "la ligne de fstab monte debugfs ; sans elle le dossier reste vide",
   "proof": "S36/linux-fstab/usage",
   "line": 84
  },
  {
   "source": "linux-qemu-port-serie",
   "target": "linux-grub-amorcage",
   "kind": "complementaire",
   "status": "theoretical",
   "date": "12/11/2026",
   "limit": "le fichier du port série reste vide tant que la ligne du noyau n'a pas console=ttyS0",
   "proof": null,
   "line": 85
  },
  {
   "source": "linux-localversion-auto",
   "target": "linux-noyau-configuration",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "13/11/2026",
   "limit": null,
   "proof": null,
   "line": 86
  },
  {
   "source": "linux-bzimage-vmlinux",
   "target": "linux-noyau-configuration",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "13/11/2026",
   "limit": null,
   "proof": null,
   "line": 87
  },
  {
   "source": "linux-arbre-noyau-stable",
   "target": "linux-noyau-secours",
   "kind": "complementaire",
   "status": "recognized",
   "date": "13/11/2026",
   "limit": "l'entrée de secours protège d'un noyau de l'arbre de Linus qui ne démarre pas, pas d'une image écrasée",
   "proof": "S37/linux-arbre-noyau-stable/M3",
   "line": 88
  },
  {
   "source": "noyau-module-premier",
   "target": "noyau-module-kbuild",
   "kind": "complementaire",
   "status": "demonstrated",
   "date": "13/11/2026",
   "limit": "le module ne se charge que si son .ko a été construit pour le noyau en marche ; le Makefile vise ce noyau",
   "proof": "S37/noyau-module-kbuild/M3",
   "line": 89
  },
  {
   "source": "c-makefile-cibles-factices",
   "target": "noyau-module-kbuild",
   "kind": "complementaire",
   "status": "demonstrated",
   "date": "13/11/2026",
   "limit": "sans .PHONY, un fichier nommé all ou clean empêche la construction du module",
   "proof": "S37/c-makefile-cibles-factices/M2",
   "line": 90
  },
  {
   "source": "noyau-module-premier",
   "target": "linux-modules-noyau",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "13/11/2026",
   "limit": null,
   "proof": null,
   "line": 91
  },
  {
   "source": "noyau-patch",
   "target": "noyau-style-code",
   "kind": "complementaire",
   "status": "theoretical",
   "date": "13/11/2026",
   "limit": null,
   "proof": null,
   "line": 92
  },
  {
   "source": "noyau-version-noyau",
   "target": "linux-localversion-auto",
   "kind": "complementaire",
   "status": "demonstrated",
   "date": "13/11/2026",
   "limit": "la version assemble EXTRAVERSION du Makefile, LOCALVERSION du .config et le suffixe du dépôt git",
   "proof": "S37/noyau-version-noyau/M3",
   "line": 93
  },
  {
   "source": "noyau-patch",
   "target": "linux-git-administration",
   "kind": "prerequis",
   "status": "theoretical",
   "date": "13/11/2026",
   "limit": null,
   "proof": null,
   "line": 94
  },
  {
   "source": "linux-tty-terminaux",
   "target": "linux-qemu-port-serie",
   "kind": "complementaire",
   "status": "theoretical",
   "date": "20/11/2026",
   "limit": null,
   "proof": null,
   "line": 95
  },
  {
   "source": "linux-bus-usb-hote",
   "target": "linux-tty-terminaux",
   "kind": "complementaire",
   "status": "theoretical",
   "date": "20/11/2026",
   "limit": null,
   "proof": null,
   "line": 96
  }
 ],
 "titles": [
  {
   "id": "answer-42",
   "name": "I AM THE ANSWER",
   "scope": "42",
   "condition": "niveau 42 officiel au moins égal à 25",
   "progress": {
    "value": 12.44,
    "status": "observed",
    "reason": "déclaré par Louis le 11/11/2026, API 42 non branchée"
   },
   "target": 25,
   "obtained": {
    "value": false,
    "status": "observed",
    "reason": null
   }
  },
  {
   "id": "answer-system",
   "name": "I AM THE ANSWER",
   "scope": "Système",
   "condition": "rang S sur toutes les cartes",
   "progress": {
    "value": 0,
    "status": "observed",
    "reason": null
   },
   "target": 19,
   "obtained": {
    "value": false,
    "status": "observed",
    "reason": null
   }
  },
  {
   "id": "achievements-42",
   "name": "Achievements",
   "scope": "42",
   "condition": "obtenus et non obtenus, lus dans l'API de l'intranet",
   "progress": {
    "value": null,
    "status": "insufficient",
    "reason": "liste indisponible : API 42 non branchée"
   },
   "target": null,
   "obtained": {
    "value": null,
    "status": "insufficient",
    "reason": "liste indisponible : API 42 non branchée"
   }
  }
 ],
 "anomalies": [
  {
   "file": "cartes/linux-systeme.md",
   "line": 82,
   "reason": "2 cellules au lieu de 3, ligne rejetée",
   "rejected": true
  },
  {
   "file": "cartes/linux-systeme.md",
   "line": 83,
   "reason": "2 cellules au lieu de 3, ligne rejetée",
   "rejected": true
  },
  {
   "file": "cartes/linux-systeme.md",
   "line": 84,
   "reason": "2 cellules au lieu de 3, ligne rejetée",
   "rejected": true
  },
  {
   "file": "cartes/linux-systeme.md",
   "line": 85,
   "reason": "2 cellules au lieu de 3, ligne rejetée",
   "rejected": true
  },
  {
   "file": "cartes/linux-systeme.md",
   "line": 86,
   "reason": "2 cellules au lieu de 3, ligne rejetée",
   "rejected": true
  },
  {
   "file": "cartes/linux-systeme.md",
   "line": 87,
   "reason": "2 cellules au lieu de 3, ligne rejetée",
   "rejected": true
  },
  {
   "file": "cartes/linux-systeme.md",
   "line": 88,
   "reason": "2 cellules au lieu de 3, ligne rejetée",
   "rejected": true
  },
  {
   "file": "cartes/linux-systeme.md",
   "line": 89,
   "reason": "2 cellules au lieu de 3, ligne rejetée",
   "rejected": true
  },
  {
   "file": "cartes/linux-systeme.md",
   "line": 90,
   "reason": "2 cellules au lieu de 3, ligne rejetée",
   "rejected": true
  },
  {
   "file": "cartes/linux-systeme.md",
   "line": 91,
   "reason": "2 cellules au lieu de 3, ligne rejetée",
   "rejected": true
  },
  {
   "file": "cartes/linux-systeme.md",
   "line": null,
   "reason": "en-tête : 58 notions annoncées, 48 lues",
   "rejected": false
  },
  {
   "file": "relations.csv",
   "line": 32,
   "reason": "minishell-environnement absent des cartes et de notions.md",
   "rejected": false
  }
 ]
};
