import json

FILE_PATH = '/home/femakc/Dev/foodgram-project-react/data/ingredients.json'

string1 = '{"model": "recipes.ingredient", "pk":'
string2 = ', "fields": '
string3 = '}'
ingredient_list = []

with open(FILE_PATH) as json_file:
    json_data = json.load(json_file)
    for i in json_data:
        a = 1
        ingredient_list.append(f'{string1}{a}{string2}{i}{string3}')
        a += 1
print(ingredient_list[0])
list_json = json.dumps(ingredient_list)

with open('/home/femakc/Dev/foodgram-project-react/data/list_ingredients.json', 'w') as file:
    json.dumps(ingredient_list)

# [{"model": "recipes.ingredient", "pk": 1, "fields": {"name": "Картоха", "measurement_unit": "г"}}]