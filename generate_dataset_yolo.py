import os
import random
import shutil
from PIL import Image
import uuid
import zipfile

def create_training_data(map_image_path, icons_folder, output_folder, num_images=10, val_split=0.2, icon_size=(50, 50)):
    # Remove existing train_data directory and create necessary directories
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
        
    os.makedirs(os.path.join(output_folder, 'images', 'train'), exist_ok=True)
    os.makedirs(os.path.join(output_folder, 'images', 'val'), exist_ok=True)
    os.makedirs(os.path.join(output_folder, 'labels', 'train'), exist_ok=True)
    os.makedirs(os.path.join(output_folder, 'labels', 'val'), exist_ok=True)

    # Load the map image
    map_img = Image.open(map_image_path)
    map_width, map_height = map_img.size

    # Get a list of icon files
    icon_files = [f for f in os.listdir(icons_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]

    # Extract class names from icon files
    class_names = [os.path.splitext(f)[0] for f in icon_files]

    # Write class names to a file
    classes_file_path = os.path.join(output_folder, 'classes.txt')
    with open(classes_file_path, 'w') as classes_file:
        classes_file.write("names:\n")
        for idx, class_name in enumerate(class_names):
            classes_file.write(f"  {idx}: {class_name}\n")

    # Determine the number of validation images
    num_val_images = int(num_images * val_split)
    num_train_images = num_images - num_val_images

    # Helper function to add icons to the map and save the results
    def process_and_save_images(image_count, image_type):
        for _ in range(image_count):
            # Select 10 random icons
            selected_icons = random.sample(icon_files, 10)
            
            # Create a copy of the map image to draw on
            img_copy = map_img.copy()
            
            # Initialize a list to store bounding box data
            bounding_boxes = []
            
            for icon_file in selected_icons:
                # Load the icon
                icon_path = os.path.join(icons_folder, icon_file)
                icon_img = Image.open(icon_path)
                icon_img = icon_img.resize(icon_size, Image.LANCZOS)  # Resize the icon
                icon_width, icon_height = icon_img.size
                
                # Generate random position for the icon on the map
                max_x = map_width - icon_width
                max_y = map_height - icon_height
                position_x = random.randint(0, max_x)
                position_y = random.randint(0, max_y)
                
                # Paste the icon on the map
                img_copy.paste(icon_img, (position_x, position_y), icon_img.convert('RGBA'))
                
                # Calculate bounding box coordinates normalized
                x_center = (position_x + icon_width / 2) / map_width
                y_center = (position_y + icon_height / 2) / map_height
                width = icon_width / map_width
                height = icon_height / map_height
                
                # Get the class index from the file name
                class_index = class_names.index(os.path.splitext(icon_file)[0])
                
                # Append bounding box data
                bounding_boxes.append(f"{class_index} {x_center} {y_center} {width} {height}")
            
            # Generate unique name for the output image
            unique_name = str(uuid.uuid4())
            
            # Save the modified map image
            output_image_path = os.path.join(output_folder, 'images', image_type, f"{unique_name}.jpg")
            img_copy.save(output_image_path)
            
            # Save the bounding box data to a text file
            output_label_path = os.path.join(output_folder, 'labels', image_type, f"{unique_name}.txt")
            with open(output_label_path, 'w') as label_file:
                label_file.write("\n".join(bounding_boxes))
            
            print(f"Created {image_type} image and label: {output_image_path}, {output_label_path}")
    
    # Create training images and labels
    process_and_save_images(num_train_images, 'train')
    
    # Create validation images and labels
    process_and_save_images(num_val_images, 'val')
    
    # Zip the output_folder
    zip_output_path = output_folder + '.zip'
    with zipfile.ZipFile(zip_output_path, 'w') as zipf:
        for root, dirs, files in os.walk(output_folder):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(output_folder, '..')))
    
    print(f"Zipped the output folder to: {zip_output_path}")

# Example usage
map_image_path = 'map.jpg'  # Path to your map image
icons_folder = 'champions'  # Path to your icons folder
output_folder = 'train_data'  # Path to your output folder
icon_size = (20, 20)  # Size of the icons
num_images = 250

create_training_data(map_image_path, icons_folder, output_folder, num_images, icon_size=icon_size)
