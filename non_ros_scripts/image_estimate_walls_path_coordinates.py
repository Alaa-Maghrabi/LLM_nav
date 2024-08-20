# With the available models, providing a BEV of a flat is not possible. I am trying to pass a BEV image and ask the
# model to provide the coordinates of A, B, C. However, it is not capable of doing so. A more tailored model is needed.
# Here, we pass the image and the coordinates of A, B, C, then the walls are detected using opencv (no idea how
# accurate that would be) and then find the path.

# Note, use image_estimate_walls_path_coordinates.py can be used to obtain a list of coordinates instead of a string
# as the model output

#  THIS CODE IS INCOMPLETE BECAUSE I CANNOT PARSE THE STRING INTO A LIST OF ELEMENTS

try:
    from langchain import LLMChain
    from langchain.chat_models import ChatOpenAI
    from langchain.prompts import PromptTemplate
    from PIL import Image
    from transformers import BlipProcessor, BlipForConditionalGeneration
    import torch
    import json

    import cv2
    import numpy as np

except ImportError as e:
    raise e

# Initialize the BLIP processor and model
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")


# Step 1: Detect Points A, B, and C - this function can replace the manual definition of coordinates A, B etc
def detect_circles(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    circles = cv2.HoughCircles(
        image,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=30,
        param1=50,
        param2=30,
        minRadius=10,
        maxRadius=30
    )

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        return circles
    else:
        return []


def detect_walls_and_doors(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    edges = cv2.Canny(image, 50, 150)

    # Detect lines using HoughLines
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=50, maxLineGap=10)
    walls = []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            walls.append(((x1, y1), (x2, y2)))

    # Detect circles as doors
    circles = detect_circles(image_path)  # Assuming this function is already defined
    doors = circles  # Just as an example

    return walls, doors


def visualize_walls_and_doors(image_path, walls, doors, output_path='output_image.png'):
    # Load the image
    image = cv2.imread(image_path)

    # Draw walls in red
    for (start, end) in walls:
        cv2.line(image, start, end, (0, 0, 255), 2)  # Red color in BGR

    # Draw doors in green
    for (x, y) in doors:
        cv2.circle(image, (x, y), 5, (0, 255, 0), -1)  # Green color in BGR

    # Save or display the result
    cv2.imwrite(output_path, image)
    cv2.imshow('Walls and Doors Visualization', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# Function to process the image and generate a description
def describe_image(image_path):
    try:
        image = Image.open(image_path)
        inputs = processor(images=image, return_tensors="pt")
        out = model.generate(**inputs)
        description = processor.decode(out[0], skip_special_tokens=True)
        return description
    except Exception as e:
        return str(e)


def get_path(start_point_idx, end_point_idx):
    key = ""
    image_path = "/home/spyros/Elm/LLM_nav/non_ros_scripts/example_room.png"

    # Example usage
    walls, doors = detect_walls_and_doors(image_path)

    # visualize_walls_and_doors(image_path, walls, doors)
    # print("Detected Walls:", walls)
    # print("Detected Doors:", doors)

    # Generate the image description
    description = describe_image(image_path)
    print("Generated Image Description:", description)

    # Initialize the language model
    llm = ChatOpenAI(model_name="gpt-4", openai_api_key=key)


    # Coordinates of points A and B
    coordinates_A = (146, 102)
    coordinates_B = (118, 272)
    coordinates_C = (530, 106)
    coordinates_Start = (357, 336)  # start at the door on the bottom line
    points_of_interest = [coordinates_A, coordinates_B, coordinates_C, coordinates_Start]
    start_point = points_of_interest[start_point_idx]
    end_point = points_of_interest[end_point_idx]

    door1 = (150, 175)
    door2 = (188, 277)
    door3 = (470, 188)
    doors = [door1, door2, door3]  # Manually define them because opencv function is not working well

    #########################################################################################################
    # Template
    prompt_template = PromptTemplate.from_template("""
            You are given a 2D floor plan with the following coordinates:
            - Point A: {coordinates_A}
            - Point B: {coordinates_B}
            - Point C: {coordinates_C}
            - Start Point: {coordinates_Start}

            Walls are represented by the following line segments (cannot be crossed):
            {walls}

            Doors are represented by the following points (can be used to pass through):
            {doors}

            The image scale is such that each pixel represents 1 mm. Based on this information, please provide a list of 2D coordinates (in pixels) that represent the path from the start point to the end point. The path should be sequential, starting with the start point, followed by the next point, and so on, until the end point. The coordinates should avoid walls and make use of doors where applicable.

            Here is a description of the image: '{description}'

            Navigation Request: From {start_point} to {end_point}

            Please format your response as a JSON array of coordinates, e.g., [[x1, y1], [x2, y2], ...].
        """)
    # Create an instance of the LLMChain with the prompt template
    navigation_chain = LLMChain(llm=llm, prompt=prompt_template)

    ##################################################################################################
    # Inputs for navigation

    # Request instructions based on dynamic start and end points
    inputs = {
        "description": description,
        "coordinates_A": coordinates_A,
        "coordinates_B": coordinates_B,
        "coordinates_C": coordinates_C,
        "coordinates_Start": coordinates_Start,
        "walls": walls,
        "doors": doors,
        "start_point": start_point,
        "end_point": end_point
    }
    result = navigation_chain.run(inputs)

    # Parse the result to get a list of coordinates
    try:
        # Assume the result is a JSON string representing an array of coordinates
        path_coordinates = json.loads(result)  # Convert the JSON string to a Python list
        return path_coordinates
    except json.JSONDecodeError as e:
        print("Error parsing the JSON result:", e)
        return []


def main():
    # The locations are [A, B, C, Starting_point], e.g. a request from 0 to 2 will be from A to C
    # Get navigation instructions from Start to A
    start_point = 0
    end_point = 1
    instructions_from_Start_to_A, image_path, doors, walls = get_path(start_point, end_point)

    # Get navigation instructions from Start to B
    start_point = 0
    end_point = 2
    instructions_from_Start_to_B, _, _, _ = get_path(start_point, end_point)

    # Get navigation instructions from B to C
    start_point = 1
    end_point = 2
    instructions_from_B_to_C, _, _, _ = get_path(start_point, end_point)

    print("Navigation Instructions from Start to A:", instructions_from_Start_to_A)
    print("Navigation Instructions from Start to B:", instructions_from_Start_to_B)
    print("Navigation Instructions from B to C:", instructions_from_B_to_C)
    visualize_walls_and_doors(image_path, walls, doors)


if __name__ == "__main__":
    main()
