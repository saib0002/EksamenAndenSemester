from gpiozero import PWMOutputDevice
from time import sleep

# Define the pin (GPIO 23)
motor = PWMOutputDevice(23)

try:
    print("Motor starting at 50% speed...")
    # value ranges from 0.0 to 1.0 (0.5 is 50% duty cycle)
    motor.value = 1
    
    # Run for 5 seconds
    sleep(5)
    
    print("Stopping motor.")
    motor.off()

except KeyboardInterrupt:
    # Safely turn off if you stop the script with Ctrl+C
    motor.off()
    print("Script interrupted, motor stopped.")