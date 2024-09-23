#!/usr/bin/python3

import xlsxwriter

# Crée un classeur et une feuille de calcul
workbook = xlsxwriter.Workbook('exemple_sum.xlsx')
worksheet = workbook.add_worksheet()

# Ajoute des données dans les cellules
worksheet.write('A1', 10)
worksheet.write('A2', 20)
worksheet.write('A3', 30)
# data = ['Nom', 'Âge', 'Ville', 'Pays']
data = [8,5,4,0]
worksheet.write_row('A4', data)
# Ajoute une formule SUM (fonction en anglais) dans la cellule A4
worksheet.write_formula('A5', '=SUM(A1:A4)')
# workbook.read_only_recommended()

# Ferme le classeur
workbook.close()
