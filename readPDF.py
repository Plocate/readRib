# -*-coding:Utf-8 -*

import PyPDF2
import struct
from PyPDF2 import PdfFileReader
import time
import os
from math import floor
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO
import json
from Tkinter import *
from tkFileDialog import askopenfilename
from PIL import Image
import pytesseract
import cv2
import sys



FILETYPES = [("PDF", "*.pdf")]


#Formats des differents IBAN selon les pays (séparés par des |)
casPays = ("AL\d{10}[0-9A-Z]{16}|"
           + "AD\d{10}[0-9A-Z]{12}|"
           + "AT\d{18}|"
           + "BH\d{2}[A-Z]{4}[0-9A-Z]{14}|"
           + "BE\d{14}|"
           + "BA\d{18}|"
           + "BG\d{2}[A-Z]{4}\d{6}[0-9A-Z]{8}|"
           + "HR\d{19}|"
           + "CY\d{10}[0-9A-Z]{16}|"
           + "CZ\d{22}|"
           + "DK\d{16}|"
           + "FO\d{16}|"
           + "GL\d{16}|"
           + "DO\d{2}[0-9A-Z]{4}\d{20}|"
           + "EE\d{18}|"
           + "FI\d{16}|"
           + "FR\d{12}[0-9A-Z]{11}\d{2}|"
           + "GE\d{2}[A-Z]{2}\d{16}|"
           + "DE\d{20}|"
           + "GI\d{2}[A-Z]{4}[0-9A-Z]{15}|"
           + "GR\d{9}[0-9A-Z]{16}|"
           + "HU\d{26}|"
           + "IS\d{24}|"
           + "IE\d{2}[A-Z]{4}\d{14}|"
           + "IL\d{21}|"
           + "IT\d{2}[A-Z]\d{10}[0-9A-Z]{12}|"
           + "KW\d{2}[A-Z]{4}22!|"
           + "LV\d{2}[A-Z]{4}[0-9A-Z]{13}|"
           + "LB\d{6}[0-9A-Z]{20}|"
           + "LI\d{7}[0-9A-Z]{12}|"
           + "LT\d{18}|"
           + "LU\d{5}[0-9A-Z]{13}|"
           + "MK\d{5}[0-9A-Z]{10}\d{2}|"
           + "MT\d{2}[A-Z]{4}\d{5}[0-9A-Z]{18}|"
           + "MR13\d{23}|"
           + "MU\d{2}[A-Z]{4}\d{19}[A-Z]{3}|"
           + "MC\d{12}[0-9A-Z]{11}\d{2}|"
           + "ME\d{20}|"
           + "NL\d{2}[A-Z]{4}\d{10}|"
           + "NO\d{13}|"
           + "PL\d{10}[0-9A-Z]{,16}n|"
           + "PT\d{23}|"
           + "RO\d{2}[A-Z]{4}[0-9A-Z]{16}|"
           + "SM\d{2}[A-Z]\d{10}[0-9A-Z]{12}|"
           + "SA\d{4}[0-9A-Z]{18}|"
           + "RS\d{20}|"
           + "SK\d{22}|"
           + "SI\d{17}|"
           + "ES\d{22}|"
           + "SE\d{22}|"
           + "CH\d{7}[0-9A-Z]{12}|"
           + "TN59\d{20}|"
           + "TR\d{7}[0-9A-Z]{17}|"
           + "AE\d{21}|"
           + "GB\d{2}[A-Z]{4}\d{14}")


complementAdresse = "((BATIMENT|BÂTIMENT|BAT|BÂT|IMMEUBLE|CASE|ETAGE|ÉTAGE|APPARTEMENT|CHAMBRE|ESCALIER|ESC) ([A-Z]{1,4}|[0-9]{1,4}))$"
complementAdresseBis = "(batiment|bâtiment|bat|bât|immeuble|case|etage|étage|appartement|chambre|escalier|esc|BATIMENT|BÂTIMENT|BAT|BÂT|IMMEUBLE|CASE|ETAGE|ÉTAGE|APPARTEMENT|CHAMBRE|ESCALIER|ESC) ([a-z]{1,4}|[A-Z]{1,4}|[0-9]{1,4})$"

