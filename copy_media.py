import os
import shutil

def main():
    src_dir = r"C:\Users\harry\.gemini\antigravity\brain\63717daa-c20c-417a-8af1-a34ab02fa1cd"
    dest_dir = r"C:\Users\harry\OneDrive\Desktop\Decision_IQ\docs\images"

    os.makedirs(dest_dir, exist_ok=True)

    mappings = {
        "media__1783281008185.png": "pbi_ceo_tower.png",
        "media__1783281023645.png": "pbi_finance.png",
        "media__1783281036503.png": "pbi_operations.png",
        "media__1783281063811.png": "pbi_customer_success.png",
        "media__1783281122018.png": "streamlit_dark_mockup.png"
    }

    for src_name, dest_name in mappings.items():
        src_path = os.path.join(src_dir, src_name)
        dest_path = os.path.join(dest_dir, dest_name)
        if os.path.exists(src_path):
            shutil.copy(src_path, dest_path)
            print(f"Copied {src_name} -> {dest_path}")
        else:
            print(f"Warning: {src_path} does not exist!")

if __name__ == "__main__":
    main()
