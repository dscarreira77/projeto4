from flask import Flask, request, jsonify
import json
import requests
import sqlite3
from os.path import isfile
import sll

app = Flask(__name__)

def connect_db():
    db_is_created = isfile('voos.db')
    conn = sqlite3.connect('voos.db')
    cursor= conn.cursor()
    if not db_is_created:
        cursor.execute('PRAGMA foreign_keys = ON;')
        cursor.execute('PRAGMA busy_timeout = 5000;')
        cursor.execute('''CREATE TABLE roundtrips (
            id TEXT PRIMARY KEY,
            cost INTEGER,
            id_leg0 INTEGER,
            id_leg1 INTEGER,
            FOREIGN KEY(id_leg0) REFERENCES legs(id) ON DELETE CASCADE,
            FOREIGN KEY(id_leg1) REFERENCES legs(id) ON DELETE CASCADE
            );''')
        cursor.execute('''CREATE TABLE legs (
            id TEXT PRIMARY KEY,
            dep_IATA TEXT,
            arr_IATA TEXT,
            dep_datetime TEXT,
            arr_datetime TEXT,
            duration TEXT,
            airline TEXT,
            FOREIGN KEY(dep_IATA) REFERENCES locations(IATA) ON DELETE CASCADE,
            FOREIGN KEY(arr_IATA) REFERENCES locations(IATA) ON DELETE CASCADE
            );''')
        cursor.execute('''CREATE TABLE locations (
            id TEXT PRIMARY KEY,
            name TEXT,
            IATA TEXT,
            wea_name TEXT,
            FOREIGN KEY(IATA) REFERENCES legs(IATA) ON DELETE CASCADE,
            FOREIGN KEY(wea_name) REFERENCES weather(location) ON DELETE CASCADE
            );''')
        cursor.execute('''CREATE TABLE airlines (
            code TEXT PRIMARY KEY,
            name TEXT
            );''')
        
        cursor.execute('''CREATE TABLE weather (
            id TEXT PRIMARY KEY,
            date TEXT,
            location TEXT,
            condition TEXT,
            temp_min INTEGER,
            temp_max INTEGER,
            FOREIGN KEY(location) REFERENCES locations(wea_name) ON DELETE CASCADE
            );''')
    return conn, cursor

def insert_bd():
    conn, cursor = connect_db()
    
    # Insert locations
    locations=[('1', 'Amsterdam', 'AMS', 'amsterdam'),
               ('2', 'Berlin', 'BER', 'berlin'),
               ('3', 'Brussels', 'BRU', 'brussels'),
               ('4', 'Dublin', 'DUB', 'dublin'),
               ('5', 'Lisbon', 'LIS', 'lisbon'),
               ('6', 'Madrid', 'MAD', 'madrid'),
               ('7', 'Paris', 'ORY', 'paris'),
               ('8', 'Rome', 'FCO', 'rome'),
               ('9', 'Vienna', 'VIE', 'vienna'),
               ('10', 'Ljubljana', 'LJU', 'ljubljana')
               ]
    
    APi_url = 'https://lmpinto.eu.pythonanywhere.com/v1/forecast.json?key=dfsdfsdfsdfsdf&q={countrie}&days=14'
    
    paises = ['amsterdam', 'berlin', 'brussels', 'dublin', 'lisbon', 'madrid', 'paris', 'rome', 'vienna','ljubljana',]
    
    a=0
    for i in range(len(paises)):
        response = requests.get(APi_url.format(countrie=paises[i]))
        data = response.json()
        for day in data['forecast']['forecastday']:
           a +=1
           data =day['date']
           location =locations[i][3]
           condition =day['day']['condition']['text']
           min_temp =day['day']['mintemp_c']
           max_temp =day['day']['maxtemp_c']
           cursor.execute("INSERT OR IGNORE INTO weather VALUES (?, ?, ?, ?, ?, ?)", (a, data, location, condition, min_temp, max_temp))


    for location in locations:
        cursor.execute("INSERT OR IGNORE INTO locations VALUES (?, ?, ?,?)", location)
    
    # Insert airlines
    airlines = [('A3', 'Aegean Airlines'),
                ('AF', 'Air France'),
                ('BA', 'British Airways'),
                ('EI', 'Aer Lingus'),
                ('IB', 'Iberia'),
                ('LH', 'Lufthansa'),
                ('SK', 'Scandinavian Airlines'),
                ('TK', 'Turkish Airlines'),
                ('U2', 'EasyJet'),
                ('VY', 'Vueling')]
    
    for airline in airlines:
        cursor.execute("SELECT * FROM airlines WHERE code=?", (airline[0],))
        data = cursor.fetchone()
        if data is None:
            cursor.execute("INSERT INTO airlines VALUES (?, ?)", airline)
    conn.commit()
    conn.close()

