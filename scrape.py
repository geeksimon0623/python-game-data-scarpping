import requests
from bs4 import BeautifulSoup
import mysql.connector

with open('config.inf','r') as f:
    inf = f.readlines

def compare_datetime_less(t1, t2):
    for i in range(len(t1)):
        if t1[i] < t2[i]:
            return False
        elif t1[i] > t2[i]:
            return True
    return True
if __name__ == "__main__":
    try:
        f = open('config.inf','r')
        inf = f.readlines()
        f.close()
    except:
        print("Sorry, cannot read config file.")
        # input("Press any key to exit...")
        exit()
    try:
        mydb = mysql.connector.connect(
            host=inf[0].replace('\n',''),
            user=inf[1].replace('\n',''),
            password=inf[2].replace('\n',''),
            database=inf[3].replace('\n','')
        )

        mycursor = mydb.cursor()
    except:
        input('Soryy, DB Connection Error!\nPress any key to exit...')
        exit()
    sql = "UPDATE alliances SET Status='Extinct' WHERE ID>1"
    mycursor.execute(sql)
    mydb.commit()

    data = {
        'loginname' : 'your name',
        'loginpass' : 'your password',
        'logincap' : ''
    }
    try:
        r1 = requests.post("https://www.baseattackforce.com/?sh=Y",data=data)
    except:
        print('Server seems not to run')
        exit()
    print(r1.cookies)

    # alliances
    r3 = requests.post("https://www.baseattackforce.com/ally.php?a=2", cookies=r1.cookies)
    soup = BeautifulSoup(r3.content, 'html.parser')
    alliances = []
    rows = soup.table.find_all('tr')
    alliance_urls = []
    for row in rows[1:]:
        alliance_inf = row.find_all('td')[1:7]
        name = alliance_inf[1].get_text().split(' ')[0]
        alliance_detail_url = 'https://www.baseattackforce.com/{0}'.format(alliance_inf[1].find('a')['href'])
        game_id = alliance_detail_url.split('=')[-1]
        alliance_urls.append(game_id)
        creation_date = alliance_inf[1].get_text().split(' ')[1]
        day = creation_date.split('.')[0]
        month = creation_date.split('.')[1]
        year = creation_date.split('.')[2]
        creation_date = '20{0}-{1}-{2}'.format(year, month, day)
        more_info = alliance_inf[5].get_text()
        if "newcomers" in more_info:
            newcomers = 'yes'
        else:
            newcomers = 'no'
        if "Democracy" in more_info:
            democracy = 'yes'
        else:
            democracy = 'no'
        if "Points" in more_info:
            requirements = more_info.split("Points")[0].split("Requirements:")[-1].strip().replace('.','')
        else:
            requirements = '0'
        if "language" in more_info:
            language = more_info.split("language:")[1].split('Conquered')[0].strip().split(' ')[-1]
        else:
            language = '-'
        if "Conquered Maps:" in more_info:
            total_maps = more_info.split("Conquered Maps:")[-1].strip()
        else:
            total_maps = '0'
        alliance = {
            'Ranking' : alliance_inf[0].get_text(),
            'Name' : name,
            'Creation_Date' : creation_date,
            'Total_Points' : alliance_inf[2].get_text().replace('.',''),
            'Total_Bases' : alliance_inf[3].get_text().replace('.',''),
            'Total_Members' : alliance_inf[4].get_text(),
            'Newcomers' : newcomers,
            'Requirements' : requirements,
            'Democracy' : democracy,
            'Language' : language,
            'Total_Maps' : total_maps
        }
        alliances.append(alliance)
        try:
            sql = "UPDATE Alliances SET Status='Exist',Total_Points={0},Total_Bases={1},Total_Members={2},Newcomers='{3}',Requirements={4},Democracy='{5}',Language='{6}',Total_Maps={7},Rank={8} WHERE Game_ID={9}".format(
                alliance['Total_Points'],
                alliance['Total_Bases'],
                alliance['Total_Members'],
                alliance['Newcomers'],
                alliance['Requirements'],
                alliance['Democracy'],
                alliance['Language'],
                alliance['Total_Maps'],
                alliance['Ranking'],
                game_id
            )
            mycursor.execute(sql)
            mydb.commit()

            if mycursor.rowcount != 0:
                continue
            sql = "INSERT INTO Alliances (Name,Game_ID,Creation_Date,Status,Approval,Total_Points,Total_Bases,Total_Members,Newcomers,Requirements,Democracy,Language,Total_Maps,Rank) VALUES ('{0}',{1},'{2}','Exist',1,{3},{4},{5},'{6}',{7},'{8}','{9}',{10},{11})".format(
                alliance['Name'],
                game_id,
                alliance['Creation_Date'],
                alliance['Total_Points'],
                alliance['Total_Bases'],
                alliance['Total_Members'],
                alliance['Newcomers'],
                alliance['Requirements'],
                alliance['Democracy'],
                alliance['Language'],
                alliance['Total_Maps'],
                alliance['Ranking']
            )
            mycursor.execute(sql)
            mydb.commit()
        except:
            pass
    # members of alliance
    sql = "UPDATE users SET previous_ally =  alliance, alliance = 0"
    mycursor.execute(sql)
    mydb.commit()
    sql="SELECT MAX(Datetime) FROM battles"
    mycursor.execute(sql)
    result = mycursor.fetchall()[0][0]
    if result == None:
        result = "2001-06-23 00:00:00"
    else:
        result = result.strftime("%Y-%m-%d %H:%M:%S")
    for url in alliance_urls:
        try:
            r2 = requests.post("https://www.baseattackforce.com/ally.php?b={0}".format(url), cookies=r1.cookies)
        except:
            continue
        soup = BeautifulSoup(r2.content, 'html.parser')
        your_alliance = []
        try:
            rows = soup.find_all('table')[1].find_all('tr')
        except:
            continue
        for row in rows[1:]:
            ally_inf = row.find_all('td')[1:7]
            if ally_inf[4].get_text() == "":
                online = 'off'
            else:
                online = ally_inf[4].get_text()
            if ally_inf[5].get_text() == "":
                position = 'member'
            else:
                position = ally_inf[5].get_text()
            ally = {
                'Name' : ally_inf[0].get_text(),
                'Points' : ally_inf[1].get_text().replace('.',''),
                'Bases' : ally_inf[2].get_text().replace('.',''),
                'Rank' : ally_inf[3].get_text().replace('.',''),
                'Online' : online,
                'Position' : position
            }
            try:
                sql = "UPDATE users SET points={0},bases={1},rank={2},is_online='{3}',position='{4}', alliance = {6} WHERE username='{5}'".format(
                    ally['Points'],
                    ally['Bases'],
                    ally['Rank'],
                    ally['Online'],
                    ally['Position'],
                    ally['Name'],
                    url
                )
                mycursor.execute(sql)
                mydb.commit()
                if mycursor.rowcount != 0:
                    continue
                sql = "INSERT INTO users (points,bases,rank,is_online,position,username,alliance) VALUES({0},{1},{2},'{3}','{4}','{5}',{6})".format(
                    ally['Points'],
                    ally['Bases'],
                    ally['Rank'],
                    ally['Online'],
                    ally['Position'],
                    ally['Name'],
                    url
                )
                mycursor.execute(sql)
                mydb.commit()
            except:
                pass
            try:
                batlle_report = requests.post("https://www.baseattackforce.com/charts.php?a={0}&more=1".format(ally['Name']), cookies=r1.cookies)
                battle_soup = BeautifulSoup(batlle_report.content, 'html.parser')
                user_battles = []
                battle_rows = battle_soup.find_all('table')[-1].find_all('tr')
            except:
                pass
            try:
                for battle in battle_rows:
                    battle_infs=battle.find_all('td')
                    date = battle_infs[0].get_text().replace(':','-')
                    time = battle_infs[1].get_text().replace('.',':')
                    datetime = "20{0}-{1}-{2} {3}".format(date.split('.')[-1],date.split('.')[-2],date.split('.')[-3],time)
                    if compare_datetime_less(result,datetime):
                        continue
                    map = battle_infs[2].get_text().replace('MAP','')
                    attacker = battle_infs[3].get_text()
                    victim = battle_infs[5].get_text()
                    sql = "INSERT INTO battles (Map,Attacker,Victim,Datetime) VALUES({0},'{1}','{2}','{3}')".format(
                        map,
                        attacker,
                        victim,
                        datetime
                    )
                    mycursor.execute(sql)
                    mydb.commit()
            except:
                pass