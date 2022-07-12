

class Emoji:

    FAST_FORWARD = "⏩"
    PLAY = "▶"
    FAST_REVERSE = "⏪"
    THUMBS_UP = "👍"
    STOP = "⏹️"
    PAUSE = "⏸️"
    SHUFFLE = "🔀"
    LOOP_SINGLE = "🔂"

    #'un.'
    def has_playlist(self):
        return len(self.music_queue) > 0

    def is_playlist_empty(self):
        return len(self.music_queue) == 0
