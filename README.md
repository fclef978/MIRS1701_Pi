# MIRS1701_Pi

## Member
* Hirokazu Suzuki
* Hisashi Sakashita
* Kazuki Unno

## TaskMainの使い方
超音波センサの値を見たかったらuss.vals(list型)
Arduinoからの値を見たかったらreq.vals(dict型)
Arduinoへの指令は[cmd, val1, val2, ...]をreq.order()に渡す

### uss
valsの中身はちゃんと作っていない。
たぶんdict型になって'front'とか'left'みたいなキーをとる

### request
valsの中身は現状適当(回路ができてないから)
キー一覧は↓
* バッテリーA -> battA
* バッテリーB -> battB
* ジョイスティックX軸 -> jsX
* ジョイスティックY軸 -> jsY


order()に渡すlistは0番目の値(cmd)がstr、そのあとが可変長のintまたはfloatとなっている。
cmdは大文字と小文字を区別しない
cmdの一覧は↓
* 停止 -> 'stop'
* 直進 -> 'straight' (そのあとに速度・距離を渡す)
* 旋回 -> 'rotation' (そのあとに角速度・角度を渡す)
* リセット -> 'reset' (Arduino側が未実装)


### 例
* ['stop'] (停止)
* ['straight', 50, 100] (速度50cm/s 距離100cmで直進)
