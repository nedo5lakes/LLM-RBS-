
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

def main():
    # Modellname
    model_name = "mistralai/Mistral-7B-v0.1"

    # Tokenizer laden
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
 # Gerät auswählen: GPU (cuda) falls verfügbar, sonst CPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Verwende Gerät: {device}")

    # Modell laden
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        device_map={"": device},
        trust_remote_code=True
    )
#Pipeline aufsetzen
    generator = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer
    )

    # Prompt abfragen
    prompt = input("Bitte gib deine Prompt ein: ")

    # Text generieren
    output = generator(
        prompt,
        max_length=50,
        do_sample=True,
        temperature=0.7
    )

    # Ergebnis ausgeben
    print("\nAntwort: ", output[0]["generated_text"])

if __name__ == "__main__":
    main()