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
      "lines_rejected": 1
    },
    {
      "name": "api42",
      "status": "cache",
      "lines_read": 3,
      "lines_rejected": 0
    },
    {
      "name": "xp_table",
      "status": "ok",
      "lines_read": 1,
      "lines_rejected": 0
    }
  ],
  "level42": {
    "level": {
      "value": 12.44,
      "status": "observed",
      "sources": [
        "api42"
      ],
      "reason": null
    },
    "xp": {
      "value": 133834,
      "status": "estimated",
      "sources": [
        "xp_table"
      ],
      "reason": "interpolation linéaire"
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
          "reason": null
        }
      }
    ]
  },
  "system": {
    "xp": {
      "value": 140000,
      "status": "estimated",
      "sources": [
        "professor",
        "xp_table"
      ],
      "reason": "taux de l'IA"
    },
    "level": {
      "value": 12.6,
      "status": "estimated",
      "sources": [
        "xp_table"
      ],
      "reason": "table tierce"
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
          "reason": "table tierce"
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
          "reason": "taux de l'IA"
        }
      }
    ],
    "calibration": {
      "value": "provisional",
      "status": "estimated",
      "sources": [
        "professor"
      ],
      "reason": "moins de 3 projets"
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
      "name": "<img src=x onerror=alert(1)>",
      "rank": {
        "value": "E",
        "status": "observed",
        "sources": [
          "professor"
        ],
        "reason": null
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
          "tier": "débutant",
          "obtained": {
            "value": false,
            "status": "observed",
            "sources": [
              "professor"
            ],
            "reason": null
          }
        }
      ],
      "gaps": [
        "</script>"
      ]
    },
    {
      "id": "card_beta",
      "name": "Bêta",
      "rank": {
        "value": null,
        "status": "insufficient",
        "sources": [],
        "reason": "liste des certifications illisible"
      },
      "tiers": [],
      "certifications": [],
      "gaps": []
    }
  ],
  "notions": {
    "notion_a": {
      "label": "Notion A",
      "state": {
        "value": "comprise",
        "status": "observed",
        "sources": [
          "professor"
        ],
        "reason": null
      },
      "goal": "appliquée",
      "card": "card_alpha",
      "tier": "débutant",
      "last_practice": "2026-11-01"
    },
    "notion_b": {
      "label": "Notion B",
      "state": {
        "value": "non rencontrée",
        "status": "observed",
        "sources": [
          "professor"
        ],
        "reason": null
      },
      "goal": null,
      "card": "card_alpha",
      "tier": "débutant",
      "last_practice": null
    },
    "notion_hors_carte": {
      "label": "Notion hors carte",
      "state": {
        "value": "en cours",
        "status": "observed",
        "sources": [
          "professor"
        ],
        "reason": null
      },
      "goal": null,
      "card": null,
      "tier": null,
      "last_practice": null
    }
  },
  "relations": [
    {
      "source_id": "notion_a",
      "target_id": "notion_b",
      "kind": "prerequis",
      "status": "reconnu",
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
        "reason": "moyenne des taux"
      },
      "xp": {
        "value": 2100,
        "status": "estimated",
        "sources": [
          "ia_history",
          "xp_table"
        ],
        "reason": "taux de l'IA"
      }
    }
  ],
  "titles": [
    {
      "id": "answer_42",
      "name": "I AM THE ANSWER (42)",
      "scope": "42",
      "condition": "niveau 42 au moins égal à 25",
      "obtained": {
        "value": false,
        "status": "observed",
        "sources": [
          "api42"
        ],
        "reason": null
      },
      "progress": {
        "value": 12.44,
        "status": "observed",
        "sources": [
          "api42"
        ],
        "reason": null
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
        "status": "insufficient",
        "sources": [],
        "reason": "une carte est insuffisante"
      },
      "progress": {
        "value": null,
        "status": "insufficient",
        "sources": [],
        "reason": "une carte est insuffisante"
      },
      "target": null
    }
  ],
  "anomalies": [
    {
      "file": "relations.csv",
      "line": 7,
      "kind": "ligne mal formée",
      "detail": "<img src=x onerror=alert(1)> et </script>"
    }
  ],
  "network": {
    "nodes": [
      {
        "id": "notion_a",
        "type": "notion"
      },
      {
        "id": "card_alpha",
        "type": "card"
      }
    ],
    "edges": [
      {
        "source": "notion_a",
        "target": "card_alpha",
        "kind": "appartenance",
        "status": "reconnu"
      }
    ],
    "highlights": [
      {
        "id": "notion_b",
        "kind": "fragile_prerequisite"
      }
    ]
  }
};
