from PIL import Image, ImageDraw, ImageFont



def draw_bounding_boxes(file_path, bounding_boxes):
    
    img = Image.open(file_path)
    draw = ImageDraw.Draw(img)
    width, height = img.size

    
    try:
        font = ImageFont.truetype("fonts/Arial.ttf", 16)
    except IOError:
        font = ImageFont.load_default()

    for obj in bounding_boxes:
        label = obj["label"] 
        box = obj["bounding_box"] 

      
        ymin = int((box[0] / 1000) * height)
        xmin = int((box[1] / 1000) * width)
        ymax = int((box[2] / 1000) * height)
        xmax = int((box[3] / 1000) * width)

       
        draw.rectangle([xmin, ymin, xmax, ymax], outline="green", width=2)

        
        text = f"{label}"

        # Get the size of the text using getbbox()
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        text_x = xmin
        text_y = ymin - text_height if ymin - text_height > 0 else ymin + 5

        # Create a rectangle behind the text for better visibility
        draw.rectangle(
            [text_x, text_y, text_x + text_width, text_y + text_height], fill="green"
        )

        # Draw the label and confidence text
        draw.text((text_x, text_y), text, fill="white", font=font)

    return img
