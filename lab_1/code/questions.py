import random
from typing import List, Union


def get_unlearned_questions():
    questions = {}
    with open("src/unlearned_questions.txt", 'r', encoding='utf-8') as f:
        for row in f.readlines():
            questions[row] = 0
    return questions


class Questions:
    files = {'all': 'src/questions.txt',
             'old': 'src/learned_questions.txt',
             'new': "src/unlearned_questions.txt"}
    status = None  # old new or all
    queue: List[List[Union[int, str]]] = []
    learned_count: int = 0
    inprocess_count: int = 0
    random_state: bool = True

    @classmethod
    def clear_data(cls):
        cls.queue = []
        cls.learned_count = 0
        cls.inprocess_count = 0

    @classmethod
    def repeat_old(cls):
        cls.queue = []
        cls.status = "old"
        cls.read_file()

    @classmethod
    def learn_new(cls):
        cls.queue = []
        cls.status = 'new'
        cls.read_file()

    @classmethod
    def repeat_all(cls):
        cls.queue = []
        cls.status = 'all'
        cls.read_file()

    @classmethod
    def get_question(cls) -> Union[str, None]:
        if len(cls.queue) == 0:
            return None
        return cls.queue[0][0]

    @classmethod
    def read_file(cls):
        with open(cls.files[cls.status], 'r', encoding='utf-8') as f:
            if cls.random_state:
                for text in f.readlines():
                    cls.queue.insert(random.randint(0, len(cls.queue) + 1), [text, 0])
            else:
                for text in f.readlines():
                    cls.queue.append([text, 0])

    @classmethod
    def question_accept(cls):
        """Вызывается, если пользовоатель дал верный ответ на вопрос"""
        cls.queue[0][1] += 1
        if cls.queue[0][1] > 3:
            cls.add_learned()
            text = cls.queue.pop(0)[0]
            cls.remove_from_unlearned(text)
            cls.learned_count += 1
            if cls.inprocess_count >= 1:
                cls.inprocess_count -= 1
        else:
            if cls.queue[0][1] == 1:
                cls.inprocess_count += 1
            place: int = cls.queue[0][1] * 4
            text = cls.queue[0]
            cls.queue.pop(0)
            cls.queue.insert(place, text)

    @classmethod
    def update_learned(cls):
        with open(cls.files['old'], 'w', encoding='utf-8') as f:
            for elem in cls.queue:
                f.write(elem[0])

    @classmethod
    def add_learned(cls):
        """Вызывается после каждого выученного и добавляет его в список выученных
        """
        if cls.status == 'new':
            with open(cls.files['old'], 'a+', encoding='utf-8') as f:
                f.write(cls.queue[0][0])
        elif cls.status == 'all':
            learned = set()
            with open(cls.files['old'], 'r', encoding='utf-8') as f:
                for text in f.readlines():
                    learned.add(text)
            learned.add(cls.queue[0][0])
            with open(cls.files['old'], 'w', encoding='utf-8') as f:
                for text in learned:
                    f.write(text)

    @classmethod
    def remove_from_unlearned(cls, unlearned_text: str):
        """Сохраняет новый список невыученных вопроов после каждого выученного"""
        if cls.status == 'new':
            with open(cls.files['new'], 'w', encoding='utf-8') as f:
                for elem in cls.queue:
                    f.write(elem[0])
        elif cls.status == 'all':
            unlearned = set()
            with open(cls.files['new'], 'r', encoding='utf-8') as f:
                for text in f.readlines():
                    if unlearned_text != text:
                        unlearned.add(text)
            with open(cls.files['new'], 'w', encoding='utf-8') as f:
                for text in unlearned:
                    f.write(text)

    @classmethod
    def delete_from_learned(cls, unlearned_text: str):
        if cls.status == 'old':
            with open(cls.files['old'], 'w', encoding='utf-8') as f:
                for text in cls.queue[1:]:
                    f.write(text[0])
        elif cls.status == 'all':
            learned = set()
            with open(cls.files['old'], 'r', encoding='utf-8') as f:
                for text in f.readlines():
                    if unlearned_text != text:
                        learned.add(text)
            with open(cls.files['old'], 'w', encoding='utf-8') as f:
                for text in learned:
                    f.write(text)

    @classmethod
    def add_to_unlearned(cls, unlearned_text: str):
        if cls.status == 'old':
            with open(cls.files['new'], 'a+', encoding='utf-8') as f:
                f.write(unlearned_text)
        elif cls.status == 'all':
            unlearned = set()
            with open(cls.files['new'], 'r', encoding='utf-8') as f:
                for text in f.readlines():
                    unlearned.add(text)
            unlearned.add(unlearned_text)
            with open(cls.files['new'], 'w', encoding='utf-8') as f:
                for text in unlearned:
                    f.write(text)

    @classmethod
    def question_failed(cls):
        """Вызывается если пользователь провалил вопрос"""
        if cls.inprocess_count >= 1 and cls.queue[0][1] > 0:
            cls.inprocess_count -= 1
        cls.queue[0][1] = 0
        cls.delete_from_learned(cls.queue[0][0])
        cls.add_to_unlearned(cls.queue[0][0])

    @classmethod
    def get_learned(cls):
        return cls.learned_count

    @classmethod
    def get_unlearned(cls):
        return len(cls.queue)

    @classmethod
    def get_inprocess(cls):
        return cls.inprocess_count

    @classmethod
    def skip_question(cls):
        text = cls.queue.pop(0)
        if text[1] > 0:
            cls.inprocess_count -= 1
        cls.queue.append([text[0], 0])

    @classmethod
    def set_random_state(cls, random_state: bool) -> None:
        cls.random_state = random_state

