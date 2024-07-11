from chat_gpt.chat_gpt_c import  ask_chatgpt, process_items
from doc_creation.doc_creation_c import ask_recording_type, create_document, create_excel_with_values, update_excel_file
from ocr_processing.ocr_processing_c import *


def main():
    items_dict = {
    "Target functionality": None,
    "Solution": None,
    "Inputs": None,
    "Outputs": None,
    "Requirements and assumptions": None,
    "PoC vs production implementation": None,
    "Human review of outputs": None,
    "Post-PoC improvements and functionality add-ons": None,
    "Infrastructure": None,
    "Limitations": None
    }
    # Example usage
    #print(ask_chatgpt("is italy good country to invest in ?"))
    notes  = ask_recording_type()
    translation = input("would you like to translate notes ?[y/n]").lower()
    if translation == "y":
        translation = input("would you like to translate to czech or english ?[e/c]").lower()
        if translation =="e":
            notes = ask_chatgpt("traslate this to english if it is czech"+notes)
        elif translation =="c":
            notes = ask_chatgpt("traslate this to czech if it is english"+notes)


    process_items(items_dict, notes)

    print("Final assigned values:")
    for item, value in items_dict.items():
        print(f"{item}: {value}")

    image_path = "proposal_droid\Screenshot 2024-05-23 171557.png"
    create_document(image_path,items_dict)


    create_excel_with_values()

    update_excel_file()



if __name__ == "__main__":
    main()
