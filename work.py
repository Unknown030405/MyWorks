import os
from datetime import datetime
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
import csv

prepositions = {'cercare': 'di', 'provare': 'a', 'dimenticare': 'di', 'sperare': 'di', 'dire': 'di', 'raccontare': 'di',
                'chiedere': 'di',
                'domandare': 'di', 'promettere': 'di', 'riferire': 'a', 'dispiacere': 'di', 'paura': 'di',
                'temere': 'di', 'preoccuparsi': 'di',
                'cominciare': 'a', 'iniziare': 'a', 'continuare': 'a', 'finire': 'di', 'smettere': 'di',
                'concludere': 'di', 'chiedere': 'di',
                'richiedere': 'di', 'pregare': 'di', 'ordinare': 'di', 'indurre': 'a', 'credere': 'di', 'pensare': 'di',
                'dubitare': 'di',
                'rinunciare': 'a', 'fingere': 'di', 'riuscire': 'a', 'cercare': 'di', 'provare': 'a', 'osare': 'a',
                'ricordare': 'di', 'tentare': 'di'}

PAGES = 5000
# PAGES = 5


async def zero(lemma, session, num=None):
    out = []
    for page in range(1, PAGES):
        raw_response = None
        while not raw_response:
            try:
                response = await session.get(
                    'https://corpora.dipintra.it/public/run.cgi/view?q=aword%2C%5Blemma%3D"' + lemma +
                    '"%5D&q=P-3+3+1+%5Bword%3D"questo"%7Cword%3D"quello"%7Cword%3D"ciò"%7' +
                    'Cword%3D"cio%27"%7Cword%3D"lo"%7Cword%3D"l%27"%5D;fromp=' + str(
                        page) + ';corpname=itwac_full&viewmode=sen&refs=%23&lemma=' + lemma)
                raw_response = await response.text()
            except Exception as e:
                print(e)
                with open(r"logs\errors.txt", "a", encoding="utf-8") as file:
                    file.write(f"{datetime.now().strftime('%HH:%MM:%SS')} " + str(e) + "\n")

        soup = BeautifulSoup(raw_response, 'html.parser')
        phrases = soup.find_all(['span', 'i', 'b'], {'class': ('nott', 'coll nott', 'col0 coll nott')})
        a = []
        previousname = ''
        for i in range(len(phrases)):
            if phrases[i].name == previousname:
                out.append(' '.join(a))
                a = [phrases[i].get_text().strip()]
                previousname = phrases[i].name
            else:
                if phrases[i].name == 'b':
                    a.append('<' + phrases[i].get_text().strip() + '>')
                else:
                    a.append(phrases[i].get_text().strip())
                previousname = phrases[i].name
        print(f"{page / PAGES * 100}% is done in thread {num}")
    foldername = r''
    path = os.path.join(foldername, lemma + '.txt')
    with open(path, 'w', encoding="utf-8") as f:
        for line in out:
            f.write(line + '\n\n')


async def first(filename):
    with open(filename, 'r', encoding="utf-8", errors='ignore') as f:
        data = f.readlines()
    questo, quello, lo, cio = [], [], [], []
    for line in data:
        phrases = line.split(' ')
        for i in range(len(phrases)):
            word = phrases[i]
            if '<' in word:
                if i >= 3:
                    for n in range(-3, -1):
                        if phrases[i + n] == 'lo' or phrases[i + n] == "l'":
                            lo.append(line)
                        elif phrases[i + n] == "ci" or phrases[i + n] == "c'":
                            lo.append(line)
                        elif phrases[i + n] == "ne" or phrases[i + n] == "n'":
                            lo.append(line)
                    for n in range(2):
                        if n + i >= len(phrases):
                            break
                        elif phrases[i + n] == 'questo':
                            questo.append(line)
                        elif phrases[i + n] == 'quello':
                            quello.append(line)
                else:
                    for n in range(-i, -1):
                        if phrases[i + n] == 'lo' or phrases[i + n] == "l'":
                            lo.append(line)
                        elif phrases[i + n] == "cio'" or phrases[i + n] == 'ciò':
                            cio.append(line)
                        elif phrases[i + n] == "ci" or phrases[i + n] == "c'":
                            lo.append(line)
                        elif phrases[i + n] == "ne" or phrases[i + n] == "n'":
                            lo.append(line)
                    for n in range(2):
                        if n + i >= len(phrases):
                            break
                        elif phrases[i + n] == 'questo':
                            questo.append(line)
                        elif phrases[i + n] == 'quello':
                            quello.append(line)
    return questo, quello, lo, cio


