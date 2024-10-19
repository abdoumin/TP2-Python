import csv
import random
import string

def generate_election_csv(filename, num_voters, num_candidates):
    # Générer les noms des candidats (A, B, C, ...)
    candidates = list(string.ascii_uppercase[:num_candidates])
    
    # Créer les données pour le fichier CSV
    data = [['Voter'] + candidates]  # En-tête
    
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
    return None  # Pas de vainqueur de Condorcet

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
print("Résultat Vote Condorcet:", VoteCondorcet(preferences))
print("Résultat Vote Borda:", VoteBorda(preferences))
