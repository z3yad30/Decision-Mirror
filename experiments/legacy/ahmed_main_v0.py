import os
import json
import time
import random

from dotenv import load_dotenv
from groq import Groq


# ==========================================
# 1. Load API Key
# ==========================================

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY was not found")


# ==========================================
# 2. Create Groq Client
# ==========================================

client = Groq(api_key=api_key)


# ==========================================
# 3. Read Prompt
# ==========================================

with open("prompt.txt", "r", encoding="utf-8") as file:
    prompt = file.read()


# ==========================================
# 4. Read Golden Dataset
# ==========================================

with open("decision_mirror_gold_dataset.json", "r", encoding="utf-8") as file:
    dataset = json.load(file)


# ==========================================
# 5. Prepare output file
# ==========================================

responses_file = "responses.json"

if os.path.exists(responses_file):
    with open(responses_file, "r", encoding="utf-8") as file:
        responses = json.load(file)
else:
    responses = []


# ==========================================
# 6. Run the model on each record
# ==========================================

for record in dataset["records"]:

    record_id = record["record_id"]

    print(f"Processing {record_id}...")


    # Build the input that the LLM should see
    decision_input = {
        "decision_id": record["record_id"],
        "user_id": record["record_id"],
        "source_type": record["source"],
        "decision_text": (
            f"Scenario:\n{record['scenario']}\n\n"
            f"User answer:\n{record['answer_text']}"
        ),
        "ontology_version": "v1.0"
    }


      # ==========================================
    # Send request to Groq with retry handling
    # ==========================================

    max_retries = 3
    success = False

    for attempt in range(max_retries):

        try:

            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",

                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user",
                        "content": json.dumps(
                            decision_input,
                            ensure_ascii=False
                        )
                    }
                ],
            )

            # Get model response
            model_response = response.choices[0].message.content

            # ==========================================
            # Save successful result
            # ==========================================

            result = {
                "record_id": record_id,
                "gold_value": record["gold_value"],
                "model_response": model_response
            }

            responses.append(result)

            with open(responses_file, "w", encoding="utf-8") as file:
                json.dump(
                    responses,
                    file,
                    ensure_ascii=False,
                    indent=2
                )

            print(f"✓ {record_id} completed")

            success = True
            break


        except Exception as e:

            error_message = str(e)

            # ==========================================
            # Rate Limit (429)
            # ==========================================

            if "429" in error_message or "Rate limit" in error_message:

                if attempt < max_retries - 1:

                    wait_time = 10 * (attempt + 1)

                    print(
                        f"⚠ Rate limit for {record_id}. "
                        f"Waiting {wait_time}s..."
                    )

                    time.sleep(wait_time)

                else:

                    print(
                        f"✗ {record_id} failed after "
                        f"{max_retries} attempts."
                    )

            # ==========================================
            # Other Errors
            # ==========================================

            else:

                print(f"✗ Error with {record_id}: {e}")

                error_result = {
                    "record_id": record_id,
                    "gold_value": record["gold_value"],
                    "error": error_message
                }

                responses.append(error_result)

                with open(responses_file, "w", encoding="utf-8") as file:
                    json.dump(
                        responses,
                        file,
                        ensure_ascii=False,
                        indent=2
                    )

                break


    # ==========================================
    # If all retries failed because of 429
    # ==========================================

    if not success:

        # Check whether this record was already saved
        already_saved = any(
            r.get("record_id") == record_id
            for r in responses
        )

        if not already_saved:

            error_result = {
                "record_id": record_id,
                "gold_value": record["gold_value"],
                "error": "Rate limit exceeded after retries."
            }

            responses.append(error_result)

            with open(responses_file, "w", encoding="utf-8") as file:
                json.dump(
                    responses,
                    file,
                    ensure_ascii=False,
                    indent=2
                )


    # Small delay between successful requests
    time.sleep(3)

print("\n================================")
print("All records processed.")
print("Results saved in responses.json")
print("================================")