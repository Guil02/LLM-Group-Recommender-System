MIN_SCORE = 3.0

import openai

api_key = ""


def average_recommendation(preference_list, max_tags=10):
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

    average_scores = {item: item_totals[item] / item_counts[item] for item in item_totals if
                      item_totals[item] / item_counts[item] >= MIN_SCORE}
    recommended_items = sorted(average_scores.items(), key=lambda x: x[1], reverse=True)
    recommended_items = recommended_items[0:max_tags]
    return recommended_items


def least_misery_recommendation(preference_list, max_tags=10):
    item_min_scores = {}

    for preferences in preference_list:
        for item, score in preferences.items():
            if item in item_min_scores:
                item_min_scores[item] = min(item_min_scores[item], score)
            else:
                item_min_scores[item] = score

    recommended_items = {item: score for item, score in item_min_scores.items() if score >= MIN_SCORE}
    recommended_items = sorted(recommended_items.items(), key=lambda x: x[1], reverse=True)[0:max_tags]

    return recommended_items


def most_pleasure_recommendation(preference_list, max_tags=10):
    item_max_scores = {}

    for preferences in preference_list:
        for item, score in preferences.items():
            if item in item_max_scores:
                item_max_scores[item] = max(item_max_scores[item], score)
            else:
                item_max_scores[item] = score

    recommended_items = {item: score for item, score in item_max_scores.items() if score >= MIN_SCORE}
    recommended_items = sorted(recommended_items.items(), key=lambda x: x[1], reverse=True)[0:max_tags]

    return recommended_items


def openai_recommendation(preference_list, max_tags=10, api_key=api_key):
    openai.api_key = api_key

    def construct_prompt(preference_list, max_tags):
        prompt = (
            "Given a list of user-rated preferences, aggregate the tags and provide the best tags for the group. "
            "Each item in the list is a dictionary with tags and their corresponding ratings by users. "
            "Here is an example of the list of preferences:\n\n"
            '[{"tag1": 4, "tag2": 3}, {"tag1": 2, "tag3": 5}]\n\n'
            "Here is the actual list of preferences:\n\n"
            f"{preference_list}\n\n"
            f"Please ONLY return the top {max_tags} tags that are best suited for the group based on user ratings. "
            "Do not include any explanation or description of the method used to determine the best tags. "
            "Simply list the tags in order of their suitability in the following format:\n"
            '[("tag1",rating), ("tag2",rating), ("tag3",rating), ...]'
        )
        return prompt

    prompt = construct_prompt(preference_list, max_tags)
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()
