"""Explicit English vocabulary additions reviewed for release 0.3.

Source tokens are preserved; meanings are editorial musical explanations.
Legacy source tag grades do not establish current Suno performance.
"""


def extend_vocabulary(band_entries, cook_entries, entry, evidence, band, cook, tags, core):
    legacy = evidence("legacy catalogue; publisher HIGH instrument-tag grading",
        "Musical explanation is an editorial adaptation. Listing a token does not establish reliable current-model instrument control; no model version or test count is inferred.")
    instrument_groups = [
        ("`[Piano]`, `[Electric Piano]`", [
            ("rhodes", "[Rhodes]", "A tine-based electric-piano timbre, from mellow rounded notes to a bell-like attack."),
            ("hammond", "[Hammond Organ]", "A tonewheel-organ sound associated with drawbar registration and sustained tones."),
            ("clavinet", "[Clavinet]", "A plucked-string electric-keyboard timbre with a sharp, percussive attack."),
        ]),
        ("`[Synth]`, `[Analog Synth]`", [
            ("synth-pad", "[Synth Pad]", "A sustained synthesizer layer supporting harmony or atmosphere."),
            ("lead-synth", "[Lead Synth]", "A synthesizer voice carrying a foreground melody or hook."),
            ("synth-stabs", "[Synth Stabs]", "Short accented synth notes or chords used as rhythmic punctuation."),
            ("arpeggiated-synth", "[Arpeggiated Synth]", "A synth pattern that presents chord tones successively rather than simultaneously."),
            ("acid-bass", "[Acid Bass]", "A resonant, squelching synth-bass character commonly associated with acid dance styles."),
            ("supersaw", "[Supersaw]", "A thick synthesizer texture built from multiple detuned sawtooth voices."),
        ]),
        ("`[Acoustic Guitar]`, `[Electric Guitar]`", [
            ("slide-guitar", "[Slide Guitar]", "Guitar played with a slide, allowing continuous pitch glides between notes."),
            ("twelve-string", "[12-String Guitar]", "A guitar with paired string courses producing a bright, doubled shimmer."),
            ("slap-bass", "[Slap Bass]", "A percussive bass technique using thumb strikes and often plucked or popped strings."),
            ("fretless-bass", "[Fretless Bass]", "Bass played without frets, allowing continuous slides and flexible intonation."),
            ("string-quartet", "[String Quartet]", "A four-part bowed-string ensemble, conventionally two violins, viola and cello."),
            ("pizzicato", "[Pizzicato]", "Plucked articulation on a string instrument, especially in contrast to bowed playing."),
            ("cello", "[Cello]", "A bowed low-to-middle-register string instrument that can support bass, harmony or a melody."),
            ("mandolin", "[Mandolin]", "A small plucked-string instrument with a bright attack and short sustain."),
        ]),
        ("`[Saxophone]`, `[Tenor Sax]`", [
            ("tenor-sax", "[Tenor Sax]", "A saxophone voice with a lower range than alto sax, usable for melody or ensemble parts."),
            ("brass-section", "[Brass Section]", "A group of brass instruments used for ensemble lines, sustained chords or rhythmic accents."),
            ("harmonica", "[Harmonica]", "A breath-driven free-reed instrument often used for compact melodic phrases and bends."),
        ]),
        ("`[Drums]`, `[Acoustic Drums]`", [
            ("brushed-drums", "[Brushed Drums]", "Drum-kit articulation using brushes for swishes and softer attacks."),
            ("drum-machine", "[Drum Machine]", "Programmed percussion produced by a dedicated machine or its sampled or synthesized sound."),
            ("tr909", "[TR-909]", "A Roland drum-machine sound palette associated with punchy electronic dance rhythms."),
            ("trap-hihats", "[Trap Hi-Hats]", "Rapid hi-hat subdivisions, rolls and rhythmic variation associated with trap production."),
            ("congas", "[Congas]", "Tall hand drums used for pitched accents and interlocking percussion patterns."),
            ("shaker", "[Shaker]", "A shaken percussion instrument providing a continuous or accented subdivision texture."),
        ]),
    ]
    for fragment, rows in instrument_groups:
        for id, text, meaning in rows:
            band_entries.append(entry("band-manager", band, id, "term", tags, fragment, text, meaning, "instrumentation", legacy, "lyrics"))

    vocal_rows = [
        ("whispered", "| `[Whispered]` /", "[Whispered]", "Breath-dominant whispered delivery rather than a fully voiced sung tone."),
        ("spoken-word", "| `[Spoken]` /", "[Spoken Word]", "Words delivered as speech rather than a pitched sung melody."),
        ("belting", "| `[Belted]` /", "[Belting]", "A forceful, projecting singing approach often used for a strong upper-range phrase."),
        ("falsetto", "| `[Falsetto]` /", "[Falsetto]", "A vocal register often heard as lighter or airier; not simply a synonym for every high note or for head voice."),
        ("chest-voice", "| `[Chest Voice]` |", "[Chest Voice]", "A chest-dominant vocal registration or tonal quality, rather than a fixed note range."),
        ("breathy", "| `[Breathy]` |", "[Breathy]", "An audible airflow component mixed into the sung tone."),
        ("raspy", "| `[Raspy]` |", "[Raspy]", "A rough or grainy vocal texture; this alone does not specify loudness or pitch register."),
        ("crooning", "| `[Crooning]` |", "[Crooning]", "A soft, intimate microphone-oriented singing style."),
        ("adlibs", "| `[Ad-libs]` /", "[Ad-libs]", "Additional short vocal phrases or ornaments around a main melody or lyric."),
        ("melisma", "| `[Vocal Run]` /", "[Melisma]", "Several successive pitches sung on one syllable; not a requirement for multiple syllables."),
        ("vibrato", "| `[Vibrato]` |", "[Vibrato]", "A repeated small pitch variation around a sustained sung note."),
        ("staccato", "| `[Staccato]` |", "[Staccato]", "Short, detached articulation with audible separation between notes."),
        ("legato", "| `[Legato]` |", "[Legato]", "Connected articulation that joins successive sung notes smoothly."),
        ("call-response", "| `[Call and Response]` |", "[Call and Response]", "An answering pattern between alternating voices or between a voice and an instrument."),
        ("scat", "| `[Scat]` |", "[Scat]", "Vocal improvisation using nonlexical syllables, often in jazz."),
        ("humming", "| `[Hummed]` /", "[Humming]", "A closed-mouth or mostly closed-mouth melodic vocal sound without articulated words."),
        ("backing-vocals", "| `[Backing Vocals]` |", "[Backing Vocals]", "Supporting vocal parts behind or around the main singer."),
        ("stacked-harmonies", "| `[Stacked Harmonies]` |", "[Stacked Harmonies]", "Multiple layered vocal parts creating a dense harmonic texture."),
        ("slow-flow", "| `[Slow Flow]` |", "[Slow Flow]", "A rap delivery leaving generous space between phrases or syllabic groups."),
        ("melodic-rap", "| `[Melodic Rap]` |", "[Melodic Rap]", "Delivery combining rap-like rhythmic placement with a noticeable sung pitch contour."),
        ("vocoder", "| `[Vocoder]` |", "[Vocoder]", "A processed vocal effect that transfers speech-like articulation to a carrier sound, commonly a synthesizer."),
        ("telephone-vocal", "| `[Telephone Effect]` |", "[Telephone Effect]", "A deliberately bandwidth-limited vocal color suggesting telephone transmission."),
    ]
    for id, fragment, text, meaning in vocal_rows:
        ev = evidence("legacy vocal catalogue; row not independently verified",
            "The musical term is useful independently of the bracket syntax. Source includes mixed reliability grades; no current-model reliability is inferred.")
        if id == "falsetto":
            ev["source_label"] = "LOW reliability (publisher, citing HookGenius)"
            ev["context"] += " Source explicitly reports inconsistent falsetto tag results; head voice and falsetto are not normalized as equivalent concepts."
        band_entries.append(entry("band-manager", band, id, "term", tags, fragment, text, meaning, "vocals", ev, "lyrics"))

    rhythms = [
        ("half-time", "| `[Half-Time]` |", "[Half-Time]", "A drum feel perceived at half the prevailing pulse, often by spacing backbeat accents farther apart without changing the underlying tempo."),
        ("swung", "| `[Swung Feel]` /", "[Swung Feel]", "Unequal timing of paired subdivisions instead of evenly spaced straight notes; the amount of swing can vary."),
        ("triplet", "| `[Triplet Feel]` |", "[Triplet Feel]", "A feel organized around three subdivisions of a beat rather than two or four equal subdivisions."),
        ("syncopated", "| `[Syncopated]` |", "[Syncopated]", "Accents or attacks placed away from expected strong beats, often emphasizing offbeats."),
        ("straight", "| `[Straight]` |", "[Straight]", "Even subdivision timing rather than swung subdivision pairs."),
        ("four-floor", "| `[Four on the Floor]` |", "[Four on the Floor]", "A kick-drum hit on each quarter-note beat of a four-beat bar."),
        ("polyrhythmic", "| `[Polyrhythmic]` |", "[Polyrhythmic]", "Simultaneous rhythmic layers using contrasting subdivisions or groupings, such as three against two."),
        ("breakbeat", "| `[Breakbeat]` |", "[Breakbeat]", "A groove based on a broken or syncopated drum-break pattern rather than only an unbroken four-on-the-floor kick."),
        ("double-time", "| `[Double Time]` |", "[Double Time]", "A drum feel with increased accent or subdivision density suggesting twice the pace; it need not change the underlying tempo."),
    ]
    for id, fragment, text, meaning in rhythms:
        band_entries.append(entry("band-manager", band, id, "term", tags, fragment, text, meaning, "rhythm",
            evidence("legacy rhythm catalogue; publisher grading",
            "Definition describes musical feel, not a guaranteed tempo transformation. Model version and reliability are not established by this table."), "lyrics"))

    dynamics = [
        ("swell", "| `[Swell]` |", "[Swell]", "A gradual rise in intensity or level, often within a sustained sound or short passage.", "arrangement"),
        ("crescendo", "| `[Crescendo]` |", "[Crescendo]", "An increase in loudness across a passage; it does not inherently require adding instruments.", "arrangement"),
        ("decrescendo", "| `[Decrescendo]` |", "[Decrescendo]", "A decrease in loudness across a passage.", "arrangement"),
        ("fade-in", "| `[Fade In]` |", "[Fade In]", "An opening level increase from silence or a low starting level.", "production"),
        ("fade-out", "| `[Fade Out]` /", "[Fade Out]", "A closing level reduction toward silence; source elsewhere reports unreliable rendering, so this is intended behavior rather than a promise.", "production"),
        ("instrumental-fade", "| `[Instrumental Fade Out]` |", "[Instrumental Fade Out]", "An ending in which vocals finish before the instrumental bed fades.", "structure"),
        ("key-change", "| `[Key Change]` /", "[Key Change]", "A move to a new tonal center; the destination and interval require additional musical direction.", "harmony"),
        ("ritardando", "| `[Ritardando]` |", "[Ritardando]", "A gradual slowing of performed tempo. Its musical meaning does not establish that a Suno tag realizes it.", "rhythm"),
    ]
    for id, fragment, text, meaning, category in dynamics:
        band_entries.append(entry("band-manager", band, id, "term", tags, fragment, text, meaning, category,
            evidence("legacy transition catalogue; mixed publisher grades",
            "Intended musical meaning retained even where the source's ending or tempo guidance questions actual tag behavior. Not a verified control."), "lyrics"))
    for id, text, meaning, fragment, category in [
        ("palm-muted", "palm-muted", "Guitar articulation damped with the picking-hand palm near the bridge for a shorter, more percussive sound.", "Each instrument gets a job", "instrumentation"),
        ("backbeat", "backbeat", "Prominent drum accents conventionally on beats two and four in a four-beat groove.", "Tempo as feel", "rhythm"),
        ("hard-stop", "hard stop", "A coordinated abrupt end rather than a fade or sustained play-out.", "State both edges", "structure"),
    ]:
        band_entries.append(entry("band-manager", band, id, "term", core, fragment, text, meaning, category,
            evidence("musical vocabulary selected from v6 production-direction examples",
            "The definition is editorial; no isolated causal effect is claimed for the individual term."), "style"))

    additions = [
        ("acoustic-folk", "Fingerpicked guitar, wooden room", [
            ("earthy-percussion", "earthy percussion", "Percussion described by an organic, less polished texture; specify instruments when precision matters.", "instrumentation"),
            ("wooden-room", "wooden room", "A room-color descriptor suggesting woody reflections rather than a precise measured reverberation.", "production"),
        ]),
        ("acoustic-folk", "Acoustic guitar or fingerpicked ukulele/banjo", [
            ("light-percussion", "light percussion", "A supporting percussion role with restrained weight or density.", "instrumentation"),
            ("fiddle-accent", "fiddle or mandolin accents", "Short string-instrument gestures used as punctuation rather than a continuous foreground lead.", "arrangement"),
        ]),
        ("acoustic-folk", "Natural, grounded, and narrative", [
            ("clear-consonants", "clear consonants", "Articulate consonants to make sung words easier to understand.", "vocals"),
            ("restrained-ornament", "restrained ornamentation", "Use relatively few runs, turns or decorative notes around the main melody.", "vocals"),
        ]),
        ("acoustic-folk", "Around 76–108 BPM", [
            ("room-breath", "leave breath and room sound", "Retain audible breathing and room cues for a less sealed-off acoustic impression.", "production"),
            ("human-dynamics", "Keep dynamics human", "Ask for expressive level differences rather than a uniformly constrained performance; this is a broad direction, not a technical setting.", "production"),
        ]),
        ("english-indie-pop", "Jangly electric guitar, handclaps", [
            ("handclaps", "handclaps", "Clapping sounds used as rhythmic accents or a backing pulse.", "instrumentation"),
            ("airy-synth", "airy synth", "A light or breathy synthesizer texture rather than a dense foreground sound.", "instrumentation"),
        ]),
        ("english-indie-pop", "Clean or slightly chorused electric guitar", [
            ("chorused-guitar", "slightly chorused electric guitar", "Electric guitar with a modest chorus effect that adds moving pitch and time variation.", "production"),
            ("soft-synth-pad", "soft synth pad", "A restrained sustained synth bed supporting harmony behind other parts.", "instrumentation"),
            ("countermelody", "simple countermelody", "A secondary melodic line that complements the principal melody without competing with it.", "arrangement"),
        ]),
        ("english-indie-pop", "Conversational and slightly vulnerable", [
            ("conversational-vocal", "Conversational", "Singing shaped with speech-like intimacy or phrasing; it can remain pitched singing rather than spoken word.", "vocals"),
            ("repeated-melodic-phrase", "one big repeated melodic phrase", "Center a section on a recurring melodic hook rather than continuously new material.", "structure"),
        ]),
        ("english-indie-pop", "Around 100–124 BPM", [
            ("verse-chorus-contrast", "dynamic verse/chorus contrast", "Make the verse and chorus differ audibly in level, density or instrumental activity.", "arrangement"),
        ]),
        ("electronic-dance", "Kick, clap, hi-hats, bass synth", [
            ("chord-stab", "chord stab", "A short sharply articulated chord used as a rhythmic accent.", "instrumentation"),
            ("riser", "riser", "A sound that develops upward in pitch, brightness or intensity to signal a transition.", "arrangement"),
            ("vocal-chops", "sparse vocal chops", "Brief cut-up vocal gestures used sparingly as rhythmic or melodic texture.", "vocals"),
            ("bass-synth", "bass synth", "A synthesizer assigned to the low-frequency bass role.", "instrumentation"),
        ]),
        ("electronic-dance", "Short and rhythmic", [
            ("pre-drop-phrase", "memorable phrase before the drop", "Place a short identifying vocal idea immediately before the electronic payoff.", "structure"),
        ]),
        ("electronic-dance", "Common range 122–130 BPM", [
            ("groove-reset", "a groove reset", "A section that reduces or reorganizes the groove before the next lift.", "arrangement"),
            ("one-drop-idea", "one drop idea", "Give the main drop one clear central motif rather than several competing ideas.", "arrangement"),
            ("final-lift", "one final lift", "Reserve one further rise in energy or density for the closing portion of the track.", "structure"),
        ]),
    ]
    for genre, fragment, rows in additions:
        label = "official-informed" if genre == "english-indie-pop" else "working-hypothesis"
        for id, text, meaning, category in rows:
            cook_entries.append(entry("cookbook", cook, id, "phrase", f"library/genres/{genre}.md", fragment, text, meaning, category,
                evidence(label, "Wording is from this genre page. Meaning is an editorial explanation; musical usefulness is separate from demonstrated Suno response.", ("v6",),
                    "source_claim" if label == "official-informed" else "working_hypothesis"), "style"))
