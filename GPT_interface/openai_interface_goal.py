from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
import os
import sys
import glob
import json
from typing import Any

# Assuming the ai_interface package is in the parent directory
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

class GPT_Interface_Goal:
    def __init__(self, key: str, model: str):
        self.chat = ChatOpenAI(openai_api_key=key, temperature=0.7, model=model)
        
        self.interfaces = ""
        self.curr_x = 0
        self.curr_y = 0

        # Filter out the entries that are directories
        msg_dir = os.path.join(parent_dir, "msg")  # Path to the 'msg' directory
        messages = glob.glob(os.path.join(msg_dir, "Pose.msg"))  # Use absolute path

        for msg in messages:
            separator = "<msg:" + msg.split(".msg")[0][-4:] + ">"
            with open(msg, 'r') as rd:
                self.interfaces += separator + rd.read() + separator +"\n"
    
    def correct_output(self, input_string):

        dict_strings = input_string.strip().split('\n')
        list_of_dicts = []

        for dict_string in dict_strings:
            dict_dict = json.loads(dict_string)  # Convert string to dictionary using JSON
            list_of_dicts.append(dict_dict)

        result_string = json.dumps(list_of_dicts)

        return result_string
    
    def remove_nbr(self, input_string):

        list_strings = input_string.split(' + ')
        output_list = []

        for list_string in list_strings:
            count = 1
            if '*' in list_string:
                list_string_parts = list_string.split('*')
                count = int(list_string_parts[1].strip())
                list_string = list_string_parts[0]
            
            dict_list = json.loads(list_string)
            
            for _ in range(count):
                output_list.extend(dict_list)

        result_string = json.dumps(output_list, indent=4)  # Convert list of dictionaries to JSON string
        return result_string

    def get_response(self, prompt: str) -> Any:
        system_template = ('''
            Following are the format of the interfaces in ROS delimited with their respective interface_type:interface_name as the tags.
            {interfaces_format}

            MUST Return a python dict of the interface required in order to reach the user's goals in ROS with no explanation. Goals will be delimited by the <prompt> tags.
            
            The dict should be of the following format:
            {output_format} (only consider the values in to_be_published and take respective interface_type from the given description), the format key in the dict only include the position and orientation
            All the properties of the messages should be enclosed within double quotes. Do not include anything else.
            
            The dict value corresponds to the goal that needs to be reached, simplify all the moves dicted and conclude with the final coordinates the goal needs to be at.
            The final coordinates need to summarise the whole movement dicted in the prompt, knowing that the X axis is for frontal movement (front, back) and Y axis is for side movement (right, left)
            Do not add any explanation. 
        ''')
    
        human_template = "<prompt>{prompt}<prompt>"
        
        system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
        print(self.interfaces)
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        chat_prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )
        '''Format of the response given by ChatGPT'''
        output_format = '''{"category": msg, "type": interface_type, "format": to_be_published}'''
        
        response = self.chat(
            chat_prompt.format_prompt(
                interfaces_format=self.interfaces, output_format=output_format, prompt = prompt
            ).to_messages()
        ).content

        print(response)
        ret_ans = json.loads(response.replace("'", '"'))
        self.curr_x += float(ret_ans["format"]["position"]["x"])
        self.curr_y += float(ret_ans["format"]["position"]["y"])

        ret_ans["format"]["position"]["x"] = self.curr_x
        ret_ans["format"]["position"]["y"] = self.curr_y

        return ret_ans
