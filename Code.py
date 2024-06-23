import tkinter as tk
from tkinter import ttk, simpledialog
from PIL import Image, ImageTk
import yfinance as yf
import matplotlib.pyplot as plt
import os
import uuid
from datetime import datetime

def importer_liste_surveillance() :
    with open("Liste_surveillance.txt", 'r') as f :
        lignes = f.readlines()
        liste_de_strings = [ligne.strip() for ligne in lignes]
    return liste_de_strings
    
def ajouter_liste_surveillance(symbole) :
    with open("Liste_surveillance.txt", 'a') as f:
        f.write(f"{symbole}\n")
    return

def actualiser_cours(symboles) :
    for symbole in symboles :
        supprimer_fichier("Données/"+symbole+".png")
        historique = yf.Ticker(symbole).history(period='1y')  # Vous pouvez ajuster la période selon vos besoins
        couleurs , date , prix= [] , list(historique.index) , list(historique['Close'])
        for k in range(len(prix) - 1) :
            if prix[k] < prix[k+1] :
                couleurs.append("green")
            else :
                couleurs.append("red")
            plt.plot([date[k],date[k+1]],[prix[k],prix[k+1]], color=couleurs[k])
        plt.title("Cours de l'action "+symbole)
        plt.xlabel("Date")
        plt.ylabel("Prix de clôture")
        plt.grid(False)
        plt.savefig("Données/"+symbole+".png")
        plt.close()
        print("Le cours de",symbole,"a été actualisé.")
    return
    
def supprimer_fichier(chemin_fichier) :
    try:
        os.remove(chemin_fichier)
        print(f"Le fichier {chemin_fichier} a été supprimé avec succès.")
    except FileNotFoundError:
        print(f"Le fichier {chemin_fichier} n'a pas été trouvé.")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")

def supprimer_liste_surveillance(symbole):
    # Lire le contenu du fichier
    with open("Liste_surveillance.txt", 'r') as fichier:
        lignes = fichier.readlines()
    # Rechercher la ligne à supprimer
    lignes_a_garder = [ligne for ligne in lignes if symbole not in ligne]
    # Réécrire le fichier avec les lignes restantes
    with open("Liste_surveillance.txt", 'w') as fichier:
        fichier.writelines(lignes_a_garder)

def importer_transactions():
    chemin_fichier , transactions= "Transactions.txt" , []
    with open(chemin_fichier, 'r') as fichier:
        for ligne in fichier:
            # Supprimer les espaces blancs autour des éléments et diviser par virgule
            transaction_data = [element.strip() for element in ligne.split(',')]
            
            # Assurez-vous qu'il y a suffisamment d'éléments dans la ligne
            if len(transaction_data) == 5:
                transactions.append(transaction_data)
            else:
                print(f"Ignorer la ligne mal formatée : {ligne}")
    return transactions

def ajouter_transaction(transaction_id, date, quantité,cours, symbole) :
    with open("Transactions.txt", 'a') as f:
        f.write(transaction_id+","+date+","+str(quantité)+","+str(cours)+","+symbole+"\n")
    print(f"Transaction avec l'identifiant {transaction_id} ajoutée.")
    return

def supprimer_transactions(identifiant):
    chemin_fichier = "Transactions.txt"
    transactions = []

    
    # Lire les transactions existantes
    with open(chemin_fichier, 'r') as fichier:
        for ligne in fichier:
            transaction_data = [element.strip() for element in ligne.split(',')]
            if len(transaction_data) == 5:
                transactions.append(transaction_data)
            else:
                print(f"Ignorer la ligne mal formatée : {ligne}")
    
    # Identifier l'index de la transaction à supprimer
    index_a_supprimer = None
    for i, transaction in enumerate(transactions):
        if transaction[0] == identifiant:
            index_a_supprimer = i
            break
        
    # Supprimer la transaction de la liste
    if index_a_supprimer is not None:
        del transactions[index_a_supprimer]
        print(f"Transaction avec l'identifiant {identifiant} supprimée.")
    else:
        print(f"Identifiant {identifiant} non trouvé. Aucune transaction supprimée.")

    # Réécrire le fichier avec la liste mise à jour
    with open(chemin_fichier, 'w') as fichier:
        for transaction in transactions:
            ligne = ','.join(transaction) + '\n'
            fichier.write(ligne)

