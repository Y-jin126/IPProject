import requests
import gps
import time

#pressing Parking Button -> taking On/Off Data
def ParkingData():
    GetUrl = 'http://203.253.128.177:7579/Mobius/IPproject6/Parking/la'
    GetHeaders = {
        'Accept': 'application/json',
        'X-M2M-RI': '12345',
        'X-M2M-Origin': 'SOrigin'
    }

    try:
        r = requests.get(GetUrl, headers=GetHeaders)
        r.raise_for_status()
        jr = r.json()
        return jr['m2m:cin']['con']
    except Exception as exc:
        print('There was a problem: %s' % (exc))
        return None

#Measure the GPS Data
def GetGPSdata():
    session = gps.gps(mode=gps.WATCH_ENABLE)
    try:
        report = session.next()
        if report['class'] == 'TPV':
            latitude = getattr(report, 'lat', "Unknown")
            longitude = getattr(report, 'lon', "Unknown")
            return latitude, longitude
    except KeyError:
        pass
    except StopIteration:
        session = None
        print("GPSD has terminated")
    except Exception as e:
        print("GPS error: %s" % str(e))
    return None, None

 #Transmit GPS Data to Server
def SendGPSdata(latitude, longitude):
    PostUrl = 'http://203.253.128.177:7579/Mobius/IPproject6/GPS'
    PostHeaders = {
        'Accept':'application/json',
        'X-M2M-RI':'12345',
        'X-M2M-Origin':'SOrigin',
        'Content-Type':'application/vnd.onem2m-res+json; ty=4'
    }

    data = {
        "m2m:cin": {
            "con": f"{latitude},{longitude}"
        }
    }

    try:
        r = requests.post(PostUrl, headers=PostHeaders, json=data)
        r.raise_for_status()
        print('GPS data sent successfully:', data)
    except Exception as exc:
        print('There was a problem: %s' % (exc))

#Checking
if __name__ == "__main__":
    while True:
        # 1sec
        ServerData = ParkingData()
        if  ServerData == '1':
            latitude, longitude = GetGPSdata()
            if latitude != "Unknown" and longitude != "Unknown":
                SendGPSdata(latitude, longitude)
        time.sleep(1)
