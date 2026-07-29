## 1. Matériel — brochage et préconditions physiques

- [ ] 1.1 Documenter le brochage J33 dans `essensys-doc` (source : R1, schéma Altium PDF page 5, feuille "Coeur") — brochage déjà levé, tâche = transcription doc, pas re-recherche
- [ ] 1.2 **[À LEVER]** Extraire la **position physique du jumper JC1** sur le PCB assemblé, depuis `Assembly Drawings_[No Variations].pdf` (essensys-board-SC944D) ou par inspection visuelle directe d'une carte assemblée — **bloquant avant tout câblage**, ne pas deviner
- [ ] 1.3 Vérifier/monter JC1 en position BDM (« 0 = monté ») sur la carte de test dédiée avant tout câblage du pod
- [ ] 1.4 **[À LEVER, mineur]** Confirmer le rôle exact de TCLK (broche 1 de J33) en mode BDM pur — doc P&E Micro du connecteur 10 broches, ou mesure passive lecture seule sans risque
- [ ] 1.5 Câbler le pod BDM (Piste 1) à J33 (BKPT/DSO/DSI/DSCLK/RESET/GND, sense `+3V3S`) sur la carte de test ; masse commune Pi4↔cible
- [ ] 1.6 Vérifier niveaux 3.3 V et absence de tension 5 V côté GPIO si un chemin bit-bang (Piste 2) est câblé en parallèle pour évaluation

## 2. POC — validation Piste 1 (USBDM sur ARM64)

- [ ] 2.1 **[À LEVER, bloquant POC, risque Piste 1]** `git clone` + build `usbdm-eclipse-makefiles-build` (ou équivalent) sur Raspberry Pi OS 64-bit, sans cible branchée — vérifier que la compilation aboutit et qu'un exécutable CLI de flash existe
- [ ] 2.2 Tester cet exécutable en CLI headless (sans environnement graphique) — documenter s'il fonctionne tel quel, nécessite un wrapper d'automatisation GUI, ou échoue
- [ ] 2.3 Si 2.1/2.2 échouent : évaluer le repli Piste 2 (bit-bang GPIO, protocole intégralement sourcé en `design.md` §b) ou un pod alternatif au protocole USB documenté et ré-implémentable nativement ARM64
- [ ] 2.4 Documenter la décision finale Piste 1 vs Piste 2 dans `essensys-doc`, avec le résultat factuel du POC (pas de supposition)

## 3. POC — lecture flash (backup)

- [ ] 3.1 Implémenter la séquence BDM d'entrée (BKPT dans les 8 cycles post-RESET) et vérifier l'accès registre (RAREG/RDREG) sur la carte de test
- [ ] 3.2 Implémenter `backup` : READ intégral `0x0-0x7FFFF`, écriture `.bin`/`.s19`, calcul `sha256` pendant lecture BDM
- [ ] 3.3 Implémenter la relecture-vérification du fichier backup après écriture disque (hash disque == hash lecture BDM) avant de marquer "vérifié"
- [ ] 3.4 Export du backup hors-machine (artefact CI / release asset) et test de l'interlock : toute commande d'écriture doit être refusée tant que ce backup vérifié n'existe pas pour la cible

## 4. POC — flash zone app + verify

- [ ] 4.1 Implémenter `erase-app` restreint à `0x3000-0x7DFFF`, avec refus explicite de toute plage hors bornes (y compris `0x400-0x417`)
- [ ] 4.2 Implémenter `program` (WRITE) avec refus si CRC placeholder `0x0102` détecté à `0x3000`, et refus si l'image chevauche `0x400-0x417`
- [ ] 4.3 Implémenter `verify` : relecture READ et comparaison octet-à-octet avec l'image source, rapport de l'adresse en cas de divergence
- [ ] 4.4 Implémenter `reset` : GO/négation RESET, attente boot, confirmation que le bootloader valide le CRC applicatif et démarre l'app
- [ ] 4.5 Tester explicitement l'interlock CFM : tenter une écriture dans `0x400-0x417` et vérifier le refus avant tout envoi BDM
- [ ] 4.6 Tester que `0x7E000` (persistance `Tb_Echange[]`) reste bit-à-bit intact après un cycle erase-app + program

## 5. Injection CRC-16

- [ ] 5.1 Suivre le statut de `essensys-gcc#14` (injection CRC-16 post-link) — **dépendance dure**, ne pas dupliquer la logique de calcul CRC dans ce repo
- [ ] 5.2 Une fois `#14` livré, intégrer l'outil comme étape `crc-inject` du pipeline (consommation, pas réimplémentation)
- [ ] 5.3 Si `#14` prend du retard : documenter explicitement le blocage dans le pipeline (le job `crc-inject` échoue tant que l'outil n'est pas disponible) plutôt que de flasher un CRC placeholder

