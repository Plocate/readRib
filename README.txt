TO DO

- installer python

- installer les bibliothèques nécessaires :
	- pdfminer
	- tkinter
	- pypdf2
	- cv2
	- pillow
	- pytesseract
	
- ... a compléter
	
- Executer le fichier readPDF.py sans argument



Fonctionnement :

- Le programme ne prend normalement que des fichiers PDF, sinon il renvoie une erreur
- Le programme essaye plusieurs techniques pour extraire les données : deux techniques qui extraient le texte encodé dans le fichier, et deux qui font de la reconnaissance optique de caractère sur les images du pdf.
- On n'arrive pas toujours à récupérer le texte du PDF, un échec arrivant la plupart du temps quand le pdf est constitué d'une image.
- La reconnaissance optique de caractère est une technologie peut précise, il peut lui arriver de ne pas reconnaître des caractères, ou de les confondre. Par exemple, on confondra un I et un l.
	Il est recommandé à l'utilisateur de vérifier le résultat obtenu.
- Lorsqu'on envoie un fichier PDF qui n'est pas un RIB, le programme ne reconnait aucune donnée, sauf peut-être dans de très rares cas ou le fichier contiendrait accidentellement des données semblables à celle d'un RIB.
- Dans les deux cas précédents, et lorsque le programme n'arrive à reconnaître aucune donnée du RIB fourni, il crée un fichier json contenant seulement le texte suivant : 
	"L'extraction des donnees a echoue. Est-ce bien un RIB ?"
- Lorsque le fichier reconnait des données du rib, il génère un fichier json au même emplacement que le PDF, avec le même titre.
- Le champ IBAN du fichier généré reconnait un code IBAN présent sur le RIB, s'il correspond au format parmi ceux de 55 pays (lignes 28 à 82 dans le code). A priori il ne se trompe pas, ou très rarement.
- Le champ BIC du fichier généré reconnait un code BIC présent sur le RIB. Il reconnait deux formats, un à 8 caractères, et un à 11 caractères.
- Le champ client reconnait le nom et l'adresse du client du rib. Son fonctionnement est un peu plus imprécis. Il cherche en priorité une adresse postale française, et le nom du client ou de l'entreprise qui précède.
	S'il ne trouve pas d'adresse, il cherche un nom propre précédé de M., Mme, ou Mr, etc. Il arrive qu'il ne renvoie rien si l'extraction des données se passe mal ou si le format du RIB est trop inhabituel.
- Certains complément d'adresse sont prévus par le programme, et peuvent être reconnus. Mais il peut arriver qu'un complément d'adresse se retrouve accidentellement dans le nom du client.
- Il peut arriver que, par erreur, plusieurs clients soient trouvés. Le programme ne permet alors pas de trancher, et stock tous les clients trouvés dans une liste.
- Le champ warning peut afficher divers erreurs : lorsque plusieurs clients sont trouvés, lorsqu'aucun client n'est trouvé, lorsque l'IBAN ou le BIC ne sont pas trouvés. Plusieurs warnings peuvent être stockés dans une liste.