Wheater_api= 'https://lmpinto.eu.pythonanywhere.com/v1/forecast.json?key=dfsdfsdfsdfsdf&q={countrie}&days=14'

flights_api = 'https://lmpinto.eu.pythonanywhere.com/roundtrip/ygyghjgjh/{partida}/{chegada}/{data_inicio}/{data_fim}/1/0/0/Economy/EUR'

connect_db()

def sol(pais,data1,data2):
    if pais == 'MAD':
        pais = 'madrid'
    if pais == 'ATH':
        pais = 'athens'
    if pais == 'FCO':
        pais = 'rome'
    if pais == 'ORY':
        pais = 'paris'
    if pais == 'VIE':
        pais = 'vienna'
    response = requests.get(Wheater_api.format(countrie=pais))
    data = response.json()
    counter = 0
    dataFim = 0
    for x in range(len(data['forecast']['forecastday'])):
        if data['forecast']['forecastday'][x]['date'] == data1:
            DataInicio = x
        if data['forecast']['forecastday'][x]['date'] == data2:
            dataFim = x
    if dataFim != 0:
        for i in range(DataInicio,dataFim+1):
            if data['forecast']['forecastday'][i]['day']['condition']['text'] == "Sunny" :
                counter += 1
    return counter

def inserirTudo(location,voos):
    destinos = ['ATH','FCO','MAD','ORY','VIE']
    partida = location

    #RoundtripTable
    roundripTableId = []
    roundripTableLeg0 = []
    roundripTableLeg1 = []
    roundtripPrice = []

    #Auxiliar
    roundtripsTotais = []
    
    #LegsTable
    legsTableId = []
    legsTableArr = []
    legsTableDep = []
    legsTableDepDate = []
    legsTableArrDate = []
    legsTableDuration = []
    legsTableAirline = []
    
    #airlines
    airlinesCode = []
    airlinesName = []
    for i in range(len(destinos)):
            for day in range(26,29):
                if day <=27:
                    data1 = '2023-04-'+str(day)
                    data2 = '2023-04-'+str(day+3)
                elif day > 27:
                    data1 = '2023-04-'+str(day)
                    data2 = '2023-05-' + str(day-27)

                if sol(destinos[i],data1,data2) >= 2:
                    response = requests.get(flights_api.format(partida=partida,chegada=destinos[i],data_inicio=data1,data_fim=data2))
                    data = response.json()
                    for x in range(len(data['trips'])):
                        if data['trips'][x]['id'] in voos:
                            roundripTableId.append(data['trips'][x]['id'])
                            roundripTableLeg0.append(data['trips'][x]['legIds'][0])
                            roundripTableLeg1.append(data['trips'][x]['legIds'][1])
                            roundtripsTotais.append(data['trips'][x]['legIds'][0])
                            roundtripsTotais.append(data['trips'][x]['legIds'][1])
                    for x in range(len(roundripTableId)):
                        for y in range(len(data['fares'])):
                            if roundripTableId[x] == data['fares'][y]['tripId'] and len(roundtripPrice)<= x:
                                roundtripPrice.append(data['fares'][y]['price']['totalAmount'])
                    for x in range(len(roundtripsTotais)):
                        for y in range(len(data['legs'])):
                            if roundtripsTotais[x] == data['legs'][y]['id'] and roundtripsTotais[x] not in legsTableId:
                                    legsTableId.append(data['legs'][y]['id'])
                                    legsTableArr.append(data['legs'][y]['arrivalAirportCode'])
                                    legsTableDep.append(data['legs'][y]['departureAirportCode'])
                                    legsTableDepDate.append(data['legs'][y]['departureDateTime'])
                                    legsTableArrDate.append(data['legs'][y]['arrivalDateTime'])
                                    legsTableDuration.append(data['legs'][y]['durationMinutes'])
                                    legsTableAirline.append(data['legs'][y]['airlineCodes'][0])
                    for x in range(len(data['airlines'])):
                        airlinesCode.append(data['airlines'][x]['code'])
                        airlinesName.append(data['airlines'][x]['name'])
    conn, cursor = connect_db()
    for x in range(len(airlinesCode)):
        cursor.execute("INSERT OR IGNORE INTO airlines VALUES (?, ?)", (airlinesCode[x], airlinesName[x]))
        conn.commit()
    for x in range(len(roundripTableId)):
        cursor.execute("INSERT OR IGNORE INTO roundtrips VALUES (?, ?, ?, ?)", (roundripTableId[x], roundtripPrice[x], roundripTableLeg0[x], roundripTableLeg1[x]))
        conn.commit()
    for x in range(len(legsTableId)):
        cursor.execute("INSERT OR IGNORE INTO legs VALUES (?, ?, ?, ?, ?, ?, ?)", (legsTableId[x], legsTableDep[x], legsTableArr[x], legsTableDepDate[x], legsTableArrDate[x], legsTableDuration[x], legsTableAirline[x]))
        conn.commit()
