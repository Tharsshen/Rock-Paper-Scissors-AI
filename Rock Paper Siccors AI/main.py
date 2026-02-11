import random
import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import time
import pygame
from tkinter import *
from tkvideo import tkvideo

# Initializee pygame mixer for music and soundssss 
pygame.mixer.init()

# Load sound effectss
sound_player_win = pygame.mixer.Sound("Resources/player_win.mp3")
sound_ai_win = pygame.mixer.Sound("Resources/ai_win.mp3")
sound_tournament_end = pygame.mixer.Sound("Resources/tournament_end.mp3")
sound_select_mode = pygame.mixer.Sound("Resources/select_mode.mp3")  # New sound for mode selection
sound_draw = pygame.mixer.Sound("Resources/draw.mp3")  # New sound for draw

# Initialize webcam and settingss
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# Detect Hands
detector = HandDetector(maxHands=1)

timer = 0
stateResult = False
startGame = False
scores = [0, 0]  # [AI, Player]
randomNumber = 1
winnerText = ""
gameMode = None  # Stores the selected game mode
roundNumber = 1  # To keep track of rounds
tournamentWinnerText = ""  # Text to display who won the tournament

# Variables for delayed video playback
tournamentEndTime = None
videoToPlay = None

# Define button coordinates
buttons = {
    "easy": (50, 660, 200, 710),
    "medium": (250, 660, 400, 710),
    "hard": (450, 660, 600, 710),
}

# AI Behavior Function
def get_ai_move(player_move=None, mode="medium", round_num=1):
    if mode == "easy":
        # Predefined sequence for easy difficulty
        predefined_moves = [3, 1, 2, 3, 1]  # Scissors, Rock, Paper, Scissors, Rock
        return predefined_moves[(round_num - 1) % len(predefined_moves)]  # Cycle through predefined moves
    elif mode == "medium":
        return random.randint(1, 3)  # Fair match
    elif mode == "hard":
        if player_move == 1:
            return 2  # Rock -> Paper
        elif player_move == 2:
            return 3  # Paper -> Scissors
        elif player_move == 3:
            return 1  # Scissors -> Rock
    return random.randint(1, 3)

# Mouse event callback
def mouse_click(event, x, y, flags, param):
    global gameMode, startGame, initialTime, stateResult, winnerText
    if event == cv2.EVENT_LBUTTONDOWN:
        for mode, (x1, y1, x2, y2) in buttons.items():
            if x1 <= x <= x2 and y1 <= y <= y2:
                if mode in ["easy", "medium", "hard"]:
                    gameMode = mode
                    startGame = True
                    initialTime = time.time()
                    stateResult = False
                    winnerText = ""
                    pygame.mixer.Sound.play(sound_select_mode)  # Play mode selection sound
                    print(f"Selected Mode: {mode.capitalize()}")

cv2.namedWindow("BG")
cv2.setMouseCallback("BG", mouse_click)

