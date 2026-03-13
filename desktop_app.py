import FreeSimpleGUI as fsg

class MyApp:
    def __init__(self):
        self.window = fsg.Window('My Desktop App')

    def run(self):
        while True:
            event, values = self.window.read()  
            if event in (fsg.WIN_CLOSED, 'Exit'):
                break
            self.window['-OUTPUT-'].update(f'You entered: {values[0]}')
        self.window.close()

if __name__ == '__main__':
    app = MyApp()
    app.run()