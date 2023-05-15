import json
import requests
import ssl

server = 'http://localhost:5000'
while True:
    comando = input("Operação (SEARCH, FILTER, FILTER DIVERSIFY ou DETAILS): ")
    comando = comando.split()

    if comando[0] == 'SEARCH':
        location = input("Localização: ")
        cost = input("Custo máximo: ")
        url = f"{server}/search?location={location}&cost={cost}"
        response = requests.get(url)
    
    if comando[0] == 'FILTER' and len(comando) == 1:
        location = input('Localização: ')
        n = input('Dias de sol: ')
        airline = input('Companhia aérea: ')
        url = f"{server}/filter?location={location}&n={n}&airline={airline}"
        response = requests.get(url)

    if comando[0] == 'FILTER' and comando[1] == 'DIVERSIFY':
        url = f"{server}/filter_diversify"
        response = requests.get(url)

    if comando[0] == 'DETAILS':
        id = input('ID: ')
        url = f"{server}/details?id={id}"
        response = requests.get(url)

    if response.status_code == 200:
        data = json.loads(response.text)
        print(json.dumps(data, indent=4))
    else:
        print(f"Erro: {response.status_code}")

