# With the available models, here we explore if it is possible to directly describe all points of interest in a BEV
# image using an LLM without and preprocessing. Spoiler alert, it does not work.
# In image_estimate_robot_path.py, the same image is passed with the coordinates of A, B, C and a path is to be
# estimated.

try:
    from langchain import LLMChain
    from langchain.chat_models import ChatOpenAI
    from langchain.prompts import PromptTemplate
    from PIL import Image
    from transformers import BlipProcessor, BlipForConditionalGeneration
    import torch

    from helper_functions.load_key_from_txt import load_key

except ImportError as e:
    raise e

# Initialize the BLIP processor and model
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")


# Function to process the image and generate a description
def describe_image(image_path):
    """
    #TODO: Find the link to this code that was provided online and tweaked to your needs

    :param image_path: a string to the location of the image to be used
    :return: a text description of the provided image
    """
    try:
        image = Image.open(image_path)
        inputs = processor(images=image, return_tensors="pt")
        out = model.generate(**inputs)
        description = processor.decode(out[0], skip_special_tokens=True)
        return description
    except Exception as e:
        return str(e)


def main():
    # key = ""
    key = load_key()
    image_path = "example_room.png"

    # Generate the image description
    description = describe_image(image_path)  # For the BEV image, this is gibberish, it's just random letters

    # Coordinates of points A and B
    # Note, these were extracted by loading the image in a pixel locator online and just hovering over the points
    coordinates_A = (146, 102)
    coordinates_B = (118, 272)

    # Define the PromptTemplate with f-strings to include variable values
    prompt_template = PromptTemplate.from_template(f"""
        The following 2D floor plan image contains points labeled A, B, and C. The coordinates of points A and B are given below.
        The coordinate axes start from the top left of the image, with the x axis pointing to the right and the y axis 
        increasing downwards.
        The image has each pixel representing 1 mm. Based on the known coordinates of A ({coordinates_A}) and B ({coordinates_B}),
         identify and provide the pixel coordinates of point C, which is located on the same floor plan.
        Here is the description of the image:
        '{description}'
        Please provide the coordinates of point C in pixels.
    """)

    # Initialize the language model
    llm = ChatOpenAI(model_name="gpt-4", openai_api_key=key)

    # Fuse the LLM and the prompt template
    image_chain = LLMChain(llm=llm, prompt=prompt_template)

    # Print the description to verify it
    print("Generated Image Description:", description)

    # Prepare the input dictionary with the updated description and known coordinates
    inputs = {
        "description": description,
        "coordinates_A": coordinates_A,
        "coordinates_B": coordinates_B
    }

    result = image_chain.run(inputs)
    print(result)


if __name__ == "__main__":
    main()
