import subprocess
from gpio import IO
from time import sleep


class Sound():
    """
    音声通知を行うクラスです。
    """
    def __init__(self):
        """
        コンストラクタです。openJtalkの各種値を設定します。
        """
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
        
        :param text: 喋らせたい文字列
        :return self.say(): 音声
        """
        self.generate_wave(text)
        return self.say()

    def generate_wave(self, text, name='tmp.wav'):
        """
        渡した文字列を喋ったwavファイルを生成します。
        
        :param text: 喋らせたい文字列
        :param name: wavファイルの名前
        :return: なし
        """
        outWav = ['-ow', './wav/' + name]
        cmd = self.openJtalk + self.dic + self.htsVoice + self.speed + outWav
        c = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        c.stdin.__write(text.encode('utf-8'))
        c.stdin.close()
        c.wait()

    def say(self, name='tmp.wav'):
        """
        渡した文字列のwavファイルを再生します。
        wavファイルはあらかじめ用意する必要があります。
        
        :param name: 喋らせたいwavファイルの名前
        :return self.sp: 音声
        """
        try:
            self.sp.terminate()
        except:
            pass
        aplay = ['aplay', '-q', './wav/' + name]
        self.sp = subprocess.Popen(aplay)
        return self.sp

    def speak_help(self):
        """
        救援要請用の音声です。
        
        :return: なし
        """
        self.sp_ssw.on()
        sleep(0.1)
        # self.say(name='help.wav')
        self.talk("テスト").wait()

    def sperker_off(self):
        """
        スピーカーをオフにします。
        
        :return: なし
        """
        self.sp_ssw.off()

    def sperker_on(self):
        """
        スピーカーをオンにします。
        
        :return: なし
        """
        self.sp_ssw.on()
        sleep(0.5)

    def say_init(self):
        """
        初期状態用の音声です。
        
        :return: なし
        """
        self.say("init.wav")

    def say_dist(self, dist_count):
        """
        走行距離通知用の音声です。
        
        :param dist_count: 5メートルごとの回数
        :return: なし
        """
        self.say("dist_" + str(dist_count * 5) + ".wav")

    def say_straight(self):
        """
        直進用の音声です。
        
        :return: なし
        """
        self.say("straight.wav")

    def say_turn(self):
        """
        曲がり角回転用の音声です。
        
        :return: なし
        """
        self.say("turn.wav")

    def say_corner(self):
        """
        曲がり角直進用の音声です。
        
        :return: なし
        """
        self.say(name='corner.wav')

    def say_obstacle(self):
        """
        障害物回避用の音声です。
        
        :return: なし
        """
        self.say(name='obstacle.wav')

    def say_step(self):
        """
        段差用の音声です。
        
        :return: なし
        """
        self.say(name='step.wav')

    def say_stop(self):
        """
        停止用の音声です。
        
        :return: なし
        """
        self.say(name='stop.wav')

    def say_help(self):
        """
        救援要請用の音声です。
        
        :return: なし
        """
        self.say(name='help.wav')

    def say_touch(self):
        """
        ハーネスから手が離れたとき用の音声です。
        
        :return: なし
        """
        self.say(name='touch.wav')

    def say_wait(self, expected):
        """
        待機用の音声です。
        渡された走行状況により流す音声を変更します。
        
        :return: なし
        """
        if expected == "turn":
            self.say(name='corner.wav')
        elif expected == "avoid":
            self.say(name='obstacle.wav')


if __name__ == "__main__":
    s = Sound()
    s.say_touch()
    sleep(10)
