import qrcode
from PIL import Image, ImageDraw, ImageFont
import os
import argparse

def load_text(input_data):
    """Load text from a file or return the string itself if it's not a file."""
    if os.path.isfile(input_data):
        with open(input_data, 'r') as file:
            return file.read().strip()
    return input_data

def generate_qr_code(data, box_size=10, border=4):
    """Generate a QR code image from the given data."""
    qr = qrcode.QRCode(box_size=box_size, border=border)
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill="black", back_color="white").convert('RGB')

def create_meme(no_image_path, yes_image_path, upper_text, lower_text, upper_qr_data, lower_qr_data, output_path):
    # Load the images
    no_image = Image.open(no_image_path)
    yes_image = Image.open(yes_image_path)

    # Define the template size (2x the size of the largest image)
    template_width = max(no_image.width, yes_image.width) * 2
    template_height = max(no_image.height, yes_image.height) * 2
    template_size = (template_width, template_height)

    # Create a new blank image for the final meme template
    meme_template = Image.new("RGB", template_size, color=(255, 255, 255))

    # Place the no_image in the upper left quadrant
    meme_template.paste(no_image, (0, 0))

    # Place the yes_image in the lower left quadrant
    meme_template.paste(yes_image, (0, no_image.height))

    # Load and generate the QR codes
    upper_qr_code = generate_qr_code(load_text(upper_qr_data))
    lower_qr_code = generate_qr_code(load_text(lower_qr_data))

    # Resize the QR codes to be smaller
    new_qr_width = (template_width // 2) // 2
    new_qr_height = (template_height // 2) // 2
    upper_qr_code_resized = upper_qr_code.resize((new_qr_width, new_qr_height))
    lower_qr_code_resized = lower_qr_code.resize((new_qr_width, new_qr_height))

    # Calculate positions for the QR codes (ensuring they don't overlap with text)
    upper_right_position = (template_width // 2 + (template_width // 2 - new_qr_width) // 2, 100)
    lower_right_position = (template_width // 2 + (template_width // 2 - new_qr_width) // 2, template_height // 2 + 100)

    # Paste the QR codes into the meme template
    meme_template.paste(upper_qr_code_resized, upper_right_position)
    meme_template.paste(lower_qr_code_resized, lower_right_position)

    # Draw the text on the right-hand side of the meme
    draw = ImageDraw.Draw(meme_template)
    try:
        large_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 40)
    except IOError:
        large_font = ImageFont.load_default()

    # Calculate and draw the text centered in the upper right quadrant
    text1_width, text1_height = draw.textsize(upper_text, font=large_font)
    text1_x_centered = template_width // 2 + (template_width // 2 - text1_width) // 2
    draw.text((text1_x_centered, 10), upper_text, fill="black", font=large_font)

    # Calculate and draw the text centered in the lower right quadrant
    text2_width, text2_height = draw.textsize(lower_text, font=large_font)
    text2_x_centered = template_width // 2 + (template_width // 2 - text2_width) // 2
    draw.text((text2_x_centered, template_height // 2 + 10), lower_text, fill="black", font=large_font)

    # Draw black lines to segment the image both horizontally and vertically, ensuring they are on top of the images
    draw.line([(template_width // 2, 0), (template_width // 2, template_height)], fill="black", width=5)
    draw.line([(0, template_height // 2), (template_width, template_height // 2)], fill="black", width=5)

    # Save the final meme template
    meme_template.save(output_path)
    print(f"Final meme created and saved to {output_path}")

def add_qr_to_template(template_path, upper_qr_data, lower_qr_data, output_path):
    # Load the existing template
    meme_template = Image.open(template_path)

    # Generate the QR codes
    upper_qr_code = generate_qr_code(load_text(upper_qr_data))
    lower_qr_code = generate_qr_code(load_text(lower_qr_data))

    # Resize the QR codes to fit within the quadrants
    template_width, template_height = meme_template.size
    new_qr_width = (template_width // 2) // 2
    new_qr_height = (template_height // 2) // 2
    upper_qr_code_resized = upper_qr_code.resize((new_qr_width, new_qr_height))
    lower_qr_code_resized = lower_qr_code.resize((new_qr_width, new_qr_height))

    # Calculate positions for the QR codes
    upper_right_position = (template_width // 2 + (template_width // 2 - new_qr_width) // 2, 100)
    lower_right_position = (template_width // 2 + (template_width // 2 - new_qr_width) // 2, template_height // 2 + 100)

    # Paste the QR codes into the template
    meme_template.paste(upper_qr_code_resized, upper_right_position)
    meme_template.paste(lower_qr_code_resized, lower_right_position)

    # Save the updated meme template
    meme_template.save(output_path)
    print(f"QR codes added and meme saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a meme with QR codes.",
        epilog="Script written by David Maynor (dmaynor@gmail.com) Twitter/X: @dave_maynor"
    )
    
    parser.add_argument("--no-image", help="Path to the 'no' image for the upper left quadrant.")
    parser.add_argument("--yes-image", help="Path to the 'yes' image for the lower left quadrant.")
    parser.add_argument("--upper-text", help="Text for the upper right quadrant.")
    parser.add_argument("--lower-text", help="Text for the lower right quadrant.")
    parser.add_argument("--upper-qr", required=True, help="Text or file path for the upper right QR code.")
    parser.add_argument("--lower-qr", required=True, help="Text or file path for the lower right QR code.")
    parser.add_argument("--output", required=True, help="Path to save the final meme image.")
    parser.add_argument("--template", help="Path to a pre-existing template image. If provided, images and text options are ignored.")

    args = parser.parse_args()

    if args.template:
        add_qr_to_template(args.template, args.upper_qr, args.lower_qr, args.output)
    else:
        if not (args.no_image and args.yes_image and args.upper_text and args.lower_text):
            parser.error("When --template is not used, --no-image, --yes-image, --upper-text, and --lower-text are required.")
        create_meme(args.no_image, args.yes_image, args.upper_text, args.lower_text, args.upper_qr, args.lower_qr, args.output)


