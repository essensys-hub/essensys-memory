# portal-command-delivery Specification

## Purpose

Garantir que les commandes envoyées depuis le portail mon.essensys.fr arrivent à l'armoire avec le même effet que si elles avaient été exécutées une à une, même quand plusieurs commandes attendent et sont livrées ensemble.

## Requirements

### Requirement: Fusion sans perte des commandes lumières et volets
Quand plusieurs commandes en attente pour une même armoire sont livrées ensemble, la commande livrée SHALL avoir le même effet que l'application successive de ces commandes, dans leur ordre d'émission. Pour les index lumières et volets (605 à 622), les bits de commandes différentes MUST se cumuler. Une commande ultérieure MUST NOT effacer l'effet d'une commande précédente sur une autre lampe ou un autre volet.

#### Scenario: Tout allumer
- **WHEN** le portail envoie 21 commandes « allumer », une par lampe, dont plusieurs lampes qui partagent le même index, et que l'armoire les reçoit en une seule livraison
- **THEN** la commande livrée allume les 21 lampes

#### Scenario: Deux lampes sur le même index
- **WHEN** deux commandes en attente allument respectivement la lampe de bit 1 et la lampe de bit 4 du même index
- **THEN** la commande livrée porte la valeur 5 sur cet index

### Requirement: Dernière intention par équipement
Pour une même lampe ou un même volet, la commande livrée SHALL refléter la dernière demande émise. Si une lampe est allumée puis éteinte avant la livraison, elle MUST être éteinte, et réciproquement ; de même pour un volet ouvert puis fermé.

#### Scenario: Allumer puis éteindre
- **WHEN** une lampe est allumée puis éteinte, et les deux commandes attendent encore l'armoire
- **THEN** la commande livrée éteint cette lampe et ne l'allume pas

#### Scenario: Ouvrir puis fermer un volet
- **WHEN** un volet est ouvert puis fermé avant la livraison
- **THEN** la commande livrée ferme ce volet et ne l'ouvre pas

### Requirement: Commande conforme au firmware
Une commande livrée qui touche les lumières ou les volets MUST contenir le bloc complet des index 605 à 622 et le déclencheur 590 à `"1"`. Une commande livrée MUST NOT dépasser 30 paramètres. Les commandes qui ne touchent ni lumières ni volets SHALL être livrées dans leur ordre d'émission, sans perte.

#### Scenario: Scénario et lumières en attente
- **WHEN** une modification de scénario et deux commandes de lampes attendent la même armoire
- **THEN** l'armoire reçoit les deux effets, chaque commande livrée a au plus 30 paramètres, et le bloc lumières est complet

### Requirement: Acquittement de toutes les commandes livrées
Quand l'armoire acquitte une livraison, toutes les commandes en attente qui y ont été regroupées SHALL passer au statut « exécutée ». La dernière action affichée au portail MUST correspondre à la dernière commande émise.

#### Scenario: Acquittement d'une livraison groupée
- **WHEN** l'armoire acquitte une livraison qui regroupait 14 commandes
- **THEN** les 14 commandes sont marquées exécutées et le portail affiche « Exécutée » pour la dernière
