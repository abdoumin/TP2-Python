import csv
import random
import string

# Voting methods
def VoteUnTour(voters):
    votes = {}
    for v in voters.values():
        first_choice = v['preferences'][0]
        votes[first_choice] = votes.get(first_choice, 0) + 1
    winner = max(votes, key=votes.get)
    return winner

def VoteDeuxTours(voters):
    # First round
    votes = {}
    for v in voters.values():
        first_choice = v['preferences'][0]
        votes[first_choice] = votes.get(first_choice, 0) + 1

    # Top two candidates
    sorted_candidates = sorted(votes.items(), key=lambda item: item[1], reverse=True)
    finalists = [sorted_candidates[0][0], sorted_candidates[1][0]]

    # Second round
    second_round_votes = {finalists[0]: 0, finalists[1]: 0}
    for v in voters.values():
        for candidate in v['preferences']:
            if candidate in finalists:
                second_round_votes[candidate] += 1
                break

    winner = finalists[0] if second_round_votes[finalists[0]] > second_round_votes[finalists[1]] else finalists[1]
    return winner

def VoteCondorcet(voters):
    candidates = voters[next(iter(voters))]['preferences']
    duels = {c1: {c2: 0 for c2 in candidates if c2 != c1} for c1 in candidates}

    for v in voters.values():
        prefs = v['preferences']
        for i, c1 in enumerate(prefs):
            for c2 in prefs[i+1:]:
                duels[c1][c2] += 1

    for candidate in candidates:
        if all(duels[candidate][opponent] > duels[opponent][candidate] for opponent in candidates if opponent != candidate):
            return candidate
    return None  # No Condorcet winner

def VoteBorda(voters):
    scores = {}
    num_candidates = len(voters[next(iter(voters))]['preferences'])
    for v in voters.values():
        prefs = v['preferences']
        for rank, candidate in enumerate(prefs):
            scores[candidate] = scores.get(candidate, 0) + (num_candidates - rank)
    winner = max(scores, key=scores.get)
    return winner

# Function to generate election data for Question 6, ensuring all methods yield the same winner
def generate_election_data_q5():
    num_voters = 70
    num_candidates = 10  # Adjusted to 10 candidates to meet the requirement
    candidates = list(string.ascii_uppercase[:num_candidates])  # ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

    # Initialize voter groups
    voters = {}
    group1_voters = {}
    group2_voters = {}

    # Group 1: 56 voters (80% of 70) who all rank Candidate A first
    group1_size = int(0.8 * num_voters)
    candidate_winner = 'A'

    for voter_id in range(1, group1_size + 1):
        voter_label = f"Voter_{voter_id}"
        group = 'Standard Preferences'
        remaining_candidates = [c for c in candidates if c != candidate_winner]
        random.shuffle(remaining_candidates)
        preferences = [candidate_winner] + remaining_candidates
        voters[voter_label] = {'preferences': preferences, 'group': group}
        group1_voters[voter_label] = {'preferences': preferences, 'group': group}

    # Group 2: 14 voters (20% of 70) with varied preferences
    group2_size = num_voters - group1_size
    group2_varied_size = int(0.7 * group2_size)  # 70% of 14 = 10 voters
    group2_remaining_size = group2_size - group2_varied_size

    # Subgroup 2A: 10 voters with unique first-choice candidates (but not Candidate A)
    other_candidates = [c for c in candidates if c != candidate_winner]
    for voter_id in range(group1_size + 1, group1_size + group2_varied_size + 1):
        voter_label = f"Voter_{voter_id}"
        group = 'Varied Preferences'
        first_choice = random.choice(other_candidates)
        remaining_candidates = [c for c in candidates if c != first_choice]
        random.shuffle(remaining_candidates)
        preferences = [first_choice] + remaining_candidates
        voters[voter_label] = {'preferences': preferences, 'group': group}
        group2_voters[voter_label] = {'preferences': preferences, 'group': group}

    # Subgroup 2B: 4 voters with random preferences
    for voter_id in range(group1_size + group2_varied_size + 1, num_voters + 1):
        voter_label = f"Voter_{voter_id}"
        group = 'Varied Preferences'
        preferences = random.sample(candidates, len(candidates))
        voters[voter_label] = {'preferences': preferences, 'group': group}
        group2_voters[voter_label] = {'preferences': preferences, 'group': group}

    return voters, group1_voters, group2_voters, candidates
