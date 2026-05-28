import time
import threading
from gpiozero import DigitalInputDevice, OutputDevice, LED
import json

s2 = OutputDevice(24)
s3 = OutputDevice(25)
out_pin = DigitalInputDevice(17, pull_up=True)

red_led = LED(27)
green_led = LED(22)
blue_led = LED(18)
jackpot_led = LED(26)

JACKPOT_THRESHOLD = 55

is_spinning = False

spin_finished_event = threading.Event()

def read_sensor(s2_val, s3_val):
    s2.value = s2_val
    s3.value = s3_val
    time.sleep(0.02)
    
    count = 0
    start = time.time()
    last_state = out_pin.value
    
    while time.time() - start < 0.05:
        curr = out_pin.value
        if curr == 1 and last_state == 0:
            count = count + 1
        last_state = curr
        
        
    return count


def check_current_color():
    r = read_sensor(0, 0)
    g = read_sensor(1, 1)
    b = read_sensor(0, 1)
    
    if r-10 < JACKPOT_THRESHOLD and g+15 < JACKPOT_THRESHOLD and b < JACKPOT_THRESHOLD:
        return "BLACK"
    elif g+15 > r and g > b:
        return "GREEN"
    elif b > r and b > g:
        return "BLUE"
    else:
        return "RED"


def turn_on_single_led(color_name):
    red_led.off()
    green_led.off()
    blue_led.off()
    jackpot_led.off()
    
    if color_name == "BLACK":
        jackpot_led.on()
    elif color_name == "GREEN":
        green_led.on()
    elif color_name == "BLUE":
        blue_led.on()
    elif color_name == "RED":
        red_led.on()


def run_wheel_sequence():
    global is_spinning
    spin_finished_event.clear()
    if is_spinning:
        return
        
    is_spinning = True
    print("🎡 SPINNING! Flashing LEDs...")
    
    for _ in range(30):
        turn_on_single_led("RED")
        time.sleep(0.1)
        turn_on_single_led("GREEN")
        time.sleep(0.1)
        turn_on_single_led("BLUE")
        time.sleep(0.1)
        turn_on_single_led("BLACK")
        time.sleep(0.1)
        
    print("🛑 STOPPING! Checking final winner...")
    
    red_led.off()
    green_led.off()
    blue_led.off()
    jackpot_led.off()
    time.sleep(0.1)
    
    red_count = 0
    green_count = 0
    blue_count = 0
    black_count = 0
    
    for _ in range(3):
        detected = check_current_color()
        if detected == "RED":
            red_count = red_count + 1
        elif detected == "GREEN":
            green_count = green_count + 1
        elif detected == "BLUE":
            blue_count = blue_count + 1
        elif detected == "BLACK":
            black_count = black_count + 1
        time.sleep(0.01)
            
    highest_score = max(red_count, green_count, blue_count, black_count)
    
    if highest_score == red_count:
        winner = "RED"
        red_led.on()
    elif highest_score == green_count:
        winner = "GREEN"
        green_led.on()
    elif highest_score == blue_count:
        winner = "BLUE"
        blue_led.on()
    elif highest_score == black_count:
        winner = "BLACK"
        jackpot_led.on()
    else:
        winner = "RED"
        red_led.on()
        
    turn_on_single_led(winner)
    print("=== FINAL WINNER IS: " + winner + " ===\n")
    time.sleep(5)
    
    is_spinning = False
    result = {"winner": winner}
    

    with open("WinnerData.json", "w") as f:
        json.dump(result, f)

    with open("lifetimeSpins.json", "r") as f:
        lifetimeSpins = json.load(f)

    lifetimeSpins["lifetimeSpins"] += 1

    with open("lifetimeSpins.json", "w") as f:
        json.dump(lifetimeSpins, f)

    spin_finished_event.set()
    return winner

def start_threaded_spin():
    thread = threading.Thread(target=run_wheel_sequence)
    
    thread.start()
    


