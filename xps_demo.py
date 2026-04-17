import collections
import collections.abc
collections.Mapping = collections.abc.Mapping

from datetime import datetime
from experta import KnowledgeEngine, Fact, Rule, Field, MATCH
from experta import AS, TEST


class Intent(Fact):
    """Represents a user intent extracted from the prompt."""
    intent = Field(str, mandatory=True)

class Location(Fact):
    """Represents a location in the smart home (e.g., 'Badezimmer', 'Schlafzimmer')."""
    place = Field(str, mandatory=True)

class Parameter(Fact):
    """Represents additional parameters such as brightness, temperature, timer durations."""
    name = Field(str, mandatory=True)
    value = Field(object, mandatory=True)

class DeviceStatus(Fact):
    """Represents the status of a smart home device."""
    device = Field(str, mandatory=True)
    status = Field(str, mandatory=True)  # e.g., 'on', 'off'

class DateInfo(Fact):
    """Repräsentiert ein Datum, z. B. für geplante Aktionen."""
    date = Field(str, mandatory=True)  # Format z. B. '2025-06-01'

class TimeOfDay(Fact):
    """Repräsentiert die Tageszeit (z. B. 'morgens', 'nachmittags', 'abends', 'nachts')."""
    period = Field(str, mandatory=True)
class PresenceStatus(Fact):
    """Gibt an, ob sich Bewohner im Smart Home befinden."""
    present = Field(bool, mandatory=True)
class UsageEvent(Fact):
    """Repräsentiert ein Ereignis der Nutzung eines Geräts in einem Raum."""
    device = Field(str, mandatory=True)     # z. B. 'licht'
    place = Field(str, mandatory=True)      # z. B. 'abstellkammer'
    timestamp = Field(float, mandatory=True)  # Unix-Timestamp oder datetime.timestamp()
class UsagePatternDetected(Fact):
    """Wird abgeleitet, wenn ein Nutzungsverhalten ein Muster ergibt."""
    device = Field(str, mandatory=True)
    place = Field(str, mandatory=True)
    pattern = Field(str, mandatory=True)  # z. B. 'frequent_use'

class time(Fact):
    uhrzeit = Field(float, mandatory=True)
    lenght = Field(float, mandatory=True)

class temperatur(Fact):
    outside = Field(float,mandatory=True)
    inside = Field(float,mandatory=True)





