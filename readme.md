# General

Ce projet ouvre les données de Météo-France sur les Bulletins d'estimation du risque d'avalanche (BERA).
Ces données sont déjà [disponibles](https://donneespubliques.meteofrance.fr/?fond=produit&id_produit=265&id_rubrique=50) mais difficiles à traiter pour des ré-utilisations.

Les données sont disponibles : `data/<MASSIF>/hist.csv`

Objectifs de réutilisations :
  - Evaluation du risque de la partie supérieure du manteau neigeux (préparation sorties)
  - Outil pédagogique afin d'étudier les accidents ayant eu lieu

# Autres projets
- [MetaSkiRando :](https://www.metaskirando.ovh/Nivo.php) Moteur de recherche du ski de rando (et [code source](https://github.com/c2corg/metaskirando))
- [Data Avalanche :](http://www.data-avalanche.org) Recensemement des avalanches
- [Synthesis :](http://www.data-avalanche.org/synthesis/) Centrale de données nivologiques
- [Anena :](https://www.anena.org/)  Association Nationale pour l’Étude de la Neige et des Avalanches

# Modèle de données
Source :
  Météo-France 
  
Clé Primaires :
- date
- massif

|Nom|Titre|Type|Description|Exemple|Propriétés|
|-|-|-|-|-|-|
|date|Date d'émission du bulletin|string|Date d'émission. Le bulletin est valable pour le jour suivant. En général, les bulletins sont émis vers 16H|2022-04-17|Valeur obligatoire|
|massif|Massif|string|Massif concerné par l'estimation. La liste des massifs est connue. Le champ doit faire parti de cette liste|THABOR|Valeur obligatoire|
|risque1|Risque 1|int|Risque estimé pour le massif à toutes les altitudes ou éventuellement pour les altitudes les plus basses (précisé par le champ altitude). Le risque peut pendre une valeur de 0 à 5. Plus la valeur est importante, plus le risque est important. Une valeur à -1 indique que le risque n'a pas pu être évalué. |1|Valeur obligatoire|
|evolurisque1| Evolution Risque 1|string|Evolution du risque pour  au cours de la journée pour le risque 1||Valeur optionnelle|
|loc1|Localisation 1|int|Altitude à laquelle nous passons du rique 1 au risque 2|2200 |
|altitude|Altitude|string|Altitude à laquelle nous passons du rique 1 au risque 2|2200|Valeur optionnelle|
|risque2|Risque 2|int| Risque estimé pour le massif pour les altitudes les plus hautes (précisé par le champ altitude). Le risque peut pendre une valeur de 0 à 5. Plus la valeur est importante, plus le risque est important. Une valeur à -1 indique que le risque n'a pas pu être évalué.|1|Valeur optionnelle (sauf si le champ altitude n'est pas vide)|
|evolurisque2|Evolution Risque 2|int| Evolution du rique au cours de la journée pour le risque 2 |2|Valeur optionnelle (sauf si le champ altitude n'est pas vide)|
|loc2|Localisation 2|string|Localisation 2| Altitude à laquelle nous passons du rique 1 au risque 2 | Valeur optionnelle (sauf si le champ altitude n'est pas vide)|
|risque_maxi|Risque Maximum|string|Risque estimé maximum pour le massif| 2 | Valeur obligatoire|
|commentaire|Commentaire|string|Commentaire fourni par météo france (déclanchements spontanés, déclanchements par skieur)| Au dessus de 2200m : Risque faible évoluant en Risque limité. En dessous : Risque faible | Valeur optionnelle|

Illustration de l'exemple :

![ex_thabor](https://user-images.githubusercontent.com/14170613/169779005-bae4fa10-16ad-4457-895b-7dbff6494dbe.png)


🔴 Cas particulier 🔴 :

![cas_particulier_1](https://user-images.githubusercontent.com/14170613/169779307-1ec4ae30-6036-4a2c-8b2a-81bcfdc4e608.png)

## Arborescene originale

Sur le site de météo-france, les massifs sont regroupés par département ou régions. Vous pouvez retrouver ce découpage dans le fichier `zones.json`

Pour les coordonnées de ces zones, vous pouvez retrouvez les travaux de l'ENSG sur leur [API](https://api.ensg.eu/zonesbra).

