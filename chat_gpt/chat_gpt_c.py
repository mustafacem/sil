import openai
import base64
import requests




def ask_chatgpt(question):
    """
    for infrancing the bussnies proposal
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "you are tasked with helping bussnies proposal just create the desired part and don't write anything else ."},
            {"role": "user", "content": question},
        ]
    )
    answer = response['choices'][0]['message']['content']
    return answer


def mandays_chatgpt(notes, aspect):
    """
    for guessing mandays for the given aspect for the excel
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"you are tasked with guesssing {aspect} for price estimate for AI startup, you will be only recive notes and just return  a integer nothing else"},
            {"role": "user", "content": notes},
        ]
    )
    answer = response['choices'][0]['message']['content']
    return answer


def checker(item, part):
    """
    AI checking it's repsonse is correct or not and recommended changes
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "you are tasked with checking if provided text is suitable for given part of bussnies proposal and if you think changes are should made what would you recommend, dont provide a revised version just provide your assessment and reccomendations keep it as short as poosible "},
            {"role": "user", "content": "part of bussnies proposal:" + item + "provided text:" + part },
        ]
    )
    answer = response['choices'][0]['message']['content']
    return answer

def decoder(ocr_output,decoder_prompt):
    """
    for translating ocr output to text
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o",  # or "gpt-3.5-turbo" if you prefer to use that model
        messages=[
            {"role": "system", "content": "You are a tasked with creating normal text from a ocr output from a very bad handwriting  you are just supposed to only return translated text here instructions on how to translate ocr output to text:" + decoder_prompt},
            {"role": "user", "content": ocr_output},
        ]
    )
    answer = response['choices'][0]['message']['content']
    return answer


def process_items(items_dict, notes):

    """
    AI generates nessercy parts of proposal and assign it to the items_dict user can change them via prompts
    """
    print("AI generated Use_case_description :")
    Use_case_description = ask_chatgpt("generate use case description from given notes: "+notes)
    print(f"Use_case_description: {Use_case_description}")
    response = input(f"would you like to enter use case description if so enter y ?")
    if response == 'y':
      Use_case_description =  input(f"Enter desired use case description")

    for item in items_dict:
        task_successful = False
        desired_changes = ""
        while not task_successful:
            prompt = f"{desired_changes} generate {item} for business proposal for {Use_case_description} from : {notes} "
            value = ask_chatgpt(prompt)
            print(f"Assigned value for {item}: {value}")
            print("******************************************************************************************************************************")
            opion_ai = checker(item, value)
            print(f"As AI my opinion on this part of proposal is : {opion_ai}")

            response = input("Happy with output? (y/n): ").strip().lower()
            if response == 'y':
                task_successful = True
                items_dict[item] = value
                print(f"Value for {item} confirmed: {value}\n")
            else:
                desired_changes = input(f"Enter desired changes for {item}: ")