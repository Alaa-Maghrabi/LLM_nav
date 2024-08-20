# With the available models, providing a BEV of a flat is not possible. I am trying to pass a BEV image and ask the
# model to provide the coordinates of A, B, C. However, it is not capable of doing so. A more tailored model is needed.
# In image_estimate_robot_path.py, the same image is passed with the coordinates of A, B, C and a path is to be
# estimated.

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

    # Coordinates of points A and B
    coordinates_A = (146, 102)  # Replace with actual values, e.g., "(150, 200)"
    coordinates_B = (118, 272)  # Replace with actual values, e.g., "(300, 400)"

    # Define the PromptTemplate with f-strings to include variable values
    prompt_template = PromptTemplate.from_template(f"""
        The following 2D floor plan image contains points labeled A, B, and C. The coordinates of points A and B are given below.
        The coordinate axes start from the top left of the image, with the x axis pointing to the right and the y axis 
        increasing downwards.
        The image has each pixel representing 1 mm. Based on the known coordinates of A ({coordinates_A}) and B ({coordinates_B}),
        please identify and provide the pixel coordinates of point C, which is located on the same floor plan.
        Here is the description of the image:
        '{description}'
        Please provide the coordinates of point C in pixels.
    """)

    # Initialize the language model
    llm = ChatOpenAI(model_name="gpt-4", openai_api_key=key)

    image_chain = LLMChain(llm=llm, prompt=prompt_template)



    # Generate the image description
    description = describe_image(image_path)

    # Print the description to verify it
    print("Generated Image Description:", description)

    # Prepare the input dictionary with the updated description and known coordinates
    inputs = {
        "description": description,
        "coordinates_A": coordinates_A,
        "coordinates_B": coordinates_B
    }

    # Example manual description (modify with actual data if known)
    # manual_description = """
    #     The image is a 2D floor plan of an apartment. The coordinates for specific points are:
    #     - Point A is located at (x1, y1) mm from the top left corner.
    #     - Point B is located at (x2, y2) mm from the top left corner.
    #     - Point C is located at (x3, y3) mm from the top left corner.
    #     Each pixel in the image equals 1 mm.
    # """

    # Prepare the input dictionary with the description
    # inputs = {"description": description}
    #
    # # Run the chain with the inputs
    result = image_chain.run(inputs)
    print(result)


if __name__ == "__main__":
    main()
