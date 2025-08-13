import RPi.GPIO as GPIO
import time

class ServoController:
    def __init__(self, pin=18, frequency=50, unlock_angle=90):
        self.pin = pin
        self.frequency = frequency
        self.unlock_angle = unlock_angle
        
        # Servo pulse width constants (in milliseconds)
        self.min_pulse_width = 0.5   # 0.5ms for 0 degrees
        self.max_pulse_width = 2.5   # 2.5ms for 180 degrees
        self.period_ms = 1000 / frequency  # Period in milliseconds
        
        self._setup_gpio()
    
    def _setup_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        self.servo = GPIO.PWM(self.pin, self.frequency)
        self.servo.start(0)
    
    def angle_to_pulse_width(self, angle):
        """Convert angle (0-180) to pulse width in milliseconds"""
        if angle < 0:
            angle = 0
        elif angle > 180:
            angle = 180
        
        # Linear interpolation: 0° = 0.5ms, 180° = 2.5ms
        return self.min_pulse_width + (angle / 180.0) * (self.max_pulse_width - self.min_pulse_width)
    
    def angle_to_duty_cycle(self, angle):
        """Convert angle to duty cycle percentage"""
        pulse_width = self.angle_to_pulse_width(angle)
        return (pulse_width / self.period_ms) * 100
    
    def rotate_to_angle(self, angle):
        """Rotate servo to any angle between 0-180 degrees"""
        if not (0 <= angle <= 180):
            raise ValueError("Angle must be between 0 and 180 degrees")
        
        try:
            duty_cycle = self.angle_to_duty_cycle(angle)
            self.servo.ChangeDutyCycle(duty_cycle)
            print(f"Rotating to {angle}° (pulse: {self.angle_to_pulse_width(angle):.2f}ms, duty: {duty_cycle:.2f}%)")
            time.sleep(0.5)  # Reduced sleep time for smoother operation
            return True
        except Exception as e:
            raise RuntimeError(f"Servo control error: {str(e)}")
    
    def unlock(self):
        """Execute unlock sequence with precise control"""
        print("Starting unlock sequence...")
        
        self.rotate_to_angle(0)
        time.sleep(0.05)
        self.rotate_to_angle(60)
        time.sleep(0.05)
        self.rotate_to_angle(0)
        
        print("Unlock sequence completed")
    
    def calibration_mode(self):
        """Interactive calibration mode"""
        print("Servo Calibration Mode")
        print("Commands:")
        print("- Enter angle (0-180): Set servo to specific angle")
        print("- 'u': Unlock")
        print("- 'q': Quit")
        
        try:
            while True:
                user_input = input("\nEnter command: ").strip()
                
                if user_input.lower() == 'q':
                    break
                if user_input.lower() == 'u':           
                    self.unlock()
                else:
                    try:
                        angle = float(user_input)
                        if 0 <= angle <= 180:
                            self.rotate_to_angle(angle)
                        else:
                            print("Angle must be between 0 and 180")
                    except ValueError:
                        print("Invalid input. Enter a number, 'sweep', 'test', or 'q'")
        
        except KeyboardInterrupt:
            print("\nCalibration interrupted")
    
    def cleanup(self):
        self.servo.stop()
        GPIO.cleanup()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

if __name__ == "__main__":
    with ServoController() as servo:
        servo.calibration_mode()
