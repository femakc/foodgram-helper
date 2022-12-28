TRANS_DICT = {
    'ingredient__name': 'Название ингредиента',
    'ingredient__measurement_unit': 'еденица измерения',
    'amount': 'количество'
}


def make_send_file(ingredient):
    with open('shop_list_file.txt', 'w') as shop_list_file:
        shop_list_file.write('Список ингредиентов:\n\n')
        for i in ingredient:
            for key, value in i.items():
                shop_list_file.write(f'{TRANS_DICT[key]} - {value}\n')
                if key == 'amount':
                    shop_list_file.write('\n')

    with open('shop_list_file.txt', 'r') as f:
        file_data = f.read()
    return file_data
