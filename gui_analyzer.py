import requests
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from io import BytesIO
import webbrowser
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import datetime


# --- GitHub API functions ---
def get_user_info(username):
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

def get_repos(username):
    url = f"https://api.github.com/users/{username}/repos"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

def analyze_repos(repos, username):
    repo_names, stars, languages = [], [], {}

    for repo in repos:
        name = repo["name"]
        star_count = repo["stargazers_count"]
        lang = repo["language"]

        repo_names.append(name)
        stars.append(star_count)

        if lang:
            languages[lang] = languages.get(lang, 0) + 1

    avg_stars = sum(stars) / len(stars) if stars else 0
    most_used_language = max(languages, key=languages.get) if languages else "N/A"

    return avg_stars, most_used_language, repo_names, stars, languages


# --- GUI Functions ---
def analyze_profile():
    username = entry_username.get().strip()
    if not username:
        messagebox.showwarning("Input Error", "Please enter a GitHub username.")
        return

    user_data = get_user_info(username)
    if not user_data:
        messagebox.showerror("Error", "User not found or API issue.")
        return

    repos = get_repos(username)
    if not repos:
        messagebox.showinfo("No Data", "This user has no public repositories.")
        return

    global current_data
    avg_stars, most_lang, repo_names, stars, languages = analyze_repos(repos, username)
    current_data = {
        "username": username,
        "name": user_data.get("name", "N/A"),
        "repos": user_data["public_repos"],
        "followers": user_data["followers"],
        "most_lang": most_lang,
        "avg_stars": avg_stars,
        "repo_names": repo_names,
        "stars": stars,
        "languages": languages,
        "profile_url": user_data["html_url"]
    }

    label_name_val.config(text=current_data["name"])
    label_repos_val.config(text=current_data["repos"])
    label_followers_val.config(text=current_data["followers"])
    label_lang_val.config(text=current_data["most_lang"])
    label_avg_val.config(text=f"{current_data['avg_stars']:.2f}")

    # Enable buttons
    view_profile_button.config(state="normal")
    save_pdf_button.config(state="normal")

    # --- Display profile picture ---
    avatar_url = user_data.get("avatar_url")
    if avatar_url:
        try:
            img_data = requests.get(avatar_url).content
            img = Image.open(BytesIO(img_data))
            img = img.resize((100, 100))
            photo = ImageTk.PhotoImage(img)
            avatar_label.config(image=photo)
            avatar_label.image = photo
        except Exception as e:
            print("Error loading avatar:", e)

    # --- Show charts ---
    plt.figure(figsize=(10,5))
    plt.barh(repo_names, stars, color="skyblue")
    plt.xlabel("Stars")
    plt.ylabel("Repositories")
    plt.title(f"Stars per Repository - {username}")
    plt.tight_layout()
    plt.show()

    if languages:
        plt.figure(figsize=(6,6))
        plt.pie(languages.values(), labels=languages.keys(), autopct='%1.1f%%', startangle=140)
        plt.title(f"Languages Used - {username}")
        plt.show()


def open_profile():
    if current_data and current_data["profile_url"]:
        webbrowser.open(current_data["profile_url"])
    else:
        messagebox.showwarning("No Profile", "Analyze a user first!")


#  --- Function to Save Report as PDF ---
def save_as_pdf():
    if not current_data:
        messagebox.showwarning("No Data", "Analyze a user first!")
        return

    filename = f"{current_data['username']}_report.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Title and header
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width/2, height - 50, "GitHub Profile Report")

    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2, height - 70, f"Generated on {datetime.date.today()}")

    # User details
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 110, "Profile Information:")
    c.setFont("Helvetica", 11)
    c.drawString(70, height - 130, f"Username: {current_data['username']}")
    c.drawString(70, height - 150, f"Name: {current_data['name']}")
    c.drawString(70, height - 170, f"Followers: {current_data['followers']}")
    c.drawString(70, height - 190, f"Public Repos: {current_data['repos']}")
    c.drawString(70, height - 210, f"Most Used Language: {current_data['most_lang']}")
    c.drawString(70, height - 230, f"Average Stars: {current_data['avg_stars']:.2f}")
    c.drawString(70, height - 250, f"Profile URL: {current_data['profile_url']}")

    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(width/2, 50, "Mini Project: GitHub Profile Analyzer | Made by Dhruval Gohil")

    c.save()
    messagebox.showinfo("PDF Saved", f"Report saved as '{filename}'")


# --- Tkinter Window ---
root = tk.Tk()
root.title("GitHub Profile Analyzer")
root.geometry("430x570")
root.config(bg="#f0f0f0")

title_label = tk.Label(root, text="GitHub Profile Analyzer", font=("Arial", 16, "bold"), bg="#f0f0f0")
title_label.pack(pady=10)

frame_input = tk.Frame(root, bg="#f0f0f0")
frame_input.pack(pady=5)
tk.Label(frame_input, text="GitHub Username:", bg="#f0f0f0").grid(row=0, column=0, padx=5)
entry_username = tk.Entry(frame_input, width=25)
entry_username.grid(row=0, column=1, padx=5)

analyze_button = tk.Button(root, text="Analyze", command=analyze_profile, bg="#0078D7", fg="white", width=15)
analyze_button.pack(pady=10)

view_profile_button = tk.Button(root, text="View GitHub Profile", command=open_profile, bg="#28a745", fg="white", width=20, state="disabled")
view_profile_button.pack(pady=5)

save_pdf_button = tk.Button(root, text="Save as PDF Report", command=save_as_pdf, bg="#ff9800", fg="white", width=20, state="disabled")
save_pdf_button.pack(pady=5)

avatar_label = tk.Label(root, bg="#f0f0f0")
avatar_label.pack(pady=10)

frame_info = tk.Frame(root, bg="#f0f0f0")
frame_info.pack(pady=10)

def add_label(row, text):
    tk.Label(frame_info, text=text, anchor="w", bg="#f0f0f0").grid(row=row, column=0, sticky="w", padx=10)
    val = tk.Label(frame_info, text="-", bg="#f0f0f0", fg="blue")
    val.grid(row=row, column=1, sticky="w")
    return val

label_name_val = add_label(0, "Name:")
label_repos_val = add_label(1, "Public Repos:")
label_followers_val = add_label(2, "Followers:")
label_lang_val = add_label(3, "Most Used Language:")
label_avg_val = add_label(4, "Average Stars:")

current_data = None  #  store analyzed user data

root.mainloop()