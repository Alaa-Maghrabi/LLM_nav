
# **LLM_Nav**
**An AI controller that uses text prompts to control your robot using ROS Noetic.**

## **Overview**
LLM_Nav is a ROS node designed to subscribe to a ROS topic (/speech_recognition/final_result) of type `String` and publish to a ROS topic (/goal) of type `PoseStamped`. This allows the robot to interpret natural language commands and navigate accordingly.

## **Prerequisites**
- ROS Noetic installed on your system
- A working OpenAI API key

## **Setup Instructions**

### Cloning the Repository
```bash
git clone https://github.com/Alaa-Maghrabi/LLM_Nav.git
cd ~/LLM_Nav
```

### Creating and Activating a Virtual Environment
```bash
conda create --name LLM_nav python=3.8
conda activate LLM_nav
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

### Updating the GPT Key
Update your OpenAI API key in the `LLM_nav.launch` file.

## **Running the Project**

### Starting the ROS Node
Ensure your ROS environment is set up and then run the launch file:
```bash
source /opt/ros/noetic/setup.bash
roslaunch LLM_Nav LLM_nav.launch
```

## **Main Components**

### `main.py`
- Initializes the ROS node.
- Subscribes to `/speech_recognition/final_result`.
- Publishes to `/goal` of type `PoseStamped`.
- Uses the `GPT_Interface_Goal` class to interact with OpenAI's GPT model.

### `openai_interface_goal.py`
- Defines the `GPT_Interface_Goal` class.
- Interfaces with OpenAI's GPT model to interpret natural language commands.
- Converts commands into ROS-compatible messages.
