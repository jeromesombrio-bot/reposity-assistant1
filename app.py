# Call Gemini API
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            answer_text = "System configuration error: GEMINI_API_KEY environment variable is missing."
        else:
            try:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(temperature=0.1)
                )
                answer_text = response.text.strip()
            except Exception as err:
                print(f"Gemini API Exception: {err}")
                answer_text = f"API Error: {err}"