class SmartHomeEngine(KnowledgeEngine):
    @Rule(Intent(intent='turn_on_light'), Location(place=MATCH.place))
    def rule_turn_on_light(self, place):
        # Check if someone is in the room (for demo purposes, assume True)
        person_present = True
        if person_present:
            self.declare(DeviceStatus(device='licht',status='on'))
            print(f"Licht im {place} wird eingeschaltet.")
        else:
            print(f"Kein Bewohner im {place}. Licht bleibt aus.")

    @Rule(Intent(intent='lower_blinds'), Location(place=MATCH.place))
    def rule_lower_blinds(self, place):
        print(f"Rolläden im {place} werden heruntergefahren.")
        # Beispiel: Licht an, wenn Bewohner im Raum ist
        person_present = True
        if person_present:
            self.declare(DeviceStatus(device='blinds',status='on') )
            print(f"Licht im {place} wird ebenfalls eingeschaltet.")
        else:
            print(f"Kein Bewohner im {place}. Licht bleibt aus.")

    @Rule(Intent(intent='turn_on_vacuum'))
    def rule_turn_on_vacuum(self):
     print("Staubsauger wird gestartet.")
     self.declare(DeviceStatus(device='staubsauger', status='on'))

    @Rule(TimeOfDay(period='morgens'))
    def rule_morning_greeting(self):
        print("Guten Morgen! Ich hoffe, du hast gut geschlafen.")
        
    @Rule(Intent(intent='prepare_for_guests'), DateInfo(date=MATCH.date))
    def rule_prepare_for_guests_with_date(self, date):
        print(f"Vorbereitungen für Gäste werden für den {date} getroffen.")   

    @Rule(Intent(intent='turn_on_light'), Location(place=MATCH.place), PresenceStatus(present=True))
    def rule_turn_on_light_with_presence(self, place):
        print(f"Licht im {place} wird eingeschaltet (Bewohner erkannt).")

    @Rule(Intent(intent='turn_on_light'), Location(place=MATCH.place), PresenceStatus(present=False))
    def rule_turn_on_light_without_presence(self, place):
        print(f"Licht im {place} bleibt aus (kein Bewohner erkannt).")
    
    @Rule(AS.e1 << UsageEvent(device='licht', place='Abstellkammer', timestamp=MATCH.t1),
        AS.e2 << UsageEvent(device='licht', place='Abstellkammer', timestamp=MATCH.t2),
        AS.e3 << UsageEvent(device='licht', place='Abstellkammer', timestamp=MATCH.t3),
        TEST(lambda t1, t2, t3: max(t1, t2, t3) - min(t1, t2, t3) < 86400))  # innerhalb 24h
    def rule_detect_frequent_usage_in_abstellkammer(self, e1, e2, e3):
        print("Häufige Nutzung des Lichts in der Abstellkammer erkannt.")
        self.declare(UsagePatternDetected(device='licht', place='Abstellkammer', pattern='frequent_use'))
    
    @Rule(Intent(intent='turn_on_light'), Location(place='Abstellkammer'), UsagePatternDetected(device='licht', place='Abstellkammer', pattern='frequent_use'))
    def rule_adapt_light_duration(self):
        print("Licht in der Abstellkammer wird eingeschaltet und bleibt heute länger an.")    

    @Rule(Intent(intent='emergency_help'))
    def rule_emergency(self):
        print("Notrufnummern werden kontaktiert: Polizei, Krankenwagen, Feuerwehr.")

    @Rule(Intent(intent='turn_off_microwave'))
    def rule_turn_off_microwave(self):
        print("Mikrowelle wird ausgeschaltet.")

    @Rule(Intent(intent='turn_on_radio'), Location(place=MATCH.place))
    def rule_turn_on_radio(self, place):
        print(f"Televison in der {place} wird eingeschaltet.")

    @Rule(Intent(intent='turn_on_television'), Location(place=MATCH.place))
    def rule_turn_on_television(self, place):
        print(f"Television in der {place} wird eingeschaltet.")

    @Rule(Intent(intent='dim_light'), Location(place=MATCH.place), Parameter(name='brightness', value=MATCH.value))
    def rule_dim_light(self, place, value):
        print(f"Licht in der {place} wird auf {value}% gedimmt.")

    @Rule(Intent(intent='set_microwave_timer'), Parameter(name='timer', value=MATCH.value))
    def rule_set_microwave_timer(self, value):
        print(f"Timer der Mikrowelle wird auf {value} Minuten gesetzt.")

    @Rule(Intent(intent='set_temperature'), Location(place=MATCH.place), Parameter(name='temperature', value=MATCH.temp), Parameter(name='duration', value=MATCH.dur))
    def rule_set_temperature(self, place, temp, dur):
        print(f"Temperatur im {place} wird auf {temp}°C eingestellt für {dur} Stunden.")

    @Rule(Intent(intent='halloween_ambience'), Location(place='Wohnzimmer'))
    def rule_halloween_ambience(self):
        print("Lichter im Wohnzimmer werden gedimmt und auf Orange/Lila gestellt.")
        print("Halloween-Playlist wird auf mittlerer Lautstärke abgespielt.")

    @Rule(Intent(intent='prepare_for_guests'))
    def rule_prepare_for_guests(self):
        print("Staubsaugroboter wird geschickt, um zu reinigen.")
        print("Fenster im Wohnzimmer, Küche und Partyraum werden gekippt, um zu lüften.")

    @Rule(Intent(intent='cozy_evening'), Location(place='Wohnzimmer'))
    def rule_cozy_evening(self, place):
        print(f"Licht in der {place} wird auf 25% gedimmt mit warmer Lichtfarbe.")
        print(f"Sanfte Hintergrundmusik wird im {place} gestartet.")
        print(f"Temperatur im {place} wird auf 22°C reguliert.")
        print(f"Vorhänge im {place} werden zugezogen.")
        print("Smart-Kerzen-Modus wird aktiviert.")

    @Rule(Intent(intent='open_window'), Parameter(name='alarm_mode', value=True))
    def rule_alarm_mode_open_window(self):
      self.declare(DeviceStatus(device='Alarmanlage', status='on'))
      self.declare(DeviceStatus(device='Fenster', status='open'))
      print("Achtung! Fensteröffnung im Alarmmodus – Sicherheitswarnung wird ausgelöst.")


