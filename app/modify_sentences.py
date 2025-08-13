import pandas as pd
import time
from langchain_ollama import OllamaLLM
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv

def process_sentence(ollama_llm, sentence, index, retries=2, delay=5):
    prompt = (
        "Ве молам намерно вметни 1 до 5 граматички грешки во следната реченица, "
        "како да е напишана од почетник по македонски јазик без да ја менуваш "
        f"{sentence}\n\nРеченицата со грешки:"
    )

    for attempt in range(retries + 1):
        try:
            response = ollama_llm.invoke(prompt)
            print(f"Row {index} processed.")
            return (index, sentence, response)
        except Exception as e:
            error_msg = str(e)
            if "504" in error_msg or "loading model" in error_msg:
                print(f"Retry {attempt+1}/{retries} for row {index} due to error: {e}")
                time.sleep(delay)
            else:
                print(f"Skipping row {index} due to error: {e}")
                return None

    print(f"Final fail at row {index} after {retries} retries.")
    return None

def modify_sentences_from_csv(input_path, output_path, max_workers=5):
    try:
        df = pd.read_csv(
            input_path,
            header=None,
            quoting=csv.QUOTE_NONE,
            on_bad_lines='skip',
            encoding='utf-8'
        )
    except Exception as e:
        print(f"Failed to read input CSV: {e}")
        return

    ollama_llm = OllamaLLM(model="llama3.3:70b", base_url="https://llama3.finki.ukim.mk")

    print("Warming up the model...")
    try:
        ollama_llm.invoke("Здраво")
        print("Model warmed up successfully.\n")
    except Exception as e:
        print(f"Warm-up failed: {e}\n")
        return

    results = []

    print(f"Starting processing with {max_workers} threads...\n")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(process_sentence, ollama_llm, sentence, i)
            for i, sentence in enumerate(df[1000:1100][0], start=1000)
        ]

        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)

    results.sort(key=lambda x: x[0])

    result_df = pd.DataFrame({
        'original_sentence': [r[1] for r in results],
        'modified_sentence': [r[2] for r in results]
    })

    result_df.to_csv(
        output_path,
        mode='a',
        header=not pd.io.common.file_exists(output_path),
        index=False,
        encoding='utf-8'
    )

    print(f"\nFinished. Output saved to: {output_path}")

if __name__ == "__main__":
    modify_sentences_from_csv(
        "",
        "output_sentences_with_errors.csv",
        max_workers=5
    )
