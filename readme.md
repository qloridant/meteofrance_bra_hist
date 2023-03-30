# General

Ce projet ouvre les données de Météo-France sur les Bulletins d'estimation du risque d'avalanche (BERA).
Ces données sont déjà [disponibles](https://donneespubliques.meteofrance.fr/?fond=produit&id_produit=265&id_rubrique=50), 
mais uniquement au format pdf et difficiles à traiter pour des réutilisations.

Les données extraites des BERAs sont enregistrées et disponibles dans les fichiers `data/<MASSIF>/hist.csv` de ce projet.

Objectifs de réutilisations :
  - Evaluation du risque de la partie supérieure du manteau neigeux (préparation sorties)
  - Outil pédagogique afin d'étudier les accidents ayant eu lieu

# Autres projets
- [MetaSkiRando :](https://www.metaskirando.ovh/Nivo.php) Moteur de recherche du ski de rando (et [code source](https://github.com/c2corg/metaskirando))
- [Data Avalanche :](http://www.data-avalanche.org) Recensement des avalanches
- [Synthesis :](http://www.data-avalanche.org/synthesis/) Centrale de données nivologiques
- [Anena :](https://www.anena.org/)  Association Nationale pour l’Étude de la Neige et des Avalanches
- [YETI par CampToCamp](https://www.camptocamp.org/yeti) Préparation de sorties avec méthode de réduction des risques
- [Snowmap](https://snowmap.fr/)  Outil de visualisation cartographique de l'enneigement par massif
- [Aineva : bulletins d'estimation des risques d'avalanahc en Italie](https://bollettini-fr.aineva.it/bulletin/latest) Visualisation des risques d'avalanches sur les massifs montagneux italiens

# Modèle de données
Source :
  [Météo-France](https://donneespubliques.meteofrance.fr/?fond=produit&id_produit=265&id_rubrique=50)
  
Clé Primaire :
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
|url_telechargement|Url de téléchargement|string|Url de téléchargement du BERA en pdf|https://donneespubliques.meteofrance.fr/donnees_libres/Pdf/BRA/BRA.ANDORRE.20230327133137.pdf|Valeur optionnelle|
Illustration de l'exemple :

![ex_thabor](https://user-images.githubusercontent.com/14170613/169779005-bae4fa10-16ad-4457-895b-7dbff6494dbe.png)


🔴 Cas particulier 🔴 :

![cas_particulier_1](https://user-images.githubusercontent.com/14170613/169779307-1ec4ae30-6036-4a2c-8b2a-81bcfdc4e608.png)

## Arborescene originale

Sur le site de météo-france, les massifs sont regroupés par département ou régions. Vous pouvez retrouver ce découpage dans le fichier `zones.json`

Pour les coordonnées de ces zones, vous pouvez retrouver les travaux de l'ENSG sur leur [API](https://api.ensg.eu/zonesbra).


# Developpement

## Scripts du projet
Les différents scripts constituant ce projet sont les suivants :
- bera/daily_build_urls.py
- bera/daily_extract_all_beras.py
- bera/historical_build_urls.py
- bera/historical_extract_all_beras.py
- bera/utils/bulletin.py

Ces différents scripts sont détaillés dans chacun des fichiers de scripts.

De manière générale, ces scripts n'ont pas vocation à être lancés manuellement.

Toutefois, dans un contexte de développement, il peut être nécessaire des les utiliser.

Pour se faire :
1. Exporter les variables d'environnement nécessaires  à l'exécution des scripts
```
export GIT_BRANCH=<nom_de_la_branche_de_travail_courante_git>
export GIT_LOGIN=<nom_utilisateur_github>
export TOKEN=<personnal_access_token_github>
```

2. Installer poetry
```
install poetry
```

3. Lancer le script avec poetry
```
poetry run python <script>
```
