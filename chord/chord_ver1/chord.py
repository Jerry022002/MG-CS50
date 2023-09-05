# cspell: disable

# Libraries
import pygame.midi
from pychord import Chord

# List of note names and corresponding MIDI note number
note_list = [
    ('C', 60),
    ('C#', 61),
    ('D', 62),
    ('D#', 63),
    ('E', 64),
    ('F', 65),
    ('F#', 66),
    ('G', 67),
    ('G#', 68),
    ('A', 69),
    ('A#', 70),
    ('B', 71)
]

def chord_octave (number_of_octave):
    standard_note_list = [
        ('C', 60),
        ('C#', 61),
        ('D', 62),
        ('D#', 63),
        ('E', 64),
        ('F', 65),
        ('F#', 66),
        ('G', 67),
        ('G#', 68),
        ('A', 69),
        ('A#', 70),
        ('B', 71)
    ]

    adjusted_note_list = []
    for note_name, midi_number in standard_note_list:
        adjusted_midi_number = midi_number + (12 * number_of_octave)
        adjusted_note_list.append((note_name, adjusted_midi_number))
    return adjusted_note_list

# List of instruments and corresponding MIDI program number
instruments = [
    {0: 'piano'},
    {25: 'guitar'},
    {40: 'violin'},
    {56: 'trumpet'},
    {73: 'flute'}
]

# Play chord progression function
def chord_progression_play(chord_progressions, tempo, time_signature,instrument_program, octave):

    """
    chord_progression: list of chords to be played
    tempo: in BPM, how fast being played between each chord themselves before moving to next chord
    time_signature: turple how many time of playing each chord before moving to the next chord
    instrument_program: the instrument to be played: 0: piano, 25: guitar, 40: violin, 56: trumpet, 73: flute
    """

    # Initialize the pygame MIDI module
    pygame.midi.init()

    # Set up the MIDI output device
    output_device = pygame.midi.get_default_output_id()
    midi_out = pygame.midi.Output(output_device)

    # Set the velocity (volume) for all notes
    velocity = 100

    # Set the duration for each chord (in milliseconds)
    chord_duration_ms = int(round((60/tempo)*1000)); # 1 second tempo = 60 BPM

    # Set the instrument program
    for instrument in instruments:
        if list(instrument.values())[0] == instrument_program:            
            midi_out.set_instrument(list(instrument.keys())[0])

    # Generate the MIDI note numbers for each chord
    for chords in range(len(chord_progressions)):
        chord_progressions[chords] = chord_generator(chord_progressions[chords], octave)

    # Get the MIDI note numbers and chord names
    chord_ls = [list(d.values())[0] for d in chord_progressions]
    midi_ls = [list(d.keys())[0] for d in chord_progressions]

    # Play the chord progression
    for chord_notes in chord_ls:
        # Play each chord for the duration of the time signature    
        for beat in range(time_signature[0]):
            if beat == 0:
                # Play the first beat stronger
                # Play each note in the chord simultaneously
                for note_number in chord_notes:
                    midi_out.note_on(note_number, velocity + 20)
                # Wait for the chord duration
                pygame.time.wait(chord_duration_ms)
                # Stop playing the chord
                for note_number in chord_notes:
                    midi_out.note_off(note_number)
            else:
                # Play the remaining beats
                # Play each note in the chord simultaneously
                for note_number in chord_notes:
                    midi_out.note_on(note_number, velocity)
                # Wait for the chord duration
                pygame.time.wait(chord_duration_ms)
                # Stop playing the chord
                for note_number in chord_notes:
                    midi_out.note_off(note_number)
            

    # Clean up and close the MIDI output
    midi_out.close()
    pygame.midi.quit()

# Generate chord function
def chord_generator(chord, octave):
    midi = []
    
    # If the user input is correct
    try:
        # Ensure the user input is case sensitive
        
        # Capitalize the first letter
        if len(chord) == 1:
            chord = chord.upper()
        else:
            # Capitalize the first letter
            first_letter = chord[0].upper()
            # Lowercase the remaining letters
            remaining_letters = chord[1:].lower()
            # Concatenate the modified letters
            chord = first_letter + remaining_letters
        # Get the MIDI note numbers in the chord
        notes_ls = Chord(chord).components()
    # If the user input the chord name incorrectly
    except:
        return None
    
    # Return the list of MIDI note numbers in the chord
    for notes in notes_ls:
        for note, midi_number in chord_octave(octave):
            if notes == note:
                midi.append(midi_number)
    return {chord: midi}


    




