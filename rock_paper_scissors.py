import cv2
import random
import mediapipe as mp
import tkinter as tk
from tkinter import messagebox
from threading import Thread
import time

# Initialize global variables
user_score = 0
computer_score = 0
choices = ["rock", "paper", "scissors"]
round_number = 1

# Function to determine winner
def determine_winner(user_choice, computer_choice):
    global user_score, computer_score
    if user_choice == computer_choice:
        return "It's a tie!"
    elif (user_choice == "rock" and computer_choice == "scissors") or \
         (user_choice == "paper" and computer_choice == "rock") or \
         (user_choice == "scissors" and computer_choice == "paper"):
        user_score += 1
        return "You win!"
    else:
        computer_score += 1
        return "Computer wins!"

# Function to detect hand gesture using MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

def detect_hand_gesture(frame):
    with mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5) as hands:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                landmarks = hand_landmarks.landmark
                try:
                    # Get y-coordinates of finger tips and middle knuckles
                    thumb_tip = landmarks[4].y
                    index_tip = landmarks[8].y
                    middle_tip = landmarks[12].y
                    ring_tip = landmarks[16].y
                    pinky_tip = landmarks[20].y

                    index_mcp = landmarks[5].y
                    middle_mcp = landmarks[9].y
                    ring_mcp = landmarks[13].y
                    pinky_mcp = landmarks[17].y

                    # Detect "rock": all fingers (except thumb) are curled
                    if index_tip > index_mcp and middle_tip > middle_mcp and ring_tip > ring_mcp and pinky_tip > pinky_mcp:
                        return "rock", frame

                    # Detect "paper": all fingers are extended
                    elif index_tip < index_mcp and middle_tip < middle_mcp and ring_tip < ring_mcp and pinky_tip < pinky_mcp:
                        return "paper", frame

                    # Detect "scissors": index and middle fingers extended, ring and pinky curled
                    elif index_tip < index_mcp and middle_tip < middle_mcp and ring_tip > ring_mcp and pinky_tip > pinky_mcp:
                        return "scissors", frame
                except IndexError:
                    # Handle cases where landmarks are not fully detected
                    return None, frame
        return None, frame

# Function to start the camera and play the game
def play_game():
    global user_score, computer_score, round_number

    cap = cv2.VideoCapture(0)
    countdown = 3

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Show countdown on the frame
        if countdown > 0:
            cv2.putText(frame, str(countdown), (250, 250), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.imshow("Rock Paper Scissors", frame)
            cv2.waitKey(1000)  # Wait 1 second
            countdown -= 1
        else:
            user_choice, annotated_frame = detect_hand_gesture(frame)
            if user_choice:
                computer_choice = random.choice(choices)
                result = determine_winner(user_choice, computer_choice)

                # Display result
                cv2.putText(annotated_frame, f"Round {round_number}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(annotated_frame, f"You: {user_choice}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                cv2.putText(annotated_frame, f"Computer: {computer_choice}", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                cv2.putText(annotated_frame, result, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(annotated_frame, f"Score: You {user_score} - {computer_score} Computer", (50, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

                cv2.imshow("Rock Paper Scissors", annotated_frame)
                cv2.waitKey(3000)  # Wait for 3 seconds

                # Check if game over
                if round_number >= 3:
                    if user_score != computer_score:
                        final_result = "You win the game!" if user_score > computer_score else "Computer wins the game!"
                        cv2.putText(annotated_frame, final_result, (50, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                        cv2.imshow("Rock Paper Scissors", annotated_frame)
                        cv2.waitKey(3000)

                        # Ask to play again
                        cap.release()
                        cv2.destroyAllWindows()
                        play_again_prompt()
                        return
                    else:
                        cv2.putText(annotated_frame, "It's a tie! One more round!", (50, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                        cv2.imshow("Rock Paper Scissors", annotated_frame)
                        cv2.waitKey(3000)

                # Increment round and reset countdown
                round_number += 1
                countdown = 3
            else:
                cv2.putText(frame, "Show your hand!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.imshow("Rock Paper Scissors", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Function to prompt for playing again
def play_again_prompt():
    global user_score, computer_score, round_number

    def on_yes():
        global user_score, computer_score, round_number
        user_score = 0
        computer_score = 0
        round_number = 1
        root.destroy()
        play_game()

    def on_no():
        root.destroy()

    root = tk.Tk()
    root.title("Play Again?")

    label = tk.Label(root, text=f"Final Score: You {user_score} - {computer_score} Computer\nDo you want to play again?", font=("Arial", 14))
    label.pack(pady=20)

    yes_button = tk.Button(root, text="Yes", font=("Arial", 12), command=on_yes)
    yes_button.pack(side="left", padx=20, pady=20)

    no_button = tk.Button(root, text="No", font=("Arial", 12), command=on_no)
    no_button.pack(side="right", padx=20, pady=20)

    root.mainloop()

# GUI to start the game
def start_gui():
    def on_start():
        root.destroy()
        play_game()

    root = tk.Tk()
    root.title("Rock Paper Scissors")
    
    label = tk.Label(root, text="Ready to play Rock Paper Scissors?", font=("Arial", 16))
    label.pack(pady=20)

    start_button = tk.Button(root, text="Start", font=("Arial", 14), command=on_start)
    start_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    start_gui()