def parse_prompt(prompt):
    facts = []
    text = prompt.lower()

    # Einfache Intent-Erkennung
    if 'hilfe' in text or 'notruf' in text:
        facts.append(Intent(intent='emergency_help'))
        return facts

    # Licht ein
    if 'licht' in text and ('an' in text or 'einschalten' in text):
        facts.append(Intent(intent='turn_on_light'))

    # Licht dimmen
    if 'dimme' in text or 'dimmung' in text:
        facts.append(Intent(intent='dim_light'))
        # Extrahiere Prozentangabe
        import re
        match = re.search(r'(\d{1,3})\s*%', prompt)
        if match:
            brightness = int(match.group(1))
        else:
            brightness = 50  # Standardwert
        facts.append(Parameter(name='brightness', value=brightness))
    
    # Aktuelles Datum einfügen
    heute = datetime.now().strftime('%Y-%m-%d')
    facts.append(DateInfo(date=heute))
    now = datetime.now().timestamp()
    facts.append(UsageEvent(device='licht', place='Abstellkammer', timestamp=now))

    # Tageszeit einfügen basierend auf aktueller Uhrzeit
    stunde = datetime.now().hour
    if 5 <= stunde < 11:
        facts.append(TimeOfDay(period='morgens'))
    elif 11 <= stunde < 17:
     facts.append(TimeOfDay(period='nachmittags'))
    elif 17 <= stunde < 22:
        facts.append(TimeOfDay(period='abends'))
    else:
        facts.append(TimeOfDay(period='nachts'))

    # Für Demo-Zwecke fest auf True gesetzt. Kann man auch mit sensordaten
    facts.append(PresenceStatus(present=True))

    # Rolläden runter
    if 'rolläden' in text or 'rolladen' in text:
        facts.append(Intent(intent='lower_blinds'))
    
    # Staubsauger einschalten
    if 'staubsauger' in text and ('an' in text or 'einschalten' in text or 'start' in text):
        facts.append(Intent(intent='turn_on_vacuum'))

    # Mikrowelle ausschalten
    if 'mikrowelle' in text and 'aus' in text:
        facts.append(Intent(intent='turn_off_microwave'))

    # Radio an
    if 'radio' in text and ('an' in text or 'einschalten' in text):
        facts.append(Intent(intent='turn_on_radio'))

    # Mikrowellen-Timer setzen
    if 'timer' in text and 'mikrowelle' in text:
        facts.append(Intent(intent='set_microwave_timer'))
        import re
        match = re.search(r'(\d+)\s*min', prompt)
        if match:
            timer_value = int(match.group(1))
            facts.append(Parameter(name='timer', value=timer_value))

    # Temperatur setzen
    if 'temperatur' in text and 'stellen' in text:
        facts.append(Intent(intent='set_temperature'))
        import re
        match_temp = re.search(r'(\d{1,2})\s*grad', prompt)
        match_dur = re.search(r'(\d+)\s*stunde', prompt)
        if match_temp:
            temp_value = int(match_temp.group(1))
            facts.append(Parameter(name='temperature', value=temp_value))
        else:
            temp_value = 20
            facts.append(Parameter(name='temperature', value=temp_value))
        if match_dur:
            dur_value = int(match_dur.group(1))
            facts.append(Parameter(name='duration', value=dur_value))
        else:
            dur_value = 1
            facts.append(Parameter(name='duration', value=dur_value))

    # Halloween-Ambiente
    if 'halloween' in text and 'wohnzimmer' in text:
        facts.append(Intent(intent='halloween_ambience'))

    # Vorbereitung für Gäste
    if 'gäste' in text:
        facts.append(Intent(intent='prepare_for_guests'))

    # Gemütlichen Abend
    if 'gemütlich' in text or 'gemuetlich' in text:
        facts.append(Intent(intent='cozy_evening'))

    # Ortserkennung
    for location in ['badezimmer', 'schlafzimmer', 'küche', 'wohnzimmer', 'partyraum']:
        if location in text:
            facts.append(Location(place=location.capitalize()))

    return facts

# Beispiel
if __name__ == '__main__':
    engine = SmartHomeEngine()
    engine.reset()

    prompts = [
        "Mache das Licht im Badezimmer an",  # Facts: turn_on_light, Location('Badezimmer')
        "Rolläden im Schlafzimmer runtermachen",  # Facts: lower_blinds, Location('Schlafzimmer')
        "HILFEEEEE",
        "Schalte Mikrowelle aus",
        "Mach bitte das Radio an und dimme das Licht in der Küche.",
        "Kannst du Timer von Mikrowelle auf 4 Minuten setzen",
        "Kannst du Raumtemperatur auf 23 Grad stellen für die nächsten 3 Stunden",
        "Ich möchte Halloween-Ambiente im Wohnzimmer",
        "Ich erwarte später Gäste",
        "Ich will es heute Abend richtig gemütlich haben, kannst du das regeln?"
    ]

    for prompt in prompts:
        print(f"\nPrompt: {prompt}")
        facts = parse_prompt(prompt)
        for fact in facts:
            engine.declare(fact)
        engine.run()

        engine.reset()

# Zum Ausprobieren:
# pip install experta