import csv
import sys


def main():

    # TODO: Check for command-line usage
    # indivuals name of text file(dna sequnce)
    if len(sys.argv) != 3:
        sys.exit("Usage: python dna.py FILENAME FILENAME")

    database_file = sys.argv[1]

    sequence_file = sys.argv[2]

 # TODO: Read database file into a variable
    database = []
    with open(database_file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            database.append(row)

    # print(database)

    # TODO: Read DNA sequence file into a variable
    sequence = []
    with open(sequence_file) as file:
        sequence = file.read()

    # print(sequence)

    # TODO: Find longest match of each STR in DNA sequence
    sub_sequences = []

    for key in database[0].keys():
        if key != "name":
            sub_sequences.append(key)

    person = {

    }

    for sub in sub_sequences:
        person[sub] = longest_match(sequence, sub)
    # print(person)
    # print(sequence)

    # TODO: Check database for matching profiles
    foundMatch = False
    for p in database:
        ismatch = True
        for sub in sub_sequences:
            if str(p[sub]) != str(person[sub]):
                ismatch = False
        if ismatch:
            foundMatch = True
            print(p['name'])

    if foundMatch != True:
        print("No match")

    return


def longest_match(sequence, subsequence):
    """Returns length of longest run of subsequence in sequence."""

    # Initialize variables
    longest_run = 0
    subsequence_length = len(subsequence)
    sequence_length = len(sequence)

    # Check each character in sequence for most consecutive runs of subsequence
    for i in range(sequence_length):

        # Initialize count of consecutive runs
        count = 0

        # Check for a subsequence match in a "substring" (a subset of characters) within sequence
        # If a match, move substring to next potential match in sequence
        # Continue moving substring and checking for matches until out of consecutive matches
        while True:

            # Adjust substring start and end
            start = i + count * subsequence_length
            end = start + subsequence_length

            # If there is a match in the substring
            if sequence[start:end] == subsequence:
                count += 1

            # If there is no match in the substring
            else:
                break

        # Update most consecutive matches found
        longest_run = max(longest_run, count)

    # After checking for runs at each character in seqeuence, return longest run found
    return longest_run


main()