# Function to run Question 5 election
def run_election_q5():
    max_attempts = 10000
    attempt = 0
    while attempt < max_attempts:
        attempt += 1
        voters, group1_voters, group2_voters, candidates = generate_election_data_q6()
        if verify_conditions(voters, group1_voters, group2_voters):
            # Apply voting methods
            winner_un_tour = VoteUnTour(voters)
            winner_deux_tours = VoteDeuxTours(voters)
            winner_condorcet = VoteCondorcet(voters)
            winner_borda = VoteBorda(voters)

            # Check for unique winners
            winners = [winner_un_tour, winner_deux_tours, winner_condorcet, winner_borda]
            if None in winners:
                continue  # No Condorcet winner, try again
            unique_winners = set(winners)
            if len(unique_winners) == 1:
                # All conditions are met
                print(f"Election results after {attempt} attempts:")
                print(f"Single-Round Voting Winner: {winner_un_tour}")
                print(f"Two-Round Voting Winner: {winner_deux_tours}")
                print(f"Condorcet Winner: {winner_condorcet}")
                print(f"Borda Count Winner: {winner_borda}\n")

                # Print conditions verification
                total_voters = len(voters)
                num_varied_voters = len(group2_voters)
                percentage_varied = (num_varied_voters / total_voters) * 100
                print(f"Percentage of voters with varied preferences: {percentage_varied:.2f}% (Condition: ≥20%)")

                num_different_first_choices = sum(1 for v in group2_voters.values() if v['preferences'][0] not in [v1['preferences'][0] for v1 in group1_voters.values()])
                percentage_different_first_choices = (num_different_first_choices / num_varied_voters) * 100
                print(f"Percentage of varied voters with different first choice than Group 1: {percentage_different_first_choices:.2f}% (Condition: ≥70%)\n")

                # Write election data to CSV file
                filename = 'election_results_q5.csv'
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['Voter', 'Group'] + candidates
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    for voter_label, data in voters.items():
                        row = {'Voter': voter_label, 'Group': data['group']}
                        for idx, candidate in enumerate(data['preferences']):
                            row[candidate] = idx + 1  # Rank
                        writer.writerow(row)

                print(f"Election data has been written to '{filename}'.")
                print("Each voter's group (Standard or Varied Preferences) is indicated in the 'Group' column of the CSV file.")
                return
    print("Unable to generate an election meeting all conditions after maximum attempts.")

def verify_conditions(voters, group1_voters, group2_voters):
    total_voters = len(voters)
    num_varied_voters = len(group2_voters)
    percentage_varied = (num_varied_voters / total_voters) * 100

    # Condition 1: At least 20% of voters have varied preferences
    condition1 = percentage_varied >= 20

    # Condition 2: Among varied voters, at least 70% have unique first-choice candidates compared to Group 1
    group1_first_choices = [v['preferences'][0] for v in group1_voters.values()]
    group2_first_choices = [v['preferences'][0] for v in group2_voters.values()]
    unique_group2_first_choices = set(group2_first_choices)

    # Count how many varied voters have a different first choice from Group 1's first choices
    num_different_first_choices = sum(1 for choice in group2_first_choices if choice not in group1_first_choices)
    percentage_different_first_choices = (num_different_first_choices / num_varied_voters) * 100

    condition2 = percentage_different_first_choices >= 70

    return condition1 and condition2

# Function to run Question 6 election
def run_election_q6():
    max_attempts = 10000
    attempt = 0
    while attempt < max_attempts:
        attempt += 1
        voters, group1_voters, group2_voters, candidates = generate_election_data_q6()
        if verify_conditions(voters, group1_voters, group2_voters):
            # Apply voting methods
            winner_un_tour = VoteUnTour(voters)
            winner_deux_tours = VoteDeuxTours(voters)
            winner_condorcet = VoteCondorcet(voters)
            winner_borda = VoteBorda(voters)

            # Check for unique winners
            winners = [winner_un_tour, winner_deux_tours, winner_condorcet, winner_borda]
            if None in winners:
                continue  # No Condorcet winner, try again
            unique_winners = set(winners)
            if len(unique_winners) == 4:
                # All conditions are met
                print(f"Election results after {attempt} attempts:")
                print(f"Single-Round Voting Winner: {winner_un_tour}")
                print(f"Two-Round Voting Winner: {winner_deux_tours}")
                print(f"Condorcet Winner: {winner_condorcet}")
                print(f"Borda Count Winner: {winner_borda}\n")

                # Print conditions verification
                total_voters = len(voters)
                num_varied_voters = len(group2_voters)
                percentage_varied = (num_varied_voters / total_voters) * 100
                print(f"Percentage of voters with varied preferences: {percentage_varied:.2f}% (Condition: ≥20%)")

                num_different_first_choices = sum(1 for v in group2_voters.values() if v['preferences'][0] not in [v1['preferences'][0] for v1 in group1_voters.values()])
                percentage_different_first_choices = (num_different_first_choices / num_varied_voters) * 100
                print(f"Percentage of varied voters with different first choice than Group 1: {percentage_different_first_choices:.2f}% (Condition: ≥70%)\n")

                # Write election data to CSV file
                filename = 'election_results_q6.csv'
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['Voter', 'Group'] + candidates
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    for voter_label, data in voters.items():
                        row = {'Voter': voter_label, 'Group': data['group']}
                        for idx, candidate in enumerate(data['preferences']):
                            row[candidate] = idx + 1  # Rank
                        writer.writerow(row)

                print(f"Election data has been written to '{filename}'.")
                print("Each voter's group (Standard or Varied Preferences) is indicated in the 'Group' column of the CSV file.")
                return
    print("Unable to generate an election meeting all conditions after maximum attempts.")

