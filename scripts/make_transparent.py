import sys
from pathlib import Path
from PIL import Image
import numpy as np

ASSETS_DIR = Path(__file__).resolve().parent.parent / "frontend" / "public" / "assets"
BRAIN_DIR = Path(r"C:\Users\suren\.gemini\antigravity-ide\brain\0d48f16f-ed28-4b4f-bfa7-85b32d891953")

def remove_black_background(input_path: Path, output_path: Path, threshold=25):
    img = Image.open(input_path).convert("RGBA")
    data = np.array(img)
    
    rgb = data[:, :, :3]
    brightness = np.max(rgb, axis=2)
    
    alpha = np.clip((brightness.astype(float) - threshold) / (75 - threshold) * 255, 0, 255).astype(np.uint8)
    data[:, :, 3] = alpha
    result = Image.fromarray(data)
    result.save(output_path, "PNG")
    print(f"Saved transparent PNG: {output_path}")

def main():
    # Process hero core
    core_files = list(BRAIN_DIR.glob("hero_gateway_core_*.jpg"))
    if core_files:
        remove_black_background(core_files[-1], ASSETS_DIR / "hero_gateway_core.png")
    
    # Process others
    files = [
        ("floating_shield_3d.jpg", "floating_shield_3d.png"),
        ("floating_neural_matrix.jpg", "floating_neural_matrix.png"),
        ("floating_biometric_card.jpg", "floating_biometric_card.png"),
    ]
    for src, dst in files:
        src_path = ASSETS_DIR / src
        dst_path = ASSETS_DIR / dst
        if src_path.exists():
            remove_black_background(src_path, dst_path)

if __name__ == "__main__":
    main()
