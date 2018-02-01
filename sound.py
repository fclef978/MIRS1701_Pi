import subprocess
from gpio import IO
from time import sleep


class Sound():
    def __init__(self):
        self.openJtalk = ['open_jtalk']
        self.dic = ['-x', '/var/lib/mecab/dic/open-jtalk/naist-jdic']
        self.htsVoice = ['-m', '/usr/share/hts-voice/mei/mei_normal.htsvoice']
        self.speed = ['-r', '1.0']
        self.sp_ssw = IO(IO.SP_SSW, IO.OUT)
        self.sp = None

    def talk(self, text):
        """
        openJtalkに喋らせるメソッドです。
        渡した文字列を喋ります。
        """
        self.generate_wave(text)
        return self.say()

    def generate_wave(self, text, name='tmp.wav'):
        outWav = ['-ow', './wav/' + name]
        cmd = self.openJtalk + self.dic + self.htsVoice + self.speed + outWav
        c = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        c.stdin.write(text.encode('utf-8'))
        c.stdin.close()
        c.wait()

    def say(self, name='tmp.wav'):
        try:
            self.sp.terminate()
        except:
            pass
        aplay = ['aplay', '-q', './wav/' + name]
        self.sp =  subprocess.Popen(aplay)
        return self.sp

    def speak_help(self):
        self.sp_ssw.on()
        sleep(0.1)
        # self.say(name='help.wav')
        self.talk("テスト").wait()

    def sperker_off(self):
        self.sp_ssw.off()

    def say_init(self):
        self.say("init.wav")

    def say_dist(self, dist_count):
        self.say("dist_" + str(dist_count * 5) + ".wav")

    def say_straight(self):
        self.say("straight.wav")

    def say_turn(self):
        self.say("turn.wav")

    def say_corner(self):
        self.say(name='corner.wav')

    def say_obstacle(self):
        self.say(name='obstacle.wav')

    def say_step(self):
        self.say(name='step.wav')

    def say_stop(self):
        self.say(name='stop.wav')

    def say_help(self):
        self.sp_ssw.on()
        sleep(0.1)
        self.say(name='help.wav')

    def say_touch(self):
        self.sp_ssw.on()
        sleep(0.1)
        self.say(name='touch.wav')

    def say_wait(self, expected):
        """
        待機時の音声通知です。
        次の状態によって、流す音声を変更します。
        :param expected:
        """
        if expected == "turn":
            self.say(name='corner.wav')
        elif expected == "avoid":
            self.say(name='obstacle.wav')


if __name__ == "__main__":
    s = Sound()
    s.say_touch()
    sleep(10)