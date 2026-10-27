"""Explicit conversion of the first challenge log, preserving ambiguous scores."""
from ..listening import ListeningAssessment, GenerationContext, RatedObservation, ListeningValue, ReportedProblems


def convert_report(report: dict) -> ListeningAssessment:
    observations = report["observations"]
    raw_metal = observations.get("heavy_riff_and_drums")
    qualification = report.get("rating_qualifications", {}).get("heavy_riff_and_drums")
    musical = [RatedObservation(id=id, label=label, score=observations.get(key)) for id, label, key in [
        ("throat-technique", "Throat drone and overtone", "throat_drone_and_overtone"),
        ("pop-hook", "Clear sung pop hook", "bright_pop_hook"),
        ("role-coexistence", "Three roles coexist in chorus", "simultaneous_fusion"),
        ("bell-motif", "Bell motif relates to the hook", "bell_motif"),
        ("bridge-return", "Throat exposed in bridge and return", "bridge_throat_and_return"),
    ]]
    musical.insert(2, RatedObservation(id="metal-arrangement", label="Metal riffs and rhythmic movement", score=None,
        note=f"Original combined metal/sound question: {raw_metal}. No separate arrangement score was supplied. " +
        ("User clarified that the lower score concerned thin sound, explicitly not a prompt failure." if qualification else
         "Do not split this combined rating into independent arrangement and sound-quality scores.")))
    sound = [RatedObservation(id="sound-body", label="Body, weight and fullness", score=raw_metal if qualification else None,
        note="User explained the original 1 as thin rendered sound." if qualification else
             f"Original combined question scored {raw_metal}; a separate sound-body rating remains open."),
        RatedObservation(id="clarity", label="Clarity and separation", note="Not separately rated.")]
    problems_known = str(report["issue_observation"].get("interpretation", "")).startswith("No listed problems")
    confirmation = report.get("prompt_identity_confirmation", {})
    identity = (f"User confirmed {confirmation['style']} and {confirmation.get('lyrics', 'lyrics identity unspecified')}. "
                if confirmation.get("source") == "explicit_user_confirmation" and confirmation.get("style") else
                "Prompt and lyrics identity are unconfirmed. ")
    return ListeningAssessment(
        generation=GenerationContext(provider="Suno", model=report["actual_model"],
            settings={key: report.get(key) for key in ["weirdness", "style_influence", "variety", "persona", "audio_upload", "generation_mode"]},
            song_reference=report.get("song_url_or_local_path") or "",
            input_note=identity + "Song identity, remaining controls and sample count are unconfirmed.",
            style_sha256=report.get("style_sha256"), lyrics_sha256=report.get("lyrics_sha256")),
        musical_execution=musical, sound_quality=sound,
        listening_value=ListeningValue(immediate_replay=observations.get("first_listen_replay_value"),
            later_replay=observations.get("later_listen_replay_value")),
        problems=ReportedProblems(**{key: "none" if problems_known else "unknown"
            for key in ["sung_instructions", "omitted_lyrics", "merged_voices"]},
            note=("User explicitly confirmed that no listed problems were heard."
                  if report["issue_observation"].get("confirmation") == "explicit_user_confirmation" else
                  "No listed problems reported, using the question meaning confirmed in the preceding report.")
                 if problems_known else "Problem occurrence has not been confirmed."),
        interpretation="User attributes thin sound to Suno generally for this kind of song, explicitly not to the prompt. This is the user's attribution, not an independently established cause." if qualification else "",
        raw_report=report,
    )
