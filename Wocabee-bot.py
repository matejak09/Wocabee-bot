import time
import json
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
gulicky = 0
MB_OK = 0x0
meno = None
heslo = None
vybrany_balik = None
baliky_mena = []
baliky_spustit = []
nazvy_tried = ["Trieda A", "Trieda B", "Trieda C"]
driver = None 
začatý_balík = False
riadok = None
slovnik = {}
vybrany_balik_el = None
nový_balík = False


def dalej_na_balik():
    frame_login.pack_forget()
    global meno, heslo, driver
    meno = entry_meno.get()
    heslo = entry_heslo.get()
    print("Meno:", meno)

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
    tk.Label(frame_trieda, text="Select class:").pack(pady=5)

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
        try:
            driver.find_element(By.CLASS_NAME, "package")
        except:
            ctypes.windll.user32.MessageBoxW(0, "This class has no packages\nor all packages are already complete", "Error", MB_OK)
            root.destroy()
            driver.quit()
            raise SystemExit(0)

        frame_balik = tk.Frame(root)
        tk.Label(frame_balik, text="Select package:").pack(pady=5)

        label_balik = tk.Label(
            frame_balik,
            text="Package completion mode.\nClick Start to continue.",
            font=("Arial", 11)
        )
        label_balik.pack(pady=15)

        def potvrdit():
            global vybrany_balik, začatý_balík, riadok, vybrany_balik_el
            vybrany_balik_el = driver.find_element(By.CLASS_NAME, "package")
            riadok = vybrany_balik_el.find_element(By.XPATH, "..").find_element(By.XPATH, "..")
            vybrany_balik = riadok.find_element(By.CLASS_NAME, "package-name").text.strip()
            try:
                riadok.find_element(By.CSS_SELECTOR, "div.actionBtn.btn.btn-mic.btn-block")
                začatý_balík = True
            except:
                začatý_balík = False
            root.destroy()

        tk.Button(frame_balik, text="Start", command=potvrdit).pack(pady=10)
        frame_balik.pack(padx=20, pady=20)

    combo_trieda = ttk.Combobox(frame_trieda, values=nazvy_tried, state="readonly")
    combo_trieda.current(0)
    combo_trieda.pack(pady=5)
    tk.Button(frame_trieda, text="Select", command=potvrdit_triedu).pack(pady=10)
    frame_trieda.pack(padx=20, pady=20)

def start_main_gui():
    global entry_meno, entry_heslo, root, dalej_na_balik, frame_login
    root = tk.Tk()
    root.title("Login and Package Selection")
    root.update_idletasks()
    win_w, win_h = 250, 250
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x = screen_w - win_w - ((screen_w - win_w) // 4)
    y = (screen_h - win_h) // 2
    root.geometry(f"{win_w}x{win_h}+{x}+{y}")
    frame_login = tk.Frame(root)
    frame_login.pack(padx=20, pady=20)
    tk.Label(frame_login, text="Username:").pack(pady=5)
    entry_meno = tk.Entry(frame_login)
    entry_meno.pack(pady=5)
    tk.Label(frame_login, text="Password:").pack(pady=5)
    entry_heslo = tk.Entry(frame_login, show="*")
    entry_heslo.pack(pady=5)
    tk.Button(
        frame_login,
        text="Login",
        command=dalej_na_balik
    ).pack(pady=10)
    root.mainloop()

start_main_gui()





# Results
# try:
#     print("Package name:", vybrany_balik)
# except Exception:
#     print("No selected package")
# if začatý_balík:
#     print("Selected package is already started")
    

def zisti_slovíčka_normálne():
    global slovnik, vybrany_balik_el
    driver.execute_script("arguments[0].scrollIntoView();", vybrany_balik_el)
    vybrany_balik_el.click()
    button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "introRun")))
    button.click()
    slovnik = {}
    time.sleep(0.6)
    počet = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "introWordCount")))
    cislo = počet.text.strip()
    try:
        číslo = int(cislo)
    except Exception:
        číslo = 0
    # print("Počet slovíčok v balíku:", číslo)
    predosle_slovo = ""
    for i in range(číslo):

        WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.ID, "introWord").text.strip() != predosle_slovo
        )

        slovo = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "introWord")))
        key = slovo.text.strip()
        preklad = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "introTranslation")))
        value = preklad.text.strip()
        slovnik[key] = value
        slovnik[value] = key
        predosle_slovo = key
        try:
            button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "introNext")))
            button.click()
        except:
            time.sleep(0.4)
            break
    # print(json.dumps(slovnik, indent=4, ensure_ascii=False))


