import magicbot
from wpilib import \
    SpeedControllerGroup, \
    DoubleSolenoid, \
    ADXRS450_Gyro, \
    Joystick, \
    run, \
    DigitalInput, \
    AnalogPotentiometer, \
    Talon, \
    SmartDashboard, \
    Relay
from ctre import WPI_TalonSRX
from wpilib.drive import DifferentialDrive
from components.driver import Driver, GearMode
from components.lifter import Lifter, MovementDir
from utilities import truncate_float, normalize_range
from components.gripper import Gripper, GripState, GripLiftState



class Jessica(magicbot.MagicRobot):
    driver: Driver
    lifter: Lifter
    gripper: Gripper

    # Create motors and stuff here
    def createObjects(self):
        # driver component setup
        left_front = WPI_TalonSRX(4)
        left_rear = WPI_TalonSRX(3)
        right_front = WPI_TalonSRX(2)
        right_rear = WPI_TalonSRX(1)
        left = SpeedControllerGroup(left_front, left_rear)
        right = SpeedControllerGroup(right_front, right_rear)

        # driver component dependencies
        self.drive_train = DifferentialDrive(left, right)
        self.left_encoder_motor = left_front
        self.right_encoder_motor = right_rear
        self.gear_solenoid = DoubleSolenoid(0, 1)
        self.driver_gyro = ADXRS450_Gyro()

        # lifter component dependencies
        self.elevator_motor = WPI_TalonSRX(5)
        self.elevator_bottom_switch = DigitalInput(9)

        self.carriage_motor = WPI_TalonSRX(6)
        self.carriage_bottom_switch = DigitalInput(2)
        self.carriage_top_switch = DigitalInput(1)
        self.carriage_pot = AnalogPotentiometer(0)

        # gripper component dependencies
        self.claw_left_motor = Talon(0)
        self.claw_right_motor = Talon(1)
        self.claw_open_solenoid = DoubleSolenoid(2, 3)
        self.claw_up_limit = DigitalInput(0)
        self.claw_lift_motor = Relay(0)

        # controllers
        self.controller = Joystick(0)
        self.operator = Joystick(1)
        self.el_mode = False
    
    # Init: Called when mode starts; optional 
    # Periodic: Called on each iteration of the control loop
    def autonomousInit(self):
        self.driver.set_gear(GearMode.LOW)
    
    def autonomousPeriodic(self):
        pass

    def teleopInit(self):
        self.driver.set_gear(GearMode.LOW)
        self.curve = True
    
    def teleopPeriodic(self):
        left_y = truncate_float(-self.controller.getRawAxis(1))
        right_x = truncate_float(self.controller.getRawAxis(2))
        right_y = truncate_float(-self.controller.getRawAxis(5))

        # use options to toggle curve and tank drive
        if self.controller.getRawButtonPressed(10):
            self.curve = not self.curve

        # use curve drive or tank drive
        if self.curve:
            self.driver.set_curve(left_y, right_x)
        else:
            self.driver.set_tank(left_y, right_y)

        # elevator controls
        l2 = normalize_range(self.operator.getRawAxis(3), -1, 1, 0, 1)
        r2 = normalize_range(self.operator.getRawAxis(4), -1, 1, 0, 1)
        b_speed = -l2 + r2

        # touch pad toggles gear mode
        if self.controller.getRawButtonPressed(14):
            self.driver.toggle_gear()

        # grip elevator motor with l1 and r1
        if self.controller.getRawButton(5):
            self.gripper.set_lift_state(GripLiftState.DOWN)
        elif self.controller.getRawButton(6):
            self.gripper.set_lift_state(GripLiftState.UP)
        else:
            self.gripper.set_lift_state(GripLiftState.STOP)

        # if self.controller.getRawButtonPressed(2):
        #     self.el_mode = not self.el_mode

        # if self.el_mode:
        #     self.lifter.move_elevator(b_speed)
        #     self.lifter.move_carriage(0)
        # else:
        #     self.lifter.move_carriage(b_speed)
        #     self.lifter.move_elevator(0)

        SmartDashboard.putNumber("controller/direction", self.controller.getDirectionDegrees())
        SmartDashboard.putNumber("controller/pov", self.controller.getPOV())

        # elevator control with up and down on d-pad
        if self.operator.getPOV() == 0:
            self.lifter.move(MovementDir.UP)
        elif self.operator.getPOV() == 180:
            self.lifter.move(MovementDir.DOWN)
        else:
            self.lifter.move(MovementDir.STOP)

        # use triangle to open and close gripper
        if self.operator.getRawButtonPressed(4):
            self.gripper.toggle_open()

        # use square to shoot based on the speed from r2
        # use x to pull and fixed speed
        if self.operator.getRawButton(1):
            self.gripper.set_grip_speed(r2)
            self.gripper.set_grip_state(GripState.PUSH)
        elif self.operator.getRawButton(2):
            self.gripper.set_grip_speed(self.gripper.default_speed)
            self.gripper.set_grip_state(GripState.PULL)
        else:
            self.gripper.set_grip_state(GripState.STOP)



if __name__ == '__main__':
    print("hello world")
    run(Jessica)