#Format des données du client qu'on espère trouver
clientParser = "((( *(\n|\r|\r\n|:)){1,2} *[A-Z0-9\-,'_][A-Z0-9\-,'_ ]*){1,4})((( *(\n|\r|\r\n)){1,4})| )( *\d+,? ([A-Z]+[ \-',])*[A-Z0-9]+((([ ]*(\n|\r|\r\n)){1,2})| (- )?) *\d{2} ?\d{3} [A-Z]+([ \-',][A-Z0-9]+)*)[ ]*(\n|\r|\n\r)"
clientParserBis = "((( *(\n|\r|\r\n|:)){1,2} *[\S][\S ]*){1,4})((( *(\n|\r|\r\n)){1,4})| )( *\d+,? ([À-ÿA-Za-z]+[ \-',])*[À-ÿA-Za-z0-9]+((([ ]*(\n|\r|\r\n)){1,2})| (- )?) *\d{2} ?\d{3} {1,5}[À-ÿA-Za-z]+([ \-',][À-ÿA-Za-z0-9]+)*)[ ]*(\n|\r|\n\r)"


#interface graphique
fenetre = Tk()
champ_label = Label(fenetre, text="Bienvenue")
json_label = Label(fenetre, text="", justify = "left")
fichier = StringVar(fenetre)
fichierLabel = Label(fenetre, textvariable = fichier)
etat = StringVar(fenetre)
etat.set("En attente d'un fichier")
etatLabel = Label(fenetre, textvariable = etat)


class Client():
    
    def __init__(self, nom, adresse):
        self.nom = nom
        self.adresse = adresse
        
    def __eq__(self, other):
        return self.nom == other.nom and self.adresse == other.adresse
    
    def __ne__(self, other):
        return not(self == other)

    def __hash__(self):
        return hash((self.nom, self.adresse))
    
class Rib():
    def __init__(self, iban, bic):
        self.iban = iban
        self.bic = bic
        self.client = []
        self.warning  = []

#Va transformer nos objets en json.
def serialize_rib(obj):
    if isinstance(obj, Rib):
        return {"iban": obj.iban,
                "bic": obj.bic,
                "client": obj.client,
                "warnings": obj.warning}
    
    if isinstance(obj, Client):
        return {"nom": obj.nom,
                "adresse": obj.adresse}
    
    raise TypeError(repr(obj) + " n'est pas sérialisable !")


#Premier technique d'extraction de texte depuis le pdf
def firstPDFExtraction(nomFichier, fp):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()
    
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching, check_extractable=True):
        interpreter.process_page(page)
    text = retstr.getvalue()
    
    device.close()
    retstr.close()
    return text


#On tente une deuxième méthode d'extraction de texte du pdf
def secondPDFExtraction(nomFichier, fp):
    pdfFile = PdfFileReader(fp)
    nPages = pdfFile.getNumPages()
    text = ""
    for i in range(0,nPages):
        s = pdfFile.getPage(i).extractText()
        if re.search("\w", s):
            success = True
        text += re.sub(r"[ ]{2,}", "\n", re.sub(r"[ ]{2}", " ", s.encode("utf-8")+"\n"))
           
    return text
    
#Troisième méthode d'extraction de texte : on commence par extraire les images du pdf
def thirdPDFExtraction(nomFichier, fp):
    #On extrait les images
    fp2 = fp.read()
    startmark = "\xff\xd8"
    startfix = 0
    endmark = "\xff\xd9"
    endfix = 2
    njpg = 0    
    i = 0
    fichiersImage = []
    while True:
        istream = fp2.find("stream", i)
        if istream < 0:
            break
        istart = fp2.find(startmark, istream, istream+20)
        if istart < 0:
            i = istream+20
            continue
        iend = fp2.find("endstream", istart)
        if iend < 0:
            raise Exception("Didn't find end of stream!")
        iend = fp2.find(endmark, iend-20)
        if iend < 0:
            raise Exception("Didn't find end of JPG!")
         
        istart += startfix
        iend += endfix
        jpg = fp2[istart:iend]
        if njpg == 0:
            jpgfile = file(nomFichier + ".jpg", "wb")
        else:
            jpgfile = file(nomFichier + str(njpg+1) + ".jpg", "wb")
        jpgfile.write(jpg)
        jpgfile.close()
        njpg += 1
        i = iend
    return ocrImage(nomFichier, njpg)

