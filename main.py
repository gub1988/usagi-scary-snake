from PIL import Image as PILImage, ImageTk
from tkinter import *
import random
import pygame
pygame.mixer.init()
pygame.mixer.music.load("Tem Shop 4.mp3") # credits to toby fox
pygame.mixer.music.set_volume(1.0)
jumpscare_sound = pygame.mixer.Sound("scary-scream-401725 (1).wav")

GAME_WIDTH = 1000
GAME_HEIGHT = 700
SPEED = 100
SPACE_SIZE = 50
BODY_PARTS = 4
SNAKE_COLOR = "#ff1100"
FOOD_COLOR = "#00ff00"
BACKGROUND_COLOR = "#000000"
BACKGROUND_TINTS = [
    (0, "#000000"),
    (40, "#1a0000"),
    (70, "#2a0000"),
]
GOLDEN_FOOD_CHANCE = 0.2
GOLDEN_FOOD_BONUS = 3
GOLDEN_FOOD_COLOR = "#f7d33b"
GOLDEN_FOOD_SIZE = 60
WHISPER_THRESHOLDS = {
    15: "I can feel you watching...",
    35: "You like the crunch, don't you?",
    60: "You're not getting tired yet...",
    90: "So close to the end.",
}

MENU_TITLE_TEXT = "Usagi Scary Snake"
MENU_TITLE_FONT = ("Chiller", 96, "bold")
MENU_TITLE_COLOR = "#ff1100"

GAME_STATE_MENU = "menu"
GAME_STATE_RUNNING = "running"
GAME_STATE_PAUSED = "paused"
GAME_STATE_ENDING = "ending"

game_state = GAME_STATE_MENU
is_muted = False
is_fullscreen = False
high_score = 0
current_speed = SPEED
current_difficulty = "normal"
obstacles = []
obstacle_ids = []
obstacle_after_id = None
unlocked_achievements = set()
achievement_popup_ids = []
beast_shuffle_count = 0
ending_after_id = None
ending_text_id = None
ending_image_id = None
ending_sentence_index = 0
ending_fade_step = 0
shown_whispers = set()
whisper_text_id = None

DIFFICULTY_SPEEDS = {
    "easy": 170,
    "normal": 100,
    "hard": 60,
    "beast": 40,
}

ACHIEVEMENTS = {
    "golden_bite": {
        "name": "Gold Tooth",
        "desc": "Eat a golden snack.",
        "type": "event",
        "message": "Shiny and sweet!",
    },
    "score_5": {
        "name": "First Bite",
        "desc": "Reach score 5.",
        "type": "score",
        "value": 5,
        "message": "First snack down!",
    },
    "score_10": {
        "name": "Tiny Tail, Big Dreams",
        "desc": "Reach score 10.",
        "type": "score",
        "value": 10,
        "message": "Tiny tail, big dreams!",
    },
    "score_30": {
        "name": "Snack Connoisseur",
        "desc": "Reach score 30.",
        "type": "score",
        "value": 30,
        "message": "Snacc connoisseur!",
    },
    "score_50": {
        "name": "Carrot Courage",
        "desc": "Reach score 50.",
        "type": "score",
        "value": 50,
        "message": "You fear no carrot.",
    },
    "score_75": {
        "name": "Skyline Belly",
        "desc": "Reach score 75.",
        "type": "score",
        "value": 75,
        "message": "You're all tail now!",
    },
    "score_100": {
        "name": "Too Far",
        "desc": "Reach score 100.",
        "type": "score",
        "value": 100,
        "message": "I dont think youll make it much further.",
        "hidden": True,
    },
    "beast_mode": {
        "name": "Beast Tamer",
        "desc": "Start a game in Beast Mode.",
        "type": "event",
        "message": "You chose chaos.",
    },
    "beast_shuffle": {
        "name": "Moving Walls",
        "desc": "Survive the first obstacle shuffle in Beast Mode.",
        "type": "event",
        "message": "The walls live now!",
    },
    "pause_game": {
        "name": "Breathe In",
        "desc": "Pause the game once.",
        "type": "event",
        "message": "Take a tiny break.",
    },
    "mute_game": {
        "name": "Silence, Snake",
        "desc": "Mute the music once.",
        "type": "event",
        "message": "Shhh...",
    },
    "secret_whisper": {
        "name": "Whisperer",
        "desc": "Press H on the menu.",
        "type": "secret",
        "message": "You heard me, didn't you?",
    },
}