def convert_pandas_timestamp_to_date(pd_timestamp):
    # Extraire le timestamp de l'objet pandas Timestamp
    timestamp = pd_timestamp.timestamp()

    # Convertir le timestamp en objet datetime
    dt_object = datetime.fromtimestamp(timestamp)

    # Formater la date selon le format requis (dd/mm/yyyy)
    formatted_date = dt_object.strftime("%d/%m/%Y")

    return formatted_date

def min_dates(date_str1, date_str2, format_str='%d/%m/%Y'):
    date1 = datetime.strptime(date_str1, format_str)
    date2 = datetime.strptime(date_str2, format_str)
    if date1 < date2:
        return date_str1
    else :
        return date_str2

def date_dans_tous_cours(date,dictionnaire) :
    for action in dictionnaire :
        if date not in dictionnaire[action][0] :
            return False
    return True

def valeur_action(cours,date) :
    k = 0
    while cours[0][k] != date :
        k += 1
    return cours[1][k]

def graphique_portefeuille() : # On suppose que les transactions sont classée par ordre croissant de temps
    supprimer_fichier("Données/Portefeuille.png")
    données , transactions , portefeuille = {} , importer_transactions() , []
    date_min , data = transactions[0][1] , yf.download(transactions[0][4], period="max")
    dates = list(data.index)
    for i in range(len(dates)) :
        if min_dates(date_min,convert_pandas_timestamp_to_date(dates[i])) == date_min :
            break
    données[transactions[0][4]] = [list(data.index)[i::],list(data["Close"])[i::]]
    portefeuille.append((transactions[0][4],transactions[0][2]))
    k , abscisses , ordonées = 0 , [] , []
    liste = données[transactions[0][4]][0]
    transactions.pop(0)
    for date in liste :
        à_pop = []
        for k in range(len(transactions)) :
            if min_dates(convert_pandas_timestamp_to_date(date),transactions[k][1]) == transactions[k][1] :
                data = yf.download(transactions[k][4], period="max")
                dates = list(data.index)
                for i in range(len(dates)) :
                    if min_dates(date_min,convert_pandas_timestamp_to_date(dates[i])) == date_min :
                        break
                données[transactions[k][4]] = [list(data.index)[i::],list(data["Close"])[i::]]
                portefeuille.append((transactions[k][4],transactions[k][2]))
                à_pop.append(k)
        sorted(à_pop,reverse=True)
        for indice in à_pop :
            transactions.pop(indice)
        if date_dans_tous_cours(date,données) :
            abscisses.append(date)
            somme = 0
            for action in portefeuille :
                somme += float(action[1]) * valeur_action(données[action[0]],date)
            ordonées.append(somme)
    plt.plot(abscisses,ordonées)
    plt.title("Valeur du portefeuille d'actions")
    plt.xlabel("Date")
    plt.ylabel("Prix de clôture")
    plt.grid(False)
    plt.savefig("Données/Portefeuille.png")
    plt.close()
    print("Le graphique en camembert a été actualisé.")
    return

def graphique_camembert():
    supprimer_fichier("Données/Camembert.png")
    transactions = importer_transactions()
    dictionnaire , actions , valeurs = {} , [] ,[]
    for transaction in transactions :
        if transaction[4] in dictionnaire :
            dictionnaire[transaction[4]]  += float(transaction[2])
        else :
            dictionnaire[transaction[4]] = float(transaction[2])
    for action in dictionnaire :
        if dictionnaire[action] != 0 :
            valeurs.append(yf.Ticker(action).info["ask"]*dictionnaire[action])
            actions.append(action)
    plt.title("Répartition en actions du portefeuille")
    plt.pie(valeurs, labels=actions, autopct='%1.1f%%')
    plt.savefig("Données/Camembert.png")
    plt.close()
    print("Le portefeuille a été actualisé.")
    return

def somme() :
    transactions , somme_début , somme_fin = importer_transactions() , 0 , 0
    for transaction in transactions :
        somme_début += float(transaction[3]) * float(transaction[2])
        somme_fin += float(transaction[2]) * yf.Ticker(transaction[4]).info["ask"]
    return (somme_début,somme_fin)

class InterfaceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Application de gestion d'un portefeuille d'actions")

        # Déclaration et initialisation de l'attribut 'noms'
        self.noms = importer_liste_surveillance()

        # Créer un Notebook pour les onglets
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)

        # Onglet "Cours des actions"
        self.cours_des_actions_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.cours_des_actions_tab, text='Cours des actions')
        self.configure_cours_des_actions_tab()

        # Onglet "Historique"
        self.historique_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.historique_tab, text='Historique des transactions')
        self.configure_historique_tab()

        # Onglet "Portefeuille"
        self.portefeuille_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.portefeuille_tab, text='Portefeuille')
        self.configure_portefeuille_tab()

    def configure_cours_des_actions_tab(self):
        # Mettez ici la configuration spécifique à l'onglet "Cours des actions"

        # Menu déroulant pour la sélection du nom
        self.nom_var = tk.StringVar()
        self.nom_var.set(self.noms[0])  # Définir la valeur par défaut
        self.nom_menu = ttk.Combobox(self.cours_des_actions_tab, textvariable=self.nom_var, values=self.noms)
        self.nom_menu.grid(row=0, column=0, padx=10, pady=10)

        # Bouton d'ajout de nouveau nom
        self.bouton_ajout = tk.Button(self.cours_des_actions_tab, text="Ajouter action", command=self.ajouter_nom)
        self.bouton_ajout.grid(row=0, column=1, padx=10, pady=10)

        # Bouton pour retirer un nom
        self.bouton_retirer = tk.Button(self.cours_des_actions_tab, text="Retirer action sélectionnée", command=self.retirer_nom)
        self.bouton_retirer.grid(row=0, column=2, padx=10, pady=10, sticky='ew')

        # Zone d'affichage d'image
        self.image_label = tk.Label(self.cours_des_actions_tab)
        self.image_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        self.nom_var.trace_add("write", self.maj_image)

    def configure_historique_tab(self):
        # Bouton pour ajouter une transaction
        self.bouton_ajouter_transaction = tk.Button(self.historique_tab, text="Ajouter Transaction", command=self.ajouter_transaction)
        self.bouton_ajouter_transaction.grid(row=0, column=1, padx=10, pady=10, sticky='e')
        # Bouton pour supprimer une transaction
        self.bouton_supprimer_transaction = tk.Button(self.historique_tab, text="Supprimer Transaction", command=self.supprimer_transaction)
        self.bouton_supprimer_transaction.grid(row=0, column=2, padx=10, pady=10, sticky='e')
        # Treeview pour afficher le tableau
        self.treeview = ttk.Treeview(self.historique_tab, columns=('Date', 'Quantité' , 'Cours', 'Symbole'))
        self.treeview.heading('Date', text='Date')
        self.treeview.heading('Quantité', text='Quantité')
        self.treeview.heading('Cours', text='Cours')
        self.treeview.heading('Symbole', text='Symbole')

        # Réglages supplémentaires pour résoudre le problème de colonne blanche vide
        self.treeview.column('#0', width=0, stretch=tk.NO)
        transactions = importer_transactions()
        for transaction in transactions :
            self.ajouter_transaction_dans_tableau(transaction[0],transaction[1],transaction[2],transaction[3],transaction[4])
        self.treeview.grid(row=1, column=0, columnspan=4, padx=10, pady=10)

    def ajouter_transaction_dans_tableau(self, transaction_id ,date, quantité,cours, symbole):
        self.treeview.insert('', 'end', iid=transaction_id, values=(date, quantité,cours, symbole))

    def ajouter_transaction(self):
        # Boîte de dialogue pour obtenir toutes les informations de la transaction
        jour = simpledialog.askinteger("Ajouter Transaction", "Entrez le jour:", parent=self.root)
        mois = simpledialog.askinteger("Ajouter Transaction", "Entrez le mois:", parent=self.root)
        annee = simpledialog.askinteger("Ajouter Transaction", "Entrez l'année:", parent=self.root)
        quantité = simpledialog.askfloat("Ajouter Transaction", "Entrez la quantité :", parent=self.root)
        cours = simpledialog.askfloat("Ajouter Transaction", "Entrez le cours :", parent=self.root)
        symbole = simpledialog.askstring("Ajouter Transaction", "Entrez le symbole:", parent=self.root)
        transaction_id = str(uuid.uuid4())
        self.ajouter_transaction_dans_tableau(transaction_id, f"{jour}/{mois}/{annee}", quantité,cours, symbole)
        ajouter_transaction(transaction_id,f"{jour}/{mois}/{annee}", quantité,cours, symbole)

    def supprimer_transaction(self):
        # Récupérer l'identifiant de la transaction sélectionnée
        selection = self.treeview.selection()
        if selection:
            transaction_id = selection[0]

            supprimer_transactions(transaction_id)

            # Effacer tous les éléments actuels du tableau
            for item in self.treeview.get_children():
                self.treeview.delete(item)

            # Actualiser le tableau avec les transactions mises à jour
            transactions = importer_transactions()  # Assurez-vous d'importer les transactions correctes
            for transaction in transactions:
                self.treeview.insert('', 'end', iid=transaction[0], values=(transaction[1], transaction[2], transaction[3], transaction[4]))

            # Sélectionner le premier élément dans le tableau (s'il y en a)
            if transactions:
                self.treeview.selection_set(transactions[0][0])

    def configure_portefeuille_tab(self):
        # Label pour la première image
        chemin_image1 = "Données/Portefeuille.png"
        image1 = Image.open(chemin_image1)
        image1 = ImageTk.PhotoImage(image1)
        self.label_image1 = tk.Label(self.portefeuille_tab, image=image1)
        self.label_image1.image = image1
        self.label_image1.pack(padx=10, pady=10)

        # Label pour la deuxième image
        chemin_image2 =  "Données/Camembert.png"
        image2 = Image.open(chemin_image2)
        image2 = ImageTk.PhotoImage(image2)
        self.label_image2 = tk.Label(self.portefeuille_tab, image=image2)
        self.label_image2.image = image2
        self.label_image2.pack(padx=10, pady=10)

        # Label pour la première phrase prédéfinie
        valeurs = somme()
        phrase1 = "Montant total du portefeuille : "+ str(round(valeurs[0],2)) + " $"
        self.label_phrase1 = tk.Label(self.portefeuille_tab, text=phrase1)
        self.label_phrase1.pack(padx=10, pady=10)

        # Label pour la deuxième phrase prédéfinie
        phrase2 = "Performance du portefeuille : " + str(round((1-valeurs[1]/valeurs[0])*-100,2)) + " %"
        self.label_phrase2 = tk.Label(self.portefeuille_tab, text=phrase2)
        self.label_phrase2.pack(padx=10, pady=10)

    def maj_image(self, *args):
        nom_selectionne = self.nom_var.get()
        chemin_image = "Données/" + nom_selectionne + ".png"
        try:
            # Charger l'image et l'afficher
            image = Image.open(chemin_image)
            image = ImageTk.PhotoImage(image)
            self.image_label.config(image=image)
            self.image_label.image = image
        except FileNotFoundError:
            # Gérer le cas où l'image n'est pas trouvée
            self.image_label.config(image=None)

    def ajouter_nom(self):
        nouveau_nom = tk.simpledialog.askstring("Ajouter action", "Entrez le nom de l'action")
        ajouter_liste_surveillance(nouveau_nom)
        actualiser_cours([nouveau_nom])
        if nouveau_nom:
            self.noms.append(nouveau_nom)
            self.nom_menu['values'] = self.noms

    def retirer_nom(self):
        nom_selectionne = self.nom_var.get()

        # S'assurer qu'il y a au moins un nom dans la liste
        if len(self.noms) > 1:
            # Retirer le nom sélectionné de la liste
            self.noms.remove(nom_selectionne)
            supprimer_fichier("Données/" + nom_selectionne + ".png")
            supprimer_liste_surveillance(nom_selectionne)
            # Mettre à jour la liste déroulante
            self.nom_menu['values'] = self.noms

            # Sélectionner le premier nom de la liste
            self.nom_var.set(self.noms[0])

            # Actualiser l'image avec le nouveau nom sélectionné
            self.maj_image()

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfaceApp(root)
    root.mainloop()