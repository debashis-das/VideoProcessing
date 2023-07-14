import time

import numpy as np
import cv2 as cv

ball_thickness = 10
board_thickness = 10
slider_width = 540
slider_row = 650
movement = 100
ball_color = (0, 65, 255)
colors_set = set([(122, 33, 83), (83, 33, 122), (18, 126, 227), (17, 186, 102)])
slider_color = (255, 65, 0)
current_movement = [False, False]
prev_slider = [False]
stop_game = [False]
font = cv.FONT_HERSHEY_SIMPLEX
double_collision = [False]


def init():
    img = np.zeros((720, 1280, 3), np.uint8)
    img[150:160][:] = (122, 33, 83)
    img[160:170][:] = (83, 33, 122)
    img[170:180][:] = (18, 126, 227)
    img[180:190][:] = (17, 186, 102)
    img[190:200][:] = (122, 33, 83)
    img[200:210][:] = (83, 33, 122)
    left = len(img[0]) // 2 - slider_width // 2
    right = len(img[0]) // 2 + slider_width // 2

    img[slider_row:slider_row + board_thickness, left:right] = slider_color
    hitter = [[left, slider_row], [right, slider_row + board_thickness]]

    mid_board = left + (right - left) // 2
    img[slider_row - ball_thickness:slider_row, mid_board:mid_board + ball_thickness] = ball_color
    init_ball_cordinate = [[mid_board, slider_row - ball_thickness], [mid_board + ball_thickness, slider_row]]
    return img, hitter, init_ball_cordinate


image, board, prev_move = init()


def moveSliderRight():
    # print('HERE RIGHT')
    temp_movement = 1280 - board[1][0] if board[1][0] + movement >= 1280 else movement
    image[board[0][1]:board[1][1], board[0][0]:board[0][0] + temp_movement] = (0, 0, 0)
    image[board[0][1]:board[1][1], board[1][0]:board[1][0] + temp_movement] = slider_color
    board[0][0] = board[0][0] + temp_movement
    board[1][0] = board[1][0] + temp_movement


def moveSliderLeft():
    # print('HERE LEFT')
    temp_movement = board[0][0] if board[0][0] - movement < 0 else movement
    image[board[0][1]:board[1][1], board[1][0] - temp_movement:board[1][0]] = (0, 0, 0)
    image[board[0][1]:board[1][1], board[0][0] - temp_movement:board[0][0]] = slider_color
    board[0][0] = board[0][0] - temp_movement
    board[1][0] = board[1][0] - temp_movement


def slider_hit(current_move, rowMove, colMove):
    changePixelColor(current_move, slider_color)
    prev_slider[0] = True
    current_movement[0] = not rowMove
    point_hit_on_slider = current_move[0][0] - board[0][0]
    displacement = point_hit_on_slider // (slider_width // 3)
    # print('slider hit !!!', displacement, colMove)
    if displacement == 0 and colMove:
        # print('change direction')
        current_movement[1] = not colMove
    elif displacement == 2 and not colMove:
        # print('change direction')
        current_movement[1] = not colMove
    return current_move


def moveBall(rowMove, colMove, current_move):
    next_move = nextMoveCordinate(rowMove, colMove, current_move)
    if boundary_conditions(rowMove, colMove, next_move):
        return
    current_color = pixelColor(current_move)
    if current_color == slider_color:
        return slider_hit(current_move, rowMove, colMove)

    bottom_block = [[current_move[0][0], current_move[0][1] + ball_thickness],
                    [current_move[1][0], current_move[1][1] + ball_thickness]]
    if current_color in colors_set and pixelColor(bottom_block) in colors_set:
        # print(bottom_block, pixelColor(bottom_block), current_color)
        changePixelColor(bottom_block, (0, 0, 0))
        top_block = [
            [current_move[0][0] + (ball_thickness if not colMove else -1 * ball_thickness), current_move[0][1]],
            [current_move[1][0] + (ball_thickness if not colMove else -1 * ball_thickness), current_move[1][1]]]
        # print(top_block)
        if len(top_block[0]) == 2 and len(top_block[1]) == 2 and pixelColor(top_block) in colors_set:
            changePixelColor(top_block, (0, 0, 0))
        changeRowDirection(rowMove)
        changeColDirection(colMove)
        double_collision[0] = True
        # stop_game[0] = True
    else:
        changePixelColor(current_move, ball_color)
        if current_color and current_color in colors_set:
            changeRowDirection(rowMove)
    return current_move


