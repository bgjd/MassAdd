from aqt import mw, deckchooser, notetypechooser
from anki.models import NotetypeId
from anki.notes import Note
from aqt.utils import showInfo
from aqt.qt import *


class MassAddWindow(QDialog):
    def __init__(self) -> None:
        QDialog.__init__(self, None, Qt.Window)
        self.deck_widget = None
        self.model_widget = None
        self.text_edit = None
        self.processor_widget = None
        self.processor_layout = None
        self.processor_label = None
        self.processor_text = None
        self.processor_button = None
        self.submit_button = None
        self.deck_chooser = None
        self.model_chooser = None

    def setup_ui(self):
        layout = QVBoxLayout()
        self.deck_widget = QWidget(mw)
        self.model_widget = QWidget(mw)
        self.text_edit = QTextEdit(mw)
        self.submit_button = QPushButton(mw)
        self.deck_chooser = deckchooser.DeckChooser(mw, self.deck_widget)
        defaults = mw.col.defaults_for_adding(
                       current_review_card=mw.reviewer.card
        )
        self.model_chooser = notetypechooser.NotetypeChooser(mw=mw, widget=self.model_widget,
                                                             starting_notetype_id=NotetypeId(defaults.notetype_id))


        self.processor_widget = QWidget(mw)
        self.processor_layout = QHBoxLayout(mw)
        self.processor_label = QLabel("Character to split on:")
        self.processor_text = QLineEdit(mw)
        self.processor_text.setMaxLength(1)
        self.processor_text.setFixedWidth(60)
        self.processor_button = QPushButton(mw)
        self.processor_button.setText("Split")
        self.processor_button.clicked.connect(self.split_text)
        self.processor_layout.addWidget(self.processor_label)
        self.processor_layout.addWidget(self.processor_text)
        self.processor_layout.addWidget(self.processor_button)
        self.processor_widget.setLayout(self.processor_layout)

        self.submit_button.setText("Add")
        self.submit_button.clicked.connect(self.add_current_sentences)

        layout.addWidget(self.model_widget)
        layout.addWidget(self.deck_widget)
        layout.addWidget(self.processor_widget)
        layout.addWidget(self.text_edit)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)
        self.setWindowTitle("MassAdd")
        self.setMinimumHeight(300)
        self.setMinimumWidth(400)

    def show_window(self):
        if self.submit_button is None:
            self.setup_ui()
        self.text_edit.setText("")
        self.show()

    def split_text(self):
        text = self.text_edit.toPlainText()
        split_marker = self.processor_text.text()

        new_text = (split_marker + "\n").join(text.split(split_marker))
        self.text_edit.setText(new_text)
        self.processor_text.clear()

    def add_current_sentences(self):
        deck_id = self.deck_chooser.selectedId()
        model_id = self.model_chooser.selected_notetype_id
        m = mw.col.models.get(model_id)

        # Use the first field of note as this is required to be non-blank by anki
        field = m["flds"][0]["name"]

        sentences = self.text_edit.toPlainText().split("\n")

        for s in sentences:
            note = Note(mw.col, m)
            note[field] = s.strip()
            note.model()["did"] = deck_id
            mw.col.addNote(note)

        showInfo('Done')


MAWindow = MassAddWindow()

action = QAction("MassAdd", mw)
action.triggered.connect(MAWindow.show_window)
mw.form.menuTools.addAction(action)
