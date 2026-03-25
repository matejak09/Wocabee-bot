import time
import ctypes
import tkinter as tk
from tkinter import ttk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC

options = Options()
options.add_argument("--log-level=3")  # skryje error/warning logy

# Globálne premenné
nazvy_tried = ["Trieda A", "Trieda B", "Trieda C"]
driver = None 
riadok = None
slovnik = {}
predosle_slovo = ""
MB_OK = 0x0
získané_body = 0


def dalej_na_balik():
    frame_login.pack_forget()
    global meno, heslo, driver
    meno = entry_meno.get()
    heslo = entry_heslo.get()

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.get("https://wocabee.app/app")
    input_element = driver.find_element(By.NAME, "login")
    input_element.clear()
    input_element.send_keys(meno)
    input_element = driver.find_element(By.NAME, "password")
    input_element.clear()
    input_element.send_keys(heslo)
    input_element.send_keys(Keys.ENTER)
    heslo = "*" * len(heslo)
    time.sleep(0.5)

    nazvy_tried = []
    triedy = driver.find_elements(By.CSS_SELECTOR, ".btn.btn-lg.btn-wocagrey.btn-block")
    for trie in triedy:
        a = trie.find_element(By.TAG_NAME, "span")
        nazvy_tried.append(a.text.strip())

    frame_trieda = tk.Frame(root)
    tk.Label(frame_trieda, text="Vyber triedu:").pack(pady=5)

    def potvrdit_triedu():
        vybrana_trieda_i = combo_trieda.current()
        triedy[vybrana_trieda_i].click()
        frame_trieda.pack_forget()

        try:
            button_more = driver.find_element(By.ID, "showMorePackagesBtn")
            driver.execute_script("arguments[0].scrollIntoView();", button_more)
            button_more.click()
            time.sleep(0.3)
        except:
            pass

        frame_balik = tk.Frame(root)
        tk.Label(frame_balik, text="Koľko bodov chceš získať?").pack(pady=5)

        entry_body = tk.Entry(frame_balik)
        entry_body.pack(pady=5)

        label_balik = tk.Label(
            frame_balik,
            text="Zadaj počet bodov,\nktoré chceš získať.",
            font=("Arial", 11)
        )
        def potvrdit():
            global balik_spustit, riadok, i_button, potrebné_body
            potrebné_body_text = entry_body.get()
            potrebné_body = int(potrebné_body_text)
            balik_spustit = driver.find_element(By.CSS_SELECTOR, ".actionBtn.btn.btn-primary.btn-block")
            riadok = balik_spustit.find_element(By.XPATH, "..").find_element(By.XPATH, "..").find_element(By.XPATH, "..")
            i_button = riadok.find_element(By.CLASS_NAME, "intro-icon")
            root.destroy()
            zisti_slovíčka_začatého()

        label_balik.pack(pady=15)
        tk.Button(frame_balik, text="Spustiť", command=potvrdit).pack(pady=10)
        frame_balik.pack(padx=20, pady=20)
    combo_trieda = ttk.Combobox(frame_trieda, values=nazvy_tried, state="readonly")
    combo_trieda.current(0)
    combo_trieda.pack(pady=5)
    tk.Button(frame_trieda, text="Vybrať", command=potvrdit_triedu).pack(pady=10)
    frame_trieda.pack(padx=20, pady=20)

def start_main_gui():
    global entry_meno, entry_heslo, root, dalej_na_balik, frame_login
    root = tk.Tk()
    root.title("Prihlásenie a výber balíka")
    root.update_idletasks()
    win_w, win_h = 250, 250
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x = screen_w - win_w - ((screen_w - win_w) // 4)
    y = (screen_h - win_h) // 2
    root.geometry(f"{win_w}x{win_h}+{x}+{y}")
    frame_login = tk.Frame(root)
    frame_login.pack(padx=20, pady=20)
    tk.Label(frame_login, text="Meno:").pack(pady=5)
    entry_meno = tk.Entry(frame_login)
    entry_meno.pack(pady=5)
    tk.Label(frame_login, text="Heslo:").pack(pady=5)
    entry_heslo = tk.Entry(frame_login, show="*")
    entry_heslo.pack(pady=5)
    tk.Button(
        frame_login,
        text="Prihlásiť",
        command=dalej_na_balik
    ).pack(pady=10)
    root.mainloop()

def zisti_slovíčka_začatého():
    global slovnik, riadok, i_button
    driver.execute_script("arguments[0].scrollIntoView();", i_button)
    button = WebDriverWait(riadok, 5).until(EC.element_to_be_clickable(i_button))
    button.click()
    slovnik = {}
    time.sleep(0.6)
    počet = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "wordCount")))
    cislo = počet.text.strip()
    číslo = int(cislo)
    predosle_slovo = ""
    for i in range(číslo):

        WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.ID, "word").text.strip() != predosle_slovo
        )

        slovo = driver.find_element(By.ID, "word")
        key = slovo.text.strip()
        preklad = driver.find_element(By.ID, "translation")
        value = preklad.text.strip()
        slovnik[key] = value
        slovnik[value] = key
        predosle_slovo = key
        try:
            button = driver.find_element(By.ID, "rightArrow")
            button.click()
            time.sleep(1)
        except:
            button = driver.find_element(By.ID, "backBtn")
            button.click()
            button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "showMorePackagesBtn")))
            button.click()
start_main_gui()
balik_spustit = driver.find_element(By.CSS_SELECTOR, ".actionBtn.btn.btn-primary.btn-block")
driver.execute_script("arguments[0].scrollIntoView();", balik_spustit)
button = WebDriverWait(riadok, 5).until(EC.element_to_be_clickable(balik_spustit))
button.click()
time.sleep(0.3)
driver.execute_script("""
const el = document.getElementById('levelToggle');
el.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
el.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
el.dispatchEvent(new MouseEvent('click', { bubbles: true }));
""")
time.sleep(1)
základné_body = int(driver.find_element(By.ID, "WocaPoints").text.strip())
while True:
    if získané_body >= potrebné_body:
        driver.find_element(By.ID, "backBtn").click()
        ctypes.windll.user32.MessageBoxW(0, "Body sú získané", "Ukončenie", MB_OK)
        driver.quit()
        raise SystemExit(0)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "tfw_word")))
    slovo = driver.find_element(By.ID, "tfw_word").text.strip()
    preklad = slovnik.get(slovo)
    input_element = driver.find_element(By.ID, "translateFallingWordAnswer")
    input_element.clear()
    input_element.send_keys(preklad)
    input_element.send_keys(Keys.ENTER)
    teraz_body = int(driver.find_element(By.ID, "WocaPoints").text.strip())
    získané_body = teraz_body - základné_body
    print(získané_body)
