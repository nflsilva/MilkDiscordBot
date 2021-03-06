

class Emoji:

    FAST_FORWARD = "β©"
    PLAY = "βΆ"
    FAST_REVERSE = "βͺ"
    THUMBS_UP = "π"
    STOP = "βΉοΈ"
    PAUSE = "βΈοΈ"
    SHUFFLE = "π"
    LOOP_SINGLE = "π"

    #'un.'
    def has_playlist(self):
        return len(self.music_queue) > 0

    def is_playlist_empty(self):
        return len(self.music_queue) == 0
