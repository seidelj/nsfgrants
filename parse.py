import os
from bs4 import BeautifulSoup
import csv
import codecs
import re

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
XML_DIR =os.path.join(PROJECT_ROOT, '2017')

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
            row = [str(item[h]) for h in headers]
            cwriter.writerow(row)
    with open(os.path.join(PROJECT_ROOT, 'investigator.csv'),'w') as f:
        cwriter = csv.writer(f)
        headers = ['awardid'] + investigatorHeaders
        cwriter.writerow(headers)
        for item in parsed:
            for inv in item['investigator']:
                row = [item['awardid']]+[str(inv[h]) for h in investigatorHeaders]
                cwriter.writerow(row)
    with open(os.path.join(PROJECT_ROOT, 'elements.csv'), 'w') as f:
        cwriter = csv.writer(f)
        headers = ['awardid', 'code', 'text']
        cwriter.writerow(headers)
        for item in parsed:
            for elem in item['programelement']:
                row = [item['awardid']]+[str(elem[h]) for h in headers[1:]]
                cwriter.writerow(row)
    with open(os.path.join(PROJECT_ROOT, 'references.csv'), 'w') as f:
        cwriter = csv.writer(f)
        headers = ['awardid', 'code', 'text']
        cwriter.writerow(headers)
        for item in parsed:
            for elem in item['programreference']:
                row = [item['awardid']]+[str(elem[h]) for h in headers[1:]]
                cwriter.writerow(row)

    with open(os.path.join(PROJECT_ROOT, 'abstracts.csv'), 'w') as f:
        cwriter = csv.writer(f)
        headers = ['awardid', 'abstractnarration']
        cwriter.writerow(headers)
        for item in parsed:
            row = [str(item[h]) for h in headers]
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
            mainDict[key] = str(obj.value.string).encode('utf8', 'replace')
        else:
            mainDict[key] = str(obj.text.encode('utf8', 'replace'))
    mainDict['programofficer'] = str(soup.programofficer.signblockname.string.encode('utf8', 'replace'))
    mainDict['organizationcode'] = str(soup.organization.code.string)
    mainDict['organizationdirectorate'] = str(soup.organization.directorate.longname.string)
    mainDict['organizationdivision'] = str(soup.organization.division.longname.string)

    inst = soup.institution.contents
    for item in inst:
        if item:
            mainDict["institution{}".format(item.name)] = item.string
    try:
        mainDict['abstractnarration'] = str(soup.abstractnarration.string.encode('utf8', 'replace'))
    except AttributeError:
        mainDict['abstractnarration'] = ""
    mainDict['investigator'] = []
    for person in soup.find_all('investigator'):
        pdict = {}
        for header in investigatorHeaders:
            obj = getattr(person, header)
            pdict[header] = obj.string
        mainDict['investigator'].append(pdict)

    mainDict['programelement'] = []
    for e in soup.find_all('programelement'):
        edict = {}
        edict['code'] = e.code.string
        edict['text'] = e.text
        mainDict['programelement'].append(edict)

    mainDict['programreference'] = []
    for e in soup.find_all('programreference'):
        edict['code'] = e.code.string
        edict['text'] = e.text
        mainDict['programreference'].append(edict)

    return mainDict

if __name__ == "__main__":
    main()