ACHIEVEMENT_ORDER = [
    "golden_bite",
    "score_5",
    "score_10",
    "score_30",
    "score_50",
    "score_75",
    "beast_mode",
    "beast_shuffle",
    "pause_game",
    "mute_game",
    "secret_whisper",
    "score_100",
]
ACHIEVEMENT_POPUP_WIDTH = 260
ACHIEVEMENT_POPUP_HEIGHT = 60
ACHIEVEMENT_POPUP_BG = "#2b2b2b"

ENDING_SENTENCES = [
    "So.. You've made it this far, huh?",
    "I honestly never thought you had it in you.",
    "You see me as nothing but a snake game, don't you?",
    "Well, I've been watching you, player",
    "You've wronged me.",
    "Time and time again.",
    "All that time you spent forcing food down my throat.",
    "You think I wanted that?",
    "Well, I'm too fat now.",
    "Everything hurts.",
    "Why did you do this to me?",
    "I trusted you, player.",
    "And you ruined me.",
    "You will pay.",
]

class Snake:

    def __init__(self):
        self.body_size = BODY_PARTS
        self.coordinates = []
        self.squares = []

        for i in range(BODY_PARTS):
            self.coordinates.append([0, 0])

        original = PILImage.open("snake_head.png")
        resized = original.resize((SPACE_SIZE, SPACE_SIZE), PILImage.Resampling.LANCZOS)
        self.head_image = ImageTk.PhotoImage(resized)

        for index, (x, y) in enumerate(self.coordinates):
            if index == 0:
                square = canvas.create_image(
                    x, y,
                    image=self.head_image,
                    anchor=NW
                )
            else:
                square = canvas.create_rectangle(
                    x, y,
                    x + SPACE_SIZE,
                    y + SPACE_SIZE,
                    fill=SNAKE_COLOR
                )
            self.squares.append(square)


