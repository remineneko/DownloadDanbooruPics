from BackgroundCode.DownloadPics import DownloadMultipleTags

def manual_download():
    '''
    Manually let the user pick and download the tags
    :return:
    '''
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


    print("Welcome to Danbooru Downloader!")
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

    DownloadMultipleTags(user_input_list).initiate_download()

def auto_download():
    '''
    Automatically downloads pictures with a given list of tags.
    '''
    list_of_tags = ['mash_kyrielight','mysterious_heroine_x_(alter)','hk416_(girls_frontline)',
                    'osakabe-hime_(fate/grand_order)','sesshouin_kiara']
    DownloadMultipleTags(list_of_tags).initiate_download()

def main():
    auto_download()


main()