@app.route('/search', methods=['GET'])
def search():
    cost = request.args.get('cost')
    partida = request.args.get('location')
    voo = []
    destinos = ['ATH','FCO','MAD','ORY','VIE']
    respostaId = []
    respostaPrice = []
    resultado = []
    respostaLeg0 = []
    respostaLeg1 = []

    #apagar as bases de dados
    conn, cursor = connect_db()
    cursor.execute("DELETE FROM roundtrips")
    cursor.execute("DELETE FROM legs")
    conn.commit()

    for i in range(len(destinos)):
            for day in range(26,29):
                
                if day <=27:
                    data1 = '2023-04-'+str(day)
                    data2 = '2023-04-'+str(day+3)
                
                elif day > 27:
                    data1 = '2023-04-'+str(day)
                    data2 = '2023-05-' + str(day-27)

                if sol(destinos[i],data1,data2) >= 2:
                    response = requests.get(flights_api.format(partida=partida,chegada=destinos[i],data_inicio=data1,data_fim=data2))
                    data = response.json()
                    
                    for x in range(len(data['trips'])):
                        voo.append(data['trips'][x]['id'])
                    
                    for x in range(len(voo)):
                        for y in range(len(data['fares'])):
                            if voo[x] == data['fares'][y]['tripId'] and data['fares'][y]['price']['totalAmount'] <= int(cost) and voo[x] not in respostaId:
                                respostaId.append(voo[x])
                                respostaPrice.append(data['fares'][y]['price']['totalAmount'])
                    
                    for x in range(len(data['trips'])):
                        for y in range(len(respostaId)):
                            if respostaId[y] == data['trips'][x]['id']:
                                respostaLeg0.append(data['trips'][x]['legIds'][0])
                                respostaLeg1.append(data['trips'][x]['legIds'][1])
                    
                    for x in range(len(respostaId)):
                        resultado.append({'id': respostaId[x], 'cost': respostaPrice[x], 'id_leg0': respostaLeg0[x], 'id_leg1': respostaLeg1[x]})
    inserirTudo(partida,respostaId)
    return jsonify(resultado)

@app.route('/filter', methods=['GET'])
def filter():
    #eliminar as bases de dados
    conn, cursor = connect_db()
    #fechar a ligação
    conn.commit()
    insert_bd()

    location = request.args.get('location')
    n = request.args.get('n')
    airline = request.args.get('airline')


    cursor.execute("SELECT id FROM roundtrips WHERE id_leg0 IN (SELECT id FROM legs WHERE airline = ?) AND id_leg1 IN (SELECT id FROM legs WHERE airline = ?)", (airline, airline))
    voos = cursor.fetchall()
    locaisFim = []
    for day in range(26,29):
                if day <=27:
                    data1 = '2023-04-'+str(day)
                    data2 = '2023-04-'+str(day+3)
                if day > 27:
                    data1 = '2023-04-'+str(day)
                    data2 = '2023-05-' + str(day-27)
                print(data1,data2)
                cursor.execute("SELECT location FROM weather WHERE condition = 'Sunny' AND date BETWEEN ? AND ?", (data1, data2))
                locais = cursor.fetchall()
                a = 0
                for x in range(len(locais)-1):
                    if locais[x] == locais[x+1]:
                        a+=1
                    if a == int(n):
                        locaisFim.append({'location': locais[x], 'dateInit': data1, 'dateEnd': data2})
                    if locais[x] != locais[x+1]:
                        a=0
                IATAS = []
                #get locations IATAS
                for x in range(len(locaisFim)):
                    for y in locaisFim[x]['location']:
                        cursor.execute("SELECT IATA FROM locations WHERE wea_name = ?", (y,))
                        IATA = cursor.fetchone()
                        IATAS.append(IATA[0])
                voos2 = []
                for x in range(len(IATAS)):
                    cursor.execute("SELECT id FROM roundtrips WHERE id_leg0 IN (SELECT id FROM legs WHERE arr_IATA = ?)", (IATAS[x],))
                    var = cursor.fetchall()
                    if var != None and var not in voos2:
                        voos2.append(var)

                voosFim = []
                for x in range(len(voos)):
                    if voos[x] in voos2  and voos[x] not in voosFim:
                        voosFim.append(voos[x])
    return jsonify(voosFim)

