#!/usr/bin/env bash

for massif in $(ls app/data); do
    # Lecture de la date de publication de notre fichier
    url=$(tail -n 1 app/data/$massif/urls_list.txt)

    # Traitement du fichier
    python app/utils/bulletin.py $massif $url
done
