
#program a simple game
import random

def main():
    print("Bienvenue au jeux de devinette!")
    print("Essayez de deviner un mot entre 1 et 100.")
    print("Try to guess it in as few attempts as possible.")
    print()

    # get a random number between 1 and 100
    number = random.randint(1, 100)

    # initialize variables
    guess = 0
    attempts = 0

    # loop until the user guesses the number
    while guess != number and attempts != 5:
        guess = int(input("Enter your guess: "))
        attempts += 1

        if guess < number:
            print("Trop petit. Reessayez.")
        elif guess > number:
            print("Trop grand. Reessayez.")
        else:
            print("Felicitations ! En ", attempts, " essais, vous avez trouve le mot!")

    print("\nFin du jeu.")
    print("le chiffre etait ", number)
if __name__ == "__main__":
    main()