@app.route('/filter_diversify', methods=['GET'])
def filerdiversify():
    conn, cursor = connect_db()
    #selecionar todas as localizações
    cursor.execute("SELECT IATA FROM locations")
    IATAS = cursor.fetchall()

    voos = []
    for loc in IATAS:
        #selecionar o voo mais barato para cada localização
        cursor.execute("SELECT id FROM roundtrips WHERE id_leg0 IN (SELECT id FROM legs WHERE arr_IATA = ?) ORDER BY cost ASC", (loc[0],))
        voo = cursor.fetchone()
        cursor.execute("SELECT cost FROM roundtrips WHERE id_leg0 IN (SELECT id FROM legs WHERE arr_IATA = ?) ORDER BY cost ASC", (loc[0],))
        cost = cursor.fetchone()
        if voo != None:
            voos.append({'id': voo, 'location': loc , 'cost': cost})
    return jsonify(voos)

@app.route('/details', methods=['GET'])
def details():
    id = request.args.get('id')

    conn, cursor = connect_db()

    cursor.execute("SELECT cost FROM roundtrips WHERE id = ?", (id,))
    cost = cursor.fetchone()

    cursor.execute("SELECT id_leg0 FROM roundtrips WHERE id = ?", (id,))
    id_leg0 = cursor.fetchone()
    

    cursor.execute("SELECT id_leg1 FROM roundtrips WHERE id = ?", (id,))
    id_leg1 = cursor.fetchone()
    
    cursor.execute("SELECT * FROM legs WHERE id = ?", (id_leg0[0],))
    leg0 = cursor.fetchone()    
    dep_IATA0 = leg0[1]
    arr_IATA0 = leg0[2]
    dep_datetime0 = leg0[3]
    arr_datetime0 = leg0[4]
    duracao1 = leg0[5]
    airline0 = leg0[6]

    cursor.execute("SELECT * FROM legs WHERE id = ?", (id_leg1[0],))
    leg1 = cursor.fetchone()
    dep_IATA1 = leg1[1]
    arr_IATA1 = leg1[2]
    dep_datetime1 = leg1[3]
    arr_datetime1 = leg1[4]
    duracao2 = leg1[5]
    airline1 = leg1[6]

    data0 = dep_datetime0.split('T')
    data1 = dep_datetime1.split('T')
    
    cursor.execute("SELECT * FROM weather WHERE location IN (SELECT wea_name FROM locations WHERE IATA = ?)", (arr_IATA0,))

    weather0 = cursor.fetchall()
    weather = []
    weather_final = []
    for x in range(len(weather0)):
            if weather0[x][1] == data0[0]:
                for y in range(4):
                    weather.append(weather0[x+y])

    for x in range(len(weather)):
        weather_date = weather[x][1]
        weather_condition = weather[x][3]
        weather_temp_min = weather[x][4]
        weather_temp_max = weather[x][5]
        weather_final.append({'date':{'weather_date':weather_date, 'weather_condition':weather_condition, 'weather_temp_min':weather_temp_min, 'weather_temp_max':weather_temp_max}})
    
    print(weather_final)

    answer = {'id':id,'cost':cost, 'leg0':{'dep_IATA0':dep_IATA0, 'arr_IATA0':arr_IATA0, 'dep_datetime0':dep_datetime0, 'arr_datetime0':arr_datetime0, 'duracao1':duracao1, 'airline':airline0}, 'leg1':{'dep_IATA1':dep_IATA1, 'arr_IATA1':arr_IATA1, 'dep_datetime1':dep_datetime1, 'arr_datetime1':arr_datetime1, 'duracao2':duracao2, 'airline':airline1}, 'tempo':weather_final}

    return jsonify(answer)

if __name__ == '__main__':
    app.run(debug=True)
