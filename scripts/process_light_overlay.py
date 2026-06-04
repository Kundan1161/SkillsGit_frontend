import os
from PIL import Image

def remove_white_background(input_path, output_path):
    img = Image.open(input_path).convert("RGBA")
    datas = img.getdata()
    
    new_data = []
    for item in datas:
        r, g, b, a = item
        # If already transparent, keep it
        if a == 0:
            new_data.append((0, 0, 0, 0))
            continue
            
        # Calculate alpha based on distance to white.
        # Background is white (255, 255, 255).
        # We want to un-multiply the background.
        # Since r, g, b are blended on white:
        # C_val = alpha * C_f + (1 - alpha) * 255
        # Therefore, alpha >= 1 - C_val/255 for each channel.
        # Since C_f >= 0, the maximum possible alpha that can explain the pixel is:
        # alpha = 1.0 - min(r, g, b)/255.0
        min_val = min(r, g, b)
        
        # Map values above 253 to 0 alpha (pure background) to eliminate compression noise
        if min_val >= 253:
            alpha_f = 0.0
        elif min_val <= 5:
            alpha_f = 1.0
        else:
            alpha_f = 1.0 - (min_val - 5) / (253 - 5)
            
        alpha = int(alpha_f * 255)
        
        if alpha == 0:
            new_data.append((0, 0, 0, 0))
        else:
            # Reconstruct the foreground color C_f
            # C_val = alpha_f * C_f + (1 - alpha_f) * 255
            # C_f = (C_val - 255 * (1 - alpha_f)) / alpha_f
            rf = max(0, min(255, int((r - 255 * (1.0 - alpha_f)) / alpha_f)))
            gf = max(0, min(255, int((g - 255 * (1.0 - alpha_f)) / alpha_f)))
            bf = max(0, min(255, int((b - 255 * (1.0 - alpha_f)) / alpha_f)))
            new_data.append((rf, gf, bf, alpha))
            
    img.putdata(new_data)
    
    # Save the processed transparent image
    img.save(output_path, "PNG")
    print(f"Processed image saved successfully to {output_path}")

if __name__ == '__main__':
    input_img = "/Users/KundanSrinivas/.gemini/antigravity/brain/37165e9f-435b-4778-9794-8c5dd79f75c9/digital_brain_overlay_light_new_1780569932077.png"
    output_img = "/Users/KundanSrinivas/Downloads/skillsgit-cycle-1-occupations-personas-capture/apps/web-marketplace/public/digital_brain_overlay_light.png"
    
    remove_white_background(input_img, output_img)
