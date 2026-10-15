"""GymTrack Mini: a terminal-based workout diary."""

import json
from datetime import datetime
from pathlib import Path


# Keep the data file in the same folder as this Python file.
DATA_FILE = Path(__file__).resolve().parent / "workouts.json"


def load_workouts():
    """Load saved workout entries, or return an empty list."""
    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            workouts = json.load(file)

        # Check that the file contains the expected data structure.
        required_fields = {
            "date", "exercise", "weight", "sets", "reps"
        }

        if not isinstance(workouts, list):
            raise ValueError("The saved data must be a list.")

        for workout in workouts:
            if not isinstance(workout, dict):
                raise ValueError("Invalid workout entry.")

            if not required_fields.issubset(workout):
                raise ValueError("A workout entry is missing information.")

        return workouts

    except (OSError, ValueError) as error:
        # Do not replace an unreadable file with an empty diary.
        print(f"\nCould not load the workout file: {error}")
        print("Check workouts.json before running the program again.")
        return None


def save_workouts(workouts):
    """Save all workout entries to the JSON file."""
    try:
        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(
                workouts,
                file,
                indent=4,
                ensure_ascii=False
            )
        return True

    except OSError as error:
        print(f"\nCould not save the workouts: {error}")
        return False


def read_date():
    """Ask for a valid date in DD.MM.YYYY format."""
    while True:
        value = input(
            "Date (DD.MM.YYYY, or Enter for today): "
        ).strip()

        if not value:
            return datetime.now().strftime("%d.%m.%Y")

        try:
            date = datetime.strptime(value, "%d.%m.%Y")
            return date.strftime("%d.%m.%Y")
        except ValueError:
            print("Enter a valid date, for example 15.10.2026.")


def read_positive_integer(prompt):
    """Ask for a whole number greater than zero."""
    while True:
        try:
            value = int(input(prompt))

            if value > 0:
                return value

            print("Enter a whole number greater than zero.")

        except ValueError:
            print("Invalid input. Enter a whole number.")


def read_weight():
    """Ask for a finite, non-negative weight in kilograms."""
    while True:
        try:
            # Accept either a decimal dot or a decimal comma.
            value = input("Weight (kg, 0 for bodyweight): ").strip()
            weight = float(value.replace(",", "."))

            if 0 <= weight < float("inf"):
                return weight

            print("Enter a valid weight of zero or more.")

        except ValueError:
            print("Invalid input. Enter a number such as 60 or 12.5.")


def add_workout(workouts):
    """Ask for workout details and save a new entry."""
    print("\n--- Add workout entry ---")

    date = read_date()

    while True:
        exercise = input("Exercise name: ").strip()

        if exercise:
            break

        print("The exercise name cannot be empty.")

    weight = read_weight()
    sets = read_positive_integer("Number of sets: ")
    reps = read_positive_integer("Reps per set: ")

    workout = {
        "date": date,
        "exercise": exercise,
        "weight": weight,
        "sets": sets,
        "reps": reps
    }

    # Only update the in-memory list if saving succeeds.
    updated_workouts = workouts + [workout]

    if save_workouts(updated_workouts):
        workouts.append(workout)
        print("\nWorkout entry saved successfully!")


def display_workout(number, workout):
    """Display one workout entry with its list number."""
    weight = str(workout["weight"]).removesuffix(".0")
    print(
        f"{number}. {workout['date']} | "
        f"{workout['exercise']} | "
        f"{weight} kg | "
        f"{workout['sets']} sets x {workout['reps']} reps"
    )


def show_workouts(workouts):
    """Display all workout entries in the order they were added."""
    print("\n--- All workout entries ---")

    if not workouts:
        print("No workout entries yet.")
        return

    for number, workout in enumerate(workouts, start=1):
        display_workout(number, workout)


def search_workouts(workouts):
    """Find entries whose exercise name contains the search text."""
    print("\n--- Search by exercise ---")

    if not workouts:
        print("No workout entries to search.")
        return

    search_text = input("Exercise name: ").strip().casefold()

    if not search_text:
        print("Search text cannot be empty.")
        return

    found = False

    # Keep the original entry numbers in the search results.
    for number, workout in enumerate(workouts, start=1):
        if search_text in workout["exercise"].casefold():
            display_workout(number, workout)
            found = True

    if not found:
        print("No matching workout entries found.")


def delete_workout(workouts):
    """Delete a selected entry after asking for confirmation."""
    if not workouts:
        print("\nNo workout entries to delete.")
        return

    show_workouts(workouts)

    while True:
        choice = input(
            "\nEntry number to delete (0 to cancel): "
        ).strip()

        try:
            number = int(choice)
        except ValueError:
            print("Enter a valid whole number.")
            continue

        if number == 0:
            print("Deletion cancelled.")
            return

        if 1 <= number <= len(workouts):
            break

        print("Choose an entry number from the list.")

    workout = workouts[number - 1]

    confirmation = input(
        f"Delete '{workout['exercise']}' "
        f"from {workout['date']}? (y/n): "
    ).strip().lower()

    if confirmation != "y":
        print("Deletion cancelled.")
        return

    updated_workouts = workouts.copy()
    updated_workouts.pop(number - 1)

    if save_workouts(updated_workouts):
        workouts.pop(number - 1)
        print("Workout entry deleted.")


def show_menu():
    """Display the application's main menu."""
    print("\n=== GYMTRACK MINI ===")
    print("1. Add workout entry")
    print("2. Show all entries")
    print("3. Search by exercise")
    print("4. Delete an entry")
    print("0. Exit")


def main():
    """Load the diary and run the main menu loop."""
    workouts = load_workouts()

    if workouts is None:
        return

    try:
        while True:
            show_menu()
            choice = input("Choose an option: ").strip()

            if choice == "1":
                add_workout(workouts)
            elif choice == "2":
                show_workouts(workouts)
            elif choice == "3":
                search_workouts(workouts)
            elif choice == "4":
                delete_workout(workouts)
            elif choice == "0":
                break
            else:
                print("Invalid choice. Select 0, 1, 2, 3, or 4.")
    except (EOFError, KeyboardInterrupt):
        print()

    print("Goodbye! Keep training!")


# Start the application only when this file is run directly.
if __name__ == "__main__":
    main()
