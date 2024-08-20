# Currently, this code exists just to verify that the processor and model are capable of correctly describing a
# standard image. An apple is passed as an example, and the description should explain what the image shows. From here,
# a better model is needed in order to describe e.g. a bird's eye view of a flat.
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
    try:
        image = Image.open(image_path)
        inputs = processor(images=image, return_tensors="pt")
        out = model.generate(**inputs)
        description = processor.decode(out[0], skip_special_tokens=True)
        return description
    except Exception as e:
        return str(e)


def main():
    key = load_key()
    image_path = "/home/spyros/Elm/LLM_nav/non_ros_scripts/example_room.png"
    image_path = "/home/spyros/Elm/LLM_nav/non_ros_scripts/apple.png"

    prompt_template = PromptTemplate.from_template("""
        Based on the following detailed description of a 2D floor plan, provide the exact coordinates of points A, B, and C in meters:
        '{description}'
        Each pixel in the image corresponds to 1 mm. The output should be in meters and should provide numerical coordinates for each point.
    """)

    # Initialize the language model
    llm = ChatOpenAI(model_name="gpt-4", openai_api_key=key)

    image_chain = LLMChain(llm=llm, prompt=prompt_template)

    # Generate the image description
    description = describe_image(image_path)

    # Print the description to troubleshoot
    print("Generated Image Description:", description)

    # Check if the description is valid
    if not description or "error" in description.lower():
        raise ValueError("Failed to generate a valid description for the image.")

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
    # result = image_chain.run(inputs)
    # print(result)


if __name__ == "__main__":
    main()
