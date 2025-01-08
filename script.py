from playwright.sync_api import sync_playwright
from PIL import Image
import pytesseract
import re
import time


def solve_arithmetic_captcha(captcha_image_path):
    """
    Extract and solve arithmetic CAPTCHA from the image.
    """
    captcha_image = Image.open(captcha_image_path)
    captcha_text = pytesseract.image_to_string(captcha_image, config="--psm 7")
    print(f"Extracted CAPTCHA text: {captcha_text}")

    # Solve the arithmetic question
    match = re.match(r"(\d+)\s*([\+\-\*/])\s*(\d+)", captcha_text.strip())
    if not match:
        raise ValueError("Invalid CAPTCHA format")
    num1, operator, num2 = match.groups()
    num1, num2 = int(num1), int(num2)

    if operator == "+":
        return num1 + num2
    elif operator == "-":
        return num1 - num2
    elif operator == "*":
        return num1 * num2
    elif operator == "/":
        return num1 // num2  # Integer division
    else:
        raise ValueError("Unsupported operator")


def main():
    captcha_image_path = "captcha.png"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            accept_downloads=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        )

        page = context.new_page()
        page.goto("https://itax.kra.go.ke/KRA-Portal/pinChecker.htm", timeout=60000)

        # Save the initial page content
        html_content = page.content()
        with open("kra.html", "w+", encoding="utf8") as kFile:
            kFile.write(html_content)
        
        # Fill the KRA PIN
        page.fill("#vo\\.pinNo", "A013757674Z")

        # Wait for the CAPTCHA image to load
        page.wait_for_selector("#captcha_img")

        # Capture the CAPTCHA image
        captcha_element = page.query_selector("#captcha_img")
        captcha_element.screenshot(path=captcha_image_path)
        print(f"CAPTCHA image saved as {captcha_image_path}")

        # Solve the CAPTCHA
        captcha_solution = solve_arithmetic_captcha(captcha_image_path)
        print(f"CAPTCHA solution: {captcha_solution}")

        # Fill the CAPTCHA solution
        page.fill("#captcahText", str(captcha_solution))  # Replace with the correct input selector

        # Submit the form
        page.click("#consult")  # Replace with the correct button selector
        print("CAPTCHA solved and form submitted.")

        html_content = page.content()
        with open("kra.html", "w+", encoding="utf8") as kFile:
            kFile.write(html_content)

        # Locate the second table with the class 'tab3 whitepapartdBig'
        second_table = page.locator("table.tab3.whitepapartdBig").nth(1)

        # Extract data from the rows of the table
        rows = second_table.locator("tr")
        for i in range(rows.count()):
            cells = rows.nth(i).locator("td")
            row_data = [cells.nth(j).inner_text() for j in range(cells.count())]
            if(row_data[0] == "PIN Status"):
                print(row_data[1])
            #print(row_data)
        # Wait for the page to process
        time.sleep(20)
        browser.close()


if __name__ == "__main__":
    main()