## 6. Installation runner self-hosted Pi 4

- [ ] 6.1 Installer le runner GitHub Actions self-hosted sur le Pi 4, labels `[self-hosted, rpi4, bdm, sc944d]`
- [ ] 6.2 Restreindre le runner : jamais de déclenchement `pull_request` depuis un fork ; limiter aux tags/branches protégés
- [ ] 6.3 Câbler en permanence la carte de test SC944D dédiée au pod BDM branché au runner
- [ ] 6.4 Documenter l'alimentation stable de la carte de test pendant flash (E11) et la procédure de re-vérification après coupure suspectée

## 7. Workflows GitHub Actions + rollback

- [ ] 7.1 Écrire le job `build` (ubuntu-latest, image `essensys-builder`) → artefact `.s19`/`.elf`/`.map`
- [ ] 7.2 Écrire le job `crc-inject` (dépend de §5) → artefact `.s19` flashable
- [ ] 7.3 Écrire le job `flash` (self-hosted rpi4) : backup → erase-app → program → verify → reset + smoke, avec interlocks CI (backup vérifié / CRC injecté / identité cible)
- [ ] 7.4 Écrire le job `report` : résumé versions avant/après, hashes, PASS/FAIL
- [ ] 7.5 Configurer les triggers : tag `fw-v*` et `workflow_dispatch` (choix cible + confirmation)
- [ ] 7.6 Écrire le workflow de rollback dédié (`workflow_dispatch` séparé) : reflash backup pré-flash → verify → reset
- [ ] 7.7 Tester le rollback de bout en bout sur la carte de test (flasher une version, rollback, vérifier retour à l'état précédent)

## 8. Environnement hardware-flash + reviewer

- [ ] 8.1 Créer l'environnement GitHub `hardware-flash` avec reviewer humain obligatoire
- [ ] 8.2 Lier le job `flash` à cet environnement ; tester qu'il reste en attente sans approbation
- [ ] 8.3 Documenter la procédure d'approbation (qui, sur quels critères) dans le runbook

## 9. Documentation et recovery

- [ ] 9.1 Runbook de montage matériel (brochage J33, jumper JC1 avec position physique confirmée en §1.2, câblage pod)
- [ ] 9.2 Procédure recovery : que faire en cas d'échec de verify, de coupure d'alimentation pendant flash, de mismatch d'identité cible
- [ ] 9.3 Documenter explicitement la non-couverture des mémoires SPI externes (`SST25VF016B`, `25AA02E48T`) par ce backup
- [ ] 9.4 Documenter la dépendance dure à `essensys-gcc#14` et l'état d'avancement au moment du merge de ce change

## 10. Mise à jour essensys-memory

- [ ] 10.1 Mettre à jour `wiki/` (concept BDM programmer, entité `essensys-bdm-programmer`, lien vers `SC944D` et `essensys-gcc`)
- [ ] 10.2 Mettre à jour `okf/` et la roadmap avec ce change
- [ ] 10.3 Lancer `scripts/sync-sources.sh`, `scripts/extract-git-history.sh`, `scripts/update-roadmap.sh` après merge
- [ ] 10.4 Valider `openspec validate essensys-rpi4-bdm-programmer-2026-07-037 --strict` avant clôture
- [ ] 10.5 Publier la roadmap publique si la queue le requiert (`publish-roadmap-public.sh`)

## Definition of Done (reprise du prompt de cadrage §6)

- [ ] Backup 512 KB relu et vérifié (sha256) produit et stocké hors-machine avant toute écriture — interlock prouvé par test
- [ ] Brochage J33 documenté depuis le schéma (fait) ; position JC1 confirmée physiquement (§1.2, [À LEVER])
- [ ] Flash de la zone app seule ; bootloader `0x0-0x3000` et persistance `0x7E000` intacts (vérifié par relecture)
- [ ] Image flashée = `.s19` essensys-gcc avec CRC-16 injecté ; après reset, le bootloader valide le CRC et l'app démarre
- [ ] Verify par relecture octet-à-octet OK ; rapport versions avant/après
- [ ] Pipeline GitHub Actions build → crc-inject → flash (self-hosted Pi4) → report, avec gate reviewer et workflow de rollback fonctionnels
- [ ] Runner matériel jamais exposé aux PR de forks ; restreint tags/branches protégés
- [ ] Aucune écriture en `0x400-0x417` (CFM, plage corrigée par R1) non maîtrisée ; procédure recovery documentée
- [ ] Validation POC USBDM ARM64 tranchée (§2, [À LEVER]) — Piste 1 confirmée ou repli Piste 2 documenté
- [ ] `essensys-memory` mis à jour (wiki + OKF + roadmap)