#On lit le texte trouvé sur les images du fichier avec de l'OCR
def ocrImage(nomFichier, njpg):
    
    text = ""
    for i in range(0,njpg):
        if i==0:
            nomImage = nomFichier + ".jpg"
        else:
            nomImage = nomFichier + str(i+1) + ".jpg"
            
        #  convertit l'image en nuances de gris
        image = cv2.imread(nomImage)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        #enregistre l'image sur le disque
        filename = "{}.png".format(os.getpid())
        cv2.imwrite(filename, gray)
        
        #charge l'image et lui applique l'ocr
        pytesseract.pytesseract.tesseract_cmd = 'C:/Users/admin/Desktop/pythonOcr/Tesseract-OCR/tesseract'
        text += pytesseract.image_to_string(Image.open(filename))
        #supprime l'image chargée
        os.remove(filename)
        os.remove(nomImage)
           
    return text.encode("utf-8")  



def tiff_header_for_CCITT(width, height, img_size, CCITT_group=4):
    tiff_header_struct = '<' + '2s' + 'h' + 'l' + 'h' + 'hhll' * 8 + 'h'
    return struct.pack(tiff_header_struct,
                       b'II',  # Byte order indication: Little indian
                       42,  # Version number (always 42)
                       8,  # Offset to first IFD
                       8,  # Number of tags in IFD
                       256, 4, 1, width,  # ImageWidth, LONG, 1, width
                       257, 4, 1, height,  # ImageLength, LONG, 1, lenght
                       258, 3, 1, 1,  # BitsPerSample, SHORT, 1, 1
                       259, 3, 1, CCITT_group,  # Compression, SHORT, 1, 4 = CCITT Group 4 fax encoding
                       262, 3, 1, 0,  # Threshholding, SHORT, 1, 0 = WhiteIsZero
                       273, 4, 1, struct.calcsize(tiff_header_struct),  # StripOffsets, LONG, 1, len of header
                       278, 4, 1, height,  # RowsPerStrip, LONG, 1, lenght
                       279, 4, 1, img_size,  # StripByteCounts, LONG, 1, size of image
                       0  # last IFD
                       )


def fourthPDFExtraction(nomFichier, fp):
    cond_scan_reader = PyPDF2.PdfFileReader(fp)
    text = ""
    for i in range(0, cond_scan_reader.getNumPages()):
        page = cond_scan_reader.getPage(i)
        xObject = page['/Resources']['/XObject'].getObject()
        for obj in xObject:
            if xObject[obj]['/Subtype'] == '/Image':
                if xObject[obj]['/Filter'] == '/CCITTFaxDecode':
                    
                    if xObject[obj]['/DecodeParms']['/K'] == -1:
                        CCITT_group = 4
                    else:
                        CCITT_group = 3
                    width = xObject[obj]['/Width']
                    height = xObject[obj]['/Height']
                    data = xObject[obj]._data
                    img_size = len(data)
                    
                    tiff_header = tiff_header_for_CCITT(width, height, img_size, CCITT_group)
                    img_name = nomFichier + obj[1:] + '.tiff'
                    with open(img_name, 'wb') as img_file:
                        img_file.write(tiff_header + data)
                    
                    
                    image = cv2.imread(img_name)
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]                
                    gray = cv2.medianBlur(gray, 3)
                
                    # convertit l'image en nuances de gris
                    filename = "{}.png".format(os.getpid())
                    cv2.imwrite(filename, gray)
                
                    #charge l'image et lui applique l'ocr
                    pytesseract.pytesseract.tesseract_cmd = 'C:/Users/admin/Desktop/pythonOcr/Tesseract-OCR/tesseract'
                    text += pytesseract.image_to_string(Image.open(filename)) + "\n"
                    os.remove(filename)
                    os.remove(img_name)
                    
    return text.encode('utf-8')
    



