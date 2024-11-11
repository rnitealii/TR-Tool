import sys
import speech_recognition as sr
import threading
import time
import keyboard  # For simulating keyboard inputs
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class SpeechRecognitionThread(QThread):
    update_text_signal = pyqtSignal(str)
    status_signal = pyqtSignal(str)

    def __init__(self, language_code='ur-PK'):
        super().__init__()
        self.language_code = language_code
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        self.listening = False
        self.stop_event = threading.Event()
        self.transcribed_text = ""

    def run(self):
        while not self.stop_event.is_set():
            with self.mic as source:
                self.status_signal.emit("Listening...")
                print("Listening...")  # Debugging print to check if it's listening

                # Adjust for ambient noise for better accuracy
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)

                try:
                    # Listen continuously
                    print("Ready to listen for speech")  # Debugging print to track progress
                    audio = self.recognizer.listen(source, phrase_time_limit=15)

                    print("Audio received, processing...")  # Debugging print
                    # Recognize speech and process it
                    text = self.recognizer.recognize_google(audio, language=self.language_code)
                    print(f"Recognized: {text}")  # Debugging print for recognized text

                    if text:
                        self.transcribed_text += text + " "
                        self.update_text_signal.emit(self.transcribed_text)
                    else:
                        self.status_signal.emit("No speech detected.")
                except sr.UnknownValueError:
                    self.status_signal.emit("Could not understand the audio.")
                    print("Could not understand the audio.")  # Debugging print
                except sr.RequestError:
                    self.status_signal.emit("Service unavailable. Try again later.")
                    print("Service unavailable.")  # Debugging print
                except Exception as e:
                    print(f"Error: {e}")
                    self.status_signal.emit("Error occurred, please try again.")
            
            time.sleep(0.5)

    def stop_listening(self):
        """Stop the listening thread"""
        if self.recognition_thread.isRunning():
            self.recognition_thread.stop_listening()
            self.update_status("Listening stopped.")
        else:
            self.update_status("No active listening session.")


    def reset(self):
        self.transcribed_text = ""


class SpeechRecognitionApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = QWidget()
        self.window.setWindowTitle('Speech Recognition Tool')

        # Create layout
        self.layout = QVBoxLayout()

        # Add Listening indicator
        self.indicator_label = QLabel("Click Play to start listening")
        self.indicator_label.setStyleSheet("font-size: 18px; padding: 10px; background-color: lightgreen;")
        self.indicator_label.setAlignment(Qt.AlignCenter)

        # Create Play Button
        self.play_button = QPushButton('Start Listening')
        self.play_button.setStyleSheet("background-color: green; color: white; font-size: 14px; padding: 10px;")
        self.play_button.clicked.connect(self.start_listening)

        # Create Stop Button
        self.stop_button = QPushButton('Stop Listening')
        self.stop_button.setStyleSheet("background-color: red; color: white; font-size: 14px; padding: 10px;")
        self.stop_button.clicked.connect(self.stop_listening)

        # Initialize the SpeechRecognitionThread class
        self.recognition_thread = SpeechRecognitionThread(language_code='ur-PK')
        self.recognition_thread.update_text_signal.connect(self.update_text)
        self.recognition_thread.status_signal.connect(self.update_status)

        # Add elements to layout
        self.layout.addWidget(self.indicator_label)
        self.layout.addWidget(self.play_button)
        self.layout.addWidget(self.stop_button)

        # Set layout and window size
        self.window.setLayout(self.layout)
        self.window.setStyleSheet("background-color: white;")  # Background color for clean focus
        self.window.resize(400, 200)

    def update_text(self, text):
        """Update the text and simulate typing"""
        # Clear previous text and start typing the new one
        for char in text:
            keyboard.write(char)
            time.sleep(0.05)  # Adjust speed for typing effect

    def update_status(self, status):
        """Update the indicator label with status"""
        self.indicator_label.setText(status)

    def start_listening(self):
        """Start the listening thread"""
        self.recognition_thread.reset()
        self.recognition_thread.stop_event.clear()
        self.recognition_thread.start()
        self.update_status("Listening started...")

    def stop_listening(self):
        """Stop the listening thread"""
        self.recognition_thread.stop_listening()
        self.update_status("Listening stopped.")

    def run(self):
        """Run the application"""
        self.window.show()
        sys.exit(self.app.exec_())


if __name__ == '__main__':
    app = SpeechRecognitionApp()
    app.run()