# Main Loop
while True:
    imgBG = cv2.imread("Resources/BG.png")
    success, img = cap.read()

    imgScaled = cv2.resize(img, (0, 0), None, 0.875, 0.875)
    imgScaled = imgScaled[:, 80:480]

    # Find Hands
    hands, img = detector.findHands(imgScaled)

    if startGame:
        tournamentWinnerText = ""  # Reset the tournament winner text when a new game starts
        if not stateResult:
            timer = time.time() - initialTime
            cv2.putText(imgBG, str(int(timer)), (605, 435), cv2.FONT_HERSHEY_PLAIN, 6, (255, 0, 255), 4)

            if timer > 3:
                stateResult = True
                timer = 0
                if gameMode == "hard" and hands:
                    hand = hands[0]
                    fingers = detector.fingersUp(hand)
                    if fingers == [0, 0, 0, 0, 0]:
                        playerMove = 1  # Rock
                    elif fingers == [1, 1, 1, 1, 1]:
                        playerMove = 2  # Paper
                    elif fingers == [0, 1, 1, 0, 0]:
                        playerMove = 3  # Scissors
                    else:
                        playerMove = None
                    randomNumber = get_ai_move(player_move=playerMove, mode=gameMode, round_num=roundNumber)
                else:
                    randomNumber = get_ai_move(mode=gameMode, round_num=roundNumber)
                imgAI = cv2.imread(f'Resources/{randomNumber}.png', cv2.IMREAD_UNCHANGED)

        if stateResult:
            playerMove = None
            if hands:  # Check if a hand is detected
                hand = hands[0]
                fingers = detector.fingersUp(hand)
                if fingers == [0, 0, 0, 0, 0]:
                    playerMove = 1  # Rock
                elif fingers == [1, 1, 1, 1, 1]:
                    playerMove = 2  # Paper
                elif fingers == [0, 1, 1, 0, 0]:
                    playerMove = 3  # Scissors

            if playerMove is None:  # No move made or invalid move
                scores[0] += 1
                winnerText = "No move! AI wins this round"
                sound_ai_win.play()  # Play AI win sound
            else:
                if (playerMove == 1 and randomNumber == 3) or \
                        (playerMove == 2 and randomNumber == 1) or \
                        (playerMove == 3 and randomNumber == 2):
                    scores[1] += 1
                    winnerText = "Player wins this round"
                    sound_player_win.play()  # Play player win sound
                elif (playerMove == 3 and randomNumber == 1) or \
                        (playerMove == 1 and randomNumber == 2) or \
                        (playerMove == 2 and randomNumber == 3):
                    scores[0] += 1
                    winnerText = "AI wins this round"
                    sound_ai_win.play()  # Play AI win sound
                else:
                    winnerText = "It's a draw"
                    sound_draw.play()  # Play draw sound

            roundNumber += 1
            startGame = False

            # Check for tournament winner after 5 rounds
            if roundNumber > 5:
                if scores[1] > scores[0]:  # Player has more points
                    tournamentWinnerText = "Player wins the tournament!"
                    videoToPlay = "player"
                elif scores[0] > scores[1]:  # AI has more points
                    tournamentWinnerText = "AI wins the tournament!"
                    videoToPlay = "ai"
                else:  # Tie
                    tournamentWinnerText = "The tournament is a draw!"
                    videoToPlay = "draw"
                tournamentEndTime = time.time()  # Set the end time
                sound_tournament_end.play()  # Play tournament end sound
                roundNumber = 1  # Reset for the next tournament
                scores = [0, 0]  # Reset scores

    # Draw buttons
    for mode, (x1, y1, x2, y2) in buttons.items():
        color = (0, 255, 0) if mode == "easy" else \
                (0, 255, 255) if mode == "medium" else (0, 0, 255)
        thickness = -1 if gameMode == mode else 2
        cv2.rectangle(imgBG, (x1, y1), (x2, y2), color, thickness)
        cv2.putText(imgBG, mode.capitalize(), (x1 + 10, y1 + 30), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)

    imgBG[232:652, 793:1193] = imgScaled

    # Show AI's move and winner text
    if stateResult or tournamentWinnerText:
        imgBG = cvzone.overlayPNG(imgBG, imgAI, (149, 310))
        if tournamentWinnerText:
            cv2.putText(imgBG, tournamentWinnerText, (250, 350), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 5)
        else:
            cv2.putText(imgBG, winnerText, (380, 480), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 4)

    # Display scores and round number
    cv2.putText(imgBG, f"Round: {roundNumber - 1}", (570, 185), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 4)
    cv2.putText(imgBG, str(scores[0]), (410, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)
    cv2.putText(imgBG, str(scores[1]), (1112, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)

    # Handle video playback after delay
    if tournamentEndTime is not None:
        if time.time() - tournamentEndTime > 2:  # 2-second delay
            if videoToPlay == "player":
                w = Tk()
                w.title("Congratulations!")
                lblVideo = Label(w)
                lblVideo.pack()
                video_link = "Resources/peaceful.mp4"
                player = tkvideo(video_link, lblVideo, loop=0, size=(700, 500))
                player.play()
                w.mainloop()
            elif videoToPlay == "ai":
                w = Tk()
                w.title("Game Over")
                lblVideo = Label(w)
                lblVideo.pack()
                video_link_lose = "Resources/world_end.mp4"
                player = tkvideo(video_link_lose, lblVideo, loop=0, size=(700, 500))
                player.play()
                w.mainloop()
            elif videoToPlay == "draw":
                w = Tk()
                w.title("It's a Draw!")
                lblVideo = Label(w)
                lblVideo.pack()
                video_link_draw = "Resources/draw.mp4"
                player = tkvideo(video_link_draw, lblVideo, loop=0, size=(700, 500))
                player.play()
                w.mainloop()
            tournamentEndTime = None
            videoToPlay = None
            tournamentWinnerText = ""  # Reset the tournament winner text

    cv2.imshow("BG", imgBG)
    key = cv2.waitKey(1)

    if key == ord('q'):
        break

#Have FUN!!!

cap.release()
cv2.destroyAllWindows()