#Parse le texte recupéré pour récupérer les données voulues : l'iban, le bic, le nom du client et son adresse
def findData(text, casPays, nomFichier):
    
    def remplace(m):
        return m.group(0).replace(' ', '')
    
    #Il existe deux formats de BIC : un à 11 char, et un à 8 
    def lookforBic(matches):
        for parse in [match.group(2) for match in matches]:
            if re.search("\W+[A-Z]{4}[ -._]?[A-Z]{2}[ -._]?[A-Z0-9]{2}[ -._]?[A-Z0-9]{3}\W?", parse):
                return re.sub("[\r\n -._]","",re.findall("\W+([A-Z]{4}[ -._]?[A-Z]{2}[ -._]?[A-Z0-9]{2}[ -._]?[A-Z0-9]{3})\W?", parse)[0])
            elif re.search("\W+[A-Z]{4}[ -._]?[A-Z]{2}[ -._]?[A-Z0-9]{2}\W?", parse):
                return re.sub("[\r\n -._]","",re.findall("\W+([A-Z]{4}[ -._]?[A-Z]{2}[ -._]?[A-Z0-9]{2})\W?", parse)[0])
        return ""
    
    #Si le fichier est vide, echec de lecture, retourne false
    if not re.search("\w", text):
        return Rib("",""), False

    #Recherche l'iban en se basant sur les formats dans le monde.    
    iban = ""
    if re.search("IBAN", text):
        #recherche d'abord à proximite du mot "IBAN"
        #On est obligé d'utiliser un match pour faire un find avec de l'overlapping
        matches = re.finditer("(?=(IBAN(.{120})))", re.sub('\n|\r|(\r\n)', '', text), re.DOTALL)
        for found in [match.group(2) for match in matches]:
            if re.search(casPays, re.sub('\W', '', found)):
                iban =  re.findall(casPays, re.sub('\W', '', found))[0]              
                break
        if iban == "":
            matches = re.finditer("(?=(IBAN(.*)))", re.sub('\n|\r|(\r\n)', '', text), re.DOTALL)
            for found in [match.group(2) for match in matches]:
                if re.search(casPays, re.sub('\W', '', found)):                 
                    iban =  re.findall(casPays, re.sub('\W', '', found))[0]
                    break            
    else:
        #sinon regarde n'importe où dans le doc
        if re.search(casPays, re.compile(r"\d[0-9 ]+\d").sub(remplace, text)):
            iban =  re.findall(casPays, re.compile(r"\d[0-9 ]+\d").sub(remplace, text))[0]
    
    
    #cherche le bic
    bic = ""
    if re.search("B\.?I\.?C\.?", text):
        #premier test de proximité :
        #On est obligé d'utiliser des match pour faire un find avec de l'overlapping
        matches = re.finditer("(?=(B\.?I\.?C\.?(.{35})))", text, re.DOTALL)
        bic = lookforBic(matches)
        #Si on ne trouve pas, on cherche le plus proche jusqu'a la fin du document
        if bic == "":
            matches = re.finditer("(?=(B\.?I\.?C\.?(.*)))", text, re.DOTALL)
            bic = lookforBic(matches)
    elif re.search("SWIFT", text):
        matches = re.finditer("(?=(SWIFT(.{35})))", re.sub('\n|\r|(\r\n)', '', text), re.DOTALL)
        bic = lookforBic(matches)
        #Si on ne trouve pas, on cherche le plus proche jusqu'a la fin du document
        if bic == "":
            matches = re.finditer("(?=(SWIFT(.*)))", re.sub('\n|\r|(\r\n)', '', text), re.DOTALL)        
            bic = lookforBic(matches)
    
    rib = Rib(iban, bic)
    
 

    #Vire les mots embêtants du style "titulaire"
    text2 = text
    if re.search("Titulaire", text2):
        text2 = text2.split("Titulaire")[1]
    elif re.search("TITULAIRE", text2):
        text2 = text2.split("TITULAIRE")[1]
    elif re.search("titulaire", text2):
        text2 = text2.split("titulaire")[1]
    elif re.search("Destinataire", text2):
        text2 = text2.split("Destinataire")[1]
    elif re.search("DESTINATAIRE", text2):
        text2 = text2.split("DESTINATAIRE")[1]
    elif re.search("destinataire", text2):
        text2 = text2.split("destinataire")[1]
    elif re.search("Intitulé", text2):
        text2 = text2.split("Intitulé")[1]
    elif re.search("INTITULE", text2):
        text2 = text2.split("INTITULE")[1]
    elif re.search("intitulé", text2):
        text2 = text2.split("intitulé")[1]
    if re.search("OWNER", text2):     
        text2 = text2.split("OWNER")[1]
    elif re.search("Owner", text2):
        text2 = text2.split("Owner")[1]
    elif re.search("owner", text2):
        text2 = text2.split("owner")[1]
    if text2 != text and re.search(":", text2[:15]):
        text2 = "\n" + text2.split(":")[1]
    if re.search("Domiciliation", text2):
        text2 = text2.split("Domiciliation")[0]
    elif re.search("DOMICILIATION", text2):
        text2 = text2.split("DOMICILIATION")[0]
    elif re.search("domiciliation", text2):
        text2 = text2.split("domiciliation")[0]
        
    
    
    entreprise = ""
    adresse = ""

    #Cherche le client et son adresse
    for compte in re.findall(clientParser, text2):
        
        #supprime les retours à la ligne, les espaces au début et à la fin, et les espaces multiples, ainsi que les bouts de texte indésirables
        #sépare aussi l'adresse du nom de l'entreprise
        entreprise = re.sub(' +', ' ', re.sub('\n|\r|(\r\n)',' ',compte[0]).strip())
        adresse = re.sub(' +', ' ', re.sub('\n|\r|(\r\n)',' ',compte[8]).strip())        
        
        #Cas où on a un complément d'adresse au début de l'adresse
        if re.search(complementAdresse, re.split("(\n|\r|(\r\n))", compte[0].strip())[len(re.split("(\n|\r|(\r\n))", compte[0].strip()))-1]):
            complement = re.split("(\n|\r|(\r\n))", compte[0].strip())[len(re.split("(\n|\r|(\r\n))", compte[0].strip()))-1]
            entreprise = re.split(complement, entreprise)[0].strip()
            adresse = complement.strip() + " " + adresse
        
        #Supprime l'iban et/ou le bic s'ils sont présents
        if(bic != "" and re.search(bic, entreprise)):
            entreprise = entreprise.split(bic)[1].strip()
        if(iban != "" and re.search(iban, entreprise)):
            entreprise = entreprise.split(iban)[1].strip()
        if(re.search(casPays, re.sub("\W", "", entreprise))):
            entreprise = re.findall("([0-9]\W*){6,}(.*)", entreprise)[0][1]
        rib.client.append(Client(entreprise, adresse))
        
    #Test un autre parsing avec des minuscules, des accents, et proche du mot titulaire (ou owner).
    if len(rib.client) == 0:
        
        for compte in re.findall(clientParserBis, text2):
        
            entreprise = re.sub(' +', ' ', re.sub('\n|\r|(\r\n)',' ',compte[0]).strip())
            adresse = re.sub(' +', ' ', re.sub('\n|\r|(\r\n)',' ',compte[8]).strip())
            
            #Cas où on a un complément d'adresse au début de l'adresse
            if re.search(complementAdresseBis, re.split("(\n|\r|(\r\n))", compte[0].strip())[len(re.split("(\n|\r|(\r\n))", compte[0].strip()))-1]):
                complement = re.split("(\n|\r|(\r\n))", compte[0].strip())[len(re.split("(\n|\r|(\r\n))", compte[0].strip()))-1]
                entreprise = re.split(complement, entreprise)[0].strip()
                adresse = complement.strip() + " " + adresse
    
            #Supprime l'iban et/ou le bic s'ils sont présents
            if(bic != "" and re.search(bic, entreprise)):
                entreprise = entreprise.split(bic)[1].strip()
            if(iban != "" and re.search(iban, entreprise)):
                entreprise = entreprise.split(iban)[1].strip()
            if(re.search(casPays, re.sub("\W", "", entreprise))):
                entreprise = re.findall("([0-9]\W*){6,}(.*)", entreprise)[0][1]
            rib.client.append(Client(entreprise, adresse))
    
    #Cas où il y a juste le nom, précédé de M., Mme, Mr. etc.
    if len(rib.client) == 0 and re.search("\s(M|Mme|MME|Mlle|MLLE|Mr|MR|Mrs|MRS|Ms|MS|Miss|MISS)\.? [a-zA-Z]+([ -][a-zA-Z]+)+\s", text2):
        adresse = ""
        entreprise = re.findall("\s((M|Mme|MME|Mlle|MLLE|Mr|MR|Mrs|MRS|Ms|MS|Miss|MISS)\.? [a-zA-Z]+([ -][a-zA-Z]+)+)\s", text2)[0][0]
        rib.client.append(Client(entreprise, adresse))
        
        
    #supprime les doublons
    rib.client= list(set(rib.client))
    
    if iban == "" or bic == "" or len(rib.client) == 0:
        return rib, False
    else:
        return rib, True
 
 
 
