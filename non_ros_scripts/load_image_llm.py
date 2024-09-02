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
    key = load_key()
    image_path = "apple.png"

    # Initialize the language model
    # llm = ChatOpenAI(model_name="gpt-4", openai_api_key=key)
    # image_chain = LLMChain(llm=llm, prompt=prompt_template)

    # Since this is a basic image of an apple, you just need the BLIP description, since it is not then passed to
    # a different LLM for e.g. navigation
    description = describe_image(image_path)  # Generate the image description

    # Print the description to troubleshoot
    print("Generated Image Description:", description)

    # Check if the description is valid
    if not description or "error" in description.lower():
        raise ValueError("Failed to generate a valid description for the image.")


if __name__ == "__main__":
    main()
