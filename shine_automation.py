import cv2
import numpy as np
import pyautogui
import threading
import time
import os
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# === Configuration ===
EMAIL = "atarun716@gmail.com"
PASSWORD = "Tarun@2840"
JOB_TITLE = "Software Tester"
LOCATION = "Hyderabad"
EXPERIENCE_YEARS = "2"

# === Screen Recording Function (with stop event) ===
def screen_record(filename, stop_event, fps=10):
    screen_size = pyautogui.size()
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(filename, fourcc, fps, screen_size)
    print("🎥 Screen recording started...")
    while not stop_event.is_set():
        img = pyautogui.screenshot()
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        out.write(frame)
        time.sleep(1 / fps)
    out.release()
    print(f"🎥 Screen recording saved: {filename}")

# === Screenshot Helper ===
def take_screenshot(driver, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    driver.save_screenshot(path)
    print(f"[📸] Screenshot saved: {path}")

# === Selenium Automation ===
def run_automation():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    wait = WebDriverWait(driver, 15)

    try:
        driver.get("https://www.shine.com")
        print(f"🌐 Page Title: {driver.title}")
        print(f"🔗 URL: {driver.current_url}")

        # Login
        top_login_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(),'Login')]")))
        top_login_btn.click()

        email_field = wait.until(EC.visibility_of_element_located((By.ID, "id_email_login")))
        email_field.send_keys(EMAIL)

        password_field = driver.find_element(By.ID, "id_password")
        password_field.send_keys(PASSWORD)

        final_login_btn = driver.find_element(By.XPATH,
            "//*[@id=\"cndidate_login_widget\"]/div[1]/form[5]/ul[1]/li[4]/div/button")
        final_login_btn.click()

        wait.until(EC.url_contains("shine.com"))
        take_screenshot(driver, "screenshots/1_login_success.png")
        print("✅ Logged in successfully")

        # Search Jobs
        search_container = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//*[@id='ReactContainer']/div[1]/div/div/div[1]/div[1]/div/div/div")))
        search_container.click()
        time.sleep(1.5)

        job_input = wait.until(EC.visibility_of_element_located((By.ID, "id_q")))
        job_input.clear()
        job_input.send_keys(JOB_TITLE)

        location_input = wait.until(EC.visibility_of_element_located((By.ID, "id_loc")))
        location_input.clear()
        location_input.send_keys(LOCATION)

        exp_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='search_exp_div']")))
        exp_dropdown.click()
        two_years = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='item-key-2']/label")))
        two_years.click()

        search_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id=\"frm_adv_srch\"]/div[2]")))
        search_button.click()
        take_screenshot(driver, "screenshots/2_search_filled.png")
        print("🔎 Search submitted")

        # Select second job
        time.sleep(4)
        second_job_card = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//*[@id='__next']/div[3]/div[2]/div[2]/div/div/div[2]/div[5]")))
        second_job_card.click()

        # Job Details
        job_title_elem = wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//*[@id='jdCardNova']/div[1]/div[1]/div[1]/h1")))
        company_name_elem = wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//*[@id='jdCardNova']/div[1]/div[1]/div[1]/span")))

        job_title = job_title_elem.text
        company_name = company_name_elem.text

        print(f"🧾 Job Title: {job_title}")
        print(f"🏢 Company Name: {company_name}")
        take_screenshot(driver, "screenshots/3_job_detail.png")

        # Apply
        apply_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//*[starts-with(@id, 'id_apply_')]")))
        apply_btn.click()
        print("📨 Apply button clicked")

        time.sleep(3)

        # Confirm Application
        applied_btn = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//*[starts-with(@id, 'id_apply_')]")))
        button_text = applied_btn.text.strip()
        disabled_attr = applied_btn.get_attribute("disabled")
        is_actually_disabled = disabled_attr is not None

        if (button_text.lower() in ["applied", "already applied"]) and is_actually_disabled:
            print(f"✅ Application confirmed. Button shows: {button_text}")
            take_screenshot(driver, "screenshots/4_applied_status_confirmed.png")
        else:
            print(f"⚠ Application status unclear. Button text: {button_text}, disabled: {disabled_attr}")

    except Exception as e:
        print(f"❌ Automation failed: {e}")
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    # Create a stop event for the recording thread
    stop_event = threading.Event()
    rec_thread = threading.Thread(target=screen_record, args=("automation_record.mp4", stop_event, 10))
    rec_thread.start()

    # Run Selenium automation
    run_automation()

    # Signal the recording thread to stop and wait for it to finish
    stop_event.set()
    rec_thread.join()