def pixelColor(move):
    next_pixel = image[move[0][1]:move[1][1], move[0][0]:move[1][0]]
    return tuple(next_pixel[4][4])


def changePixelColor(move, color):
    if move:
        image[move[0][1]:move[1][1], move[0][0]:move[1][0]] = color
        return True
    return False


def boundary_conditions(rowMove, colMove, next_move):
    if len(next_move[0]) != 0 and (next_move[0][0] < 0 or next_move[0][1] < 0 or next_move[1][0] >= 1280):
        print('Boundary!!', next_move)
        if next_move[0][0] <= 0 and next_move[0][1] <= 0:
            changeColDirection(colMove)
            changeRowDirection(rowMove)
        if next_move[0][0] <= 0:
            changeColDirection(colMove)
        if next_move[0][1] <= 0:
            changeRowDirection(rowMove)
        if next_move[1][0] >= 1280:
            changeColDirection(colMove)
        return True
    return False


'''
    rowMove (False,True) -> (up, down)
    colMove (False,True) -> (left, right)
'''


def startGame(rowMove, colMove):
    if stop_game[0]:
        cv.putText(image, 'Game Over', (10, 500), font, 2, (255, 255, 255), 5, cv.LINE_AA)
        return
    # next_color = nextColor(next_move)
    # if next_color in colors_set:
    #     changeRowDirection(rowMove)
    if not prev_slider[0]:
        image[prev_move[0][1]:prev_move[1][1], prev_move[0][0]:prev_move[1][0]] = (0, 0, 0)
    else:
        prev_slider[0] = False
    current_move = nextMoveCordinate(rowMove, colMove, prev_move)
    current_move = moveBall(rowMove, colMove, current_move)
    if current_move and not double_collision[0]:
        prev_move[0] = current_move[0]
        prev_move[1] = current_move[1]
    if double_collision[0]:
        double_collision[0] = False
    if current_move and current_move[0][1] >= slider_row + 50:
        stop_game[0] = True


def nextMoveCordinate(rowMove, colMove, ball_cordinate):
    if not rowMove and not colMove:
        print('move up left', ball_cordinate)
        current_move = [[ball_cordinate[0][0] - ball_thickness, ball_cordinate[0][1] - ball_thickness],
                        [ball_cordinate[0][0], ball_cordinate[0][1]]]
    elif not rowMove and colMove:
        print('move up right', ball_cordinate)
        current_move = [[ball_cordinate[1][0], ball_cordinate[0][1] - ball_thickness],
                        [ball_cordinate[1][0] + ball_thickness, ball_cordinate[0][1]]]
    elif rowMove and not colMove:
        print('move down left', ball_cordinate)
        current_move = [[ball_cordinate[0][0] - ball_thickness, ball_cordinate[1][1]],
                        [ball_cordinate[0][0], ball_cordinate[1][1] + ball_thickness]]
    elif rowMove and colMove:
        print('move down right', ball_cordinate)
        current_move = [[ball_cordinate[1][0], ball_cordinate[1][1]],
                        [ball_cordinate[1][0] + ball_thickness, ball_cordinate[1][1] + ball_thickness]]
    else:
        current_move = []
        print('Unexpected case')
    return current_move


def changeRowDirection(rowMove):
    current_movement[0] = not rowMove


def changeColDirection(colMove):
    current_movement[1] = not colMove


print(len(image))
print(len(image[0]))
# changePixelColor([[200, 200], [210, 210]], (0, 0, 0))
# counter = 0
while 1:
    cv.imshow('image', image)
    k = cv.waitKey(1) & 0xFF
    if k == 27:
        break
    if k == 3:
        moveSliderRight()
    elif k == 2:
        moveSliderLeft()
    startGame(current_movement[0], current_movement[1])
    # counter logic
    # counter += 1
    # if counter == 10000:
    #     break
    time.sleep(1 / 100)
# cv.imwrite('test2.jpg', image)
cv.destroyAllWindows()