#Coeur de l'algo, lancé après que l'utilisateur a sélectionné un fichier à lire
def interpretation():
    #recupere et decoupe l'url choisie par l'utilisateur
    fichier.set(askopenfilename(filetypes = FILETYPES))
    success = False
    split = fichier.get().split('.')
    extension = split[len(split)-1]
    nomFichier = fichier.get()[:-len(extension)-1]
    
    text = ""
    
    #Tente la premiere technique de récupération de texte
    if(extension == 'pdf'):
        fp = open(fichier.get(), "rb")
        text = firstPDFExtraction(nomFichier, fp)
        data, test = findData(text, casPays, nomFichier)
        if not test:
            #Tente la deuxième technique de parsing de texte
            text = secondPDFExtraction(nomFichier, fp)
            data2, test = findData(text, casPays, nomFichier)
        
            if test:
                data = data2
            else:
                if data.iban == "" and data2.iban == "" and data.bic == "" and data2.bic == "" and len(data.client) == 0 and len(data2.client) == 0:
                    #Troisième méthode : le texte est peut-être dans les images ?
                    text = thirdPDFExtraction(nomFichier, fp)
                    data, test = findData(text, casPays, nomFichier)
                    if data.iban == "" and data.bic == "" and len(data.client) == 0:
                        text = fourthPDFExtraction(nomFichier, fp)
                        data, test = findData(text, casPays, nomFichier)
                        if data.iban == "" and data.bic == "" and len(data.client) == 0:
                            erreur = "L'extraction des donnees a echoue. Est-ce bien un RIB ?"
                            print("Fini ! Données non-trouvées")
                            with open(nomFichier + ".json", 'w') as jsonFile:
                                json.dump(erreur, jsonFile, indent=4)
                                jsonFile.close()
                                etat.set("Données non-trouvées")
                        else:
                            test = True
                    else:
                        test = True
                else:
                    if data.iban == "" and data2.iban != "":
                        data.iban = data2.iban
                    if data.bic == "" and data2.bic != "":
                        data.bic = data2.bic
                    if len(data.client) == 0 and len(data2.client) > 0:
                        data.client = data2.client
                    test= True
                        
        if test:
            #Gestion d'infos non-trouvées
            if data.iban == "":
                data.warning.append("Iban non-trouve")
            if data.bic == "":
                data.warning.append("Bic non-trouve")
            if len(data.client) == 0:
                data.warning.append("Details du client non-trouve.") 
            elif len(data.client) > 1:
                data.warning.append(str(len(rib.client)) + " clients potentiels trouves.")      
        
        
            #Crée un fichier Json et stocke les données dedans
            with open(nomFichier + ".json", 'w') as jsonFile:
                json.dump(data, jsonFile, indent=4, default=serialize_rib)
                jsonFile.close()
                etat.set("Fichier Json généré")        
        
        fp.close()        
                
        
    else:
        etat.set("Erreur : format de fichier non-géré")
        erreur = "Format de fichier non-géré : un pdf est nécessaire."
        print(erreur)
        
        
def printjson():
    nomFichier = fichier.get()
    if(nomFichier[-4:] == ".pdf"):
        split = nomFichier.split('.')
        extension = split[len(split)-1]
        nomFichier = fichier.get()[:-len(extension)-1] + ".json"
        with open(nomFichier, 'r') as myfile:
            lines = myfile.readlines()
        text = ""
        for l in lines:
            text += l + "\n"
        json_label['text'] = text        
        
    
    
 
#Affiche l'interface
bouton = Button(fenetre, text='Charger', command=interpretation)
boutonPrint = Button(fenetre, text='Afficher', command=printjson)
champ_label.pack()
fichierLabel.pack()
bouton.pack()
etatLabel.pack()
boutonPrint.pack()
json_label.pack()

fenetre.mainloop()