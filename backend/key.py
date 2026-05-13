import google.generativeai as genai
genai.configure(api_key="AIzaSyC-veFKO7oI0sqHEV67iVoBVNOkj2TpoOM")

model = genai.GenerativeModel("gemini-1.5-flash")

response = model.generate_content("hello")

print(response.text)