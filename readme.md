# General

Ce projet a pour but d'ouvrir les données de météo france sur les Bulletins Estimations Risque Avalance (BERA).
Ces données sont déjà [disponibles](https://donneespubliques.meteofrance.fr/?fond=produit&id_produit=265&id_rubrique=50) mais difficiles à traiter pour des ré-utilisations.

Objectifs de réutilisations :
  - Evaluation du risque de la partie supérieure du manteau neigeux (préparation sorties)
  - Outil pédagogique afin d'étudier les accidents ayant eu lieu

# Autres projets
- [MetaSkiRando :](https://www.metaskirando.ovh/Nivo.php) Moteur de recherche du ski de rando (et [code source](https://github.com/c2corg/metaskirando))
- [Data Avalanche :](http://www.data-avalanche.org) Recensemement des avalanches
- [Synthesis :](http://www.data-avalanche.org/synthesis/) Centrale de données nivologiques
- [Anena :](https://www.anena.org/)  Association Nationale pour l’Étude de la Neige et des Avalanches

# Modèle de données
Clé Primaires :
- date
- massif

|Nom|Titre|Type|Description|Exemple|Propriétés|
|-|-|-|-|-|-|
|date|Date d'émission du bulletin|date|Date d'émission. Le bulletin est valable pour le jour suivant. En général, les bulletins sont émis vers 16H|2022-01-31|Valeur obligatoire|
|massif|Massif|text|Massif concerné par l'estimation. La liste des massifs est connue. Le champ doit faire parti de cette liste|CHARTREUSE|Valeur obligatoire|
|risque1|Risque 1|int|Risque estimé pour le massif à toutes les altitudes ou éventuellement pour les altitudes les plus basses (précisé par le champ altitude). Le risque peut pendre une valeur de 0 à 5. Plus la valeur est importante, plus le risque est important. |2|Valeur obligatoire|
|evolurisque1| Evolution Risque 1|text||||
|loc1|Localisation 1|text|||
|altitude|Altitude|Int|Altitude différenciant 2 niveaux de risques différents (en mètres)|1750|Valeur optionnelle|
|risque2|Risque 2|text| - |3|Valeur optionnelle (sauf si le champ altitude n'est pas vide)|
|evolurisque2|Evolution Risque 1|double precision| -  ||Valeur optionnelle (sauf si le champ altitude n'est pas vide)|
|loc2|Localisation 2|int|Localisation 2| - | Valeur optionnelle (sauf si le champ altitude n'est pas vide)|
|risque_maxi|Risque Maximum|int|Risque estimé maximum pour le massif| 3 | Valeur optionnelle (sauf si le champ altitude n'est pas vide)|
|commentaire|Commentaire|string|Commentaire fourni par météo france (déclanchements spontanés, déclanchements par skieur)| - | Valeur optionnelle|
