import random
from collections import Counter

from PIL import Image
from guizero import App, Text, PushButton, Box, Picture
from playsound import playsound


class SlotImageUrl:
    """
    This class holds a path to image file in images folder
    """

    # Base paths for image files
    BASE_PATH = 'images/{}.png'
    # complete path+name of the images file
    image_urls = [BASE_PATH.format('img1'),
                  BASE_PATH.format('img2'),
                  BASE_PATH.format('img3'),
                  BASE_PATH.format('img4'),
                  BASE_PATH.format('img5')]

    def __init__(self):
        self._x_coordinate = 0
        self._y_coordinate = 0
        self._image_url = self._reset_image_url()

    def _reset_image_url(self):
        # generate random number (say index) b/w 0-4
        random_index = random.randint(0, 1000) % 5
        # it will return a url from the image_url list
        return self.image_urls[random_index]

    def reset_image_url(self, image_url=None):
        """
        This method will set a random path of image in _image_url class variable.
        if image_url value is none (means not passed) then it will pick up random path.
        :param image_url: path of image default: is none
        :return:
        """
        if not image_url:
            self._image_url = self._reset_image_url()
            return
        self._image_url = image_url

    def get_image_url(self):
        # This method will return _image_url values
        return self._image_url


class SlotImageRoller:
    """
    This class will mange a single instance of rolling image (animation )
    """

    # Animation speed controller value must be multiple of 16, 32 64 etc
    IMAGE_DELTA = 64
    # size of images used in the game
    IMAGE_SIZE = (256, 256)
    # limit of animation resetting value
    RESET_ANIMATION_SPEED_VALUE = 256

    def __init__(self, root):
        self.image1 = SlotImageUrl()
        self.image2 = SlotImageUrl()
        # picture frame will be used for animation
        self.image_frame = Picture(root, align='left', height=96, width=96)
        self.image_crop_size = 0
        self.reset_crop_size()
        self.set_initial_image()

    def set_initial_image(self):
        self.image_frame.image = Image.open(self.image2.get_image_url())

    def reset_crop_size(self):
        self.image_crop_size = 0

    def roll(self):
        """
        As you can see this class holds two of random images path.
        The logic of animation here is to cut two different images one from the top and other one from the bottom.
        ones we get top and bottom pieces of two different images we will paste them to gather.
        In next itration the portion of top and bottom will change and a new images will be pasted in image_frame
        That's how we are doing animation here.
        """
        self.image_crop_size += self.IMAGE_DELTA

        image1 = Image.open(self.image1.get_image_url())
        image2 = Image.open(self.image2.get_image_url())
        xsize, ysize = self.IMAGE_SIZE

        part1 = image1.crop((0, 0, xsize, self.image_crop_size))
        part2 = image2.crop((0, self.image_crop_size, xsize, ysize))

        image2.paste(part1, (0, ysize-self.image_crop_size, xsize, ysize))
        image2.paste(part2, (0, 0, xsize, ysize - self.image_crop_size))

        self.image_frame.image = image2

        # Here we will check that if we reach crop limit of image
        # then we will assign path of image1 to image 2
        # and renew the path of image1 so the we get next random image
        if self.image_crop_size >= self.RESET_ANIMATION_SPEED_VALUE:
            self.image2.reset_image_url(self.image1.get_image_url())
            self.image1.reset_image_url()
            self.reset_crop_size()

    def current_status(self):
        """
        This method is used by roll_grid from SlotImageRollerGrid class
        it will tell when to stop animation.
        """
        return True if self.image_crop_size != 0 else False

    def current_img_url(self):
        # This method will return the current path of image2 of class variable
        return self.image2.get_image_url()


class SlotImageRollerGrid:
    """
    This class will mange a 5 instance of rolling images (animation )
    """

    MAX_ROLLER_GRID = 5
    # tells how many times we will call roll funtion
    MAX_ROLLING_COUNT = 150
    SlotImageRollers = []

    def __init__(self, main_window, root):
        """
        :param main_window: will be used to update window each time there is any update to window( e.g animation)
        :param root: where there rolling images will be displayed in the main app window
        """
        self.main_window = main_window
        for i in range(0, self.MAX_ROLLER_GRID):
            self.SlotImageRollers.append(SlotImageRoller(root))

    def roll_grid(self):
        i = 0
        while i < self.MAX_ROLLING_COUNT or self.SlotImageRollers[0].current_status():
            i += 1
            for image_roller in self.SlotImageRollers:
                image_roller.roll()
            self.main_window.update()

    def max_same_img(self):
        """
        This method counts the number of same image once the roller is stopped rolling.
        :return:
        """
        # Here we will first collect the path of all 5 rollers after it stops rolling
        image_urls = [img.current_img_url() for img in self.SlotImageRollers]
        # Counter method will return dict of paths(as key) with their number of occurance (as value)
        same_url_counts = Counter(image_urls)
        # then we will make a list of all value from above dict and find max value from it.
        max_same_images = max([v for k, v in same_url_counts.items()])
        # retrun the max value( max count of same images)
        return max_same_images