def zisti_slovíčka_začatého():
    global slovnik, vybrany_balik_el, riadok
    driver.execute_script("arguments[0].scrollIntoView();", vybrany_balik_el)
    button = WebDriverWait(riadok, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, "intro-icon")))
    button.click()
    slovnik = {}
    time.sleep(0.6)
    počet = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "wordCount")))
    cislo = počet.text.strip()
    číslo = int(cislo)
    # print("Počet slovíčok v balíku:", číslo)
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
    # print(json.dumps(slovnik, indent=4, ensure_ascii=False))
    time.sleep(1)
    baliky_mena.clear()
    baliky_spustit.clear()
    riadky = driver.find_elements(By.CLASS_NAME, "pTableRow")
    for ria in riadky:
        a = ria.find_element(By.CLASS_NAME, "package-name")
        b = a.text.strip()
        baliky_mena.append(b)
        try:
            a = ria.find_element(By.CLASS_NAME, "package")
            baliky_spustit.append(a)
        except:
            baliky_mena.remove(b)

    vybrany_balik_el = baliky_spustit[0]
    vybrany_balik1 = baliky_mena[0]
    predošlý_názov = vybrany_balik1
    driver.execute_script("arguments[0].scrollIntoView();", vybrany_balik_el)
    vybrany_balik_el.click()



#--------------------------Selenium-----------------------------------------------------------------------------------------------------------------
if začatý_balík == False:
    zisti_slovíčka_normálne()
else:
    zisti_slovíčka_začatého()

def find_visible_element():
    global elements
    for i in range(9999):
        time.sleep(0.01)
        for el in elements:
            if el.is_displayed():
                return el

