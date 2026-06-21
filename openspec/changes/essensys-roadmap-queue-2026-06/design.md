## Context

23 epics produit juin 2026 : Phase 0 done, Now = scénarios + mTLS + doc DNS, Next = trusted devices + prod CM5, Later = wizard + IAM + fleet.

## Décisions

1. **Format ID** : `2026-06.NNN` (NNN = 001..023, zéro-padded).
2. **Dossier nouveau change** : `essensys-{slug}-2026-06.NNN` pour les scaffolds planned uniquement.
3. **Changes legacy** : conserver le nom de dossier ; `roadmap_id` dans `.openspec.yaml`.
4. **Dépôt hôte** : memory par défaut ; backend/front/ansible/raspberry-gateway selon epic.

## Dépendances clés

```mermaid
flowchart TD
  P0[001-002 Phase 0 doc] --> NOW[006-009 Now]
  NOW --> NEXT[010-015 Next]
  NEXT --> LATER[016-023 Later]
  D007[007 doc-site] --> D008[008 doc-site-dns]
  G010[010 dual-nic] --> G012[012 prod-decision]
  G011[011 nixos] --> G012
  G009[009 mTLS] --> G013[013 trusted-devices]
  I002[002 install-doc] --> I014[014 ingest] --> I016[016 wizard]
```
