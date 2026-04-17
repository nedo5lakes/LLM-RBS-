from transformers import pipeline

# Zero-Shot-Pipeline initialisieren
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

intents = [
    "turn_on_light",
    "lower_blinds",
    "emergency_help",
    "turn_on_radio",
    "set_temperature",
    "open_window",
    "close_window"
]

# Mapping von Intents zu formalen Handlungsempfehlungen (Text)
intent_to_text = {
    "turn_on_light": "Ich schalte das Licht an.",
    "lower_blinds": "Ich fahre die Rolläden herunter.",
    "emergency_help": "Ich rufe sofort Hilfe.",
    "turn_on_radio": "Ich schalte das Radio ein.",
    "set_temperature": "Ich passe die Temperatur an.",
    "open_window": "Ich öffne das Fenster.",
    "close_window": "Ich schließe das Fenster.",
    "turn_on_television":"Ich schalte den Fernseher an"
}

# Semantische Regeln für Phrasen -> Intents
semantic_rules = [
    {"keywords": ["mir ist warm", "zu heiß", "stickig"], "intent": "open_window"},
    {"keywords": ["mir ist kalt", "friere", "zu kalt"], "intent": "close_window"},
    {"keywords": ["musik hören", "radio", "playlist"], "intent": "turn_on_radio"},
    {"keywords": ["licht an", "dunkel"], "intent": "turn_on_light"},
    {"keywords": ["hilfe", "notruf"], "intent": "emergency_help"}
]

CONFIDENCE_THRESHOLD = 0.7

def semantic_match(prompt):
    prompt_lower = prompt.lower()
    for rule in semantic_rules:
        if any(kw in prompt_lower for kw in rule["keywords"]):
            return rule["intent"]
    return None

def parse_zero_shot(prompt):
    # 1. Semantische Regeln prüfen
    semantic_intent = semantic_match(prompt)
    if semantic_intent:
        return intent_to_text.get(semantic_intent, "Ich weiß nicht, was ich tun soll.")

    # 2. Zero-Shot-Fallback
    result = classifier(prompt, intents)
    best_intent = result["labels"][0]
    best_score = result["scores"][0]

    if best_score < CONFIDENCE_THRESHOLD:
        print(f"⚠️ Unsicherer Score ({best_score:.2f}) - Ergebnis möglicherweise ungenau.")
        return f"Ich bin mir nicht sicher, was du möchtest. Vielleicht: {intent_to_text.get(best_intent)}"

    return intent_to_text.get(best_intent, "Ich weiß nicht, was ich tun soll.")

# Beispiel
print(parse_zero_shot("Ich öffne das Fenster."))       # → open_window
print(parse_zero_shot("Ich schalte das Licht an."))    # → turn_on_light
print(parse_zero_shot("Ich senke die Temperatur."))    # → set_temperature
print(parse_zero_shot("Ich rufe sofort Hilfe."))       # → emergency_help
print(parse_zero_shot("Ich weiß nicht, was ich tun soll.")) # → unknown_intent