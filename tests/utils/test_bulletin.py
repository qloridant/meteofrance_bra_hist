import pytest
import xml.etree.ElementTree as ET

from mock import patch, PropertyMock
from bera.utils.bulletin import Bulletin, MassifInexistantException
from bera.utils.common import Label


def test_init():
    valid_bu = Bulletin('CHARTREUSE', '20160417132702')
    assert valid_bu.jour == '20160417132702'
    assert valid_bu.massif == 'CHARTREUSE'

    with pytest.raises(MassifInexistantException):
        Bulletin('CHARTREUX', '20160417132702')


def test_jour_key():
    bu = Bulletin('CHARTREUSE', '20160417132702')

    assert len(bu.jour_key) == 10
    assert (bu.jour_key[4] == '-' and bu.jour_key[7] == '-')
    assert bu.jour_key == '2016-04-17'
    assert bu.jour_key != '20160417132702'


def test_parse_donnees_risques():
    bu = Bulletin('VERCORS', '20200517132702')
    with patch('bera.utils.bulletin.Bulletin.path_file',
               new_callable=PropertyMock) as a:
        a.return_value = 'tests/valid_bera.xml'
        risques = bu.parse_donnees_risques()
        assert len(risques) == 9
        assert 'RISQUE1' in risques
        assert 'EVOLURISQUE1' in risques
        assert 'LOC1' in risques
        assert 'ALTITUDE' in risques
        assert 'RISQUE2' in risques
        assert 'EVOLURISQUE2' in risques
        assert 'LOC2' in risques
        assert 'RISQUEMAXI' in risques
        assert 'COMMENTAIRE' in risques
    with patch('bera.utils.bulletin.Bulletin.path_file',
               new_callable=PropertyMock) as a:
        a.return_value = 'tests/invalid_tag_bera.xml'
        with pytest.raises(ET.ParseError):
            bu.parse_donnees_risques()
    with patch('bera.utils.bulletin.Bulletin.path_file',
               new_callable=PropertyMock) as a:
        a.return_value = 'tests/invalid_attribute_bera.xml'
        with pytest.raises(ET.ParseError):
            bu.parse_donnees_risques()


def test_parse_situation_avalancheuse():
    bu = Bulletin('VERCORS', '20200517132702')
    with patch('bera.utils.bulletin.Bulletin.path_file',
               new_callable=PropertyMock) as a:
        a.return_value = 'tests/valid_bera.xml'
        bu.parse_donnees_risques()
        bu.parse_situation_avalancheuse()
        assert bu.situation_avalancheuse == {'situation_avalancheuse_typique': [Label.SOUS_COUCHE_FRAGILE]}


def test_extract_situation_typique_avalancheuse_from_stabilite_paragraph():
    raw_text = "Bulletin rédigé à partir d'informations réduites.\n" \
               "Situation avalancheuse : neige ventée, neige humide.\n\n" \
               "Départs spontanés : la neige tombée dans les dernières 24 heures (25/30 cm) s'humidifie et se tasse " \
               "très vite à la faveur des éclaircies de ce lundi après-midi, permettant une stabilisation efficace " \
               "du manteau neigeux."
    expected_text = "neige ventée, neige humide."
    situation_typique_avalancheuse = Bulletin.extract_situation_typique_avalancheuse_from_stabilite_paragraph(raw_text)
    assert situation_typique_avalancheuse == expected_text

    raw_text = "Situation avalancheuse typique : plaque friable, sous-couche fragile persistante.\n\n" \
               "Déclenchements provoqués : des plaques d'aspect poudreux, de petites dimensions mais faciles à " \
               "déclencher, sont localement présentes en versants ombragés au-dessus de 2400 m. D'autres " \
               "pourraient se former mardi avec la petite couche de fraîche prévue, accompagnée d'un vent de sud-ouest."
    expected_text = "plaque friable, sous-couche fragile persistante."
    situation_typique_avalancheuse = Bulletin.extract_situation_typique_avalancheuse_from_stabilite_paragraph(raw_text)
    assert situation_typique_avalancheuse == expected_text

def test_extract_labels_situation_avalancheuse():
    basic_test_cases = [
        {
            "raw_text": "sous couche fragile persistante.",
            "expected_labels": {Label.SOUS_COUCHE_FRAGILE}
        },
        {
            "raw_text": "neige ventée",
            "expected_labels": {Label.NEIGE_SOUFFLEE}
        },
        {
            "raw_text": "neige fraîche.",
            "expected_labels": {Label.NEIGE_FRAICHE}
        },
        {
            "raw_text": "neige humide, ",
            "expected_labels": {Label.NEIGE_HUMIDE}
        },
        {
            "raw_text": "Plaque de fond.",
            "expected_labels": {Label.AVALANCHE_GLISSEMENT}
        },
        {
            "raw_text": "neige ventée, neige humide",
            "expected_labels": {Label.NEIGE_SOUFFLEE, Label.NEIGE_HUMIDE}
        },
        {
            "raw_text": "neige ventée, neige humide",
            "expected_labels": {Label.NEIGE_HUMIDE, Label.NEIGE_SOUFFLEE}
        }
    ]

    for tc in basic_test_cases:
        labels = Bulletin.extract_labels_situation_avalancheuse(tc["raw_text"])
        assert labels == tc["expected_labels"]

    raw_texts_sous_couche_fragile_persistante = [
        "sous-couche fragile persistante",
        "sous-couches fragiles persistantes",
        "Sous-couche fragile persistante",
        "sous couche fragile persistante",
        "sous couches fragile persistantes",
    ]
    for raw_text in raw_texts_sous_couche_fragile_persistante:
        labels = Bulletin.extract_labels_situation_avalancheuse(raw_text)
        assert labels == {Label.SOUS_COUCHE_FRAGILE}


def test_append_csv():
    bu = Bulletin('VERCORS', '20200517132702')
    with patch('bera.utils.bulletin.Bulletin.path_file',
               new_callable=PropertyMock) as a:
        a.return_value = 'tests/valid_bera.xml'
        bu.parse_donnees_risques()
        bu.parse_donnees_meteo()
        bu.parse_situation_avalancheuse()

        expected_data_list = [
            '2020-05-17', 'VERCORS', '1', '', '<2000', '2000', '2', '', '>2000', '2', ' ',
            'https://donneespubliques.meteofrance.fr/donnees_libres/Pdf/BRA/BRA.VERCORS.20200517132702.pdf',
            'Eclaircies', 'Non', 'Sans objet', '1800', '3400', '2000', '2500', 'S', '40', 'S', '50',
            'Eclaircies', 'Non', 'Sans objet', '2000', '3400', '2000', '2500', 'S', '30', 'S', '40',
            'Peu nuageux', 'Non', 'Sans objet', '2100', '3500', '2000', '2500', 'S', '30', 'S', '40',
            '1800', '0', f'{Label.SOUS_COUCHE_FRAGILE._value_}'
        ]

        bu_data_list = bu.append_csv()

        assert bu_data_list == expected_data_list
