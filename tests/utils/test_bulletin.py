import pytest
from mock import patch, PropertyMock
import xml.etree.ElementTree as ET

from utils.bulletin import Bulletin, MassifInexistantException, FormatDateException


def test_init():
    valid_bu = Bulletin('CHARTREUSE', '20160417132702')
    assert valid_bu.jour == '20160417132702'
    assert valid_bu.massif == 'CHARTREUSE'

    with pytest.raises(MassifInexistantException) as e_info:
        invalid_massif = Bulletin('CHARTREUX', '20160417132702')

    with pytest.raises(FormatDateException) as e_info:
        invalid_massif = Bulletin('CHARTREUSE', '2016')

def test_jour_key():
    bu = Bulletin('CHARTREUSE', '20160417132702')

    assert len(bu.jour_key) == 10
    assert (bu.jour_key[4] == '-' and bu.jour_key[7] == '-')
    assert bu.jour_key == '2016-04-17'

    assert bu.jour_key != '20160417132702'

def test():
    return ET.parse('tests/tmp_bera.xml')

def mock_et_parse():
    return test

def test_parse():
    bu = Bulletin('VERCORS', '20200517132702')
    with patch('utils.bulletin.Bulletin.path_file', new_callable=PropertyMock) as a:
        a.return_value = 'tests/valid_bera.xml'
        risques = bu.parse()
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
    with patch('utils.bulletin.Bulletin.path_file', new_callable=PropertyMock) as a:
        a.return_value = 'tests/invalid_tag_bera.xml'
        with pytest.raises(ET.ParseError) as e_info:
            risques = bu.parse()
    with patch('utils.bulletin.Bulletin.path_file', new_callable=PropertyMock) as a:
        a.return_value = 'tests/invalid_attribute_bera.xml'
        with pytest.raises(ET.ParseError) as e_info:
            risques = bu.parse()



    # mocker.patch('xml.etree.ElementTree.parse', new_callable=mock_et_parse)
    # bu.parse()

    #
    # def parse(self):
    #     root = ET.parse('app/tmp_bera.xml').getroot()
    #     self.cartouche_risque = root[0].find('CARTOUCHERISQUE')
    #     self.risques = self.cartouche_risque[0].attrib
    #     logger.debug(self.risques)
    #
    # def append_csv(self):
    #     # Removing comma as we will save the file as a csv
    #     risques = list(map(lambda x: x.replace(',', '-'), self.risques.values()))
    #     return [self.jour_key, self.massif, *risques]
