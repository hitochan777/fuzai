import RPi.GPIO as GPIO
import time

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
    
    def angle_to_duty_cycle(self, angle):
        return 2 + (angle / 18)
    
    def rotate_to_angle(self, angle):
        if not (0 <= angle <= 180):
            raise ValueError("Angle must be between 0 and 180 degrees")
        
        try:
            duty = self.angle_to_duty_cycle(angle)
            self.servo.ChangeDutyCycle(duty)
            time.sleep(0.5)
            self.servo.ChangeDutyCycle(0)
            return True
        except Exception as e:
            raise RuntimeError(f"Servo control error: {str(e)}")
    
    def unlock(self):
        return self.rotate_to_angle(self.unlock_angle)
    
    def cleanup(self):
        self.servo.stop()
        GPIO.cleanup()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
