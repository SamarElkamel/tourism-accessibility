import mysql.connector
import json
import os

# Connexion à la base MySQL
conn = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST", "localhost"),
    user=os.getenv("MYSQL_USER", "root"),
    password=os.getenv("MYSQL_PASSWORD", ""),
    database=os.getenv("MYSQL_DATABASE", "tourismdb")
)
cursor = conn.cursor(dictionary=True)

# Récupération des données depuis MySQL
cursor.execute("SELECT * FROM hebergements")
hebergements = cursor.fetchall()

# Calcul proportion d'accessibilité globale
total = len(hebergements)
accessible_count = sum(1 for h in hebergements if h['accessibilite'] == "Oui")
proportion_globale = (accessible_count / total) * 100 if total else 0

# Nombre d'hébergements par code postal et proportion accessibles par code postal
par_code_postal = {}
for h in hebergements:
    cp = h['code_postal'] if h['code_postal'] else "Unknown"
    if cp not in par_code_postal:
        par_code_postal[cp] = {'total': 0, 'accessible': 0}
    par_code_postal[cp]['total'] += 1
    if h['accessibilite'] == "Oui":
        par_code_postal[cp]['accessible'] += 1

# Calcul proportion accessible par code postal
for cp, data in par_code_postal.items():
    data['proportion_accessible'] = (data['accessible'] / data['total'])*100 if data['total'] else 0

# Top 5 communes les plus accessibles (avec plus de 2 hébergements pour éviter les biais)
communes = {}
for h in hebergements:
    commune = h['commune'] if h['commune'] else "Unknown"
    if commune not in communes:
        communes[commune] = {'total': 0, 'accessible': 0}
    communes[commune]['total'] += 1
    if h['accessibilite'] == "Oui":
        communes[commune]['accessible'] += 1

# Calcul proportion accessible par commune
for c, data in communes.items():
    data['proportion_accessible'] = (data['accessible'] / data['total'])*100 if data['total'] else 0

top_5_communes = sorted(communes.items(), key=lambda x: x[1]['proportion_accessible'], reverse=True)[:5]

# Mini-algorithme : Détection des communes avec faible accessibilité (<50%)
communes_faible_accessibilite = {c: data for c, data in communes.items() if data['proportion_accessible'] < 50}

# Affichage console
print(" Top 5 communes les plus accessibles :")
for c, data in top_5_communes:
    print(f"{c}: {data['proportion_accessible']:.1f}% d'hébergements accessibles")

print(f" Proportion globale d'hébergements accessibles : {proportion_globale:.1f}%")

print(" Nombre d'hébergements par code postal :")
for cp, data in par_code_postal.items():
    print(f"{cp}: {data['total']} hébergements, {data['proportion_accessible']:.1f}% accessibles")

print("\n Communes avec faible accessibilité (<50%) :")
for c, data in communes_faible_accessibilite.items():
    print(f"{c}: {data['proportion_accessible']:.1f}% d'hébergements accessibles")

# Création du dossier datavis s'il n'existe pas
os.makedirs("dataviz", exist_ok=True)

# Export pour dataviz
data_for_viz = {
    "global_accessibility": round(proportion_globale, 1),
    "par_code_postal": par_code_postal,
    "top_5_communes": top_5_communes,
    "communes_faible_accessibilite": communes_faible_accessibilite
}

with open("dataviz/data_for_viz.json", "w", encoding="utf-8") as f:
    json.dump(data_for_viz, f, ensure_ascii=False, indent=4)

print("✅ Données traitées et exportées pour dataviz (datavis/data_for_viz.json)")
