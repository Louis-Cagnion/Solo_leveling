window.SYSTEM_STATE = {
  "meta": {
    "schema_version": 1,
    "generated_at": "2026-11-11T10:00:00Z",
    "rules_fingerprint": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
  },
  "sources": [
    {
      "name": "professor",
      "status": "ok",
      "lines_read": 120,
      "lines_rejected": 1,
      "observed_at": "2026-11-11"
    },
    {
      "name": "api42",
      "status": "cache",
      "lines_read": 3,
      "lines_rejected": 0,
      "observed_at": "2026-11-10"
    },
    {
      "name": "xp_table",
      "status": "ok",
      "lines_read": 1,
      "lines_rejected": 0,
      "observed_at": null
    }
  ],
  "level42": {
    "level": {
      "value": 12.44,
      "status": "observed",
      "sources": [
        "api42"
      ],
      "reason": null,
      "reason_code": null
    },
    "xp": {
      "value": 133834,
      "status": "estimated",
      "sources": [
        "xp_table"
      ],
      "reason": "interpolation linéaire",
      "reason_code": "xp_interpolated"
    },
    "target_xp": {
      "value": 1000000,
      "status": "estimated",
      "sources": [
        "xp_table"
      ],
      "reason": "table tierce",
      "reason_code": "third_party_table"
    },
    "projects": [
      {
        "id": "projet_a",
        "name": "Projet A",
        "base_xp": {
          "value": 4200,
          "status": "observed",
          "sources": [
            "api42"
          ],
          "reason": null,
          "reason_code": null
        }
      }
    ],
    "email": "fictif"
  },
  "system": {
    "xp": {
      "value": 140000,
      "status": "estimated",
      "sources": [
        "professor",
        "xp_table"
      ],
      "reason": "taux de l'IA",
      "reason_code": "ia_rate"
    },
    "level": {
      "value": 12.6,
      "status": "estimated",
      "sources": [
        "xp_table"
      ],
      "reason": "table tierce",
      "reason_code": "third_party_table"
    },
    "origins": [
      {
        "origin": "42",
        "xp": {
          "value": 133834,
          "status": "estimated",
          "sources": [
            "xp_table"
          ],
          "reason": "table tierce",
          "reason_code": "third_party_table"
        }
      },
      {
        "origin": "perso",
        "xp": {
          "value": 6166,
          "status": "estimated",
          "sources": [
            "professor"
          ],
          "reason": "taux de l'IA",
          "reason_code": "ia_rate"
        }
      }
    ],
    "calibration": {
      "value": "provisional",
      "status": "insufficient",
      "sources": [
        "professor"
      ],
      "reason": "moins de 3 projets",
      "reason_code": "below_threshold"
    }
  },
  "trajectory": [
    {
      "date": "2026-11-10",
      "level42": 12.4,
      "system_level": 12.5
    }
  ],
  "cards": [
    {
      "id": "card_alpha",
      "name": "Alpha",
      "rank": {
        "value": "E",
        "status": "observed",
        "sources": [
          "professor"
        ],
        "reason": null,
        "reason_code": null
      },
      "next_rank": {
        "rank": "D",
        "condition": "toutes les notions débutantes au moins comprises",
        "progress": {
          "value": 1,
          "status": "observed",
          "sources": [
            "professor"
          ],
          "reason": null,
          "reason_code": null
        },
        "total": 2,
        "missing": [
          {
            "id": "notion_b",
            "state": "non rencontrée"
          }
        ]
      },
      "tiers": [
        {
          "name": "débutant",
          "notions": [
            "notion_a",
            "notion_b"
          ]
        }
      ],
      "certifications": [
        {
          "code": "CERT_X",
          "detail": "Certification X",
          "notions": [
            "notion_a"
          ],
          "conditions": null,
          "obtained": {
            "value": false,
            "status": "observed",
            "sources": [
              "professor"
            ],
            "reason": null,
            "reason_code": null
          },
          "obtained_on": null,
          "accessible": {
            "value": false,
            "status": "observed",
            "sources": [
              "professor"
            ],
            "reason": null,
            "reason_code": null
          }
        }
      ]
    },
    {
      "id": "card_beta",
      "name": "Bêta",
      "rank": {
        "value": null,
        "status": "unmeasurable",
        "sources": [],
        "reason": "liste des certifications illisible",
        "reason_code": "certification_list_unreadable"
      },
      "next_rank": null,
      "tiers": [],
      "certifications": [
        {
          "code": "CERT_Y",
          "detail": null,
          "notions": [],
          "conditions": null,
          "obtained": {
            "value": true,
            "status": "observed",
            "sources": [
              "professor"
            ],
            "reason": null,
            "reason_code": null
          },
          "obtained_on": "2026-10-20",
          "accessible": {
            "value": null,
            "status": "unmeasurable",
            "sources": [],
            "reason": "aucune notion ne cite cette certification",
            "reason_code": "no_certification_notion"
          }
        }
      ]
    },
    {
      "id": "card_gamma",
      "name": "Gamma",
      "rank": {
        "value": "none",
        "status": "observed",
        "sources": [
          "professor"
        ],
        "reason": null,
        "reason_code": null
      },
      "next_rank": {
        "rank": "E",
        "condition": "au moins une notion de la carte suivie",
        "progress": {
          "value": 0,
          "status": "observed",
          "sources": [
            "professor"
          ],
          "reason": null,
          "reason_code": null
        },
        "total": null,
        "missing": []
      },
      "tiers": [],
      "certifications": []
    }
  ],
  "notions": {
    "notion_a": {
      "label": "Notion A",
      "section": "Alpha",
      "state": {
        "value": "comprise",
        "status": "observed",
        "sources": [
          "professor"
        ],
        "reason": null,
        "reason_code": null
      },
      "goal": "appliquée",
      "card": "card_alpha",
      "tier": "débutant",
      "last_practice": "2026-11-01"
    },
    "notion_b": {
      "label": "Notion B",
      "section": "Alpha",
      "state": {
        "value": "non rencontrée",
        "status": "observed",
        "sources": [
          "professor"
        ],
        "reason": null,
        "reason_code": null
      },
      "goal": null,
      "card": "card_alpha",
      "tier": "débutant",
      "last_practice": null
    },
    "notion_hors_carte": {
      "label": "Notion hors carte",
      "section": null,
      "state": {
        "value": "en cours",
        "status": "observed",
        "sources": [
          "professor"
        ],
        "reason": null,
        "reason_code": null
      },
      "goal": null,
      "card": null,
      "tier": null,
      "last_practice": null
    }
  },
  "relations": [
    {
      "source": "notion_a",
      "target": "notion_b",
      "kind": "prerequis",
      "status": "reconnue",
      "limit": "valable hors contexte",
      "proof": null
    }
  ],
  "projects": [
    {
      "id": "projet_perso_01",
      "setting": "perso",
      "name": "Projet perso 01",
      "status": "livré",
      "date": "2026-10-15",
      "equivalent_42": "projet_a",
      "ia_factor": {
        "value": 0.5,
        "status": "estimated",
        "sources": [
          "ia_history"
        ],
        "reason": "moyenne des taux",
        "reason_code": "ia_rate"
      },
      "xp": {
        "value": 2100,
        "status": "estimated",
        "sources": [
          "ia_history",
          "xp_table"
        ],
        "reason": "taux de l'IA",
        "reason_code": "ia_rate"
      }
    }
  ],
  "titles": [
    {
      "id": "answer_42",
      "name": "I AM THE ANSWER",
      "scope": "42",
      "condition": "niveau 42 au moins égal à 25",
      "obtained": {
        "value": false,
        "status": "observed",
        "sources": [
          "api42"
        ],
        "reason": null,
        "reason_code": null
      },
      "progress": {
        "value": 12.44,
        "status": "observed",
        "sources": [
          "api42"
        ],
        "reason": null,
        "reason_code": null
      },
      "target": 25
    },
    {
      "id": "answer_system",
      "name": "I AM THE ANSWER (Système)",
      "scope": "Système",
      "condition": "rang S sur toutes les cartes",
      "obtained": {
        "value": null,
        "status": "unmeasurable",
        "sources": [],
        "reason": "une carte est non mesurable",
        "reason_code": "card_unmeasurable"
      },
      "progress": {
        "value": null,
        "status": "unmeasurable",
        "sources": [],
        "reason": "une carte est non mesurable",
        "reason_code": "card_unmeasurable"
      },
      "target": null
    }
  ],
  "anomalies": [
    {
      "file": "relations.csv",
      "line": 7,
      "kind": "ligne mal formée",
      "detail": "virgule"
    }
  ],
  "rules": {
    "proof_order": [
      "en cours",
      "comprise",
      "appliquée",
      "retenue"
    ],
    "excluded_states": [
      "déclarée"
    ],
    "rank_d_threshold": "comprise",
    "cert_threshold": "retenue",
    "target_level": 25
  },
  "achievements": {
    "complete": {
      "value": true,
      "status": "observed",
      "sources": [
        "api42"
      ],
      "reason": null,
      "reason_code": null
    },
    "items": [
      {
        "id": "achievement_first",
        "name": "Premier pas",
        "description": "Rendre un premier projet",
        "obtained": {
          "value": true,
          "status": "observed",
          "sources": [
            "api42"
          ],
          "reason": null,
          "reason_code": null
        },
        "obtained_on": "2026-10-01",
        "title": null
      },
      {
        "id": "achievement_answer",
        "name": "La réponse",
        "description": "Atteindre le niveau 25",
        "obtained": {
          "value": false,
          "status": "observed",
          "sources": [
            "api42"
          ],
          "reason": null,
          "reason_code": null
        },
        "obtained_on": null,
        "title": "answer_42"
      }
    ]
  },
  "names": {
    "en": {
      "notion_a": "Notion A",
      "card_alpha": "Alpha",
      "CERT_X": "Certification X"
    }
  }
};
