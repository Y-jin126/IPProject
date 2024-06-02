from gpiozero import LED, DistanceSensor
from gpiozero.pins.pigpio import PiGPIOFactory
import spidev
from time import sleep

# Raspberry Pi에 연결된 PiGPIOFactory 사용
factory = PiGPIOFactory()

# LED 설정
red_led = LED(10)

# 초음파 센서 설정
ultrasonic_front = DistanceSensor(echo=17, trigger=4)
ultrasonic_back = DistanceSensor(echo=27, trigger=22)

# SPI 인터페이스 설정
spi = spidev.SpiDev()
spi.open(0, 0)  # (버스, 디바이스)

# 압력 센서 설정
def read_fsr():
    spi.max_speed_hz = 1000000
    adc = spi.xfer2([1, 0b10000000, 0])  # 채널 0에서 아날로그 값을 읽음
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

# 임계값 설정
distance_threshold = 0.01  # 1cm (단위: m)
fsr_threshold = 1000  # FSR-402의 임계값 (예: 1000으로 설정)

# 작동 상태 변수
is_stopped = False

# 작동 정지 함수
def stop_operation():
    global is_stopped
    red_led.on()
    is_stopped = True
    print("작동을 멈춥니다.")

# 작동 재개 함수
def start_operation():
    global is_stopped
    red_led.off()
    is_stopped = False
    print("작동을 재개합니다.")

# 메인 루프
while True:
    # 압력 센서 값 읽기
    fsr_value = read_fsr()

    # 초음파 센서 값 읽기
    distance_front = ultrasonic_front.distance
    distance_back = ultrasonic_back.distance

    print(f"압력 센서 값: {fsr_value}")
    print(f"앞쪽 초음파 센서 거리: {distance_front:.2f}m")
    print(f"뒤쪽 초음파 센서 거리: {distance_back:.2f}m")

    # 조건에 따라 작동 제어
    if (distance_front < distance_threshold or distance_back < distance_threshold):
        if not is_stopped:
            stop_operation()
    elif fsr_value > fsr_threshold:
        if not is_stopped:
            start_operation()
    elif is_stopped and fsr_value <= fsr_threshold and distance_front >= distance_threshold and distance_back >= distance_threshold:
        start_operation()

    sleep(1)
