import time
import os
import sys
from scipy.spatial.transform import Rotation
import numpy as np
from non_ros_scripts.openai_interface_goal import GPT_Interface_Goal

from helper_functions.load_key_from_txt import load_key

# Assuming the ai_interface package is in the parent directory
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)


class ChatGPTNode:
    def __init__(self):
        '''Initialize the ROS node and set up subscribers and publishers'''

        # self.key = ''
        self.key = load_key()
        self.model = "gpt-4"

        print(self.key)

        self.openai_interface = GPT_Interface_Goal(key=self.key, model=self.model)

        self.TwistMsg = {"linear": {'x': 0.0, 'y': 0.0, 'z': 0}, "angular": {'x': 0.0, 'y': 0.0, 'z': 0.0}}
        self.PoseStampedMsg = {"position": {'x': 0.0, 'y': 0.0, 'z': 0.0},
                               "orientation": {'x': 0.0, 'y': 0.0, 'z': 0.0}}  # maybe add w

    def execute_command(self, command: str, convert_to_degrees: bool = False):
        interface = self.openai_interface.get_response(prompt=command)

        if isinstance(interface, dict):
            interface_data = interface["format"]
            if convert_to_degrees:
                command = self.convert_to_PoseStamped_euler_degrees(interface_data)
            else:
                command = self.convert_to_PoseStamped(interface_data)

            print(f' Received Command: {command}')

    def update_twist_msg(self, twist_dict):

        self.TwistMsg = twist_dict
        return self.TwistMsg

    def convert_to_PoseStamped(self, twist_dict):

        # Check for 'linear' and 'angular' keys in twist_dict
        linear = twist_dict.get('position', {})
        angular = twist_dict.get('orientation', {})

        print(linear)
        # Check and assign linear values
        if 'x' in linear:
            self.PoseStampedMsg['position']['x'] = float(linear['x'])
        if 'y' in linear:
            self.PoseStampedMsg['position']['y'] = float(linear['y'])
        if 'z' in linear:  # Check for 'linear_z'
            self.PoseStampedMsg['position']['z'] = float(linear['z'])

        # Check and assign angular values
        if 'x' in angular:  # Check for 'angular_x'
            self.PoseStampedMsg['orientation']['x'] = float(angular['x'])
        if 'y' in angular:  # Check for 'angular_y'
            self.PoseStampedMsg['orientation']['y'] = float(angular['y'])
        if 'z' in angular:
            self.PoseStampedMsg['orientation']['z'] = float(angular['z'])

        return self.PoseStampedMsg

    def convert_to_PoseStamped_euler_degrees(self, twist_dict):

        # Check for 'linear' and 'angular' keys in twist_dict
        linear = twist_dict.get('position', {})
        angular = twist_dict.get('orientation', {})

        # Convert the dictionary orientation into a numpy array with two columns as done here:
        # https://stackoverflow.com/questions/15579649/python-dict-to-numpy-structured-array
        # Then keep the second column which includes the numerical values of the 4 quaternions
        orientation_quat = np.array(list(angular.items()))[:, 1]

        # Construct a Rotation and then convert to euler
        rotquat = Rotation.from_quat(orientation_quat)
        roteul = rotquat.as_euler('xyz', degrees=True)
        angular_degrees = {'x': roteul[0], 'y': roteul[1], 'z': roteul[2]}

        # Check and assign linear values
        if 'x' in linear:
            self.PoseStampedMsg['position']['x'] = float(linear['x'])
        if 'y' in linear:
            self.PoseStampedMsg['position']['y'] = float(linear['y'])
        if 'z' in linear:  # Check for 'linear_z'
            self.PoseStampedMsg['position']['z'] = float(linear['z'])

        # Check and assign angular values
        if 'x' in angular:  # Check for 'angular_x'
            self.PoseStampedMsg['orientation']['x'] = float(angular_degrees['x'])
        if 'y' in angular:  # Check for 'angular_y'
            self.PoseStampedMsg['orientation']['y'] = float(angular_degrees['y'])
        if 'z' in angular:
            self.PoseStampedMsg['orientation']['z'] = float(angular_degrees['z'])

        return self.PoseStampedMsg


def main():
    chatnode = ChatGPTNode()

    robot_command = 'Go to position [-35, 20, 40] facing at 45 degrees in the north-east direction.'
    chatnode.execute_command(robot_command, convert_to_degrees=True)

    # discuss the problem below with orientation
    robot_command2 = 'Now go back in x by 13 and add 5 degrees clockwise to your previous orientation towards north-east'
    chatnode.execute_command(robot_command2, convert_to_degrees=True)


if __name__ == '__main__':
    main()
