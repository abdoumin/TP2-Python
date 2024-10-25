
import csv
import random
import string

#ajouter l'entete du nombre de candidats et d'electeurs
def generate_election_csv(filename, num_voters, num_candidates):
    
    # Générer les noms des candidats (A, B, C, ...)
    candidates = list(string.ascii_uppercase[:num_candidates])
    
    # Créer les données pour le fichier CSV
    data = [['Voter'] + candidates + [f"Nombre d'élécteurs: {num_voters}", f"Nombre de candidats: {num_candidates}"]] # En-tête
    
    for i in range(1, num_voters + 1):
        voter_id = f"Voter_{i}"
        # Générer une préférence aléatoire pour chaque électeur
        preferences = random.sample(candidates, len(candidates))
        data.append([voter_id] + preferences)
    
    # Écrire les données dans le fichier CSV
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

# Générer un fichier CSV avec 10 électeurs et 5 candidats

#rendre les inputs variables
generate_election_csv('election_data.csv', 10, 5)

def lire_donnees_csv(nom_fichier):
    preferences = {}
    with open(nom_fichier, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Ignorer l'en-tête
        for row in reader:
            voter_id, *ranking = row
            preferences[voter_id] = ranking
    return preferences

def VoteUnTour(preferences):
    votes = {}
    for voter_preferences in preferences.values():
        premier_choix = voter_preferences[0]
        if premier_choix in votes:
            votes[premier_choix] += 1
        else:
            votes[premier_choix] = 1
    
    gagnant = None
    max_votes = 0
    for candidat, nombre_votes in votes.items():
        if nombre_votes > max_votes:
            gagnant = candidat
            max_votes = nombre_votes
    return gagnant

def VoteDeuxTours(preferences):
    # Premier tour
    premier_tour_votes = {}
    for voter_preferences in preferences.values():
        premier_choix = voter_preferences[0]
        if premier_choix in premier_tour_votes:
            premier_tour_votes[premier_choix] += 1
        else:
            premier_tour_votes[premier_choix] = 1
    
    # Sélectionner les deux finalistes
    finalistes = sorted(premier_tour_votes, key=premier_tour_votes.get, reverse=True)[:2]
    
    # Deuxième tour
    deuxieme_tour_votes = {finaliste: 0 for finaliste in finalistes}
    for voter_preferences in preferences.values():
        for candidat in voter_preferences:
            if candidat in finalistes:
                deuxieme_tour_votes[candidat] += 1
                break
    
    # Déterminer le gagnant
    if deuxieme_tour_votes[finalistes[0]] > deuxieme_tour_votes[finalistes[1]]:
        return finalistes[0]
    else:
        return finalistes[1]

def VoteCondorcet(preferences):
    candidats = set(preferences[next(iter(preferences))])
    duels = {(c1, c2): 0 for c1 in candidats for c2 in candidats if c1 != c2}
    
    for voter_preferences in preferences.values():
        for i, c1 in enumerate(voter_preferences):
            for c2 in voter_preferences[i+1:]:
                duels[(c1, c2)] += 1
    
    for candidat in candidats:
        if all(duels.get((candidat, autre), 0) > duels.get((autre, candidat), 0) 
               for autre in candidats if autre != candidat):
            return candidat
    return "Il n'y a pas de vainqueur de Condorcet."

def VoteBorda(preferences):
    scores = {}
    n = len(next(iter(preferences.values())))
    
    for voter_preferences in preferences.values():
        for i, candidat in enumerate(voter_preferences):
            if candidat in scores:
                scores[candidat] += n - i - 1
            else:
                scores[candidat] = n - i - 1
    
    gagnant = None
    max_score = -1
    for candidat, score in scores.items():
        if score > max_score:
            gagnant = candidat
            max_score = score
    return gagnant

# Utilisation des fonctions
preferences = lire_donnees_csv('election_data.csv')

print("Résultat Vote Un Tour:", VoteUnTour(preferences))
print("Résultat Vote Deux Tours:", VoteDeuxTours(preferences))
#Modifier si le resultat = none
print("Résultat Vote Condorcet:", VoteCondorcet(preferences))
print("Résultat Vote Borda:", VoteBorda(preferences))




# Fonction pour vérifier les conditions avec retour des pourcentages
from collections import Counter

def verifier_conditions(preferences):
    num_voters = len(preferences)
    preferences_list = list(preferences.values())
    
    different_preferences_count = 0  # Compteur de préférences différentes
    unique_preferences = []  # Stocker uniquement les préférences uniques
    
    # Parcourir chaque préférence pour identifier les uniques
    for i, preference in enumerate(preferences_list):
        is_unique = True  # Indicateur pour vérifier si la préférence est unique
        
        # Comparer cette préférence avec toutes les autres
        for j, other_preference in enumerate(preferences_list):
            if i != j and preference == other_preference:
                is_unique = False  # La préférence n'est pas unique
                break
        
        # Si la préférence est unique, on la compte
        if is_unique:
            different_preferences_count += 1
            unique_preferences.append(preference)  # Ajouter la préférence unique à la liste
            
    # Calcul du pourcentage de préférences différentes
    percent_different_preferences = (different_preferences_count / num_voters) * 100
    
    # Calcul du pourcentage de candidats en tête différents parmi les préférences uniques
    # Extraire les premiers choix des préférences uniques
    unique_heads = [pref[0] for pref in unique_preferences]
    
    # Compter la fréquence de chaque premier choix
    head_counts = Counter(unique_heads)
    most_common_head_count = head_counts.most_common(1)[0][1]  # Compte du candidat en tête le plus fréquent
    
    # Calculer le nombre de candidats en tête différents des plus fréquents
    different_head_count = sum(count for candidate, count in head_counts.items() if count < most_common_head_count)
    
    # Calcul du pourcentage de candidats en tête différents
    percent_different_head = (different_head_count / len(unique_preferences)) * 100 if len(unique_preferences) > 0 else 0
    
    return percent_different_preferences, percent_different_head


# Fonction principale pour générer l'élection et trouver un vainqueur unique
def trouver_election_avec_vainqueur_unique(filename, num_voters, num_candidates):
    iteration_count = 0  # Initialiser un compteur d'itérations
    while True:
        iteration_count += 1
        
        # Générer le fichier CSV avec des préférences aléatoires
        generate_election_csv(filename, num_voters, num_candidates)
        
        # Lire les préférences
        preferences = lire_donnees_csv(filename)
        
        # Vérifier les conditions de diversité des préférences
        percent_different_preferences, percent_different_head = verifier_conditions(preferences)
        
        # Vérifier si les pourcentages respectent les conditions
        if percent_different_preferences >= 20 and percent_different_head >= 70:
            # Calculer les vainqueurs pour chaque méthode de vote
            gagnant_un_tour = VoteUnTour(preferences)
            gagnant_deux_tours = VoteDeuxTours(preferences)
            gagnant_condorcet = VoteCondorcet(preferences)
            gagnant_borda = VoteBorda(preferences)
            
            # Vérifier si les vainqueurs sont les mêmes pour toutes les méthodes
            if (gagnant_un_tour == gagnant_deux_tours == gagnant_condorcet == gagnant_borda):
                return (preferences, gagnant_un_tour, percent_different_preferences, 
                        percent_different_head, iteration_count)

# Exemple d'utilisation pour la question 5
filename = 'election_data_question5.csv'
num_voters = 100
num_candidates = 7

# Appeler la fonction pour trouver une élection avec un vainqueur unique
preferences, gagnant_unique, percent_different_preferences, percent_different_head, iteration_count = trouver_election_avec_vainqueur_unique(filename, num_voters, num_candidates)

# Afficher les résultats



print(f"\nRésultat Vote Un Tour: {gagnant_unique}")
print(f"Résultat Vote Deux Tours: {gagnant_unique}")
print(f"Résultat Vote Condorcet: {gagnant_unique}")
print(f"Résultat Vote Borda: {gagnant_unique}")

# Conclure que les vainqueurs sont les mêmes
print(f"Le vainqueur commun de toutes les méthodes est : {gagnant_unique}")

print(f"Pourcentage de préférences différentes: {percent_different_preferences:.2f}%")
print(f"Pourcentage de préférences avec un candidat différent en tête: {percent_different_head:.2f}%")
print(f"Nombre d'itérations avant de trouver une élection valide : {iteration_count}")



# Fonction principale pour générer l'élection et trouver des vainqueurs différents
def trouver_election_avec_vainqueurs_differents(filename, num_voters, num_candidates):
    iteration_count = 0  # Initialiser un compteur d'itérations
    while True:
        iteration_count += 1
        
        # Générer le fichier CSV avec des préférences aléatoires
        generate_election_csv(filename, num_voters, num_candidates)
        
        # Lire les préférences
        preferences = lire_donnees_csv(filename)
        
        # Vérifier les conditions de diversité des préférences
        percent_different_preferences, percent_different_head = verifier_conditions(preferences)
        
        # Vérifier si les pourcentages respectent les conditions
        if percent_different_preferences >= 20 and percent_different_head >= 70:
            # Vérifier si les vainqueurs des quatre méthodes sont tous différents
            gagnant_un_tour = VoteUnTour(preferences)
            gagnant_deux_tours = VoteDeuxTours(preferences)
            gagnant_condorcet = VoteCondorcet(preferences)
            gagnant_borda = VoteBorda(preferences)
            
            # Vérifier si les vainqueurs des quatre méthodes sont tous différents
            if (gagnant_condorcet != "Il n'y a pas de vainqueur de Condorcet." and 
                gagnant_un_tour != gagnant_deux_tours and
                gagnant_un_tour != gagnant_condorcet and
                gagnant_un_tour != gagnant_borda and
                gagnant_deux_tours != gagnant_condorcet and
                gagnant_deux_tours != gagnant_borda and
                gagnant_condorcet != gagnant_borda):
                
                # Retourner toutes les valeurs attendues
                return (preferences, gagnant_un_tour, gagnant_deux_tours, 
                        gagnant_condorcet, gagnant_borda, 
                        percent_different_preferences, percent_different_head, iteration_count)

# Exemple d'utilisation pour la question 6
filename = 'election_data_question6.csv'
num_voters = 100
num_candidates = 7

preferences, gagnant_un_tour, gagnant_deux_tours, gagnant_condorcet, gagnant_borda, percent_different_preferences, percent_different_head, iteration_count = trouver_election_avec_vainqueurs_differents(filename, num_voters, num_candidates)

# Afficher les résultats des méthodes de vote



print(f"\nRésultat Vote Un Tour: {gagnant_un_tour}")
print(f"Résultat Vote Deux Tours: {gagnant_deux_tours}")
print(f"Résultat Vote Condorcet: {gagnant_condorcet}")
print(f"Résultat Vote Borda: {gagnant_borda}")
# Conclure que les vainqueurs sont différents
print("Les vainqueurs sont tous différents selon les méthodes de vote.")

print(f"\nPourcentage de préférences différentes: {percent_different_preferences:.2f}%")
print(f"Pourcentage de préférences avec un candidat différent en tête: {percent_different_head:.2f}%")
print(f"Nombre d'itérations avant de trouver une élection valide : {iteration_count}")
