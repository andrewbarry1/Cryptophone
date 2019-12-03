from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
import clib # Cryptophone library
import time

class SendMessageScreen:
    def __init__(self, container, who=None):
        self.container = container
        self.who = who
        self.entry = 0

    def draw(self, window):
        self.w_label = QLabel('Name/Phone Number:')
        self.who_in = QLineEdit()
        self.m_label = QLabel('Message:')
        self.message = QTextEdit()

        window.grid.addWidget(self.w_label, 0, 0)
        window.grid.addWidget(self.who_in, 1, 0)
        window.grid.addWidget(self.m_label, 2, 0)
        window.grid.addWidget(self.message, 3, 0)

        if self.who is not None:
            self.who_in.setText(self.who)
            self.message.setFocus()
            self.entry = 1
        else:
            self.who_in.setFocus()
        
    def input(self, window, key):
        if key == Qt.Key_Enter or key == Qt.Key_Return:
            if self.entry == 0 and len(self.who_in.text()) > 0:
                self.message.setFocus()
                self.entry = 1
            elif len(self.message.toPlainText()) > 0:
                to_u = self.who_in.text()
                msg = self.message.toPlainText()
                clib.send_message(self.container.Crypto, self.container.dev_id, self.container.pn, to_u, msg)
                window.setScreen(MainScreen(self.container))
        elif key == Qt.Key_Escape:
            window.setScreen(MainScreen(self.container))

    def clear(self, window):
        self.w_label.deleteLater()
        self.who_in.deleteLater()
        self.m_label.deleteLater()
        self.message.deleteLater()


class AddContactScreen:
    def __init__(self, container):
        self.container = container
        self.entry = 0

    def draw(self, window):
        self.o_label = QLabel('Name:')
        self.t_label = QLabel('Phone Number:')

        self.name = QLineEdit()
        self.pn = QLineEdit()
        
        window.grid.addWidget(self.o_label, 0, 0)
        window.grid.addWidget(self.name, 1, 0)
        window.grid.addWidget(self.t_label, 2, 0)
        window.grid.addWidget(self.pn, 3, 0)

        self.name.setFocus()

    def input(self, window, key):
        if key == Qt.Key_Enter or key == Qt.Key_Return:
            if self.entry == 0:
                self.pn.setFocus()
                self.entry += 1
            else:
                clib.add_contact(self.container.Crypto, self.name.text(), self.pn.text())
                window.setScreen(MainScreen(self.container))
        elif key == Qt.Key_Escape:
            window.setScreen(MainScreen(self.container))


    def clear(self, window):
        self.o_label.deleteLater()
        self.t_label.deleteLater()
        self.name.deleteLater()
        self.pn.deleteLater()


class PasswordCreateScreen:
    def __init__(self, container, first_run):
        self.container = container
        self.entry = 0
        self.first_run = first_run

    def draw(self, window):
        self.o_label = QLabel('New password:')
        self.t_label = QLabel('Enter it again:')

        self.pw = QLineEdit()
        self.pw.setEchoMode(QLineEdit.Password)

        self.pwt = QLineEdit()
        self.pwt.setEchoMode(QLineEdit.Password)
        
        window.grid.addWidget(self.o_label, 0, 0)
        window.grid.addWidget(self.pw, 1, 0)
        window.grid.addWidget(self.t_label, 2, 0)
        window.grid.addWidget(self.pwt, 3, 0)

        self.pw.setFocus()

    def input(self, window, key):
        if key == Qt.Key_Enter or key == Qt.Key_Return:
            if self.entry == 0:
                self.pwt.setFocus()
                self.entry += 1
            elif self.pw.text() == self.pwt.text():
                prep = clib.prep_pass(self.pw.text())
                if self.first_run:
                    clib.first_run(prep)
                    window.setScreen(LockScreen())
                else:
                    clib.change_local_pw(self.container.Crypto, prep)
                    window.setScreen(MainScreen(self.container))
            else:
                self.o_label.setText('New password: (Did not match)')
                self.pw.setFocus()
                self.pw.setText('')
                self.pwt.setText('')
                self.entry = 0
        elif key == Qt.Key_Escape and not self.first_run:
            window.setScreen(MainScreen(self.container))


    def clear(self, window):
        self.o_label.deleteLater()
        self.t_label.deleteLater()
        self.pw.deleteLater()
        self.pwt.deleteLater()


class KeyRegenScreen:
    def __init__(self, container):
        self.container = container

    def draw(self, window):
        self.warning = QTextEdit()
        self.warning.setText('<b>WARNING</b><br/><br/>This will delete all messages you have received. Press ENTER to continue, or Escape to back out.')
        window.grid.addWidget(self.warning, 0, 0)

    def input(self, window, key):
        if key == Qt.Key_Enter or key == Qt.Key_Return:
            clib.regen_keys(Crypto)
            window.setScreen(MainScreen(self.container))
        elif key == Qt.Key_Escape:
            window.setScreen(MainScreen(self.container))

    def clear(self, window):
        self.warning.deleteLater()

class SecurityMenuScreen:
    def __init__(self, container):
        self.container = container

    def draw(self, window):
        self.k_label = QLabel('(1) Regenerate Keys')
        self.p_label = QLabel('(2) Change Local Password')
        self.b_label = QLabel('(3) Back')
        window.grid.addWidget(self.k_label, 0, 0)
        window.grid.addWidget(self.p_label, 1, 0)
        window.grid.addWidget(self.b_label, 2, 0)

    def input(self, window, key):
        if key == Qt.Key_1:
            window.setScreen(KeyRegenScreen(self.container))
        elif key == Qt.Key_2:
            window.setScreen(PasswordCreateScreen(self.container))
        elif key == Qt.Key_3 or key == Qt.Key_Escape:
            window.setScreen(MainScreen(self.container))

    def clear(self, window):
        self.k_label.deleteLater()
        self.p_label.deleteLater()
        self.b_label.deleteLater()