while True:
    elements = driver.find_elements(By.CLASS_NAME, "methodDesc")
    visible_element = None
    visible_element = find_visible_element() 
    if visible_element:
        parent = visible_element.find_element(By.XPATH, "..")
        zadanie = parent.get_attribute("id")
        if zadanie == None or zadanie == "":
            parent = parent.find_element(By.XPATH, "..")
            zadanie = parent.get_attribute("id")

    if zadanie == "addMissingWord":
        spravna_el = driver.find_element(By.ID, "q_sentence").text.strip()
        spravna = slovnik.get(spravna_el)
        chyba_el = driver.find_element(By.ID, 'a_sentence')
        chyba = chyba_el.text
        spravna_slova = spravna.split()
        chyba_slova = chyba.split()
        for i in range(len(chyba_slova)):
            if spravna_slova[i] != chyba_slova[i]:
                treba_doplnit = spravna_slova[i]
                break
        if len(spravna_slova) > len(chyba_slova):
            treba_doplnit = spravna_slova[-1]
        input_el = driver.find_element(By.ID, "missingWordAnswer")
        input_el.send_keys(treba_doplnit)
        input_el.send_keys(Keys.ENTER)
    elif zadanie == "describePicture":
        input_el = driver.find_element(By.ID, "describePictureAnswer")
        input_el.send_keys("abc")
        button = driver.find_element(By.ID, "describePictureSubmitBtn")
        button.click()
        button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "incorrect-next-button")))
        button.click()
    elif zadanie == "arrangeWords":
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "arrangeWordsSubmitBtn"))).click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "incorrect-next-button"))).click()
    elif zadanie == "choosePicture":
        slv = driver.find_element(By.ID, "choosePictureWord")
        slovo = slv.text.strip()
        preklad = slovnik.get(slovo)
        skupina = driver.find_element(By.ID, "choosePicture")
        parent = skupina.find_element(By.CSS_SELECTOR, "div.slick-track")
        obrázky = parent.find_elements(By.XPATH, "./*")
        for ob in obrázky:
            info = ob.find_element(By.XPATH, "./*")
            ob_slovo = info.get_attribute("word")
            if ob_slovo == preklad:
                ob.click()
                time.sleep(0.2)
                ob.click()
                break
            else:
                WebDriverWait(skupina, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.slick-next.slick-arrow"))).click()
                time.sleep(0.5)
    elif zadanie == "findPair":
        slova1 = []
        preklady1 = []
        time.sleep(0.1)
        slova_s = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "q_words")))
        slova_e = slova_s.find_elements(By.CSS_SELECTOR, "button.btn.btn-lg.btn-success.btn-block.fp_q.questionBtn")
        preklady_s = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "a_words")))
        preklady_e = preklady_s.find_elements(By.CSS_SELECTOR, "button.btn.btn-lg.btn-primary.btn-block.fp_a.questionBtn")
        for i in range(len(slova_e)):
            a = slova_e[i].text.strip()
            b = preklady_e[i].text.strip()
            slova1.append(a)
            preklady1.append(b)
        for s in slova1:
            for p in preklady1:
                if slovnik.get(s) == p or slovnik.get(p) == s:
                    spravne_s = s
                    spravne_p = p
        for i in range(len(slova1)):
            if spravne_s == slova1[i]:
                slova_e[i].click()
        for i in range(len(preklady1)):
            if spravne_p == preklady1[i]:
                preklady_e[i].click()

    elif zadanie == "translateWord":
        time.sleep(0.3)
        slovicko_element = driver.find_element(By.ID, "q_word")
        slovicko = slovicko_element.text.strip()
        preklad = slovnik.get(slovicko)
        input_element = driver.find_element(By.ID, "translateWordAnswer")
        input_element.clear()
        input_element.send_keys(preklad)
        input_element.send_keys(Keys.ENTER)
    elif zadanie == "completeWord":
        time.sleep(0.1)
        slovicko_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "completeWordQuestion")))
        slovicko = slovicko_element.text.strip()
        sablona_element = driver.find_element(By.ID, "completeWordAnswer")
        sablona = sablona_element.text.strip()
        pís = driver.find_element(By.ID, "characters")
        písmená = pís.find_elements(By.CSS_SELECTOR, "span.char.btn-wocagrey")
        preklad = slovnik.get(slovicko)
        chybajuce = [p for s, p in zip(sablona, preklad) if s == "_"]  
        for pismeno in chybajuce:
            for element in písmená:
                if element.text.strip() == pismeno:
                    element.click()   
                    break
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button#completeWordSubmitBtn.btn.btn-lg.btn-secondary.btn-block"))).click()
    
    elif zadanie == "chooseWord":
        slovicka = []
        slv = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "ch_word")))
        slovo = slv.text.strip()
        slova_s = driver.find_element(By.ID, "chooseWords")
        slova_e = driver.find_elements(By.CSS_SELECTOR, "button.chooseWordAnswer.btn.btn-lg.btn-primary.btn-block")
        for i in range(len(slova_e)):
            a = slova_e[i].text.strip()
            slovicka.append(a)
        spravne = slovnik.get(slovo)
        for i in range(len(slova_e)):
            if spravne == slovicka[i]:
                slova_e[i].click()
    elif zadanie == "oneOutOfMany":
        slovicka = []
        slv = driver.find_element(By.ID, "oneOutOfManyQuestionWord")
        slovo = slv.text.strip()
        elementy = driver.find_elements(By.CSS_SELECTOR, "div.oneOutOfManyWord.btn.btn-primary.btn-block")
        for i in range(len(elementy)):
            a = elementy[i].text.strip()
            slovicka.append(a)
        spravne = slovnik.get(slovo)
        for i in range(len(elementy)):
            if spravne == slovicka[i]:
                elementy[i].click()
    elif zadanie == "pexeso":
        pq_words = driver.find_element(By.ID, "pq_words")
        elementy1 = pq_words.find_elements(By.CSS_SELECTOR, "div.pexesoCardWrapper.pexesoWord")
        karty1 = pq_words.find_elements(By.CSS_SELECTOR, "div.pexesoCard.pexesoBack.btn.btn-info.btn-block ")
        elementy1[0].click()
        a1 = karty1[0].text.strip()
        elementy1[1].click()
        a2 = karty1[1].text.strip()
        elementy1[2].click()
        a3 = karty1[2].text.strip()
        elementy1[3].click()
        a4 = karty1[3].text.strip()
        pa_words = driver.find_element(By.ID, "pa_words")
        elementy = pa_words.find_elements(By.CSS_SELECTOR, "div.pexesoCardWrapper.pexesoTranslation")
        karty = pa_words.find_elements(By.CSS_SELECTOR, "div.pexesoCard.pexesoBack.btn.btn-primary.btn-block ")
        elementy[0].click()
        b1 = karty[0].text.strip()
        elementy[1].click()
        b2 = karty[1].text.strip()
        elementy[2].click()
        b3 = karty[2].text.strip()
        elementy[3].click()
        b4 = karty[3].text.strip()
        time.sleep(0.5)
        elementy[3].click()
        a_list = [a1, a2, a3, a4]
        b_list = [b1, b2, b3, b4]
        slova_matched = []
        preklady_matched = []
        for slovo in a_list:
            preklad = slovnik.get(slovo)
            if preklad in b_list:
                slova_matched.append(slovo)
                preklady_matched.append(preklad)
        for preklad in b_list:
            slovo = slovnik.get(preklad)
            if slovo in a_list and slovo not in slova_matched:
                slova_matched.append(slovo)
                preklady_matched.append(preklad)
        time.sleep(0.6)
        for i in range(len(slova_matched)):
            slovo = slova_matched[i]
            preklad = preklady_matched[i]
            if slovnik.get(slovo) != preklad:
                continue
            index_b = b_list.index(preklad)
            elementy1[i].click()
            time.sleep(0.4)
            elementy1[i].click()
            time.sleep(0.4)
            elementy[index_b].click()
            time.sleep(0.4)
            elementy[index_b].click()
            time.sleep(0.4)
    elif zadanie == "transcribe":
        button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "transcribeSkipBtn")))
        button.click()
        time.sleep(0.1)
        slovicko_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "q_word")))
        slovicko = slovicko_element.text.strip()
        preklad = slovnik.get(slovicko)
        input_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "translateWordAnswer")))
        input_element.clear()
        input_element.send_keys(preklad)
        input_element.send_keys(Keys.ENTER)
    elif driver.find_element(By.ID, "incorrect-next-button").is_displayed():
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "incorrect-next-button"))).click()
    percentá_el = driver.find_element(By.ID,"progressValue")
    percenta = percentá_el.text.strip()
    percentá = int(percenta.replace("%", ""))
    if percentá < 100:
        continue
    else:
        try:
            while True:
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "continueBtn"))).click()
        except:
            pass
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "backBtn"))).click()
        time.sleep(1)
        baliky_mena.clear()
        baliky_spustit.clear()
        driver.find_element(By.ID, "showMorePackagesBtn").click()
        time.sleep(0.5)
        try:
            balik_na_spustenie = driver.find_element(By.CLASS_NAME, "package")
        except:
            gulicky = 3
            print(f"{predošlý_názov}: {'●'*gulicky}")
            ctypes.windll.user32.MessageBoxW(0, "All packages are complete", "Exit", MB_OK)
            driver.quit()
            raise SystemExit(0)
        riadok = balik_na_spustenie.find_element(By.XPATH, "..").find_element(By.XPATH, "..")
        balik_na_spustenie_názov = riadok.find_element(By.CLASS_NAME, "package-name").text.strip()

        if not balik_na_spustenie_názov:
            gulicky = 3
            print(f"{predošlý_názov}: {'●'*gulicky}")
            ctypes.windll.user32.MessageBoxW(0, "All packages are complete", "Exit", MB_OK)
            driver.quit()
            raise SystemExit(0)
        elif balik_na_spustenie_názov != vybrany_balik:
            gulicky = 3
            vybrany_balik = balik_na_spustenie_názov
            print(f"{predošlý_názov}: {'●'*gulicky}")
            print("Switching to next package:", balik_na_spustenie_názov)
            try:
                element = riadok.find_element(By.CSS_SELECTOR, "div.actionBtn.btn.btn-mic.btn-block")
                začatý_balík = True
            except:
                začatý_balík = False
            vybrany_balik_el = balik_na_spustenie

            if začatý_balík == False:
                zisti_slovíčka_normálne()
            else:
                zisti_slovíčka_začatého()
            gulicky = 0
        elif balik_na_spustenie_názov == vybrany_balik:
            gulicky += 1
            prázdne = 3 - gulicky
            print(f"{balik_na_spustenie_názov}: {'●'*gulicky}{'○'*prázdne}")
            predošlý_názov = balik_na_spustenie_názov
            driver.execute_script("arguments[0].scrollIntoView();", balik_na_spustenie)
            balik_na_spustenie.click()
        time.sleep(0.4)
