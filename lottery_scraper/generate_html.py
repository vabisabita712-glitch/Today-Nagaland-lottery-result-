import json
import os
from datetime import datetime

def create_html_page():
    """
    Reads lottery results from a JSON file and generates a mobile-friendly
    HTML page to display them, with the latest result featured at the top.
    """
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, 'results.json')
    html_path = os.path.join(script_dir, 'lottery_results.html')

    # ধাপ ১: JSON ফাইল পড়া
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        results = data.get("lottery_results", [])
        if not results:
            print("JSON ফাইলে কোনো ফলাফল পাওয়া যায়নি।")
            return
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"'{json_path}' ফাইলটি পড়া যায়নি বা এটি সঠিক JSON ফরম্যাটে নেই। ত্রুটি: {e}")
        return

    # ধাপ ২: তারিখ ও সময় অনুযায়ী ফলাফল সাজানো
    def sort_key(result):
        # তারিখ এবং সময়কে datetime অবজেক্টে রূপান্তর করা হচ্ছে
        # সময় থেকে 'AM/PM' বাদ দিয়ে এবং 12-ঘণ্টার ফরম্যাটকে 24-ঘণ্টায় রূপান্তর করে
        time_str = result['draw_time'].replace(' ', '')
        datetime_str = f"{result['draw_date']} {time_str}"
        return datetime.strptime(datetime_str, '%d-%m-%Y %I:%M%p')

    results.sort(key=sort_key, reverse=True)

    latest_result = results[0]
    older_results = results[1:]

    # ধাপ ৩: HTML কনটেন্ট তৈরি করা

    # HTML হেড এবং স্টাইল
    html_content = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>লটারি রেজাল্ট</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 15px; background-color: #f0f2f5; color: #1c1e21; }
        .container { max-width: 900px; margin: auto; background: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); }
        h1, h2, h3 { text-align: center; color: #1877f2; }
        .latest-result { background-color: #e7f3ff; border: 1px solid #1877f2; padding: 20px; margin-bottom: 30px; border-radius: 8px; }
        .latest-result h2 { margin-top: 0; font-size: 1.8em; }
        .older-results h3 { border-bottom: 2px solid #e0e0e0; padding-bottom: 10px; margin-top: 40px; }
        .result-item { border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; border-radius: 8px; background-color: #fafafa; }
        .result-item p { margin: 5px 0; font-size: 1.1em; }
        .result-numbers { display: flex; flex-wrap: wrap; gap: 10px; list-style: none; padding: 0; margin-top: 10px; justify-content: center; }
        .result-numbers li { background-color: #42b72a; color: white; padding: 10px 15px; border-radius: 50px; font-weight: bold; font-size: 1.2em; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2); }
        footer { text-align: center; margin-top: 30px; color: #65676b; }
    </style>
</head>
<body>
    <div class="container">
        <h1>লটারি সংবাদ</h1>
    """

    # সর্বশেষ ফলাফল যোগ করা
    html_content += f"""
        <div class="latest-result">
            <h2>সর্বশেষ ফলাফল</h2>
            <p><strong>তারিখ:</strong> {latest_result['draw_date']}</p>
            <p><strong>সময়:</strong> {latest_result['draw_time']}</p>
            <h3>বিজয়ী নম্বর:</h3>
            <ul class="result-numbers">
                {''.join(f"<li>{num}</li>" for num in latest_result['result_numbers'])}
            </ul>
        </div>
    """

    # পুরানো ফলাফল যোগ করা
    if older_results:
        html_content += """
        <div class="older-results">
            <h3>পুরানো ফলাফল</h3>
        """
        for result in older_results:
            html_content += f"""
            <div class="result-item">
                <p><strong>তারিখ:</strong> {result['draw_date']}</p>
                <p><strong>সময়:</strong> {result['draw_time']}</p>
                <ul class="result-numbers">
                    {''.join(f"<li>{num}</li>" for num in result['result_numbers'])}
                </ul>
            </div>
            """
        html_content += "</div>"

    # HTML শেষ করা
    html_content += """
        <footer>
            <p>&copy; 2025 লটারি রেজাল্ট ওয়েবসাইট। সর্বস্বত্ব সংরক্ষিত।</p>
        </footer>
    </div>
</body>
</html>
    """

    # ধাপ ৪: HTML ফাইল লেখা
    try:
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"HTML পেজ সফলভাবে '{html_path}' ফাইলে তৈরি করা হয়েছে।")
    except IOError as e:
        print(f"HTML ফাইল লেখায় সমস্যা হয়েছে: {e}")

if __name__ == "__main__":
    create_html_page()
