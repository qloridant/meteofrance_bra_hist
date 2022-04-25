MASSIFS = ['CHABLAIS', 'MONT-BLANC', 'ARAVIS', 'CHARTREUSE', 'BELLEDONNE', 'GRANDES-ROUSSES', 'VERCORS', 'OISANS', 'HAUTE-TARENTAISE', 'BEAUFORTAIN', 'BAUGES', 'VANOISE', 'HAUTE-MAURIENNE', 'MAURIENNE', 'UBAYE', 'HAUT-VAR_HAUT-VERDON', 'THABOR', 'PELVOUX', 'QUEYRAS', 'CHAMPSAUR', 'DEVOLUY', 'EMBRUNAIS-PARPAILLON', 'MERCANTOUR', 'CINTO-ROTONDO', 'RENOSO-INCUDINE', 'ANDORRE', 'ORLU__ST_BARTHELEMY', 'HAUTE-ARIEGE', 'COUSERANS', 'LUCHONNAIS', 'AURE-LOURON', 'HAUTE-BIGORRE', 'ASPE-OSSAU', 'PAYS-BASQUE', 'CERDAGNE-CANIGOU','CAPCIR-PUYMORENS']

import os

with open(f'app/data/urls_list.txt') as f:
    pdfs = f.read().splitlines()

# print(pdfs)

for massif in MASSIFS:
    pdfs_massif = [url for url in pdfs if massif in url]
    print(pdfs_massif)
    with open(f'app/data/{massif}/urls_list.txt', 'w') as f:
        pdfs_massif = '\n'.join(map(lambda x:str(x).replace(massif + '.', ''), pdfs_massif))
        f.write(pdfs_massif)
