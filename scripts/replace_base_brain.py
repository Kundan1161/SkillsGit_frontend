import os
from PIL import Image, ImageFilter

def process_brain_images(input_path, output_light_path, output_dark_path):
    img = Image.open(input_path).convert("RGBA")
    width, height = img.size
    pixels = img.load()
    
    # 1. BFS to identify connected white background pixels
    visited = set()
    queue = [(0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1)]
    for q in queue:
        visited.add(q)
        
    background_pixels = set()
    
    # Helper to calculate color distance to pure white
    def dist_to_white(r, g, b):
        return ((r - 255)**2 + (g - 255)**2 + (b - 255)**2)**0.5
        
    threshold = 60.0 # Increased threshold to capture all off-white and compression noise
    
    while queue:
        x, y = queue.pop(0)
        r, g, b, a = pixels[x, y]
        
        if dist_to_white(r, g, b) < threshold:
            background_pixels.add((x, y))
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    if (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append((nx, ny))
                        
    # 2. Create binary mask (0 = background, 255 = foreground)
    mask = Image.new("L", (width, height), 255)
    mask_pixels = mask.load()
    for x, y in background_pixels:
        mask_pixels[x, y] = 0
        
    # 3. Apply Gaussian blur to the mask to achieve smooth edges
    blurred_mask = mask.filter(ImageFilter.GaussianBlur(1.2))
    
    # 4. Reconstruct RGBA pixels with un-multiplying to remove the white halo
    original_data = img.getdata()
    alpha_data = blurred_mask.getdata()
    
    light_data = []
    dark_data = []
    
    for i in range(len(original_data)):
        r, g, b, a = original_data[i]
        alpha = alpha_data[i]
        
        if alpha == 0:
            light_data.append((0, 0, 0, 0))
            dark_data.append((0, 0, 0, 0))
        elif alpha == 255:
            light_data.append((r, g, b, 255))
            
            # For dark mode: darken the brain sculpture to a sleek charcoal/metallic look (brightness * 0.28)
            # but keep a bit of the blue glows vibrant
            dr = int(r * 0.28)
            dg = int(g * 0.28)
            db = int(b * 0.38) # Slightly boost blue channel for a high-tech vibe
            dark_data.append((dr, dg, db, 255))
        else:
            alpha_f = alpha / 255.0
            # Un-multiply white background
            rf = max(0, min(255, int((r - 255 * (1.0 - alpha_f)) / alpha_f)))
            gf = max(0, min(255, int((g - 255 * (1.0 - alpha_f)) / alpha_f)))
            bf = max(0, min(255, int((b - 255 * (1.0 - alpha_f)) / alpha_f)))
            
            light_data.append((rf, gf, bf, alpha))
            
            # Dark mode version of the anti-aliased edge
            dr = int(rf * 0.28)
            dg = int(gf * 0.28)
            db = int(bf * 0.38)
            dark_data.append((dr, dg, db, alpha))
            
    # Save light mode image
    img_light = Image.new("RGBA", (width, height))
    img_light.putdata(light_data)
    img_light.save(output_light_path, "PNG")
    print(f"Processed light brain saved to {output_light_path}")
    
    # Save dark mode image
    img_dark = Image.new("RGBA", (width, height))
    img_dark.putdata(dark_data)
    img_dark.save(output_dark_path, "PNG")
    print(f"Processed dark brain saved to {output_dark_path}")

if __name__ == '__main__':
    input_img = "/Users/KundanSrinivas/.gemini/antigravity/brain/37165e9f-435b-4778-9794-8c5dd79f75c9/media__1780570322994.png"
    out_light = "/Users/KundanSrinivas/Downloads/skillsgit-cycle-1-occupations-personas-capture/apps/web-marketplace/public/neumorphic_brain_light.png"
    out_dark = "/Users/KundanSrinivas/Downloads/skillsgit-cycle-1-occupations-personas-capture/apps/web-marketplace/public/neumorphic_brain_dark.png"
    
    process_brain_images(input_img, out_light, out_dark)