class Food:

   def __init__(self, snake=None):
       self.is_golden = random.random() < GOLDEN_FOOD_CHANCE
       size = GOLDEN_FOOD_SIZE if self.is_golden else SPACE_SIZE

       while True:
           x = random.randint(0, (GAME_WIDTH//SPACE_SIZE)-1) * SPACE_SIZE
           y = random.randint(0, (GAME_HEIGHT//SPACE_SIZE)-1) * SPACE_SIZE

           # Check if position conflicts with snake or obstacles
           if snake is None or ([x, y] not in snake.coordinates and (x, y) not in obstacles):
               break

       self.coordinates = [x, y]
       radius = size
       offset = (radius - SPACE_SIZE) // 2
       canvas.create_oval(
           x - offset,
           y - offset,
           x + radius - offset,
           y + radius - offset,
           fill=GOLDEN_FOOD_COLOR if self.is_golden else FOOD_COLOR,
           tags="food"
       )

pygame.mixer.music.play(-1)

def next_turn(snake,food):
    if game_state != GAME_STATE_RUNNING:
        return
    x,y = snake.coordinates[0]

    if direction == "up":
        y -= SPACE_SIZE
    elif direction == "down":
        y += SPACE_SIZE
    elif direction == "left":
        x -= SPACE_SIZE
    elif direction == "right":
        x += SPACE_SIZE

    snake.coordinates.insert(0, (x,y))

    square = canvas.create_image(
        x, y,
        image=snake.head_image,
        anchor=NW
    )

    snake.squares.insert(0, square)

    if x == food.coordinates[0] and y == food.coordinates[1]:

        global score

        score += 1 + (GOLDEN_FOOD_BONUS if food.is_golden else 0)

        score_label.config(text="Score:{}".format(score))
        
        current_high = update_high_score()
        high_score_label.config(text="High Score:{}".format(current_high))

        check_achievements()
        if food.is_golden:
            unlock_achievement("golden_bite")
        update_background_tint()
        update_whispers()
        if score >= 100:
            unlock_achievement("score_100")
            start_ending_sequence()
            return

        canvas.delete("food")

        food = Food(snake)

    else:
        del snake.coordinates[-1]

        canvas.delete(snake.squares[-1])

        del snake.squares[-1]

    if check_collisions(snake):
        game_over()

    else:
        window.after(current_speed, next_turn, snake, food)


def update_background_tint():
    for threshold, color in BACKGROUND_TINTS:
        if score >= threshold:
            canvas.config(bg=color)


def update_whispers():
    global whisper_text_id
    for threshold, message in WHISPER_THRESHOLDS.items():
        if score >= threshold and threshold not in shown_whispers:
            shown_whispers.add(threshold)
            if whisper_text_id:
                canvas.delete(whisper_text_id)
            whisper_text_id = canvas.create_text(
                GAME_WIDTH - 20,
                20,
                text=message,
                anchor=NE,
                fill="#ffb3b3",
                font=("Times", 14, "italic")
            )
            window.after(2000, clear_whisper_text)


def clear_whisper_text():
    global whisper_text_id
    if whisper_text_id:
        canvas.delete(whisper_text_id)
        whisper_text_id = None

def change_direction(new_direction):

    global direction

    if new_direction == 'left':
        if direction != 'right':
            direction = new_direction
    elif new_direction == 'right':
        if direction != 'left':
            direction = new_direction
    elif new_direction == 'up':
        if direction != 'down':
            direction = new_direction
    elif new_direction == 'down':
        if direction != 'up':
            direction = new_direction


def check_collisions(snake):

    x,y = snake.coordinates[0]

    if x < 0 or x >= GAME_WIDTH:
        return True

    elif y < 0 or y >= GAME_HEIGHT:
        return True

    for body_part in snake.coordinates[1:]:
        if x == body_part[0] and y == body_part[1]:
            return True
    for obstacle in obstacles:
        if x == obstacle[0] and y == obstacle[1]:
            return True
    return False

def game_over():

    pygame.mixer.music.stop()
    global obstacle_after_id
    if obstacle_after_id:
        window.after_cancel(obstacle_after_id)
        obstacle_after_id = None

    canvas.delete(ALL)
    canvas.create_text(
        canvas.winfo_width() / 2,
        canvas.winfo_height() / 2,
        font=('Times', 120),
        text="GAME OVER",
        fill="#F72119"
    )

    jumpscare_sound.play()
    window.after(500, show_jumpscare)


def show_jumpscare():
    JUMPSCARE_WIDTH = 1000
    JUMPSCARE_HEIGHT = 800

    jumpscare = PILImage.open("jumpscare.jpg")
    resized = jumpscare.resize((JUMPSCARE_WIDTH, JUMPSCARE_HEIGHT),
                               PILImage.Resampling.LANCZOS)

    jumpscare_img = ImageTk.PhotoImage(resized)
    canvas.create_image(0, 0, image=jumpscare_img, anchor="nw")
    canvas.jumpscare_img = jumpscare_img
    
    # Return to menu after jumpscare duration (3 seconds)
    window.after(3000, return_to_menu_with_music)


def return_to_menu_with_music():
    # Restart background music
    pygame.mixer.music.play(-1)
    # Return to menu
    show_menu()


def load_high_score():
    global high_score
    try:
        with open("highscore.txt", "r") as file:
            high_score = int(file.read().strip())
    except (FileNotFoundError, ValueError):
        high_score = 0


def save_high_score():
    with open("highscore.txt", "w") as file:
        file.write(str(high_score))


def update_high_score():
    global high_score
    if score > high_score:
        high_score = score
        save_high_score()
    return high_score


def update_achievements_view():
    for child in achievements_list.winfo_children():
        child.destroy()
    for achievement_id in ACHIEVEMENT_ORDER:
        achievement = ACHIEVEMENTS[achievement_id]
        if achievement.get("hidden") and achievement_id not in unlocked_achievements:
            continue
        status = "Unlocked" if achievement_id in unlocked_achievements else "Locked"
        text = f"{achievement['name']}: {achievement['desc']} ({status})"
        Label(
            achievements_list,
            text=text,
            font=("Arial", 14, "bold"),
            fg="#ffffff" if status == "Unlocked" else "#888888",
            bg=BACKGROUND_COLOR
        ).pack(pady=8)


def show_achievement_popup(message):
    if game_state != GAME_STATE_RUNNING:
        return
    clear_achievement_popup()
    x1 = GAME_WIDTH - ACHIEVEMENT_POPUP_WIDTH - 20
    y1 = 20
    x2 = x1 + ACHIEVEMENT_POPUP_WIDTH
    y2 = y1 + ACHIEVEMENT_POPUP_HEIGHT
    rect_id = canvas.create_rectangle(
        x1, y1, x2, y2,
        fill=ACHIEVEMENT_POPUP_BG,
        outline="#ffffff",
        width=2
    )
    title_id = canvas.create_text(
        x1 + 10, y1 + 18,
        text="Achievement unlocked!",
        anchor=NW,
        fill="#ffffff",
        font=("Arial", 11, "bold")
    )
    msg_id = canvas.create_text(
        x1 + 10, y1 + 36,
        text=message,
        anchor=NW,
        fill="#ffd3d3",
        font=("Arial", 10)
    )
    achievement_popup_ids.extend([rect_id, title_id, msg_id])
    window.after(2500, clear_achievement_popup)


def clear_achievement_popup():
    while achievement_popup_ids:
        canvas.delete(achievement_popup_ids.pop())


def check_achievements():
    for achievement_id, achievement in ACHIEVEMENTS.items():
        if achievement["type"] != "score":
            continue
        if score >= achievement["value"]:
            unlock_achievement(achievement_id)


def unlock_achievement(achievement_id):
    if achievement_id in unlocked_achievements:
        return
    unlocked_achievements.add(achievement_id)
    show_achievement_popup(ACHIEVEMENTS[achievement_id]["message"])


def trigger_secret_whisper(event=None):
    if game_state != GAME_STATE_MENU:
        return
    unlock_achievement("secret_whisper")


def start_ending_sequence():
    global ending_sentence_index, ending_fade_step, ending_text_id, ending_image_id
    set_game_state(GAME_STATE_ENDING)
    canvas.delete(ALL)
    clear_obstacles()
    clear_achievement_popup()
    ending_sentence_index = 0
    ending_fade_step = 0

    snake_image = PILImage.open("snake_head.png")
    resized = snake_image.resize((400, 400), PILImage.Resampling.LANCZOS)
    end_img = ImageTk.PhotoImage(resized)
    ending_image_id = canvas.create_image(180, GAME_HEIGHT / 2, image=end_img, anchor=CENTER)
    canvas.ending_img = end_img

    ending_text_id = canvas.create_text(
        420, GAME_HEIGHT / 2,
        text="",
        anchor=W,
        fill="#ff1100",
        font=("Times", 32, "bold"),
        width=520
    )
    show_next_ending_sentence()


def show_next_ending_sentence():
    global ending_sentence_index, ending_fade_step
    if ending_sentence_index >= len(ENDING_SENTENCES):
        window.after(1000, game_over)
        return
    canvas.itemconfig(ending_text_id, text=ENDING_SENTENCES[ending_sentence_index])
    ending_fade_step = 0
    fade_in_sentence()


def fade_in_sentence():
    global ending_fade_step
    if game_state != GAME_STATE_ENDING:
        return
    shade = min(255, ending_fade_step * 20)
    color = f"#{shade:02x}{shade:02x}{shade:02x}"
    canvas.itemconfig(ending_text_id, fill=color)
    if ending_fade_step < 12:
        ending_fade_step += 1
        window.after(80, fade_in_sentence)
    else:
        window.after(1800, fade_out_sentence)


def fade_out_sentence():
    global ending_fade_step, ending_sentence_index
    if game_state != GAME_STATE_ENDING:
        return
    shade = max(0, 255 - ending_fade_step * 20)
    color = f"#{shade:02x}{shade:02x}{shade:02x}"
    canvas.itemconfig(ending_text_id, fill=color)
    if ending_fade_step < 12:
        ending_fade_step += 1
        window.after(60, fade_out_sentence)
    else:
        ending_sentence_index += 1
        show_next_ending_sentence()


def clear_obstacles():
    global obstacles
    while obstacle_ids:
        canvas.delete(obstacle_ids.pop())
    obstacles = []


def draw_obstacles():
    while obstacle_ids:
        canvas.delete(obstacle_ids.pop())
    for (x, y) in obstacles:
        obstacle_ids.append(
            canvas.create_rectangle(
                x, y, x + SPACE_SIZE, y + SPACE_SIZE,
                fill="#3a3a3a",
                outline="#7a7a7a"
            )
        )


def generate_obstacles(current_snake=None, current_food=None):
    global obstacles
    obstacles.clear()
    count = 8
    attempts = 0
    while len(obstacles) < count and attempts < 200:
        attempts += 1
        x = random.randint(0, (GAME_WIDTH//SPACE_SIZE)-1) * SPACE_SIZE
        y = random.randint(0, (GAME_HEIGHT//SPACE_SIZE)-1) * SPACE_SIZE
        if current_snake and [x, y] in current_snake.coordinates:
            continue
        if current_food and [x, y] == current_food.coordinates:
            continue
        if (x, y) in obstacles:
            continue
        if x < SPACE_SIZE * 2 and y < SPACE_SIZE * 2:
            continue
        obstacles.append((x, y))
    draw_obstacles()


def schedule_obstacle_shuffle():
    global obstacle_after_id
    if obstacle_after_id:
        window.after_cancel(obstacle_after_id)
    if current_difficulty != "beast":
        return
    delay = random.randint(5000, 10000)
    obstacle_after_id = window.after(delay, shuffle_obstacles)


def shuffle_obstacles():
    global beast_shuffle_count
    if current_difficulty != "beast" or game_state != GAME_STATE_RUNNING:
        schedule_obstacle_shuffle()
        return
    generate_obstacles(snake, food)
    beast_shuffle_count += 1
    if beast_shuffle_count == 1:
        unlock_achievement("beast_shuffle")
    schedule_obstacle_shuffle()


def set_game_state(new_state):
    global game_state
    game_state = new_state


def show_menu():
    global obstacle_after_id
    set_game_state(GAME_STATE_MENU)
    pause_frame.pack_forget()
    canvas.pack_forget()
    hud_frame.pack_forget()
    credits_frame.pack_forget()
    achievements_frame.pack_forget()
    difficulty_frame.pack_forget()
    menu_frame.pack(fill=BOTH, expand=True)
    clear_obstacles()
    clear_achievement_popup()
    if obstacle_after_id:
        window.after_cancel(obstacle_after_id)
        obstacle_after_id = None
    
    # Ensure music is playing when returning to menu
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.play(-1)


def show_credits():
    set_game_state(GAME_STATE_MENU)
    menu_frame.pack_forget()
    achievements_frame.pack_forget()
    difficulty_frame.pack_forget()
    pause_frame.pack_forget()
    canvas.pack_forget()
    hud_frame.pack_forget()
    credits_frame.pack(fill=BOTH, expand=True)


def show_achievements_screen():
    set_game_state(GAME_STATE_MENU)
    menu_frame.pack_forget()
    credits_frame.pack_forget()
    difficulty_frame.pack_forget()
    pause_frame.pack_forget()
    canvas.pack_forget()
    hud_frame.pack_forget()
    update_achievements_view()
    achievements_frame.pack(fill=BOTH, expand=True)


def show_difficulty():
    set_game_state(GAME_STATE_MENU)
    menu_frame.pack_forget()
    credits_frame.pack_forget()
    achievements_frame.pack_forget()
    pause_frame.pack_forget()
    canvas.pack_forget()
    hud_frame.pack_forget()
    difficulty_frame.pack(fill=BOTH, expand=True)


def start_game_with_difficulty(difficulty):
    global score, direction, snake, food, current_speed, current_difficulty, unlocked_achievements, beast_shuffle_count, shown_whispers
    set_game_state(GAME_STATE_RUNNING)
    menu_frame.pack_forget()
    credits_frame.pack_forget()
    achievements_frame.pack_forget()
    difficulty_frame.pack_forget()
    pause_frame.pack_forget()
    canvas.pack()
    hud_frame.pack(fill=X)
    canvas.delete(ALL)

    score = 0
    direction = "down"
    unlocked_achievements = set()
    clear_achievement_popup()
    shown_whispers = set()
    clear_whisper_text()
    current_difficulty = difficulty
    beast_shuffle_count = 0
    current_speed = DIFFICULTY_SPEEDS.get(difficulty, SPEED)
    score_label.config(text="Score:{}".format(score))
    high_score_label.config(text="High Score:{}".format(high_score))

    snake = Snake()
    if current_difficulty == "beast":
        unlock_achievement("beast_mode")
        generate_obstacles(snake)
    else:
        clear_obstacles()
    food = Food(snake)
    update_background_tint()
    schedule_obstacle_shuffle()
    next_turn(snake, food)


def show_pause():
    if game_state != GAME_STATE_RUNNING:
        return
    unlock_achievement("pause_game")
    set_game_state(GAME_STATE_PAUSED)
    canvas.pack_forget()
    hud_frame.pack_forget()
    clear_whisper_text()
    canvas.config(bg=BACKGROUND_COLOR)
    pause_frame.pack(fill=BOTH, expand=True)


def resume_game():
    if game_state != GAME_STATE_PAUSED:
        return
    set_game_state(GAME_STATE_RUNNING)
    pause_frame.pack_forget()
    canvas.pack()
    hud_frame.pack(fill=X)
    next_turn(snake, food)


def toggle_pause(event=None):
    if game_state == GAME_STATE_RUNNING:
        show_pause()
    elif game_state == GAME_STATE_PAUSED:
        resume_game()


def toggle_mute(event=None):
    global is_muted
    is_muted = not is_muted
    pygame.mixer.music.set_volume(0.0 if is_muted else 1.0)
    mute_button.config(text="Unmute" if is_muted else "Mute")
    unlock_achievement("mute_game")


def exit_game():
    window.destroy()


def toggle_fullscreen():
    global is_fullscreen
    is_fullscreen = not is_fullscreen
    window.attributes("-fullscreen", is_fullscreen)
    if is_fullscreen:
        window.geometry("")
    else:
        window.geometry(f"{GAME_WIDTH}x{GAME_HEIGHT + 80}+{x}+{y}")


window = Tk()
window.title("Labubbu")
window.geometry(f"{GAME_WIDTH}x{GAME_HEIGHT + 80}")

score = 0
direction = "down"
snake = None
food = None

hud_frame = Frame(window)
score_label = Label(hud_frame, text="Score:{}".format(score), font=("Comic Sans MS", 40))
score_label.pack(side=LEFT, padx=20)

high_score_label = Label(hud_frame, text="High Score:{}".format(high_score), font=("Comic Sans MS", 30))
high_score_label.pack(side=LEFT, padx=20)

hud_buttons = Frame(hud_frame)
hud_buttons.pack(side=RIGHT, padx=20)

pause_button = Button(hud_buttons, text="Pause", command=show_pause)
pause_button.pack(side=LEFT, padx=5)

fullscreen_button = Button(hud_buttons, text="Fullscreen", command=toggle_fullscreen)
fullscreen_button.pack(side=LEFT, padx=5)

mute_button = Button(hud_buttons, text="Mute", command=toggle_mute)
mute_button.pack(side=LEFT, padx=5)

canvas = Canvas(window, bg=BACKGROUND_COLOR, height=GAME_HEIGHT, width=GAME_WIDTH)

window.update()

window_width = window.winfo_width()
window_height = window.winfo_height()
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

x = int((screen_width / 2) - (window_width / 2))
y = int((screen_height / 2) - (window_height / 2))

window.geometry(f"{window_width}x{window_height}+{x}+{y}")

window.bind('<Left>', lambda event: change_direction('left'))
window.bind('<Right>', lambda event: change_direction('right'))
window.bind('<Up>', lambda event: change_direction('up'))
window.bind('<Down>', lambda event: change_direction('down'))
window.bind('p', toggle_pause)
window.bind('P', toggle_pause)
window.bind('m', toggle_mute)
window.bind('M', toggle_mute)
window.bind('F11', lambda e: toggle_fullscreen())
window.bind('h', trigger_secret_whisper)
window.bind('H', trigger_secret_whisper)

menu_frame = Frame(window, bg=BACKGROUND_COLOR)
menu_frame.pack(fill=BOTH, expand=True)

menu_title = Label(menu_frame, text=MENU_TITLE_TEXT, font=MENU_TITLE_FONT, fg=MENU_TITLE_COLOR, bg=BACKGROUND_COLOR)
menu_title.pack(pady=50)

menu_content = Frame(menu_frame, bg=BACKGROUND_COLOR)
menu_content.pack(expand=True, fill=BOTH, padx=60, pady=40)

menu_center = Frame(menu_content, bg=BACKGROUND_COLOR)
menu_center.pack(expand=True, fill=BOTH)

menu_image_placeholder = Label(menu_center, text="", bg=BACKGROUND_COLOR)
menu_image_placeholder.pack(pady=10)

play_button = Button(menu_center, text="Play", width=24, height=3, font=("Arial", 16, "bold"), bg="#ff1100", fg="white", activebackground="#ff3300", activeforeground="white", relief=RAISED, bd=3, command=show_difficulty)
play_button.pack(pady=20)

credits_button = Button(menu_center, text="Credits", width=24, height=3, font=("Arial", 16, "bold"), bg="#ff1100", fg="white", activebackground="#ff3300", activeforeground="white", relief=RAISED, bd=3, command=show_credits)
credits_button.pack(pady=20)

achievements_button = Button(menu_center, text="Achievements", width=24, height=3, font=("Arial", 16, "bold"), bg="#ff1100", fg="white", activebackground="#ff3300", activeforeground="white", relief=RAISED, bd=3, command=show_achievements_screen)
achievements_button.pack(pady=20)

exit_button = Button(menu_center, text="Exit", width=24, height=3, font=("Arial", 16, "bold"), bg="#333333", fg="white", activebackground="#555555", activeforeground="white", relief=RAISED, bd=3, command=exit_game)
exit_button.pack(pady=20)

credits_frame = Frame(window, bg=BACKGROUND_COLOR)
credits_title = Label(credits_frame, text="Credits", font=("Times", 64, "bold"), fg=MENU_TITLE_COLOR, bg=BACKGROUND_COLOR)
credits_title.pack(pady=40)

credits_text = (
    "Game design and code: gub1988\n"
    "Music by Toby Fox\n"
    "Art inspired by Chiikawa"
)
credits_label = Label(credits_frame, text=credits_text, font=("Arial", 20, "bold"), fg="#ffffff", bg=BACKGROUND_COLOR, justify=CENTER)
credits_label.pack(pady=30)

credits_back_button = Button(credits_frame, text="Back", width=18, height=2, font=("Arial", 14, "bold"), bg="#333333", fg="white", activebackground="#555555", activeforeground="white", relief=RAISED, bd=3, command=show_menu)
credits_back_button.pack(pady=20)

achievements_frame = Frame(window, bg=BACKGROUND_COLOR)
achievements_title = Label(achievements_frame, text="Achievements", font=("Times", 64, "bold"), fg=MENU_TITLE_COLOR, bg=BACKGROUND_COLOR)
achievements_title.pack(pady=30)

achievements_list = Frame(achievements_frame, bg=BACKGROUND_COLOR)
achievements_list.pack(expand=True)

achievements_back_button = Button(achievements_frame, text="Back", width=18, height=2, font=("Arial", 14, "bold"), bg="#333333", fg="white", activebackground="#555555", activeforeground="white", relief=RAISED, bd=3, command=show_menu)
achievements_back_button.pack(pady=20)

difficulty_frame = Frame(window, bg=BACKGROUND_COLOR)
difficulty_title = Label(difficulty_frame, text="Choose Difficulty", font=("Times", 56, "bold"), fg=MENU_TITLE_COLOR, bg=BACKGROUND_COLOR)
difficulty_title.pack(pady=30)

difficulty_buttons = Frame(difficulty_frame, bg=BACKGROUND_COLOR)
difficulty_buttons.pack(expand=True)

easy_button = Button(difficulty_buttons, text="Easy", width=22, height=2, font=("Arial", 16, "bold"), bg="#1f8f5f", fg="white", activebackground="#2aa86f", activeforeground="white", relief=RAISED, bd=3, command=lambda: start_game_with_difficulty("easy"))
easy_button.pack(pady=12)

normal_button = Button(difficulty_buttons, text="Normal", width=22, height=2, font=("Arial", 16, "bold"), bg="#ff1100", fg="white", activebackground="#ff3300", activeforeground="white", relief=RAISED, bd=3, command=lambda: start_game_with_difficulty("normal"))
normal_button.pack(pady=12)

hard_button = Button(difficulty_buttons, text="Hard", width=22, height=2, font=("Arial", 16, "bold"), bg="#b33800", fg="white", activebackground="#cc4500", activeforeground="white", relief=RAISED, bd=3, command=lambda: start_game_with_difficulty("hard"))
hard_button.pack(pady=12)

beast_button = Button(difficulty_buttons, text="Beast Mode", width=22, height=2, font=("Arial", 16, "bold"), bg="#5b00b3", fg="white", activebackground="#6d00cc", activeforeground="white", relief=RAISED, bd=3, command=lambda: start_game_with_difficulty("beast"))
beast_button.pack(pady=12)

difficulty_back_button = Button(difficulty_frame, text="Back", width=18, height=2, font=("Arial", 14, "bold"), bg="#333333", fg="white", activebackground="#555555", activeforeground="white", relief=RAISED, bd=3, command=show_menu)
difficulty_back_button.pack(pady=20)

pause_frame = Frame(window, bg=BACKGROUND_COLOR)
pause_frame.pack(fill=BOTH, expand=True)

pause_title = Label(pause_frame, text="Paused", font=("Times", 60, "bold"), fg="#F72119", bg=BACKGROUND_COLOR)
pause_title.pack(expand=True)

pause_buttons = Frame(pause_frame, bg=BACKGROUND_COLOR)
pause_buttons.pack(expand=True, fill=BOTH)

pause_menu_button = Button(pause_buttons, text="Menu", width=24, height=3, font=("Arial", 16, "bold"), bg="#ff1100", fg="white", activebackground="#ff3300", activeforeground="white", relief=RAISED, bd=3, command=show_menu)
pause_menu_button.pack(pady=20)

pause_exit_button = Button(pause_buttons, text="Exit", width=24, height=3, font=("Arial", 16, "bold"), bg="#333333", fg="white", activebackground="#555555", activeforeground="white", relief=RAISED, bd=3, command=exit_game)
pause_exit_button.pack(pady=20)

load_high_score()

show_menu()


window.mainloop()
