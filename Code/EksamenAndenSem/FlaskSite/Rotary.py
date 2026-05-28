from gpiozero import RotaryEncoder, Button, LED
from threading import Timer
from time import sleep
import math
from flask import Flask
from Modelss import Winner, db
from ColorWho import start_threaded_spin, spin_finished_event
import os
import json

# Initialize the encoder and reset button
encoder = RotaryEncoder(a=16, b=15, wrap=False, max_steps=100000)
sleep(0.5)  # Short delay to ensure encoder is ready
encoder.steps = 0  # Reset steps to 0 at the start
reset_button = Button(14)
motor_clockwise = LED(23)

# Global variables
click_count = 0
measuring = False
start_click_count = 0
baseline_steps = 0  # Tracks the encoder position when the wheel is completely idle

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
db.init_app(app)

def start_measurement():
    global measuring, start_click_count
    print("First change detected! Starting 1.5-second timer...")
    measuring = True
    start_click_count = encoder.steps  # Capture exact starting point
    Timer(1.5, stop_measurement).start()

def stop_measurement():
    global measuring, start_click_count, click_count, baseline_steps
    
    # 1. Calculate the clicks immediately when the timer ends
    click_count = abs(encoder.steps - start_click_count)
    
    print(f"\n--- Measurement Complete ---")
    print(f"Total clicks in 1.5 seconds: {click_count}")
    print(f"----------------------------")
    
    # 2. Run the motor sequence
    motor_clockwise.on()
    print(f"Motor running for {0.7 * click_count + 1:.2f} seconds...")
    sleep(0.7 * click_count + 1)  
    motor_clockwise.off()
    
    # 3. Process file data
    try:
        with open("lifetimeSpins.json", "r") as f:
            current_lifetime_spins = json.load(f)
        print(f"Current Lifetime Spins: {current_lifetime_spins}")
    except Exception as e:
        print(f"Error reading lifetimeSpins.json: {e}")

    # 4. Wait for color sensor
    print("Waiting for color sensor to finish...")
    spin_finished_event.wait(timeout=10)
    sleep(5)

    # 5. Log to database
    if os.path.exists("WinnerData.json"):
        try:
            with open("WinnerData.json", "r") as f:
                data = json.load(f)
                TempWinner = data["winner"]
            print(f"TempWinner: {TempWinner}")
            
            with app.app_context():
                new_win = Winner(color=str(TempWinner), prize=str(click_count))
                db.session.add(new_win)
                db.session.commit()
                print("Logged win to database!")
            os.remove("WinnerData.json")
        except Exception as e:
            print(f"Error processing winner data: {e}")
    
    # --- RESET STATE FOR NEXT ROUND ---
    # Update our baseline to where the encoder is sitting right now
    baseline_steps = encoder.steps
    
    # ONLY unlock the system here at the very end of the sequence
    measuring = False
    print("Ready for next spin...\n")

def handle_rotation():
    global measuring, baseline_steps

    # If we are already running a spin or processing data, ignore ALL inputs
    if measuring:
        return  

    # Check if the wheel has moved more than 2 steps away from its idle baseline
    # Using abs() handles rotation safely without fighting internal variables
    if abs(encoder.steps - baseline_steps) > 2:
        start_measurement()
        start_threaded_spin()

def reset_system():
    global click_count, measuring, baseline_steps
    click_count = 0
    baseline_steps = encoder.steps
    measuring = False
    print("System reset!")

# Assign the events
encoder.when_rotated = handle_rotation
reset_button.when_pressed = reset_system

print("Ready. Rotate to begin count.")
import signal
signal.pause()