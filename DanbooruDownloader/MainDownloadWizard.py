from DanbooruDownloader.DownloadPics import DownloadMultipleTags
import os


def isPath(path):
    '''
    Checks if a directory is valid or not
    :param path: A directory
    :return: The directory if and only if it is valid.
    '''
    if os.path.isdir(path) and len(path) != 0:
        print("The path exists. Continuing with the download...")
        return path
    else:
        new_path = input('Please provide a path to the folder you want your pictures to be installed:\n')
        return isPath(new_path)


def isContinue(answer):
    '''
    Checks if more tag needs to be added
    :param answer: An answer
    :return: True if more is needed, False otherwise
    '''
    if answer.lower() == "y" or answer.lower() == "yes":
        continue_adding = True
    elif answer.lower() == "n" or answer.lower() == "yes":
        continue_adding = False
    return continue_adding


def question():
    '''
    Manually let the user pick the tags
    :return: A list of tags
    :type: list
    '''
    user_input_list = []
    continue_input = True
    acceptable_boolean_answers = ["Y", "N", "yes", "no", "Yes", "No", "YEs", "NO", 'YeS', "nO", "yES", "yeS", "yEs", "YES",
                                  "y", "n"]
    while continue_input:
        user_input = input("Please enter your desired tag on Danbooru: ")
        user_input_list.append(user_input)
        answer = input("Do you want to search for another tag? Y/N: ")
        if answer in acceptable_boolean_answers:
            continue_input = isContinue(answer)
        else:
            satisfactory_format = False
            while not satisfactory_format:
                print("Please enter Y or N.")
                answer = input("Do you want to search for another tag? Y/N: ")
                if answer in acceptable_boolean_answers:
                    satisfactory_format = True
                else:
                    satisfactory_format = False
            continue_input = isContinue(answer)
    print()
    return user_input_list

def start_download(user_input_list,path):
    '''
    Starts the download
    :param user_input_list: A list of inputs
    :param path: A directory
    '''
    DownloadMultipleTags(user_input_list, path).initiate_download()



