import os
from bs4 import BeautifulSoup
import csv
import codecs

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
XML_DIR =os.path.join(PROJECT_ROOT, 'xml')

mainHeaders = [
    'awardtitle', 'awardeffectivedate', 'awardexpirationdate',
    'awardamount', 'awardinstrument', 'minamdletterdate',
    'maxamdletterdate', 'arraamount', 'awardid'
]

institutionHeaders = [
    'name', 'cityname', 'zipcode', 'phonenumber', 'streetaddress',
    'countryname', 'statename', 'statecode',
]

investigatorHeaders = [
    'firstname', 'lastname', 'emailaddress', 'startdate', 'enddate', 'rolecode'
]

def main():
    xmlFiles = os.listdir(XML_DIR)
    parsed = []
    for filename in xmlFiles:
        if "DS_Store" in filename:
            continue
        soup = make_soup(filename)
        #count_tags(soup, 'institution')
        parsed.append(parse_soup(soup))
    write_csv(parsed)

def write_csv(parsed):
    with open(os.path.join(PROJECT_ROOT, 'main.csv'),'w') as f:
        cwriter = csv.writer(f)
        headers = mainHeaders + ['programofficer', 'organizationcode',
            'organizationdirectorate', 'organizationdivision'
        ] + ['institution{}'.format(x) for x in institutionHeaders]
        cwriter.writerow(headers)
        for item in parsed:
            row = [item[h] for h in headers]
            cwriter.writerow(row)


def count_tags(soup, tag):
    print len(soup.find_all(tag))

def make_soup(filename):
    doc = open(os.path.join(XML_DIR,filename))
    return BeautifulSoup(doc, 'lxml')

def parse_soup(soup):
    mainDict = {}
    aID = soup.awardid.text
    for h in mainHeaders:
        key = h.replace('.value','')
        obj = getattr(soup, key)
        if "awardinstrument" in h:
            mainDict[key] = str(obj.value.text)
        else:
            mainDict[key] = codecs.utf_8_decode(obj.text.encode('utf-8'))
    mainDict['programofficer'] = str(soup.programofficer.signblockname)
    mainDict['organizationcode'] = str(soup.organization.code.text)
    mainDict['organizationdirectorate'] = soup.organization.directorate.longname.text
    mainDict['organizationdivision'] = soup.organization.longname.text

    inst = soup.institution.contents
    for item in inst:
        if item:
            mainDict["institution{}".format(item.name)] = item.string
    mainDict['abstractnarration'] = soup.abstractnarration.text
    mainDict['investigator'] = []
    for person in soup.find_all('investigator'):
        pdict = {}
        for header in investigatorHeaders:
            obj = getattr(person, header)
            pdict[header] = obj.text
        mainDict['investigator'].append(pdict)

    mainDict['programelement'] = []
    for e in soup.find_all('programelement'):
        edict = {}
        edict['code'] = e.code.string
        edict['text'] = e.text
        mainDict['programelement'].append(edict)

    mainDict['programreference'] = []
    for e in soup.find_all('programreference'):
        edict = {}
        edict['code'] = e.code.string
        edict['text'] = e.text
        mainDict['programreference'].append(edict)

    return mainDict

if __name__ == "__main__":
    main()
