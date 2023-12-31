from model.menu_state import MenuState
from model.question import Question


class QuestionMapper:

    def from_json(self, json: dict) -> Question:
        image = json["image"][2:]
        question = Question()
        question.id = json['id']
        question.image = image if 'no_image.jpg' not in image else ''
        question.text = json['question']
        question.answers = list(
            map(
                lambda answer: answer['answer_text'],
                json['answers']
            ),
        )
        for i, answer in enumerate(json['answers']):
            if answer['is_correct']:
                question.correct_answer_index = i
        question.answer_tip = json['answer_tip']
        return question
