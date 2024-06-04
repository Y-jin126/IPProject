import requests
import RPi.GPIO as GPIO
import time

# GPIO 설정
LED_PIN = 18
BUZZER_PIN = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setwarnings(False)

pwm = GPIO.PWM(BUZZER_PIN,262)

def get_data(url):
    headers = {
        'Accept': 'application/json',
        'X-M2M-RI': '12345',
        'X-M2M-Origin': 'SOrigin'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        json_response = response.json()
        return json_response['m2m:cin']['con']
    except requests.exceptions.RequestException as e:
        print(f'There was a problem: {e}')
        return None
    except KeyError as e:
        print(f'Key error: {e}')
        return None

if __name__ == '__main__':
    try:
        while True:
            weight_value = get_data('http://203.253.128.177:7579/Mobius/IPproject6/Weight/la')
            helmet_value = get_data('http://203.253.128.177:7579/Mobius/IPproject6/Helmet/la')

            if weight_value is not None and helmet_value is not None:
                print(f"Weight value: {weight_value}")
                print(f"Helmet value: {helmet_value}")

                if weight_value == '1' and helmet_value == '1':
                    GPIO.output(LED_PIN, GPIO.HIGH)  # LED 켜기
                    GPIO.output(BUZZER_PIN, GPIO.LOW)  # 부저 끄기
                    print("LED ON, Buzzer OFF")
                else:
                    GPIO.output(LED_PIN, GPIO.LOW)  # LED 끄기
                    GPIO.output(BUZZER_PIN, GPIO.HIGH)
                    print("LED OFF, Buzzer ON")  # 부저 켜기
                    pwm.start(50.0) 

            time.sleep(5)  # 5초 대기
    except KeyboardInterrupt:
        print("프로그램 종료")
    finally:
        pwm.stop()
        GPIO.cleanup()  # GPIO 설정 초기화
