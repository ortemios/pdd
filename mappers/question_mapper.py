from model.menu_state import MenuState
from model.question import Question


class QuestionMapper:

    def from_json(self, json: dict) -> Question:
        question = Question()
        question.id = json['id']
        question.image = f'https://raw.githubusercontent.com/etspring/pdd_russia/master{json["image"][1:]}?raw=true' if 'no_image.jpg' not in json["image"] else ''
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