class SlotZilla:

    FORMAT_TURNS_LEFT = 'Turns left {turns_left}'
    FORMAT_AMOUNT_WON = 'You won: ${amount_won}'
    WINNING_AMOUNT = {
        '1': 0,
        '2': 50,
        '3': 100,
        '4': 5000,
        '5': 50000
    }

    def __init__(self):
        self.app = App('Slot Zilla', layout='grid')
        self.turn_left = 0
        self.amount_won = 0

        # These are the boxes (portions of window) where the widgets will be dsiplayed
        self.money_box = Box(self.app, width="fill", grid=[0, 0])
        self.image_grid_box = Box(self.app, width=500, height=150, border=True, grid=[0, 1])
        self.bet_grid_box = Box(self.app, width="fill", grid=[0, 2])
        self.function_grid_box = Box(self.app, width="fill", grid=[0, 3])

        self.roller_grid = SlotImageRollerGrid(self.app, self.image_grid_box)

        self.lbl_amount_won = Text(self.money_box, size=20)

        # Button widgets and settng up therir onclick methods to perform action.
        self.btn_bet_1_doller = PushButton(self.bet_grid_box, text='1$', align='left', command=self.bet_1_doller,
                                           width=12, height=2)
        self.btn_bet_10_doller = PushButton(self.bet_grid_box, text='10$', align='left', command=self.bet_10_doller,
                                            width=12, height=2)
        self.btn_bet_20_doller = PushButton(self.bet_grid_box, text='20$', align='left', command=self.bet_20_doller,
                                            width=12, height=2)
        self.btn_bet_50_doller = PushButton(self.bet_grid_box, text='50$', align='left', command=self.bet_50_doller,
                                            width=12, height=2)
        self.btn_reset_all = PushButton(self.function_grid_box, text='Rest', align='right', command=self.reset_all,
                                        width=12, height=2)
        self.btn_turns_left = PushButton(self.function_grid_box, align='left', command=self.decrement_turn,
                                         width=12, height=2)
        self.set_turn_btn_txt()
        self.set_amount_lbl_txt()
        self.app.display()

    def reset_all(self):
        self.turn_left = 0
        self.amount_won = 0
        self.set_turn_btn_txt()
        self.set_amount_lbl_txt()

    def decrement_turn(self):
        # On each call this will roll the image roller and check for the number of images to be same.
        # and count the winning amount and then update the winning amount string, turns string on the window
        if self.turn_left > 0:
            self.turn_left -= 1
            self.roller_grid.roll_grid()
            count_same_images = self.roller_grid.max_same_img()
            self.set_win_amount(count_same_images)
            self.set_turn_btn_txt()
            self.set_amount_lbl_txt()
        else:
            self.app.info("Bet Again!", "No Turns Left!")
        self.app.update()

    def set_win_amount(self, count_same_imag):
        if count_same_imag > 1:
            self.amount_won += self.WINNING_AMOUNT[str(count_same_imag)]
            try:
                playsound('music.mp3')
            except:
                pass

    def set_turn_btn_txt(self):
        self.btn_turns_left.text = self.FORMAT_TURNS_LEFT.format(turns_left=self.turn_left)

    def set_amount_lbl_txt(self):
        self.lbl_amount_won.value = self.FORMAT_AMOUNT_WON.format(amount_won=self.amount_won)

    def set_turns(self, turns):
        self.turn_left += turns
        self.set_turn_btn_txt()

    def bet_1_doller(self):
        self.set_turns(2)

    def bet_10_doller(self):
        self.set_turns(5)

    def bet_20_doller(self):
        self.set_turns(10)

    def bet_50_doller(self):
        self.set_turns(20)


if __name__ == '__main__':
    SlotZilla()