def generate_election_data_q6():
    num_voters = 70
    num_candidates = 10  # At least 10 candidates
    candidates = list(string.ascii_uppercase[:num_candidates])  # ['A', 'B', ..., 'J']

    # Initialize voter groups
    voters = {}
    group1_voters = {}
    group2_voters = {}

    # Group 1: 56 voters (80% of 70)
    group1_size = int(0.8 * num_voters)
    group1_subgroups = {
        'A': 20,  # Subgroup 1A: 20 voters prefer Candidate A
        'B': 12,  # Subgroup 1B: 12 voters prefer Candidate B
        'C': 12,  # Subgroup 1C: 12 voters prefer Candidate C
        'D': 12,  # Subgroup 1D: 12 voters prefer Candidate D
    }

    voter_id = 1

    # Generate Group 1 voters
    for candidate, subgroup_size in group1_subgroups.items():
        for _ in range(subgroup_size):
            voter_label = f"Voter_{voter_id}"
            group = 'Standard Preferences'
            # Start with preferred candidate
            preferences = [candidate]
            # Remaining candidates
            remaining_candidates = [c for c in candidates if c != candidate]
            # Assign lower preferences to influence outcomes
            if candidate == 'A':
                # For Candidate A supporters, rank D low to reduce D's Borda score
                remaining_candidates.remove('D')
                random.shuffle(remaining_candidates)
                preferences += remaining_candidates + ['D']
            elif candidate == 'B':
                # For Candidate B supporters, rank B over A
                remaining_candidates.remove('A')
                random.shuffle(remaining_candidates)
                preferences += remaining_candidates + ['A']
            elif candidate == 'C':
                # For Candidate C supporters, rank C over all others
                random.shuffle(remaining_candidates)
                preferences += remaining_candidates
            elif candidate == 'D':
                # For Candidate D supporters, rank D high
                random.shuffle(remaining_candidates)
                preferences += remaining_candidates
            voters[voter_label] = {'preferences': preferences, 'group': group}
            group1_voters[voter_label] = {'preferences': preferences, 'group': group}
            voter_id += 1

    # Group 2: 14 voters (20% of 70)
    group2_size = num_voters - group1_size
    group2_varied_size = int(0.7 * group2_size)  # At least 70% of 14 = 10 voters
    group2_remaining_size = group2_size - group2_varied_size

    # Subgroup 2A: 10 voters with unique first-choice candidates
    unique_first_choices = candidates.copy()
    random.shuffle(unique_first_choices)
    for _ in range(group2_varied_size):
        voter_label = f"Voter_{voter_id}"
        group = 'Varied Preferences'
        first_choice = unique_first_choices.pop()
        remaining_candidates = [c for c in candidates if c != first_choice]
        random.shuffle(remaining_candidates)
        preferences = [first_choice] + remaining_candidates
        voters[voter_label] = {'preferences': preferences, 'group': group}
        group2_voters[voter_label] = {'preferences': preferences, 'group': group}
        voter_id += 1

    # Subgroup 2B: 4 voters with random preferences
    for _ in range(group2_remaining_size):
        voter_label = f"Voter_{voter_id}"
        group = 'Varied Preferences'
        preferences = random.sample(candidates, len(candidates))
        voters[voter_label] = {'preferences': preferences, 'group': group}
        group2_voters[voter_label] = {'preferences': preferences, 'group': group}
        voter_id += 1

    return voters, group1_voters, group2_voters, candidates


# Main execution
if __name__ == "__main__":
    # Run Question 5 Election
    print("Running Election for Question 5:")
    run_election_q5()
    print("\n---------------------------------\n")

    # Run Question 6 Election
    print("Running Election for Question 6:")
    run_election_q6()
