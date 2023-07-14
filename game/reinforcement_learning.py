import simple_game as sg
import time

while 1:
    sg.cv.imshow('image', sg.image)
    k = sg.cv.waitKey(1) & 0xFF
    if k == 27:
        break
    if k == 3:
        sg.moveSliderRight()
    elif k == 2:
        sg.moveSliderLeft()
    sg.startGame(sg.current_movement[0], sg.current_movement[1])
    # counter logic
    # counter += 1
    # if counter == 10000:
    #     break
    time.sleep(1 / 100)
# cv.imwrite('test2.jpg', image)
sg.cv.destroyAllWindows()