async def second(filename, questo, quello, lo, cio, verbasfilename):
    verb = os.path.splitext(filename)[0]
    global prepositions
    with open(filename, 'w', encoding="utf-8") as f:
        f.write('QUESTO\n\n\n\n')
        for line in questo:
            x = re.findall(re.compile(r"(?:.)*>(?: a | di | )questo (?:.)*"), line.lower())
            if x != []:
                f.write(x[0] + '\n')
        f.write('\n\n\nQUELLO\n\n\n\n')
        for line in quello:
            x = re.findall(re.compile(r"(?:.)*> (?:a |di )*quello (?:.)*"), line.lower())
            if x != []:
                f.write(x[0] + '\n')
        f.write('\n\n\nLO\n\n\n\n')
        for line in lo:
            a = prepositions.get(verb, 'no')
            if a == 'no':
                x = re.findall(re.compile(r"(?:.)* lo <(?:.)*"), line.lower())
                if x != []:
                    f.write(x[0] + '\n')
                x = re.findall(re.compile(r"(?:.)* l' <(?:.)*"), line.lower())
                if x != []:
                    f.write(x[0] + '\n')
                x = re.findall(re.compile(r"(?:.)* l' (?:ha|av|er|eb|è |e' )+(?:.)* <(?:.)*"), line.lower())
                if x != []:
                    f.write(x[0] + '\n')
            elif a == 'a':
                x = re.findall(re.compile(r"(?:.)* ci <(?:.)*"), line.lower())
                if x != []:
                    f.write(x[0] + '\n')
                x = re.findall(re.compile(r"(?:.)* c' (?:ha|av|er|eb|è |e' )+(?:.)* <(?:.)*"), line.lower())
                if x != []:
                    f.write(x[0] + '\n')
            elif a == 'di':
                x = re.findall(re.compile(r"(?:.)* ne <(?:.)*"), line.lower())
                if x != []:
                    f.write(x[0] + '\n')
                x = re.findall(re.compile(r"(?:.)* n' (?:ha|av|er|eb|è |e' )+(?:.)* <(?:.)*"), line.lower())
                if x != []:
                    f.write(x[0] + '\n')
            else:
                print(verb, a)
        f.write('\n\n\nCIO\n\n\n\n')
        for line in cio:
            x = re.findall(re.compile(r"(?:.)*>(?: a | di | )cio' (?:.)*"), line.lower())
            if x != []:
                f.write(x[0] + '\n')
            x = re.findall(re.compile(r"(?:.)*>(?: a | di | )ciò (?:.)*"), line.lower())
            if x != []:
                f.write(x[0] + '\n')


async def third(num=None):
    foldername = r'.'
    files = os.listdir(foldername)
    for item in files:
        if item != 'res' and item != 'work.py' and item[-3::] == "txt":
            path = os.path.join(foldername, item)
            print(path)
            a, b, c, d = await first(path)
            newpath = os.path.join(foldername, 'res')
            newpath = os.path.join(newpath, item)
            newfile = os.path.splitext(newpath)[0] + 'done' + os.path.splitext(newpath)[1]
            await second(newfile, a, b, c, d, item)
            print('done with ' + item)
    print('almost completely done')


async def forth(session, left=0, right=-1, num=None):
    all_verbs = ['potere', 'volere', 'dovere', 'bisogna', 'sentire', 'capire', 'sapere', 'realizzare', 'dimenticare',
                 'vedere', 'desiderare', 'sperare', 'confidare', 'dire', 'raccontare', 'informare', 'chiedere',
                 'domandare', 'promettere', 'riferire', 'annunciare', 'immaginare', 'dispiacere', 'paura', 'temere',
                 'preoccuparsi', 'cominciare', 'iniziare', 'continuare', 'finire', 'smettere', 'concludere', 'chiedere',
                 'richiedere', 'pregare', 'ordinare', 'indurre', 'sembrare', 'credere', 'pensare', 'dubitare',
                 'rinunciare', 'supporre', 'fingere', 'riuscire', 'cercare', 'provare', 'osare', 'ricordare', 'tentare']
    # verbs = ['dire', 'credere', 'provare']
    verbs = all_verbs[left:right]
    print(verbs)
    for verb in verbs:
        await zero(verb, session, num=num)
        print('done with ' + verb)
    await third()


async def fifth(path, filename, name):
    with open(path, 'r', encoding='utf-8') as f:
        data = f.readlines()
    verb = os.path.splitext(filename)[0]
    verb = verb[:-4]
    print(verb)
    flag = 0
    counter = [-1, 0, 0, 0]
    for line in data:
        if line == 'QUELLO\n':
            flag = 1
        elif line == 'LO\n':
            flag = 2
        elif line == 'CIO\n':
            flag = 3
        else:
            if line != '':
                counter[flag] += 1
    counter.append(counter[0] + counter[1] + counter[2] + counter[3])
    counter.extend([counter[0] * 100 / counter[4], counter[1] * 100 / counter[4], counter[2] * 100 / counter[4],
                    counter[3] * 100 / counter[4]])
    output = [verb]
    output.extend(counter)
    with open(rf'res\output{name}.csv', 'a') as file:
        csv.writer(file).writerow(output)


async def sixth(name, num=None):
    foldername = r'.\res'
    files = os.listdir(foldername)
    with open(rf'res\output{name}.csv', 'a') as file:
        csv.writer(file).writerow(['verbs', 'questo', 'quello', 'lo', 'cio', 'sum', 'questo', 'quello', 'lo', 'cio'])
    for item in files:
        path = os.path.join(foldername, item)
        if item != 'work.py':
            await fifth(path, item, name)
