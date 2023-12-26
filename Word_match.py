import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QListWidget, QListWidgetItem, QWidget, QLabel
from PyQt5.QtGui import QBrush, QColor, QFontMetrics
from PyQt5.QtCore import Qt


class WordMatching(QMainWindow):
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.initUI()

    def initUI(self):
        self.words, self.meanings, self.meanings_cn = self.readWords(self.file_path)
        self.correct_pairs = dict(zip(self.words, zip(self.meanings, self.meanings_cn)))
        self.matched_pairs = {}
        self.current_word = None
        self.current_meaning = None

        # 创建单词列表和解释列表
        self.words_list = QListWidget()
        self.meanings_list = QListWidget()

        # 填充单词列表
        for word in self.words:
            self.words_list.addItem(word)

        # 填充解释列表，使用random.sample()确保顺序是随机的
        shuffled_meanings = random.sample(self.meanings, len(self.meanings))
        for meaning in shuffled_meanings:
            self.meanings_list.addItem(meaning)

        # 自适应单词列表和解释列表宽度
        self.setListWidth(self.words_list)
        self.setListWidth(self.meanings_list)

        # 创建布局并添加列表和标签
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.words_list)
        main_layout.addWidget(self.meanings_list)

        self.status_label = QLabel("Select a word and then select its meaning.")
        main_layout.addWidget(self.status_label)

        # 设置中央组件
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.setGeometry(300, 300, 800, 400)
        self.setWindowTitle('Word Matching Game')
        self.show()

        # 连接点击事件
        self.words_list.itemClicked.connect(self.word_selected)
        self.meanings_list.itemClicked.connect(self.meaning_selected)

    def setListWidth(self, list_widget):
        font_metrics = QFontMetrics(list_widget.font())
        max_width = 0
        for index in range(list_widget.count()):
            item = list_widget.item(index)
            item_width = font_metrics.width(item.text())
            max_width = max(max_width, item_width)
        # 设置固定宽度，确保不会随着内容的改变而变化
        list_widget.setFixedWidth(max_width + 20)

    def readWords(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        word_triplets = [line.strip().split(';', 2) for line in lines if ';' in line]
        if len(word_triplets) < 10:
            raise ValueError(
                f"The word list must contain at least 10 triplets, but only {len(word_triplets)} were found.")
        selected_triplets = random.sample(word_triplets, min(10, len(word_triplets)))
        words, meanings, meanings_cn = zip(*selected_triplets)
        return list(words), list(meanings), list(meanings_cn)

    def word_selected(self, item):
        self.current_word = item.text()
        self.check_match()

    def meaning_selected(self, item):
        self.current_meaning = item.text()
        self.check_match()

    def check_match(self):
        if self.current_word and self.current_meaning:
            correct_english, correct_chinese = self.correct_pairs[self.current_word]
            is_correct = self.current_meaning == correct_english

            self.matched_pairs[self.current_word] = {
                'selected_meaning': self.current_meaning,
                'correct_meaning': correct_english,  # 这可能是不需要的，因为我们已经有了 correct_pairs
                'chinese_meaning': correct_chinese,
                'is_correct': is_correct
            }

            self.current_word = None
            self.current_meaning = None
            self.update_list_status()

            if len(self.matched_pairs) == len(self.words):
                self.show_results()
                self.disable_interaction()  # 禁用进一步的交互

    def disable_interaction(self):
        self.words_list.setEnabled(False)
        self.meanings_list.setEnabled(False)
    def update_list_status(self):
        for i in range(self.words_list.count()):
            word_item = self.words_list.item(i)
            word = word_item.text()
            if word in self.matched_pairs:
                word_item.setBackground(QBrush(QColor('lightgrey')))
                word_item.setFlags(word_item.flags() & ~Qt.ItemIsEnabled)

        # 这里我们清除之前的背景色设置，以便重新标记已匹配的项
        for i in range(self.meanings_list.count()):
            self.meanings_list.item(i).setBackground(QBrush(QColor('white')))

        for word, match_info in self.matched_pairs.items():
            selected_meaning = match_info['selected_meaning']
            for i in range(self.meanings_list.count()):
                meaning_item = self.meanings_list.item(i)
                if meaning_item.text() == selected_meaning:
                    color = 'lightgreen' if match_info['is_correct'] else 'pink'
                    meaning_item.setBackground(QBrush(QColor(color)))
                    meaning_item.setFlags(meaning_item.flags() & ~Qt.ItemIsEnabled)
                    break  # 找到匹配项后就不需要继续查找

    def show_results(self):
        correct_count = 0
        results_text = "<b>Results:</b><br>"

        for i in range(self.words_list.count()):
            word_item = self.words_list.item(i)
            word = word_item.text()

            if word in self.matched_pairs:
                selected_meaning = self.matched_pairs[word]['selected_meaning']
                is_correct = self.matched_pairs[word]['is_correct']
                # 此处我们获取正确的英文和中文解释
                correct_english, correct_chinese = self.correct_pairs[word]

                # 根据是否正确选择了解释来设置结果颜色
                color = 'green' if is_correct else 'red'
                results_text += f"<span style='color: {color};'>{word}</span> -> {correct_english}<br>"
                results_text += f"中文解释: {correct_chinese}<br><br>"

                correct_count += is_correct
            else:
                # 如果单词没有被选择过，也显示正确的解释
                correct_english, correct_chinese = self.correct_pairs[word]
                results_text += f"{word} -> {correct_english}<br>"
                results_text += f"中文解释: {correct_chinese}<br><br>"

        results_text += f"You got {correct_count} correct out of {len(self.words_list)}."
        self.status_label.setText(results_text)
    def disable_interaction(self):
        # 禁用单词列表和解释列表的进一步交互
        self.words_list.setEnabled(False)
        self.meanings_list.setEnabled(False)


def main():
    app = QApplication(sys.argv)
    file_path = '1.txt'  # Replace with your actual file path
    game = WordMatching(file_path)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
