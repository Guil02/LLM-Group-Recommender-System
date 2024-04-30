MIN_SCORE = 3.0

def average_recommendation(preference_list):
    item_totals = {}
    item_counts = {}

    for preferences in preference_list:
        for item, score in preferences.items():
            if item in item_totals:
                item_totals[item] += score
                item_counts[item] += 1
            else:
                item_totals[item] = score
                item_counts[item] = 1

    average_scores = {item: item_totals[item] / item_counts[item] for item in item_totals if item_totals[item] / item_counts[item] >= MIN_SCORE}
    recommended_items = sorted(average_scores.items(), key=lambda x: x[1], reverse=True)
    return recommended_items

def least_misery_recommendation(preference_list):
    item_min_scores = {}

    for preferences in preference_list:
        for item, score in preferences.items():
            if item in item_min_scores:
                item_min_scores[item] = min(item_min_scores[item], score)
            else:
                item_min_scores[item] = score

    recommended_items = {item: score for item, score in item_min_scores.items() if score >= MIN_SCORE}
    return sorted(recommended_items.items(), key=lambda x: x[1], reverse=True)

def most_pleasure_recommendation(preference_list):
    item_max_scores = {}

    for preferences in preference_list:
        for item, score in preferences.items():
            if item in item_max_scores:
                item_max_scores[item] = max(item_max_scores[item], score)
            else:
                item_max_scores[item] = score

    recommended_items = {item: score for item, score in item_max_scores.items() if score >= MIN_SCORE}
    return sorted(recommended_items.items(), key=lambda x: x[1], reverse=True)

# Example usage
preferences = [
    {"banana": 5, "apple": 2, "orange": 3},
    {"banana": 3, "apple": 2, "grape": 4},
    {"banana": 4, "apple": 5, "grape": 2}
]

print("Average Recommendation:", average_recommendation(preferences))
print("Least Misery Recommendation:", least_misery_recommendation(preferences))
print("Most Pleasure Recommendation:", most_pleasure_recommendation(preferences))
