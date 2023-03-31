import pytest
import xml.etree.ElementTree as ET

from mock import patch, PropertyMock
from src.utils.bulletin import Bulletin, MassifInexistantException


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


def test_parse():
    bu = Bulletin('VERCORS', '20200517132702')
    with patch('src.utils.bulletin.Bulletin.path_file',
               new_callable=PropertyMock) as a:
        a.return_value = 'tests/valid_bera.xml'
        risques = bu.parse_données_risques()
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
    with patch('src.utils.bulletin.Bulletin.path_file',
               new_callable=PropertyMock) as a:
        a.return_value = 'tests/invalid_tag_bera.xml'
        with pytest.raises(ET.ParseError):
            bu.parse_données_risques()
    with patch('src.utils.bulletin.Bulletin.path_file',
               new_callable=PropertyMock) as a:
        a.return_value = 'tests/invalid_attribute_bera.xml'
        with pytest.raises(ET.ParseError):
            bu.parse_données_risques()
