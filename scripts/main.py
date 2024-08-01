import rospy
import time
from geometry_msgs.msg import Twist, PoseStamped
from std_msgs.msg import String
import os
import sys

# Assuming the ai_interface package is in the parent directory
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

from GPT_interface.openai_interface_goal import GPT_Interface_Goal


class ChatGPTNode:
    def __init__(self):
        '''Initialize the ROS node and set up subscribers and publishers'''
        rospy.init_node('chat_gpt_node')

        self.key = rospy.get_param('~key', 'default_key')
        self.model = rospy.get_param('~model', 'gpt-4')

        print(self.key)
        
        self.openai_interface = GPT_Interface_Goal(key=self.key, model=self.model)

        rospy.Subscriber('/speech_recognition/final_result', String, self.listener_callback)
        
        # Initialize any publishers you need
        # self.twist_publisher = rospy.Publisher("/cmd_vel", Twist, queue_size=10)
        self.pose_publisher = rospy.Publisher("/goal", PoseStamped, queue_size=10)

    def listener_callback(self, data):
        rospy.loginfo('Received: ' + data.data)
        self.publish_command(data.data)

    def publish_command(self, voice_cmd):
        if not rospy.is_shutdown():
            # Get the response from the OpenAI interface
            interface = self.openai_interface.get_response(prompt=voice_cmd)

            if isinstance(interface, dict):
                interface_data = interface["format"]
                self.pose_publisher.publish(self.convert_to_PoseStamped(interface_data))
                print("DONE PUBLISHING")

                time.sleep(0.5)

    @staticmethod
    def convert_string_to_Twist(twist_dict):
        twist_msg = Twist()
        twist_msg.linear.x = float(twist_dict['linear']['x'])
        twist_msg.linear.y = float(twist_dict['linear']['y'])
        twist_msg.linear.z = float(twist_dict['linear']['z'])
        twist_msg.angular.x = float(twist_dict['angular']['x'])
        twist_msg.angular.y = float(twist_dict['angular']['y'])
        twist_msg.angular.z = float(twist_dict['angular']['z'])

        return twist_msg

    @staticmethod
    def convert_to_PoseStamped(twist_dict):
        pose_msg = PoseStamped()

        # Check for 'linear' and 'angular' keys in twist_dict
        linear = twist_dict.get('position', {})
        angular = twist_dict.get('orientation', {})

        print(linear)
        # Check and assign linear values
        if 'x' in linear:
            pose_msg.pose.position.x = float(linear['x'])
        if 'y' in linear:
            pose_msg.pose.position.y = float(linear['y'])
        if 'z' in linear:  # Check for 'linear_z'
            pose_msg.pose.position.z = float(linear['z'])

        # Check and assign angular values
        if 'x' in angular:  # Check for 'angular_x'
            pose_msg.pose.orientation.x = float(angular['x'])
        if 'y' in angular:  # Check for 'angular_y'
            pose_msg.pose.orientation.y = float(angular['y'])
        if 'z' in angular:
            pose_msg.pose.orientation.z = float(angular['z'])

        return pose_msg



def main():
    try:
        node = ChatGPTNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass


if __name__ == '__main__':
    main()
