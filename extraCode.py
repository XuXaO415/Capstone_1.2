#In a file called playback.py, implement a program in 
# Python that prompts the user for input and then outputs that same input, 
# replacing each space with ... (i.e., three periods).

from lib2to3.pytree import convert
from tkinter import E
from traceback import print_tb


playback = input("Enter a sentence: ")
playback = playback.replace(" ", "...")
print(playback)



#prompts the user for mass as an integer in kilograms and outputs
#the equivalent number of Joules as an integer.

# def convert_mass_to_joules(mass):
#     return mass * 9.8

# mass = int(input("Enter a mass in kilograms: "))
# int(mass * 9.8)


#implement a function called convert that accepts a str as input and returns that same input with any :) 
# converted to 🙂 (otherwise known as a slightly smiling face) and any :( converted to 🙁 (otherwise known as a slightly frowning face).
# All other text should be returned unchanged.

# def convert(str):
#     if str == ":)":
#         return "😊"
#     elif str == ":(":
#         return "😢"
#     else:
#         return str

# def convert(str):
#     convert = input("Enter a string: \n")
#     if convert == ":)":
#         return "😊"
#     elif convert == ":(":
#         return "😢"
#     else:
#         return convert
#     print(convert)

# convert = input("Enter a string: \n")
# if convert == ":)":
#     print("😊")
# elif convert == ":(":
#     print("😢")
# else:
#     print(convert)

# convert = str(input("Enter a string: \n"))
# if convert == ":)":
#     # print str(input + "😊")
#     print(input + "😊")
# elif convert == ":(":
#     print(input + "😢")
# else:
#     print(input)
#convert  string input to 🙁 or 😊


        
    
     
    
    
#Then, in that same file, implement a function called main that prompts the user for input, 
# calls convert on that input, and prints the result. 
# You’re welcome, but not required, to prompt the user explicitly, as by passing a str of your own as an argument to input. 
# Be sure to call main at the bottom of your fi


def main():
    dollars = dollars_to_float(input("How much was the meal? "))
    percent = percent_to_float(
        input("What percentage would you like to tip? "))
    tip = dollars * percent
    print(f"Leave ${tip:.2f}")


def dollars_to_float(d):
    #TODO
    # accepts a str as input formatted as a dollar amount, remove the leading $ and returns a float
    # print(float(d[1:]))
    # str(d[1:])
    str = d[1:]
    return float(str)
    


    print(float(d))


def percent_to_float(p):
    #TODO

    print(float(p))


main()
