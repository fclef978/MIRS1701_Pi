import uss
import math

class Run():
    RADIUS = 40 #MIRSのタイヤ間の距離[cm]
    USS_DIST = 19 #MIRSの中心から超音波センサまでの距離[cm]
    Kp = 1
    Ki = 1
    Kd = 1
    TARGET_DIST = 0.4 #目標となる壁との距離[m]
    INTERVAL = 0.01 #制御周期[s]


    def __init__(self):
        self.vel_left_sum = 0
        self.vel_right_sum = 0

    def straight(self,ussvals,reqvals,vel,wall_flag):
        """
        壁と一定の距離を保ち、直進走行します。
        :return
        """
        posi = []
        cmd = ['Velosity']
        #目標値との差を計算
        posi.extend(self.position(ussvals,wall_flag))
        distx_diff = Run.TARGET_DIST - posi[0]
        disty_diff = math.sqrt(vel - distx_diff)

        #速度計算
        vel_left = distx_diff * math.cos(posi[1]) + disty_diff * math.sin(posi[1]) + (Run.RADIUS * wall_flag * posi[1] / 2) / Run.INTERVAL
        vel_right = distx_diff * math.cos(posi[1]) + disty_diff * math.sin(posi[1]) - (Run.RADIUS * wall_flag * posi[1] / 2) / Run.INTERVAL

        vel_left_diff = vel_left - reqvals[1]
        vel_right_diff = vel_right - reqvals[2]
        self.vel_left_sum += vel_left_diff
        self.vel_right_sum += vel_right_diff
        vel_left_target = Run.Kp * vel_left + Run.Ki * vel_left_diff + Run.Kd * vel_left_diff
        vel_right_target = Run.Kp * vel_right + Run.Ki * vel_right_diff + Run.Kd * vel_right_diff

        #整数に変換
        cmd.append(round(vel_left_target))
        cmd.append(round(vel_right_target))

        return cmd

    def position(self,ussvals,wall_flag):
        """
        MIRSの壁との距離x、壁と平行な線に対する自分の角度radを計算します。
        (超音波センサは正面が0、そこから時計回りに割り振られているものとする。)
        :return: [x,rad]
        """
        if  wall_flag == 1: #右壁の時
            rad = (math.pi / 4) - math.atan(Run.USS_DIST + ussvals[1] / Run.USS_DIST + ussvals[3])
            x = ussvals[2] * math.cos(rad) / 100
        else: #左壁の時
            rad = (math.pi / 4) - math.atan(Run.USS_DIST + ussvals[5] / Run.USS_DIST + ussvals[7])
            x = ussvals[2] * math.cos(rad) / 100
        return (x, rad)

run = Run()