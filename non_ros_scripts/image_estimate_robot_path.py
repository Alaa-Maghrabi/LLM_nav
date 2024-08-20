# With the available models, providing a BEV of a flat is not possible. I am trying to pass a BEV image and ask the
# model to provide the coordinates of A, B, C. However, it is not capable of doing so. A more tailored model is needed.
# In image_estimate_robot_path.py, the same image is passed with the coordinates of A, B, C and a path is to be
# estimated.

# This code WORKS but does not take into account walls and other obstacles. For that, use image_estimate_walls_path.py

try:
    from langchain import LLMChain
    from langchain.chat_models import ChatOpenAI
    from langchain.prompts import PromptTemplate
    from PIL import Image
    from transformers import BlipProcessor, BlipForConditionalGeneration
    import torch

except ImportError as e:
    raise e

# Initialize the BLIP processor and model
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")


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


def main():
    key = "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"
    image_path = "/home/spyros/Elm/LLM_nav/non_ros_scripts/example_room.png"

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

    # Define the PromptTemplate with f-strings to include variable values
    prompt_template = PromptTemplate.from_template(f"""
        You are given a 2D floor plan with the following coordinates for specific points:
        - Point A: {coordinates_A}
        - Point B: {coordinates_B}
        - Point C: {coordinates_C}

        The image scale is such that each pixel represents 1 mm. Based on the provided coordinates, please provide detailed steps to navigate to a specified point from a given starting point.

        Here is a description of the image: '{description}'

        Given a request to navigate to point A, please provide the step-by-step instructions to reach that point.
    """)

    # Create an instance of the LLMChain with the prompt template
    navigation_chain = LLMChain(llm=llm, prompt=prompt_template)

    # Prepare the input dictionary with the coordinates and description
    inputs = {
        "description": description,
        "coordinates_A": coordinates_A,
        "coordinates_B": coordinates_B,
        "coordinates_C": coordinates_C
    }

    # Request navigation instructions to point A
    request = "Please provide the steps to navigate to point A."
    inputs["request"] = request

    # Run the chain with the inputs
    result = navigation_chain.run(inputs)

    print("Navigation Instructions:", result)





if __name__ == "__main__":
    main()
