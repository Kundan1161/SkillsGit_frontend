import os
from PIL import Image

def process_digital_brain(input_path, output_path):
    img = Image.open(input_path).convert("RGB")
    width, height = img.size
    pixels = img.load()
    
    new_data = []
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            
            # Calculate alpha based on maximum channel value (un-premultiplying black background)
            max_val = max(r, g, b)
            
            # To eliminate compression noise in the background, we completely transparentize pixels below 30
            if max_val < 30:
                alpha_f = 0.0
            elif max_val > 250:
                alpha_f = 1.0
            else:
                # Linearly map alpha_f from 0.0 (at 30) to 1.0 (at 250)
                alpha_f = (max_val - 30) / (250 - 30)
                
            alpha = int(alpha_f * 255)
            
            if alpha == 0:
                new_data.append((0, 0, 0, 0))
            else:
                # Reconstruct the foreground color C_f
                rf = min(255, int(r / alpha_f))
                gf = min(255, int(g / alpha_f))
                bf = min(255, int(b / alpha_f))
                new_data.append((rf, gf, bf, alpha))
                
    result_img = Image.new("RGBA", (width, height))
    result_img.putdata(new_data)
    result_img.save(output_path, "PNG")
    print(f"Processed digital brain overlay saved successfully to {output_path}")

if __name__ == '__main__':
    input_img = "/Users/KundanSrinivas/.gemini/antigravity/brain/37165e9f-435b-4778-9794-8c5dd79f75c9/media__1780570525186.jpg"
    out_dark_overlay = "/Users/KundanSrinivas/Downloads/skillsgit-cycle-1-occupations-personas-capture/apps/web-marketplace/public/digital_brain_overlay.png"
    out_light_overlay = "/Users/KundanSrinivas/Downloads/skillsgit-cycle-1-occupations-personas-capture/apps/web-marketplace/public/digital_brain_overlay_light.png"
    
    process_digital_brain(input_img, out_dark_overlay)
    process_digital_brain(input_img, out_light_overlay)
