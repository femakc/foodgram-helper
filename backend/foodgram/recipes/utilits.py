
def make_send_file(ingredient):
    shop_list_file = open('shop_list_file.txt', 'w')
    for i in ingredient:
        shop_list_file.write("\n")
        for key, value in i.items():
            shop_list_file.write(f'{key} - {value}\n')

    shop_list_file.close()
    with open('shop_list_file.txt', 'r') as f:
        file_data = f.read()
    return file_data
