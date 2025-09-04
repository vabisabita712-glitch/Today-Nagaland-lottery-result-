import requests
from bs4 import BeautifulSoup
import json
from PyPDF2 import PdfReader
import io
import re
from urllib.parse import urljoin
import os

# প্রধান ফাংশন যা পুরো স্ক্র্যাপিং প্রক্রিয়াটি চালাবে
def scrape_lottery_results():
    """
    এই ফাংশনটি নাগাল্যান্ড রাজ্য লটারির ওয়েবসাইট থেকে ফলাফল স্ক্র্যাপ করে।
    এটি লেটেস্ট রেজাল্টের PDF লিঙ্ক খুঁজে বের করে, PDF ডাউনলোড করে,
    এবং ডেটা এক্সট্র্যাক্ট করে একটি JSON ফাইলে সংরক্ষণ করে।
    """
    # নতুন ওয়েবসাইটটির URL
    BASE_URL = "https://nagalandstatelottery.in/"
    print(f"'{BASE_URL}' ওয়েবসাইট ভিজিট করা হচ্ছে...")

    # ধাপ ১: ওয়েবসাইট থেকে HTML কনটেন্ট আনা
    try:
        # কিছু ওয়েবসাইট সাধারণ স্ক্রিপ্ট ব্লক করে, তাই একটি ব্রাউজারের মতো User-Agent পাঠানো হচ্ছে
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(BASE_URL, headers=headers)
        response.raise_for_status()  # কোনো HTTP ত্রুটি থাকলে exception দেখাবে
    except requests.exceptions.RequestException as e:
        print(f"দুঃখিত, ওয়েবসাইট অ্যাক্সেস করা যায়নি: {e}")
        return

    # ধাপ ২: BeautifulSoup ব্যবহার করে HTML পার্স করা
    soup = BeautifulSoup(response.text, 'html.parser')

    # ধাপ ৩: PDF লিঙ্ক খুঁজে বের করা (নতুন এবং সহজ পদ্ধতি)
    pdf_link = ''
    try:
        # আমরা লেটেস্ট রেজাল্ট (8PM) এর সেকশনটি খুঁজব
        # 'h2', 'h3', 'p' ইত্যাদি বিভিন্ন ট্যাগের মধ্যে '8PM Result' লেখাটি খুঁজছি
        latest_result_header = soup.find(['h1', 'h2', 'h3', 'h4', 'p', 'div'], string=re.compile(r'8PM Result', re.IGNORECASE))
        if not latest_result_header:
            raise ValueError("'8PM Result' শিরোনাম খুঁজে পাওয়া যায়নি।")

        # শিরোনামের ঠিক পরেই থাকা 'a' ট্যাগটি খুঁজছি, যার মধ্যে 'GET PDF' লেখা আছে
        # find_next('a') ব্যবহার করে সবচেয়ে কাছের লিঙ্কটি বের করা হচ্ছে
        pdf_link_tag = latest_result_header.find_next('a')

        if not pdf_link_tag or 'pdf' not in pdf_link_tag.get('href', '').lower():
             raise ValueError("'8PM Result' সেকশনের নিচে কোনো PDF লিঙ্ক খুঁজে পাওয়া যায়নি।")

        # লিঙ্কটি সম্পূর্ণ URL হওয়ায় urljoin এর প্রয়োজন নেই
        pdf_link = pdf_link_tag['href']
        print(f"সঠিক PDF লিঙ্ক পাওয়া গেছে: {pdf_link}")

    except (AttributeError, ValueError) as e:
        print(f"PDF লিঙ্ক খুঁজে পাওয়া যায়নি। ওয়েবসাইটের গঠন পরিবর্তন হয়েছে হয়তো। ত্রুটি: {e}")
        return

    # ধাপ ৪: PDF ডাউনলোড করা
    print("PDF ডাউনলোড করা হচ্ছে...")
    try:
        pdf_response = requests.get(pdf_link, headers=headers)
        pdf_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"PDF ডাউনলোড করা যায়নি: {e}")
        return

    # ধাপ ৫: PDF থেকে টেক্সট এক্সট্র্যাক্ট করা
    print("PDF থেকে ডেটা এক্সট্র্যাক্ট করা হচ্ছে...")
    extracted_text = ""
    try:
        # PDF ফাইলটি সরাসরি মেমোরি থেকে পড়া হচ্ছে
        with io.BytesIO(pdf_response.content) as pdf_file:
            reader = PdfReader(pdf_file)
            # সাধারণত রেজাল্ট প্রথম পেজেই থাকে
            page = reader.pages[0]
            extracted_text = page.extract_text()

    except Exception as e:
        print(f"PDF থেকে টেক্সট এক্সট্র্যাক্ট করা যায়নি: {e}")
        return

    # ধাপ ৬: এক্সট্র্যাক্ট করা টেক্সট থেকে প্রয়োজনীয় তথ্য খুঁজে বের করা
    # এই অংশটি PDF এর টেক্সট ফরম্যাটের ওপর নির্ভরশীল
    result_data = {
        "draw_date": None,
        "draw_time": None,
        "first_prize_number": None,
        "source_pdf": pdf_link
    }

    # তারিখ খুঁজে বের করার জন্য নতুন Regex (e.g., 04/09/25)
    date_match = re.search(r'(\d{2}/\d{2}/\d{2})', extracted_text)
    if date_match:
        result_data["draw_date"] = date_match.group(1)

    # সময় খুঁজে বের করার জন্য Regex (e.g., 08:00 PM)
    time_match = re.search(r'(\d{1,2}:\d{2}\s*(?:AM|PM))', extracted_text, re.IGNORECASE)
    if time_match:
        result_data["draw_time"] = time_match.group(1)
    else:
        # যদি সময় না পাওয়া যায়, আমরা ধরে নিচ্ছি এটি 8 PM এর রেজাল্ট
        result_data["draw_time"] = "08:00 PM"

    # প্রথম পুরস্কারের নম্বর খুঁজে বের করার নতুন কৌশল
    # আমরা তারিখের সাথে যুক্ত থাকা ৫-সংখ্যার নম্বরটি খুঁজছি
    prize_match = re.search(r'\d{2}/\d{2}/\d{2}(\d{5})', extracted_text)
    if prize_match:
        result_data["first_prize_number"] = prize_match.group(1)
    else:
        # যদি উপরের পদ্ধতি কাজ না করে, আমরা লটারির নামের পাশের নম্বরটি খুঁজব
        # যেমন: "SANDPIPER THURSDAY 84E 02779"
        prize_match_alt = re.search(r'[A-Z]+\s+THURSDAY\s+[A-Z0-9]+\s+(\d{5})', extracted_text)
        if prize_match_alt:
            result_data["first_prize_number"] = prize_match_alt.group(1)

    print(f"এক্সট্র্যাক্ট করা ডেটা: {result_data}")

    # ধাপ ৭: JSON ফাইলে ডেটা সংরক্ষণ করা
    print("ডেটা results.json ফাইলে সংরক্ষণ করা হচ্ছে...")
    try:
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Define the output file path relative to the script's directory
        output_path = os.path.join(script_dir, 'results.json')

        with open(output_path, 'w', encoding='utf-8') as json_file:
            json.dump(result_data, json_file, ensure_ascii=False, indent=4)
        print(f"স্ক্র্যাপিং সফলভাবে সম্পন্ন হয়েছে! '{output_path}' ফাইলটি দেখুন।")
    except IOError as e:
        print(f"JSON ফাইলে ডেটা সংরক্ষণ করা যায়নি: {e}")


if __name__ == "__main__":
    scrape_lottery_results()
