import os
import shutil
import datetime

# Define categories for file organization
FILE_CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif"],
    "Videos": [".mp4", ".mkv", ".avi"],
    "Documents": [".pdf", ".docx", ".txt", ".pptx"],
    "Music": [".mp3", ".wav"],
    "Archives": [".zip", ".rar", ".7z"],
    "Code Files": [".py", ".js", ".html", ".css"],
}

# Themes for UI customization
THEMES = {
    "dark": {"bg": "#2B2D42", "fg": "#EDF2F4", "btn_bg": "#8D99AE", "btn_fg": "#2B2D42"},
    "light": {"bg": "#F7F7F7", "fg": "#2B2D42", "btn_bg": "#4CAF50", "btn_fg": "#FFFFFF"},
}

def move_file(file_path, destination_folder):
    os.makedirs(destination_folder, exist_ok=True)
    shutil.move(file_path, os.path.join(destination_folder, os.path.basename(file_path)))


def categorize_files(directory, progress_var, file_count_var, selected_categories, summary_var, size_filter, date_filter):
    # Validate selected_categories structure
    if not isinstance(selected_categories, dict):
        raise ValueError("selected_categories must be a dictionary with category keys and tkinter.BooleanVar values.")
    
    for category, value in selected_categories.items():
        if not hasattr(value, "get") or not callable(value.get):
            raise ValueError(f"The value for category '{category}' must be a tkinter.BooleanVar or similar object with a 'get' method.")

    total_files = sum(len(files) for _, _, files in os.walk(directory))
    processed_files = 0
    file_count_var.set(f"Files Processed: {processed_files}/{total_files}")

    filter_size = 1 * 1024 * 1024 if size_filter.get() else 0  # 1 MB filter
    recent_days_limit = datetime.timedelta(days=30) if date_filter.get() else None

    file_summary = {category: 0 for category in FILE_CATEGORIES}

    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1].lower()

            if os.path.getsize(file_path) < filter_size:
                continue

            if recent_days_limit:
                file_mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                if datetime.datetime.now() - file_mod_time > recent_days_limit:
                    continue

            for category, extensions in FILE_CATEGORIES.items():
                if file_ext in extensions:
                    # Ensure the category exists in selected_categories and is enabled
                    if category in selected_categories and selected_categories[category].get():
                        destination_folder = os.path.join(directory, category)
                        move_file(file_path, destination_folder)
                        file_summary[category] += 1
                        break

            processed_files += 1
            progress_var.set((processed_files / total_files) * 100)
            file_count_var.set(f"Files Processed: {processed_files}/{total_files}")

    summary_var.set("\n".join(f"{category}: {count} files" for category, count in file_summary.items() if count > 0))