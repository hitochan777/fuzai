import RPi.GPIO as GPIO
import time

high_time = {
    0: 0.5,
    45: 1,
    90: 1.5,
    135: 2,
    180: 2.5
}

class ServoController:
    def __init__(self, pin=18, frequency=50, unlock_angle=90):
        self.pin = pin
        self.frequency = frequency
        self.unlock_angle = unlock_angle
        self._setup_gpio()
    
    def _setup_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        self.servo = GPIO.PWM(self.pin, self.frequency)
        self.servo.start(0)
        # time.sleep(1)  # Give servo time to initialize
    
    def angle_to_duty_cycle(self, angle):
        return ((high_time[angle]) / (1000 / self.frequency)) * 100
    
    def rotate_to_angle(self, angle):
        if angle not in high_time:
            raise ValueError("Angle must be between 0 and 180 degrees")
        
        try:
            self.servo.ChangeDutyCycle(self.angle_to_duty_cycle(angle))
            time.sleep(1)
            return True
        except Exception as e:
            raise RuntimeError(f"Servo control error: {str(e)}")
    
    def unlock(self):
        print("start unlock")
        self.rotate_to_angle(90)
        self.rotate_to_angle(0)
        self.rotate_to_angle(180)
        # return self.rotate_to_angle(self.unlock_angle)
    
    def cleanup(self):
        self.servo.stop()
        GPIO.cleanup()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

if __name__ == "__main__":
   with ServoController() as servo:
       servo.unlock()
