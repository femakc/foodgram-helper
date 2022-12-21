import json
PATH_FILE = "ingredients.json"
data_list = []

with open(PATH_FILE) as f:
    d = json.load(f)
    for i in range(len(d)):
        a = {"model": "recipes.ingredient", "pk": i + 1, "fields": d[i]}
        data_list.append(a)

with open('new_ingredients.json', 'w', encoding='utf-8') as file:
    json.dump(data_list, file, ensure_ascii=False, indent=4)
