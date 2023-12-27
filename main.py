import io
import sys
import g4f

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog

with open("mainWindow.ui", encoding="utf8") as uif:
    template = uif.read()
with open("endWindow.ui", encoding="utf8") as uif:
    end_template = uif.read()


def ask_ai(question):
    response = g4f.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": question}],
    )

    return response


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        f = io.StringIO(template)
        uic.loadUi(f, self)

        self.words_data = {}
        self.knowledge = {}
        self.endw = None

        self.startBtn.clicked.connect(self.run)
        self.statBtn.clicked.connect(self.view_stat)
        self.checkTBtn.clicked.connect(self.check_translate)
        self.seeTBtn.clicked.connect(self.see_translate)
        self.loadFileBtn.clicked.connect(self.load_file)
        self.endBtn.clicked.connect(self.end_train)

    def run(self):
        self.words_data = {word.split(' - ')[0]: set(word.split(' - ')[1].split(', ')) for word in
                           self.setP.toPlainText().lower().split('\n')}
        self.knowledge = {word: [0, 0] for word in self.words_data}
        words = [word for word in self.words_data]
        text = ask_ai(f"""Generate an english text (200-250 words) that will contain these words:
                            {', '.join(words)}""")
        self.textBrowser.setText(text)

    def view_stat(self):
        self.endw = EndWindow()
        self.endw.show()
        for word, kn in self.knowledge.items():
            self.endw.statView.insertPlainText(
                f"({'!' * int(3 - (kn[0] / max(kn[1], 1)) * 3)}) {word} - {round(kn[0] * 100 / max(kn[1], 1))}%\n")

    def check_translate(self):
        self.knowledge[self.wordP.text().lower()][1] += 1
        if (self.translateP.text().lower() in self.words_data[self.wordP.text().lower()] or
                set(self.translateP.text().lower().split(', ')) == self.words_data[self.wordP.text().lower()]):
            self.statusLabel.setText("Верный перевод! Так держать!")
            self.knowledge[self.wordP.text().lower()][0] += 1
        else:
            self.statusLabel.setText('Неверно, нажмите "посмотреть перевод".')

    def see_translate(self):
        self.translateP.setText(', '.join(self.words_data[self.wordP.text().lower()]))

    def load_file(self):
        fname = QFileDialog.getOpenFileName(self, 'Выберите файл:', '')[0]
        if fname:
            with open(fname) as nf:
                self.setP.setPlainText(nf.read())

    def end_train(self):
        ex.close()
        try:
            self.endw.close()
        except AttributeError:
            self.view_stat()


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
