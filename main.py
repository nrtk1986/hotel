from geopy.geocoders import Nominatim
import requests
import re
import datetime
import pandas as pd
import os

## 地名から緯度経度を返す関数 ##
def geocoding(place):
    geolocator = Nominatim(user_agent="searchhotel")
    location = geolocator.geocode(place, timeout=10)
    if location is None:
        return
    else:
        latitude = location.latitude
        longitude = location.longitude
        return latitude, longitude


## 楽天トラベルAPIからデータを取得する関数 ##
def hotel_search(place, hotel_num, checkin, checkout, adult_num, child_num, insertDatetime):
    latitude, longitude = geocoding(place)

    url = "https://app.rakuten.co.jp/services/api/Travel/VacantHotelSearch/20170426"
    params = {'applicationId': os.environ["RAKTENTRAVEL_APP_ID"],
              'formatVersion': '2',
              'checkinDate': checkin,
              'checkoutDate': checkout,
              'adultNum': adult_num,
              'infantWithoutMBNum': child_num,
              'hotelNo': hotel_num,
              'latitude': latitude,
              'longitude': longitude,
              'squeezeCondition': 'breakfast',
              'searchRadius': '3',
              'searchPattern': '1',
              'responseType': 'large',
              'datumType': '1',
              'allReturnFlag': '1'}
    try:
        r = requests.get(url, params=params)
        content = r.json()
        error = content.get("error")
        if error is not None:
            msg = content["error_description"]
            return msg

        df = pd.DataFrame()
        hotels = content["hotels"]
        for i, hotel in enumerate(hotels):
            room_info = hotel[3]["roomInfo"][0]["roomBasicInfo"]
            cost_info = hotel[3]["roomInfo"][1]["dailyCharge"]
            _df_room = pd.DataFrame(room_info, index=[i]).drop("planContents", axis=1)
            _df_cost = pd.DataFrame(cost_info, index=[i])
            _df = pd.concat([_df_room, _df_cost], axis=1)
            df = pd.concat([df, _df], axis=0)

        # データの入力時刻を入れる
        df['insertDatetime'] = insertDatetime

        df = df[(df['roomClass'] == 'dbb') & (df['planId'] == 4890033)]

        write_sql(df)

    except:
        import traceback
        traceback.print_exc()
        return "API接続中に何らかのエラーが発生しました"


## SQLに書き込む関数 ##
def write_sql(df):
    import pandas as pd
    import psycopg2
    from sqlalchemy import create_engine

    engine = create_engine(os.environ["DATABASE_URL"])
    df.to_sql('ah_hos_karakusa_new', con=engine, if_exists='append', index=False)


## データの取得からSQLへの書き込みまで指示する ##A
# からくさホテル
startDate = datetime.datetime.strptime('2020-12-27', '%Y-%m-%d')
endDate = datetime.datetime.strptime('2021-01-02', '%Y-%m-%d')

date = datetime.date(startDate.year, startDate.month, startDate.day)

insertDatetime = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime('%Y-%m-%d %H:%M:%S')

# CSVに書き出す場合使用
# df_final = pd.DataFrame()

while date < datetime.date(endDate.year, endDate.month, endDate.day):
    s_startDate = date.strftime('%Y-%m-%d')
    s_endDate = (date + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

    hotel_search("新大阪", 176602, s_startDate, s_endDate, 2, 1, insertDatetime)

    # CSVに書き出す場合使用
    # df_final = pd.concat([df_final, hotel_search("新大阪",176602, s_startDate, s_endDate, 2, 1, insertDatetime)], axis=0)

    date = date + datetime.timedelta(days=1)



##herokuへのデプロイ
##参考：https://qiita.com/osakasho/items/527421ec483052055b34
