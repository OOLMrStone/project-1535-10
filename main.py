import io
import sys
import g4f
import random
import spacy

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from googletrans import Translator

with open("startWindow.ui", encoding="utf8") as uif:
    start_template = uif.read()
with open("mainWindow.ui", encoding="utf8") as uif:
    template = uif.read()
with open("endWindow.ui", encoding="utf8") as uif:
    end_template = uif.read()

language_codes = {"English": "en",
                  "Spanish": "es",
                  "German": "de",
                  "Italian": "it",
                  "Chinese (simplified)": "zh",
                  "French": "fr"}

def ask_ai(question):
    response = g4f.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": question}],
    )

    return response


def prompt(language, level, words) -> str:
    return f"""Generate a new {language} text that will contain {random.randint(250, 340)}-{random.randint(360, 450)} words. 
    Text has to be {level} level, so it would not be hard for people at that level of language to read it.
    Text also needed to contain ALL of these words: {words}.
    Also let it will be only text in your response, nothing else"""


def translate(word: str, language: str):
    try:
        result = Translator().translate(word, dest=language).text
    except Exception:
        result = "Проверьте текст на отсутствие опечаток и попробуйте снова."
    return result


def to_usual_from(word, language):
    nlp = spacy.load(f'{language_codes[language]}_core_web_sm')
    doc = nlp(word)
    return ' '.join([token.lemma_ for token in doc])


class StartWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        f = io.StringIO(start_template)
        uic.loadUi(f, self)

        self.loadFileBtn.clicked.connect(self.load_file)
        self.saveFileBtn.clicked.connect(self.save_file)

    def load_file(self):
        file_name = QFileDialog.getOpenFileName(self, 'Выберите файл:', '')[0]
        if file_name:
            with open(file_name) as nf:
                self.setP.setPlainText(nf.read())

    def save_file(self):
        file_name = QFileDialog.getOpenFileName(self, 'Выберите файл:', '')[0]
        if file_name:
            with open(file_name, 'w') as nf:
                nf.write(self.setP.toPlainText())



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        f = io.StringIO(template)
        uic.loadUi(f, self)

        self.words_data = {}
        self.knowledge = {}
        self.words = None
        self.end_window = None
        self.start_window = None

        self.startBtn.clicked.connect(self.run)
        self.statBtn.clicked.connect(self.view_stat)
        self.checkTBtn.clicked.connect(self.check_translate)
        self.seeTBtn.clicked.connect(self.see_translate)
        self.endBtn.clicked.connect(self.end_train)
        self.returnButton.clicked.connect(self.make_word_set)

    def run(self):
        if self.start_window is None:
            self.statusLabel.setText("Набор слов отсутствует.")
            return
        # TODO: inform user about the text is generating
        self.words_data = {word.split(' - ')[0]: set(word.split(' - ')[1].split(', '))
                           for word in self.start_window.setP.toPlainText().lower().split('\n')}
        self.words = [word for word in self.words_data]
        text = ask_ai(prompt(str(self.lang_query.currentText()),
                             str(self.lvl_query.currentText()), ', '.join(self.words)))
        text = "\n\n".join(text.split("\n\n")[1:-1])
        self.textBrowser.setText(text)

    def view_stat(self):
        self.end_window = EndWindow()
        self.end_window.show()
        print(self.knowledge)
        for word, kn in self.knowledge.items():
            marks = int(3 - (kn[0] / max(kn[1], 1)) * 3)
            percentage = round(kn[0] * 100 / max(kn[1], 1))
            self.end_window.statView.insertPlainText(f"{'!' * marks} {word} - {percentage}%\n")

    def check_translate(self):
        if self.words is None:
            self.statusLabel.setText("Набор слов отсутствует.")
            return
        current_word = self.wordP.text().lower()
        if current_word not in self.words:
            self.statusLabel.setText("Такого слова нет в наборе.")
            return

        self.knowledge[current_word] = self.knowledge.get(current_word, [0, 0])
        self.knowledge[current_word][1] += 1
        if (self.translateP.toPlainText().lower() in self.words_data[current_word] or
                set(self.translateP.toPlainText().lower().split(', ')) == self.words_data[current_word]):
            self.statusLabel.setText("Верный перевод! Так держать!")
            self.knowledge[current_word][0] += 1
        else:
            self.statusLabel.setText('Неверно, нажмите "посмотреть перевод".')

    def see_translate(self):
        self.statusLabel.clear()
        if self.wordP.text().lower() in self.words_data:
            text = ', '.join(self.words_data[self.wordP.text().lower()])
        else:
            base = to_usual_from(self.wordP.text().lower(), self.lang_query.currentText())
            text = f"Перевод фразы: {translate(self.wordP.text().lower(), 'ru')}.\n\n\n"
            if base.lower() != self.wordP.text().lower() and self.wordP.text().lower().count(' ') <= 1:
                text += f"Начальная форма (инфинитив): {base};\n\n"
                text += f"Перевод: {translate(base, 'ru')}."
        self.translateP.setPlainText(text)

    def end_train(self):
        ex.close()
        try:
            self.end_window.close()
        except AttributeError:
            self.view_stat()

    def make_word_set(self):
        self.start_window = StartWindow()
        self.start_window.show()


class EndWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        f = io.StringIO(end_template)
        uic.loadUi(f, self)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.excepthook = except_hook
    ex.show()
    sys.exit(app.exec_())