class ConversationScreen:
    def __init__(self, container, from_pn):
        self.container = container
        self.from_pn = from_pn
        self.messages = clib.get_threaded_conversation(container.Crypto, container.dev_id, container.pn, from_pn)

    def draw(self, window):
        self.te = QTextEdit()
        convo = ''
        for msg in self.messages:
            ts_format = time.strftime('%d/%m/%y %I:%M%p', time.gmtime(int(msg[0])))
            convo += ts_format
            if msg[1] == 0:
                convo += ' (You)'
            convo += '\n' + msg[2] + '\n\n'
        convo = convo[:-2]
        self.te.setText(convo)
        self.te.setReadOnly(True)
        self.te.moveCursor(QTextCursor.End)
        window.grid.addWidget(self.te, 0, 0) # TODO how to get focus for scrolling


    def input(self, window, key):
        if key == Qt.Key_Escape:
            window.setScreen(ConversationListScreen(self.container))
        elif key == Qt.Key_Enter or key == Qt.Key_Return:
            window.setScreen(SendMessageScreen(self.container, self.from_pn))

    def clear(self, window):
        self.te.deleteLater()
        
        

class ConversationListScreen:
    def __init__(self, container):
        self.container = container
        self.convo_list = clib.get_conversation_list(container.Crypto)
    
    def draw(self, window):
        self.te = QListWidget()
        l = ['< Back'] + self.convo_list
        for c in l:
            self.te.addItem(c)
        window.grid.addWidget(self.te, 0, 0)
        self.te.setCurrentRow(0)
        self.te.setFocus()
    
    def input(self, window, key):
        if key == Qt.Key_Enter or key == Qt.Key_Return:
            selected = self.te.selectedItems()[0]
            if self.te.row(selected) == 0: # go back
                window.setScreen(MainScreen(self.container))
            else:
                selected = selected.text()
                window.setScreen(ConversationScreen(self.container, selected))
        elif key == Qt.Key_Escape:
            window.setScreen(MainScreen(self.container))

    def clear(self, window):
        self.te.deleteLater()


class LockScreen:
    def draw(self, window):
        self.l = QLabel('Enter Password')
        self.pw = QLineEdit()
        self.pw.setEchoMode(QLineEdit.Password)
        window.grid.addWidget(self.l, 0, 0)
        window.grid.addWidget(self.pw, 1, 0)
        self.pw.setFocus()

    def input(self, window, key):
        if key == Qt.Key_Enter or key == Qt.Key_Return:
            pw_text = self.pw.text()
            if clib.check_password(pw_text):
                container = clib.gen_crypto(clib.prep_pass(pw_text))
                window.setScreen(MainScreen(container))
            else:
                self.l.setText('Invalid password.')
                self.pw.setText('')


    def clear(self, window):
        self.l.deleteLater()
        self.pw.deleteLater()

    
class MainScreen:
    def __init__(self, container):
        self.container = container
    
    def draw(self, window):
        self.c_label = QLabel('(1) Conversations')
        window.grid.addWidget(self.c_label, 0, 0)

        self.n_label = QLabel('(2) New Message')
        window.grid.addWidget(self.n_label, 1, 0)

        self.s_label = QLabel('(3) Security Settings')
        window.grid.addWidget(self.s_label, 2, 0)

        self.ct_label = QLabel('(4) Contacts')
        window.grid.addWidget(self.ct_label, 3, 0)

        self.l_label = QLabel('(5) Lock')
        window.grid.addWidget(self.l_label, 4, 0)

    def input(self, window, key):
        if key == Qt.Key_1:
            window.setScreen(ConversationListScreen(self.container))
        elif key == Qt.Key_2:
            window.setScreen(SendMessageScreen(self.container))
        elif key == Qt.Key_3:
            window.setScreen(SecurityMenuScreen(self.container))
        elif key == Qt.Key_4:
            window.setScreen(AddContactScreen(self.container))
        elif key == Qt.Key_5 or key == Qt.Key_Escape:
            window.setScreen(LockScreen())

    def clear(self, window):
        self.c_label.deleteLater()
        self.n_label.deleteLater()
        self.s_label.deleteLater()
        self.ct_label.deleteLater()
        self.l_label.deleteLater()

            
class Application(QMainWindow):

    def __init__(self):
        super().__init__()
        self.screen = None
        self.initUI()
        if clib.needs_first_run():
            self.setScreen(PasswordCreateScreen(None, True))
        else:
            self.setScreen(LockScreen())

    def initUI(self):
        self.central = QWidget()
        self.grid = QGridLayout()
        self.central.setLayout(self.grid)
        self.setCentralWidget(self.central)
        
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Cryptophone')
        self.show()

    def keyPressEvent(self, e):
        if self.screen is not None:
            self.screen.input(self, e.key())

    def setScreen(self, new_screen):
        if self.screen is not None:
            self.screen.clear(self)
        self.screen = new_screen
        new_screen.draw(self)


if __name__ == '__main__':
    app = QApplication([])
    ex = Application()
    app.exec_()
