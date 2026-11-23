import json 

class Evaluation:
    def __init__(self):
        self.correct_result = 0
        self.incorrect_result = 0
        self.total_result = 0
        self.human_evaluation = 0
        self.correct_result_list = []
        self.incorrect_result_list = []
        self.human_evaluation_list = []

    def evaluate(self, extracted_result_path, given_labels_path) -> None:
        file_name = extracted_result_path.split("/")[-1]
        with open(extracted_result_path, "r", encoding="utf-8") as f:
            extracted_result = json.load(f)
        with open(given_labels_path, "r", encoding="utf-8") as f:
            given_labels = json.load(f)
        self.total_result += 1
        for field in given_labels.keys():
            if field not in extracted_result["ExtractionRequests"][0]:
                self.incorrect_result += 1
                self.incorrect_result_list.append([file_name, field, label_value, extracted_value, "Not Found"])
                return
            label_value = given_labels[field]
            extracted_value = extracted_result["ExtractionRequests"][0][field]
            if isinstance(label_value, str) and isinstance(extracted_value, str):
                same = extracted_value.lower().strip() == label_value.lower().strip()
            else:
                same = extracted_value == label_value
            if not same:
                self.incorrect_result += 1
                self.incorrect_result_list.append([file_name, field, label_value, extracted_value, "Incorrect"])
                return

        self.correct_result += 1
        self.correct_result_list.append([file_name, "Correct"])
        if extracted_result["ExtractionRequests"][0]["calculation_status"] == "Human-Evaluation-Required":
            self.human_evaluation += 1
            self.human_evaluation_list.append([file_name, field, label_value, extracted_value, "Human-Evaluation-Required", extracted_result["ExtractionRequests"][0]["calculation_reason"]])

    def get_correct_result(self) -> int:
        return self.correct_result

    def get_incorrect_result(self) -> int:
        return self.incorrect_result

    def get_total_result(self) -> int:
        return self.total_result
        
    def get_human_evaluation(self) -> int:
        return self.human_evaluation
    
    def get_accuracy(self) -> float:
        return self.correct_result / self.total_result

    def get_incorrect_result_list(self) -> list:
        return self.incorrect_result_list

    def get_human_evaluation_list(self) -> list:
        return self.human_evaluation_list

    def get_correct_result_list(self) -> list:
        return self.correct_result_list