import subprocess
from gpio import IO


class Sound():
    
    def __init__(self):
        self.openJtalk = ['open_jtalk']
        self.dic = ['-x','/var/lib/mecab/dic/open-jtalk/naist-jdic']
        self.htsVoice=['-m','/usr/share/hts-voice/mei/mei_normal.htsvoice']
        self.speed=['-r','1.0']
        self.sp_ssw = IO(IO.SP_SSW, IO.IN)
        
    def talk(self, text):
        """
        openJtalkに喋らせるメソッドです。
        渡した文字列を喋ります。
        """
        self.generate_wave(text)
        self.say()

    def generate_wave(self, text, name='tmp.wav'):
        outWav = ['-ow', './wav/'+name]
        cmd = self.openJtalk + self.dic + self.htsVoice + self.speed + outWav
        c = subprocess.Popen(cmd,stdin=subprocess.PIPE)
        c.stdin.write(text.encode('utf-8'))
        c.stdin.close()
        c.wait()

    def say(self, name='tmp.wav'):
        aplay = ['aplay','-q','./wav/'+name]
        wr = subprocess.Popen(aplay)

    def speak_help(self):
        self.sp_ssw.on()
        self.say(name='help.wav')
        self.sp_ssw.off()

    def say_corner(self):
        self.say(name='corner.wav')

    def say_obstacle(self):
        self.say(name='obstacle.wav')

    def say_step(self):
        self.say(name='step.wav')

    def say_stop(self):
        self.say(name='stop.wav')

if __name__ == "__main__":
    s = Sound()
    s.generate_wave("助けてください", 'help.wav')
    s.say_stop()
