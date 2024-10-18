import requests; import json; import time; import pickle 
import PyPDF2; import io

idx = 4774
uri = f'https://api.results.scc-events.com/cert/{idx}?ei=BM&l=en&st=rr&y=2023'

response = requests.get(uri)

if response.status_code == 200:
    #read PDF content
    with io.BytesIO(response.content) as pdf_file:
        #extract text 
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            text = page.extract_text()
            print(text)
else:
    print(f"Failed to fetch PDF: {response.status_code}")